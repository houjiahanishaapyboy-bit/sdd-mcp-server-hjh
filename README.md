# SDD Workflow MCP

一个遵循「指定 → 计划 → 任务 → 实现」的 SDD（Spec-Driven Development）规范辅助服务。使用 FastMCP、Pydantic 和 MCP stdio，生成规格初稿、检查必需章节并创建可追踪的任务清单。

## 项目约定

1. **指定**：用 `generate_spec` 生成 spec.md 初稿，人工确认用户需求、验收标准和约束。
2. **计划**：先用 `validate_spec` 检查结构，再由开发者或 AI 客户端编写并审阅 plan.md。
3. **任务**：调用 `generate_task_list`，人工补充依赖、负责人及完成定义，保存为 tasks.md。
4. **实现**：逐项实施、记录验证证据，更新规格与任务状态后提交代码。

本仓库自身的阶段产物见 [spec.md](spec.md)、[plan.md](plan.md)、[tasks.md](tasks.md)。服务不会自动批准计划、执行任务或证明业务正确性。

## 安装

需要 Python 3.10+。推荐在虚拟环境中安装；直接依赖仅有 `fastmcp`、`mcp`、`pydantic`，版本固定于 requirements.txt，安装时会自动解析它们的传递依赖。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe server.py
```

macOS/Linux 使用 `.venv/bin/python`。启动后进程等待 MCP stdio 客户端连接；这是协议服务，不是 HTTP 网页。不要在 stdout 添加调试输出。

## 工具接口

所有 inputSchema 均来自 Pydantic 模型，参数位于顶层，不需要嵌套 `request`。模型拒绝额外参数、错误类型、空白和超长输入。description 明确写有「何时调用」。成功结果为 MCP 结构化输出，`spec_content` / `tasks_content` 由客户端保存为文件。

| Tool | 何时调用 | 参数 | 主要返回字段 |
| --- | --- | --- | --- |
| `generate_spec` | 项目启动，需求澄清后 | `project_name`、`description` | `spec_content`、`needs_review`、`notes` |
| `validate_spec` | 规格新建或修改后，计划与任务拆分前 | `spec_content` | `valid`、`missing_fields`、`empty_fields`、`warnings` |
| `generate_task_list` | 规格结构通过且计划已审阅后 | `spec_content` | `tasks_content`、`requirement_count`、`acceptance_count`、`needs_review` |

生成规格的调用参数示例：

```json
{
  "project_name": "团队待办",
  "description": "用户可以创建待办\n用户可以将待办标记为完成"
}
```

项目名限单行 1–120 字符；描述限 20000 字符、100 个非空行，每个非空行对应一条需求。规格内容限 200000 字符。生成使用确定性模板，不依赖 LLM、API Key 或网络；业务验收案例仍需人工细化。无效规格调用任务生成会返回 MCP 工具错误。

## 校验范围

必需字段必须是 Markdown ATX 标题（`#` 至 `######`）及其非空正文。支持以下标题，英文不区分大小写，也允许 `## 1. 用户需求` 这样的编号：

| 字段 | 支持标题 |
| --- | --- |
| 用户需求 | 用户需求、需求、功能需求、Requirements、User Requirements |
| 验收标准 | 验收标准、Acceptance Criteria |
| 约束条件 | 约束条件、约束、Constraints |

正文中提及「需求」不会充当标题；围栏代码和 HTML 注释中的标题被忽略。只有标题、空白或纯 TODO/TBD/待补充等占位符会判为空。混合的真实内容与占位内容返回提醒；任务生成保留真实内容并提示待补充项。

这是受限的结构检查器，不支持 Setext 标题、YAML 字段或完整 Markdown 语法校验，也不判断需求是否清晰、验收是否充分、代码是否满足需求。人工确认是流程约定，不是服务可验证的审批记录。

## 验证

```powershell
python -m unittest discover -s tests -v
```

测试使用标准库 unittest，覆盖结构校验、参数约束和真实 stdio 子进程中的 MCP initialize、tools/list、tools/call。Python 3.10 语法兼容性与实际运行环境分别核验。

## 文件

- `server.py`：三个只读 MCP 工具与 stdio 启动入口。
- `requirements.txt`：直接依赖及固定版本。
- `mcp.json`：Cursor 配置示例，需替换为实际绝对路径。
- `spec.md`、`plan.md`、`tasks.md`：本项目的 SDD 阶段产物。
- `tests/`：单元测试与 MCP 协议集成测试。

浏览器操作由独立 Playwright MCP 等服务承担，本服务不包含浏览器控制逻辑。
