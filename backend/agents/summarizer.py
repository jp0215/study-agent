from openai import OpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

SUMMARY_PROMPT = """你是一位高中学科老师。根据以下解题过程，提炼出：
1. 本题考查的核心知识点（2-4个，用・分隔）
2. 解题用到的关键方法/公式（1-2条）
格式如下（严格按此格式，不要其他内容）：
考点：知识点1・知识点2・知识点3
方法：关键方法或公式"""

def summarize_knowledge_points(problem: str, solution: str) -> dict:
    """从解题过程中提炼知识点和方法"""
    content = f"题目：{problem}\n\n解题过程：{solution}"
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": content}
        ],
        max_tokens=150,
        temperature=0
    )
    text = response.choices[0].message.content.strip()
    result = {"points": [], "method": ""}
    for line in text.split("\n"):
        if line.startswith("考点："):
            result["points"] = [p.strip() for p in line[3:].split("・") if p.strip()]
        elif line.startswith("方法："):
            result["method"] = line[3:].strip()
    return result
