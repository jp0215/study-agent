import re

# 需要过滤的危险词（防止模型输出有害内容）
BLOCKED_KEYWORDS = ["作弊", "答案直接抄", "代写作业"]

# 检查输出是否包含乱码或明显错误
def validate_output(text: str) -> tuple[bool, str]:
    if not text or len(text.strip()) < 5:
        return False, "回答内容为空，请重试"
    
    # 检查是否含有违禁词
    for kw in BLOCKED_KEYWORDS:
        if kw in text:
            return False, "内容包含不当信息，已过滤"
    
    # 检查是否有大量乱码（非中文非英文非数字符号超过50%）
    valid_chars = re.findall(r'[\u4e00-\u9fff\w\s\+\-\=\*\/\^\(\)\[\]\{\}\.,，。、：:；;！!？?\n]', text)
    if len(valid_chars) / max(len(text), 1) < 0.5:
        return False, "模型输出格式异常，请重试"
    
    return True, text


def clean_output(text: str) -> str:
    # 移除多余空行（超过2个连续换行压缩为2个）
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
