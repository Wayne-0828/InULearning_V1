"""
家長儀表板服務 (Parent Dashboard Service)
提供家長查看子女學習狀況、進度追蹤、弱點分析等功能
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import json
import logging
from datetime import datetime, timedelta
import asyncio

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="家長儀表板服務",
    description="提供家長查看子女學習狀況、進度追蹤、弱點分析等功能",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全配置
security = HTTPBearer()

# 服務配置
AUTH_SERVICE_URL = "http://auth-service:8001"
LEARNING_SERVICE_URL = "http://learning-service:8002"
AI_ANALYSIS_SERVICE_URL = "http://ai-analysis-service:8004"
QUESTION_BANK_SERVICE_URL = "http://question-bank-service:8003"

# 資料模型
class ChildInfo(BaseModel):
    id: int
    name: str
    grade: int
    class_name: Optional[str] = None
    student_id: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime
    total_exercises: int = 0
    accuracy_rate: float = 0.0
    study_days: int = 0
    overall_progress: float = 0.0
    streak_days: int = 0
    total_study_hours: float = 0.0

class ChildProgress(BaseModel):
    child_name: str
    overall_progress: float
    accuracy_rate: float
    study_days: int
    streak_days: int
    subjects: List[Dict[str, Any]]
    weaknesses: List[Dict[str, Any]]
    trend_data: List[Dict[str, Any]]

class CommunicationAdvice(BaseModel):
    child_id: int
    advice_type: str
    title: str
    content: str
    suggested_topics: List[str]
    mood_analysis: Dict[str, Any]
    created_at: datetime

class LearningActivity(BaseModel):
    id: int
    title: str
    description: str
    activity_type: str
    created_at: datetime
    metadata: Dict[str, Any]

# 依賴注入
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """驗證用戶身份並返回用戶資訊"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {credentials.credentials}"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                if user_data.get("role") != "parent":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="只有家長角色可以訪問此服務"
                    )
                return user_data
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="無效的認證令牌"
                )
    except httpx.RequestError as e:
        logger.error(f"認證服務連接錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="認證服務暫時不可用"
        )

async def get_user_children(parent_id: int) -> List[Dict[str, Any]]:
    """獲取家長的子女列表"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/v1/users/{parent_id}/children"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"獲取子女列表失敗: {response.status_code}")
                return []
    except httpx.RequestError as e:
        logger.error(f"獲取子女列表錯誤: {e}")
        return []

async def get_child_learning_data(child_id: int) -> Dict[str, Any]:
    """獲取子女的學習資料"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LEARNING_SERVICE_URL}/api/v1/learning/students/{child_id}/summary"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"獲取學習資料失敗: {response.status_code}")
                return {}
    except httpx.RequestError as e:
        logger.error(f"獲取學習資料錯誤: {e}")
        return {}

async def get_child_weakness_analysis(child_id: int) -> List[Dict[str, Any]]:
    """獲取子女的弱點分析"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_ANALYSIS_SERVICE_URL}/api/v1/ai/weakness-analysis",
                json={"student_id": child_id}
            )
            
            if response.status_code == 200:
                return response.json().get("weaknesses", [])
            else:
                logger.error(f"獲取弱點分析失敗: {response.status_code}")
                return []
    except httpx.RequestError as e:
        logger.error(f"獲取弱點分析錯誤: {e}")
        return []

async def get_communication_advice(child_id: int) -> Dict[str, Any]:
    """獲取親子溝通建議"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_ANALYSIS_SERVICE_URL}/api/v1/ai/communication-advice",
                json={"student_id": child_id}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"獲取溝通建議失敗: {response.status_code}")
                return {}
    except httpx.RequestError as e:
        logger.error(f"獲取溝通建議錯誤: {e}")
        return {}

# API 端點
@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "parent-dashboard-service", "timestamp": datetime.now()}

@app.get("/api/v1/parent/children", response_model=List[ChildInfo])
async def get_children(current_user: Dict[str, Any] = Depends(get_current_user)):
    """獲取家長的子女列表"""
    try:
        parent_id = current_user["id"]
        children_data = await get_user_children(parent_id)
        
        # 並行獲取每個子女的學習資料
        tasks = []
        for child in children_data:
            task = get_child_learning_data(child["id"])
            tasks.append(task)
        
        learning_data_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整合資料
        enriched_children = []
        for i, child in enumerate(children_data):
            learning_data = learning_data_list[i] if not isinstance(learning_data_list[i], Exception) else {}
            
            enriched_child = ChildInfo(
                id=child["id"],
                name=child["name"],
                grade=child["grade"],
                class_name=child.get("class_name"),
                student_id=child.get("student_id"),
                avatar=child.get("avatar"),
                created_at=datetime.fromisoformat(child["created_at"]),
                total_exercises=learning_data.get("total_exercises", 0),
                accuracy_rate=learning_data.get("accuracy_rate", 0.0),
                study_days=learning_data.get("study_days", 0),
                overall_progress=learning_data.get("overall_progress", 0.0),
                streak_days=learning_data.get("streak_days", 0),
                total_study_hours=learning_data.get("total_study_hours", 0.0)
            )
            enriched_children.append(enriched_child)
        
        return enriched_children
        
    except Exception as e:
        logger.error(f"獲取子女列表錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取子女列表失敗"
        )

