# Runway Platform Template

## 平台特点

- **电影感强**：Gen-3 Alpha 高质量输出
- **镜头控制**：支持丰富镜头语言
- **风格多样**：从写实到风格化
- **运动流畅**：人物动作自然

## Prompt 模板

```
[主体描述], [动作/表情]
[环境设定]
[镜头规格]: [角度], [运动]
[风格]: [电影/纪录片/风格化]
[光照]: [光照描述]

Shot on RED camera, cinematic color grading
```

## Prompt 示例

**输入 (shot_spec)**:
```yaml
subject:
  type: character
  character_id: zhang_san
  expression: cold_smile
  pose: walking
visual_intent:
  shot_type: medium
  camera_angle: eye_level
  camera_movement: tracking
  style: cinematic
  lighting: natural
```

**输出 (Runway Prompt)**:
```
A man in his 30s with short messy hair, wearing a worn leather jacket, walks confidently through a dimly lit corridor. Cold, calculating expression with an emotionless smile. Natural lighting from a nearby window creates soft shadows.

Medium shot, eye level, tracking shot following the character.
Style: Cinematic, film-quality
Lighting: Natural, soft shadows

Shot on RED camera with cinematic color grading
```

## 负面 Prompt 模板

```
anime, cartoon, illustration, painting, drawing, low quality, distorted face, extra limbs, black and white, sepia, watermark, text, logo, smooth skin, beauty filter, oversaturated, amateur
```

## 参数规格

| 参数 | 值 |
|------|-----|
| 最大 Prompt 长度 | 300 字符 |
| 默认时长 | 4-10 秒 |
| 推荐分辨率 | 1280x720 |
| 运动强度 | medium |

## 优化建议

1. **镜头语言**：使用专业镜头术语
2. **设备标签**：加入 "Shot on RED camera"
3. **色调描述**：加入色彩风格描述
4. **保持简洁**：Runway 对过长 Prompt 容忍度较低
