"""
Test Models for InULearning Platform

This module contains tests for all database models to ensure they work correctly.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models
from shared.models.user import User, UserRole
from shared.models.learning_session import LearningSession, SessionStatus, SessionType
from shared.models.learning_record import LearningRecord, AnswerStatus
from shared.models.user_profile import UserProfile
from shared.models.learning_progress import LearningProgress
from shared.models.question import Question, QuestionType, DifficultyLevel
from shared.models.chapter import Chapter
from shared.models.knowledge_point import KnowledgePoint


class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation(self):
        """Test basic user creation."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            first_name="Test",
            last_name="User",
            role=UserRole.STUDENT
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_student is True
        assert user.is_parent is False
        assert user.is_teacher is False
        assert user.is_admin is False
    
    def test_user_roles(self):
        """Test user role functionality."""
        student = User(
            email="student@example.com",
            username="student",
            hashed_password="password",
            first_name="Student",
            last_name="User",
            role=UserRole.STUDENT
        )
        
        parent = User(
            email="parent@example.com",
            username="parent",
            hashed_password="password",
            first_name="Parent",
            last_name="User",
            role=UserRole.PARENT
        )
        
        teacher = User(
            email="teacher@example.com",
            username="teacher",
            hashed_password="password",
            first_name="Teacher",
            last_name="User",
            role=UserRole.TEACHER
        )
        
        assert student.can_access_student_features() is True
        assert parent.can_access_parent_features() is True
        assert teacher.can_access_teacher_features() is True


class TestLearningSessionModel:
    """Test LearningSession model functionality."""
    
    def test_session_creation(self):
        """Test basic session creation."""
        session = LearningSession(
            user_id=1,
            title="數學練習",
            subject="數學",
            grade="7A",
            version="南一",
            chapter="整數的運算",
            session_type=SessionType.PRACTICE
        )
        
        assert session.title == "數學練習"
        assert session.subject == "數學"
        assert session.session_type == SessionType.PRACTICE
        assert session.status == SessionStatus.CREATED
        assert session.is_active is True
        assert session.is_completed is False
    
    def test_session_lifecycle(self):
        """Test session lifecycle methods."""
        session = LearningSession(
            user_id=1,
            title="測試會話",
            subject="數學",
            grade="7A",
            version="南一",
            chapter="測試章節"
        )
        
        # Start session
        session.start_session()
        assert session.status == SessionStatus.IN_PROGRESS
        assert session.started_at is not None
        
        # Pause session
        session.pause_session()
        assert session.status == SessionStatus.PAUSED
        assert session.paused_at is not None
        
        # Resume session
        session.resume_session()
        assert session.status == SessionStatus.IN_PROGRESS
        assert session.resumed_at is not None
        
        # Complete session
        session.complete_session()
        assert session.status == SessionStatus.COMPLETED
        assert session.completed_at is not None
        assert session.is_completed is True
    
    def test_performance_update(self):
        """Test performance update functionality."""
        session = LearningSession(
            user_id=1,
            title="測試會話",
            subject="數學",
            grade="7A",
            version="南一",
            chapter="測試章節"
        )
        
        session.update_performance(80, 100, 1800)  # 80/100 score, 30 minutes
        
        assert session.total_score == 80
        assert session.max_score == 100
        assert session.accuracy_rate == 80
        assert session.time_spent_seconds == 1800


