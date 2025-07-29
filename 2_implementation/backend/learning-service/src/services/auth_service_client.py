"""
認證服務客戶端
與認證服務進行通信，獲取用戶關係數據
"""
import httpx
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AuthServiceClient:
    def __init__(self):
        self.base_url = "http://auth-service:8000/api/v1"  # 使用Docker內部網路
        self.timeout = 30.0
    
    async def get_parent_children_ids(self, parent_id: int, token: str) -> List[int]:
        """
        獲取家長的子女ID列表
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/relationships/parent-child",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return [relation["child_id"] for relation in data]
                elif response.status_code == 404:
                    # 沒有找到關係，返回空列表
                    return []
                else:
                    logger.error(f"獲取家長子女關係失敗: {response.status_code} - {response.text}")
                    return []
                    
        except httpx.TimeoutException:
            logger.error("獲取家長子女關係超時")
            return []
        except Exception as e:
            logger.error(f"獲取家長子女關係異常: {str(e)}")
            return []
    
    async def get_teacher_student_ids(self, teacher_id: int, token: str) -> List[int]:
        """
        獲取教師的學生ID列表
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # 首先獲取教師的班級
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 獲取教師班級關係
                teacher_classes_response = await client.get(
                    f"{self.base_url}/relationships/teacher-class",
                    headers=headers
                )
                
                if teacher_classes_response.status_code != 200:
                    logger.error(f"獲取教師班級關係失敗: {teacher_classes_response.status_code}")
                    return []
                
                teacher_classes = teacher_classes_response.json()
                class_ids = [relation["class_id"] for relation in teacher_classes]
                
                if not class_ids:
                    return []
                
                # 獲取這些班級的所有學生
                student_ids = []
                for class_id in class_ids:
                    students_response = await client.get(
                        f"{self.base_url}/relationships/student-class?class_id={class_id}",
                        headers=headers
                    )
                    
                    if students_response.status_code == 200:
                        students_data = students_response.json()
                        student_ids.extend([relation["student_id"] for relation in students_data])
                
                return list(set(student_ids))  # 去重
                
        except httpx.TimeoutException:
            logger.error("獲取教師學生關係超時")
            return []
        except Exception as e:
            logger.error(f"獲取教師學生關係異常: {str(e)}")
            return []
    
    async def get_user_info(self, user_id: int, token: str) -> Optional[Dict]:
        """
        獲取用戶基本信息
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/users/{user_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"獲取用戶信息失敗: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("獲取用戶信息超時")
            return None
        except Exception as e:
            logger.error(f"獲取用戶信息異常: {str(e)}")
            return None
    
    async def verify_parent_child_relationship(self, parent_id: int, child_id: int, token: str) -> bool:
        """
        驗證家長與子女的關係
        """
        try:
            children_ids = await self.get_parent_children_ids(parent_id, token)
            return child_id in children_ids
        except Exception as e:
            logger.error(f"驗證親子關係異常: {str(e)}")
            return False
    
    async def verify_teacher_student_relationship(self, teacher_id: int, student_id: int, token: str) -> bool:
        """
        驗證教師與學生的關係
        """
        try:
            student_ids = await self.get_teacher_student_ids(teacher_id, token)
            return student_id in student_ids
        except Exception as e:
            logger.error(f"驗證師生關係異常: {str(e)}")
            return False
    
    async def get_class_info(self, class_id: int, token: str) -> Optional[Dict]:
        """
        獲取班級信息
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/relationships/classes/{class_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"獲取班級信息失敗: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("獲取班級信息超時")
            return None
        except Exception as e:
            logger.error(f"獲取班級信息異常: {str(e)}")
            return None

# 創建全局實例
auth_service_client = AuthServiceClient() 