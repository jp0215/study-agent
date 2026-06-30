from openai import OpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

SUBJECT_PROMPT = """判断用户输入涉及的高中学科，只返回以下之一：
math（数学）、physics（物理）、chemistry（化学）、biology（生物）、
chinese（语文）、english（英语）、history（历史）、geography（地理）、general（通用/不明确）

只返回一个英文单词，不要任何解释。"""

SUBJECT_LABELS = {
    "math": "📐 数学",
    "physics": "⚗️ 物理",
    "chemistry": "🧪 化学",
    "biology": "🧬 生物",
    "chinese": "📖 语文",
    "english": "🌐 英语",
    "history": "🏛️ 历史",
    "geography": "🌍 地理",
    "general": "📚 通用",
}

VALID_SUBJECTS = set(SUBJECT_LABELS.keys())


def detect_subject(user_input: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SUBJECT_PROMPT},
            {"role": "user", "content": user_input}
        ],
        max_tokens=10,
        temperature=0
    )
    subject = response.choices[0].message.content.strip().lower()
    return subject if subject in VALID_SUBJECTS else "general"


def get_subject_label(subject: str) -> str:
    return SUBJECT_LABELS.get(subject, "📚 通用")
