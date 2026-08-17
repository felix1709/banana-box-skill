---
name: 内网视觉识别备用
description: 调用内网 glm-5v-turbo 多模态模型识别/理解图片。这是主视觉模型 doubao-seed-1-6-vision-250815 不可用时的备用方案；当用户发来图片、截图、照片，或 Agent 需要查看图片内容来回答问题、理解上下文时触发。
---

# 内网视觉识别（备用）


> **本机 Python**：C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe（若 python 不在 PATH，用完整路径调用）。
> **备用方案**：当 glm-vision（主模型 doubao-seed-1-6-vision-250815）返回限流或错误时，改用本 skill 识别图片。

调用 `C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py` 通过内网 `glm-5v-turbo` 视觉 API 理解图片内容。这是主模型不可用时的备用视觉能力来源。

## 触发规则

以下任一情况必须调用此 skill：

1. **用户直接发图片** → 我收到图片路径或看到图片时，立即调用此脚本获取图片内容
2. **用户提到"看看这个"、"这个图"、"截图里"、"看图"** → 调用脚本
3. **Agent 需要查看图片才能回答** → 主动调用（如"帮我分析这个UI截图"、"这个设计图有什么问题"）
4. **用户说"你看下"、"帮我看下"** → 调用脚本
5. **任何需要视觉理解的场景** → 调用脚本，不要猜测图片内容

## ⚠️ 关键规则：先看再答

**禁止在没看到图片的情况下猜测或编造图片内容。** 如果用户发来一张图并问问题，步骤如下：

1. 立即运行 `python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i <图片路径> -p "<合适的问题>"`
2. 读取脚本的 stdout 输出，这就是我对那张图的理解
3. 基于识别结果回答用户

如果没有调用脚本，我就不知道图片里有什么。

## 命令示例

### 基础识别——描述图片
```bash
python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i "图片路径"
```

### 专项识别——带针对性问题
```bash
python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i "截图.png" -p "图片中有哪些按钮和菜单？请逐条列出。"
```

### 多图对比
```bash
python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i "修改前.png" -i "修改后.png" -p "这两张图有什么不同？"
```

### 文字提取
```bash
python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i "文档.jpg" -p "提取图片中所有文字，保持原有排版结构。"
```

### v2 新功能：结构化分析
```bash
# 结构化风格分析（输出 JSON + PIL 图片信息）
python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i "参考图.png" --structured -o analysis.json

# 双图对比模式（自动生成对比 prompt，输出评分）
python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i "新图标.png" --compare "参考图集.png" -o compare.json

# 只看图片技术信息（不调用 API，纯本地 PIL 分析）
python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i "图片.png" --info
```

### 保存到文件（避免 Windows 终端乱码）
```bash
python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i "图片.png" -p "描述这张图" -o result.txt
```

## 全部参数

| 参数 | 说明 | 默认值 |
|---|---|---|
| `-i` / `--image` | 图片路径（可重复传入多张） | 必填 |
| `-p` / `--prompt` | 提问/指令 | `请详细描述这张图片的内容。` |
| `-S` / `--structured` | **v2** 结构化风格分析（自动 prompt + JSON 输出） | 否 |
| `-C` / `--compare` | **v2** 对比模式，传入参考图路径 | 无 |
| `--info` | **v2** 仅输出 PIL 技术信息（无 API 调用） | 否 |
| `-o` / `--output` | **v2** 保存输出到文件（UTF-8，解决乱码） | stdout |
| `-m` / `--model` | 模型名 | `glm-5v-turbo` |
| `--max-tokens` | 最大输出 token 数 | `4096` |
| `--temperature` | 采样温度 [0, 1.5] | `1.0` |
| `--top-p` | 核采样阈值 [0.01, 1.0] | `0.95` |
| `-r` / `--raw` | 输出完整 JSON 响应 | 否 |

## 模型特性

- **glm-5v-turbo**：内网备用视觉模型，支持中文 prompt
- 单张图片建议控制文件大小，过大可能导致 400 错误
- 超时 120 秒，大图或复杂任务可能较慢

## 使用场景示例

| 用户说什么 | 我应该做什么 |
|---|---|
| "帮我看看这张图" | `python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i 图片 -p "请详细描述这张图片。"` |
| "这个报错截图啥意思？" | `python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i 截图 -p "这是一个报错截图，请识别错误信息并解释原因。"` |
| "这个设计和那个设计哪个好？" | `python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i 设计A -i 设计B -p "从设计角度比较这两张图，给出优劣分析。"` |
| 用户发来一张游戏截图 | `python "C:\Users\admin\.codex\skills\mimo-vision\scripts\mimo_vision.py" -i 截图 -p "请详细描述这个游戏画面中的内容，包括UI、角色、场景等。"` |

## API 信息

- 端点：`POST https://ai.leihuo.netease.com/v1/chat/completions`
- 认证：`Authorization: Bearer $LEIHUO_VISION_API_KEY`
- 模型：`glm-5v-turbo`
- 能力：图片理解

## 注意事项

- 主动使用！当用户的问题需要看图才能准确回答时，不要猜，直接调脚本看
- `--prompt` 要具体明确——"提取所有文字"比"看看"效果好得多
- 脚本 stdout 就是我对图片的认知，我应该在回复中基于这个认知来回答用户
- 如果脚本报编码错误，用 `--raw` 获取 JSON 再从中提取 content
