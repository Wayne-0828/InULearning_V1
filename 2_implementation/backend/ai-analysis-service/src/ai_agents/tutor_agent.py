"""
Tutor Agent for Learning Recommendations

This agent is responsible for generating personalized learning recommendations and study plans.
"""

from typing import List, Dict, Any
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from ..models.schemas import (
    LearningRecommendationRequest, 
    LearningRecommendationResponse, 
    RecommendedQuestion
)


class TutorAgent:
    """學習導師 Agent"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """創建導師 Agent"""
        return Agent(
            role="Learning Tutor",
            goal="Generate personalized learning recommendations and study plans based on student weaknesses",
            backstory="""You are an experienced educational tutor specializing in middle school subjects. 
            You have deep knowledge of curriculum design and learning psychology. You excel at creating 
            personalized study plans that help students overcome their weaknesses and improve their performance.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[]
        )
    
    def generate_recommendations(self, request: LearningRecommendationRequest) -> LearningRecommendationResponse:
        """生成學習建議"""
        
        # 準備推薦數據
        recommendation_data = self._prepare_recommendation_data(request)
        
        # 執行推薦任務
        task = self._create_recommendation_task(recommendation_data)
        result = self.agent.execute_task(task)
        
        # 解析結果並構建回應
        return self._parse_recommendation_result(result, request)
    
    def _prepare_recommendation_data(self, request: LearningRecommendationRequest) -> Dict[str, Any]:
        """準備推薦數據"""
        return {
            "user_id": request.user_id,
            "subject": request.subject.value,
            "grade": request.grade.value,
            "version": request.version.value,
            "weakness_points": request.weakness_points,
            "target_difficulty": request.target_difficulty.value,
            "question_count": request.question_count,
            "include_explanations": request.include_explanations
        }
    
    def _create_recommendation_task(self, recommendation_data: Dict[str, Any]) -> str:
        """創建推薦任務"""
        return f"""
        Generate personalized learning recommendations for a student based on the following information:
        
        Student Information:
        - User ID: {recommendation_data['user_id']}
        - Subject: {recommendation_data['subject']}
        - Grade: {recommendation_data['grade']}
        - Version: {recommendation_data['version']}
        
        Learning Needs:
        - Weakness Points: {', '.join(recommendation_data['weakness_points'])}
        - Target Difficulty: {recommendation_data['target_difficulty']}
        - Number of Questions: {recommendation_data['question_count']}
        - Include Explanations: {recommendation_data['include_explanations']}
        
        Please provide:
        1. A comprehensive study plan
        2. Estimated study time
        3. Priority topics to focus on
        4. Confidence score for the recommendations (0-1)
        5. Specific learning strategies
        
        Format your response as a structured JSON with the following structure:
        {{
            "study_plan": "detailed study plan text",
            "estimated_time": integer_minutes,
            "priority_topics": ["topic1", "topic2", "topic3"],
            "confidence_score": float_0_to_1,
            "learning_strategies": ["strategy1", "strategy2", "strategy3"]
        }}
        """
    
    def _parse_recommendation_result(self, result: str, request: LearningRecommendationRequest) -> LearningRecommendationResponse:
        """解析推薦結果"""
        try:
            import json
            import re
            
            # 嘗試提取 JSON 部分
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                # 如果無法解析，使用默認值
                parsed_data = self._create_default_recommendation(request)
            
            # 生成推薦題目（這裡應該從題庫服務獲取）
            recommendations = self._generate_recommended_questions(request, parsed_data)
            
            return LearningRecommendationResponse(
                user_id=request.user_id,
                recommendations=recommendations,
                study_plan=parsed_data.get("study_plan", "建議按照難度遞增的順序進行練習"),
                estimated_time=parsed_data.get("estimated_time", 30),
                priority_topics=parsed_data.get("priority_topics", request.weakness_points),
                confidence_score=parsed_data.get("confidence_score", 0.8)
            )
            
        except Exception as e:
            # 錯誤處理：返回默認推薦
            return self._create_default_recommendation_response(request)
    
    def _generate_recommended_questions(self, request: LearningRecommendationRequest, parsed_data: Dict[str, Any]) -> List[RecommendedQuestion]:
        """生成推薦題目"""
        # 這裡應該從題庫服務獲取實際題目
        # 為了演示，我們創建示例題目
        recommendations = []
        
        for i in range(min(request.question_count, 5)):  # 限制最多5題作為示例
            recommendation = RecommendedQuestion(
                question_id=f"rec_{request.user_id}_{i}",
                title=f"{request.subject.value}練習題 {i+1}",
                content=f"這是一道關於{request.weakness_points[0] if request.weakness_points else '基礎概念'}的練習題",
                difficulty=request.target_difficulty,
                knowledge_points=request.weakness_points[:2],  # 取前兩個弱點
                similarity_score=0.85 - (i * 0.05),  # 遞減的相似度分數
                explanation="這道題目幫助鞏固相關知識點，建議仔細思考後再查看詳解" if request.include_explanations else None
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _create_default_recommendation(self, request: LearningRecommendationRequest) -> Dict[str, Any]:
        """創建默認推薦結果"""
        return {
            "study_plan": f"建議針對{', '.join(request.weakness_points)}進行專項練習，從基礎題型開始，逐步提升難度",
            "estimated_time": request.question_count * 3,  # 每題3分鐘
            "priority_topics": request.weakness_points,
            "confidence_score": 0.75,
            "learning_strategies": [
                "先複習相關概念",
                "從簡單題型開始練習",
                "及時總結錯誤原因",
                "定期複習鞏固"
            ]
        }
    
    def _create_default_recommendation_response(self, request: LearningRecommendationRequest) -> LearningRecommendationResponse:
        """創建默認推薦回應"""
        recommendations = self._generate_recommended_questions(request, {})
        
        return LearningRecommendationResponse(
            user_id=request.user_id,
            recommendations=recommendations,
            study_plan=f"建議針對{', '.join(request.weakness_points)}進行專項練習",
            estimated_time=request.question_count * 3,
            priority_topics=request.weakness_points,
            confidence_score=0.75
        ) 