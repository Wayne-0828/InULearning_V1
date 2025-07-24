"""
自定義異常類別

定義學習服務中使用的各種異常類型
"""

from typing import Optional, Dict, Any


class LearningException(Exception):
    """學習服務基礎異常類別"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "LEARNING_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class QuestionBankException(LearningException):
    """題庫服務異常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="QUESTION_BANK_ERROR",
            status_code=503,
            details=details
        )


class AIAnalysisException(LearningException):
    """AI 分析服務異常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AI_ANALYSIS_ERROR",
            status_code=503,
            details=details
        )


class SessionNotFoundException(LearningException):
    """會話不存在異常"""
    
    def __init__(self, session_id: str):
        super().__init__(
            message=f"會話 {session_id} 不存在",
            error_code="SESSION_NOT_FOUND",
            status_code=404,
            details={"session_id": session_id}
        )


class InvalidSessionException(LearningException):
    """無效會話異常"""
    
    def __init__(self, session_id: str, reason: str):
        super().__init__(
            message=f"會話 {session_id} 無效: {reason}",
            error_code="INVALID_SESSION",
            status_code=400,
            details={"session_id": session_id, "reason": reason}
        )


class ExerciseCreationException(LearningException):
    """練習創建異常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="EXERCISE_CREATION_ERROR",
            status_code=400,
            details=details
        )


class AnswerSubmissionException(LearningException):
    """答案提交異常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="ANSWER_SUBMISSION_ERROR",
            status_code=400,
            details=details
        )


class DatabaseException(LearningException):
    """資料庫異常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details
        )


class ValidationException(LearningException):
    """資料驗證異常"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details={"field": field, **details} if details else {"field": field}
        )


class AuthenticationException(LearningException):
    """認證異常"""
    
    def __init__(self, message: str = "認證失敗", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationException(LearningException):
    """授權異常"""
    
    def __init__(self, message: str = "權限不足", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details
        )


class RateLimitException(LearningException):
    """速率限制異常"""
    
    def __init__(self, message: str = "請求過於頻繁", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=429,
            details=details
        ) 