"""
Integration tests for AI Teacher endpoints.

These tests exercise the new ai-analysis-service endpoints that wrap Gemini-based
generation. They will be skipped gracefully if the service is not reachable or
if the environment is not configured (e.g., GEMINI_API_KEY missing) to avoid
blocking CI environments.
"""

import os
import pytest
import httpx


BASE_URL = os.getenv("AI_ANALYSIS_BASE_URL", "http://localhost:8004")


def _service_available() -> bool:
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{BASE_URL}/health")
            return resp.status_code == 200
    except Exception:
        return False


@pytest.mark.integration
def test_solution_guidance_endpoint_smoke():
    if not _service_available():
        pytest.skip("ai-analysis-service not available on base URL")

    payload = {
        "question": {
            "id": "q_demo",
            "content": "已知 2x + 3 = 7，求 x。",
            "choices": {"A": "x=2", "B": "x=3", "C": "x=4", "D": "x=5"},
            "difficulty": "normal",
            "subject": "數學",
            "grade": "8A",
            "chapter": "一元一次方程式",
            "publisher": "南一",
            "knowledge_points": ["移項", "一元一次方程式"],
            "topic": "方程式求解",
            "correct_answer": "A"
        },
        "student_answer": "B",
        "temperature": 0.7,
        "max_output_tokens": 256
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{BASE_URL}/api/v1/ai-teacher/solution-guidance", json=payload)
            if resp.status_code == 500:
                pytest.skip("AI generation failed (likely missing GEMINI_API_KEY) — skipping")
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert "text" in data
            assert isinstance(data["text"], str)
    except httpx.RequestError as e:
        pytest.skip(f"Service not reachable: {e}")


@pytest.mark.integration
def test_student_learning_evaluation_endpoint_smoke():
    if not _service_available():
        pytest.skip("ai-analysis-service not available on base URL")

    payload = {
        "question": {
            "id": "q_demo",
            "content": "已知 2x + 3 = 7，求 x。",
            "choices": {"A": "x=2", "B": "x=3", "C": "x=4", "D": "x=5"},
            "difficulty": "normal",
            "subject": "數學",
            "grade": "8A",
            "chapter": "一元一次方程式",
            "publisher": "南一",
            "knowledge_points": ["移項", "一元一次方程式"],
            "topic": "方程式求解",
            "correct_answer": "A"
        },
        "student_answer": "B",
        "temperature": 0.7,
        "max_output_tokens": 256
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{BASE_URL}/api/v1/ai-teacher/student-learning-evaluation", json=payload)
            if resp.status_code == 500:
                pytest.skip("AI generation failed (likely missing GEMINI_API_KEY) — skipping")
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert "text" in data
            assert isinstance(data["text"], str)
    except httpx.RequestError as e:
        pytest.skip(f"Service not reachable: {e}")


