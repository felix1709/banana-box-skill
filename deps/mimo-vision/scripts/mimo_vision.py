#!/usr/bin/env python3
"""内网视觉识别备用脚本 — 调用 glm-5v-turbo 多模态模型识别/描述图片。

v2 新增:
  --structured    结构化风格分析（输出 JSON，合并 PIL 技术信息）
  --compare B.png  双图对比模式（自动生成对比 prompt）
  -o result.json  输出到文件（解决 Windows GBK 终端乱码）
  自动集成 PIL 图片尺寸/格式/通道信息

Usage:
  python scripts/mimo_vision.py -i test.png
  python scripts/mimo_vision.py -i test.png --structured -o analysis.json
  python scripts/mimo_vision.py -i a.png --compare b.png -o compare.json
  python scripts/mimo_vision.py -i test.png -p "图中有什么文字？"
  python scripts/mimo_vision.py -i test.png --raw
"""

import os
import sys
import json
import base64
import argparse
import urllib.request
import urllib.error
import tempfile
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

API_BASE = "https://ai.leihuo.netease.com/v1"
DEFAULT_MODEL = "glm-5v-turbo"


def get_api_key():
    for var in ("LEIHUO_VISION_API_KEY", "MIMO_API_KEY", "XIAOMI_MIMO_API_KEY"):
        key = os.environ.get(var)
        if key:
            return key
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as reg:
            for var in ("LEIHUO_VISION_API_KEY", "MIMO_API_KEY", "XIAOMI_MIMO_API_KEY"):
                try:
                    value, _ = winreg.QueryValueEx(reg, var)
                    if value:
                        return value
                except Exception:
                    continue
    except Exception:
        pass
    sys.exit("Error: No API key. Set LEIHUO_VISION_API_KEY in Windows user environment.")


def image_to_base64(path: str) -> str:
    p = Path(path)
    if not p.exists():
        sys.exit(f"Error: file not found: {path}")
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    ext = p.suffix.lower()
    mime_map = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp",
    }
    mime = mime_map.get(ext, "image/png")
    return f"data:{mime};base64,{b64}"


# ---------- PIL image info (auto-collected) ----------

def get_image_info(path: str) -> dict:
    """Extract technical image metadata using PIL."""
    try:
        from PIL import Image
        img = Image.open(path)
        info = {
            "path": str(Path(path).absolute()),
            "filename": Path(path).name,
            "width": img.size[0],
            "height": img.size[1],
            "mode": img.mode,
            "format": img.format,
            "file_size": Path(path).stat().st_size,
        }
        if img.mode == "RGBA":
            alpha = img.getchannel("A")
            info["has_alpha"] = True
            info["alpha_min"] = alpha.getextrema()[0]
            info["alpha_max"] = alpha.getextrema()[1]
        elif img.mode == "P":
            info["has_alpha"] = "transparency" in img.info
        else:
            info["has_alpha"] = False
        return info
    except ImportError:
        return {"path": str(Path(path).absolute()), "filename": Path(path).name,
                "error": "PIL not available"}
    except Exception as e:
        return {"path": str(Path(path).absolute()), "filename": Path(path).name,
                "error": str(e)}


# ---------- API call ----------

