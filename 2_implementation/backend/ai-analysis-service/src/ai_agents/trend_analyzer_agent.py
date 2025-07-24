"""
Trend Analyzer Agent for Learning Trend Analysis

This agent is responsible for analyzing learning trends and providing long-term insights.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from ..models.schemas import (
    TrendAnalysisRequest, 
    TrendAnalysisResponse, 
    TrendData
)


class TrendAnalyzerAgent:
    """趨勢分析 Agent"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """創建趨勢分析 Agent"""
        return Agent(
            role="Learning Trend Analyzer",
            goal="Analyze long-term learning trends and provide insights for continuous improvement",
            backstory="""You are an expert in educational data analysis and learning psychology. 
            You specialize in identifying learning patterns, tracking progress over time, and 
            providing actionable insights for long-term learning improvement.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[]
        )
    
    def analyze_trends(self, request: TrendAnalysisRequest) -> TrendAnalysisResponse:
        """分析學習趨勢"""
        
        # 準備趨勢分析數據
        trend_data = self._prepare_trend_data(request)
        
        # 執行趨勢分析任務
        task = self._create_trend_analysis_task(trend_data)
        result = self.agent.execute_task(task)
        
        # 解析結果並構建回應
        return self._parse_trend_result(result, request)
    
    def _prepare_trend_data(self, request: TrendAnalysisRequest) -> Dict[str, Any]:
        """準備趨勢分析數據"""
        # 這裡應該從資料庫獲取實際的學習歷史數據
        # 為了演示，我們創建模擬數據
        
        # 生成模擬趨勢數據
        trend_data = []
        current_date = request.start_date
        base_score = 70.0
        base_accuracy = 0.7
        
        while current_date <= request.end_date:
            # 模擬學習進步趨勢
            days_passed = (current_date - request.start_date).days
            progress_factor = min(days_passed / 30, 1.0)  # 30天內逐步進步
            
            score = base_score + (progress_factor * 20) + (days_passed % 7 - 3)  # 加入週期性波動
            accuracy = base_accuracy + (progress_factor * 0.2) + ((days_passed % 5 - 2) * 0.02)
            
            trend_data.append({
                "date": current_date.isoformat(),
                "score": max(0, min(100, score)),
                "question_count": 5 + (days_passed % 3),  # 5-7題
                "accuracy_rate": max(0.3, min(1.0, accuracy)),
                "average_time": 120 + (days_passed % 4 * 10)  # 120-150秒
            })
            
            current_date += timedelta(days=1)
        
        return {
            "user_id": request.user_id,
            "subject": request.subject.value if request.subject else "all",
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat(),
            "analysis_type": request.analysis_type,
            "trend_data": trend_data
        }
    
    def _create_trend_analysis_task(self, trend_data: Dict[str, Any]) -> str:
        """創建趨勢分析任務"""
        return f"""
        Analyze the following learning trend data and provide comprehensive insights:
        
        Student Information:
        - User ID: {trend_data['user_id']}
        - Subject: {trend_data['subject']}
        - Analysis Period: {trend_data['start_date']} to {trend_data['end_date']}
        - Analysis Type: {trend_data['analysis_type']}
        
        Trend Data: {trend_data['trend_data']}
        
        Please provide:
        1. Overall progress assessment
        2. Improvement areas identification
        3. Consistent weaknesses analysis
        4. Learning patterns insights
        5. Long-term recommendations
        
        Format your response as a structured JSON with the following structure:
        {{
            "overall_progress": "string",
            "improvement_areas": ["area1", "area2", "area3"],
            "consistent_weaknesses": ["weakness1", "weakness2"],
            "learning_patterns": {{
                "study_frequency": "string",
                "performance_trend": "string",
                "time_management": "string"
            }},
            "recommendations": ["rec1", "rec2", "rec3"]
        }}
        """
    
    def _parse_trend_result(self, result: str, request: TrendAnalysisRequest) -> TrendAnalysisResponse:
        """解析趨勢分析結果"""
        try:
            import json
            import re
            
            # 嘗試提取 JSON 部分
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                # 如果無法解析，使用默認值
                parsed_data = self._create_default_trend_analysis(request)
            
            # 構建趨勢數據
            trend_data = self._build_trend_data(request)
            
            return TrendAnalysisResponse(
                user_id=request.user_id,
                subject=request.subject,
                trend_data=trend_data,
                overall_progress=parsed_data.get("overall_progress", "學習表現穩定，有進步空間"),
                improvement_areas=parsed_data.get("improvement_areas", ["基礎概念理解", "解題速度"]),
                consistent_weaknesses=parsed_data.get("consistent_weaknesses", ["複雜題型處理"]),
                learning_patterns=parsed_data.get("learning_patterns", {
                    "study_frequency": "每週3-4次",
                    "performance_trend": "穩步提升",
                    "time_management": "需要改善"
                }),
                recommendations=parsed_data.get("recommendations", [
                    "增加練習頻率",
                    "專注弱點強化",
                    "改善時間管理"
                ]),
                analysis_period=f"{request.start_date.strftime('%Y-%m-%d')} 至 {request.end_date.strftime('%Y-%m-%d')}"
            )
            
        except Exception as e:
            # 錯誤處理：返回默認分析
            return self._create_default_trend_response(request)
    
    def _build_trend_data(self, request: TrendAnalysisRequest) -> List[TrendData]:
        """構建趨勢數據"""
        trend_data = []
        current_date = request.start_date
        base_score = 70.0
        base_accuracy = 0.7
        
        while current_date <= request.end_date:
            # 模擬學習進步趨勢
            days_passed = (current_date - request.start_date).days
            progress_factor = min(days_passed / 30, 1.0)
            
            score = base_score + (progress_factor * 20) + (days_passed % 7 - 3)
            accuracy = base_accuracy + (progress_factor * 0.2) + ((days_passed % 5 - 2) * 0.02)
            
            trend_data.append(TrendData(
                date=current_date,
                score=max(0, min(100, score)),
                question_count=5 + (days_passed % 3),
                accuracy_rate=max(0.3, min(1.0, accuracy)),
                average_time=120 + (days_passed % 4 * 10)
            ))
            
            current_date += timedelta(days=1)
        
        return trend_data
    
    def _create_default_trend_analysis(self, request: TrendAnalysisRequest) -> Dict[str, Any]:
        """創建默認趨勢分析結果"""
        return {
            "overall_progress": "學習表現穩定，有進步空間",
            "improvement_areas": [
                "基礎概念理解",
                "解題速度",
                "複雜題型處理"
            ],
            "consistent_weaknesses": [
                "時間管理",
                "高難度題目"
            ],
            "learning_patterns": {
                "study_frequency": "每週3-4次",
                "performance_trend": "穩步提升",
                "time_management": "需要改善",
                "accuracy_consistency": "中等"
            },
            "recommendations": [
                "增加練習頻率",
                "專注弱點強化",
                "改善時間管理",
                "尋求教師指導"
            ]
        }
    
    def _create_default_trend_response(self, request: TrendAnalysisRequest) -> TrendAnalysisResponse:
        """創建默認趨勢分析回應"""
        trend_data = self._build_trend_data(request)
        
        return TrendAnalysisResponse(
            user_id=request.user_id,
            subject=request.subject,
            trend_data=trend_data,
            overall_progress="學習表現穩定，有進步空間",
            improvement_areas=["基礎概念理解", "解題速度"],
            consistent_weaknesses=["複雜題型處理"],
            learning_patterns={
                "study_frequency": "每週3-4次",
                "performance_trend": "穩步提升",
                "time_management": "需要改善"
            },
            recommendations=[
                "增加練習頻率",
                "專注弱點強化",
                "改善時間管理"
            ],
            analysis_period=f"{request.start_date.strftime('%Y-%m-%d')} 至 {request.end_date.strftime('%Y-%m-%d')}"
        ) 