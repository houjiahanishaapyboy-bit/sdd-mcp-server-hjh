# 计划

1. 定义 Pydantic 输入/输出模型；通过公开 FunctionTool API 将 model_json_schema 作为 inputSchema，保持顶层参数形式。
2. 使用 FastMCP 注册三个只读、幂等工具；显式说明调用时机，启动入口限定 stdio。
3. 用标准库解析 ATX 章节，忽略围栏代码与 HTML 注释；区分缺失与空内容，支持中英文别名。
4. 根据项目描述生成带 REQ/AC 编号的规格初稿；从有效规格逐项生成实现和验收任务，保留来源引用。
5. 编写 unittest 单元测试，以及通过真实子进程 stdio 的 MCP 协议集成测试。
6. 校验配置 JSON、Python 3.10 语法和依赖范围；完成 Git 首次提交。
7. 使用已登录的 GitHub 页面创建不含初始文件的仓库，添加 origin 并推送 main。
8. 首次推送后为 README 增加使用方式和 Cursor 配置，提交并推送；核对远程提交。

设计选择：无需数据库、HTTP 服务、LLM 或浏览器依赖。结构校验是进入任务生成的关口；人工审阅及开发执行由客户端工作流负责。
