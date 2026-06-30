from openai import OpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

DIFFICULTY_PROMPT = """你是一位高中学科专家，判断以下内容的学习难度等级，只返回以下之一：
- basic（基础）：高考必考基础知识、概念理解、简单计算
- intermediate（提高）：综合应用、多知识点结合、中等难度题
- advanced（竞赛/拔高）：竞赛题、高难度推导、超纲内容

只返回一个英文单词，不要任何解释。"""

DIFFICULTY_LABELS = {
    "basic": "🟢 基础",
    "intermediate": "🟡 提高",
    "advanced": "🔴 竞赛",
}


def assess_difficulty(user_input: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": DIFFICULTY_PROMPT},
            {"role": "user", "content": user_input}
        ],
        max_tokens=10,
        temperature=0
    )
    level = response.choices[0].message.content.strip().lower()
    return level if level in DIFFICULTY_LABELS else "basic"


def get_difficulty_label(level: str) -> str:
    return DIFFICULTY_LABELS.get(level, "🟢 基础")
