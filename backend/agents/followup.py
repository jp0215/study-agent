from openai import OpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

FOLLOWUP_PROMPT = """根据对话内容，生成3个简短的追问建议，帮助学生深入学习。
要求：
- 每条15字以内
- 有梯度：巩固 → 拓展 → 应用
- 直接输出3条，每条一行，不加编号和符号"""


def generate_followups(user_input: str, reply: str) -> list[str]:
    content = f"用户问：{user_input}\n\n回答：{reply[:300]}"
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": FOLLOWUP_PROMPT},
            {"role": "user", "content": content}
        ],
        max_tokens=100,
        temperature=0.7
    )
    lines = response.choices[0].message.content.strip().split("\n")
    return [l.strip() for l in lines if l.strip()][:3]
