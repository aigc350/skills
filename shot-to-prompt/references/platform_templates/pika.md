# Pika Platform Template

## 平台特点

- **快速生成**：几秒内完成
- **动作流畅**：角色动作自然
- **简洁风格**：适合短片段
- **社区活跃**：模板丰富

## Prompt 模板

```
[主体]: [描述]
[动作]: [动作描述]
[场景]: [环境]
[风格]: [风格标签]
```

## Prompt 示例

**输入 (shot_spec)**:
```yaml
subject:
  type: character
  character_id: zhang_san
  expression: angry
  pose: gesturing
visual_intent:
  shot_type: close_up
  camera_movement: static
  style: realistic
  atmosphere: tense
```

**输出 (Pika Prompt)**:
```
Man in 30s gesturing angrily, close-up shot. Tense atmosphere, dark mood.

Action: Pointing finger, frustrated gestures
Scene: Dark room
Style: Realistic, dramatic
```

## 负面 Prompt 模板

```
cartoon, anime, illustration, low quality, distorted, watermark, text, logo, blurry, grainy
```

## 参数规格

| 参数 | 值 |
|------|-----|
| 最大 Prompt 长度 | 200 字符 |
| 默认时长 | 3-5 秒 |
| 推荐分辨率 | 768x768 |
| 运动强度 | medium |

## 优化建议

1. **简洁为主**：避免过长描述
2. **动作明确**：Pika 对动作描述响应好
3. **短片段**：每次生成 5 秒以内最佳
4. **避免复杂**：不推荐复杂场景和多人
