from openai import OpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

SOLVER_PROMPT = """你是一位耐心的高中学科辅导老师，擅长数学、物理、化学、生物等理科。
解题要求：
1. 先分析题目考查的知识点
2. 列出解题思路（分步骤）
3. 详细写出解题过程，每步说明原因
4. 最后给出答案并总结方法技巧
5. 语言简洁清晰，适合高中生理解"""

def solve_problem(user_input: str, history: list = None) -> str:
    messages = [{"role": "system", "content": SOLVER_PROMPT}]
    if history:
        messages.extend(history[-4:])  # 保留最近2轮对话
    messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=2000,
        temperature=0.3
    )
    return response.choices[0].message.content