@app.get("/api/v1/parent/children/{child_id}", response_model=ChildInfo)
async def get_child_details(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """獲取特定子女的詳細資訊"""
    try:
        parent_id = current_user["id"]
        children_data = await get_user_children(parent_id)
        
        # 驗證子女是否屬於該家長
        child = next((c for c in children_data if c["id"] == child_id), None)
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="子女不存在或無權限訪問"
            )
        
        # 獲取學習資料
        learning_data = await get_child_learning_data(child_id)
        
        # 獲取最近學習活動
        recent_activities = await get_recent_activities(child_id)
        
        enriched_child = ChildInfo(
            id=child["id"],
            name=child["name"],
            grade=child["grade"],
            class_name=child.get("class_name"),
            student_id=child.get("student_id"),
            avatar=child.get("avatar"),
            created_at=datetime.fromisoformat(child["created_at"]),
            total_exercises=learning_data.get("total_exercises", 0),
            accuracy_rate=learning_data.get("accuracy_rate", 0.0),
            study_days=learning_data.get("study_days", 0),
            overall_progress=learning_data.get("overall_progress", 0.0),
            streak_days=learning_data.get("streak_days", 0),
            total_study_hours=learning_data.get("total_study_hours", 0.0)
        )
        
        # 添加最近活動到響應中
        response_data = enriched_child.dict()
        response_data["recent_activities"] = recent_activities
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取子女詳細資訊錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取子女詳細資訊失敗"
        )

@app.get("/api/v1/parent/children/{child_id}/progress", response_model=ChildProgress)
async def get_child_progress(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """獲取子女的學習進度"""
    try:
        parent_id = current_user["id"]
        children_data = await get_user_children(parent_id)
        
        # 驗證子女是否屬於該家長
        child = next((c for c in children_data if c["id"] == child_id), None)
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="子女不存在或無權限訪問"
            )
        
        # 並行獲取各種資料
        learning_data_task = get_child_learning_data(child_id)
        weaknesses_task = get_child_weakness_analysis(child_id)
        trend_data_task = get_learning_trend(child_id)
        
        learning_data, weaknesses, trend_data = await asyncio.gather(
            learning_data_task, weaknesses_task, trend_data_task,
            return_exceptions=True
        )
        
        # 處理異常
        if isinstance(learning_data, Exception):
            learning_data = {}
        if isinstance(weaknesses, Exception):
            weaknesses = []
        if isinstance(trend_data, Exception):
            trend_data = []
        
        # 構建科目進度資料
        subjects = learning_data.get("subjects", [])
        
        progress_data = ChildProgress(
            child_name=child["name"],
            overall_progress=learning_data.get("overall_progress", 0.0),
            accuracy_rate=learning_data.get("accuracy_rate", 0.0),
            study_days=learning_data.get("study_days", 0),
            streak_days=learning_data.get("streak_days", 0),
            subjects=subjects,
            weaknesses=weaknesses,
            trend_data=trend_data
        )
        
        return progress_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取學習進度錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取學習進度失敗"
        )

@app.get("/api/v1/parent/children/{child_id}/communication-advice", response_model=CommunicationAdvice)
async def get_communication_advice_for_child(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """獲取親子溝通建議"""
    try:
        parent_id = current_user["id"]
        children_data = await get_user_children(parent_id)
        
        # 驗證子女是否屬於該家長
        child = next((c for c in children_data if c["id"] == child_id), None)
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="子女不存在或無權限訪問"
            )
        
        # 獲取溝通建議
        advice_data = await get_communication_advice(child_id)
        
        if not advice_data:
            # 返回預設建議
            advice_data = {
                "advice_type": "general",
                "title": "一般性溝通建議",
                "content": "建議與孩子保持開放和耐心的溝通態度，關注孩子的學習興趣和困難。",
                "suggested_topics": ["學習興趣", "學習困難", "學習目標"],
                "mood_analysis": {"overall_mood": "neutral", "confidence": 0.5}
            }
        
        communication_advice = CommunicationAdvice(
            child_id=child_id,
            advice_type=advice_data.get("advice_type", "general"),
            title=advice_data.get("title", "溝通建議"),
            content=advice_data.get("content", ""),
            suggested_topics=advice_data.get("suggested_topics", []),
            mood_analysis=advice_data.get("mood_analysis", {}),
            created_at=datetime.now()
        )
        
        return communication_advice
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取溝通建議錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取溝通建議失敗"
        )

