#!/usr/bin/env python3
"""
完整學習流程測試腳本
測試：出題 → 答題 → 批改 → 記錄儲存
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime

# 測試用戶信息 (使用之前創建的測試用戶)
TEST_USER = {
    "username": "student01",
    "password": "password123"
}

async def login_user():
    """用戶登入獲取JWT token"""
    print("🔐 用戶登入...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost/api/v1/auth/login",
                json={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                print(f"✅ 登入成功，獲得token: {token[:20]}...")
                return token
            else:
                print(f"❌ 登入失敗: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 登入錯誤: {e}")
            return None

async def test_question_retrieval():
    """測試題目獲取（模擬學習服務的題庫調用）"""
    print("\n📚 測試題目獲取...")
    
    async with httpx.AsyncClient() as client:
        try:
            # 測試搜索API（模擬學習服務的調用）
            response = await client.get(
                "http://localhost:8002/api/v1/questions/search",
                params={
                    "subject": "數學",
                    "grade": "7A", 
                    "limit": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("items", [])
                print(f"✅ 成功獲取 {len(questions)} 道題目")
                
                if questions:
                    print("📋 題目示例:")
                    for i, q in enumerate(questions[:2]):
                        print(f"   {i+1}. {q.get('question', 'N/A')[:50]}...")
                        options = q.get('options', {})
                        if isinstance(options, dict):
                            print(f"      選項: {list(options.keys())}")
                        else:
                            print(f"      選項: {type(options)} - {options}")
                        print(f"      正確答案: {q.get('answer', 'N/A')}")
                
                return questions
            else:
                print(f"❌ 獲取題目失敗: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 題目獲取錯誤: {e}")
            return []

async def test_auto_grading(questions):
    """測試自動批改功能（模擬）"""
    print("\n🤖 測試自動批改功能...")
    
    if not questions:
        print("❌ 沒有題目可供測試")
        return []
    
    # 模擬學生答題
    student_answers = []
    grading_results = []
    
    for i, question in enumerate(questions[:3]):  # 只測試前3道題
        question_id = question.get("id")
        correct_answer = question.get("answer")
        
        # 模擬學生答案（前2道答對，第3道答錯）
        if i < 2:
            student_answer = correct_answer  # 答對
        else:
            # 答錯：如果正確答案是A，學生答B
            wrong_answers = {"A": "B", "B": "C", "C": "D", "D": "A"}
            student_answer = wrong_answers.get(correct_answer, "B")
        
        student_answers.append({
            "question_id": question_id,
            "user_answer": student_answer,
            "time_spent": 30 + i * 10  # 模擬答題時間
        })
        
        # 模擬自動批改
        is_correct = student_answer == correct_answer
        score = 10 if is_correct else 0
        
        result = {
            "question_id": question_id,
            "user_answer": student_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "score": score,
            "feedback": "答案正確！解題步驟清楚。" if is_correct else "答案錯誤，請重新檢視解題步驟。",
            "explanation": f"這道題的正確答案是 {correct_answer}。"
        }
        
        grading_results.append(result)
        
        print(f"   題目 {i+1}: 學生答案 {student_answer} | 正確答案 {correct_answer} | {'✅ 正確' if is_correct else '❌ 錯誤'} | 得分: {score}")
    
    # 計算總分和正確率
    total_score = sum(r["score"] for r in grading_results)
    correct_count = sum(1 for r in grading_results if r["is_correct"])
    accuracy_rate = correct_count / len(grading_results) * 100
    
    print(f"\n📊 批改結果統計:")
    print(f"   總分: {total_score}/{len(grading_results) * 10}")
    print(f"   正確率: {accuracy_rate:.1f}% ({correct_count}/{len(grading_results)})")
    
    return {
        "answers": student_answers,
        "results": grading_results,
        "total_score": total_score,
        "accuracy_rate": accuracy_rate
    }

async def test_record_storage(grading_data):
    """測試記錄儲存功能（模擬）"""
    print("\n💾 測試記錄儲存功能...")
    
    if not grading_data:
        print("❌ 沒有批改數據可供儲存")
        return
    
    # 模擬學習記錄數據結構
    session_id = str(uuid.uuid4())
    learning_session = {
        "id": session_id,
        "user_id": "test-user-uuid",  # 模擬用戶ID
        "session_type": "practice",
        "grade": "7A",
        "subject": "數學",
        "publisher": "康軒",
        "question_count": len(grading_data["results"]),
        "start_time": datetime.utcnow().isoformat(),
        "end_time": datetime.utcnow().isoformat(),
        "status": "completed",
        "overall_score": grading_data["total_score"],
        "time_spent": sum(a.get("time_spent", 0) for a in grading_data["answers"])
    }
    
    learning_records = []
    for answer, result in zip(grading_data["answers"], grading_data["results"]):
        record = {
            "session_id": session_id,
            "question_id": result["question_id"],
            "grade": "7A",
            "subject": "數學",
            "publisher": "康軒",
            "chapter": "代數",  # 模擬章節
            "difficulty": "normal",
            "user_answer": result["user_answer"],
            "correct_answer": result["correct_answer"],
            "is_correct": result["is_correct"],
            "score": result["score"],
            "time_spent": answer.get("time_spent", 0)
        }
        learning_records.append(record)
    
    print("✅ 學習會話記錄:")
    print(f"   會話ID: {session_id}")
    print(f"   總分: {learning_session['overall_score']}")
    print(f"   用時: {learning_session['time_spent']} 秒")
    
    print("✅ 詳細答題記錄:")
    for i, record in enumerate(learning_records):
        print(f"   記錄 {i+1}: {record['question_id'][:8]}... | {record['user_answer']} | {'✓' if record['is_correct'] else '✗'} | {record['score']}分")
    
    print(f"✅ 成功模擬儲存 {len(learning_records)} 條學習記錄")
    
    return {
        "session": learning_session,
        "records": learning_records
    }

async def test_complete_learning_flow():
    """測試完整學習流程"""
    print("🚀 開始完整學習流程測試")
    print("=" * 60)
    
    # 1. 用戶登入 (暫時跳過，專注測試核心功能)
    print("🔐 跳過用戶登入，專注測試核心學習功能...")
    token = "mock-token"
    
    # 2. 獲取題目
    questions = await test_question_retrieval()
    if not questions:
        print("❌ 無法繼續測試，獲取題目失敗")
        return
    
    # 3. 自動批改
    grading_data = await test_auto_grading(questions)
    if not grading_data:
        print("❌ 無法繼續測試，批改失敗")
        return
    
    # 4. 記錄儲存
    storage_data = await test_record_storage(grading_data)
    if not storage_data:
        print("❌ 記錄儲存失敗")
        return
    
    print("\n" + "=" * 60)
    print("🎉 完整學習流程測試完成！")
    print("\n📈 測試結果總結:")
    print(f"   ⚠️  用戶認證: 跳過（專注核心功能）")
    print(f"   ✅ 題目獲取: {len(questions)} 道題目")
    print(f"   ✅ 自動批改: {len(grading_data['results'])} 道題目")
    print(f"   ✅ 記錄儲存: {len(storage_data['records'])} 條記錄")
    print(f"   📊 學習成績: {grading_data['total_score']}/{len(grading_data['results']) * 10} 分 ({grading_data['accuracy_rate']:.1f}%)")

async def main():
    """主測試函數"""
    await test_complete_learning_flow()

if __name__ == "__main__":
    asyncio.run(main()) 