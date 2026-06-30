import os
import json
import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "usage.jsonl")


def _ensure_log_dir():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log_request(session_id: str, subject: str, intent: str, difficulty: str, question: str):
    """每次对话请求写一条日志"""
    _ensure_log_dir()
    record = {
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": session_id,
        "subject": subject,
        "intent": intent,
        "difficulty": difficulty,
        "question": question[:80],  # 只记录前80字
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def get_stats() -> dict:
    """读取日志，返回统计数据"""
    _ensure_log_dir()
    if not os.path.exists(LOG_FILE):
        return {"total": 0, "sessions": 0, "subjects": {}, "intents": {}, "difficulties": {}, "daily": {}}

    records = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    sessions = set()
    subjects = {}
    intents = {}
    difficulties = {}
    daily = {}

    for r in records:
        sessions.add(r.get("session_id", ""))
        s = r.get("subject", "general")
        subjects[s] = subjects.get(s, 0) + 1
        i = r.get("intent", "knowledge")
        intents[i] = intents.get(i, 0) + 1
        d = r.get("difficulty", "basic")
        difficulties[d] = difficulties.get(d, 0) + 1
        day = r.get("time", "")[:10]
        daily[day] = daily.get(day, 0) + 1

    return {
        "total": len(records),
        "sessions": len(sessions),
        "subjects": subjects,
        "intents": intents,
        "difficulties": difficulties,
        "daily": dict(sorted(daily.items())[-14:]),  # 最近14天
    }
