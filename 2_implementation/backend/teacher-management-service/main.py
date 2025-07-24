"""
教師管理服務 (Teacher Management Service)
提供教師查看班級管理、學生追蹤、課程分析等功能
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
    title="教師管理服務",
    description="提供教師查看班級管理、學生追蹤、課程分析等功能",
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
class ClassInfo(BaseModel):
    id: int
    name: str
    grade: int
    subject: str
    student_count: int
    average_progress: float
    average_accuracy: float
    created_at: datetime

class StudentInfo(BaseModel):
    id: int
    name: str
    grade: int
    class_name: str
    student_id: str
    avatar: Optional[str] = None
    total_exercises: int = 0
    accuracy_rate: float = 0.0
    study_days: int = 0
    overall_progress: float = 0.0
    last_active: Optional[datetime] = None

class ClassAnalytics(BaseModel):
    class_id: int
    class_name: str
    total_students: int
    active_students: int
    average_progress: float
    average_accuracy: float
    subject_breakdown: List[Dict[str, Any]]
    student_rankings: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]

class CourseInfo(BaseModel):
    id: int
    name: str
    subject: str
    grade: int
    description: str
    total_lessons: int
    completed_lessons: int
    average_completion_rate: float
    created_at: datetime

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
                if user_data.get("role") != "teacher":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="只有教師角色可以訪問此服務"
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

async def get_teacher_classes(teacher_id: int) -> List[Dict[str, Any]]:
    """獲取教師的班級列表"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/v1/teachers/{teacher_id}/classes"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"獲取班級列表失敗: {response.status_code}")
                return []
    except httpx.RequestError as e:
        logger.error(f"獲取班級列表錯誤: {e}")
        return []

async def get_class_students(class_id: int) -> List[Dict[str, Any]]:
    """獲取班級的學生列表"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/v1/classes/{class_id}/students"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"獲取學生列表失敗: {response.status_code}")
                return []
    except httpx.RequestError as e:
        logger.error(f"獲取學生列表錯誤: {e}")
        return []

async def get_student_learning_data(student_id: int) -> Dict[str, Any]:
    """獲取學生的學習資料"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LEARNING_SERVICE_URL}/api/v1/learning/students/{student_id}/summary"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"獲取學習資料失敗: {response.status_code}")
                return {}
    except httpx.RequestError as e:
        logger.error(f"獲取學習資料錯誤: {e}")
        return {}

