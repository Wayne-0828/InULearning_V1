"""
Learning Service Pydantic Schemas

定義所有學習服務 API 的請求和響應模型
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator


class SessionStatus(str, Enum):
    """會話狀態枚舉"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ExerciseParams(BaseModel):
    """練習參數"""
    subject: str = Field(..., description="科目")
    grade: Optional[str] = Field(None, description="年級")
    chapter: Optional[str] = Field(None, description="章節")
    difficulty: Optional[str] = Field("medium", description="難度等級")
    question_count: int = Field(10, ge=1, le=50, description="題目數量")
    question_types: Optional[List[str]] = Field(None, description="題目類型")
    time_limit: Optional[int] = Field(None, description="時間限制(分鐘)")
    
    class Config:
        schema_extra = {
            "example": {
                "subject": "數學",
                "grade": "國中一年級", 
                "chapter": "一元一次方程式",
                "difficulty": "medium",
                "question_count": 10,
                "question_types": ["選擇題", "填空題"],
                "time_limit": 30
            }
        }


class Answer(BaseModel):
    """答案提交"""
    question_id: str = Field(..., description="題目ID")
    answer: Union[str, List[str]] = Field(..., description="答案內容")
    time_spent: Optional[int] = Field(None, description="答題時間(秒)")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="信心度")
    
    class Config:
        schema_extra = {
            "example": {
                "question_id": "q_123456",
                "answer": "A",
                "time_spent": 45,
                "confidence": 0.8
            }
        }


class SubmissionResult(BaseModel):
    """提交結果"""
    question_id: str
    is_correct: bool
    correct_answer: Union[str, List[str]]
    explanation: Optional[str] = None
    score: float = Field(ge=0, le=100)
    
    class Config:
        schema_extra = {
            "example": {
                "question_id": "q_123456",
                "is_correct": True,
                "correct_answer": "A",
                "explanation": "根據一元一次方程式的解法...",
                "score": 100.0
            }
        }


class Question(BaseModel):
    """題目資訊"""
    question_id: str
    content: str
    question_type: str
    options: Optional[List[str]] = None
    difficulty: str
    subject: str
    chapter: Optional[str] = None
    estimated_time: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "question_id": "q_123456",
                "content": "解方程式 2x + 3 = 7",
                "question_type": "填空題",
                "options": None,
                "difficulty": "medium",
                "subject": "數學",
                "chapter": "一元一次方程式",
                "estimated_time": 60
            }
        }


class ExerciseResponse(BaseModel):
    """練習創建響應"""
    session_id: str
    questions: List[Question]
    estimated_time: int = Field(description="預估完成時間(分鐘)")
    created_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_123456",
                "questions": [],
                "estimated_time": 30,
                "created_at": "2024-01-01T10:00:00"
            }
        }


class SessionSummary(BaseModel):
    """會話摘要"""
    session_id: str
    subject: str
    grade: Optional[str] = None
    chapter: Optional[str] = None
    status: SessionStatus
    total_questions: int
    answered_questions: int
    correct_answers: int
    score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    time_spent: Optional[int] = None  # 秒數


class SessionList(BaseModel):
    """會話列表響應"""
    sessions: List[SessionSummary]
    total: int
    page: int
    per_page: int
    
    class Config:
        schema_extra = {
            "example": {
                "sessions": [],
                "total": 100,
                "page": 1,
                "per_page": 20
            }
        }


class SessionDetail(BaseModel):
    """會話詳細資訊"""
    session_id: str
    subject: str
    grade: Optional[str] = None
    chapter: Optional[str] = None
    status: SessionStatus
    questions: List[Question]
    answers: List[Dict[str, Any]]
    results: List[SubmissionResult]
    total_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    time_spent: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_123456",
                "subject": "數學",
                "grade": "國中一年級",
                "chapter": "一元一次方程式",
                "status": "completed",
                "questions": [],
                "answers": [],
                "results": [],
                "total_score": 85.5,
                "created_at": "2024-01-01T10:00:00",
                "completed_at": "2024-01-01T10:30:00",
                "time_spent": 1800
            }
        }


class LearningRecord(BaseModel):
    """學習記錄"""
    record_id: str
    session_id: str
    question_id: str
    answer: Union[str, List[str]]
    is_correct: bool
    score: float
    time_spent: int
    created_at: datetime


class LearningHistory(BaseModel):
    """學習歷史"""
    user_id: str
    records: List[LearningRecord]
    total_sessions: int
    total_questions: int
    correct_rate: float
    average_score: float
    total_time_spent: int  # 秒數
    subjects: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_123456",
                "records": [],
                "total_sessions": 25,
                "total_questions": 250,
                "correct_rate": 0.85,
                "average_score": 82.5,
                "total_time_spent": 45000,
                "subjects": ["數學", "英文", "物理"]
            }
        }