class TestLearningRecordModel:
    """Test LearningRecord model functionality."""
    
    def test_record_creation(self):
        """Test basic record creation."""
        record = LearningRecord(
            session_id=1,
            user_id=1,
            question_id="Q001",
            question_type="multiple_choice",
            question_content="1 + 1 = ?",
            correct_answer="2",
            answer_status=AnswerStatus.CORRECT
        )
        
        assert record.question_id == "Q001"
        assert record.is_correct is True
        assert record.is_incorrect is False
        assert record.was_answered is True
    
    def test_score_update(self):
        """Test score update functionality."""
        record = LearningRecord(
            session_id=1,
            user_id=1,
            question_id="Q001",
            question_type="multiple_choice",
            question_content="測試題目",
            correct_answer="A",
            answer_status=AnswerStatus.INCORRECT
        )
        
        # Update with correct answer
        record.update_score(1, 1)
        assert record.score == 1
        assert record.max_score == 1
        assert record.answer_status == AnswerStatus.CORRECT
        assert record.score_percentage == 100.0
        
        # Update with partial answer
        record.update_score(1, 2)
        assert record.score == 1
        assert record.max_score == 2
        assert record.answer_status == AnswerStatus.PARTIAL
        assert record.score_percentage == 50.0


class TestUserProfileModel:
    """Test UserProfile model functionality."""
    
    def test_profile_creation(self):
        """Test basic profile creation."""
        profile = UserProfile(
            user_id=1,
            grade="7A",
            school="測試中學",
            preferred_subjects=["數學", "英文"],
            preferred_version="南一"
        )
        
        assert profile.grade == "7A"
        assert profile.school == "測試中學"
        assert profile.preferred_subjects == ["數學", "英文"]
        assert profile.is_profile_complete is False
    
    def test_study_stats_update(self):
        """Test study statistics update."""
        profile = UserProfile(user_id=1)
        
        # Update stats after a session
        profile.update_study_stats(30, 10, 85)  # 30 minutes, 10 questions, 85% score
        
        assert profile.total_study_time_hours == 0.5  # 30 minutes = 0.5 hours
        assert profile.total_sessions_completed == 1
        assert profile.total_questions_answered == 10
        assert profile.average_score == 85


class TestLearningProgressModel:
    """Test LearningProgress model functionality."""
    
    def test_progress_creation(self):
        """Test basic progress creation."""
        progress = LearningProgress(
            user_id=1,
            subject="數學",
            grade="7A",
            version="南一",
            chapter="整數的運算"
        )
        
        assert progress.subject == "數學"
        assert progress.is_in_progress is False
        assert progress.progress_percentage == 0.0
    
    def test_progress_update(self):
        """Test progress update functionality."""
        progress = LearningProgress(
            user_id=1,
            subject="數學",
            grade="7A",
            version="南一",
            chapter="整數的運算",
            total_questions=10
        )
        
        # Start learning
        progress.start_learning()
        assert progress.is_started is True
        assert progress.is_in_progress is True
        
        # Update progress
        progress.update_progress(5, 4, 30, 80.0)  # 5 questions, 4 correct, 30 minutes, 80% score
        
        assert progress.completed_questions == 5
        assert progress.correct_answers == 4
        assert progress.completion_percentage == 50.0
        assert progress.accuracy_rate == 80.0
        assert progress.average_score == 80.0
        
        # Complete learning
        progress.update_progress(5, 5, 30, 100.0)  # Complete the remaining 5 questions
        
        assert progress.completion_percentage == 100.0
        assert progress.is_completed is True