def chat_vision(image_paths: list[str], prompt: str, model: str = DEFAULT_MODEL,
                max_tokens: int = 4096, temperature: float = 1.0,
                top_p: float = 0.95, raw: bool = False, output_file: str = None):
    api_key = get_api_key()

    content_parts = []
    for img_path in image_paths:
        data_url = image_to_base64(img_path)
        content_parts.append({"type": "image_url", "image_url": {"url": data_url}})
    content_parts.append({"type": "text", "text": prompt})

    body = {
        "model": model,
        "messages": [{"role": "user", "content": content_parts}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }

    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer %s" % api_key, "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8") if e.fp else ""
        sys.exit(f"HTTP {e.code}: {err}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error: {e.reason}")

    if raw:
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Raw JSON saved to: {output_file}", file=sys.stderr)
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        return result

    try:
        content = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit("Error: unexpected response format.")

    # If output_file is specified, write there (UTF-8, no terminal encoding issues)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Output saved to: {output_file}", file=sys.stderr)
        return content

    # Otherwise, print to stdout (may have encoding issues on Windows GBK terminals)
    try:
        print(content)
    except UnicodeEncodeError:
        # Fallback: write to temp file on encoding error
        tmp = Path(tempfile.gettempdir()) / f"mimo_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        tmp.write_text(content, encoding="utf-8")
        print(f"[Encoding error — output saved to: {tmp}]", file=sys.stderr)
        print(f"[Use --raw and pipe through python to decode, or use -o flag]", file=sys.stderr)

    return content


# ---------- Structured analysis ----------

STRUCTURED_PROMPT = """Analyze this image as a game UI / art asset. Provide a structured analysis in the following format. Be specific and factual — no fluff.

## STYLE
- Art style: (e.g. flat vector, pixel art, realistic, cartoon, etc.)
- Shape language: (e.g. pure silhouettes, outlined, filled shapes, stencil cutouts, etc.)
- Edge treatment: (e.g. crisp hard edges, soft glow, anti-aliased, dithered, etc.)
- Dimensionality: (e.g. completely flat 2D, subtle 3D bevel, full 3D render, etc.)

## COLORS
- Background: (describe background color/gradient/transparency)
- Foreground: (describe main element colors)
- Palette size: (approximate number of distinct colors)
- Contrast level: (high / medium / low)

## LAYOUT
- Arrangement: (e.g. grid, single icon, scattered, sprite sheet)
- Grid dimensions: (rows x columns, if applicable)
- Element count: (number of distinct icons/elements)
- Element size: (approximate size of each element, e.g. "small ~64px icons")

## SUBJECT
- What is depicted: (weapons, characters, UI elements, effects, etc.)
- Genre/theme: (sci-fi, fantasy, modern military, abstract, etc.)
- Recognizable elements: (list the key identifiable items)

## OVERALL
- Consistency: (how uniform is the set? high / medium / low)
- Complexity: (simple / moderate / detailed)
- Use case: (what kind of game/project this looks designed for)"""


def run_structured(image_paths: list[str], model: str, output_file: str = None) -> dict:
    """Run Mimo with structured analysis prompt and merge with PIL data."""
    # Collect PIL info for all images
    images_info = [get_image_info(p) for p in image_paths]

    # Run Mimo with structured prompt
    content = chat_vision(
        image_paths=image_paths,
        prompt=STRUCTURED_PROMPT,
        model=model,
        max_tokens=2048,
        temperature=0.3,  # Lower temp for more factual output
        raw=False,
    )

    # Build structured result
    result = {
        "analyzed_at": datetime.now().isoformat(),
        "model": model,
        "images": images_info,
        "mimo_analysis": content,
    }

    # Parse Mimo's output to extract sections
    sections = {}
    current_section = "preamble"
    for line in content.split("\n"):
        line_stripped = line.strip()
        if line_stripped.startswith("## "):
            # Extract section name: "## STYLE" -> "style"
            section_name = line_stripped.replace("## ", "").strip().lower()
            current_section = section_name
            sections[current_section] = []
        elif current_section:
            sections.setdefault(current_section, []).append(line)

    result["parsed_sections"] = sections

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Structured analysis saved to: {output_file}", file=sys.stderr)
    else:
        # Print JSON to stdout
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")

    return result


# ---------- Compare mode ----------

COMPARE_PROMPT = """Compare these two images. The LEFT image(s) are the new/generated content, and the RIGHT image is the reference/target.

Evaluate:
1. STYLE MATCH: Does the left match the right's art style? (0-100 score, with specific reasons)
2. COLOR MATCH: Does the color scheme match? (0-100)
3. SHAPE LANGUAGE: Do the shapes/forms feel like they belong in the same set? (0-100)
4. QUALITY GAP: Is there an obvious quality difference? Describe specifically.
5. OVERALL: Can these pass as assets from the same game/project? (YES / ALMOST / NO)
6. TOP ISSUES: List the 3 most important things to fix on the left.

Be critical and specific — vague praise is not helpful."""


def run_compare(new_paths: list[str], ref_path: str, model: str,
                output_file: str = None) -> dict:
    """Compare generated images against a reference."""
    all_paths = new_paths + [ref_path]
    images_info = [get_image_info(p) for p in all_paths]

    content = chat_vision(
        image_paths=all_paths,
        prompt=COMPARE_PROMPT,
        model=model,
        max_tokens=2048,
        temperature=0.3,
        raw=False,
    )

    result = {
        "compared_at": datetime.now().isoformat(),
        "model": model,
        "new_images": images_info[:-1],
        "reference_image": images_info[-1],
        "mimo_comparison": content,
    }

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Comparison saved to: {output_file}", file=sys.stderr)
    else:
        # Print JSON
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")

    return result


# ---------- CLI ----------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="MiMo Vision v2 — multimodal image understanding with structured output"
    )
    parser.add_argument("--image", "-i", action="append", required=True,
                        help="Image file path (repeatable for multiple images)")
    parser.add_argument("--prompt", "-p",
                        help="Question/prompt for the model")
    parser.add_argument("--structured", "-S", action="store_true",
                        help="Structured style analysis mode (auto-prompt + JSON output)")
    parser.add_argument("--compare", "-C", default=None,
                        help="Reference image path for comparison mode")
    parser.add_argument("--output", "-o", default=None,
                        help="Save output to file (UTF-8, avoids terminal encoding issues)")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--raw", "-r", action="store_true",
                        help="Print raw JSON response from API")
    parser.add_argument("--info", action="store_true",
                        help="Only print PIL image technical info (no API call)")
    args = parser.parse_args()

    # --info mode: just print PIL data, no API call
    if args.info:
        info = [get_image_info(p) for p in args.image]
        print(json.dumps(info, indent=2, ensure_ascii=False))
        sys.exit(0)

    # --compare mode
    if args.compare:
        run_compare(
            new_paths=args.image,
            ref_path=args.compare,
            model=args.model,
            output_file=args.output,
        )
        sys.exit(0)

    # --structured mode
    if args.structured:
        run_structured(
            image_paths=args.image,
            model=args.model,
            output_file=args.output,
        )
        sys.exit(0)

    # Default: describe mode
    prompt = args.prompt or "请详细描述这张图片的内容。"
    chat_vision(
        image_paths=args.image,
        prompt=prompt,
        model=args.model,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        raw=args.raw,
        output_file=args.output,
    )