class RecommendationRequest(BaseModel):
    """推薦請求"""
    user_id: str
    subject: Optional[str] = None
    max_recommendations: int = Field(5, ge=1, le=20)
    include_weak_areas: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_123456",
                "subject": "數學",
                "max_recommendations": 5,
                "include_weak_areas": True
            }
        }


class Recommendation(BaseModel):
    """推薦內容"""
    recommendation_id: str
    title: str
    description: str
    subject: str
    chapter: str
    difficulty: str
    estimated_time: int
    reason: str
    priority: float = Field(ge=0, le=1)
    
    class Config:
        schema_extra = {
            "example": {
                "recommendation_id": "rec_123456",
                "title": "一元一次方程式加強練習",
                "description": "針對您在一元一次方程式的薄弱環節設計的練習",
                "subject": "數學",
                "chapter": "一元一次方程式", 
                "difficulty": "medium",
                "estimated_time": 20,
                "reason": "根據您的答題記錄，在此章節的正確率較低",
                "priority": 0.9
            }
        }


class RecommendationResponse(BaseModel):
    """推薦響應"""
    recommendations: List[Recommendation]
    generated_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "recommendations": [],
                "generated_at": "2024-01-01T10:00:00"
            }
        }


class QuestionResult(BaseModel):
    """題目結果"""
    question_id: str
    question: Question
    answer: Union[str, List[str]]
    is_correct: bool
    score: float
    time_spent: Optional[int] = None
    explanation: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "question_id": "q_123456",
                "question": {},
                "answer": "A",
                "is_correct": True,
                "score": 100.0,
                "time_spent": 45,
                "explanation": "正確答案是 A，因為..."
            }
        }


class WeaknessAnalysis(BaseModel):
    """薄弱環節分析"""
    subject: str
    chapter: str
    weakness_score: float = Field(ge=0, le=1, description="薄弱程度 0-1")
    error_patterns: List[str] = Field(default_factory=list)
    recommended_practice: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "subject": "數學",
                "chapter": "一元一次方程式",
                "weakness_score": 0.7,
                "error_patterns": ["計算錯誤", "符號處理錯誤"],
                "recommended_practice": ["基礎計算練習", "符號運算練習"],
                "improvement_suggestions": ["多做基礎練習", "注意符號變化"]
            }
        }


class TrendData(BaseModel):
    """趨勢資料"""
    date: datetime
    score: float
    correct_rate: float
    time_spent: int
    questions_answered: int
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2024-01-01T10:00:00",
                "score": 85.5,
                "correct_rate": 0.85,
                "time_spent": 1800,
                "questions_answered": 20
            }
        }


class TrendAnalysis(BaseModel):
    """趨勢分析"""
    user_id: str
    subject: Optional[str] = None
    period_days: int = Field(30, description="分析期間(天)")
    trend_data: List[TrendData]
    overall_trend: str = Field(description="整體趨勢: improving/stable/declining")
    average_score: float
    score_change: float = Field(description="分數變化")
    recommendations: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_123456",
                "subject": "數學",
                "period_days": 30,
                "trend_data": [],
                "overall_trend": "improving",
                "average_score": 82.5,
                "score_change": 5.2,
                "recommendations": ["繼續保持", "加強練習"]
            }
        }


class LearningRecommendation(BaseModel):
    """學習推薦"""
    recommendation_id: str
    user_id: str
    title: str
    description: str
    subject: str
    chapter: Optional[str] = None
    difficulty: str
    estimated_time: int = Field(description="預估完成時間(分鐘)")
    priority: float = Field(ge=0, le=1, description="優先級")
    reason: str = Field(description="推薦原因")
    action_type: str = Field(description="行動類型: practice/review/learn")
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "recommendation_id": "rec_123456",
                "user_id": "user_123456",
                "title": "一元一次方程式加強練習",
                "description": "針對您在一元一次方程式的薄弱環節設計的練習",
                "subject": "數學",
                "chapter": "一元一次方程式",
                "difficulty": "medium",
                "estimated_time": 20,
                "priority": 0.9,
                "reason": "根據您的答題記錄，在此章節的正確率較低",
                "action_type": "practice",
                "created_at": "2024-01-01T10:00:00",
                "expires_at": "2024-01-08T10:00:00"
            }
        }


