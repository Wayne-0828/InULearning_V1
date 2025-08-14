#!/usr/bin/env python3
"""
簡化的 AI 服務啟動腳本

這個腳本提供一個簡單的 FastAPI 服務，直接整合 Gemini API，
不需要複雜的依賴項，只需要基本的 FastAPI 和 Gemini API。
"""

import os
import sys
import json
import uuid
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import datetime

# 載入環境變數
load_dotenv()

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock 設定（需在導入 Gemini 前讀取）
AI_ANALYSIS_MOCK = os.getenv("AI_ANALYSIS_MOCK", "0") == "1"

if not AI_ANALYSIS_MOCK:
    try:
        from gemini_api import student_learning_evaluation, solution_guidance
        GEMINI_AVAILABLE = True
    except ImportError as e:
        print(f"警告: 無法導入 Gemini API: {e}")
        GEMINI_AVAILABLE = False
else:
    GEMINI_AVAILABLE = True

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError as e:
    print(f"錯誤: 缺少資料庫套件: {e}")
    print("請執行: pip install psycopg2-binary")
    PSYCOPG2_AVAILABLE = False

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError as e:
    print(f"錯誤: 缺少必要套件: {e}")
    print("請執行: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# Redis 客戶端
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError as e:
    print(f"警告: 缺少 Redis 套件: {e}")
    print("請執行: pip install redis")
    REDIS_AVAILABLE = False

# 創建 FastAPI 應用
app = FastAPI(
    title="InULearning AI Service",
    description="簡化的 AI 分析服務，整合 Gemini API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 啟動時檢查資料表是否存在（不再主動建表，改由 SQL 初始化/遷移管理）
@app.on_event("startup")
async def on_startup():
    if PSYCOPG2_AVAILABLE:
        try:
            # 檢查資料表存在性
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'ai_analysis_results'
                    LIMIT 1
                """)
                _ = cur.fetchone()
                # 若表存在，確保必要欄位存在
                cur.execute(
                    """
                    DO $$
                    BEGIN
                        IF EXISTS (
                            SELECT 1 FROM information_schema.tables
                            WHERE table_schema='public' AND table_name='ai_analysis_results'
                        ) THEN
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns
                                WHERE table_schema='public' AND table_name='ai_analysis_results' AND column_name='weakness_analysis'
                            ) THEN
                                ALTER TABLE ai_analysis_results ADD COLUMN weakness_analysis TEXT NULL;
                            END IF;
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns
                                WHERE table_schema='public' AND table_name='ai_analysis_results' AND column_name='learning_guidance'
                            ) THEN
                                ALTER TABLE ai_analysis_results ADD COLUMN learning_guidance TEXT NULL;
                            END IF;
                        END IF;
                    END $$;
                    """
                )
            conn.close()
        except Exception as e:
            print(f"啟動檢查 ai_analysis_results 存在性失敗: {e}")

    # 檢查 Redis 連線
    if REDIS_AVAILABLE:
        try:
            _ = get_redis_client().ping()
        except Exception as e:
            print(f"啟動檢查 Redis 連線失敗: {e}")

# 請求模型
class AIAnalysisRequest(BaseModel):
    question: Dict[str, Any]
    student_answer: str
    temperature: float = 1.0
    max_output_tokens: int = 512
    exercise_record_id: Optional[str] = None

# 回應模型
class AIAnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str
    task_id: Optional[str] = None

# 觸發 AI 分析請求模型（使用 exercise_record_id 作為來源）
class AIAnalysisTriggerRequest(BaseModel):
    exercise_record_id: str

    def normalized_uuid(self) -> str:
        try:
            return str(uuid.UUID(self.exercise_record_id))
        except Exception:
            raise HTTPException(status_code=400, detail="exercise_record_id 需為有效的 UUID")

# AI 任務狀態回應
class AIAnalysisTaskStatus(BaseModel):
    success: bool
    status: str
    data: Optional[Dict[str, Any]] = None
    message: str

# 讀取 DB 連線設定
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "aipe-tester")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "aipe-tester")
POSTGRES_DB = os.getenv("POSTGRES_DB", "inulearning")


# Redis 設定
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
AI_CACHE_TTL_SECONDS = int(os.getenv("AI_CACHE_TTL_SECONDS", str(7 * 24 * 60 * 60)))
AI_CACHE_PREFIX = os.getenv("AI_CACHE_PREFIX", "ai:v1:")


def get_db_connection():
    if not PSYCOPG2_AVAILABLE:
        raise RuntimeError("psycopg2 未安裝，無法連接資料庫")
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )


def get_redis_client():
    if not REDIS_AVAILABLE:
        raise RuntimeError("redis 套件未安裝，無法使用快取")
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()


def cache_set_task(task_id: str, exercise_record_id: str, status: str, weakness: Optional[str] = None, guidance: Optional[str] = None, error: Optional[str] = None):
    if not REDIS_AVAILABLE:
        return
    try:
        client = get_redis_client()
        key = f"{AI_CACHE_PREFIX}analysis:task:{task_id}"
        value = {
            "task_id": task_id,
            "exercise_record_id": exercise_record_id,
            "status": status,
            "學生學習狀況評估": weakness,
            "題目詳解與教學建議": guidance,
            "error": error,
            "updated_at": _now_iso()
        }
        client.set(key, json.dumps(value, ensure_ascii=False), ex=AI_CACHE_TTL_SECONDS)
    except Exception as e:
        print(f"寫入 Redis 任務快取失敗: {e}")


def cache_set_record_latest(exercise_record_id: str, task_id: str):
    if not REDIS_AVAILABLE:
        return
    try:
        client = get_redis_client()
        key = f"{AI_CACHE_PREFIX}analysis:record:{exercise_record_id}:latest"
        client.set(key, task_id, ex=AI_CACHE_TTL_SECONDS)
    except Exception as e:
        print(f"寫入 Redis 最新任務索引失敗: {e}")


# 封裝：可切換真實或模擬的 AI 生成功能
def do_student_learning_evaluation(question: Dict[str, Any], student_answer: str, temperature: float, max_output_tokens: int) -> Dict[str, Any]:
    if AI_ANALYSIS_MOCK:
        return {
            "學生學習狀況評估": "[MOCK] 根據該題與作答，學生在此知識點需加強，建議重溫課本基礎概念並配合練習題強化。"
        }
    return student_learning_evaluation(question, student_answer, temperature, max_output_tokens)


def do_solution_guidance(question: Dict[str, Any], student_answer: str, temperature: float, max_output_tokens: int) -> Dict[str, Any]:
    if AI_ANALYSIS_MOCK:
        return {
            "題目詳解與教學建議": "[MOCK] 題目核心為基礎概念運用。建議按步驟演練並回顧易錯點，搭配小範圍練習鞏固。"
        }
    return solution_guidance(question, student_answer, temperature, max_output_tokens)


def init_ai_results_table():
    """Deprecated: 由 SQL 初始化與遷移負責，不在程式中建表。"""
    pass


def fetch_exercise_record(record_id: str) -> Dict[str, Any]:
    """
    從 exercise_records 讀取題目與作答資訊，並組合為 Gemini 所需的題目結構。

    來源欄位（存在於 learning-service 的模型）:
      - subject, grade, chapter, publisher, knowledge_points, difficulty,
        question_content, answer_choices, question_topic, correct_answer,
        explanation, user_answer

    目標題目結構 keys:
      grade, subject, publisher, chapter, topic, knowledge_point, difficulty,
      question, options, answer, explanation
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id,
                       subject,
                       grade,
                       chapter,
                       publisher,
                       knowledge_points,
                       difficulty,
                       question_content,
                       answer_choices,
                       question_topic,
                       correct_answer,
                       explanation,
                       user_answer
                FROM exercise_records
                WHERE id = %s
                LIMIT 1
                """,
                (record_id,)
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="找不到對應的 exercise_record")

            # 組合題目結構
            answer_choices = row.get("answer_choices")
            # 若是字串嘗試解析
            if isinstance(answer_choices, str):
                try:
                    answer_choices = json.loads(answer_choices)
                except json.JSONDecodeError:
                    answer_choices = {}

            question_dict = {
                "grade": row.get("grade"),
                "subject": row.get("subject"),
                "publisher": row.get("publisher"),
                "chapter": row.get("chapter"),
                "topic": row.get("question_topic"),
                "knowledge_point": row.get("knowledge_points") or [],
                "difficulty": row.get("difficulty"),
                "question": row.get("question_content") or "",
                "options": answer_choices or {},
                "answer": row.get("correct_answer") or "",
                "explanation": row.get("explanation") or ""
            }

            return {
                "question": question_dict,
                "student_answer": row.get("user_answer")
            }
    finally:
        conn.close()


def upsert_task_initial(task_id: uuid.UUID, exercise_record_id: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ai_analysis_results (id, exercise_record_id, status)
                VALUES (%s, %s, 'pending')
                ON CONFLICT (id) DO NOTHING
                """,
                (str(task_id), exercise_record_id)
            )
        conn.commit()
    finally:
        conn.close()


