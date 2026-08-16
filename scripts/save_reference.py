#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""banana-box 参考库存取：复制图片到参考库对应维度目录，按维度聚焦指令调识图，生成 .md 描述。

用法：
  python save_reference.py --image <图片路径> --dimension <维度> --name <文件名> --lib <参考库根目录> [--tags 标签1,标签2] [--skip-vision]
"""
import argparse
import os
import shutil
import subprocess
import sys
from datetime import date

GLM_SCRIPT = r"C:\Users\Felix\.codex\skills\glm-vision\scripts\glm_vision.py"
MIMO_SCRIPT = r"C:\Users\Felix\.codex\skills\mimo-vision\scripts\mimo_vision.py"

VALID_DIMENSIONS = [
    "画面构图", "美术风格", "角色动作", "灯光氛围",
    "环境氛围", "场景参考", "多人动作", "人物比例",
]

FOCUS_PROMPTS = {
    "画面构图": "请只分析这张参考图的【画面构图】要素：景别（特写/近景/中景/全景/远景）、镜头角度（俯拍/仰拍/平视）、透视关系、视觉引导（线条/视线/框架/留白）、画面平衡（主体位置/重量分布）。视角判断必须结合地平线位置、透视灭点、人物与地面比例等可见依据，并说明判断理由。忽略故事、角色细节等其他信息。输出格式：先写'## 识图分析'分节逐项列出，再写'## 提示词片段'分节，把分析转成可直接用于提示词的文字。判断必须基于画面可见特征；无法确定的项明确写'无法判断'；禁止编造画面中不存在的元素（如具体生物种类、身份、剧情）。",
    "美术风格": "请只分析这张参考图的【美术风格】要素：风格类型（写实/卡通/赛璐璐/厚涂/水彩/三渲二等）、线条特征（粗细/虚实）、渲染质感、上色方式（平涂/渐变/笔触）、色彩特征（饱和度/对比度/色调）。风格判断基于线条粗细、笔触、上色方式、渲染质感等可见特征。忽略故事、角色细节等其他信息。输出格式：先写'## 识图分析'分节逐项列出，再写'## 提示词片段'分节，把分析转成可直接用于提示词的文字。判断必须基于画面可见特征；无法确定的项明确写'无法判断'；禁止编造画面中不存在的元素（如具体生物种类、身份、剧情）。",
    "角色动作": "请只分析这张参考图的【角色动作】要素：姿态与重心（站/跑/跳/摔倒等）、肢体语言（手部/躯干朝向）、动态暗示（残留动态/衣摆头发飘动）、力量感与张力。动作判断基于重心位置、关节角度、肢体动势线、衣物动态等可见依据。忽略环境、道具等其他信息。输出格式：先写'## 识图分析'分节逐项列出，再写'## 提示词片段'分节，把分析转成可直接用于提示词的文字。判断必须基于画面可见特征；无法确定的项明确写'无法判断'；禁止编造画面中不存在的元素（如具体生物种类、身份、剧情）。",
    "灯光氛围": "请只分析这张参考图的【灯光氛围】要素：光源位置与数量（主光/辅光/环境光）、光源类型（硬光/软光/逆光/侧光/顶光）、阴影方向与软硬、明暗层次（高光/中间调/暗部/闭塞阴影）、色彩调性（冷暖/氛围色）。光源判断基于阴影方向、高光位置、明暗过渡软硬等可见依据。忽略故事、角色细节等其他信息。输出格式：先写'## 识图分析'分节逐项列出，再写'## 提示词片段'分节，把分析转成可直接用于提示词的文字。判断必须基于画面可见特征；无法确定的项明确写'无法判断'；禁止编造画面中不存在的元素（如具体生物种类、身份、剧情）。",
    "环境氛围": "请只分析这张参考图的【环境氛围】要素：时间与天气（白天/夜晚/雨/雾等）、环境细节（植被/建筑/道具）、空气透视（远景饱和度/对比度）、空间层次。时间与天气判断基于光线色温、天空状态、能见度、地表反光等可见依据。忽略角色、故事等其他信息。输出格式：先写'## 识图分析'分节逐项列出，再写'## 提示词片段'分节，把分析转成可直接用于提示词的文字。判断必须基于画面可见特征；无法确定的项明确写'无法判断'；禁止编造画面中不存在的元素（如具体生物种类、身份、剧情）。",
    "场景参考": "请只分析这张参考图的【场景】要素：场景类型（室内/室外/街道/森林等）、空间布局（前后景/纵深）、关键道具与陈设、建筑风格/时代特征。场景类型判断基于建筑形式、植被地貌、器物陈设等可见特征。忽略角色、故事等其他信息。输出格式：先写'## 识图分析'分节逐项列出，再写'## 提示词片段'分节，把分析转成可直接用于提示词的文字。判断必须基于画面可见特征；无法确定的项明确写'无法判断'；禁止编造画面中不存在的元素（如具体生物种类、身份、剧情）。",
    "多人动作": "请只分析这张参考图的【多人动作】要素：角色数量与位置关系、互动动作（对话/打斗/协作）、视线关系、主次关系、空间遮挡。互动关系判断基于肢体朝向、接触点、视线方向等可见依据。忽略环境、道具等其他信息。输出格式：先写'## 识图分析'分节逐项列出，再写'## 提示词片段'分节，把分析转成可直接用于提示词的文字。判断必须基于画面可见特征；无法确定的项明确写'无法判断'；禁止编造画面中不存在的元素（如具体生物种类、身份、剧情）。",
    "人物比例": "请只分析这张参考图的【人物比例】要素：头身比（Q版/正常/夸张）、体型特征、透视下的比例变形、人物与场景的比例关系。头身比判断基于头部与躯干长度比、四肢比例等可见依据。忽略表情、故事等其他信息。输出格式：先写'## 识图分析'分节逐项列出，再写'## 提示词片段'分节，把分析转成可直接用于提示词的文字。判断必须基于画面可见特征；无法确定的项明确写'无法判断'；禁止编造画面中不存在的元素（如具体生物种类、身份、剧情）。",
}


def copy_image(src, lib_root, dimension, name):
    if os.path.basename(name) != name:
        raise ValueError("文件名不能包含路径分隔符：%s" % name)
    name = os.path.splitext(name)[0]
    dim_dir = os.path.join(lib_root, dimension)
    os.makedirs(dim_dir, exist_ok=True)
    ext = os.path.splitext(src)[1].lower() or ".png"
    dst_img = os.path.join(dim_dir, name + ext)
    shutil.copy2(src, dst_img)
    return dst_img


def run_glm(img, prompt):
    r = subprocess.run([sys.executable, GLM_SCRIPT, img, "-q", prompt, "--thinking"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=180)
    return r.returncode, (r.stdout or r.stderr or "").strip()


def run_mimo(img, prompt):
    r = subprocess.run([sys.executable, MIMO_SCRIPT, "-i", img, "-p", prompt],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=180)
    return r.returncode, (r.stdout or r.stderr or "").strip()


def describe(img, dimension):
    prompt = FOCUS_PROMPTS[dimension]
    code, out = run_glm(img, prompt)
    if code != 0 or ("限流" in out or "429" in out or "1305" in out):
        code, out = run_mimo(img, prompt)
    if code != 0:
        raise RuntimeError("识图失败（glm 与 mimo 均不可用）：%s" % out)
    return out


def _ensure_api_keys():
    """识图 API key 兜底：进程环境缺省时，从 Windows 用户环境变量读取。

    解决新开的 Codex/终端会话未加载新配置 key 的问题（用户级环境变量
    在会话启动后才设置时，进程环境里读不到）。
    """
    for var in ("ZHIPU_API_KEY", "MIMO_API_KEY"):
        if os.environ.get(var):
            continue
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                val, _ = winreg.QueryValueEx(key, var)
                if val:
                    os.environ[var] = val
        except Exception:
            pass


def write_md(dst_img, dimension, analysis, tags):
    name = os.path.splitext(os.path.basename(dst_img))[0]
    md_path = os.path.splitext(dst_img)[0] + ".md"
    lines = [
        "# 参考图：%s" % name,
        "- 维度：%s" % dimension,
        "- 存储日期：%s" % date.today().isoformat(),
        "- 标签：%s" % (", ".join(tags) if tags else "无"),
        "",
        analysis,
        "",
    ]
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return md_path


def main():
    parser = argparse.ArgumentParser(description="存入参考图并生成识图描述")
    parser.add_argument("--image", required=True, help="参考图路径")
    parser.add_argument("--dimension", required=True, choices=VALID_DIMENSIONS, help="维度")
    parser.add_argument("--name", required=True, help="文件名（不含路径，自动去掉扩展名）")
    parser.add_argument("--lib", required=True, help="参考库根目录")
    parser.add_argument("--tags", default="", help="逗号分隔标签（可选）")
    parser.add_argument("--skip-vision", action="store_true", help="跳过识图只存图")
    _ensure_api_keys()
    args = parser.parse_args()

    if not os.path.isfile(args.image):
        print("错误：找不到图片 %s" % args.image, file=sys.stderr)
        sys.exit(1)
    dst_img = copy_image(args.image, args.lib, args.dimension, args.name)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    if args.skip_vision:
        analysis = "（已跳过识图）"
    else:
        try:
            analysis = describe(dst_img, args.dimension)
        except RuntimeError as e:
            print(e, file=sys.stderr)
            sys.exit(2)
    md_path = write_md(dst_img, args.dimension, analysis, tags)
    print("已存入：%s" % dst_img)
    print("描述文件：%s" % md_path)
    preview = analysis[:200] + ("..." if len(analysis) > 200 else "")
    print("识图结果：%s" % preview)


if __name__ == "__main__":
    main()
