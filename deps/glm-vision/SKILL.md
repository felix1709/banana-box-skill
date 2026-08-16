---
name: glm-vision
description: 使用智谱 GLM-4.6V-Flash 视觉模型识别和理解图片。当用户发送图片并要求识别内容、描述画面、提取图片中的文字、分析图表/截图/照片，或需要视觉理解时使用。通过本地脚本调用智谱开放平台 API，支持本地图片文件或图片 URL。
---

# GLM-4.6V-Flash 识图

通过智谱开放平台的 `glm-4.6v-flash` 视觉模型识别图片内容。模型免费，支持图片、视频、文件输入，并可通过 `--thinking` 开启深度思考。

## 何时使用

- 用户发送图片并提问（如"这张图里有什么""帮我看看这张截图""图片里的字是什么"）
- 需要理解图表、截图、照片、海报、文档扫描件等视觉内容
- 用户明确要求用 GLM 视觉模型识别图片

## 调用方式

用 Python 运行脚本（推荐开启深度思考以获得更准确结果）：

```powershell
python "C:\Users\Felix\.codex\skills\glm-vision\scripts\glm_vision.py" <图片路径或URL> [-q "问题"] [--thinking]
```

示例：

```powershell
# 识别本地图片，默认问"这张图片内容是什么"
python "C:\Users\Felix\.codex\skills\glm-vision\scripts\glm_vision.py" "D:\photos\demo.png" --thinking

# 指定问题
python "C:\Users\Felix\.codex\skills\glm-vision\scripts\glm_vision.py" "D:\photos\demo.png" -q "图中文字是什么？" --thinking

# 支持多张图片和图片 URL
python "C:\Users\Felix\.codex\skills\glm-vision\scripts\glm_vision.py" "https://example.com/a.jpg" -q "描述这张图"
```

## 配置

- API Key 从环境变量 `ZHIPU_API_KEY` 读取（已配置，无需手动填写）
- 端点：`https://open.bigmodel.cn/api/paas/v4/chat/completions`
- 模型：`glm-4.6v-flash`
- 脚本位置：`C:\Users\Felix\.codex\skills\glm-vision\scripts\glm_vision.py`