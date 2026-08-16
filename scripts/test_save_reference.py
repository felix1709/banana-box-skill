# -*- coding: utf-8 -*-
"""save_reference.py 单元测试（不联网，mock 识图子进程）。"""
import os
import sys
import tempfile
import unittest
import unittest.mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_reference


class TestSaveReference(unittest.TestCase):
    def test_focus_prompts_cover_all_dimensions(self):
        self.assertEqual(set(save_reference.VALID_DIMENSIONS),
                         set(save_reference.FOCUS_PROMPTS))

    def test_copy_image_creates_dimension_dir_and_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "src.png")
            with open(src, "wb") as f:
                f.write(b"fake-png")
            lib = os.path.join(tmp, "lib")
            dst = save_reference.copy_image(src, lib, "画面构图", "低角度_特写")
            self.assertTrue(os.path.isfile(dst))
            self.assertIn("画面构图", dst)

    def test_describe_falls_back_to_mimo_on_glm_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            img = os.path.join(tmp, "a.png")
            with open(img, "wb") as f:
                f.write(b"x")
            with unittest.mock.patch.object(save_reference, "run_glm",
                                            return_value=(1, "限流 429")):
                with unittest.mock.patch.object(save_reference, "run_mimo",
                                                return_value=(0, "小米识别结果")):
                    self.assertEqual(save_reference.describe(img, "灯光氛围"),
                                     "小米识别结果")

    def test_write_md_writes_analysis_and_tags(self):
        with tempfile.TemporaryDirectory() as tmp:
            img = os.path.join(tmp, "lib", "美术风格", "t.png")
            os.makedirs(os.path.dirname(img))
            with open(img, "wb") as f:
                f.write(b"x")
            analysis = ("## 识图分析\n厚涂画风，暖色调\n"
                        "## 提示词片段\n厚涂暖色调，强笔触\n")
            md = save_reference.write_md(img, "美术风格", analysis, ["厚涂", "暖色"])
            self.assertTrue(os.path.isfile(md))
            with open(md, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("美术风格", content)
            self.assertIn("## 识图分析", content)
            self.assertIn("## 提示词片段", content)
            self.assertIn("厚涂暖色调，强笔触", content)
            self.assertIn("厚涂", content)

    def test_copy_image_rejects_path_in_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "s.png")
            with open(src, "wb") as f:
                f.write(b"x")
            lib = os.path.join(tmp, "lib")
            with self.assertRaises(ValueError):
                save_reference.copy_image(src, lib, "画面构图", os.path.join("..", "evil"))

    def test_copy_image_strips_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "s.png")
            with open(src, "wb") as f:
                f.write(b"x")
            lib = os.path.join(tmp, "lib")
            dst = save_reference.copy_image(src, lib, "画面构图", "low_angle.png")
            self.assertEqual(os.path.basename(dst), "low_angle.png")


if __name__ == "__main__":
    unittest.main()
