"""
AI 分析服務客戶端

負責與 AI 分析服務進行通信，進行弱點分析和學習建議
"""

import logging
import httpx
from typing import Dict, Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class AIAnalysisClient:
    """AI 分析服務客戶端"""
    
    def __init__(self):
        self.base_url = "http://localhost:8003"  # AI 分析服務地址
        self.timeout = 60.0  # AI 分析可能需要更長時間
    
    async def analyze_weaknesses(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """進行弱點分析"""
        
        try:
            # 發送請求
            url = urljoin(self.base_url, "/api/v1/analysis/weaknesses")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=analysis_data)
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when analyzing weaknesses: {e}")
            # 返回基礎分析結果
            return self._generate_basic_analysis(analysis_data)
        except Exception as e:
            logger.error(f"Error analyzing weaknesses: {e}")
            # 返回基礎分析結果
            return self._generate_basic_analysis(analysis_data)
    
    async def generate_learning_recommendations(
        self, 
        user_id: str, 
        subject: str,
        recent_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成學習建議"""
        
        try:
            # 構建請求數據
            payload = {
                "user_id": user_id,
                "subject": subject,
                "recent_performance": recent_performance
            }
            
            # 發送請求
            url = urljoin(self.base_url, "/api/v1/analysis/recommendations")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when generating recommendations: {e}")
            return self._generate_basic_recommendations(subject)
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self._generate_basic_recommendations(subject)
    
    async def analyze_learning_trends(
        self, 
        user_id: str, 
        subject: str,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """分析學習趨勢"""
        
        try:
            # 構建查詢參數
            params = {
                "user_id": user_id,
                "subject": subject,
                "time_range": time_range
            }
            
            # 發送請求
            url = urljoin(self.base_url, "/api/v1/analysis/trends")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when analyzing trends: {e}")
            return self._generate_basic_trends()
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return self._generate_basic_trends()
    
    async def predict_performance(
        self, 
        user_id: str, 
        subject: str,
        target_exam: str
    ) -> Dict[str, Any]:
        """預測考試表現"""
        
        try:
            # 構建請求數據
            payload = {
                "user_id": user_id,
                "subject": subject,
                "target_exam": target_exam
            }
            
            # 發送請求
            url = urljoin(self.base_url, "/api/v1/analysis/predict")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when predicting performance: {e}")
            return self._generate_basic_prediction()
        except Exception as e:
            logger.error(f"Error predicting performance: {e}")
            return self._generate_basic_prediction()
    
    async def health_check(self) -> bool:
        """健康檢查"""
        
        try:
            url = urljoin(self.base_url, "/health")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def _generate_basic_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成基礎分析結果"""
        
        records = analysis_data.get("records", [])
        if not records:
            return {
                "weak_concepts": [],
                "knowledge_points_to_strengthen": [],
                "recommendations": ["建議多練習基礎題目"]
            }
        
        # 計算錯誤率
        total_questions = len(records)
        correct_questions = sum(1 for r in records if r.get("is_correct", False))
        error_rate = (total_questions - correct_questions) / total_questions
        
        # 基礎分析
        weak_concepts = []
        knowledge_points = []
        recommendations = []
        
        if error_rate > 0.5:
            weak_concepts = ["基礎概念理解"]
            knowledge_points = ["基礎知識點"]
            recommendations = [
                "建議從基礎概念開始複習",
                "多做基礎練習題",
                "尋求老師或同學的幫助"
            ]
        elif error_rate > 0.3:
            weak_concepts = ["部分概念理解"]
            knowledge_points = ["重點知識點"]
            recommendations = [
                "針對錯誤題目進行重點複習",
                "加強相關概念的練習"
            ]
        else:
            recommendations = ["表現良好，建議繼續保持"]
        
        return {
            "weak_concepts": weak_concepts,
            "knowledge_points_to_strengthen": knowledge_points,
            "recommendations": recommendations
        }
    
    def _generate_basic_recommendations(self, subject: str) -> Dict[str, Any]:
        """生成基礎學習建議"""
        
        return {
            "recommendations": [
                f"建議多練習{subject}相關題目",
                "定期複習已學內容",
                "建立錯題本記錄錯誤題目"
            ],
            "priority_topics": [],
            "study_plan": "建議每天練習 30 分鐘"
        }
    
    def _generate_basic_trends(self) -> Dict[str, Any]:
        """生成基礎趨勢分析"""
        
        return {
            "trend": "stable",
            "improvement_rate": 0.0,
            "consistency_score": 0.7,
            "recommendations": ["建議保持現有學習節奏"]
        }
    
    def _generate_basic_prediction(self) -> Dict[str, Any]:
        """生成基礎預測結果"""
        
        return {
            "predicted_score": 75.0,
            "confidence": 0.6,
            "risk_factors": ["基礎概念需要加強"],
            "recommendations": ["建議加強基礎練習"]
        } 