#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检索参考库历史片段：按维度/关键词搜索 .md 描述，返回提示词片段。

知识库机制：参考库是永久积累的（每个类目一个文件夹），本脚本让生成提示词时
能自动翻出历史片段作为经验，用得越多、库越丰富、提示词越聪明。

用法：
  python search_library.py --lib <参考库路径> --dimension <维度> [--keyword <关键词>] [--limit <数量>]
"""
import argparse
import os
import sys

DIMENSIONS = ["画面构图", "美术风格", "角色动作", "灯光氛围",
              "环境氛围", "场景参考", "多人动作", "人物比例"]


def extract_snippet(md_path):
    """从参考图 .md 中提取 '## 提示词片段' 分节内容。"""
    with open(md_path, encoding="utf-8-sig") as f:
        content = f.read()
    for marker in ("## 提示词片段", "【提示词片段】"):
        idx = content.find(marker)
        if idx >= 0:
            return content[idx + len(marker):].strip()
    return ""


def search(lib, dimension, keyword="", limit=10):
    """返回该维度下匹配的 [{"file": 路径, "snippet": 片段}] 列表。"""
    dim_dir = os.path.join(lib, dimension)
    if not os.path.isdir(dim_dir):
        return []
    results = []
    for name in sorted(os.listdir(dim_dir)):
        if not name.endswith(".md"):
            continue
        md_path = os.path.join(dim_dir, name)
        try:
            snippet = extract_snippet(md_path)
        except Exception:
            continue
        if not snippet:
            continue
        if keyword and keyword not in snippet and keyword not in name:
            continue
        results.append({"file": md_path, "snippet": snippet})
        if len(results) >= limit:
            break
    return results


def main():
    parser = argparse.ArgumentParser(description="检索参考库历史片段")
    parser.add_argument("--lib", required=True, help="参考库根目录")
    parser.add_argument("--dimension", required=True, choices=DIMENSIONS, help="维度")
    parser.add_argument("--keyword", default="", help="关键词过滤（可选）")
    parser.add_argument("--limit", type=int, default=10, help="最多返回条数")
    args = parser.parse_args()

    results = search(args.lib, args.dimension, args.keyword, args.limit)
    if not results:
        print("（该维度暂无匹配的历史片段）")
        return
    for i, r in enumerate(results, 1):
        print("--- [%d] %s ---" % (i, os.path.basename(r["file"])))
        print(r["snippet"])
        print()


if __name__ == "__main__":
    main()
