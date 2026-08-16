#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并需求 JSON 为单帧画面提示词。

输入 JSON 结构：
{
  "core": {"subject": "...", "action": "...", "scene": "...", "emotion": "...", "style": "..."},
  "dimensions": {
    "画面构图": {"text": "低角度仰拍", "refs": ["C:/.../画面构图/a.md"]},
    ...
  }
}

用法：
  python merge_prompt.py --input <需求.json> [--output <输出.md>]
"""
import argparse
import json
import os
import sys

CORE_SECTIONS = [
    ("subject", "主体"),
    ("action", "动作"),
    ("scene", "场景"),
    ("emotion", "情绪/叙事目的"),
    ("style", "画面风格"),
]

DIMENSION_SECTIONS = [
    ("画面构图", "构图"),
    ("美术风格", "美术风格"),
    ("角色动作", "角色动作"),
    ("灯光氛围", "灯光氛围"),
    ("环境氛围", "环境氛围"),
    ("场景参考", "场景参考"),
    ("多人动作", "多人动作"),
    ("人物比例", "人物比例"),
]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def extract_snippet(md_path):
    if not os.path.isfile(md_path):
        return ""
    with open(md_path, encoding="utf-8-sig") as f:
        content = f.read()
    for marker in ("## 提示词片段", "【提示词片段】"):
        idx = content.find(marker)
        if idx >= 0:
            return content[idx + len(marker):].strip()
    return content.strip()


def build_prompt(data, role_mode="full"):
    core = data.get("core", {}) or {}
    dims = data.get("dimensions", {}) or {}
    lines = ["# 单帧画面提示词", ""]
    for key, label in CORE_SECTIONS:
        if key == "subject" and role_mode == "simplified":
            val = (core.get("subject_short") or core.get("subject") or "").strip()
        else:
            val = (core.get(key) or "").strip()
        if val:
            lines += ["## %s" % label, val, ""]
    for dim, label in DIMENSION_SECTIONS:
        info = dims.get(dim)
        if not info or not isinstance(info, dict):
            continue
        parts = []
        text = (info.get("text") or "").strip()
        if text:
            parts.append(text)
        for ref in (info.get("refs") or []):
            snippet = extract_snippet(ref)
            if snippet:
                parts.append(snippet)
        if parts:
            lines += ["## %s" % label, "\n\n".join(parts), ""]
    return "\n".join(lines).rstrip() + "\n"


def load_data(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="合并需求为单帧画面提示词")
    parser.add_argument("--input", required=True, help="需求 JSON 路径")
    parser.add_argument("--output", default="", help="输出 md 路径（默认打印到 stdout）")
    parser.add_argument("--role-mode", default="full", choices=["full", "simplified"], help="主体描述模式：full 完整描述 / simplified 简化（形象以引用图为准）")
    args = parser.parse_args()

    data = load_data(args.input)
    prompt = build_prompt(data, role_mode=args.role_mode)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(prompt)
        print("已生成：%s" % args.output)
    else:
        print(prompt)


if __name__ == "__main__":
    main()
