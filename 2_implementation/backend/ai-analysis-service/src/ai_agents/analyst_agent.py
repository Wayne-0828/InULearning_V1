"""
Analyst Agent for Learning Weakness Analysis

This agent is responsible for analyzing student learning patterns and identifying weaknesses.
"""

from typing import List, Dict, Any
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from ..models.schemas import WeaknessAnalysisRequest, WeaknessAnalysisResponse, WeaknessPoint


class AnalystAgent:
    """學習分析師 Agent"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """創建分析師 Agent"""
        return Agent(
            role="Learning Analyst",
            goal="Analyze student learning patterns and identify specific weaknesses in knowledge points",
            backstory="""You are an expert educational analyst with deep understanding of 
            middle school curriculum and learning psychology. You specialize in identifying 
            learning weaknesses and providing actionable insights for improvement.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[]  # Will add specific tools later
        )
    
    def analyze_weaknesses(self, request: WeaknessAnalysisRequest) -> WeaknessAnalysisResponse:
        """分析學習弱點"""
        
        # 準備分析數據
        analysis_data = self._prepare_analysis_data(request)
        
        # 執行分析任務
        task = self._create_analysis_task(analysis_data)
        result = self.agent.execute_task(task)
        
        # 解析結果並構建回應
        return self._parse_analysis_result(result, request)
    
    def _prepare_analysis_data(self, request: WeaknessAnalysisRequest) -> Dict[str, Any]:
        """準備分析數據"""
        return {
            "session_id": request.session_id,
            "user_id": request.user_id,
            "subject": request.subject.value,
            "grade": request.grade.value,
            "version": request.version.value,
            "total_questions": request.total_questions,
            "correct_count": request.correct_count,
            "accuracy_rate": request.correct_count / request.total_questions,
            "total_time": request.total_time,
            "average_time": request.total_time / request.total_questions,
            "answer_records": [
                {
                    "question_id": record.question_id,
                    "is_correct": record.is_correct,
                    "time_spent": record.time_spent,
                    "confidence_score": record.confidence_score
                }
                for record in request.answer_records
            ]
        }
    
    def _create_analysis_task(self, analysis_data: Dict[str, Any]) -> str:
        """創建分析任務"""
        return f"""
        Analyze the following learning session data and provide a comprehensive weakness analysis:
        
        Session Information:
        - Session ID: {analysis_data['session_id']}
        - Subject: {analysis_data['subject']}
        - Grade: {analysis_data['grade']}
        - Version: {analysis_data['version']}
        
        Performance Metrics:
        - Total Questions: {analysis_data['total_questions']}
        - Correct Answers: {analysis_data['correct_count']}
        - Accuracy Rate: {analysis_data['accuracy_rate']:.2%}
        - Total Time: {analysis_data['total_time']} seconds
        - Average Time per Question: {analysis_data['average_time']:.1f} seconds
        
        Answer Records: {analysis_data['answer_records']}
        
        Please provide:
        1. Overall score (0-100)
        2. Detailed weakness points with:
           - Knowledge point identification
           - Weakness level (low/medium/high)
           - Error pattern description
           - Improvement suggestions
        3. Learning insights
        4. Next steps recommendations
        
        Format your response as a structured JSON with the following structure:
        {{
            "overall_score": float,
            "weakness_points": [
                {{
                    "knowledge_point": "string",
                    "weakness_level": "low|medium|high",
                    "error_pattern": "string",
                    "improvement_suggestion": "string",
                    "related_questions": ["question_id1", "question_id2"]
                }}
            ],
            "learning_insights": "string",
            "next_steps": ["step1", "step2", "step3"]
        }}
        """
    
    def _parse_analysis_result(self, result: str, request: WeaknessAnalysisRequest) -> WeaknessAnalysisResponse:
        """解析分析結果"""
        try:
            # 這裡應該解析 AI 返回的 JSON 結果
            # 為了演示，我們創建一個示例回應
            import json
            import re
            
            # 嘗試提取 JSON 部分
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                # 如果無法解析，使用默認值
                parsed_data = self._create_default_analysis(request)
            
            # 構建弱點分析回應
            weakness_points = []
            for wp_data in parsed_data.get("weakness_points", []):
                weakness_point = WeaknessPoint(
                    knowledge_point=wp_data.get("knowledge_point", "未知知識點"),
                    weakness_level=wp_data.get("weakness_level", "medium"),
                    error_pattern=wp_data.get("error_pattern", "需要進一步分析"),
                    improvement_suggestion=wp_data.get("improvement_suggestion", "建議加強練習"),
                    related_questions=wp_data.get("related_questions", [])
                )
                weakness_points.append(weakness_point)
            
            return WeaknessAnalysisResponse(
                session_id=request.session_id,
                user_id=request.user_id,
                overall_score=parsed_data.get("overall_score", 70.0),
                accuracy_rate=request.correct_count / request.total_questions,
                average_time=request.total_time / request.total_questions,
                weakness_points=weakness_points,
                learning_insights=parsed_data.get("learning_insights", "需要更多數據進行深入分析"),
                next_steps=parsed_data.get("next_steps", ["繼續練習", "複習基礎概念"])
            )
            
        except Exception as e:
            # 錯誤處理：返回默認分析
            return self._create_default_analysis_response(request)
    
    def _create_default_analysis(self, request: WeaknessAnalysisRequest) -> Dict[str, Any]:
        """創建默認分析結果"""
        accuracy_rate = request.correct_count / request.total_questions
        overall_score = accuracy_rate * 100
        
        return {
            "overall_score": overall_score,
            "weakness_points": [
                {
                    "knowledge_point": f"{request.subject.value}基礎概念",
                    "weakness_level": "medium" if accuracy_rate < 0.8 else "low",
                    "error_pattern": "概念理解需要加強",
                    "improvement_suggestion": "建議多練習基礎題型，鞏固核心概念",
                    "related_questions": []
                }
            ],
            "learning_insights": f"學生在{request.subject.value}科目表現{'良好' if accuracy_rate >= 0.8 else '需要改進'}",
            "next_steps": ["繼續練習", "複習基礎概念", "尋求教師指導"]
        }
    
    def _create_default_analysis_response(self, request: WeaknessAnalysisRequest) -> WeaknessAnalysisResponse:
        """創建默認分析回應"""
        accuracy_rate = request.correct_count / request.total_questions
        
        return WeaknessAnalysisResponse(
            session_id=request.session_id,
            user_id=request.user_id,
            overall_score=accuracy_rate * 100,
            accuracy_rate=accuracy_rate,
            average_time=request.total_time / request.total_questions,
            weakness_points=[
                WeaknessPoint(
                    knowledge_point=f"{request.subject.value}基礎概念",
                    weakness_level="medium" if accuracy_rate < 0.8 else "low",
                    error_pattern="概念理解需要加強",
                    improvement_suggestion="建議多練習基礎題型，鞏固核心概念",
                    related_questions=[]
                )
            ],
            learning_insights=f"學生在{request.subject.value}科目表現{'良好' if accuracy_rate >= 0.8 else '需要改進'}",
            next_steps=["繼續練習", "複習基礎概念", "尋求教師指導"]
        ) 