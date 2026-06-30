from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import sys
import os
import traceback
import concurrent.futures

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.intent import identify_intent
from backend.agents.subject_detector import detect_subject, get_subject_label
from backend.agents.difficulty import assess_difficulty, get_difficulty_label
from backend.agents.solver import solve_problem
from backend.agents.knowledge import explain_knowledge
from backend.agents.quiz import generate_quiz
from backend.agents.summarizer import summarize_knowledge_points
from backend.agents.followup import generate_followups
from backend.agents.cross_subject import find_cross_subject
from backend.agents.calculator import verify_answer
from backend.validator import validate_output, clean_output
from backend.logger import log_request, get_stats
from backend.mistake_book import save_mistake, get_mistakes, mark_reviewed

app = FastAPI(title="学科学习辅助 Agent")
app.mount("/static", StaticFiles(directory="frontend"), name="static")

sessions: dict = {}


# ── 数据模型 ────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    intent: str
    subject: str
    subject_label: str
    difficulty: str
    difficulty_label: str
    knowledge_points: list
    method: str
    followups: list
    cross_subjects: list
    verify: dict
    session_id: str

class HardwareAskRequest(BaseModel):
    question: str
    session_id: Optional[str] = "hw_default"

class MistakeRequest(BaseModel):
    session_id: str
    question: str
    solution: str
    subject: str
    knowledge_points: list

class ReviewRequest(BaseModel):
    mistake_id: str


# ── 页面路由 ────────────────────────────────────────────
@app.get("/")
def index():
    return FileResponse("frontend/index.html")

@app.get("/stats-page")
def stats_page():
    return FileResponse("frontend/stats.html")

@app.get("/mistakes-page")
def mistakes_page():
    return FileResponse("frontend/mistakes.html")


# ── 主对话接口 ──────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id
    user_msg = req.message.strip()

    if not user_msg:
        return ChatResponse(
            reply="请输入内容", intent="unknown",
            subject="general", subject_label="📚 通用",
            difficulty="basic", difficulty_label="🟢 基础",
            knowledge_points=[], method="", followups=[], cross_subjects=[],
            verify={"status": "skip"},
            session_id=session_id
        )

    history = sessions.get(session_id, [])

    try:
        # ══════════════════════════════════════════
        # 工作流节点1：并行分析（意图 + 学科 + 难度）
        # ══════════════════════════════════════════
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            f_intent     = executor.submit(identify_intent, user_msg)
            f_subject    = executor.submit(detect_subject, user_msg)
            f_difficulty = executor.submit(assess_difficulty, user_msg)
            intent     = f_intent.result()
            subject    = f_subject.result()
            difficulty = f_difficulty.result()

        subject_label    = get_subject_label(subject)
        difficulty_label = get_difficulty_label(difficulty)

        # ══════════════════════════════════════════
        # 工作流节点2：路由 + 难度自适应
        # ══════════════════════════════════════════
        depth_hint = {
            "basic":        "请用基础、简洁的语言讲解，适合高中入门学生。",
            "intermediate": "请适当深入，涉及综合应用和技巧。",
            "advanced":     "请深入讲解，可涉及竞赛技巧和拓展内容。",
        }.get(difficulty, "")
        enhanced_msg = f"{user_msg}\n\n[难度要求：{depth_hint}]"

        if intent == "solver":
            raw_reply = solve_problem(enhanced_msg, history)
        elif intent == "quiz":
            raw_reply = generate_quiz(enhanced_msg, history)
        else:
            raw_reply = explain_knowledge(enhanced_msg, history)

        # ══════════════════════════════════════════
        # 工作流节点3：输出校验（防幻觉）
        # ══════════════════════════════════════════
        is_valid, result = validate_output(raw_reply)
        reply = clean_output(result) if is_valid else result

        # ══════════════════════════════════════════
        # 工作流节点4：并行后处理
        # 知识点提炼 + 追问建议 + 跨学科联系
        # ══════════════════════════════════════════
        knowledge_points = []
        method = ""
        cross_subjects = []
        verify_result = {"status": "skip"}

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            f_followup = executor.submit(generate_followups, user_msg, reply)
            f_cross    = executor.submit(find_cross_subject, user_msg, subject)

            if intent == "solver":
                f_summary = executor.submit(summarize_knowledge_points, user_msg, reply)
                # ══════════════════════════════════════════
                # 工作流节点4b：计算验证 Agent
                # 用 Python 实际执行计算，核验 LLM 给出的数值答案
                # ══════════════════════════════════════════
                f_verify  = executor.submit(verify_answer, user_msg, reply)
                summary = f_summary.result()
                knowledge_points = summary.get("points", [])
                method = summary.get("method", "")
                verify_result = f_verify.result()

            followups      = f_followup.result()
            cross_subjects = f_cross.result()

        # ══════════════════════════════════════════
        # 工作流节点5：记录日志 + 更新会话记忆
        # ══════════════════════════════════════════
        log_request(session_id, subject, intent, difficulty, user_msg)

        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": reply})
        sessions[session_id] = history[-10:]

        return ChatResponse(
            reply=reply, intent=intent,
            subject=subject, subject_label=subject_label,
            verify=verify_result,
            difficulty=difficulty, difficulty_label=difficulty_label,
            knowledge_points=knowledge_points, method=method,
            followups=followups, cross_subjects=cross_subjects,
            session_id=session_id
        )

    except Exception as e:
        traceback.print_exc()
        return ChatResponse(
            reply=f"服务出错：{str(e)}", intent="error",
            subject="general", subject_label="📚 通用",
            difficulty="basic", difficulty_label="🟢 基础",
            knowledge_points=[], method="", followups=[], cross_subjects=[],
            verify={"status": "skip"},
            session_id=session_id
        )


# ══════════════════════════════════════════
# 硬件扩展接口（供树莓派/智能设备调用）
# 入参/出参极简，方便嵌入式设备解析
# ══════════════════════════════════════════
@app.post("/api/ask")
def hardware_ask(req: HardwareAskRequest):
    """轻量级接口，专为硬件/第三方设备设计"""
    user_msg = req.question.strip()
    if not user_msg:
        return {"answer": "请输入问题", "subject": "general", "intent": "unknown"}
    try:
        intent  = identify_intent(user_msg)
        subject = detect_subject(user_msg)
        if intent == "solver":
            reply = solve_problem(user_msg)
        elif intent == "quiz":
            reply = generate_quiz(user_msg)
        else:
            reply = explain_knowledge(user_msg)
        is_valid, result = validate_output(reply)
        answer = clean_output(result) if is_valid else result
        log_request(req.session_id, subject, intent, "basic", user_msg)
        return {"answer": answer, "subject": subject, "intent": intent}
    except Exception as e:
        return {"answer": f"错误：{str(e)}", "subject": "general", "intent": "error"}


# ══════════════════════════════════════════
# 错题本接口
# ══════════════════════════════════════════
@app.post("/mistakes/save")
def save_mistake_api(req: MistakeRequest):
    mid = save_mistake(req.session_id, req.subject, req.question, req.solution, req.knowledge_points)
    return {"status": "ok", "id": mid}

@app.get("/mistakes/list")
def list_mistakes(session_id: str = None):
    return get_mistakes(session_id)

@app.post("/mistakes/review")
def review_mistake(req: ReviewRequest):
    mark_reviewed(req.mistake_id)
    return {"status": "ok"}


# ══════════════════════════════════════════
# 统计数据接口
# ══════════════════════════════════════════
@app.get("/stats")
def stats():
    return get_stats()


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
