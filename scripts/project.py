#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目/帧记录管理：创建项目、添加帧、列出项目/帧。

项目记录默认存 ~/.banana-box/projects.json；--dir 可覆盖（用于测试）。

用法：
  python project.py init <项目名> --mode concept|project --lib <参考库路径> [--dir <记录目录>]
  python project.py add-frame <项目名> --name <帧名> --prompt <提示词文件> [--dir <记录目录>]
  python project.py list [--project <项目名>] [--dir <记录目录>]
"""
import argparse
import json
import os
import sys
from datetime import date

DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".banana-box")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def records_path(store_dir):
    return os.path.join(store_dir, "projects.json")


def load_records(store_dir):
    path = records_path(store_dir)
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"projects": {}}


def save_records(store_dir, records):
    os.makedirs(store_dir, exist_ok=True)
    with open(records_path(store_dir), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def init_project(store_dir, name, mode, lib):
    records = load_records(store_dir)
    if name in records["projects"]:
        raise ValueError("项目已存在：%s" % name)
    records["projects"][name] = {
        "name": name,
        "mode": mode,
        "lib": lib,
        "created": date.today().isoformat(),
        "frames": [],
    }
    save_records(store_dir, records)


def add_frame(store_dir, name, frame_name, prompt):
    records = load_records(store_dir)
    if name not in records["projects"]:
        raise ValueError("项目不存在：%s" % name)
    records["projects"][name]["frames"].append({
        "name": frame_name,
        "prompt": prompt,
        "date": date.today().isoformat(),
    })
    save_records(store_dir, records)


def list_frames(store_dir, name):
    records = load_records(store_dir)
    if name not in records["projects"]:
        raise ValueError("项目不存在：%s" % name)
    return records["projects"][name]["frames"]


def list_projects(store_dir):
    records = load_records(store_dir)
    return list(records["projects"].keys())


def main():
    parser = argparse.ArgumentParser(description="项目/帧记录管理")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("name")
    p_init.add_argument("--mode", required=True, choices=["concept", "project"])
    p_init.add_argument("--lib", default="")
    p_init.add_argument("--dir", default=DEFAULT_DIR)

    p_add = sub.add_parser("add-frame")
    p_add.add_argument("name")
    p_add.add_argument("--name", dest="frame_name", required=True)
    p_add.add_argument("--prompt", required=True)
    p_add.add_argument("--dir", default=DEFAULT_DIR)

    p_list = sub.add_parser("list")
    p_list.add_argument("--project", default="")
    p_list.add_argument("--dir", default=DEFAULT_DIR)

    args = parser.parse_args()

    if args.cmd == "init":
        init_project(args.dir, args.name, args.mode, args.lib)
        print("已创建项目：%s（模式：%s）" % (args.name, args.mode))
    elif args.cmd == "add-frame":
        add_frame(args.dir, args.name, args.frame_name, args.prompt)
        print("已添加帧：%s / %s" % (args.name, args.frame_name))
    elif args.cmd == "list":
        if args.project:
            for f in list_frames(args.dir, args.project):
                print("- %s（%s）：%s" % (f["name"], f["date"], f["prompt"]))
        else:
            for p in list_projects(args.dir):
                print(p)


if __name__ == "__main__":
    main()