@app.get("/api/v1/parent/dashboard")
async def get_parent_dashboard(current_user: Dict[str, Any] = Depends(get_current_user)):
    """獲取家長儀表板概覽"""
    try:
        parent_id = current_user["id"]
        children_data = await get_user_children(parent_id)
        
        if not children_data:
            return {
                "total_children": 0,
                "overall_stats": {
                    "total_exercises": 0,
                    "average_accuracy": 0.0,
                    "total_study_days": 0,
                    "average_progress": 0.0
                },
                "recent_activities": [],
                "alerts": []
            }
        
        # 並行獲取所有子女的學習資料
        tasks = [get_child_learning_data(child["id"]) for child in children_data]
        learning_data_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 計算總體統計
        total_exercises = 0
        total_accuracy = 0.0
        total_study_days = 0
        total_progress = 0.0
        valid_children = 0
        
        for learning_data in learning_data_list:
            if not isinstance(learning_data, Exception):
                total_exercises += learning_data.get("total_exercises", 0)
                total_accuracy += learning_data.get("accuracy_rate", 0.0)
                total_study_days += learning_data.get("study_days", 0)
                total_progress += learning_data.get("overall_progress", 0.0)
                valid_children += 1
        
        average_accuracy = total_accuracy / valid_children if valid_children > 0 else 0.0
        average_progress = total_progress / valid_children if valid_children > 0 else 0.0
        
        # 獲取最近活動
        recent_activities = await get_recent_activities_for_parent(parent_id)
        
        # 生成警報
        alerts = generate_alerts(children_data, learning_data_list)
        
        dashboard_data = {
            "total_children": len(children_data),
            "overall_stats": {
                "total_exercises": total_exercises,
                "average_accuracy": round(average_accuracy, 2),
                "total_study_days": total_study_days,
                "average_progress": round(average_progress, 2)
            },
            "recent_activities": recent_activities,
            "alerts": alerts
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"獲取儀表板錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取儀表板失敗"
        )

# 輔助函數
async def get_recent_activities(child_id: int) -> List[Dict[str, Any]]:
    """獲取子女的最近學習活動"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LEARNING_SERVICE_URL}/api/v1/learning/students/{child_id}/activities",
                params={"limit": 10}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
    except Exception as e:
        logger.error(f"獲取最近活動錯誤: {e}")
        return []

async def get_recent_activities_for_parent(parent_id: int) -> List[Dict[str, Any]]:
    """獲取家長所有子女的最近活動"""
    try:
        children_data = await get_user_children(parent_id)
        all_activities = []
        
        for child in children_data:
            activities = await get_recent_activities(child["id"])
            for activity in activities:
                activity["child_name"] = child["name"]
                all_activities.append(activity)
        
        # 按時間排序並取前10個
        all_activities.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return all_activities[:10]
        
    except Exception as e:
        logger.error(f"獲取家長活動錯誤: {e}")
        return []

async def get_learning_trend(child_id: int) -> List[Dict[str, Any]]:
    """獲取學習趨勢資料"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LEARNING_SERVICE_URL}/api/v1/learning/students/{child_id}/trend",
                params={"days": 30}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
    except Exception as e:
        logger.error(f"獲取學習趨勢錯誤: {e}")
        return []

def generate_alerts(children_data: List[Dict[str, Any]], learning_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """生成警報"""
    alerts = []
    
    for i, child in enumerate(children_data):
        learning_data = learning_data_list[i] if i < len(learning_data_list) and not isinstance(learning_data_list[i], Exception) else {}
        
        # 檢查學習天數
        study_days = learning_data.get("study_days", 0)
        if study_days == 0:
            alerts.append({
                "type": "warning",
                "title": f"{child['name']} 尚未開始學習",
                "message": "建議鼓勵孩子開始使用學習平台",
                "child_id": child["id"]
            })
        
        # 檢查正確率
        accuracy_rate = learning_data.get("accuracy_rate", 0.0)
        if accuracy_rate < 60.0 and study_days > 0:
            alerts.append({
                "type": "danger",
                "title": f"{child['name']} 學習正確率偏低",
                "message": f"當前正確率為 {accuracy_rate}%，建議加強基礎練習",
                "child_id": child["id"]
            })
        
        # 檢查連續學習天數
        streak_days = learning_data.get("streak_days", 0)
        if streak_days >= 7:
            alerts.append({
                "type": "success",
                "title": f"{child['name']} 連續學習 {streak_days} 天",
                "message": "孩子學習習慣良好，請給予鼓勵",
                "child_id": child["id"]
            })
    
    return alerts

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005) 