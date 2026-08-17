---
name: banana-box
description: 生成单帧画面提示词的引导型 skill。当用户想从模糊想法得到完整的单帧画面提示词（主体/动作/场景/情绪/风格/构图/灯光等），或需要把单帧扩展成 AI 视频提示词时使用。触发词："生成单帧画面"、"帮我做一帧"、"单帧画面提示词"。
---

# banana-box：单帧画面需求引导与提示词生成

把模糊想法逐步细化为完整单帧画面提示词，确认后交给 cinematic-video-prompt-engineer 输出视频提示词。

## 依赖检查与配置（启动时第一步执行）

按顺序检查以下依赖，**已安装就跳过，未安装用仓库内 deps/ 版本**：

1. **识图 skill**：检查 `C:\Users\admin\.codex\skills\glm-vision\SKILL.md` 和 `mimo-vision\SKILL.md` 是否存在
   - 已存在 → 使用系统版，跳过
   - 不存在 → 使用仓库内置 `deps/glm-vision/`（主）和 `deps/mimo-vision/`（备），并提示用户配置 API key：
     - 主模型 `glm-vision`：`doubao-seed-1-6-vision-250815`
     - 备用模型 `mimo-vision`：`glm-5v-turbo`
     - 统一走内网接口 `https://ai.leihuo.netease.com/v1/chat/completions`
     - 配置命令（PowerShell）：`[Environment]::SetEnvironmentVariable("LEIHUO_VISION_API_KEY","你的key","User")`
     - 未配置 key 时识图功能不可用，此时引导用户改用文字描述
2. **单帧生图 skill**：检查 `C:\Users\admin\.codex\skills\cinematic-prompt-engine\SKILL.md` 是否存在
   - 已存在 → 单帧画面提示词使用 `cinematic-prompt-engine`
   - 不存在 → 使用仓库内置 `deps/cinematic-prompt-engine/`（按其 SKILL.md 执行）
3. **视频连续镜头 skill**：检查 `C:\Users\admin\.codex\skills\cinematic-video-prompt-engineer\SKILL.md` 是否存在
   - 已存在 → 使用系统版
   - 不存在 → 使用仓库内置 `deps/cinematic-video-prompt-engineer/`（按其 SKILL.md 执行）
4. **参考库**：默认 `references/`（仓库内置，随 git 同步）

> 说明：脚本自动做"系统优先、deps 兜底"（save_reference.py 的 _resolve_script），无需手动切换。

## 启动流程

1. 询问创作模式：
   - **概念创作**：单个画面，快速产出
   - **项目制作**：连续多帧，一个项目积累多个画面
2. 指定参考库：默认使用 skill 内置知识库 `C:\Users\admin\.codex\skills\banana-box-skill\references\`（8 个类目文件夹，随 git 同步逐步积累）；也可指定自定义外部参考库（多项目共用）
3. 若是"项目制作"，用 project.py 创建/选择项目
4. 开始混合式引导（见下）

## 混合式引导协议

### 必填核心项（按顺序问，画面风格是重点）

1. **主体**：画面里是谁/什么
2. **动作**：主体在做什么
3. **场景**：在哪里
4. **情绪/叙事目的**：这一帧想传达什么
5. **画面风格（重点）**：必须明确——风格参考图或文字描述，不能跳过

### 动态展开 8 维度

画面构图、美术风格、角色动作、灯光氛围、环境氛围、场景参考、多人动作、人物比例。

根据核心项答案挑相关维度追问（如角色特写→重点问表情和灯光；宏大场景→重点问景别和氛围）。

### 每个维度的补充方式（先问参考图）

**每个维度（含必填核心项的场景、画面风格）都必须先询问："这个维度你有参考图吗？"** 不要等用户主动给。

- **有参考图** → 用 save_reference.py 存库并针对性识图：
  `python "C:\Users\admin\.codex\skills\banana-box-skill\scripts\save_reference.py" --image <图片> --dimension <维度> --name <标签名> --lib <参考库> --tags <标签>`
  识图失败（限流）时脚本自动切备用模型 `glm-5v-turbo`。识图结果如与用户判断不符，**以用户确认为准**，并修正参考库 .md。
- **无参考图** → 用户直接文字描述，记入该维度文本。

**针对性识图规范**：识图必须按维度聚焦，不得泛泛识别。各维度聚焦指令内置在 save_reference.py 中（如构图维度只看景别/角度/透视/视觉引导/画面平衡）。识图输出格式：`## 识图分析` + `## 提示词片段` 两个分节。若参考图与维度明显不符，提示用户换图或改文字描述。

