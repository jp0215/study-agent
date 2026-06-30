"""
计算验证工具：
1. 让 LLM 从解题过程中提取可验证的数值计算式
2. 用 Python 安全执行计算，与 LLM 给出的答案对比
3. 返回验证结果
"""
import re
import math
import ast
from openai import OpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

EXTRACT_PROMPT = """从以下解题过程中，提取最终数值答案对应的 Python 计算表达式。
要求：
- 只输出一个可以被 Python eval() 执行的表达式，如：2**2 - 2*2 + 3
- 如果答案是纯数字（如 x=5），直接输出该数字：5
- 如果无法提取数值计算（如答案是文字描述、方程组、证明题等），输出：SKIP
- 不要输出任何解释，只输出表达式或 SKIP"""

# 安全的数学函数白名单
SAFE_GLOBALS = {
    "__builtins__": {},
    "abs": abs, "round": round, "max": max, "min": min,
    "sqrt": math.sqrt, "pow": math.pow, "log": math.log,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "pi": math.pi, "e": math.e,
}


def safe_eval(expr: str):
    """安全执行数学表达式，防止代码注入"""
    # 只允许数字、运算符、空格、括号、小数点
    if not re.match(r'^[\d\s\+\-\*\/\(\)\.\^%sqrtlogsincotan,piea_]+$', expr, re.IGNORECASE):
        return None, "表达式含有不合法字符"
    try:
        result = eval(expr, SAFE_GLOBALS)
        return round(float(result), 6), None
    except Exception as ex:
        return None, str(ex)


def extract_calc_expr(problem: str, solution: str) -> str:
    """让 LLM 提取最终计算表达式"""
    content = f"题目：{problem}\n\n解题过程（最后几行）：\n{solution[-400:]}"
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": EXTRACT_PROMPT},
                {"role": "user", "content": content}
            ],
            max_tokens=60,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "SKIP"


def verify_answer(problem: str, solution: str) -> dict:
    """
    主入口：验证解题答案
    返回：{verified: bool, result: float|None, expr: str, message: str, status: 'ok'|'warn'|'skip'}
    """
    expr = extract_calc_expr(problem, solution)

    if expr == "SKIP" or not expr:
        return {"status": "skip", "message": "此题为非数值型，跳过自动验算", "expr": "", "result": None}

    value, error = safe_eval(expr)

    if error:
        return {"status": "skip", "message": f"表达式无法执行：{error}", "expr": expr, "result": None}

    return {
        "status": "ok",
        "message": f"Python 自动验算结果：{value}",
        "expr": expr,
        "result": value,
    }
