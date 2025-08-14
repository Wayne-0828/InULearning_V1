import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# 讀取 API KEY
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")  
genai.configure(api_key=api_key)


def student_learning_evaluation(question: dict, student_answer: str, temperature: float = 1.0, max_output_tokens: int = 512):
    """
    學生學習狀況評估
    
    Args:
        question: 題目資料字典
        student_answer: 學生答案
        temperature: 生成溫度 (0-2.0)
        max_output_tokens: 最大輸出長度
    
    Returns:
        dict: 包含學生學習狀況評估的字典
    """
    prompt = f"""你是一位耐心且鼓勵學生的國中老師。根據題目資料與學生作答情況，請生成「學生學習狀況評估」的內容（請獨立一段文字輸出）。

內容須包含：
1. 分析學生對相關知識點的理解現況。
2. 說明學生可能存在的常見誤解或遇到的學習困難。
3. 根據題目所屬科目（國文、英文、數學、自然、社會），給出對應學科常見學習難點的具體建議。

題目資料：{json.dumps(question, ensure_ascii=False, indent=2)}
學生答案：{student_answer}
"""

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature": temperature,
            "top_p": 0.95,
            "max_output_tokens": max_output_tokens
        }
    )
    
    evaluation_json = {"學生學習狀況評估": None}
    
    try:
        evaluation_response = model.generate_content(prompt).text
        evaluation_json["學生學習狀況評估"] = evaluation_response
    except Exception as e:
        evaluation_json["學生學習狀況評估"] = f"評估生成失敗：{str(e)}"
    
    return evaluation_json


def solution_guidance(question: dict, student_answer: str, temperature: float = 1.0, max_output_tokens: int = 512):
    """
    題目詳解與教學建議
    
    Args:
        question: 題目資料字典
        student_answer: 學生答案
        temperature: 生成溫度 (0-2.0)
        max_output_tokens: 最大輸出長度
    
    Returns:
        dict: 包含題目詳解與教學建議的字典
    """
    prompt = f"""你是一位耐心且引導式的國中老師。根據題目資料與學生作答情況，請生成「題目詳解與教學建議」的內容（請合併為一段文字，不要條列）。

內容須包含：
1. 詳細解釋題目的核心概念。
2. 說明正確答案的理由。
3. 根據此題的難度與學生常見迷思，提出具體可行的學習建議，建議內容可以包含：
   - 推薦回顧哪些教材章節
   - 適合的練習方式
   - 補強資源
   - 本題型容易出現的理解誤區提醒

題目資料：{json.dumps(question, ensure_ascii=False, indent=2)}
學生答案：{student_answer}"""

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature": temperature,
            "top_p": 0.95,
            "max_output_tokens": max_output_tokens
        }
    )
    
    guidance_json = {"題目詳解與教學建議": None}
    
    try:
        guidance_response = model.generate_content(prompt).text
        guidance_json["題目詳解與教學建議"] = guidance_response
    except Exception as e:
        guidance_json["題目詳解與教學建議"] = f"建議生成失敗：{str(e)}"
    
    return guidance_json


# 測試範例
if __name__ == "__main__":
    # 測試題目資料
    question = {
        "grade": "7A",
        "subject": "數學",
        "publisher": "翰林",
        "chapter": "1-1正數與負數",
        "topic": "正數與負數",
        "knowledge_point": [
            "正負數的定義",
            "數線表示"
        ],
        "difficulty": "easy",
        "question": "下列關於正數與負數的敘述，何者正確？",
        "options": {
            "A": "$0$ 是正數。",
            "B": "$0$ 是負數。",
            "C": "$0$ 既不是正數也不是負數。",
            "D": "$0$ 是最小的正數。"
        },
        "answer": "C",
        "explanation": "$0$ 既不是正數也不是負數，它是正負數的分界點。"
    }

    student_answer = "B"
    temperature = 1.0
    max_output_tokens = 512

    # 測試函數
    print("=== 學生學習狀況評估 ===")
    evaluation_result = student_learning_evaluation(question, student_answer, temperature, max_output_tokens)
    print(json.dumps(evaluation_result, ensure_ascii=False, indent=2))
    
    print("\n=== 題目詳解與教學建議 ===")
    guidance_result = solution_guidance(question, student_answer, temperature, max_output_tokens)
    print(json.dumps(guidance_result, ensure_ascii=False, indent=2))