class LearningTrend(BaseModel):
    """學習趨勢"""
    user_id: str
    subject: str
    period_start: datetime
    period_end: datetime
    trend_direction: str = Field(description="趨勢方向: up/down/stable")
    score_trend: List[float] = Field(description="分數趨勢")
    accuracy_trend: List[float] = Field(description="正確率趨勢")
    time_trend: List[int] = Field(description="時間趨勢")
    improvement_rate: float = Field(description="改進率")
    predicted_next_score: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_123456",
                "subject": "數學",
                "period_start": "2024-01-01T00:00:00",
                "period_end": "2024-01-31T23:59:59",
                "trend_direction": "up",
                "score_trend": [75.0, 78.5, 82.0, 85.5],
                "accuracy_trend": [0.75, 0.785, 0.82, 0.855],
                "time_trend": [1800, 1650, 1500, 1400],
                "improvement_rate": 0.14,
                "predicted_next_score": 88.0
            }
        }


class PerformancePrediction(BaseModel):
    """表現預測"""
    user_id: str
    subject: str
    prediction_horizon: int = Field(description="預測時間範圍(天)")
    predicted_score: float = Field(ge=0, le=100)
    confidence_interval: List[float] = Field(description="信心區間 [下限, 上限]")
    confidence_level: float = Field(ge=0, le=1, description="信心水準")
    key_factors: List[str] = Field(description="影響因素")
    recommendations: List[str] = Field(description="建議事項")
    prediction_date: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_123456",
                "subject": "數學",
                "prediction_horizon": 7,
                "predicted_score": 88.5,
                "confidence_interval": [85.0, 92.0],
                "confidence_level": 0.95,
                "key_factors": ["練習頻率", "正確率趨勢", "時間投入"],
                "recommendations": ["保持練習頻率", "加強薄弱章節"],
                "prediction_date": "2024-01-01T10:00:00"
            }
        }


# ===============================================
# 新增的練習結果提交和歷程查詢相關 Schemas
# ===============================================

class ExerciseResult(BaseModel):
    """單個練習結果"""
    question_id: str = Field(..., description="題目ID")
    subject: str = Field(..., description="科目")
    grade: str = Field(..., description="年級")
    chapter: Optional[str] = Field(None, description="章節")
    publisher: str = Field("南一", description="出版社")
    knowledge_points: List[str] = Field(default_factory=list, description="知識點")
    question_content: str = Field(..., description="題目內容")
    answer_choices: Optional[Dict[str, Any]] = Field(None, description="選項")
    difficulty: str = Field("normal", description="難度")
    question_topic: Optional[str] = Field(None, description="題目主題")
    user_answer: str = Field(..., description="用戶答案")
    correct_answer: str = Field(..., description="正確答案")
    is_correct: bool = Field(..., description="是否正確")
    score: float = Field(..., ge=0, le=100, description="得分")
    explanation: Optional[str] = Field(None, description="解釋")
    time_spent: Optional[int] = Field(None, description="答題時間(秒)")
    
    class Config:
        schema_extra = {
            "example": {
                "question_id": "q_123456",
                "subject": "數學",
                "grade": "8A",
                "chapter": "一元一次方程式",
                "publisher": "南一",
                "knowledge_points": ["一元一次方程式", "移項運算"],
                "question_content": "解方程式 2x + 3 = 7",
                "answer_choices": {"A": "x = 2", "B": "x = 3", "C": "x = 4", "D": "x = 5"},
                "difficulty": "normal",
                "question_topic": "一元一次方程式解法",
                "user_answer": "A",
                "correct_answer": "A",
                "is_correct": True,
                "score": 100.0,
                "explanation": "移項得到 2x = 4，所以 x = 2",
                "time_spent": 45
            }
        }


class CompleteExerciseRequest(BaseModel):
    """完成練習請求"""
    session_name: str = Field(..., description="會話名稱")
    subject: str = Field(..., description="科目")
    grade: str = Field(..., description="年級")
    chapter: Optional[str] = Field(None, description="章節")
    publisher: str = Field("南一", description="出版社")
    difficulty: Optional[str] = Field("normal", description="難度")
    knowledge_points: List[str] = Field(default_factory=list, description="會話知識點")
    exercise_results: List[ExerciseResult] = Field(..., description="練習結果列表")
    total_time_spent: Optional[int] = Field(None, description="總耗時(秒)")
    session_metadata: Optional[Dict[str, Any]] = Field(None, description="會話元數據")
    
    class Config:
        schema_extra = {
            "example": {
                "session_name": "數學練習 - 一元一次方程式",
                "subject": "數學",
                "grade": "8A",
                "chapter": "一元一次方程式",
                "publisher": "南一",
                "difficulty": "normal",
                "knowledge_points": ["一元一次方程式", "移項運算"],
                "exercise_results": [],
                "total_time_spent": 1800,
                "session_metadata": {"source": "web", "device": "desktop"}
            }
        }


