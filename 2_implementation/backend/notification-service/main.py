"""
通知服務 (Notification Service)
提供學習提醒、成績通知、家長通知等異步通知功能
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import json
import logging
from datetime import datetime, timedelta
import asyncio
import aio_pika
from aio_pika import connect_robust, Message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="通知服務",
    description="提供學習提醒、成績通知、家長通知等異步通知功能",
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
RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"

# 資料模型
class NotificationRequest(BaseModel):
    user_id: int
    notification_type: str  # "learning_reminder", "grade_notification", "parent_notification", "achievement"
    title: str
    message: str
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    metadata: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None

class NotificationResponse(BaseModel):
    id: str
    user_id: int
    notification_type: str
    title: str
    message: str
    status: str  # "pending", "sent", "failed"
    created_at: datetime
    sent_at: Optional[datetime] = None

class NotificationTemplate(BaseModel):
    id: str
    name: str
    notification_type: str
    subject: str
    body_template: str
    variables: List[str]
    is_active: bool = True

# 通知模板
NOTIFICATION_TEMPLATES = {
    "learning_reminder": {
        "subject": "學習提醒",
        "body_template": "親愛的 {student_name}，今天是學習的好日子！建議您花 30 分鐘練習 {subject} 科目，保持學習的連續性。",
        "variables": ["student_name", "subject"]
    },
    "grade_notification": {
        "subject": "成績通知",
        "body_template": "恭喜 {student_name}！您在 {subject} 的練習中取得了 {score} 分的好成績！",
        "variables": ["student_name", "subject", "score"]
    },
    "parent_notification": {
        "subject": "學習進度通知",
        "body_template": "親愛的家長，{student_name} 今天完成了 {subject} 的練習，正確率為 {accuracy}%。",
        "variables": ["student_name", "subject", "accuracy"]
    },
    "achievement": {
        "subject": "成就解鎖",
        "body_template": "恭喜 {student_name} 解鎖了「{achievement_name}」成就！繼續加油！",
        "variables": ["student_name", "achievement_name"]
    },
    "weakness_alert": {
        "subject": "學習弱點提醒",
        "body_template": "親愛的 {student_name}，系統發現您在 {topic} 方面需要加強練習，建議多做相關題目。",
        "variables": ["student_name", "topic"]
    }
}

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
                return response.json()
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

# RabbitMQ 連接管理
class RabbitMQManager:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "notifications"

    async def connect(self):
        """連接到 RabbitMQ"""
        try:
            self.connection = await connect_robust(RABBITMQ_URL)
            self.channel = await self.connection.channel()
            
            # 聲明隊列
            await self.channel.declare_queue(
                self.queue_name,
                durable=True
            )
            
            logger.info("成功連接到 RabbitMQ")
        except Exception as e:
            logger.error(f"RabbitMQ 連接失敗: {e}")
            raise

    async def publish_notification(self, notification_data: Dict[str, Any]):
        """發布通知到隊列"""
        try:
            if not self.channel:
                await self.connect()
            
            message = Message(
                body=json.dumps(notification_data).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            await self.channel.default_exchange.publish(
                message,
                routing_key=self.queue_name
            )
            
            logger.info(f"通知已發布到隊列: {notification_data.get('id')}")
        except Exception as e:
            logger.error(f"發布通知失敗: {e}")
            raise

    async def close(self):
        """關閉連接"""
        if self.connection:
            await self.connection.close()

# 全局 RabbitMQ 管理器
rabbitmq_manager = RabbitMQManager()

# 啟動事件
@app.on_event("startup")
async def startup_event():
    """服務啟動時初始化"""
    await rabbitmq_manager.connect()
    # 啟動通知處理器
    asyncio.create_task(process_notifications())

# 關閉事件
@app.on_event("shutdown")
async def shutdown_event():
    """服務關閉時清理"""
    await rabbitmq_manager.close()

# API 端點
@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "notification-service", "timestamp": datetime.now()}

@app.post("/api/v1/notifications", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """創建通知"""
    try:
        # 生成通知 ID
        notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{notification.user_id}"
        
        # 構建通知資料
        notification_data = {
            "id": notification_id,
            "user_id": notification.user_id,
            "notification_type": notification.notification_type,
            "title": notification.title,
            "message": notification.message,
            "priority": notification.priority,
            "metadata": notification.metadata or {},
            "scheduled_at": notification.scheduled_at.isoformat() if notification.scheduled_at else None,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # 發布到隊列
        await rabbitmq_manager.publish_notification(notification_data)
        
        # 如果是即時通知，立即處理
        if not notification.scheduled_at:
            background_tasks.add_task(process_single_notification, notification_data)
        
        response = NotificationResponse(
            id=notification_id,
            user_id=notification.user_id,
            notification_type=notification.notification_type,
            title=notification.title,
            message=notification.message,
            status="pending",
            created_at=datetime.now()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"創建通知失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="創建通知失敗"
        )

@app.post("/api/v1/notifications/bulk")
async def create_bulk_notifications(
    notifications: List[NotificationRequest],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """批量創建通知"""
    try:
        results = []
        
        for notification in notifications:
            notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{notification.user_id}"
            
            notification_data = {
                "id": notification_id,
                "user_id": notification.user_id,
                "notification_type": notification.notification_type,
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority,
                "metadata": notification.metadata or {},
                "scheduled_at": notification.scheduled_at.isoformat() if notification.scheduled_at else None,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
            
            await rabbitmq_manager.publish_notification(notification_data)
            
            results.append({
                "id": notification_id,
                "status": "queued"
            })
        
        return {
            "message": f"成功創建 {len(results)} 個通知",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"批量創建通知失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量創建通知失敗"
        )

@app.get("/api/v1/notifications/templates", response_model=List[NotificationTemplate])
async def get_notification_templates(current_user: Dict[str, Any] = Depends(get_current_user)):
    """獲取通知模板列表"""
    try:
        templates = []
        for template_id, template_data in NOTIFICATION_TEMPLATES.items():
            template = NotificationTemplate(
                id=template_id,
                name=template_data["subject"],
                notification_type=template_id,
                subject=template_data["subject"],
                body_template=template_data["body_template"],
                variables=template_data["variables"],
                is_active=True
            )
            templates.append(template)
        
        return templates
        
    except Exception as e:
        logger.error(f"獲取通知模板失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取通知模板失敗"
        )

@app.post("/api/v1/notifications/learning-reminder")
async def send_learning_reminder(
    student_id: int,
    subject: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """發送學習提醒"""
    try:
        # 獲取學生資訊
        student_info = await get_user_info(student_id)
        if not student_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="學生不存在"
            )
        
        # 使用模板創建通知
        template = NOTIFICATION_TEMPLATES["learning_reminder"]
        message = template["body_template"].format(
            student_name=student_info["name"],
            subject=subject
        )
        
        notification = NotificationRequest(
            user_id=student_id,
            notification_type="learning_reminder",
            title=template["subject"],
            message=message,
            priority="normal",
            metadata={"subject": subject}
        )
        
        # 創建通知
        result = await create_notification(notification, BackgroundTasks(), current_user)
        
        return {
            "message": "學習提醒已發送",
            "notification_id": result.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"發送學習提醒失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="發送學習提醒失敗"
        )

@app.post("/api/v1/notifications/grade-notification")
async def send_grade_notification(
    student_id: int,
    subject: str,
    score: float,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """發送成績通知"""
    try:
        # 獲取學生資訊
        student_info = await get_user_info(student_id)
        if not student_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="學生不存在"
            )
        
        # 使用模板創建通知
        template = NOTIFICATION_TEMPLATES["grade_notification"]
        message = template["body_template"].format(
            student_name=student_info["name"],
            subject=subject,
            score=score
        )
        
        notification = NotificationRequest(
            user_id=student_id,
            notification_type="grade_notification",
            title=template["subject"],
            message=message,
            priority="normal",
            metadata={"subject": subject, "score": score}
        )
        
        # 創建通知
        result = await create_notification(notification, BackgroundTasks(), current_user)
        
        # 如果是家長，也發送家長通知
        if student_info.get("parent_id"):
            await send_parent_notification(student_info["parent_id"], student_info["name"], subject, score)
        
        return {
            "message": "成績通知已發送",
            "notification_id": result.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"發送成績通知失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="發送成績通知失敗"
        )

@app.post("/api/v1/notifications/weakness-alert")
async def send_weakness_alert(
    student_id: int,
    topic: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """發送弱點提醒"""
    try:
        # 獲取學生資訊
        student_info = await get_user_info(student_id)
        if not student_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="學生不存在"
            )
        
        # 使用模板創建通知
        template = NOTIFICATION_TEMPLATES["weakness_alert"]
        message = template["body_template"].format(
            student_name=student_info["name"],
            topic=topic
        )
        
        notification = NotificationRequest(
            user_id=student_id,
            notification_type="weakness_alert",
            title=template["subject"],
            message=message,
            priority="high",
            metadata={"topic": topic}
        )
        
        # 創建通知
        result = await create_notification(notification, BackgroundTasks(), current_user)
        
        return {
            "message": "弱點提醒已發送",
            "notification_id": result.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"發送弱點提醒失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="發送弱點提醒失敗"
        )

# 背景任務
async def process_notifications():
    """處理通知隊列"""
    try:
        if not rabbitmq_manager.channel:
            await rabbitmq_manager.connect()
        
        # 聲明消費者
        queue = await rabbitmq_manager.channel.declare_queue(
            rabbitmq_manager.queue_name,
            durable=True
        )
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        notification_data = json.loads(message.body.decode())
                        await process_single_notification(notification_data)
                    except Exception as e:
                        logger.error(f"處理通知失敗: {e}")
                        
    except Exception as e:
        logger.error(f"通知處理器錯誤: {e}")

async def process_single_notification(notification_data: Dict[str, Any]):
    """處理單個通知"""
    try:
        notification_id = notification_data["id"]
        user_id = notification_data["user_id"]
        notification_type = notification_data["notification_type"]
        
        logger.info(f"處理通知: {notification_id}")
        
        # 獲取用戶資訊
        user_info = await get_user_info(user_id)
        if not user_info:
            logger.error(f"用戶不存在: {user_id}")
            return
        
        # 根據通知類型處理
        if notification_type == "learning_reminder":
            await send_email_notification(user_info, notification_data)
        elif notification_type == "grade_notification":
            await send_email_notification(user_info, notification_data)
        elif notification_type == "parent_notification":
            await send_email_notification(user_info, notification_data)
        elif notification_type == "achievement":
            await send_email_notification(user_info, notification_data)
        elif notification_type == "weakness_alert":
            await send_email_notification(user_info, notification_data)
        
        # 更新通知狀態
        notification_data["status"] = "sent"
        notification_data["sent_at"] = datetime.now().isoformat()
        
        logger.info(f"通知處理完成: {notification_id}")
        
    except Exception as e:
        logger.error(f"處理通知失敗: {e}")
        notification_data["status"] = "failed"

async def send_email_notification(user_info: Dict[str, Any], notification_data: Dict[str, Any]):
    """發送郵件通知"""
    try:
        # 這裡應該整合實際的郵件服務
        # 目前只是記錄日誌
        logger.info(f"發送郵件通知給 {user_info.get('email', 'unknown')}: {notification_data['title']}")
        
        # 實際的郵件發送邏輯
        # await send_email(
        #     to_email=user_info["email"],
        #     subject=notification_data["title"],
        #     body=notification_data["message"]
        # )
        
    except Exception as e:
        logger.error(f"發送郵件失敗: {e}")
        raise

async def send_parent_notification(parent_id: int, student_name: str, subject: str, score: float):
    """發送家長通知"""
    try:
        # 獲取家長資訊
        parent_info = await get_user_info(parent_id)
        if not parent_info:
            return
        
        # 使用模板創建通知
        template = NOTIFICATION_TEMPLATES["parent_notification"]
        message = template["body_template"].format(
            student_name=student_name,
            subject=subject,
            accuracy=score
        )
        
        notification_data = {
            "id": f"parent_notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{parent_id}",
            "user_id": parent_id,
            "notification_type": "parent_notification",
            "title": template["subject"],
            "message": message,
            "priority": "normal",
            "metadata": {"student_name": student_name, "subject": subject, "score": score},
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # 發布到隊列
        await rabbitmq_manager.publish_notification(notification_data)
        
        logger.info(f"家長通知已發送: {parent_id}")
        
    except Exception as e:
        logger.error(f"發送家長通知失敗: {e}")

# 輔助函數
async def get_user_info(user_id: int) -> Optional[Dict[str, Any]]:
    """獲取用戶資訊"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/v1/users/{user_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
    except Exception as e:
        logger.error(f"獲取用戶資訊失敗: {e}")
        return None

async def send_email(to_email: str, subject: str, body: str):
    """發送郵件（實際實現）"""
    # 這裡應該整合實際的郵件服務，如 SendGrid、AWS SES 等
    # 目前只是佔位符
    logger.info(f"發送郵件到 {to_email}: {subject}")
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007) 