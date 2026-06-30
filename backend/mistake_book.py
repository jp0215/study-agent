import os
import json
import datetime

MISTAKES_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "mistakes.jsonl")


def _ensure_dir():
    os.makedirs(os.path.dirname(MISTAKES_FILE), exist_ok=True)


def save_mistake(session_id: str, subject: str, question: str, solution: str, knowledge_points: list):
    """保存错题记录"""
    _ensure_dir()
    record = {
        "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "_" + session_id[-6:],
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": session_id,
        "subject": subject,
        "question": question[:200],
        "solution": solution[:500],
        "knowledge_points": knowledge_points,
        "reviewed": False,
    }
    with open(MISTAKES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record["id"]


def get_mistakes(session_id: str = None) -> list:
    """获取错题列表"""
    _ensure_dir()
    if not os.path.exists(MISTAKES_FILE):
        return []
    records = []
    with open(MISTAKES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    if session_id is None or r.get("session_id") == session_id:
                        records.append(r)
                except Exception:
                    pass
    return records


def mark_reviewed(mistake_id: str):
    """标记错题为已复习"""
    if not os.path.exists(MISTAKES_FILE):
        return
    records = []
    with open(MISTAKES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    if r.get("id") == mistake_id:
                        r["reviewed"] = True
                    records.append(r)
                except Exception:
                    pass
    with open(MISTAKES_FILE, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
