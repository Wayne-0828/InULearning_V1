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

# 載入環境變數
load_dotenv()

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from gemini_api import student_learning_evaluation, solution_guidance
    GEMINI_AVAILABLE = True
except ImportError as e:
    print(f"警告: 無法導入 Gemini API: {e}")
    GEMINI_AVAILABLE = False

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

# 啟動時初始化資料表（容器模式不會走 __main__）
@app.on_event("startup")
async def on_startup():
    if PSYCOPG2_AVAILABLE:
        try:
            init_ai_results_table()
        except Exception as e:
            print(f"啟動時初始化 ai_analysis_results 失敗: {e}")

# 請求模型
class AIAnalysisRequest(BaseModel):
    question: Dict[str, Any]
    student_answer: str
    temperature: float = 1.0
    max_output_tokens: int = 512

# 回應模型
class AIAnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str

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


def init_ai_results_table():
    """在啟動時建立 ai_analysis_results 資料表（若不存在）。"""
    try:
        conn = get_db_connection()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_analysis_results (
                    id UUID PRIMARY KEY,
                    exercise_record_id UUID NOT NULL,
                    status VARCHAR(32) NOT NULL,
                    weakness_analysis TEXT NULL,
                    learning_guidance TEXT NULL,
                    error TEXT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
                """
            )
        conn.close()
    except Exception as e:
        print(f"警告: 建立 ai_analysis_results 資料表失敗: {e}")


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
                    error = COALESCE(%s, error),
                    updated_at = NOW()
                WHERE id = %s
                """,
                (status, weakness, guidance, error, str(task_id))
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


def process_analysis_task(task_id: uuid.UUID, exercise_record_id: str, temperature: float = 1.0, max_output_tokens: int = 512):
    """背景任務：從 DB 取資料，呼叫 Gemini，回寫結果。"""
    try:
        update_task_status(task_id, status="processing")

        record = fetch_exercise_record(exercise_record_id)
        question = record["question"]
        student_answer = record["student_answer"]

        # 呼叫 Gemini
        eval_result = student_learning_evaluation(question, student_answer, temperature, max_output_tokens)
        guide_result = solution_guidance(question, student_answer, temperature, max_output_tokens)

        weakness_text = eval_result.get("學生學習狀況評估") if isinstance(eval_result, dict) else str(eval_result)
        guidance_text = guide_result.get("題目詳解與教學建議") if isinstance(guide_result, dict) else str(guide_result)

        update_task_status(task_id, status="succeeded", weakness=weakness_text, guidance=guidance_text)
    except Exception as e:
        update_task_status(task_id, status="failed", error=str(e))

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
    return {
        "status": "healthy",
        "service": "inulearning-ai-service",
        "version": "1.0.0",
        "gemini_available": GEMINI_AVAILABLE,
        "db_driver_available": PSYCOPG2_AVAILABLE
    }

# AI 弱點分析端點
@app.post("/api/v1/weakness-analysis/question-analysis", response_model=AIAnalysisResponse)
async def analyze_weakness(request: AIAnalysisRequest):
    """AI 弱點分析"""
    if not GEMINI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gemini API 不可用")
    
    try:
        result = student_learning_evaluation(
            question=request.question,
            student_answer=request.student_answer,
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens
        )
        
        return {
            "success": True,
            "data": result,
            "message": "AI 弱點分析完成"
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
        result = solution_guidance(
            question=request.question,
            student_answer=request.student_answer,
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens
        )
        
        return {
            "success": True,
            "data": result,
            "message": "學習建議生成完成"
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

    task_id = uuid.uuid4()
    upsert_task_initial(task_id, normalized_record_id)

    # 送入背景處理
    background_tasks.add_task(process_analysis_task, task_id, normalized_record_id)

    return {
        "success": True,
        "task_id": str(task_id),
        "message": "queued"
    }


@app.get("/api/v1/ai/analysis/{task_id}")
async def get_ai_analysis_status(task_id: str):
    if not PSYCOPG2_AVAILABLE:
        raise HTTPException(status_code=503, detail="資料庫驅動不可用")

    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="找不到任務")

    data: Optional[Dict[str, Any]] = None
    if task["status"] == "succeeded":
        data = {
            "學生學習狀況評估": task.get("weakness_analysis"),
            "題目詳解與教學建議": task.get("learning_guidance")
        }

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
    
    # 初始化資料表
    try:
        init_ai_results_table()
    except Exception as e:
        print(f"⚠️  警告: 初始化資料表時發生錯誤: {e}")

    # 啟動服務
    uvicorn.run(
        "start_ai_service:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
