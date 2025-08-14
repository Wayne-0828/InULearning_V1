"""
E2E test: submit exercise -> server saves -> AI texts generated -> fetch session detail.

This test uses real services if available. It will be skipped if any dependency
is not reachable to keep CI stable.
"""

import os
import pytest
import httpx
import time


LEARNING_BASE = os.getenv("LEARNING_BASE_URL", "http://localhost:8002")


def _svc_ok(url: str) -> bool:
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get(f"{url}/health")
            return r.status_code == 200
    except Exception:
        return False


@pytest.mark.e2e
def test_submit_and_fetch_session_detail_smoke():
    if not _svc_ok(LEARNING_BASE):
        pytest.skip("learning-service not available")

    # You need a valid auth token for real env. For CI/dev, this may be proxied or not enforced.
    token = os.getenv("TEST_AUTH_TOKEN", "")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Prepare a minimal complete payload
    payload = {
        "session_name": "數學練習 - 自動測試",
        "subject": "數學",
        "grade": "8A",
        "chapter": "一元一次方程式",
        "publisher": "南一",
        "difficulty": "normal",
        "knowledge_points": ["移項", "一元一次方程式"],
        "exercise_results": [
            {
                "question_id": "q_demo_1",
                "subject": "數學",
                "grade": "8A",
                "chapter": "一元一次方程式",
                "publisher": "南一",
                "knowledge_points": ["移項"],
                "question_content": "已知 2x + 3 = 7，求 x。",
                "answer_choices": {"A": "x=2", "B": "x=3", "C": "x=4", "D": "x=5"},
                "difficulty": "normal",
                "question_topic": "方程式求解",
                "user_answer": "B",
                "correct_answer": "A",
                "is_correct": False,
                "score": 0,
                "explanation": "",
                "time_spent": 30
            }
        ],
        "total_time_spent": 30,
        "session_metadata": {"source": "test"}
    }

    # Submit
    with httpx.Client(timeout=60.0) as client:
        r = client.post(f"{LEARNING_BASE}/api/v1/learning/exercises/complete", json=payload, headers=headers)
        if r.status_code in (401, 403):
            pytest.skip("auth required for e2e submit in this environment")
        assert r.status_code == 200, r.text
        data = r.json()
        session_id = data["session_id"]

        # Wait briefly for AI (synchronous MVP should be immediate; still add small delay)
        time.sleep(1.0)

        # Fetch detail
        r2 = client.get(f"{LEARNING_BASE}/api/v1/learning/records/{session_id}", headers=headers)
        assert r2.status_code == 200, r2.text
        detail = r2.json()
        records = detail.get("exercise_records", [])
        assert len(records) >= 1
        rec = records[0]
        # AI texts may be None if AI unavailable; just assert keys exist
        assert "ai_solution_guidance" in rec
        assert "ai_learning_evaluation" in rec


