from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys
import tempfile
import unittest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import ValidationError

import server


ROOT = Path(__file__).resolve().parents[1]
VALID_SPEC = """# 示例
## 用户需求
- REQ-001：用户可以创建待办
- REQ-002：用户可以完成待办
## 验收标准
- AC-001：输入标题后出现新待办
- AC-002：完成后状态改变
## 约束条件
- CON-001：Python 3.10+
"""


class SpecTests(unittest.TestCase):
    def test_generation_is_deterministic_and_valid(self):
        first = server.generate_spec("团队待办", "创建待办\n完成待办")
        self.assertEqual(first, server.generate_spec("团队待办", "创建待办\n完成待办"))
        self.assertTrue(first.needs_review)
        self.assertTrue(server.validate_spec(first.spec_content).valid)
        self.assertIn("REQ-002", first.spec_content)
        self.assertIn("AC-002", first.spec_content)

    def test_generated_text_cannot_inject_sections(self):
        result = server.generate_spec("# <项目>", "## 约束条件\n<script>alert(1)</script>")
        self.assertNotIn("<script>", result.spec_content)
        self.assertEqual(len(server._items(server._sections(result.spec_content)["用户需求"])), 2)
        self.assertTrue(server.validate_spec(result.spec_content).valid)

    def test_missing_fields(self):
        result = server.validate_spec("## 用户需求\n- 创建待办")
        self.assertFalse(result.valid)
        self.assertEqual(result.missing_fields, ["验收标准", "约束条件"])

    def test_prose_does_not_count_as_headings(self):
        result = server.validate_spec("用户需求、验收标准、约束条件都在这里。")
        self.assertEqual(result.missing_fields, list(server.REQUIRED_FIELDS))

    def test_empty_sections(self):
        result = server.validate_spec("## 用户需求\n## 验收标准\n- [ ] \n## 约束条件\n")
        self.assertFalse(result.valid)
        self.assertEqual(result.empty_fields, list(server.REQUIRED_FIELDS))
        self.assertFalse(result.missing_fields)

    def test_placeholders_are_empty(self):
        result = server.validate_spec("## 需求\n- REQ-001：TODO\n## 验收标准\nTBD\n## 约束\n待补充")
        self.assertEqual(result.empty_fields, list(server.REQUIRED_FIELDS))

    def test_mixed_placeholders_warn_and_do_not_become_tasks(self):
        spec = VALID_SPEC.replace("## 验收标准", "- TODO\n## 验收标准")
        result = server.validate_spec(spec)
        self.assertTrue(result.valid)
        self.assertTrue(result.warnings)
        tasks = server.generate_task_list(spec)
        self.assertEqual(tasks.requirement_count, 2)
        self.assertIn("待处理提醒", tasks.tasks_content)

    def test_english_and_numbered_headings(self):
        spec = "## 1. USER REQUIREMENTS\n- create\n## 2. Acceptance Criteria ##\n- works\n## 3. Constraints\n- offline"
        self.assertTrue(server.validate_spec(spec).valid)

    def test_comments_and_fenced_headings_are_ignored(self):
        for fence in ("```", "~~~~"):
            spec = f"{fence}markdown\n{VALID_SPEC}{fence}\n"
            with self.subTest(fence=fence):
                self.assertFalse(server.validate_spec(spec).valid)
        self.assertFalse(server.validate_spec(f"<!--\n{VALID_SPEC}\n-->").valid)

    def test_wrong_length_fence_does_not_close_code(self):
        spec = "````md\n```\n" + VALID_SPEC + "````"
        self.assertEqual(server.validate_spec(spec).missing_fields, list(server.REQUIRED_FIELDS))

    def test_empty_section_cannot_borrow_unrelated_body(self):
        spec = "## 用户需求\n## 背景\n创建任务\n## 验收标准\n通过\n## 约束\n离线"
        self.assertIn("用户需求", server.validate_spec(spec).empty_fields)

    def test_subsection_body_counts(self):
        spec = VALID_SPEC.replace("- REQ-001", "### 创建\n- REQ-001")
        self.assertTrue(server.validate_spec(spec).valid)

    def test_continuations_do_not_create_spurious_requirements(self):
        spec = VALID_SPEC.replace("- REQ-002：用户可以完成待办", "  并保留记录")
        tasks = server.generate_task_list(spec)
        self.assertEqual(tasks.requirement_count, 1)
        self.assertIn("并保留记录", tasks.tasks_content)

    def test_invalid_spec_blocks_tasks(self):
        with self.assertRaisesRegex(ValueError, "不能生成任务"):
            server.generate_task_list("## 需求\n创建")

    def test_task_traceability(self):
        tasks = server.generate_task_list(VALID_SPEC)
        self.assertEqual(tasks.requirement_count, 2)
        self.assertEqual(tasks.acceptance_count, 2)
        for marker in ("指定", "计划", "任务", "实现", "REQ-001", "REQ-002", "AC-001", "AC-002", "CON-001"):
            self.assertIn(marker, tasks.tasks_content)
        self.assertNotIn("[x]", tasks.tasks_content)

    def test_input_boundaries(self):
        for name, description in (("", "需求"), (" \n ", "需求"), ("x\ny", "需求"), ("x" * 121, "需求"), ("x", "  "), ("x", "d" * 20001), ("x", "d\n" * 101), (1, "需求")):
            with self.subTest(name=str(name)[:20], description=str(description)[:20]):
                with self.assertRaises(ValidationError):
                    server.generate_spec(name, description)
        for content in ("", "  ", "x" * 200001, 42):
            with self.subTest(content=str(content)[:20]):
                with self.assertRaises(ValidationError):
                    server.validate_spec(content)

    def test_models_reject_extra_fields(self):
        with self.assertRaises(ValidationError):
            server.GenerateSpecInput.model_validate({"project_name": "x", "description": "y", "secret": "z"})

    def test_config_is_valid_example(self):
        config = json.loads((ROOT / "mcp.json").read_text(encoding="utf-8"))
        entry = config["mcpServers"]["sdd-workflow"]
        self.assertTrue(entry["command"].endswith("python.exe"))
        self.assertTrue(entry["args"][0].endswith("server.py"))


class StdioTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_mcp_session(self):
        await asyncio.wait_for(self._exercise_session(), timeout=45)

    async def _exercise_session(self):
        parameters = StdioServerParameters(command=sys.executable, args=[str(ROOT / "server.py")])
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as errors:
            async with stdio_client(parameters, errlog=errors) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = (await session.list_tools()).tools
                    models = {
                        "generate_spec": server.GenerateSpecInput,
                        "validate_spec": server.SpecInput,
                        "generate_task_list": server.SpecInput,
                    }
                    self.assertEqual({t.name for t in tools}, set(models))
                    for tool in tools:
                        self.assertEqual(tool.inputSchema, models[tool.name].model_json_schema())
                        self.assertIn("何时调用", tool.description)
                        self.assertFalse(tool.inputSchema["additionalProperties"])
                        self.assertTrue(tool.annotations.readOnlyHint)
                    result = await session.call_tool("generate_spec", {"project_name": "待办", "description": "创建待办"})
                    self.assertFalse(result.isError)
                    content = result.structuredContent["spec_content"]
                    checked = await session.call_tool("validate_spec", {"spec_content": content})
                    self.assertTrue(checked.structuredContent["valid"])
                    tasks = await session.call_tool("generate_task_list", {"spec_content": content})
                    self.assertFalse(tasks.isError)
                    self.assertEqual(tasks.structuredContent["requirement_count"], 1)
                    missing = await session.call_tool("validate_spec", {"spec_content": "## 需求\n创建"})
                    self.assertEqual(missing.structuredContent["missing_fields"], ["验收标准", "约束条件"])
                    for name, arguments in (
                        ("generate_spec", {"project_name": "", "description": "需求"}),
                        ("generate_spec", {"project_name": 42, "description": "需求"}),
                        ("generate_spec", {"project_name": "x", "description": "y", "extra": True}),
                        ("validate_spec", {"spec_content": "  "}),
                        ("generate_task_list", {"spec_content": "不完整"}),
                    ):
                        with self.subTest(name=name, arguments=arguments):
                            response = await session.call_tool(name, arguments)
                            self.assertTrue(response.isError)


if __name__ == "__main__":
    unittest.main()