## 输出协议

0. **自动检索知识库**：合成前，对已收集的每个维度（尤其画面构图/灯光氛围/美术风格/场景参考）调用 search_library.py 检索历史片段：
  `python "C:\Users\admin\.codex\skills\banana-box-skill\scripts\search_library.py" --lib <参考库> --dimension <维度>`
  把命中的历史片段合入该维度 `text`（标注"参考库经验：..."）。参考库越用越丰富，提示词质量随之提升。
1. 所有维度收集完后，把信息整理成需求 JSON：
```json
{
  "core": {"subject": "<完整角色描述，MJ 版用>", "subject_short": "<角色身份/数量/关系，形象以引用设定图为准，通用版用>", "action": "", "scene": "", "emotion": "", "style": ""},
  "dimensions": {
    "画面构图": {"text": "", "refs": ["<参考库>/画面构图/xx.md"]}
  }
}
```
2. 调用 `cinematic-prompt-engine` 生成单帧生图提示词：
   - 根据用户风格按该 skill 的流程处理：明确预设走预设路径；模糊 LOOK 先出 LOOK CARD 确认，再组装 L1-L9。
   - 单帧画面只生成一张静止画面提示词，不包含视频运镜、分镜或连续镜头指令。
   - **生图提示词默认不保存本地文件**：直接在对话中展示一个可复制的提示词代码块；只有用户明确说“保存本地”时才写文件。
3. **用户确认单帧提示词**（可修改后重试）
4. 确认后调用 `cinematic-video-prompt-engineer` 输出视频连续镜头提示词，输入包格式：
   - 【场景叙述】= 主体+动作+场景+情绪 写成叙事文字
   - 【画面风格】= 风格描述 + 参考库风格图 .md 描述
   - 【参考图清单】= 本次用到的参考图 .md 路径
   - 【镜头/时长目标】= 景别、角度、视频时长
   - 默认走"打磨模式"；需求仍模糊时自动降级"方向确认模式"
   - **必须实际调用**：不能只说明“接下来会生成”，要按 `cinematic-video-prompt-engineer` 的 SKILL.md 执行。
   - **如果未调用或未完成**：必须主动提醒用户“最后还需要调用 cinematic-video-prompt-engineer 生成视频提示词”。
5. **存档规则**：
   - 单帧生图提示词：默认只在对话中显示可复制文本，不写本地文件。
   - 视频提示词、参考图：可分别询问用户是否保存，用户要求保存时再写文件。

## 多帧模式（项目制作）

- 每完成一帧，用 project.py 记录：
  `python "C:\Users\admin\.codex\skills\banana-box-skill\scripts\project.py" add-frame <项目名> --name <帧名> --prompt <提示词文件>`
- 查看项目进度：`project.py list --project <项目名>`

## 注意事项

- 参考库路径用正斜杠或双反斜杠，避免 PowerShell 转义问题
- 识图脚本依赖 `LEIHUO_VISION_API_KEY`（已配置；脚本会自动从 Windows 用户环境变量读取，无需手动设置）
- cinematic-video-prompt-engineer 必须先安装（见 README）
- **知识库（references/）**：每个类目一个文件夹，永久积累参考图 + .md 分析，随 git 仓库同步备份；生成提示词时自动检索历史片段增强
- **角色描述策略**：用户通常已有角色设定图。通用版（GPT-image2）提示词中角色描述保持简化，生成时由用户添加引用图确定长相；MJ 版保留完整角色文字描述（MJ 不支持图引用，可用 --cref 角色参考）。
- **最后生成视频提示词时必须调用 `cinematic-video-prompt-engineer`**；如果该环节被跳过或未执行，必须主动提醒用户。
- **生成单帧画面时调用 `cinematic-prompt-engine`；生成视频连续镜头时调用 `cinematic-video-prompt-engineer`**。两个 skill 用途不同，不要混用。
