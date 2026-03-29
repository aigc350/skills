# Kling (可灵) Platform Template

## 平台特点

- **国产优势**：中文 Prompt 支持好
- **亚洲面孔**：东亚人特征识别准确
- **风格多样**：武侠、古风、现代表现都好
- **动作丰富**：复杂动作生成能力强

## Prompt 模板

```
[主体描述]，[动作描述]，[场景描述]，[镜头规格]，[光照描述]，[风格描述]

镜头：[类型] [角度] [运动]
时长：[秒数]秒
风格：[电影感/写实/古风/武侠]
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
  atmosphere: dark
```

**输出 (Kling Prompt)**:
```
30岁左右男性，短发凌乱，穿磨损皮夹克，冷漠表情，站在废弃仓库中央。目光直视前方，神情冷漠自信。

镜头：全景仰拍，缓慢推进
光照：单束追光，低角度照射
时长：5秒
风格：电影感，暗调，悬疑氛围
```

## 负面 Prompt 模板

```
卡通，动漫，低质量，面部扭曲，额外肢体，水印，文字，标志，高饱和度，美颜滤镜，过度磨皮，西方脸孔，欧美风格
```

## 参数规格

| 参数 | 值 |
|------|-----|
| 最大 Prompt 长度 | 250 字符 |
| 默认时长 | 5-10 秒 |
| 推荐分辨率 | 1080x1920 (竖版) |
| 运动强度 | medium 到 high |

## 优化建议

1. **中文优先**：Kling 对中文理解更好
2. **人脸描述**：强调东亚人特征
3. **动作详细**：复杂动作描述清晰
4. **风格标签**：加入 "电影感"、"写实" 等
