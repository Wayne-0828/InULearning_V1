"""
Analytics API 路由

提供各科目雷達圖與趨勢圖所需的彙總資料
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct, cast, Float, Integer, case

from ..utils.auth import get_current_user
from ..utils.database import get_db_session
from ..models.exercise_record import ExerciseRecord
from ..models.learning_session import LearningSession


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _parse_window_days(window: str) -> int:
    """Parse window strings like '7d', '30d', '90d' into day count."""
    value = (window or "30d").strip().lower()
    if value.endswith("d") and value[:-1].isdigit():
        days = int(value[:-1])
        return days if days > 0 else 30
    # fallback
    if value.isdigit():
        days_int = int(value)
        return days_int if days_int > 0 else 30
    return 30


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except Exception:
        return None


@router.get("/subjects/radar")
async def get_subjects_radar(
    window: str = Query("30d", description="時間範圍 (7d, 30d, 90d)"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    """取得各科目的六維度雷達圖指標 (raw + normalized)。"""
    days = _parse_window_days(window)
    user_id_int = _safe_int(current_user.user_id)
    if user_id_int is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id in token")

    # 聚合每科目資料
    # - accuracy_pct = AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) * 100
    # - avg_time_spent_s = AVG(er.time_spent)
    # - qpm = 60 / avg_time_spent_s
    # - dwell_min = AVG(ls.time_spent) / 60
    # - questions_count = COUNT(*)
    # - sessions_count = COUNT(DISTINCT er.session_id)
    try:
        window_start = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(
                ExerciseRecord.subject.label("subject"),
                (func.avg(cast(case((ExerciseRecord.is_correct == True, 1), else_=0), Float)) * 100.0).label("accuracy_pct"),
                func.avg(ExerciseRecord.time_spent).label("avg_time_spent_s"),
                func.count().label("questions_count"),
                func.count(distinct(ExerciseRecord.session_id)).label("sessions_count"),
                (func.avg(LearningSession.time_spent) / 60.0).label("dwell_min"),
            )
            .join(LearningSession, LearningSession.id == ExerciseRecord.session_id)
            .where(
                ExerciseRecord.user_id == user_id_int,
                ExerciseRecord.created_at >= window_start,
            )
            .group_by(ExerciseRecord.subject)
        )

        rows = (await db_session.execute(stmt)).all()
    except Exception as e:
        logger.error(f"Radar aggregation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Radar aggregation failed")

    # 整理 raw 指標，計算 qpm 與 avg_q_per_session
    subjects_raw: List[Dict[str, Any]] = []
    for subject, accuracy_pct, avg_time_spent_s, questions_count, sessions_count, dwell_min in rows:
        avg_time_spent_s = float(avg_time_spent_s) if avg_time_spent_s is not None else None
        qpm = 60.0 / avg_time_spent_s if (avg_time_spent_s and avg_time_spent_s > 0) else 0.0
        questions_count = int(questions_count or 0)
        sessions_count = int(sessions_count or 0)
        avg_q_per_session = (questions_count / sessions_count) if sessions_count > 0 else 0.0
        dwell_min = float(dwell_min or 0.0)
        subjects_raw.append(
            {
                "subject": subject or "未知科目",
                "raw": {
                    "accuracy_pct": float(accuracy_pct or 0.0),
                    "qpm": float(qpm),
                    "dwell_min": dwell_min,
                    "questions_count": questions_count,
                    "avg_q_per_session": float(avg_q_per_session),
                    "sessions_count": sessions_count,
                },
            }
        )

    # 正規化到 0-100
    metric_keys = [
        "accuracy_pct",
        "qpm",
        "dwell_min",  # lower is better
        "questions_count",
        "avg_q_per_session",
        "sessions_count",
    ]

    def min_max(values: List[float]) -> List[float]:
        if not values:
            return []
        vmin = min(values)
        vmax = max(values)
        if vmax == vmin:
            return [50.0 for _ in values]
        return [((v - vmin) / (vmax - vmin)) * 100.0 for v in values]

    # 準備每個指標的值列表
    metric_to_values: Dict[str, List[float]] = {k: [] for k in metric_keys}
    for item in subjects_raw:
        r = item["raw"]
        metric_to_values["accuracy_pct"].append(r["accuracy_pct"])  # higher better
        metric_to_values["qpm"].append(r["qpm"])  # higher better
        # invert dwell for normalization: use reciprocal to turn lower-better into higher-better
        inv_dwell = 1.0 / r["dwell_min"] if r["dwell_min"] and r["dwell_min"] > 0 else 0.0
        metric_to_values["dwell_min"].append(inv_dwell)
        metric_to_values["questions_count"].append(float(r["questions_count"]))
        metric_to_values["avg_q_per_session"].append(r["avg_q_per_session"]) 
        metric_to_values["sessions_count"].append(float(r["sessions_count"]))

    # 計算 normalized
    normalized_map: Dict[str, List[float]] = {}
    for key, values in metric_to_values.items():
        normalized_map[key] = min_max(values)

    # 組裝輸出
    subjects_out: List[Dict[str, Any]] = []
    for idx, item in enumerate(subjects_raw):
        r = item["raw"]
        subjects_out.append(
            {
                "subject_id": item["subject"],
                "label": item["subject"],
                "raw": r,
                "normalized": {
                    "accuracy_pct": normalized_map["accuracy_pct"][idx] if subjects_raw else 0.0,
                    "qpm": normalized_map["qpm"][idx] if subjects_raw else 0.0,
                    # note: dwell_min normalized is computed from inverse dwell for higher-better scaling
                    "dwell_min": normalized_map["dwell_min"][idx] if subjects_raw else 0.0,
                    "questions_count": normalized_map["questions_count"][idx] if subjects_raw else 0.0,
                    "avg_q_per_session": normalized_map["avg_q_per_session"][idx] if subjects_raw else 0.0,
                    "sessions_count": normalized_map["sessions_count"][idx] if subjects_raw else 0.0,
                },
            }
        )

    return {
        "window": f"{days}d",
        "metrics": metric_keys,
        "subjects": subjects_out,
    }


@router.get("/subjects/trend")
async def get_subjects_trend(
    metric: str = Query("accuracy", regex="^(accuracy|score)$", description="指標: accuracy 或 score"),
    window: str = Query("30d", description="時間範圍 (7d, 30d, 90d)"),
    limit: int = Query(100, ge=1, le=500, description="每科目最大點數"),
    subject: Optional[str] = Query(None, description="單一科目過濾"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    """取得各科目的每次會話趨勢資料。"""
    days = _parse_window_days(window)
    user_id_int = _safe_int(current_user.user_id)
    if user_id_int is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id in token")

    try:
        window_start = datetime.utcnow() - timedelta(days=days)
        # 先抓取每科目 x=開始時間、y=accuracy/score 的 per-session 聚合
        # accuracy = AVG(is_correct::int)
        acc_expr = func.avg(cast(case((ExerciseRecord.is_correct == True, 1), else_=0), Float))
        score_expr = func.avg(cast(ExerciseRecord.score, Float))
        y_expr = acc_expr if metric == "accuracy" else score_expr

        stmt = (
            select(
                ExerciseRecord.subject.label("subject"),
                ExerciseRecord.session_id.label("session_id"),
                LearningSession.start_time.label("x"),
                y_expr.label("y"),
            )
            .join(LearningSession, LearningSession.id == ExerciseRecord.session_id)
            .where(
                ExerciseRecord.user_id == user_id_int,
                ExerciseRecord.created_at >= window_start,
                *(
                    [ExerciseRecord.subject == subject]
                    if subject is not None and subject != ""
                    else []
                ),
            )
            .group_by(ExerciseRecord.subject, ExerciseRecord.session_id, LearningSession.start_time)
            .order_by(LearningSession.start_time.asc())
        )

        rows = (await db_session.execute(stmt)).all()
    except Exception as e:
        logger.error(f"Trend aggregation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Trend aggregation failed")

    # 整理為 { subject -> list of points }
    series_map: Dict[str, List[Dict[str, Any]]] = {}
    for subj, _session_id, x, y in rows:
        if subj not in series_map:
            series_map[subj] = []
        # accuracy 0..1, score 0..100 (如果為 None，給 0)
        y_value = float(y) if y is not None else 0.0
        series_map[subj].append({"x": x.isoformat() if x else None, "y": y_value})

    # 依每科目限制點數
    out_series: List[Dict[str, Any]] = []
    for subj, points in series_map.items():
        if limit and len(points) > limit:
            points = points[-limit:]  # 取最新的 limit 筆
        out_series.append({"subject_id": subj, "label": subj, "points": points})

    return {
        "window": f"{days}d",
        "metric": metric,
        "series": out_series,
    }


