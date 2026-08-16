# -*- coding: utf-8 -*-
"""search_library.py 单元测试。"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import search_library


def _make_md(root, dim, name, snippet):
    d = os.path.join(root, dim)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + ".md")
    with open(p, "w", encoding="utf-8") as f:
        f.write("# 参考图：%s\n## 识图分析\nxxx\n## 提示词片段\n%s\n" % (name, snippet))
    return p


class TestSearchLibrary(unittest.TestCase):
    def test_search_finds_snippets(self):
        with tempfile.TemporaryDirectory() as tmp:
            _make_md(tmp, "灯光氛围", "夜景", "金色逆光，暖冷对比")
            _make_md(tmp, "灯光氛围", "烛光", "暖黄烛光，柔和阴影")
            results = search_library.search(tmp, "灯光氛围")
            self.assertEqual(len(results), 2)

    def test_search_keyword_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            _make_md(tmp, "灯光氛围", "夜景", "金色逆光，暖冷对比")
            _make_md(tmp, "灯光氛围", "烛光", "暖黄烛光")
            results = search_library.search(tmp, "灯光氛围", keyword="烛光")
            self.assertEqual(len(results), 1)
            self.assertIn("暖黄烛光", results[0]["snippet"])

    def test_search_empty_dimension(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = search_library.search(tmp, "画面构图")
            self.assertEqual(results, [])

    def test_search_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(5):
                _make_md(tmp, "美术风格", "s%d" % i, "风格片段%d" % i)
            results = search_library.search(tmp, "美术风格", limit=3)
            self.assertEqual(len(results), 3)


if __name__ == "__main__":
    unittest.main()
