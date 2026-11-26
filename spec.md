# SDD 规范校验 MCP Server

## 用户需求

- REQ-001：提供 `generate_spec(project_name, description)`，返回包含用户需求、验收标准、约束条件的 spec.md 内容。
- REQ-002：提供 `validate_spec(spec_content)`，报告缺失章节、空章节和结构校验结果。
- REQ-003：提供 `generate_task_list(spec_content)`，将有效规格转换为可追踪的 tasks.md 清单。
- REQ-004：三个工具均通过 Pydantic 定义扁平 inputSchema，说明何时调用；结果使用结构化输出。
- REQ-005：提供 requirements.txt、README.md 和供 Cursor 使用的 mcp.json 示例。
- REQ-006：先完成本地 Git 首次提交，再创建 GitHub 空仓库并推送 main；首次推送后补充 README 使用方式并再次提交推送。

## 验收标准

- AC-001：使用 MCP stdio 客户端完成 initialize、tools/list 和三个 tools/call；工具名称、必填字段、字段说明与 Pydantic 模型一致。
- AC-002：生成的 spec 可通过结构校验，包含 REQ/AC 编号并标明需要人工确认；输出不捏造领域约束。
- AC-003：缺失、空白、纯 TODO/TBD、中文/英文标题、代码块伪标题、HTML 注释伪标题均有测试。
- AC-004：无效规格不会生成任务；有效规格的每条需求对应实现任务，每条验收标准对应验证任务，并包含四阶段关口。
- AC-005：空字符串、超长输入、额外字段和错误类型被拒绝；正常中文和多行描述可用。
- AC-006：Python 3.10+；直接依赖只包含 mcp、fastmcp、pydantic；服务仅使用 stdio，无网络请求、文件写入、命令执行或浏览器控制。
- AC-007：README 说明安装、工具参数、校验范围及 SDD 流程；发布后的使用方式包含 mcp.json 配置与 Cursor 接入步骤。
- AC-008：远程 main 与本地 HEAD 一致，工作区干净；若外部授权受阻，明确记录实际完成状态。

## 约束条件

- CON-001：指定 → 计划 → 任务 → 实现；本文件先于实现创建，plan.md 和 tasks.md 紧随其后。
- CON-002：生成使用确定性模板，不调用 LLM；自然语言描述由调用方提供，业务验收标准需要用户审阅。
- CON-003：校验仅覆盖 Markdown 结构与非空正文，不宣称证明业务正确性、实现符合性或人工批准。
- CON-004：工具仅返回文本和 JSON 数据，调用方负责保存 spec.md/tasks.md；浏览器由独立 Playwright MCP 等工具处理。
- CON-005：只支持 Markdown ATX 标题（# 至 ######），接受文档中说明的中英文别名；不作为完整 Markdown 解析器。
- CON-006：不添加密钥、浏览器会话或本机配置到仓库；mcp.json 使用可替换的绝对路径。