async def get_class_learning_analytics(class_id: int) -> Dict[str, Any]:
    """獲取班級的學習分析資料"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LEARNING_SERVICE_URL}/api/v1/learning/classes/{class_id}/analytics"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"獲取班級分析失敗: {response.status_code}")
                return {}
    except httpx.RequestError as e:
        logger.error(f"獲取班級分析錯誤: {e}")
        return {}

# API 端點
@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "teacher-management-service", "timestamp": datetime.now()}

@app.get("/api/v1/teacher/classes", response_model=List[ClassInfo])
async def get_teacher_classes_endpoint(current_user: Dict[str, Any] = Depends(get_current_user)):
    """獲取教師的班級列表"""
    try:
        teacher_id = current_user["id"]
        classes_data = await get_teacher_classes(teacher_id)
        
        # 並行獲取每個班級的學習資料
        tasks = []
        for class_info in classes_data:
            task = get_class_learning_analytics(class_info["id"])
            tasks.append(task)
        
        analytics_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整合資料
        enriched_classes = []
        for i, class_info in enumerate(classes_data):
            analytics = analytics_list[i] if not isinstance(analytics_list[i], Exception) else {}
            
            enriched_class = ClassInfo(
                id=class_info["id"],
                name=class_info["name"],
                grade=class_info["grade"],
                subject=class_info["subject"],
                student_count=class_info.get("student_count", 0),
                average_progress=analytics.get("average_progress", 0.0),
                average_accuracy=analytics.get("average_accuracy", 0.0),
                created_at=datetime.fromisoformat(class_info["created_at"])
            )
            enriched_classes.append(enriched_class)
        
        return enriched_classes
        
    except Exception as e:
        logger.error(f"獲取班級列表錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取班級列表失敗"
        )

@app.get("/api/v1/teacher/classes/{class_id}/students", response_model=List[StudentInfo])
async def get_class_students_endpoint(
    class_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """獲取班級的學生列表"""
    try:
        teacher_id = current_user["id"]
        teacher_classes = await get_teacher_classes(teacher_id)
        
        # 驗證班級是否屬於該教師
        class_info = next((c for c in teacher_classes if c["id"] == class_id), None)
        if not class_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="班級不存在或無權限訪問"
            )
        
        students_data = await get_class_students(class_id)
        
        # 並行獲取每個學生的學習資料
        tasks = []
        for student in students_data:
            task = get_student_learning_data(student["id"])
            tasks.append(task)
        
        learning_data_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整合資料
        enriched_students = []
        for i, student in enumerate(students_data):
            learning_data = learning_data_list[i] if not isinstance(learning_data_list[i], Exception) else {}
            
            enriched_student = StudentInfo(
                id=student["id"],
                name=student["name"],
                grade=student["grade"],
                class_name=student.get("class_name", ""),
                student_id=student.get("student_id", ""),
                avatar=student.get("avatar"),
                total_exercises=learning_data.get("total_exercises", 0),
                accuracy_rate=learning_data.get("accuracy_rate", 0.0),
                study_days=learning_data.get("study_days", 0),
                overall_progress=learning_data.get("overall_progress", 0.0),
                last_active=datetime.fromisoformat(learning_data.get("last_active", datetime.now().isoformat())) if learning_data.get("last_active") else None
            )
            enriched_students.append(enriched_student)
        
        return enriched_students
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取學生列表錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取學生列表失敗"
        )

@app.get("/api/v1/teacher/classes/{class_id}/analytics", response_model=ClassAnalytics)
async def get_class_analytics_endpoint(
    class_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """獲取班級的詳細分析資料"""
    try:
        teacher_id = current_user["id"]
        teacher_classes = await get_teacher_classes(teacher_id)
        
        # 驗證班級是否屬於該教師
        class_info = next((c for c in teacher_classes if c["id"] == class_id), None)
        if not class_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="班級不存在或無權限訪問"
            )
        
        # 並行獲取各種資料
        students_task = get_class_students(class_id)
        analytics_task = get_class_learning_analytics(class_id)
        
        students_data, analytics_data = await asyncio.gather(
            students_task, analytics_task,
            return_exceptions=True
        )
        
        # 處理異常
        if isinstance(students_data, Exception):
            students_data = []
        if isinstance(analytics_data, Exception):
            analytics_data = {}
        
        # 獲取學生學習資料
        student_learning_tasks = []
        for student in students_data:
            task = get_student_learning_data(student["id"])
            student_learning_tasks.append(task)
        
        student_learning_list = await asyncio.gather(*student_learning_tasks, return_exceptions=True)
        
        # 構建學生排名
        student_rankings = []
        for i, student in enumerate(students_data):
            learning_data = student_learning_list[i] if not isinstance(student_learning_list[i], Exception) else {}
            
            ranking_data = {
                "student_id": student["id"],
                "student_name": student["name"],
                "overall_progress": learning_data.get("overall_progress", 0.0),
                "accuracy_rate": learning_data.get("accuracy_rate", 0.0),
                "total_exercises": learning_data.get("total_exercises", 0),
                "study_days": learning_data.get("study_days", 0)
            }
            student_rankings.append(ranking_data)
        
        # 按進度排序
        student_rankings.sort(key=lambda x: x["overall_progress"], reverse=True)
        
        # 計算活躍學生數量
        active_students = sum(1 for learning_data in student_learning_list 
                            if not isinstance(learning_data, Exception) and learning_data.get("study_days", 0) > 0)
        
        # 構建分析資料
        analytics = ClassAnalytics(
            class_id=class_id,
            class_name=class_info["name"],
            total_students=len(students_data),
            active_students=active_students,
            average_progress=analytics_data.get("average_progress", 0.0),
            average_accuracy=analytics_data.get("average_accuracy", 0.0),
            subject_breakdown=analytics_data.get("subject_breakdown", []),
            student_rankings=student_rankings,
            recent_activities=analytics_data.get("recent_activities", []),
            alerts=generate_class_alerts(students_data, student_learning_list)
        )
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取班級分析錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取班級分析失敗"
        )

@app.get("/api/v1/teacher/courses", response_model=List[CourseInfo])
async def get_teacher_courses_endpoint(current_user: Dict[str, Any] = Depends(get_current_user)):
    """獲取教師的課程列表"""
    try:
        teacher_id = current_user["id"]
        
        # 獲取教師的課程資料
        courses_data = await get_teacher_courses(teacher_id)
        
        # 並行獲取每個課程的完成率資料
        tasks = []
        for course in courses_data:
            task = get_course_completion_data(course["id"])
            tasks.append(task)
        
        completion_data_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整合資料
        enriched_courses = []
        for i, course in enumerate(courses_data):
            completion_data = completion_data_list[i] if not isinstance(completion_data_list[i], Exception) else {}
            
            enriched_course = CourseInfo(
                id=course["id"],
                name=course["name"],
                subject=course["subject"],
                grade=course["grade"],
                description=course.get("description", ""),
                total_lessons=course.get("total_lessons", 0),
                completed_lessons=completion_data.get("completed_lessons", 0),
                average_completion_rate=completion_data.get("average_completion_rate", 0.0),
                created_at=datetime.fromisoformat(course["created_at"])
            )
            enriched_courses.append(enriched_course)
        
        return enriched_courses
        
    except Exception as e:
        logger.error(f"獲取課程列表錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取課程列表失敗"
        )

@app.get("/api/v1/teacher/dashboard")
async def get_teacher_dashboard(current_user: Dict[str, Any] = Depends(get_current_user)):
    """獲取教師儀表板概覽"""
    try:
        teacher_id = current_user["id"]
        
        # 並行獲取各種資料
        classes_task = get_teacher_classes(teacher_id)
        courses_task = get_teacher_courses(teacher_id)
        
        classes_data, courses_data = await asyncio.gather(
            classes_task, courses_task,
            return_exceptions=True
        )
        
        # 處理異常
        if isinstance(classes_data, Exception):
            classes_data = []
        if isinstance(courses_data, Exception):
            courses_data = []
        
        # 獲取班級分析資料
        class_analytics_tasks = []
        for class_info in classes_data:
            task = get_class_learning_analytics(class_info["id"])
            class_analytics_tasks.append(task)
        
        class_analytics_list = await asyncio.gather(*class_analytics_tasks, return_exceptions=True)
        
        # 計算總體統計
        total_students = 0
        total_progress = 0.0
        total_accuracy = 0.0
        valid_classes = 0
        
        for analytics in class_analytics_list:
            if not isinstance(analytics, Exception):
                total_students += analytics.get("total_students", 0)
                total_progress += analytics.get("average_progress", 0.0)
                total_accuracy += analytics.get("average_accuracy", 0.0)
                valid_classes += 1
        
        average_progress = total_progress / valid_classes if valid_classes > 0 else 0.0
        average_accuracy = total_accuracy / valid_classes if valid_classes > 0 else 0.0
        
        # 獲取最近活動
        recent_activities = await get_recent_activities_for_teacher(teacher_id)
        
        # 生成警報
        alerts = generate_teacher_alerts(classes_data, class_analytics_list)
        
        dashboard_data = {
            "total_classes": len(classes_data),
            "total_courses": len(courses_data),
            "total_students": total_students,
            "overall_stats": {
                "average_progress": round(average_progress, 2),
                "average_accuracy": round(average_accuracy, 2),
                "active_classes": valid_classes
            },
            "recent_activities": recent_activities,
            "alerts": alerts
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"獲取教師儀表板錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取教師儀表板失敗"
        )

# 輔助函數
async def get_teacher_courses(teacher_id: int) -> List[Dict[str, Any]]:
    """獲取教師的課程列表"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/v1/teachers/{teacher_id}/courses"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"獲取課程列表失敗: {response.status_code}")
                return []
    except httpx.RequestError as e:
        logger.error(f"獲取課程列表錯誤: {e}")
        return []

