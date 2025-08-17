import google.generativeai as genai
import os
from dotenv import load_dotenv
import os

# 讀取 API KEY（假設你已經設在 .env 或環境變數中）

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")  
genai.configure(api_key=api_key)

#學生學習狀況評估
def student_learning_evaluation(question: dict, student_anwser: str, temperature : int, max_output_tokens : int):


    prompt = f"""你是一位經驗豐富的國中老師。請根據下方提供的 [題目資料] 以及 [學生的錯誤答案]，針對該名學生的學習狀況進行簡短評估。

            評估內容應獨立為一個段落，並包含以下兩個重點：
            1.  **知識點理解分析**：從學生的錯誤選項，精準分析他對於這個題目相關的知識點，可能處於哪個理解階段（例如：初步認識但混淆、概念完全錯誤、或是在細節上出錯）。
            2.  **潛在學習困難**：結合該學科（國文、英文、數學、自然、社會）的常見學習難點，推測學生可能遇到的學習瓶頸或困難。例如，在數學上可能是計算粗心或公式應用不熟練；在社會科可能是無法理解因果關係或時序混亂。

            請用明確且具建設性的語氣，客觀地分析學生的學習狀況，目的是為了幫助老師或家長更了解學生的學習盲點。
            題目資料：{question}
            學生答案：{student_anwser}
            """


    model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config={
        "temperature": temperature,     # 溫度，0~2.0 越低越穩定
        "top_p": 0.95,          # (可選) Nucleus sampling
        "max_output_tokens": max_output_tokens  # (可選) 最長輸出長度
    }
    )
    evaluation_json = {"學生學習狀況評估" : None}

    evaluation_response = model.generate_content(prompt).text

    evaluation_json["學生學習狀況評估"] = evaluation_response 

    return evaluation_json

#題目詳解與教學建議
def solution_guidance(question: dict, student_anwser: str, temperature : int, max_output_tokens : int):

    prompt =f"""請根據下方提供的 [題目資料] 以及 [學生的錯誤答案]，撰寫一段給答錯學生的回饋。

            這段回饋內容應合併為一個段落，不要使用條列式，且必須包含以下三個部分：
            1.  **核心概念解釋**：用學生能理解的語言，詳細解釋這道題目背後的核心知識點或原理。
            2.  **正確答案說明**：清楚說明為什麼正確答案是這個選項，並與核心概念連結。
            3.  **具體學習建議**：
                * 根據這題的難度與對應學科（國文、英文、數學、自然、社會）的特性，點出學生容易出現的理解誤區或常見迷思。
                * 提出具體且可行的學習方法，例如：建議學生回去複習課本的特定章節、推薦適合的練習方式（如：多做圖表題、練習長篇閱讀等），或提供相關的補強資源。

            不要帶有語助詞以及語氣成述結果，請直接切入主題。整體語氣要耐心、鼓勵且具體，目的是幫助學生更好地理解這道題目和相關知識點。

            ---
            [題目資料]:{question}
            [學生的錯誤答案]：{student_anwser}  """
    guidance_json = {"題目詳解與教學建議" : None}
    model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config={
        "temperature": temperature,     # 溫度，0~2.0 越低越穩定
        "top_p": 0.95,          # (可選) Nucleus sampling
        "max_output_tokens": max_output_tokens  # (可選) 最長輸出長度
    }
    )

    guidance_response =  model.generate_content(prompt).text

    guidance_json["題目詳解與教學建議"] = guidance_response

    return guidance_json



#####使用name__main__來測試功能

if __name__ == "__main__":

    question = {
        "grade": "7A",
        "subject": "國文",
        "publisher": "翰林",
        "chapter": "夏夜",
        "topic": "詩歌賞析",
        "knowledge_point": [
            "意象",
            "譬喻",
            "擬人",
            "詩歌主旨"
        ],
        "difficulty": "normal",
        "question": "楊喚的《夏夜》一詩中，詩人透過哪些意象的描寫，營造出夏夜寧靜而充滿生機的氛圍？下列選項何者說明最為恰當？",
        "options": {
            "A": "「小河」的流動與「螢火蟲」的閃爍，象徵時間的快速流逝。",
            "B": "「小蟲」的歌唱與「青蛙」的鼓噪，展現夏夜的熱鬧喧囂。",
            "C": "「星星」的眨眼與「月亮」的微笑，運用擬人手法，使夏夜充滿童趣與生命力。",
            "D": "「夜風」的輕拂與「花草」的搖曳，暗示夏夜的涼爽與寂寥。"
        },
        "answer": "C",
        "explanation": "《夏夜》一詩中，「星星」的眨眼和「月亮」的微笑，是詩人運用擬人法，將無生命的星月賦予人的動作與情感，使夏夜的景象更為生動活潑，充滿童趣與生命力，營造出寧靜而富有生機的氛圍。選項A的「時間快速流逝」與詩意不符；選項B的「熱鬧喧囂」與詩中寧靜的氛圍不符；選項D的「寂寥」與詩中充滿生命力的氛圍不符。"
    }
        

    student_answer = "D"
    temperature = 2
    max_output_token = 512
    print(student_learning_evaluation(question, student_answer, temperature, max_output_token))

    print(solution_guidance(question, student_answer, temperature, max_output_token))      