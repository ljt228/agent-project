# 项目整体技术架构（Architecture）

> 仓库：`ljt228/agent-project`  
> 说明：本文用于帮助快速理解项目的模块划分、数据流与关键依赖。  
> 入口程序：`main.py`

---

## 1. 项目目标与核心能力

该项目是一个命令行（CLI）形式的“智能天气助手”，核心能力包括：

1. **对话式交互**：用户在终端连续输入问题，助手持续回复，并维护会话历史（chat history）。
2. **意图路由**：将用户问题粗粒度分成两类：
   - 天气类问题 → 走“天气专家智能体”
   - 非天气类问题 → 走“搜索专家智能体”
3. **工具增强（Tools）**：
   - 天气工具：调用和风天气 API 获取实时天气
   - 搜索工具：调用 SerpAPI 进行网络搜索

---

## 2. 总体架构图（模块视角）

```text
+-------------------+
|      main.py       |  CLI 入口：读取输入、打印输出、维护chat_history
+----------+--------+
           |
           v
+-------------------+
|     agent.py       |  WeatherAgent：LLM初始化 + 意图路由 + 调用子Agent
+----+----------+---+
     |          |
     | weather  | search
     v          v
+---------+   +---------+
|agents.py|   |agents.py|  create_weather_agent / create_search_agent
+----+----+   +----+----+
     |             |
     v             v
+---------+   +---------+
|tools.py |   |tools.py |  WeatherQueryTool / SearchTool
+----+----+   +----+----+
     |             |
     v             v
 QWeather API    SerpAPI
```

---

## 3. 关键数据流（一次用户查询如何被处理）

以用户在终端输入一句话为例，整体流程如下：

### Step 1：CLI 读取输入并维护上下文（`main.py`）
- 循环读取 `user_input`
- 调用 `WeatherAgent.process_query(user_input, chat_history)`
- 将本轮 user/assistant 消息追加到 `chat_history` 列表

特点：
- `chat_history` 在 `main.py` 自己维护，是一个 list（元素形如 `{"role": "...", "content": "..."}`）

### Step 2：意图路由与执行（`agent.py` -> `WeatherAgent`）
`WeatherAgent` 负责：
1. 初始化 LLM（`ChatOpenAI`）
2. 构建两个子 agent：
   - `self.weather_agent = create_weather_agent(self.llm)`
   - `self.search_agent = create_search_agent(self.llm)`
3. 对 query 做路由（`route_query`）：
   - 如果包含关键字：`["天气", "温度", "下雨", "晴天", "预报", "气候"]` → weather
   - 否则 → search
4. 调用对应 agent 的 `invoke()`：
   - 传入参数结构：
     - `input`: 用户问题
     - `chat_history`: 历史对话（如果为空则用 `[]`）
5. 返回 `result["output"]` 给 `main.py` 展示

### Step 3：LangChain Agent + Tool 执行（`agents.py` + `tools.py`）
- `agents.py` 使用 `initialize_agent(..., agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, memory=...)` 初始化智能体
- 每个智能体都配置：
  - tools：天气 agent 绑定 `WeatherQueryTool()`；搜索 agent 绑定 `SearchTool()`
  - memory：来自 `memory.py` 的 `ConversationBufferMemory`

当 LLM 决定调用工具时：
- 天气工具 `WeatherQueryTool._run(city)`：
  - 先查缓存（默认 300 秒过期）
  - 调用和风天气“实时天气”接口
  - 解析返回并拼接自然语言结果
- 搜索工具 `SearchTool._run(query)`：
  - 读取环境变量 `SERPAPI_API_KEY`
  - 调用 SerpAPI（GoogleSearch）获取搜索摘要并拼接返回

---

## 4. 代码结构与职责划分（按文件）

### 4.1 `main.py`（应用入口层）
职责：
- CLI UI（打印欢迎语/提示语）
- 读取用户输入与退出逻辑
- 调用 `WeatherAgent`
- 维护 `chat_history`（应用层状态）