class TestQuestionModel:
    """Test Question model functionality."""
    
    def test_question_creation(self):
        """Test basic question creation."""
        question = Question(
            question_id="MATH_001",
            content="下列何者為正數？",
            question_type=QuestionType.MULTIPLE_CHOICE,
            difficulty=DifficultyLevel.EASY,
            subject="數學",
            grade="7A",
            version="南一",
            chapter="整數的運算",
            correct_answer="A",
            options=[
                {"key": "A", "value": "5"},
                {"key": "B", "value": "-3"},
                {"key": "C", "value": "0"},
                {"key": "D", "value": "-7"}
            ]
        )
        
        assert question.question_id == "MATH_001"
        assert question.is_multiple_choice is True
        assert question.has_media is False
        assert question.option_keys == ["A", "B", "C", "D"]
        assert question.get_option_by_key("A") == "5"
    
    def test_answer_validation(self):
        """Test answer validation functionality."""
        question = Question(
            question_id="TEST_001",
            content="測試題目",
            question_type=QuestionType.MULTIPLE_CHOICE,
            difficulty=DifficultyLevel.EASY,
            subject="數學",
            grade="7A",
            version="南一",
            chapter="測試",
            correct_answer="A"
        )
        
        assert question.is_correct_answer("A") is True
        assert question.is_correct_answer("a") is True  # Case insensitive
        assert question.is_correct_answer("B") is False
    
    def test_usage_stats_update(self):
        """Test usage statistics update."""
        question = Question(
            question_id="TEST_001",
            content="測試題目",
            question_type=QuestionType.MULTIPLE_CHOICE,
            difficulty=DifficultyLevel.EASY,
            subject="數學",
            grade="7A",
            version="南一",
            chapter="測試",
            correct_answer="A"
        )
        
        # Update with correct answer
        question.update_usage_stats(True, 30.0)  # Correct, 30 seconds
        
        assert question.usage_count == 1
        assert question.correct_rate == 1.0
        assert question.average_time == 30.0
        
        # Update with incorrect answer
        question.update_usage_stats(False, 45.0)  # Incorrect, 45 seconds
        
        assert question.usage_count == 2
        assert question.correct_rate == 0.5
        assert question.average_time == 37.5  # (30 + 45) / 2


class TestChapterModel:
    """Test Chapter model functionality."""
    
    def test_chapter_creation(self):
        """Test basic chapter creation."""
        chapter = Chapter(
            chapter_id="MATH_7A_01",
            title="整數的運算",
            description="學習整數的加減乘除運算",
            subject="數學",
            grade="7A",
            version="南一",
            chapter_number=1,
            knowledge_points=["正負數", "整數運算"],
            learning_objectives=["理解正負數概念", "掌握整數運算規則"]
        )
        
        assert chapter.chapter_id == "MATH_7A_01"
        assert chapter.full_title == "數學 7A - 整數的運算"
        assert chapter.is_complete is True
        assert chapter.question_availability_rate == 0.0
    
    def test_usage_stats_update(self):
        """Test usage statistics update."""
        chapter = Chapter(
            chapter_id="TEST_001",
            title="測試章節",
            subject="數學",
            grade="7A",
            version="南一",
            chapter_number=1
        )
        
        # Update with completion
        chapter.update_usage_stats(85.0, True)  # 85% score, completed
        
        assert chapter.usage_count == 1
        assert chapter.completion_rate == 100.0
        assert chapter.average_score == 85.0
        
        # Update with partial completion
        chapter.update_usage_stats(60.0, False)  # 60% score, not completed
        
        assert chapter.usage_count == 2
        assert chapter.completion_rate == 50.0  # 1 out of 2 completed
        assert chapter.average_score == 72.5  # (85 + 60) / 2


class TestKnowledgePointModel:
    """Test KnowledgePoint model functionality."""
    
    def test_knowledge_point_creation(self):
        """Test basic knowledge point creation."""
        kp = KnowledgePoint(
            knowledge_point_id="MATH_7A_01_01",
            name="正負數概念",
            description="理解正數、負數的概念及其在數線上的表示",
            subject="數學",
            grade="7A",
            version="南一",
            category="數與量",
            subcategory="整數",
            learning_objectives=["理解正負數概念", "能在數線上表示正負數"],
            key_concepts=["正數", "負數", "數線", "絕對值"]
        )
        
        assert kp.knowledge_point_id == "MATH_7A_01_01"
        assert kp.full_name == "數學 7A - 正負數概念"
        assert kp.hierarchy_path == "數學 > 7A > 數與量 > 整數 > 正負數概念"
        assert kp.is_leaf_node is True
        assert kp.has_parent is False
    
    def test_usage_stats_update(self):
        """Test usage statistics update."""
        kp = KnowledgePoint(
            knowledge_point_id="TEST_001",
            name="測試知識點",
            subject="數學",
            grade="7A",
            version="南一",
            category="測試"
        )
        
        # Update with good score
        kp.update_usage_stats(90.0)
        
        assert kp.usage_count == 1
        assert kp.average_score == 90.0
        
        # Update with lower score
        kp.update_usage_stats(70.0)
        
        assert kp.usage_count == 2
        assert kp.average_score == 80.0  # (90 + 70) / 2
    
    def test_hierarchy_management(self):
        """Test hierarchy management functionality."""
        parent = KnowledgePoint(
            knowledge_point_id="PARENT_001",
            name="父知識點",
            subject="數學",
            grade="7A",
            version="南一",
            category="測試"
        )
        
        child = KnowledgePoint(
            knowledge_point_id="CHILD_001",
            name="子知識點",
            subject="數學",
            grade="7A",
            version="南一",
            category="測試",
            parent_id="PARENT_001"
        )
        
        # Add child to parent
        parent.add_child("CHILD_001")
        
        assert "CHILD_001" in parent.children
        assert child.has_parent is True
        assert parent.is_leaf_node is False


