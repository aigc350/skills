# Sora Platform Template

## 平台特点

- **长视频能力**：最长 60 秒
- **复杂场景**：支持多角色、多场景
- **剧情性强**：适合电影级内容
- **时间线控制**：支持场景连续性描述

## Prompt 模板

```
Cinematic scene: [场景设定]
[主体描述]
[环境细节]
[镜头运动]
[风格标签]
[氛围描述]

Camera: [镜头规格]
Lighting: [光照描述]
Duration: [时长]
Style: [电影/电视剧风格]
```

## Prompt 示例

**输入 (shot_spec)**:
```yaml
subject:
  type: character
  character_id: zhang_san
  expression: cold_smile
  pose: standing
visual_intent:
  shot_type: medium
  camera_angle: low_angle
  camera_movement: dolly_in
  style: cinematic
  lighting: low_key
  atmosphere: tense
environment:
  location_id: warehouse
```

**输出 (Sora Prompt)**:
```
Cinematic scene: A dimly lit abandoned warehouse with rusty metal structures and scattered debris. A man in his 30s with short messy hair, wearing a worn leather jacket, stands in the center of the frame. Cold, calculating expression with an emotionless smile. Single dramatic spotlight from above creates deep shadows on his face. Low angle camera slowly pushes in towards the character.

Camera: Medium shot, low angle, slow dolly in movement
Lighting: Low-key dramatic lighting with high contrast shadows
Duration: 5 seconds
Style: Film noir, cinematic, 35mm anamorphic lens
```

## 负面 Prompt 模板

```
anime, cartoon, low quality, distorted face, extra limbs, watermark, text, signature, logo, bright lighting, cheerful, happy, smiling, smooth skin, beauty filter, oversaturated, amateur video, webcam quality, phone recording
```

## 参数规格

| 参数 | 值 |
|------|-----|
| 最大 Prompt 长度 | 400 字符 |
| 默认时长 | 5-10 秒 |
| 推荐分辨率 | 1920x1080 |
| 运动强度 | medium 到 high |

## 优化建议

1. **场景设定前缀**：使用 "Cinematic scene:" 开头
2. **时间描述**：加入 "continuous shot" 表示长镜头
3. **风格标签**：加入 "film noir", "cinematic" 等标签
4. **避免**：快速切换、复杂特效、多人同步动作
