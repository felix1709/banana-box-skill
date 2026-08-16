# banana-box-skill

单帧画面需求引导 skill：把模糊想法变成完整单帧画面提示词，再扩展成 AI 视频提示词。

## 依赖
- glm-vision（识图主）/ mimo-vision（识图备）—— 已安装
- cinematic-video-prompt-engineer（视频提示词）—— 已安装

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
- 识图全部失败：检查 ZHIPU_API_KEY / MIMO_API_KEY 环境变量
- 参考库路径中文：PowerShell 中请用引号包裹完整路径
