---
name: shot-to-prompt
description: "Convert shot_spec to AI video generation prompts. Use when user wants to generate video prompts for Sora, Runway, Pika, Kling, etc. Commands: run/status/export."
---

# shot-to-prompt

将 shot_spec 转换为 AI 视频生成模型的 Prompt，建立机器可执行语言到人类可读 Prompt 的桥梁。

## 快速开始

```
/shot-to-prompt run    # 执行转换（首次运行自动初始化）
```

---

## run 命令

执行 `/shot-to-prompt run` 时，按以下步骤执行：

### Step 1: 读取配置

读取 `novel.config.md` 获取：
- `current_novel_id` - 当前小说ID
- shot_spec 源目录：`novels/{novel_id}/output/visual/`

### Step 2: 初始化目录

确保以下目录存在：

```
novels/{novel_id}/
├── output/
│   └── gen_prompts/
│       └── {chapter_id}/
│           ├── shots/
│           │   └── gen_prompt.yaml
│           └── full_gen_prompt.yaml
└── gen_prompt/
    └── memory/
```

### Step 3: 加载平台模板

根据目标平台加载对应的 Prompt 模板：
- `sora` - OpenAI Sora
- `runway` - Runway Gen-3
- `pika` - Pika Labs
- `kling` - 快手可灵

### Step 4: 执行转换 Pipeline

对每个待处理 shot_spec 执行：

1. **parse_shot_spec** - 解析 shot_spec 结构
2. **build_shot_prompt** - 为每个镜头构建 Prompt
3. **optimize_prompt** - 优化 Prompt 适配目标平台
4. **validate_prompts** - 校验 Prompt 格式
5. **assemble_chapter_prompts** - 组装章节级联 Prompts
6. **export** - 导出到 output 目录

---

## 架构概览

### 核心模块

| Module | 类型 | 职责 |
|--------|------|------|
| prompt_builder | Builder | 将 shot_spec 转换为结构化 Prompt |
| prompt_optimizer | Optimizer | 针对不同平台优化 Prompt |

### 设计原则

1. **Platform-Agnostic Core** - 核心逻辑平台无关
2. **Platform-Specific Output** - 输出适配目标平台
3. **Deterministic** - 相同输入产生相同输出
4. **Composable** - 支持镜头级和章节级 Prompt
