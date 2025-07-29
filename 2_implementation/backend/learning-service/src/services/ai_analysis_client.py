"""
AI 分析服務客戶端

負責與 AI 分析服務進行通信，進行弱點分析和學習建議
跳過 Milvus RAG 部分，提供基礎分析功能
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import json
from datetime import datetime, timedelta

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
        """預測學習表現"""
        
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
            logger.error(f"AI Analysis Service health check failed: {e}")
            return False
    
    def _generate_basic_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成基礎弱點分析（跳過 Milvus RAG）"""
        
        # 從分析數據中提取基本信息
        results = analysis_data.get("results", [])
        subject = analysis_data.get("subject", "數學")
        
        # 分析錯誤題目
        incorrect_questions = [r for r in results if not r.get("correct", True)]
        
        # 提取弱點概念
        weak_concepts = []
        knowledge_points_to_strengthen = []
        
        for question in incorrect_questions:
            # 從題目信息中提取知識點
            knowledge_points = question.get("knowledge_points", [])
            if isinstance(knowledge_points, str):
                try:
                    knowledge_points = json.loads(knowledge_points)
                except:
                    knowledge_points = []
            
            weak_concepts.extend(knowledge_points)
            knowledge_points_to_strengthen.extend(knowledge_points)
        
        # 去重
        weak_concepts = list(set(weak_concepts))
        knowledge_points_to_strengthen = list(set(knowledge_points_to_strengthen))
        
        # 生成基礎建議
        recommendations = []
        if weak_concepts:
            recommendations.append({
                "type": "similar_question",
                "question_ids": [],
                "difficulty": "easy",
                "reason": f"建議加強 {', '.join(weak_concepts[:3])} 相關練習"
            })
        
        return {
            "weak_concepts": weak_concepts,
            "knowledge_points_to_strengthen": knowledge_points_to_strengthen,
            "recommendations": recommendations,
            "analysis_version": "v1.0-basic"
        }
    
    def _generate_basic_recommendations(self, subject: str) -> Dict[str, Any]:
        """生成基礎學習建議"""
        
        subject_recommendations = {
            "數學": [
                {
                    "type": "concept_review",
                    "topics": ["基礎運算", "方程式求解"],
                    "difficulty": "easy",
                    "reason": "建議複習基礎概念"
                }
            ],
            "國文": [
                {
                    "type": "concept_review", 
                    "topics": ["文意理解", "字詞運用"],
                    "difficulty": "easy",
                    "reason": "建議加強閱讀理解"
                }
            ],
            "英文": [
                {
                    "type": "concept_review",
                    "topics": ["文法", "單字"],
                    "difficulty": "easy", 
                    "reason": "建議加強基礎文法"
                }
            ]
        }
        
        return {
            "recommendations": subject_recommendations.get(subject, []),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_basic_trends(self) -> Dict[str, Any]:
        """生成基礎趨勢分析"""
        
        # 生成模擬趨勢數據
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        trend_data = []
        current_date = start_date
        while current_date <= end_date:
            trend_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "score": 75.0,
                "session_count": 1
            })
            current_date += timedelta(days=3)
        
        return {
            "score_trend": trend_data,
            "accuracy_trend": trend_data,
            "concept_mastery_progress": {},
            "improvement_areas": [],
            "persistent_weaknesses": [],
            "learning_velocity_trend": 1.0
        }
    
    def _generate_basic_prediction(self) -> Dict[str, Any]:
        """生成基礎表現預測"""
        
        return {
            "predicted_score": 80.0,
            "confidence": 0.7,
            "risk_factors": ["基礎概念需要加強"],
            "recommendations": ["建議多做基礎練習題"]
        } 