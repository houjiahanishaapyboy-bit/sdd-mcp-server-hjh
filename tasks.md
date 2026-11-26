# 任务清单

## 指定
- [x] T-001 明确 REQ-001 至 REQ-006、AC-001 至 AC-008 与实现边界（spec.md）。

## 计划
- [x] T-002 确定 Pydantic schema、Markdown 校验和 stdio 测试方案（plan.md）。

## 任务
- [x] T-003 建立本清单与需求、验收标准的追踪关系。

## 实现
- [x] T-004 实现三个工具、输入模型及结构化输出（REQ-001 至 REQ-004）。
- [x] T-005 编写依赖、初始 README 和 mcp.json 示例（REQ-005）。
- [x] T-006 运行结构校验、边界输入与 stdio 集成测试（AC-001 至 AC-006）。
- [ ] T-007 完成本地 git init、add、commit（REQ-006）。
- [ ] T-008 创建 GitHub 空仓库，配置 origin，推送 main（REQ-006）。
- [ ] T-009 首次推送后补充 README 使用方式，提交并再次推送（AC-007）。
- [ ] T-010 核对远程 main、工作区及最终交付物（AC-008）。

## 验证记录

- 2026-11-26：Python 3.11.2 运行 19 项 unittest（含真实 stdio MCP 会话），全部通过。
- 干净虚拟环境安装 requirements.txt 后重复运行全部测试通过，pip check 无依赖冲突。
- server.py 与测试文件通过 Python 3.10 AST 语法检查；三个直接依赖声明支持 Python 3.10+，未在 Python 3.10 解释器上实际运行。
- 本项目 spec.md 通过 validate_spec，缺失和空章节均为零。