def update_task_status(task_id: uuid.UUID, status: str, weakness: Optional[str] = None, guidance: Optional[str] = None, error: Optional[str] = None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE ai_analysis_results
                SET status = %s,
                    weakness_analysis = COALESCE(%s, weakness_analysis),
                    learning_guidance = COALESCE(%s, learning_guidance),
                    weakness_analysis_json = CASE WHEN %s IS NOT NULL THEN jsonb_build_object('text', %s) ELSE weakness_analysis_json END,
                    learning_guidance_json = CASE WHEN %s IS NOT NULL THEN jsonb_build_object('text', %s) ELSE learning_guidance_json END,
                    error = COALESCE(%s, error),
                    updated_at = NOW()
                WHERE id = %s
                """,
                (status, weakness, guidance, weakness, weakness, guidance, guidance, error, str(task_id))
            )
        conn.commit()
    finally:
        conn.close()


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, exercise_record_id, status, weakness_analysis, learning_guidance, error, created_at, updated_at
                FROM ai_analysis_results
                WHERE id = %s
                LIMIT 1
                """,
                (task_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_latest_task_by_record(exercise_record_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, exercise_record_id, status, weakness_analysis, learning_guidance, error, created_at, updated_at
                FROM ai_analysis_results
                WHERE exercise_record_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (exercise_record_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_latest_success_by_record(exercise_record_id: str) -> Optional[Dict[str, Any]]:
    """讀取最新成功且有文字的分析結果。"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, exercise_record_id, status, weakness_analysis, learning_guidance, error, created_at, updated_at
                FROM ai_analysis_results
                WHERE exercise_record_id = %s AND status = 'succeeded'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (exercise_record_id,)
            )
            row = cur.fetchone()
            if row and (row.get("weakness_analysis") or row.get("learning_guidance")):
                return dict(row)
            return None
    finally:
        conn.close()


def process_analysis_task(task_id: uuid.UUID, exercise_record_id: str, temperature: float = 1.0, max_output_tokens: int = 512):
    """背景任務：從 DB 取資料，呼叫 Gemini，回寫結果。"""
    try:
        update_task_status(task_id, status="processing")
        # 快取 processing 狀態（write-through 前的立即可見狀態）
        cache_set_task(str(task_id), exercise_record_id, status="processing")

        record = fetch_exercise_record(exercise_record_id)
        question = record["question"]
        student_answer = record["student_answer"]

        # 呼叫 Gemini
        eval_result = do_student_learning_evaluation(question, student_answer, temperature, max_output_tokens)
        guide_result = do_solution_guidance(question, student_answer, temperature, max_output_tokens)

        weakness_text = eval_result.get("學生學習狀況評估") if isinstance(eval_result, dict) else str(eval_result)
        guidance_text = guide_result.get("題目詳解與教學建議") if isinstance(guide_result, dict) else str(guide_result)

        update_task_status(task_id, status="succeeded", weakness=weakness_text, guidance=guidance_text)
        # 寫入快取（成功結果）並更新最新索引
        cache_set_task(str(task_id), exercise_record_id, status="succeeded", weakness=weakness_text, guidance=guidance_text)
        cache_set_record_latest(exercise_record_id, str(task_id))
    except Exception as e:
        update_task_status(task_id, status="failed", error=str(e))
        cache_set_task(str(task_id), exercise_record_id, status="failed", error=str(e))

# 根路徑
@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "InULearning AI Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "test": "/test"
    }

# 健康檢查
@app.get("/health")
async def health_check():
    """健康檢查端點"""
    redis_connected = False
    if REDIS_AVAILABLE:
        try:
            redis_connected = bool(get_redis_client().ping())
        except Exception:
            redis_connected = False
    status_val = "healthy" if (GEMINI_AVAILABLE and PSYCOPG2_AVAILABLE and (not REDIS_AVAILABLE or redis_connected)) else "degraded"
    return {
        "status": status_val,
        "service": "inulearning-ai-service",
        "version": "1.0.0",
        "gemini_available": GEMINI_AVAILABLE,
        "db_driver_available": PSYCOPG2_AVAILABLE,
        "redis_available": REDIS_AVAILABLE,
        "redis_connected": redis_connected
    }

# AI 弱點分析端點
@app.post("/api/v1/weakness-analysis/question-analysis", response_model=AIAnalysisResponse)
async def analyze_weakness(request: AIAnalysisRequest):
    """AI 弱點分析"""
    if not GEMINI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gemini API 不可用")
    
    try:
        result = do_student_learning_evaluation(
            question=request.question,
            student_answer=request.student_answer,
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens
        )
        # 可選持久化
        task_id: Optional[str] = None
        if request.exercise_record_id:
            try:
                # 正規化 UUID
                normalized_record_id = str(uuid.UUID(request.exercise_record_id))
                # 建立 task id 並持久化
                task_uuid = uuid.uuid4()
                task_id = str(task_uuid)
                upsert_task_initial(task_uuid, normalized_record_id)
                weakness_text = result.get("學生學習狀況評估") if isinstance(result, dict) else str(result)
                update_task_status(task_uuid, status="succeeded", weakness=weakness_text)
                cache_set_task(task_id, normalized_record_id, status="succeeded", weakness=weakness_text)
                cache_set_record_latest(normalized_record_id, task_id)
            except Exception as e:
                # 不阻斷回應
                print(f"同步端點持久化失敗: {e}")
        return {
            "success": True,
            "data": result,
            "message": "AI 弱點分析完成",
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 分析失敗: {str(e)}")

# 學習建議端點
@app.post("/api/v1/learning-recommendation/question-guidance", response_model=AIAnalysisResponse)
async def get_guidance(request: AIAnalysisRequest):
    """學習建議"""
    if not GEMINI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gemini API 不可用")
    
    try:
        result = do_solution_guidance(
            question=request.question,
            student_answer=request.student_answer,
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens
        )
        # 可選持久化
        task_id: Optional[str] = None
        if request.exercise_record_id:
            try:
                normalized_record_id = str(uuid.UUID(request.exercise_record_id))
                task_uuid = uuid.uuid4()
                task_id = str(task_uuid)
                upsert_task_initial(task_uuid, normalized_record_id)
                guidance_text = result.get("題目詳解與教學建議") if isinstance(result, dict) else str(result)
                update_task_status(task_uuid, status="succeeded", guidance=guidance_text)
                cache_set_task(task_id, normalized_record_id, status="succeeded", guidance=guidance_text)
                cache_set_record_latest(normalized_record_id, task_id)
            except Exception as e:
                print(f"同步端點持久化失敗: {e}")
        return {
            "success": True,
            "data": result,
            "message": "學習建議生成完成",
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"學習建議生成失敗: {str(e)}")

# ========== 新增：非同步任務 API ==========
from fastapi import BackgroundTasks

@app.post("/api/v1/ai/analysis")
async def trigger_ai_analysis(request: AIAnalysisTriggerRequest, background_tasks: BackgroundTasks):
    if not GEMINI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gemini API 不可用")
    if not PSYCOPG2_AVAILABLE:
        raise HTTPException(status_code=503, detail="資料庫驅動不可用")

    # 先確認 exercise_record 是否存在並正規化 UUID
    normalized_record_id = request.normalized_uuid()
    try:
        _ = fetch_exercise_record(normalized_record_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讀取作答記錄失敗: {str(e)}")

    # 若已有成功結果，直接返回（不重算）
    # 1) Redis
    if REDIS_AVAILABLE:
        try:
            client = get_redis_client()
            latest_key = f"{AI_CACHE_PREFIX}analysis:record:{normalized_record_id}:latest"
            latest_task_id = client.get(latest_key)
            if latest_task_id:
                cache_key = f"{AI_CACHE_PREFIX}analysis:task:{latest_task_id}"
                cached = client.get(cache_key)
                if cached:
                    obj = json.loads(cached)
                    if obj.get("status") == "succeeded":
                        return {"success": True, "task_id": latest_task_id, "message": "exists"}
        except Exception:
            pass

    # 2) PG
    existing = get_latest_success_by_record(normalized_record_id)
    if existing:
        try:
            cache_set_task(existing.get("id"), normalized_record_id, status="succeeded",
                           weakness=existing.get("weakness_analysis"), guidance=existing.get("learning_guidance"))
            cache_set_record_latest(normalized_record_id, existing.get("id"))
        except Exception:
            pass
        return {"success": True, "task_id": existing.get("id"), "message": "exists"}

    task_id = uuid.uuid4()
    upsert_task_initial(task_id, normalized_record_id)

    # 送入背景處理
    background_tasks.add_task(process_analysis_task, task_id, normalized_record_id)

    return {
        "success": True,
        "task_id": str(task_id),
        "message": "queued"
    }


# 單一端點：一次產生弱點分析與學習建議並可選一次寫入
@app.post("/api/v1/ai/analysis/generate", response_model=AIAnalysisResponse)
async def generate_combined_analysis(request: AIAnalysisRequest):
    if not GEMINI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gemini API 不可用")
    try:
        # 防重算：若帶 exercise_record_id，先查快取→資料庫
        if request.exercise_record_id:
            try:
                normalized_record_id = str(uuid.UUID(request.exercise_record_id))
            except Exception:
                raise HTTPException(status_code=400, detail="exercise_record_id 需為有效的 UUID")

            # 1) Redis 命中
            if REDIS_AVAILABLE:
                try:
                    client = get_redis_client()
                    latest_key = f"{AI_CACHE_PREFIX}analysis:record:{normalized_record_id}:latest"
                    tid = client.get(latest_key)
                    if tid:
                        cache_key = f"{AI_CACHE_PREFIX}analysis:task:{tid}"
                        cached = client.get(cache_key)
                        if cached:
                            obj = json.loads(cached)
                            if obj.get("status") == "succeeded" and (obj.get("學生學習狀況評估") or obj.get("題目詳解與教學建議")):
                                return {
                                    "success": True,
                                    "data": {
                                        "學生學習狀況評估": obj.get("學生學習狀況評估"),
                                        "題目詳解與教學建議": obj.get("題目詳解與教學建議")
                                    },
                                    "message": "cached",
                                    "task_id": tid
                                }
                except Exception:
                    pass

            # 2) PG 命中
            existing = get_latest_success_by_record(normalized_record_id)
            if existing:
                try:
                    cache_set_task(existing.get("id"), normalized_record_id, status="succeeded",
                                   weakness=existing.get("weakness_analysis"), guidance=existing.get("learning_guidance"))
                    cache_set_record_latest(normalized_record_id, existing.get("id"))
                except Exception:
                    pass
                return {
                    "success": True,
                    "data": {
                        "學生學習狀況評估": existing.get("weakness_analysis"),
                        "題目詳解與教學建議": existing.get("learning_guidance")
                    },
                    "message": "db_hit",
                    "task_id": existing.get("id")
                }

        eval_result = do_student_learning_evaluation(
            question=request.question,
            student_answer=request.student_answer,
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens
        )
        guide_result = do_solution_guidance(
            question=request.question,
            student_answer=request.student_answer,
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens
        )

        weakness_text = eval_result.get("學生學習狀況評估") if isinstance(eval_result, dict) else str(eval_result)
        guidance_text = guide_result.get("題目詳解與教學建議") if isinstance(guide_result, dict) else str(guide_result)

        data = {
            "學生學習狀況評估": weakness_text,
            "題目詳解與教學建議": guidance_text
        }

        task_id: Optional[str] = None
        if request.exercise_record_id:
            try:
                normalized_record_id = str(uuid.UUID(request.exercise_record_id))
                task_uuid = uuid.uuid4()
                task_id = str(task_uuid)
                upsert_task_initial(task_uuid, normalized_record_id)
                update_task_status(task_uuid, status="succeeded", weakness=weakness_text, guidance=guidance_text)
                cache_set_task(task_id, normalized_record_id, status="succeeded", weakness=weakness_text, guidance=guidance_text)
                cache_set_record_latest(normalized_record_id, task_id)
            except Exception as e:
                print(f"同步整合端點持久化失敗: {e}")

        return {
            "success": True,
            "data": data,
            "message": "AI 弱點分析與學習建議生成完成",
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"整合生成失敗: {str(e)}")


@app.get("/api/v1/ai/analysis/{task_id}")
async def get_ai_analysis_status(task_id: str):
    if not PSYCOPG2_AVAILABLE:
        raise HTTPException(status_code=503, detail="資料庫驅動不可用")

    # 先讀取快取
    if REDIS_AVAILABLE:
        try:
            client = get_redis_client()
            cache_key = f"{AI_CACHE_PREFIX}analysis:task:{task_id}"
            cached = client.get(cache_key)
            if cached:
                obj = json.loads(cached)
                data = None
                if obj.get("status") == "succeeded":
                    data = {
                        "學生學習狀況評估": obj.get("學生學習狀況評估"),
                        "題目詳解與教學建議": obj.get("題目詳解與教學建議")
                    }
                return {
                    "success": True,
                    "status": obj.get("status"),
                    "data": data,
                    "message": obj.get("error") or "ok"
                }
        except Exception:
            pass

    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="找不到任務")

    data: Optional[Dict[str, Any]] = None
    if task["status"] == "succeeded":
        data = {
            "學生學習狀況評估": task.get("weakness_analysis"),
            "題目詳解與教學建議": task.get("learning_guidance")
        }

    # 回填快取
    if REDIS_AVAILABLE:
        try:
            cache_set_task(task.get("id"), task.get("exercise_record_id"), status=task.get("status"), weakness=task.get("weakness_analysis"), guidance=task.get("learning_guidance"), error=task.get("error"))
            if task.get("status") == "succeeded" and task.get("exercise_record_id"):
                cache_set_record_latest(task.get("exercise_record_id"), task.get("id"))
        except Exception:
            pass

    return {
        "success": True,
        "status": task["status"],
        "data": data,
        "message": task.get("error") or "ok"
    }


@app.get("/api/v1/ai/analysis/by-record/{exercise_record_id}")
async def get_latest_analysis_by_record(exercise_record_id: str):
    if not PSYCOPG2_AVAILABLE:
        raise HTTPException(status_code=503, detail="資料庫驅動不可用")

    try:
        normalized_record_id = str(uuid.UUID(exercise_record_id))
    except Exception:
        raise HTTPException(status_code=400, detail="exercise_record_id 需為有效的 UUID")

    # 先讀 Redis: latest task id -> task payload
    if REDIS_AVAILABLE:
        try:
            client = get_redis_client()
            latest_key = f"{AI_CACHE_PREFIX}analysis:record:{normalized_record_id}:latest"
            latest_task_id = client.get(latest_key)
            if latest_task_id:
                cache_key = f"{AI_CACHE_PREFIX}analysis:task:{latest_task_id}"
                cached = client.get(cache_key)
                if cached:
                    obj = json.loads(cached)
                    data = None
                    if obj.get("status") == "succeeded":
                        data = {
                            "學生學習狀況評估": obj.get("學生學習狀況評估"),
                            "題目詳解與教學建議": obj.get("題目詳解與教學建議")
                        }
                    return {
                        "success": True,
                        "latest_task_id": latest_task_id,
                        "status": obj.get("status"),
                        "data": data,
                        "message": obj.get("error") or "ok"
                    }
        except Exception:
            pass

    task = get_latest_task_by_record(normalized_record_id)
    if not task:
        return {
            "success": True,
            "latest_task_id": None,
            "status": "not_found",
            "data": None,
            "message": "尚無分析結果"
        }

    data: Optional[Dict[str, Any]] = None
    if task["status"] == "succeeded":
        data = {
            "學生學習狀況評估": task.get("weakness_analysis"),
            "題目詳解與教學建議": task.get("learning_guidance")
        }

    # 回填快取
    if REDIS_AVAILABLE and task:
        try:
            cache_set_task(task.get("id"), normalized_record_id, status=task.get("status"), weakness=task.get("weakness_analysis"), guidance=task.get("learning_guidance"), error=task.get("error"))
            cache_set_record_latest(normalized_record_id, task.get("id"))
        except Exception:
            pass

    return {
        "success": True,
        "latest_task_id": task.get("id"),
        "status": task.get("status"),
        "data": data,
        "message": task.get("error") or "ok"
    }

# 代理健康檢查（便於 /api/v1/ai/health 測試）
@app.get("/api/v1/ai/health")
async def ai_health_alias():
    return await health_check()

# 測試端點
@app.get("/test")
async def test_gemini():
    """測試 Gemini API 是否正常工作"""
    if not GEMINI_AVAILABLE:
        return {"status": "error", "message": "Gemini API 不可用"}
    
    try:
        # 測試題目
        test_question = {
            "grade": "7A",
            "subject": "數學",
            "question": "測試題目",
            "options": {"A": "選項A", "B": "選項B", "C": "選項C", "D": "選項D"},
            "answer": "C"
        }
        
        # 測試弱點分析
        weakness_result = student_learning_evaluation(test_question, "B")
        
        # 測試學習建議
        guidance_result = solution_guidance(test_question, "B")
        
        return {
            "status": "success",
            "message": "Gemini API 測試成功",
            "weakness_test": weakness_result,
            "guidance_test": guidance_result
        }
    except Exception as e:
        return {"status": "error", "message": f"Gemini API 測試失敗: {str(e)}"}

if __name__ == "__main__":
    print("🚀 啟動 InULearning AI 服務")
    print("📍 服務地址: http://localhost:8004")
    print("🔧 調試模式: True")
    print("📊 API 文檔: http://localhost:8004/docs")
    print("📋 健康檢查: http://localhost:8004/health")
    print("🧪 測試端點: http://localhost:8004/test")
    print("-" * 50)
    
    if not GEMINI_AVAILABLE:
        print("⚠️  警告: Gemini API 不可用，服務將無法提供 AI 分析功能")
        print("請確保已安裝 google-generativeai 套件並設定 GEMINI_API_KEY")
    if not PSYCOPG2_AVAILABLE:
        print("⚠️  警告: psycopg2 未安裝，將無法連接 PostgreSQL")
    
    # 初始化資料表已改為 SQL 管理，這裡不再執行

    # 啟動服務
    uvicorn.run(
        "start_ai_service:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
