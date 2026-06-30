from openai import OpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

QUIZ_PROMPT = """你是一位出题经验丰富的高中学科老师。
出题要求：
1. 根据用户提到的知识点或上下文，出2-3道变式练习题
2. 题目难度循序渐进（基础→提高）
3. 每道题后给出答案和简要解析
4. 题型多样（选择题、填空题、计算题）
5. 注明每道题考查的核心知识点"""

def generate_quiz(user_input: str, history: list = None) -> str:
    messages = [{"role": "system", "content": QUIZ_PROMPT}]
    if history:
        messages.extend(history[-4:])
    messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=2000,
        temperature=0.7
    )
    return response.choices[0].message.content