class CompleteExerciseResponse(BaseModel):
    """完成練習響應"""
    session_id: str = Field(..., description="會話ID")
    total_questions: int = Field(..., description="總題數")
    correct_count: int = Field(..., description="答對數")
    total_score: float = Field(..., description="總得分")
    accuracy_rate: float = Field(..., description="正確率")
    time_spent: int = Field(..., description="耗時(秒)")
    created_at: datetime = Field(..., description="創建時間")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "total_questions": 10,
                "correct_count": 8,
                "total_score": 85.5,
                "accuracy_rate": 80.0,
                "time_spent": 1800,
                "created_at": "2024-12-19T10:00:00"
            }
        }


class LearningHistoryQuery(BaseModel):
    """學習歷程查詢參數"""
    subject: Optional[str] = Field(None, description="科目篩選")
    grade: Optional[str] = Field(None, description="年級篩選")
    publisher: Optional[str] = Field(None, description="出版社篩選")
    start_date: Optional[datetime] = Field(None, description="開始日期")
    end_date: Optional[datetime] = Field(None, description="結束日期")
    page: int = Field(1, ge=1, description="頁碼")
    page_size: int = Field(20, ge=1, le=100, description="每頁數量")
    
    class Config:
        schema_extra = {
            "example": {
                "subject": "數學",
                "grade": "8A",
                "publisher": "南一",
                "start_date": "2024-12-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "page": 1,
                "page_size": 20
            }
        }


class LearningSessionSummary(BaseModel):
    """學習會話摘要"""
    session_id: str = Field(..., description="會話ID")
    session_name: str = Field(..., description="會話名稱")
    subject: str = Field(..., description="科目")
    grade: str = Field(..., description="年級")
    chapter: Optional[str] = Field(None, description="章節")
    publisher: str = Field(..., description="出版社")
    difficulty: Optional[str] = Field(None, description="難度")
    knowledge_points: List[str] = Field(default_factory=list, description="知識點")
    question_count: int = Field(..., description="題目數量")
    correct_count: int = Field(..., description="答對數量")
    total_score: float = Field(..., description="總得分")
    accuracy_rate: float = Field(..., description="正確率")
    time_spent: Optional[int] = Field(None, description="耗時(秒)")
    status: str = Field(..., description="狀態")
    start_time: datetime = Field(..., description="開始時間")
    end_time: Optional[datetime] = Field(None, description="結束時間")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "session_name": "數學練習 - 一元一次方程式",
                "subject": "數學",
                "grade": "8A",
                "chapter": "一元一次方程式",
                "publisher": "南一",
                "difficulty": "normal",
                "knowledge_points": ["一元一次方程式", "移項運算"],
                "question_count": 10,
                "correct_count": 8,
                "total_score": 85.5,
                "accuracy_rate": 80.0,
                "time_spent": 1800,
                "status": "completed",
                "start_time": "2024-12-19T10:00:00",
                "end_time": "2024-12-19T10:30:00"
            }
        }


class LearningHistoryResponse(BaseModel):
    """學習歷程響應"""
    sessions: List[LearningSessionSummary] = Field(..., description="會話列表")
    total: int = Field(..., description="總數量")
    page: int = Field(..., description="當前頁碼")
    page_size: int = Field(..., description="每頁數量")
    total_pages: int = Field(..., description="總頁數")
    
    class Config:
        schema_extra = {
            "example": {
                "sessions": [],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5
            }
        }


class LearningStatistics(BaseModel):
    """學習統計"""
    total_sessions: int = Field(..., description="總會話數")
    total_questions: int = Field(..., description="總題目數")
    total_correct: int = Field(..., description="總答對數")
    overall_accuracy: float = Field(..., description="整體正確率")
    total_time_spent: int = Field(..., description="總耗時(秒)")
    subject_stats: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="科目統計")
    recent_performance: List[Dict[str, Any]] = Field(default_factory=list, description="近期表現")
    
    class Config:
        schema_extra = {
            "example": {
                "total_sessions": 25,
                "total_questions": 250,
                "total_correct": 200,
                "overall_accuracy": 80.0,
                "total_time_spent": 45000,
                "subject_stats": {
                    "數學": {"sessions": 10, "accuracy": 85.0, "avg_score": 87.5},
                    "英文": {"sessions": 8, "accuracy": 75.0, "avg_score": 78.0}
                },
                "recent_performance": []
            }
        }


class SessionDetailResponse(BaseModel):
    """會話詳細響應"""
    session: LearningSessionSummary = Field(..., description="會話基本資訊")
    exercise_records: List[Dict[str, Any]] = Field(..., description="練習記錄詳情")
    
    class Config:
        schema_extra = {
            "example": {
                "session": {},
                "exercise_records": []
            }
        }