def test_model_relationships():
    """Test model relationships and associations."""
    # Create a user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="password",
        first_name="Test",
        last_name="User",
        role=UserRole.STUDENT
    )
    
    # Create a user profile
    profile = UserProfile(
        user_id=1,
        grade="7A",
        school="測試中學",
        preferred_subjects=["數學", "英文"]
    )
    
    # Create a learning session
    session = LearningSession(
        user_id=1,
        title="數學練習",
        subject="數學",
        grade="7A",
        version="南一",
        chapter="整數的運算"
    )
    
    # Create a learning record
    record = LearningRecord(
        session_id=1,
        user_id=1,
        question_id="Q001",
        question_type="multiple_choice",
        question_content="1 + 1 = ?",
        correct_answer="2",
        answer_status=AnswerStatus.CORRECT,
        subject="數學"
    )
    
    # Create learning progress
    progress = LearningProgress(
        user_id=1,
        subject="數學",
        grade="7A",
        version="南一",
        chapter="整數的運算"
    )
    
    # Test that all models can be created successfully
    assert user is not None
    assert profile is not None
    assert session is not None
    assert record is not None
    assert progress is not None


if __name__ == "__main__":
    # Run basic tests
    print("Running model tests...")
    
    # Test User model
    test_user = TestUserModel()
    test_user.test_user_creation()
    test_user.test_user_roles()
    print("✓ User model tests passed")
    
    # Test LearningSession model
    test_session = TestLearningSessionModel()
    test_session.test_session_creation()
    test_session.test_session_lifecycle()
    test_session.test_performance_update()
    print("✓ LearningSession model tests passed")
    
    # Test LearningRecord model
    test_record = TestLearningRecordModel()
    test_record.test_record_creation()
    test_record.test_score_update()
    print("✓ LearningRecord model tests passed")
    
    # Test UserProfile model
    test_profile = TestUserProfileModel()
    test_profile.test_profile_creation()
    test_profile.test_study_stats_update()
    print("✓ UserProfile model tests passed")
    
    # Test LearningProgress model
    test_progress = TestLearningProgressModel()
    test_progress.test_progress_creation()
    test_progress.test_progress_update()
    print("✓ LearningProgress model tests passed")
    
    # Test Question model
    test_question = TestQuestionModel()
    test_question.test_question_creation()
    test_question.test_answer_validation()
    test_question.test_usage_stats_update()
    print("✓ Question model tests passed")
    
    # Test Chapter model
    test_chapter = TestChapterModel()
    test_chapter.test_chapter_creation()
    test_chapter.test_usage_stats_update()
    print("✓ Chapter model tests passed")
    
    # Test KnowledgePoint model
    test_kp = TestKnowledgePointModel()
    test_kp.test_knowledge_point_creation()
    test_kp.test_usage_stats_update()
    test_kp.test_hierarchy_management()
    print("✓ KnowledgePoint model tests passed")
    
    # Test relationships
    test_model_relationships()
    print("✓ Model relationship tests passed")
    
    print("\n🎉 All model tests passed successfully!") 