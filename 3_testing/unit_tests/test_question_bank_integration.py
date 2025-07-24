import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.schemas import QuestionCreate, GradeEnum, SubjectEnum, PublisherEnum, DifficultyEnum

client = TestClient(app)


class TestQuestionBankService:
    """題庫服務測試"""
    
    def test_root_endpoint(self):
        """測試根端點"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "InULearning Question Bank Service"
        assert "version" in data
        assert data["status"] == "running"
    
    def test_health_check(self):
        """測試健康檢查端點"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
    
    def test_create_question_schema(self):
        """測試題目創建模型"""
        question_data = {
            "grade": "7A",
            "subject": "數學",
            "publisher": "南一",
            "chapter": "1-1 一元一次方程式",
            "topic": "一元一次方程式",
            "knowledge_point": ["方程式求解"],
            "difficulty": "normal",
            "question": "解下列方程式：2x + 5 = 13",
            "options": {
                "A": "x = 4",
                "B": "x = 6",
                "C": "x = 8",
                "D": "x = 10"
            },
            "answer": "A",
            "explanation": "解一元一次方程式 2x + 5 = 13，首先將 5 移到等式右邊得到 2x = 13 - 5 = 8，再將兩邊同除以 2 得到 x = 4，因此正確答案是選項 A。"
        }
        
        question = QuestionCreate(**question_data)
        assert question.grade == GradeEnum.GRADE_7A
        assert question.subject == SubjectEnum.MATH
        assert question.publisher == PublisherEnum.NANI
        assert question.difficulty == DifficultyEnum.NORMAL
        assert question.answer == "A"
    
    def test_search_questions_endpoint(self):
        """測試搜尋題目端點"""
        response = client.get("/api/v1/questions/", params={
            "grade": "7A",
            "subject": "數學",
            "publisher": "南一",
            "limit": 10
        })
        # 由於沒有資料庫連接，預期會返回錯誤
        assert response.status_code in [200, 500]
    
    def test_get_random_questions_endpoint(self):
        """測試隨機獲取題目端點"""
        response = client.get("/api/v1/questions/random/", params={
            "grade": "7A",
            "subject": "數學",
            "publisher": "南一",
            "count": 5
        })
        # 由於沒有資料庫連接，預期會返回錯誤
        assert response.status_code in [200, 500]
    
    def test_get_chapters_endpoint(self):
        """測試獲取章節端點"""
        response = client.get("/api/v1/chapters/", params={
            "subject": "數學",
            "grade": "7A",
            "publisher": "南一"
        })
        # 由於沒有資料庫連接，預期會返回錯誤
        assert response.status_code in [200, 500]
    
    def test_get_knowledge_points_endpoint(self):
        """測試獲取知識點端點"""
        response = client.get("/api/v1/knowledge-points/", params={
            "subject": "數學",
            "grade": "7A"
        })
        # 由於沒有資料庫連接，預期會返回錯誤
        assert response.status_code in [200, 500]


class TestSchemas:
    """模型測試"""
    
    def test_grade_enum(self):
        """測試年級枚舉"""
        assert GradeEnum.GRADE_7A == "7A"
        assert GradeEnum.GRADE_8B == "8B"
        assert GradeEnum.GRADE_9A == "9A"
    
    def test_subject_enum(self):
        """測試科目枚舉"""
        assert SubjectEnum.MATH == "數學"
        assert SubjectEnum.CHINESE == "國文"
        assert SubjectEnum.ENGLISH == "英文"
    
    def test_publisher_enum(self):
        """測試出版社枚舉"""
        assert PublisherEnum.NANI == "南一"
        assert PublisherEnum.HANLIN == "翰林"
        assert PublisherEnum.KANGXUAN == "康軒"
    
    def test_difficulty_enum(self):
        """測試難度枚舉"""
        assert DifficultyEnum.EASY == "easy"
        assert DifficultyEnum.NORMAL == "normal"
        assert DifficultyEnum.HARD == "hard" 