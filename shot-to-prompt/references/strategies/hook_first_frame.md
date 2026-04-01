# Hook First Frame Strategy - 首帧钩子策略
# 决定视频开头第一帧的设计，激发观众继续观看的欲望

## 核心理念

第一帧 = 注意力锚点
- 必须在前 3 秒抓住观众
- 制造悬念或冲突感
- 留下"为什么"的疑问

## 钩子类型

### 1. 情绪冲击型
```
描述：强烈情绪表情的第一帧
适用：爽点、打脸、身份揭晓
示例：
- 特写：主角嘴角微微上扬——"他终于要出手了"
- 特写：配角的惊恐表情——"发生了什么"
```

### 2. 悬念型
```
描述：制造未解之谜
适用：剧情反转、身份揭秘
示例：
- 逆光剪影："这个人的真实身份是..."
- 手机屏幕特写："来电显示：沈家总部"
```

### 3. 冲突型
```
描述：展示对抗/对峙场面
适用：打脸、装逼、翻盘
示例：
- 过肩镜头：主角平静直视镜头，配角在身后嚣张
- 正面特写：对手脸色突变
```

### 4. 动作中断型
```
描述：动作进行到一半，戛然而止
适用：制造紧张感
示例：
- 手即将碰到门把手
- 酒杯即将送到嘴边
```

### 5. 反差型
```
描述：预期与现实的反差
适用：反转、打脸
示例：
- 全场哄笑 → 突然安静
- 主角低头 → 缓缓抬起，眼神锐利
```

## 应用规则

1. **识别 shot_spec 中的 intent.narrative_function**
   - `climax` → 优先使用情绪冲击型
   - `reveal` → 优先使用悬念型
   - `conflict` → 优先使用冲突型

2. **首帧 Prompt 注入模板**
```
[HOOK FRAME]
视觉焦点：{subject_focus}
情绪强度：{emotion_intensity}
悬念元素：{suspense_element}
第一帧描述：{frame_description}
```

3. **Shot 组合策略**
   - Shot 1（首帧）= Hook
   - Shot 2-3 = 展开
   - Shot N = 高潮/反转

## 情绪强度映射

| 情绪 | 强度 | 首帧设计 |
|-----|------|---------|
| calm | low | 平静表面，暗流涌动 |
| confidence | medium | 胸有成竹的微笑 |
| dominance | high | 俯视角度，压迫感 |
| humiliation | high | 低头或背影，压抑 |
| shock | extreme | 表情凝固，震惊 |
| fear | extreme | 冷汗、颤抖 |

## 示例

**输入 (shot_spec):**
```yaml
intent:
  narrative_function: climax
visual_intent:
  emotion: dominance
  shot_type: close_up
```

**输出 (Hook Prompt):**
```
[HOOK FRAME]
Extreme close-up on character's eyes, cold and calculating gaze.
Intensity: Maximum - the moment before dominance is revealed.
Suspense: Viewer senses something is about to happen.
Frame: Eyes fill 80% of screen, slight shadow across face,
       mouth barely visible with subtle smirk.
       The moment before the tables turn.
```
