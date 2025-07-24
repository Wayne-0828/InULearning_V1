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
                    question_id=question["question_id"],
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
                "created_at": session.created_at
            }
            
        except Exception as e:
            logger.error(f"Failed to create exercise: {e}")
            await db_session.rollback()
            raise
    
    async def submit_answers(
        self, 
        session_id: str, 
        answers: List[Answer],
        db_session: AsyncSession
    ) -> SubmissionResult:
        """提交答案並獲得批改結果"""
        
        try:
            # 1. 獲取學習會話
            session = await self._get_session(session_id, db_session)
            if not session:
                raise ValueError("學習會話不存在")
            
            if session.status != "active":
                raise ValueError("會話已結束，無法提交答案")
            
            # 2. 獲取學習記錄
            learning_records = await self._get_learning_records(session_id, db_session)
            
            # 3. 批改答案
            results = []
            total_score = Decimal('0')
            correct_count = 0
            
            for answer in answers:
                record = next(
                    (r for r in learning_records if r.question_id == answer.question_id), 
                    None
                )
                
                if not record:
                    continue
                
                # 檢查答案
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
                
                # 生成反饋
                feedback = self._generate_feedback(is_correct)
                
                results.append(QuestionResult(
                    question_id=answer.question_id,
                    correct=is_correct,
                    score=score,
                    feedback=feedback,
                    explanation=explanation
                ))
            
            # 4. 計算總分
            overall_score = (total_score / len(answers)) if answers else Decimal('0')
            accuracy_rate = (correct_count / len(answers)) * 100 if answers else 0
            
            # 5. 更新會話狀態
            session.status = "completed"
            session.overall_score = overall_score
            session.end_time = datetime.utcnow()
            session.time_spent = sum(a.time_spent or 0 for a in answers)
            
            # 6. AI 弱點分析
            weakness_analysis = None
            if len(answers) > 0:
                weakness_analysis = await self._analyze_weaknesses(
                    session, learning_records, db_session
                )
            
            # 7. 更新學習檔案
            await self._update_user_profile(session, overall_score, accuracy_rate, db_session)
            
            # 8. 保存變更
            await db_session.commit()
            
            return SubmissionResult(
                session_id=session_id,
                overall_score=overall_score,
                results=results,
                weakness_analysis=weakness_analysis
            )
            
        except Exception as e:
            logger.error(f"Failed to submit answers: {e}")
            await db_session.rollback()
            raise
    
    async def _get_user_learning_profile(
        self, 
        user_id: str, 
        subject: str, 
        db_session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """獲取用戶學習檔案"""
        # TODO: 實現用戶學習檔案查詢
        return None
    
    async def _adjust_difficulty(
        self, 
        questions: List[Dict[str, Any]], 
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """AI 難度調整"""
        # TODO: 實現 AI 難度調整邏輯
        return questions
    
    def _calculate_estimated_time(self, questions: List[Dict[str, Any]]) -> int:
        """計算預估時間（分鐘）"""
        # 每題平均 2 分鐘
        return len(questions) * 2
    
    async def _get_session(
        self, 
        session_id: str, 
        db_session: AsyncSession
    ) -> Optional[LearningSession]:
        """獲取學習會話"""
        result = await db_session.execute(
            select(LearningSession).where(LearningSession.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_learning_records(
        self, 
        session_id: str, 
        db_session: AsyncSession
    ) -> List[LearningRecord]:
        """獲取學習記錄"""
        result = await db_session.execute(
            select(LearningRecord).where(LearningRecord.session_id == session_id)
        )
        return result.scalars().all()
    
    async def _generate_explanation(
        self, 
        record: LearningRecord, 
        is_correct: bool
    ) -> str:
        """生成題目詳解"""
        # TODO: 實現詳解生成邏輯
        if is_correct:
            return f"答案正確！這題考查的是 {record.topic or '相關概念'}。"
        else:
            return f"答案錯誤。正確答案是 {record.correct_answer}。這題考查的是 {record.topic or '相關概念'}。"
    
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
        """AI 弱點分析"""
        try:
            # 準備分析數據
            analysis_data = {
                "session_id": str(session.id),
                "user_id": str(session.user_id),
                "grade": session.grade,
                "subject": session.subject,
                "publisher": session.publisher,
                "overall_score": float(session.overall_score),
                "records": [
                    {
                        "question_id": r.question_id,
                        "topic": r.topic,
                        "knowledge_points": json.loads(r.knowledge_points) if r.knowledge_points else [],
                        "is_correct": r.is_correct,
                        "time_spent": r.time_spent
                    }
                    for r in records
                ]
            }
            
            # 調用 AI 分析服務
            analysis_result = await self.ai_analysis_client.analyze_weaknesses(analysis_data)
            
            return WeaknessAnalysis(
                weak_concepts=analysis_result.get("weak_concepts", []),
                knowledge_points_to_strengthen=analysis_result.get("knowledge_points_to_strengthen", []),
                recommendations=analysis_result.get("recommendations", [])
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
        # TODO: 實現用戶學習檔案更新邏輯
        pass 