#!/usr/bin/env python3
"""
Debug Models Script for InULearning Platform

This script helps debug model issues by testing each model individually.
"""

import sys
import os
import traceback

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_learning_session():
    """Debug LearningSession model."""
    print("Debugging LearningSession model...")
    
    try:
        from shared.models.learning_session import LearningSession, SessionStatus, SessionType
        print("✓ Import successful")
        
        # Test session creation
        session = LearningSession(
            user_id=1,
            title="數學練習",
            subject="數學",
            grade="7A",
            version="南一",
            chapter="整數的運算",
            session_type=SessionType.PRACTICE
        )
        print("✓ Session creation successful")
        
        print(f"Session: {session}")
        print(f"Title: {session.title}")
        print(f"Subject: {session.subject}")
        print(f"Session type: {session.session_type}")
        print(f"Status: {session.status}")
        
        return True
        
    except Exception as e:
        print(f"✗ LearningSession debug failed: {e}")
        traceback.print_exc()
        return False

def debug_learning_progress():
    """Debug LearningProgress model."""
    print("Debugging LearningProgress model...")
    
    try:
        from shared.models.learning_progress import LearningProgress
        print("✓ Import successful")
        
        # Test progress creation
        progress = LearningProgress(
            user_id=1,
            subject="數學",
            grade="7A",
            version="南一",
            chapter="整數的運算"
        )
        print("✓ Progress creation successful")
        
        print(f"Progress: {progress}")
        print(f"Subject: {progress.subject}")
        print(f"Is in progress: {progress.is_in_progress}")
        print(f"Progress percentage: {progress.progress_percentage}")
        
        return True
        
    except Exception as e:
        print(f"✗ LearningProgress debug failed: {e}")
        traceback.print_exc()
        return False

def debug_chapter():
    """Debug Chapter model."""
    print("Debugging Chapter model...")
    
    try:
        from shared.models.chapter import Chapter
        print("✓ Import successful")
        
        # Test chapter creation
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
        print("✓ Chapter creation successful")
        
        print(f"Chapter: {chapter}")
        print(f"Chapter ID: {chapter.chapter_id}")
        print(f"Full title: {chapter.full_title}")
        print(f"Is complete: {chapter.is_complete}")
        
        return True
        
    except Exception as e:
        print(f"✗ Chapter debug failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Starting Model Debug...\n")
    
    debug_learning_session()
    print()
    debug_learning_progress()
    print()
    debug_chapter() 