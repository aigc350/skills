# switch 命令

切换当前活动小说。

## 命令格式

```
/novel-creator switch <ID>
```

| 参数 | 说明 |
|------|------|
| `<ID>` | 目标小说的 ID（必填） |

## 执行步骤

1. 读取 `novel.config.md`
2. 验证目标小说 ID 是否存在
3. 更新 `当前小说` 字段
4. 输出切换结果

## 输出格式

```
已切换到: 星际迷航 (scifi_002)
```

## 错误处理

- ID 不存在：提示可用的小说 ID 列表
- 配置文件不存在：提示先使用 init 初始化

## 示例

```
/novel-creator switch scifi_002
/novel-creator switch xuanhuan_001
```