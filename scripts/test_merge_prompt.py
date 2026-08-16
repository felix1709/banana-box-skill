# -*- coding: utf-8 -*-
"""merge_prompt.py 单元测试。"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merge_prompt


class TestMergePrompt(unittest.TestCase):
    def test_build_prompt_contains_core_sections(self):
        data = {
            "core": {"subject": "少女", "action": "撑伞", "scene": "雨夜车站",
                     "emotion": "孤独", "style": "赛璐璐"},
            "dimensions": {"画面构图": {"text": "低角度仰拍，特写", "refs": []}},
        }
        text = merge_prompt.build_prompt(data)
        self.assertIn("## 主体", text)
        self.assertIn("少女", text)
        self.assertIn("## 画面风格", text)
        self.assertIn("赛璐璐", text)
        self.assertIn("## 构图", text)
        self.assertIn("低角度仰拍", text)

    def test_build_prompt_skips_empty_core(self):
        data = {"core": {"subject": "", "action": "", "scene": "", "emotion": "", "style": ""},
                "dimensions": {}}
        text = merge_prompt.build_prompt(data)
        self.assertNotIn("## 主体", text)

    def test_extract_snippet_reads_md_prompt_fragment(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = os.path.join(tmp, "a.md")
            with open(md, "w", encoding="utf-8") as f:
                f.write("# 参考图：a\n## 识图分析\nxxx\n## 提示词片段\n低角度逆光\n")
            self.assertEqual(merge_prompt.extract_snippet(md), "低角度逆光")

    def test_extract_snippet_compat_fullwidth_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = os.path.join(tmp, "b.md")
            with open(md, "w", encoding="utf-8") as f:
                f.write("# 参考图：b\n【识图分析】\nxxx\n【提示词片段】\n低角度逆光\n")
            self.assertEqual(merge_prompt.extract_snippet(md), "低角度逆光")

    def test_load_data_reads_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            js = os.path.join(tmp, "d.json")
            with open(js, "w", encoding="utf-8") as f:
                json.dump({"core": {"subject": "A"}}, f, ensure_ascii=False)
            self.assertEqual(merge_prompt.load_data(js)["core"]["subject"], "A")
    def test_build_prompt_handles_null_refs(self):
        data = {"core": {"subject": "A", "action": "", "scene": "", "emotion": "", "style": ""},
                "dimensions": {"画面构图": {"text": "低角度", "refs": None}}}
        text = merge_prompt.build_prompt(data)
        self.assertIn("低角度", text)

    def test_build_prompt_ignores_non_dict_info(self):
        data = {"core": {"subject": "A", "action": "", "scene": "", "emotion": "", "style": ""},
                "dimensions": {"画面构图": "低角度"}}
        text = merge_prompt.build_prompt(data)
        self.assertIn("A", text)
        self.assertNotIn("## 构图", text)
    def test_build_prompt_simplified_role_uses_subject_short(self):
        data = {"core": {"subject": "白发剑客（白袍金色龙纹、蓝腰带、持纹饰长剑）",
                        "subject_short": "白发剑客、精灵宠物、猫耳宠物（形象以引用设定图为准）",
                        "action": "背靠背防御", "scene": "战场", "emotion": "危机", "style": "3D写实"},
                "dimensions": {}}
        text = merge_prompt.build_prompt(data, role_mode="simplified")
        self.assertIn("白发剑客、精灵宠物、猫耳宠物（形象以引用设定图为准）", text)
        self.assertNotIn("白袍金色龙纹", text)
        text_full = merge_prompt.build_prompt(data, role_mode="full")
        self.assertIn("白袍金色龙纹", text_full)


if __name__ == "__main__":
    unittest.main()
