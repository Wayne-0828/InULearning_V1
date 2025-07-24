"""
題庫服務客戶端

負責與題庫服務進行通信，獲取題目資訊
"""

import logging
import httpx
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class QuestionBankClient:
    """題庫服務客戶端"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"  # 題庫服務地址
        self.timeout = 30.0
    
    async def get_questions_by_criteria(
        self,
        grade: str,
        subject: str,
        publisher: Optional[str] = None,
        chapter: Optional[str] = None,
        difficulty: Optional[str] = None,
        knowledge_points: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """根據條件獲取題目"""
        
        try:
            # 構建查詢參數
            params = {
                "grade": grade,
                "subject": subject,
                "limit": limit
            }
            
            if publisher:
                params["publisher"] = publisher
            if chapter:
                params["chapter"] = chapter
            if difficulty:
                params["difficulty"] = difficulty
            if knowledge_points:
                params["knowledge_points"] = ",".join(knowledge_points)
            
            # 發送請求
            url = urljoin(self.base_url, "/api/v1/questions/search")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                return data.get("questions", [])
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when getting questions: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting questions: {e}")
            raise
    
    async def get_questions_by_ids(self, question_ids: List[str]) -> List[Dict[str, Any]]:
        """根據題目ID獲取題目"""
        
        try:
            # 構建請求體
            payload = {"question_ids": question_ids}
            
            # 發送請求
            url = urljoin(self.base_url, "/api/v1/questions/batch")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                return data.get("questions", [])
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when getting questions by IDs: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting questions by IDs: {e}")
            raise
    
    async def get_random_questions(
        self,
        grade: str,
        subject: str,
        count: int = 10,
        exclude_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """獲取隨機題目"""
        
        try:
            # 構建查詢參數
            params = {
                "grade": grade,
                "subject": subject,
                "count": count
            }
            
            if exclude_ids:
                params["exclude_ids"] = ",".join(exclude_ids)
            
            # 發送請求
            url = urljoin(self.base_url, "/api/v1/questions/random")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                return data.get("questions", [])
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when getting random questions: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting random questions: {e}")
            raise
    
    async def get_question_statistics(
        self,
        grade: str,
        subject: str,
        publisher: Optional[str] = None
    ) -> Dict[str, Any]:
        """獲取題目統計資訊"""
        
        try:
            # 構建查詢參數
            params = {
                "grade": grade,
                "subject": subject
            }
            
            if publisher:
                params["publisher"] = publisher
            
            # 發送請求
            url = urljoin(self.base_url, "/api/v1/questions/statistics")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when getting question statistics: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting question statistics: {e}")
            raise
    
    async def health_check(self) -> bool:
        """健康檢查"""
        
        try:
            url = urljoin(self.base_url, "/health")
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False 