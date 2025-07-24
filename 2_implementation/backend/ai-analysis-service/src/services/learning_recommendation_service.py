"""
Learning Recommendation Service

This service handles learning recommendations using AI agents.
"""

from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from ..ai_agents.tutor_agent import TutorAgent
from ..ai_agents.recommender_agent import RecommenderAgent
from ..models.schemas import (
    LearningRecommendationRequest, 
    LearningRecommendationResponse,
    RecommendedQuestion
)
from ..models.database import LearningRecommendation as LearningRecommendationModel
from sqlalchemy.orm import Session
import uuid


class LearningRecommendationService:
    """學習建議服務"""
    
    def __init__(self, db_session: Session, gemini_api_key: str):
        self.db_session = db_session
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=gemini_api_key,
            temperature=0.4
        )
        self.tutor_agent = TutorAgent(self.llm)
        self.recommender_agent = RecommenderAgent(self.llm)
    
    def generate_recommendations(self, request: LearningRecommendationRequest) -> LearningRecommendationResponse:
        """生成學習建議"""
        try:
            # 使用導師 Agent 生成學習計劃
            recommendation_result = self.tutor_agent.generate_recommendations(request)
            
            # 使用推薦系統 Agent 尋找相似題目
            similar_questions = self.recommender_agent.find_similar_questions(
                knowledge_points=request.weakness_points,
                difficulty=request.target_difficulty,
                count=request.question_count
            )
            
            # 合併推薦題目
            if similar_questions:
                recommendation_result.recommendations = similar_questions
            
            # 保存推薦結果到資料庫
            self._save_recommendation_result(recommendation_result)
            
            return recommendation_result
            
        except Exception as e:
            # 錯誤處理：返回基本推薦結果
            return self._create_basic_recommendation(request)
    
    def get_user_recommendations(self, user_id: str, limit: int = 5) -> List[LearningRecommendationResponse]:
        """獲取用戶推薦歷史"""
        try:
            db_results = self.db_session.query(LearningRecommendationModel).filter(
                LearningRecommendationModel.user_id == user_id
            ).order_by(LearningRecommendationModel.created_at.desc()).limit(limit).all()
            
            recommendations = []
            for result in db_results:
                recommendation = LearningRecommendationResponse(
                    user_id=result.user_id,
                    recommendations=result.recommendations,
                    study_plan=result.study_plan,
                    estimated_time=result.estimated_time,
                    priority_topics=result.priority_topics,
                    confidence_score=result.confidence_score,
                    generated_at=result.generated_at
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            return []
    
    def get_recommendations_by_subject(self, user_id: str, subject: str) -> List[LearningRecommendationResponse]:
        """根據科目獲取推薦"""
        try:
            db_results = self.db_session.query(LearningRecommendationModel).filter(
                LearningRecommendationModel.user_id == user_id,
                LearningRecommendationModel.subject == subject
            ).order_by(LearningRecommendationModel.created_at.desc()).all()
            
            recommendations = []
            for result in db_results:
                recommendation = LearningRecommendationResponse(
                    user_id=result.user_id,
                    recommendations=result.recommendations,
                    study_plan=result.study_plan,
                    estimated_time=result.estimated_time,
                    priority_topics=result.priority_topics,
                    confidence_score=result.confidence_score,
                    generated_at=result.generated_at
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            return []
    
    def _save_recommendation_result(self, recommendation_result: LearningRecommendationResponse):
        """保存推薦結果到資料庫"""
        try:
            db_recommendation = LearningRecommendationModel(
                id=str(uuid.uuid4()),
                user_id=recommendation_result.user_id,
                subject="math",  # 這裡應該從請求中獲取
                grade="7A",      # 這裡應該從請求中獲取
                version="nanyi", # 這裡應該從請求中獲取
                recommendations=[rec.dict() for rec in recommendation_result.recommendations],
                study_plan=recommendation_result.study_plan,
                estimated_time=recommendation_result.estimated_time,
                priority_topics=recommendation_result.priority_topics,
                confidence_score=recommendation_result.confidence_score,
                generated_at=recommendation_result.generated_at
            )
            
            self.db_session.add(db_recommendation)
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            # 記錄錯誤但不中斷流程
            print(f"Error saving recommendation result: {e}")
    
    def _create_basic_recommendation(self, request: LearningRecommendationRequest) -> LearningRecommendationResponse:
        """創建基本推薦結果（當AI推薦失敗時）"""
        # 生成基本推薦題目
        recommendations = []
        for i in range(min(request.question_count, 3)):
            recommendation = RecommendedQuestion(
                question_id=f"basic_{request.user_id}_{i}",
                title=f"{request.subject.value}基礎練習 {i+1}",
                content=f"關於{request.weakness_points[0] if request.weakness_points else '基礎概念'}的練習題",
                difficulty=request.target_difficulty,
                knowledge_points=request.weakness_points[:2],
                similarity_score=0.7 - (i * 0.1),
                explanation="這是一道基礎練習題，幫助鞏固相關概念" if request.include_explanations else None
            )
            recommendations.append(recommendation)
        
        return LearningRecommendationResponse(
            user_id=request.user_id,
            recommendations=recommendations,
            study_plan=f"建議針對{', '.join(request.weakness_points)}進行專項練習",
            estimated_time=request.question_count * 3,
            priority_topics=request.weakness_points,
            confidence_score=0.6
        ) 