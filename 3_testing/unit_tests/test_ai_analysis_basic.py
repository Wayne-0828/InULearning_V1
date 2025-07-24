import pytest
from unittest.mock import Mock, patch

def test_basic_imports():
    """測試基本模組導入"""
    try:
        from pydantic import BaseModel
        print("✓ Pydantic 導入成功")
    except ImportError as e:
        pytest.fail(f"Pydantic 導入失敗: {e}")
    
    try:
        import fastapi
        print("✓ FastAPI 導入成功")
    except ImportError as e:
        pytest.fail(f"FastAPI 導入失敗: {e}")

def test_schemas_import():
    """測試 schemas 模組導入"""
    try:
        from src.models.schemas import WeaknessAnalysisRequest, WeaknessAnalysisResponse
        print("✓ Schemas 導入成功")
    except ImportError as e:
        pytest.fail(f"Schemas 導入失敗: {e}")

def test_services_import():
    """測試 services 模組導入"""
    try:
        from src.services.weakness_analysis_service import WeaknessAnalysisService
        print("✓ WeaknessAnalysisService 導入成功")
    except ImportError as e:
        pytest.fail(f"WeaknessAnalysisService 導入失敗: {e}")

def test_ai_agents_import():
    """測試 AI agents 模組導入"""
    try:
        from src.ai_agents.analyst_agent import AnalystAgent
        print("✓ AnalystAgent 導入成功")
    except ImportError as e:
        pytest.fail(f"AnalystAgent 導入失敗: {e}")

def test_config_import():
    """測試配置模組導入"""
    try:
        from src.utils.config import get_settings
        print("✓ Config 導入成功")
    except ImportError as e:
        pytest.fail(f"Config 導入失敗: {e}")

def test_database_import():
    """測試資料庫模組導入"""
    try:
        from src.utils.database import get_db
        print("✓ Database 導入成功")
    except ImportError as e:
        pytest.fail(f"Database 導入失敗: {e}")

def test_main_app_import():
    """測試主應用程式導入"""
    try:
        from src.main import app
        print("✓ Main app 導入成功")
    except ImportError as e:
        pytest.fail(f"Main app 導入失敗: {e}")

def test_basic_schema_creation():
    """測試基本 schema 創建"""
    from src.models.schemas import WeaknessAnalysisRequest, AnswerRecord, Subject, Grade, Version
    
    # 創建測試資料
    answer_record = AnswerRecord(
        question_id="q001",
        student_answer="A",
        is_correct=False,
        time_spent=45,
        confidence_score=0.8
    )
    
    request = WeaknessAnalysisRequest(
        session_id="test-session-001",
        user_id="test-user-001",
        subject=Subject.MATH,
        grade=Grade.GRADE_7A,
        version=Version.NANYI,
        answer_records=[answer_record],
        total_questions=1,
        correct_count=0,
        total_time=45
    )
    
    assert request.session_id == "test-session-001"
    assert request.user_id == "test-user-001"
    assert request.subject == Subject.MATH
    assert len(request.answer_records) == 1
    assert request.answer_records[0].question_id == "q001"

def test_service_creation():
    """測試服務創建"""
    from src.services.weakness_analysis_service import WeaknessAnalysisService
    
    with patch('src.services.weakness_analysis_service.ChatGoogleGenerativeAI'):
        with patch('src.services.weakness_analysis_service.AnalystAgent'):
            mock_db = Mock()
            service = WeaknessAnalysisService(mock_db, "test-api-key")
            assert service is not None
            assert service.db_session == mock_db

def test_agent_creation():
    """測試 AI 代理創建"""
    from src.ai_agents.analyst_agent import AnalystAgent
    
    with patch('src.ai_agents.analyst_agent.ChatGoogleGenerativeAI'):
        with patch('src.ai_agents.analyst_agent.Agent'):
            mock_llm = Mock()
            agent = AnalystAgent(mock_llm)
            assert agent is not None
            assert agent.llm == mock_llm 