### 4.2 `agent.py`（编排层 / Orchestrator）
职责：
- 初始化 LLM 客户端（`ChatOpenAI`）
- 初始化两个子智能体（weather/search）
- `route_query()`：基于关键字的简单路由策略
- `process_query()`：统一入口，屏蔽底层 agent/tool 细节

### 4.3 `agents.py`（智能体工厂层 / Agent Factory）
职责：
- `create_weather_agent(llm)`：构建“天气专家智能体”（tools=WeatherQueryTool）
- `create_search_agent(llm)`：构建“搜索专家智能体”（tools=SearchTool）
- 为每个 agent 注入 memory

### 4.4 `tools.py`（工具层 / Tools）
职责：
- 定义 Pydantic 入参 schema（`WeatherQueryInput`, `SearchInput`）
- 定义 LangChain `BaseTool`：
  - `WeatherQueryTool`：调用天气 API + 缓存
  - `SearchTool`：调用 SerpAPI

### 4.5 `memory.py`（记忆层 / Memory）
职责：
- 创建 `ConversationBufferMemory`，用于对话上下文存储与回放

---

## 5. 依赖与外部服务

### Python 侧关键依赖（从代码可见）
- `python-dotenv`：加载 `.env`
- `langchain_openai`：`ChatOpenAI`
- `langchain_classic`：agent/memory（注意：这是一个非主流命名空间，版本兼容需要关注）
- `requests`：HTTP 调用天气 API
- `serpapi`：SearchTool 的搜索能力

### 外部服务
- 天气：和风天气 API（实时天气接口）
- 搜索：SerpAPI（GoogleSearch）
- LLM：通过 `base_url` 指向的 OpenAI 兼容接口服务（你当前代码里使用了自定义 `base_url`）

---

## 6. 配置与密钥管理（建议）

当前代码里存在“密钥硬编码”的情况（应尽快整改）：

- LLM `api_key`（位于 `agent.py`）
- 和风天气 `api_key`（位于 `tools.py`）

建议统一改为：
- 使用 `.env` / 环境变量注入：
  - `AIHUBMIX_API_KEY`（或你实际使用的 key 名）
  - `QWEATHER_API_KEY`
  - `QWEATHER_API_HOST`
  - `SERPAPI_API_KEY`

并在 README 或本架构文档中提供示例：

```bash
# .env 示例（不要提交到仓库）
SERPAPI_API_KEY=xxxx
QWEATHER_API_KEY=xxxx
QWEATHER_API_HOST=xxxx
AIHUBMIX_API_KEY=xxxx
```

---

## 7. 可扩展点（后续演进建议）

1. **路由升级**：当前 `route_query()` 是关键字规则，后续可替换成：
   - LLM Router / 分类器
   - 多智能体路由（城市、时间范围、预警、空气质量等更细粒度）
2. **工具增强**：
   - 天气：支持 7 天预报、逐小时预报、空气质量、生活指数等
   - 搜索：结果结构化（标题/链接/摘要）、引用来源
3. **统一的会话历史**：
   - 目前 `main.py` 自己维护 `chat_history`，而 `agents.py` 又创建了 `ConversationBufferMemory`
   - 可考虑统一一个“会话状态管理”，避免双份上下文来源导致不一致
4. **工程化**：
   - 增加 `docs/` 索引（比如 `docs/README.md`）
   - 增加测试（mock 外部 API）
   - CI（lint/format/type-check）

---

## 8. 快速阅读路线（推荐）

如果你第一次看这个项目，建议按以下顺序阅读：

1. `main.py`：先理解入口与交互方式
2. `agent.py`：理解路由与编排
3. `agents.py`：理解两个子 agent 如何被构建
4. `tools.py`：理解工具如何访问外部 API
5. `memory.py`：理解对话记忆的配置
