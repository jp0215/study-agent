from openai import OpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

CROSS_SUBJECT_PROMPT = """你是一位跨学科联系专家。根据题目内容，简要指出：
这道题除了本学科知识外，还涉及哪些其他学科的知识点？
要求：
- 最多提2个跨学科联系
- 每条一行，格式：[学科] 关联点
- 如无明显跨学科联系，只输出：无
- 不要额外解释"""


def find_cross_subject(question: str, subject: str) -> list[str]:
    """发现题目中的跨学科联系"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": CROSS_SUBJECT_PROMPT},
                {"role": "user", "content": f"学科：{subject}\n题目：{question}"}
            ],
            max_tokens=80,
            temperature=0
        )
        text = response.choices[0].message.content.strip()
        if text == "无" or not text:
            return []
        lines = [l.strip() for l in text.split("\n") if l.strip() and l.strip() != "无"]
        return lines[:2]
    except Exception:
        return []
