#!/usr/bin/env python3
"""
題庫資料載入腳本
從 rawdata 目錄載入題目資料到 MongoDB
"""

import os
import json
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import asyncio

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings

async def load_rawdata():
    """載入 rawdata 目錄中的題目資料"""
    
    # 連接 MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_database]
    
    # 清空現有題目資料
    await db.questions.delete_many({})
    print("✅ 已清空現有題目資料")
    
    # 檢查 rawdata 目錄
    rawdata_path = Path("/app/rawdata")
    if not rawdata_path.exists():
        print("⚠️ rawdata 目錄不存在，跳過資料載入")
        return
    
    # 遍歷 rawdata 目錄
    question_count = 0
    for file_path in rawdata_path.rglob("*.json"):
        try:
            print(f"📖 載入檔案: {file_path.name}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 處理題目資料
            if isinstance(data, list):
                for item in data:
                    if await process_question_item(db, item):
                        question_count += 1
            elif isinstance(data, dict):
                if await process_question_item(db, data):
                    question_count += 1
                    
        except Exception as e:
            print(f"❌ 載入檔案 {file_path.name} 失敗: {e}")
    
    print(f"✅ 資料載入完成，共載入 {question_count} 道題目")
    
    # 關閉連接
    client.close()

async def process_question_item(db, item):
    """處理單個題目項目"""
    try:
        # 檢查必要欄位（支援新舊格式）
        if 'question' in item and 'answer' in item:
            # 新格式：南一、翰林等題目格式
            return await process_new_format(db, item)
        elif 'content' in item and 'correct_answer' in item:
            # 舊格式：sample_questions.json 格式
            return await process_old_format(db, item)
        else:
            print(f"⚠️ 跳過不完整的題目: {item.get('question_id', 'unknown')}")
            return False
        
    except Exception as e:
        print(f"❌ 處理題目失敗: {e}")
        return False

async def process_new_format(db, item):
    """處理新格式題目（南一、翰林等）"""
    try:
        # 標準化題目格式
        question_doc = {
            'question_id': item.get('question_id', f"{item.get('grade', '')}_{item.get('subject', '')}_{item.get('chapter', '')}"),
            'subject': item.get('subject', ''),
            'grade': item.get('grade', ''),
            'publisher': item.get('publisher', ''),
            'chapter': item.get('chapter', ''),
            'topic': item.get('topic', ''),
            'knowledge_points': item.get('knowledge_point', []),
            'question_type': '選擇題',
            'difficulty': convert_difficulty(item.get('difficulty', 'normal')),
            'content': item.get('question', ''),
            'options': convert_options(item.get('options', {})),
            'correct_answer': item.get('answer', ''),
            'explanation': item.get('explanation', ''),
            'created_at': None,
            'updated_at': None
        }
        
        # 插入資料庫
        await db.questions.insert_one(question_doc)
        return True
        
    except Exception as e:
        print(f"❌ 處理新格式題目失敗: {e}")
        return False

async def process_old_format(db, item):
    """處理舊格式題目（sample_questions.json）"""
    try:
        # 標準化題目格式
        question_doc = {
            'question_id': item.get('question_id', ''),
            'subject': item.get('subject', '數學'),
            'grade': item.get('grade', '7A'),
            'publisher': item.get('publisher', '南一'),
            'chapter': item.get('chapter', ''),
            'topic': item.get('topic', ''),
            'knowledge_points': item.get('knowledge_points', []),
            'question_type': item.get('question_type', '選擇題'),
            'difficulty': item.get('difficulty', '中等'),
            'content': item.get('content', ''),
            'options': item.get('options', []),
            'correct_answer': item.get('correct_answer', ''),
            'explanation': item.get('explanation', ''),
            'created_at': item.get('created_at', None),
            'updated_at': item.get('updated_at', None)
        }
        
        # 插入資料庫
        await db.questions.insert_one(question_doc)
        return True
        
    except Exception as e:
        print(f"❌ 處理舊格式題目失敗: {e}")
        return False

def convert_difficulty(difficulty):
    """轉換難度等級"""
    difficulty_map = {
        'easy': '簡單',
        'normal': '中等',
        'hard': '困難',
        '簡單': '簡單',
        '中等': '中等',
        '困難': '困難'
    }
    return difficulty_map.get(difficulty, '中等')

def convert_options(options):
    """轉換選項格式"""
    if isinstance(options, dict):
        # 新格式：{"A": "選項1", "B": "選項2"}
        return [options.get(key, '') for key in ['A', 'B', 'C', 'D']]
    elif isinstance(options, list):
        # 舊格式：["選項1", "選項2", "選項3", "選項4"]
        return options
    else:
        return []

def create_sample_questions():
    """建立範例題目資料"""
    sample_questions = [
        {
            "question_id": "MATH_001",
            "subject": "數學",
            "grade": "7A",
            "publisher": "南一",
            "chapter": "整數與分數",
            "knowledge_points": ["整數的加法"],
            "question_type": "選擇題",
            "difficulty": "簡單",
            "content": "計算：(-5) + 3 = ?",
            "options": ["-8", "-2", "2", "8"],
            "correct_answer": "-2",
            "explanation": "負數加正數，取絕對值相減，符號取絕對值較大的數的符號。|-5| = 5, |3| = 3, 5 - 3 = 2，因為 -5 的絕對值較大，所以結果為負數，即 -2。"
        },
        {
            "question_id": "MATH_002",
            "subject": "數學",
            "grade": "7A",
            "publisher": "南一",
            "chapter": "整數與分數",
            "knowledge_points": ["整數的減法"],
            "question_type": "選擇題",
            "difficulty": "簡單",
            "content": "計算：7 - (-3) = ?",
            "options": ["4", "10", "-4", "-10"],
            "correct_answer": "10",
            "explanation": "減去負數等於加上正數，所以 7 - (-3) = 7 + 3 = 10。"
        }
    ]
    
    # 將範例題目寫入 rawdata 目錄
    rawdata_path = Path("/app/rawdata")
    rawdata_path.mkdir(exist_ok=True)
    
    sample_file = rawdata_path / "sample_questions.json"
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_questions, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已建立範例題目檔案: {sample_file}")

if __name__ == "__main__":
    # 建立範例題目
    create_sample_questions()
    
    # 載入資料
    asyncio.run(load_rawdata()) 