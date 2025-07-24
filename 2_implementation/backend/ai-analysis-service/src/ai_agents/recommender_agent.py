"""
Recommender Agent for Similar Question Recommendations

This agent is responsible for finding similar questions and generating recommendations.
"""

from typing import List, Dict, Any, Optional
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from ..models.schemas import RecommendedQuestion, DifficultyLevel


class RecommenderAgent:
    """推薦系統 Agent"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """創建推薦系統 Agent"""
        return Agent(
            role="Question Recommender",
            goal="Find and recommend similar questions based on learning patterns and knowledge gaps",
            backstory="""You are an expert in educational content recommendation with deep understanding 
            of question similarity and learning progression. You excel at identifying questions that 
            match students' current learning needs and help them progress effectively.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[]
        )
    
    def find_similar_questions(
        self, 
        knowledge_points: List[str], 
        difficulty: DifficultyLevel,
        count: int = 5,
        exclude_questions: Optional[List[str]] = None
    ) -> List[RecommendedQuestion]:
        """尋找相似題目"""
        
        # 準備推薦參數
        recommendation_params = {
            "knowledge_points": knowledge_points,
            "difficulty": difficulty.value,
            "count": count,
            "exclude_questions": exclude_questions or []
        }
        
        # 執行推薦任務
        task = self._create_similarity_task(recommendation_params)
        result = self.agent.execute_task(task)
        
        # 解析結果並返回推薦題目
        return self._parse_similarity_result(result, recommendation_params)
    
    def _create_similarity_task(self, params: Dict[str, Any]) -> str:
        """創建相似度分析任務"""
        return f"""
        Find similar questions based on the following criteria:
        
        Knowledge Points: {', '.join(params['knowledge_points'])}
        Target Difficulty: {params['difficulty']}
        Number of Questions: {params['count']}
        Exclude Questions: {', '.join(params['exclude_questions'])}
        
        Please provide:
        1. Similar questions with relevance scores
        2. Reasoning for each recommendation
        3. Learning progression suggestions
        
        Format your response as a structured JSON with the following structure:
        {{
            "similar_questions": [
                {{
                    "question_id": "string",
                    "title": "string",
                    "content": "string",
                    "difficulty": "easy|medium|hard",
                    "knowledge_points": ["point1", "point2"],
                    "similarity_score": float_0_to_1,
                    "reasoning": "string"
                }}
            ],
            "learning_progression": ["step1", "step2", "step3"]
        }}
        """
    
    def _parse_similarity_result(self, result: str, params: Dict[str, Any]) -> List[RecommendedQuestion]:
        """解析相似度分析結果"""
        try:
            import json
            import re
            
            # 嘗試提取 JSON 部分
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                # 如果無法解析，使用默認值
                parsed_data = self._create_default_similarity_result(params)
            
            # 構建推薦題目列表
            recommendations = []
            for q_data in parsed_data.get("similar_questions", []):
                recommendation = RecommendedQuestion(
                    question_id=q_data.get("question_id", f"sim_{len(recommendations)}"),
                    title=q_data.get("title", f"相似題目 {len(recommendations) + 1}"),
                    content=q_data.get("content", f"關於{params['knowledge_points'][0]}的練習題"),
                    difficulty=DifficultyLevel(q_data.get("difficulty", params["difficulty"])),
                    knowledge_points=q_data.get("knowledge_points", params["knowledge_points"][:2]),
                    similarity_score=q_data.get("similarity_score", 0.8),
                    explanation=q_data.get("reasoning", "這道題目與您的學習需求相關")
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            # 錯誤處理：返回默認推薦
            return self._create_default_recommendations(params)
    
    def _create_default_similarity_result(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """創建默認相似度分析結果"""
        similar_questions = []
        for i in range(params["count"]):
            similar_questions.append({
                "question_id": f"sim_{i}",
                "title": f"相似題目 {i + 1}",
                "content": f"關於{params['knowledge_points'][0]}的練習題",
                "difficulty": params["difficulty"],
                "knowledge_points": params["knowledge_points"][:2],
                "similarity_score": 0.85 - (i * 0.05),
                "reasoning": f"這道題目涉及{params['knowledge_points'][0]}知識點，適合當前學習階段"
            })
        
        return {
            "similar_questions": similar_questions,
            "learning_progression": [
                "先完成基礎概念練習",
                "逐步提升題目難度",
                "綜合應用所學知識"
            ]
        }
    
    def _create_default_recommendations(self, params: Dict[str, Any]) -> List[RecommendedQuestion]:
        """創建默認推薦題目"""
        recommendations = []
        
        for i in range(params["count"]):
            recommendation = RecommendedQuestion(
                question_id=f"default_{i}",
                title=f"推薦題目 {i + 1}",
                content=f"關於{params['knowledge_points'][0]}的練習題",
                difficulty=DifficultyLevel(params["difficulty"]),
                knowledge_points=params["knowledge_points"][:2],
                similarity_score=0.8 - (i * 0.05),
                explanation="這道題目與您的學習需求相關，建議認真練習"
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def calculate_similarity_score(self, question1: Dict[str, Any], question2: Dict[str, Any]) -> float:
        """計算兩個題目的相似度分數"""
        # 這裡應該實現實際的相似度計算算法
        # 可以基於向量相似度、知識點重疊度等
        
        # 簡單的相似度計算示例
        score = 0.0
        
        # 知識點重疊度
        knowledge_points1 = set(question1.get("knowledge_points", []))
        knowledge_points2 = set(question2.get("knowledge_points", []))
        
        if knowledge_points1 and knowledge_points2:
            overlap = len(knowledge_points1.intersection(knowledge_points2))
            total = len(knowledge_points1.union(knowledge_points2))
            score += (overlap / total) * 0.6
        
        # 難度相似度
        if question1.get("difficulty") == question2.get("difficulty"):
            score += 0.3
        
        # 科目相似度
        if question1.get("subject") == question2.get("subject"):
            score += 0.1
        
        return min(score, 1.0) 