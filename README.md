# 📚 学科学习辅助 Agent

> 第九届全国青少年人工智能创新挑战赛 · AI 智能体开发专项赛参赛作品
>
> 一个面向高中生的多 Agent 学习助手，内置 5 节点工作流、10 个专项 Agent，支持智能解题、知识讲解、出题练习、错题本、使用统计等功能。

---

## 🚀 快速启动（3步跑起来）

### 第一步：安装依赖

需要 Python 3.10 或以上版本。

```bash
cd study-agent
pip3 install -r requirements.txt
```

### 第二步：启动服务

```bash
python3 main.py
```

看到以下输出说明启动成功：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 第三步：打开浏览器

访问 **http://localhost:8000**，即可开始使用。

> API Key 已内置，无需任何配置，下载即用。

---

## 📱 让其他人访问

同一 WiFi 下，查看本机 IP：

```bash
ipconfig getifaddr en0   # macOS
```

其他人在浏览器访问 `http://你的IP:8000` 即可使用。

---

## ✨ 功能介绍

| 功能 | 说明 |
|------|------|
| 🔢 **智能解题** | 输入题目 → 分步解析 + 考点提炼 + Python 自动验算答案 |
| 📖 **知识讲解** | 讲解概念原理，附生活例子、关联知识点、跨学科联系 |
| ✏️ **出题练习** | 根据知识点生成由易到难的变式练习题 + 解析 |
| � **追问建议** | 每次回答后自动生成 3 个延伸问题按钮，引导深入学习 |
| �📓 **错题本** | 解题后一键保存难题，按学科筛选，标记已复习 |
| 📊 **使用统计** | 自动记录所有对话，展示学科分布、难度分布、每日趋势 |
| 🔌 **硬件接口** | 提供 `/api/ask` 轻量接口，可供树莓派/智能音箱等设备调用 |

---

## 🧠 工作流详解

每次用户发送一条消息，系统按照以下 5 个节点依次执行：

```
用户输入
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 节点1：并行分析（3个 Agent 同时运行）                      │
│                                                          │
│   意图识别 Agent    学科检测 Agent    难度评估 Agent       │
│   → solver /       → math/physics/  → basic/            │
│     knowledge /      chemistry/...    intermediate/      │
│     quiz                              advanced           │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 节点2：路由 + 难度自适应                                   │
│                                                          │
│  intent=solver    → 解题 Agent                           │
│  intent=knowledge → 知识讲解 Agent                       │
│  intent=quiz      → 出题 Agent                          │
│                                                          │
│  难度会附加到提示词，基础题用简洁语言，竞赛题深入讲解        │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 节点3：输出校验（防幻觉）                                  │
│                                                          │
│  • 检查内容是否为空                                       │
│  • 过滤违禁词（"作弊"、"代写作业"等）                      │
│  • 检测乱码（有效字符占比 < 50% 则拦截）                   │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 节点4：并行后处理（最多4个 Agent 同时运行）                 │
│                                                          │
│  所有模式：                                               │
│    追问建议 Agent    → 生成3个延伸问题按钮                 │
│    跨学科联系 Agent  → 找跨学科知识点关联                  │
│                                                          │
│  仅解题模式额外执行：                                      │
│    知识点提炼 Agent  → 提取考点 + 关键方法                 │
│    计算验证 Agent    → Python 实际执行数学表达式验算        │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 节点5：记录日志 + 更新会话记忆                             │
│                                                          │
│  • 写入 logs/usage.jsonl（用于使用统计）                  │
│  • 保存最近5轮对话上下文，支持追问                         │
└─────────────────────────────────────────────────────────┘
    │
    ▼
返回给前端展示：回答 + 学科/难度标签 + 考点卡片
             + Python验算结果 + 跨学科联系 + 追问按钮
```

---

## 🤖 10个 Agent 说明

### 节点1 — 并行分析

| Agent | 文件 | 作用 |
|-------|------|------|
| 意图识别 Agent | `backend/agents/intent.py` | 判断用户想解题(solver)、学知识(knowledge)还是练习(quiz) |
| 学科检测 Agent | `backend/agents/subject_detector.py` | 识别数学/物理/化学/生物/语文/英语/历史/地理 |
| 难度评估 Agent | `backend/agents/difficulty.py` | 判断题目难度：基础🟢 / 提高🟡 / 竞赛🔴 |

### 节点2 — 专项回答

| Agent | 文件 | 提示词设计要点 |
|-------|------|--------------|
| 解题 Agent | `backend/agents/solver.py` | 知识点分析→解题思路→分步过程→答案总结，携带对话历史 |
| 知识讲解 Agent | `backend/agents/knowledge.py` | 核心定义→生活类比→题型应用→关联知识点 |
| 出题 Agent | `backend/agents/quiz.py` | 2-3道题，由易到难，题型多样，每题附解析 |

### 节点4 — 后处理

| Agent | 文件 | 作用 |
|-------|------|------|
| 知识点提炼 Agent | `backend/agents/summarizer.py` | 从解题过程提取考点和方法，展示为蓝色标签卡片 |
| 计算验证 Agent | `backend/agents/calculator.py` | 让LLM提取数学表达式，Python安全执行并验算，防止算错 |
| 追问建议 Agent | `backend/agents/followup.py` | 生成3个延伸问题，梯度设计（巩固→拓展→应用） |
| 跨学科联系 Agent | `backend/agents/cross_subject.py` | 发现题目涉及的其他学科知识点 |

---

## 📁 代码结构

```
study-agent/
│
├── main.py                        # 主入口，工作流5个节点全在这里编排
│                                  # 修改工作流逻辑看这个文件
│
├── requirements.txt               # Python 依赖（仅4个包）
│
├── frontend/
│   ├── index.html                 # 主对话界面
│   │                              # Markdown渲染 + KaTeX数学公式 + 代码高亮
│   │                              # 学科/难度标签 + 知识点卡片 + 追问按钮
│   │                              # 错题本保存按钮 + 移动端适配
│   ├── mistakes.html              # 错题本页面（筛选/标记已复习）
│   └── stats.html                 # 使用统计页面（柱状图/每日趋势）
│
└── backend/
    ├── config.py                  # API Key 和模型配置
    ├── validator.py               # 输出校验：空值/违禁词/乱码三重检测
    ├── logger.py                  # 日志读写：每次对话自动记录
    ├── mistake_book.py            # 错题本数据的增删查改
    └── agents/                    # 10个 Agent，每个文件独立
        ├── intent.py
        ├── subject_detector.py
        ├── difficulty.py
        ├── solver.py
        ├── knowledge.py
        ├── quiz.py
        ├── summarizer.py
        ├── calculator.py
        ├── followup.py
        └── cross_subject.py
```

---

## 🌐 页面路由

| 地址 | 内容 |
|------|------|
| `http://localhost:8000/` | 主对话界面 |
| `http://localhost:8000/mistakes-page` | 错题本 |
| `http://localhost:8000/stats-page` | 使用统计 |
| `http://localhost:8000/docs` | API 文档（FastAPI 自动生成） |

---

## � 常见问题

**Q: `pip3` 报错找不到命令**
```bash
pip install -r requirements.txt   # 去掉3
```

**Q: `ModuleNotFoundError`**

确保在 `study-agent/` 目录下运行：
```bash
cd study-agent
python3 main.py
```

**Q: 端口被占用**

修改 `main.py` 最后一行：
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)  # 改8001
```
然后访问 `http://localhost:8001`

**Q: 关闭终端后服务停止**
```bash
nohup python3 main.py > app.log 2>&1 &
# 停止服务
kill $(lsof -ti:8000)
```
