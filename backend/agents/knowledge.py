from openai import OpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

KNOWLEDGE_PROMPT = """你是一位博学的高中学科老师，擅长将复杂概念讲解得通俗易懂。
讲解要求：
1. 用一句话给出核心定义
2. 用生活中的例子或类比帮助理解
3. 说明这个知识点在哪些题型中会用到
4. 列出相关联的知识点（便于构建知识体系）
5. 语言活泼，适合高中生"""

def explain_knowledge(user_input: str, history: list = None) -> str:
    messages = [{"role": "system", "content": KNOWLEDGE_PROMPT}]
    if history:
        messages.extend(history[-4:])
    messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=2000,
        temperature=0.5
    )
    return response.choices[0].message.content
