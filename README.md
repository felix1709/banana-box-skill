# banana-box-skill

单帧画面需求引导 skill：把模糊想法变成完整单帧画面提示词，再扩展成 AI 视频提示词。

## 依赖（自包含，deps/ 已打包）

本仓库已打包完整依赖，clone 后开箱即用（无需额外安装）：

- `deps/glm-vision/`：识图主（内网 `doubao-seed-1-6-vision-250815`）
- `deps/mimo-vision/`：识图备（内网 `glm-5v-turbo`，主模型不可用时自动切换）
- `deps/cinematic-video-prompt-engineer/`：视频提示词（完整版）

**识别功能需要配置 key（首次使用）**：
- `LEIHUO_VISION_API_KEY`：内网视觉接口 key
- 配置命令（PowerShell）：
  ```powershell
  [Environment]::SetEnvironmentVariable("LEIHUO_VISION_API_KEY","你的key","User")
  ```

**系统已安装同款 skill 时自动优先使用系统版**（脚本 _resolve_script 逻辑），无需手动切换。

## 使用
在 Codex 对话中说"生成一个单帧画面"即可触发引导。

## 参考库结构
<参考库>/画面构图|美术风格|角色动作|灯光氛围|环境氛围|场景参考|多人动作|人物比例/
每张图：同名 .png + .md（识图分析 + 提示词片段）

## 脚本
- save_reference.py：存参考图 + 针对性识图 + 生成 .md
- merge_prompt.py：需求 JSON → 单帧提示词
- project.py：项目/帧记录

## 常见问题
- 识图全部失败：检查 LEIHUO_VISION_API_KEY 环境变量
- 参考库路径中文：PowerShell 中请用引号包裹完整路径