async def get_course_completion_data(course_id: int) -> Dict[str, Any]:
    """獲取課程完成率資料"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LEARNING_SERVICE_URL}/api/v1/learning/courses/{course_id}/completion"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"獲取課程完成率失敗: {response.status_code}")
                return {}
    except httpx.RequestError as e:
        logger.error(f"獲取課程完成率錯誤: {e}")
        return {}

async def get_recent_activities_for_teacher(teacher_id: int) -> List[Dict[str, Any]]:
    """獲取教師的最近活動"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LEARNING_SERVICE_URL}/api/v1/learning/teachers/{teacher_id}/activities",
                params={"limit": 10}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
    except Exception as e:
        logger.error(f"獲取教師活動錯誤: {e}")
        return []

def generate_class_alerts(students_data: List[Dict[str, Any]], student_learning_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """生成班級警報"""
    alerts = []
    
    # 檢查學習進度偏低的學生
    low_progress_students = []
    for i, student in enumerate(students_data):
        learning_data = student_learning_list[i] if i < len(student_learning_list) and not isinstance(student_learning_list[i], Exception) else {}
        
        progress = learning_data.get("overall_progress", 0.0)
        if progress < 50.0 and learning_data.get("study_days", 0) > 0:
            low_progress_students.append({
                "name": student["name"],
                "progress": progress
            })
    
    if low_progress_students:
        alerts.append({
            "type": "warning",
            "title": "學習進度偏低的學生",
            "message": f"有 {len(low_progress_students)} 名學生學習進度低於 50%",
            "details": low_progress_students
        })
    
    # 檢查不活躍的學生
    inactive_students = []
    for i, student in enumerate(students_data):
        learning_data = student_learning_list[i] if i < len(student_learning_list) and not isinstance(student_learning_list[i], Exception) else {}
        
        study_days = learning_data.get("study_days", 0)
        if study_days == 0:
            inactive_students.append(student["name"])
    
    if inactive_students:
        alerts.append({
            "type": "danger",
            "title": "不活躍的學生",
            "message": f"有 {len(inactive_students)} 名學生尚未開始學習",
            "details": inactive_students
        })
    
    return alerts

def generate_teacher_alerts(classes_data: List[Dict[str, Any]], class_analytics_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """生成教師警報"""
    alerts = []
    
    # 檢查班級平均進度
    low_progress_classes = []
    for i, class_info in enumerate(classes_data):
        analytics = class_analytics_list[i] if i < len(class_analytics_list) and not isinstance(class_analytics_list[i], Exception) else {}
        
        average_progress = analytics.get("average_progress", 0.0)
        if average_progress < 60.0:
            low_progress_classes.append({
                "name": class_info["name"],
                "progress": average_progress
            })
    
    if low_progress_classes:
        alerts.append({
            "type": "warning",
            "title": "班級學習進度偏低",
            "message": f"有 {len(low_progress_classes)} 個班級平均進度低於 60%",
            "details": low_progress_classes
        })
    
    # 檢查班級活躍度
    inactive_classes = []
    for i, class_info in enumerate(classes_data):
        analytics = class_analytics_list[i] if i < len(class_analytics_list) and not isinstance(class_analytics_list[i], Exception) else {}
        
        active_students = analytics.get("active_students", 0)
        total_students = analytics.get("total_students", 0)
        
        if total_students > 0 and (active_students / total_students) < 0.5:
            inactive_classes.append({
                "name": class_info["name"],
                "active_rate": round((active_students / total_students) * 100, 1)
            })
    
    if inactive_classes:
        alerts.append({
            "type": "info",
            "title": "班級活躍度偏低",
            "message": f"有 {len(inactive_classes)} 個班級活躍學生比例低於 50%",
            "details": inactive_classes
        })
    
    return alerts

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 