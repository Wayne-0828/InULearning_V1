"""
練習服務

負責個人化練習會話的創建、答案處理和批改功能
"""

import logging
import json
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from ..models.learning_session import LearningSession, LearningRecord
from ..models.schemas import (
    ExerciseParams, Question, Answer, QuestionResult, 
    SubmissionResult, WeaknessAnalysis
)
from ..utils.database import get_db_session
from .question_bank_client import QuestionBankClient
from .ai_analysis_client import AIAnalysisClient

logger = logging.getLogger(__name__)


class ExerciseService:
    """練習服務類別"""
    
    def __init__(self):
        self.question_bank_client = QuestionBankClient()
        self.ai_analysis_client = AIAnalysisClient()
    
    async def create_personalized_exercise(
        self, 
        user_id: str, 
        params: ExerciseParams,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """創建個人化練習會話"""
        
        try:
            # 1. 獲取用戶學習檔案
            user_profile = await self._get_user_learning_profile(
                user_id, params.subject, db_session
            )
            
            # 2. 從題庫獲取題目
            questions = await self.question_bank_client.get_questions_by_criteria(
                grade=params.grade,
                subject=params.subject,
                publisher=params.publisher,
                chapter=params.chapter,
                difficulty=params.difficulty,
                knowledge_points=params.knowledge_points,
                limit=params.question_count
            )
            
            if not questions:
                raise ValueError("無法找到符合條件的題目")
            
            # 3. AI 難度調整（如果沒有指定難度）
            if not params.difficulty and user_profile:
                questions = await self._adjust_difficulty(questions, user_profile)
            
            # 4. 創建學習會話
            session_id = str(uuid4())
            session = LearningSession(
                id=session_id,
                user_id=user_id,
                session_type="practice",
                grade=params.grade,
                subject=params.subject,
                publisher=params.publisher,
                chapter=params.chapter,
                difficulty=params.difficulty,
                question_count=len(questions),
                start_time=datetime.utcnow(),
                status="active"
            )
            
            db_session.add(session)
            await db_session.commit()
            
            # 5. 創建學習記錄
            learning_records = []
            for question in questions:
                record = LearningRecord(
                    session_id=session_id,
                    question_id=question["id"],  # 修正字段名
                    grade=question["grade"],
                    subject=question["subject"],
                    publisher=question["publisher"],
                    chapter=question["chapter"],
                    topic=question.get("topic"),
                    knowledge_points=json.dumps(question.get("knowledge_point", [])),
                    difficulty=question["difficulty"],
                    correct_answer=question["answer"]
                )
                learning_records.append(record)
            
            db_session.add_all(learning_records)
            await db_session.commit()
            
            # 6. 計算預估時間
            estimated_time = self._calculate_estimated_time(questions)
            
            return {
                "session_id": session_id,
                "questions": questions,
                "estimated_time": estimated_time,
                "created_at": session.start_time
            }
            
        except Exception as e:
            logger.error(f"Failed to create exercise: {e}")
            raise
    
    async def submit_answers(
        self, 
        session_id: str, 
        answers: List[Answer],
        db_session: AsyncSession
    ) -> SubmissionResult:
        """提交答案並獲得批改結果"""
        
        try:
            # 1. 獲取會話和學習記錄
            session = await self._get_session(session_id, db_session)
            if not session:
                raise ValueError("會話不存在")
            
            if session.status != "active":
                raise ValueError("會話已結束，無法提交答案")
            
            records = await self._get_learning_records(session_id, db_session)
            
            # 2. 批改答案
            results = []
            total_score = Decimal('0')
            correct_count = 0
            
            for answer in answers:
                # 找到對應的學習記錄
                record = next((r for r in records if r.question_id == answer.question_id), None)
                if not record:
                    continue
                
                # 判斷是否正確
                is_correct = answer.user_answer == record.correct_answer
                score = Decimal('10') if is_correct else Decimal('0')
                
                if is_correct:
                    correct_count += 1
                total_score += score
                
                # 更新學習記錄
                record.user_answer = answer.user_answer
                record.is_correct = is_correct
                record.score = score
                record.time_spent = answer.time_spent
                
                # 生成詳解
                explanation = await self._generate_explanation(record, is_correct)
                feedback = self._generate_feedback(is_correct)
                
                results.append(QuestionResult(
                    question_id=answer.question_id,
                    correct=is_correct,
                    score=score,
                    feedback=feedback,
                    explanation=explanation
                ))
            
            # 3. 更新會話狀態
            session.status = "completed"
            session.end_time = datetime.utcnow()
            session.overall_score = total_score
            session.time_spent = sum(a.time_spent or 0 for a in answers)
            
            await db_session.commit()
            
            # 4. 生成弱點分析（跳過 AI 分析）
            weakness_analysis = await self._analyze_weaknesses(session, records, db_session)
            
            # 5. 更新用戶檔案
            accuracy_rate = correct_count / len(answers) if answers else 0
            await self._update_user_profile(session, total_score, accuracy_rate, db_session)
            
            return SubmissionResult(
                session_id=session_id,
                overall_score=total_score,
                results=results,
                weakness_analysis=weakness_analysis
            )
            
        except Exception as e:
            logger.error(f"Failed to submit answers: {e}")
            raise
    
    async def _get_user_learning_profile(
        self, 
        user_id: str, 
        subject: str, 
        db_session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """獲取用戶學習檔案"""
        
        try:
            # 這裡可以實現獲取用戶學習檔案的邏輯
            # 暫時返回 None，表示沒有學習檔案
            return None
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    async def _adjust_difficulty(
        self, 
        questions: List[Dict[str, Any]], 
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """調整題目難度"""
        
        # 這裡可以實現基於用戶檔案的難度調整邏輯
        # 暫時返回原題目
        return questions
    
    def _calculate_estimated_time(self, questions: List[Dict[str, Any]]) -> int:
        """計算預估時間"""
        
        # 每題預估 3 分鐘
        return len(questions) * 3
    
    async def _get_session(
        self, 
        session_id: str, 
        db_session: AsyncSession
    ) -> Optional[LearningSession]:
        """獲取學習會話"""
        
        try:
            result = await db_session.execute(
                select(LearningSession).where(LearningSession.id == session_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    async def _get_learning_records(
        self, 
        session_id: str, 
        db_session: AsyncSession
    ) -> List[LearningRecord]:
        """獲取學習記錄"""
        
        try:
            result = await db_session.execute(
                select(LearningRecord).where(LearningRecord.session_id == session_id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get learning records: {e}")
            return []
    
    async def _generate_explanation(
        self, 
        record: LearningRecord, 
        is_correct: bool
    ) -> str:
        """生成題目詳解"""
        
        # 這裡可以實現詳細的題目詳解生成邏輯
        # 暫時返回基礎詳解
        subject = record.subject
        chapter = record.chapter
        
        if subject == "數學":
            return f"這是一道{chapter}的題目。正確答案是 {record.correct_answer}。請仔細檢查解題步驟，確保理解相關概念。"
        elif subject == "國文":
            return f"這是一道{chapter}的題目。正確答案是 {record.correct_answer}。請注意文意理解和字詞運用。"
        elif subject == "英文":
            return f"這是一道{chapter}的題目。正確答案是 {record.correct_answer}。請注意文法規則和單字用法。"
        else:
            return f"這是一道{chapter}的題目。正確答案是 {record.correct_answer}。請仔細閱讀題目要求。"
    
    def _generate_feedback(self, is_correct: bool) -> str:
        """生成反饋"""
        
        if is_correct:
            return "答案正確！解題步驟清楚。"
        else:
            return "答案錯誤，請重新檢視解題步驟。"
    
    async def _analyze_weaknesses(
        self, 
        session: LearningSession, 
        records: List[LearningRecord], 
        db_session: AsyncSession
    ) -> Optional[WeaknessAnalysis]:
        """分析學習弱點（跳過 AI 分析）"""
        
        try:
            # 分析錯誤題目
            incorrect_records = [r for r in records if not r.is_correct]
            
            # 提取弱點概念
            weak_concepts = []
            knowledge_points_to_strengthen = []
            
            for record in incorrect_records:
                try:
                    knowledge_points = json.loads(record.knowledge_points) if record.knowledge_points else []
                    weak_concepts.extend(knowledge_points)
                    knowledge_points_to_strengthen.extend(knowledge_points)
                except:
                    pass
            
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
            
            return WeaknessAnalysis(
                weak_concepts=weak_concepts,
                knowledge_points_to_strengthen=knowledge_points_to_strengthen,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze weaknesses: {e}")
            return None
    
    async def _update_user_profile(
        self, 
        session: LearningSession, 
        overall_score: Decimal, 
        accuracy_rate: float, 
        db_session: AsyncSession
    ):
        """更新用戶學習檔案"""
        
        try:
            # 這裡可以實現更新用戶學習檔案的邏輯
            # 暫時跳過，避免複雜性
            pass
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}") 