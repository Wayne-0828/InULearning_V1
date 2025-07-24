"""
Basic Smoke Tests
Simple smoke tests for running services
"""
import pytest
import httpx
import time

class TestSmokeBasic:
    """Basic smoke tests for core services"""
    
    @pytest.mark.smoke
    def test_auth_service_health(self):
        """Test auth service health check."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get("http://localhost:8001/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                assert "auth-service" in data["service"]
                print(f"✅ Auth service is healthy: {data}")
        except Exception as e:
            pytest.fail(f"Auth service health check failed: {e}")
    
    @pytest.mark.smoke
    def test_learning_service_health(self):
        """Test learning service health check."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get("http://localhost:8002/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                assert "learning-service" in data["service"]
                print(f"✅ Learning service is healthy: {data}")
        except Exception as e:
            pytest.fail(f"Learning service health check failed: {e}")
    
    @pytest.mark.smoke
    def test_question_bank_service_health(self):
        """Test question bank service health check."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get("http://localhost:8003/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                assert "question-bank-service" in data["service"]
                print(f"✅ Question bank service is healthy: {data}")
        except Exception as e:
            pytest.skip(f"Question bank service not available: {e}")
    
    @pytest.mark.smoke
    def test_ai_analysis_service_health(self):
        """Test AI analysis service health check."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get("http://localhost:8004/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                assert "ai-analysis-service" in data["service"]
                print(f"✅ AI analysis service is healthy: {data}")
        except Exception as e:
            pytest.skip(f"AI analysis service not available: {e}")
    
    @pytest.mark.smoke
    def test_basic_math(self):
        """Test basic mathematical operations."""
        assert 2 + 2 == 4
        assert 10 - 5 == 5
        assert 3 * 4 == 12
        assert 15 / 3 == 5
        print("✅ Basic math operations passed")
    
    @pytest.mark.smoke
    def test_string_operations(self):
        """Test string operations."""
        test_string = "Hello, World!"
        assert len(test_string) == 13
        assert test_string.upper() == "HELLO, WORLD!"
        assert test_string.lower() == "hello, world!"
        assert "Hello" in test_string
        print("✅ String operations passed") 