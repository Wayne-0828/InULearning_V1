"""
Weakness Analysis Service

This service handles learning weakness analysis using AI agents.
"""

from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from ..ai_agents.analyst_agent import AnalystAgent
from ..models.schemas import WeaknessAnalysisRequest, WeaknessAnalysisResponse
from ..models.database import WeaknessAnalysis as WeaknessAnalysisModel
from sqlalchemy.orm import Session
import uuid


class WeaknessAnalysisService:
    """弱點分析服務"""
    
    def __init__(self, db_session: Session, gemini_api_key: str):
        self.db_session = db_session
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=gemini_api_key,
            temperature=0.3
        )
        self.analyst_agent = AnalystAgent(self.llm)
    
    def analyze_weaknesses(self, request: WeaknessAnalysisRequest) -> WeaknessAnalysisResponse:
        """分析學習弱點"""
        try:
            # 使用 AI Agent 進行分析
            analysis_result = self.analyst_agent.analyze_weaknesses(request)
            
            # 保存分析結果到資料庫
            self._save_analysis_result(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            # 錯誤處理：返回基本分析結果
            return self._create_basic_analysis(request)
    
    def get_analysis_by_session(self, session_id: str) -> Optional[WeaknessAnalysisResponse]:
        """根據會話ID獲取分析結果"""
        try:
            db_result = self.db_session.query(WeaknessAnalysisModel).filter(
                WeaknessAnalysisModel.session_id == session_id
            ).first()
            
            if not db_result:
                return None
            
            # 轉換為回應格式
            return WeaknessAnalysisResponse(
                session_id=db_result.session_id,
                user_id=db_result.user_id,
                overall_score=db_result.overall_score,
                accuracy_rate=db_result.accuracy_rate,
                average_time=db_result.average_time,
                weakness_points=db_result.weakness_points,
                learning_insights=db_result.learning_insights,
                next_steps=db_result.next_steps,
                analysis_timestamp=db_result.analysis_timestamp
            )
            
        except Exception as e:
            return None
    
    def get_user_analysis_history(self, user_id: str, limit: int = 10) -> list:
        """獲取用戶分析歷史"""
        try:
            db_results = self.db_session.query(WeaknessAnalysisModel).filter(
                WeaknessAnalysisModel.user_id == user_id
            ).order_by(WeaknessAnalysisModel.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "session_id": result.session_id,
                    "subject": result.subject,
                    "overall_score": result.overall_score,
                    "accuracy_rate": result.accuracy_rate,
                    "analysis_timestamp": result.analysis_timestamp,
                    "created_at": result.created_at
                }
                for result in db_results
            ]
            
        except Exception as e:
            return []
    
    def _save_analysis_result(self, analysis_result: WeaknessAnalysisResponse):
        """保存分析結果到資料庫"""
        try:
            db_analysis = WeaknessAnalysisModel(
                id=str(uuid.uuid4()),
                session_id=analysis_result.session_id,
                user_id=analysis_result.user_id,
                subject="math",  # 這裡應該從請求中獲取
                grade="7A",      # 這裡應該從請求中獲取
                version="nanyi", # 這裡應該從請求中獲取
                overall_score=analysis_result.overall_score,
                accuracy_rate=analysis_result.accuracy_rate,
                average_time=analysis_result.average_time,
                weakness_points=[wp.dict() for wp in analysis_result.weakness_points],
                learning_insights=analysis_result.learning_insights,
                next_steps=analysis_result.next_steps,
                analysis_timestamp=analysis_result.analysis_timestamp
            )
            
            self.db_session.add(db_analysis)
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            # 記錄錯誤但不中斷流程
            print(f"Error saving analysis result: {e}")
    
    def _create_basic_analysis(self, request: WeaknessAnalysisRequest) -> WeaknessAnalysisResponse:
        """創建基本分析結果（當AI分析失敗時）"""
        accuracy_rate = request.correct_count / request.total_questions
        
        return WeaknessAnalysisResponse(
            session_id=request.session_id,
            user_id=request.user_id,
            overall_score=accuracy_rate * 100,
            accuracy_rate=accuracy_rate,
            average_time=request.total_time / request.total_questions,
            weakness_points=[
                {
                    "knowledge_point": f"{request.subject.value}基礎概念",
                    "weakness_level": "medium" if accuracy_rate < 0.8 else "low",
                    "error_pattern": "概念理解需要加強",
                    "improvement_suggestion": "建議多練習基礎題型，鞏固核心概念",
                    "related_questions": []
                }
            ],
            learning_insights=f"學生在{request.subject.value}科目表現{'良好' if accuracy_rate >= 0.8 else '需要改進'}",
            next_steps=["繼續練習", "複習基礎概念", "尋求教師指導"]
        ) 