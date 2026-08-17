#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""内网视觉识别主脚本：把本地图片/URL 发给 doubao-seed-1-6-vision-250815，返回识别结果。"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

API_URL = "https://ai.leihuo.netease.com/v1/chat/completions"
MODEL = "doubao-seed-1-6-vision-250815"


def _get_api_key():
    var = "LEIHUO_VISION_API_KEY"
    api_key = os.environ.get(var)
    if api_key:
        return api_key
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, var)
            if value:
                return value
    except Exception:
        pass
    return ""


def image_to_data_url(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return "data:%s;base64,%s" % (mime, b64)


def main():
    parser = argparse.ArgumentParser(description="用 doubao-seed-1-6-vision-250815 识别图片")
    parser.add_argument("images", nargs="+", help="图片路径或 URL")
    parser.add_argument("-q", "--question", default="请详细描述这张图片的内容。", help="对图片提出的问题")
    parser.add_argument("--thinking", action="store_true", help="开启深度思考模式")
    args = parser.parse_args()

    api_key = _get_api_key()
    if not api_key:
        print("错误：未设置 LEIHUO_VISION_API_KEY 环境变量", file=sys.stderr)
        sys.exit(1)

    content = []
    for img in args.images:
        if img.startswith(("http://", "https://")):
            content.append({"type": "image_url", "image_url": {"url": img}})
        else:
            if not os.path.isfile(img):
                print("错误：找不到图片文件 %s" % img, file=sys.stderr)
                sys.exit(1)
            content.append({"type": "image_url", "image_url": {"url": image_to_data_url(img)}})
    content.append({"type": "text", "text": args.question})

    payload = {"model": MODEL, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer %s" % api_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("API 调用失败: %s" % e, file=sys.stderr)
        sys.exit(1)

    try:
        reply = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print("响应解析失败: %s" % json.dumps(data, ensure_ascii=False)[:500], file=sys.stderr)
        sys.exit(1)
    print(reply)


if __name__ == "__main__":
    main()
