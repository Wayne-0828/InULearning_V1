from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.schemas import (
    QuestionCreate, QuestionUpdate, QuestionSearchCriteria,
    ChapterCreate, KnowledgePointCreate
)
from app.database import DatabaseManager


class QuestionCRUD:
    """題目 CRUD 操作"""
    
    @staticmethod
    async def create_question(db: DatabaseManager, question: QuestionCreate) -> str:
        """創建題目"""
        collection = await db.get_questions_collection()
        
        question_data = question.dict()
        question_data["created_at"] = datetime.utcnow()
        question_data["updated_at"] = datetime.utcnow()
        
        result = await collection.insert_one(question_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_question_by_id(db: DatabaseManager, question_id: str) -> Optional[Dict[str, Any]]:
        """根據ID獲取題目"""
        collection = await db.get_questions_collection()
        
        try:
            question = await collection.find_one({"_id": ObjectId(question_id)})
            if question:
                question["id"] = str(question["_id"])
                del question["_id"]
            return question
        except:
            return None
    
    @staticmethod
    async def update_question(db: DatabaseManager, question_id: str, question_update: QuestionUpdate) -> bool:
        """更新題目"""
        collection = await db.get_questions_collection()
        
        update_data = question_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            result = await collection.update_one(
                {"_id": ObjectId(question_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    async def delete_question(db: DatabaseManager, question_id: str) -> bool:
        """刪除題目"""
        collection = await db.get_questions_collection()
        
        try:
            result = await collection.delete_one({"_id": ObjectId(question_id)})
            return result.deleted_count > 0
        except:
            return False
    
    @staticmethod
    async def search_questions(db: DatabaseManager, criteria: QuestionSearchCriteria) -> Dict[str, Any]:
        """搜尋題目"""
        collection = await db.get_questions_collection()
        
        # 構建查詢條件
        query = {}
        
        if criteria.grade:
            query["grade"] = criteria.grade
        if criteria.subject:
            query["subject"] = criteria.subject
        if criteria.publisher:
            query["publisher"] = criteria.publisher
        if criteria.chapter:
            query["chapter"] = {"$regex": criteria.chapter, "$options": "i"}
        if criteria.topic:
            query["topic"] = {"$regex": criteria.topic, "$options": "i"}
        if criteria.knowledge_point:
            query["knowledge_point"] = {"$in": criteria.knowledge_point}
        if criteria.difficulty:
            query["difficulty"] = criteria.difficulty
        if criteria.question_type:
            query["question_type"] = criteria.question_type
        if criteria.tags:
            query["tags"] = {"$in": criteria.tags}
        if criteria.keyword:
            query["$or"] = [
                {"question": {"$regex": criteria.keyword, "$options": "i"}},
                {"explanation": {"$regex": criteria.keyword, "$options": "i"}},
                {"topic": {"$regex": criteria.keyword, "$options": "i"}}
            ]
        
        # 執行查詢
        total = await collection.count_documents(query)
        cursor = collection.find(query).skip(criteria.skip).limit(criteria.limit)
        
        questions = []
        async for question in cursor:
            question["id"] = str(question["_id"])
            del question["_id"]
            questions.append(question)
        
        return {
            "items": questions,
            "total": total,
            "skip": criteria.skip,
            "limit": criteria.limit
        }
    
    @staticmethod
    async def get_random_questions(
        db: DatabaseManager,
        grade: str,
        subject: str,
        publisher: str,
        count: int = 10,
        exclude_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """隨機獲取題目"""
        collection = await db.get_questions_collection()
        
        query = {
            "grade": grade,
            "subject": subject,
            "publisher": publisher
        }
        
        if exclude_ids:
            exclude_object_ids = [ObjectId(qid) for qid in exclude_ids]
            query["_id"] = {"$nin": exclude_object_ids}
        
        # 使用聚合管道隨機選擇
        pipeline = [
            {"$match": query},
            {"$sample": {"size": count}}
        ]
        
        questions = []
        async for question in collection.aggregate(pipeline):
            question["id"] = str(question["_id"])
            del question["_id"]
            questions.append(question)
        
        return questions
    
    @staticmethod
    async def get_questions_by_criteria(
        db: DatabaseManager,
        grade: str,
        subject: str,
        publisher: str,
        chapter: Optional[str] = None,
        difficulty: Optional[str] = None,
        knowledge_points: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """根據條件獲取題目"""
        collection = await db.get_questions_collection()
        
        query = {
            "grade": grade,
            "subject": subject,
            "publisher": publisher
        }
        
        if chapter:
            query["chapter"] = chapter
        if difficulty:
            query["difficulty"] = difficulty
        if knowledge_points:
            query["knowledge_point"] = {"$in": knowledge_points}
        
        cursor = collection.find(query).limit(limit)
        
        questions = []
        async for question in cursor:
            question["id"] = str(question["_id"])
            del question["_id"]
            questions.append(question)
        
        return questions


class ChapterCRUD:
    """章節 CRUD 操作"""
    
    @staticmethod
    async def create_chapter(db: DatabaseManager, chapter: ChapterCreate) -> str:
        """創建章節"""
        collection = await db.get_chapters_collection()
        
        chapter_data = chapter.dict()
        chapter_data["created_at"] = datetime.utcnow()
        chapter_data["updated_at"] = datetime.utcnow()
        
        result = await collection.insert_one(chapter_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_chapters_by_subject_grade(
        db: DatabaseManager,
        subject: str,
        grade: str,
        publisher: str
    ) -> List[Dict[str, Any]]:
        """根據科目年級獲取章節"""
        collection = await db.get_chapters_collection()
        
        query = {
            "subject": subject,
            "grade": grade,
            "publisher": publisher
        }
        
        cursor = collection.find(query).sort("chapter_number", 1)
        
        chapters = []
        async for chapter in cursor:
            chapter["id"] = str(chapter["_id"])
            del chapter["_id"]
            chapters.append(chapter)
        
        return chapters


class KnowledgePointCRUD:
    """知識點 CRUD 操作"""
    
    @staticmethod
    async def create_knowledge_point(db: DatabaseManager, knowledge_point: KnowledgePointCreate) -> str:
        """創建知識點"""
        collection = await db.get_knowledge_points_collection()
        
        knowledge_point_data = knowledge_point.dict()
        knowledge_point_data["created_at"] = datetime.utcnow()
        knowledge_point_data["updated_at"] = datetime.utcnow()
        
        result = await collection.insert_one(knowledge_point_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_knowledge_points_by_subject_grade(
        db: DatabaseManager,
        subject: str,
        grade: str
    ) -> List[Dict[str, Any]]:
        """根據科目年級獲取知識點"""
        collection = await db.get_knowledge_points_collection()
        
        query = {
            "subject": subject,
            "grade": grade
        }
        
        cursor = collection.find(query).sort("name", 1)
        
        knowledge_points = []
        async for knowledge_point in cursor:
            knowledge_point["id"] = str(knowledge_point["_id"])
            del knowledge_point["_id"]
            knowledge_points.append(knowledge_point)
        
        return knowledge_points 