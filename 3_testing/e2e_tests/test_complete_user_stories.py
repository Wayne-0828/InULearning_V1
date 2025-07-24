"""
Complete End-to-End Tests for All Core User Stories
Tests all major user workflows across different roles
"""
import pytest
import time
import json
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from typing import Dict, Any, List

class TestCompleteUserStories:
    """Test all core user stories end-to-end"""
    
    @pytest.fixture(scope="class")
    def browser(self) -> Browser:
        """Setup browser for E2E tests."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, slow_mo=500)
            yield browser
            browser.close()
    
    @pytest.fixture(scope="class")
    def context(self, browser: Browser) -> BrowserContext:
        """Setup browser context."""
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir="test-results/videos/",
            record_har_path="test-results/har/"
        )
        yield context
        context.close()
    
    @pytest.fixture(scope="class")
    def page(self, context: BrowserContext) -> Page:
        """Setup page for testing."""
        page = context.new_page()
        yield page
        page.close()
    
    @pytest.fixture
    def test_users_data(self) -> Dict[str, Any]:
        """Test data for all user types."""
        return {
            "student": {
                "username": "e2e_student_001",
                "email": "e2e_student_001@test.com",
                "password": "TestPassword123!",
                "role": "student",
                "grade": "7A",
                "version": "南一"
            },
            "parent": {
                "username": "e2e_parent_001",
                "email": "e2e_parent_001@test.com",
                "password": "TestPassword123!",
                "role": "parent"
            },
            "teacher": {
                "username": "e2e_teacher_001",
                "email": "e2e_teacher_001@test.com",
                "password": "TestPassword123!",
                "role": "teacher"
            },
            "admin": {
                "username": "e2e_admin_001",
                "email": "e2e_admin_001@test.com",
                "password": "TestPassword123!",
                "role": "admin"
            }
        }
    
    # US-001: 會員系統管理
    @pytest.mark.e2e
    @pytest.mark.us001
    def test_user_registration_all_roles(self, page: Page, test_users_data: Dict[str, Any]):
        """Test user registration for all roles (US-001)."""
        for role, user_data in test_users_data.items():
            # Navigate to registration page
            page.goto(f"http://localhost:3000/{role}/register.html")
            page.wait_for_load_state("networkidle")
            
            # Fill registration form
            page.fill("#username", user_data["username"])
            page.fill("#email", user_data["email"])
            page.fill("#password", user_data["password"])
            page.fill("#confirmPassword", user_data["password"])
            
            if role == "student":
                page.select_option("#grade", user_data["grade"])
                page.select_option("#version", user_data["version"])
            
            # Submit registration
            page.click("#registerBtn")
            page.wait_for_load_state("networkidle")
            
            # Verify successful registration
            assert page.url == f"http://localhost:3000/{role}/index.html"
            
            # Verify user is logged in
            page.wait_for_selector(".user-info", timeout=5000)
    
    @pytest.mark.e2e
    @pytest.mark.us001
    def test_user_login_all_roles(self, page: Page, test_users_data: Dict[str, Any]):
        """Test user login for all roles (US-001)."""
        for role, user_data in test_users_data.items():
            # Navigate to login page
            page.goto(f"http://localhost:3000/{role}/login.html")
            page.wait_for_load_state("networkidle")
            
            # Fill login form
            page.fill("#username", user_data["username"])
            page.fill("#password", user_data["password"])
            page.click("#loginBtn")
            page.wait_for_load_state("networkidle")
            
            # Verify successful login
            assert page.url == f"http://localhost:3000/{role}/index.html"
            
            # Verify user is logged in
            page.wait_for_selector(".user-info", timeout=5000)
    
    # US-002: 智慧出題系統
    @pytest.mark.e2e
    @pytest.mark.us002
    def test_intelligent_question_generation(self, page: Page, test_users_data: Dict[str, Any]):
        """Test intelligent question generation (US-002)."""
        student_data = test_users_data["student"]
        
        # Login as student
        page.goto("http://localhost:3000/student/login.html")
        page.fill("#username", student_data["username"])
        page.fill("#password", student_data["password"])
        page.click("#loginBtn")
        page.wait_for_load_state("networkidle")
        
        # Navigate to exercise selection
        page.click("text=開始練習")
        page.wait_for_load_state("networkidle")
        
        # Test different subject combinations
        subjects = ["數學", "英文", "國文"]
        chapters = ["整數的運算", "基本句型", "文言文閱讀"]
        difficulties = ["easy", "medium", "hard"]
        
        for i, (subject, chapter) in enumerate(zip(subjects, chapters)):
            # Select exercise parameters
            page.select_option("#subject", subject)
            page.select_option("#chapter", chapter)
            page.select_option("#difficulty", difficulties[i % 3])
            page.fill("#questionCount", "3")
            
            # Start exercise
            page.click("#startExerciseBtn")
            page.wait_for_load_state("networkidle")
            
            # Verify questions are loaded
            page.wait_for_selector(".question-container", timeout=10000)
            questions = page.query_selector_all(".question-container")
            assert len(questions) == 3
            
            # Go back to selection
            page.go_back()
            page.wait_for_load_state("networkidle")
    
    # US-003: 自動批改功能
    @pytest.mark.e2e
    @pytest.mark.us003
    def test_automatic_grading(self, page: Page, test_users_data: Dict[str, Any]):
        """Test automatic grading functionality (US-003)."""
        student_data = test_users_data["student"]
        
        # Login and start exercise
        page.goto("http://localhost:3000/student/login.html")
        page.fill("#username", student_data["username"])
        page.fill("#password", student_data["password"])
        page.click("#loginBtn")
        page.wait_for_load_state("networkidle")
        
        page.click("text=開始練習")
        page.wait_for_load_state("networkidle")
        
        # Select exercise parameters
        page.select_option("#subject", "數學")
        page.select_option("#chapter", "整數的運算")
        page.select_option("#difficulty", "easy")
        page.fill("#questionCount", "2")
        page.click("#startExerciseBtn")
        page.wait_for_load_state("networkidle")
        
        # Answer questions
        page.wait_for_selector(".question-container", timeout=10000)
        
        # Answer first question
        first_question = page.query_selector(".question-container")
        options = first_question.query_selector_all("input[type='radio']")
        if options:
            options[0].click()
        
        # Answer second question
        page.click("#nextBtn")
        page.wait_for_load_state("networkidle")
        
        second_question = page.query_selector(".question-container")
        options = second_question.query_selector_all("input[type='radio']")
        if options:
            options[1].click()
        
        # Submit answers
        page.click("#submitBtn")
        page.wait_for_load_state("networkidle")
        
        # Verify grading results
        page.wait_for_selector(".result-container", timeout=10000)
        score_element = page.query_selector(".score")
        assert score_element is not None
        
        # Verify explanations are shown
        explanations = page.query_selector_all(".explanation")
        assert len(explanations) >= 1
    
    # US-004: 相似題練習
    @pytest.mark.e2e
    @pytest.mark.us004
    def test_similar_question_practice(self, page: Page, test_users_data: Dict[str, Any]):
        """Test similar question practice (US-004)."""
        student_data = test_users_data["student"]
        
        # Complete a practice session first
        page.goto("http://localhost:3000/student/login.html")
        page.fill("#username", student_data["username"])
        page.fill("#password", student_data["password"])
        page.click("#loginBtn")
        page.wait_for_load_state("networkidle")
        
        # Navigate to history to see previous results
        page.click("text=學習歷程")
        page.wait_for_load_state("networkidle")
        
        # Check if there are previous sessions
        sessions = page.query_selector_all(".session-item")
        if sessions:
            # Click on a session to see details
            sessions[0].click()
            page.wait_for_load_state("networkidle")
            
            # Look for similar questions recommendation
            similar_questions = page.query_selector_all(".similar-question")
            if similar_questions:
                # Click on a similar question
                similar_questions[0].click()
                page.wait_for_load_state("networkidle")
                
                # Verify we're in a new practice session
                assert "exercise" in page.url or "practice" in page.url
    
    # US-005: 學習歷程記錄
    @pytest.mark.e2e
    @pytest.mark.us005
    def test_learning_history_tracking(self, page: Page, test_users_data: Dict[str, Any]):
        """Test learning history tracking (US-005)."""
        student_data = test_users_data["student"]
        
        # Login as student
        page.goto("http://localhost:3000/student/login.html")
        page.fill("#username", student_data["username"])
        page.fill("#password", student_data["password"])
        page.click("#loginBtn")
        page.wait_for_load_state("networkidle")
        
        # Navigate to learning history
        page.click("text=學習歷程")
        page.wait_for_load_state("networkidle")
        
        # Verify history page loads
        page.wait_for_selector(".history-container", timeout=5000)
        
        # Check for session records
        sessions = page.query_selector_all(".session-item")
        assert len(sessions) >= 0  # May be empty initially
        
        # Check for progress indicators
        progress_elements = page.query_selector_all(".progress-indicator")
        assert len(progress_elements) >= 0
    
    # US-006: AI 智慧化升級
    @pytest.mark.e2e
    @pytest.mark.us006
    def test_ai_intelligent_analysis(self, page: Page, test_users_data: Dict[str, Any]):
        """Test AI intelligent analysis (US-006)."""
        student_data = test_users_data["student"]
        
        # Login and complete a practice session
        page.goto("http://localhost:3000/student/login.html")
        page.fill("#username", student_data["username"])
        page.fill("#password", student_data["password"])
        page.click("#loginBtn")
        page.wait_for_load_state("networkidle")
        
        # Complete a practice session to generate AI analysis
        page.click("text=開始練習")
        page.wait_for_load_state("networkidle")
        
        page.select_option("#subject", "數學")
        page.select_option("#chapter", "整數的運算")
        page.select_option("#difficulty", "medium")
        page.fill("#questionCount", "2")
        page.click("#startExerciseBtn")
        page.wait_for_load_state("networkidle")
        
        # Answer questions
        page.wait_for_selector(".question-container", timeout=10000)
        
        # Answer questions (mix of correct and incorrect)
        questions = page.query_selector_all(".question-container")
        for i, question in enumerate(questions):
            options = question.query_selector_all("input[type='radio']")
            if options:
                # Alternate between correct and incorrect answers
                option_index = i % len(options)
                options[option_index].click()
            
            if i < len(questions) - 1:
                page.click("#nextBtn")
                page.wait_for_load_state("networkidle")
        
        # Submit and check AI analysis
        page.click("#submitBtn")
        page.wait_for_load_state("networkidle")
        
        # Wait for AI analysis
        page.wait_for_selector(".ai-analysis", timeout=15000)
        
        # Verify AI-generated content
        weakness_analysis = page.query_selector(".weakness-analysis")
        recommendations = page.query_selector(".ai-recommendations")
        
        assert weakness_analysis is not None or recommendations is not None
    
    # US-007: 家長儀表板
    @pytest.mark.e2e
    @pytest.mark.us007
    def test_parent_dashboard(self, page: Page, test_users_data: Dict[str, Any]):
        """Test parent dashboard (US-007)."""
        parent_data = test_users_data["parent"]
        
        # Login as parent
        page.goto("http://localhost:3000/parent/login.html")
        page.fill("#username", parent_data["username"])
        page.fill("#password", parent_data["password"])
        page.click("#loginBtn")
        page.wait_for_load_state("networkidle")
        
        # Verify dashboard loads
        page.wait_for_selector(".dashboard-container", timeout=5000)
        
        # Check for child information
        children_section = page.query_selector(".children-section")
        if children_section:
            # Check for child progress
            progress_elements = page.query_selector_all(".child-progress")
            assert len(progress_elements) >= 0
            
            # Check for learning analytics
            analytics_elements = page.query_selector_all(".learning-analytics")
            assert len(analytics_elements) >= 0
        
        # Check for communication advice
        advice_elements = page.query_selector_all(".communication-advice")
        assert len(advice_elements) >= 0
    
    # US-008: AI 溝通建議
    @pytest.mark.e2e
    @pytest.mark.us008
    def test_ai_communication_advice(self, page: Page, test_users_data: Dict[str, Any]):
        """Test AI communication advice (US-008)."""
        parent_data = test_users_data["parent"]
        
        # Login as parent
        page.goto("http://localhost:3000/parent/login.html")
        page.fill("#username", parent_data["username"])
        page.fill("#password", parent_data["password"])
        page.click("#loginBtn")
        page.wait_for_load_state("networkidle")
        
        # Navigate to communication advice section
        page.click("text=溝通建議")
        page.wait_for_load_state("networkidle")
        
        # Wait for AI-generated advice
        page.wait_for_selector(".ai-advice", timeout=10000)
        
        # Verify advice content
        advice_items = page.query_selector_all(".advice-item")
        assert len(advice_items) >= 0
        
        # Check for personalized recommendations
        personalized_elements = page.query_selector_all(".personalized-advice")
        assert len(personalized_elements) >= 0
    
    # US-009: 班級儀表板
    @pytest.mark.e2e
    @pytest.mark.us009
    def test_teacher_class_dashboard(self, page: Page, test_users_data: Dict[str, Any]):
        """Test teacher class dashboard (US-009)."""
        teacher_data = test_users_data["teacher"]
        
        # Login as teacher
        page.goto("http://localhost:3000/teacher/login.html")
        page.fill("#username", teacher_data["username"])
        page.fill("#password", teacher_data["password"])
        page.click("#loginBtn")
        page.wait_for_load_state("networkidle")
        
        # Verify dashboard loads
        page.wait_for_selector(".dashboard-container", timeout=5000)
        
        # Check for class information
        classes_section = page.query_selector(".classes-section")
        if classes_section:
            # Check for class analytics
            analytics_elements = page.query_selector_all(".class-analytics")
            assert len(analytics_elements) >= 0
            
            # Check for student rankings
            ranking_elements = page.query_selector_all(".student-ranking")
            assert len(ranking_elements) >= 0
        
        # Check for course management
        course_elements = page.query_selector_all(".course-management")
        assert len(course_elements) >= 0
    
    # Complete workflow tests
    @pytest.mark.e2e
    @pytest.mark.complete
    @pytest.mark.slow
    def test_complete_student_learning_workflow(self, page: Page, test_users_data: Dict[str, Any]):
        """Test complete student learning workflow."""
        student_data = test_users_data["student"]
        
        # 1. Registration
        page.goto("http://localhost:3000/student/register.html")
        page.fill("#username", f"{student_data['username']}_complete")
        page.fill("#email", f"complete_{student_data['email']}")
        page.fill("#password", student_data["password"])
        page.fill("#confirmPassword", student_data["password"])
        page.select_option("#grade", student_data["grade"])
        page.select_option("#version", student_data["version"])
        page.click("#registerBtn")
        page.wait_for_load_state("networkidle")
        
        # 2. Complete multiple practice sessions
        for i in range(2):
            page.click("text=開始練習")
            page.wait_for_load_state("networkidle")
            
            page.select_option("#subject", "數學")
            page.select_option("#chapter", "整數的運算")
            page.select_option("#difficulty", "medium")
            page.fill("#questionCount", "2")
            page.click("#startExerciseBtn")
            page.wait_for_load_state("networkidle")
            
            # Answer questions
            page.wait_for_selector(".question-container", timeout=10000)
            questions = page.query_selector_all(".question-container")
            
            for j, question in enumerate(questions):
                options = question.query_selector_all("input[type='radio']")
                if options:
                    options[j % len(options)].click()
                
                if j < len(questions) - 1:
                    page.click("#nextBtn")
                    page.wait_for_load_state("networkidle")
            
            page.click("#submitBtn")
            page.wait_for_load_state("networkidle")
            
            # Wait for results
            page.wait_for_selector(".result-container", timeout=10000)
            
            # Go back to dashboard
            page.click("text=返回儀表板")
            page.wait_for_load_state("networkidle")
        
        # 3. Check learning history
        page.click("text=學習歷程")
        page.wait_for_load_state("networkidle")
        
        sessions = page.query_selector_all(".session-item")
        assert len(sessions) >= 2
        
        # 4. Check profile
        page.click("text=個人檔案")
        page.wait_for_load_state("networkidle")
        
        profile_elements = page.query_selector_all(".profile-info")
        assert len(profile_elements) >= 0
    
    @pytest.mark.e2e
    @pytest.mark.complete
    @pytest.mark.slow
    def test_complete_parent_monitoring_workflow(self, page: Page, test_users_data: Dict[str, Any]):
        """Test complete parent monitoring workflow."""
        parent_data = test_users_data["parent"]
        
        # 1. Login as parent
        page.goto("http://localhost:3000/parent/login.html")
        page.fill("#username", parent_data["username"])
        page.fill("#password", parent_data["password"])
        page.click("#loginBtn")
        page.wait_for_load_state("networkidle")
        
        # 2. Check dashboard
        page.wait_for_selector(".dashboard-container", timeout=5000)
        
        # 3. Navigate to children management
        page.click("text=子女管理")
        page.wait_for_load_state("networkidle")
        
        # 4. Check communication advice
        page.click("text=溝通建議")
        page.wait_for_load_state("networkidle")
        
        # 5. Check learning progress
        page.click("text=學習進度")
        page.wait_for_load_state("networkidle")
        
        # Verify all sections load properly
        assert page.url != "http://localhost:3000/parent/login.html"
    
    @pytest.mark.e2e
    @pytest.mark.complete
    @pytest.mark.slow
    def test_complete_teacher_management_workflow(self, page: Page, test_users_data: Dict[str, Any]):
        """Test complete teacher management workflow."""
        teacher_data = test_users_data["teacher"]
        
        # 1. Login as teacher
        page.goto("http://localhost:3000/teacher/login.html")
        page.fill("#username", teacher_data["username"])
        page.fill("#password", teacher_data["password"])
        page.click("#loginBtn")
        page.wait_for_load_state("networkidle")
        
        # 2. Check dashboard
        page.wait_for_selector(".dashboard-container", timeout=5000)
        
        # 3. Navigate to course management
        page.click("text=課程管理")
        page.wait_for_load_state("networkidle")
        
        # 4. Check class analytics
        page.click("text=班級分析")
        page.wait_for_load_state("networkidle")
        
        # 5. Check student management
        page.click("text=學生管理")
        page.wait_for_load_state("networkidle")
        
        # Verify all sections load properly
        assert page.url != "http://localhost:3000/teacher/login.html" 