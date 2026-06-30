from openai import OpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

INTENT_PROMPT = """你是一个学科学习意图识别专家。分析用户输入，判断属于以下哪种类型：
1. solver - 用户有具体题目需要解题（数学、物理、化学等计算题或应用题）
2. knowledge - 用户想了解某个知识点、概念或原理
3. quiz - 用户想做练习题巩固知识

只返回一个单词：solver、knowledge 或 quiz，不要任何解释。"""

def identify_intent(user_input: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": INTENT_PROMPT},
            {"role": "user", "content": user_input}
        ],
        max_tokens=10,
        temperature=0
    )
    intent = response.choices[0].message.content.strip().lower()
    if intent not in ["solver", "knowledge", "quiz"]:
        intent = "knowledge"
    return intent
