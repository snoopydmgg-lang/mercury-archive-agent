# Kitta AI TTS API Reference

## 基础信息
- **Endpoint**: `https://kittaai.com/api/open/tts`
- **Method**: `POST`
- **Auth**: `Authorization: Bearer YOUR_API_TOKEN`

## 请求头 (Headers)
| Key | Value | Description |
| :--- | :--- | :--- |
| Content-Type | `application/json` 或 `application/msgpack` | 推荐使用 JSON |
| Authorization | `Bearer YOUR_API_TOKEN` | 必填，API Key |

## 请求参数 (Payload)
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `reference_id` | string | 是 | - | 声音模型 ID |
| `text` | string | 是 | - | 待转换文本 |
| `speed` | number | 否 | `1` | 语速 (0.5-2.0) |
| `volume` | number | 否 | `0` | 音量 (-20-20) |
| `version` | string | 否 | `v1` | 版本：`v1`, `v2`, `s1`, `v3-turbo`, `v3-hd` |
| `format` | string | 否 | `mp3` | 格式：`mp3`, `wav`, `pcm` |
| `emotion` | string | 否 | `auto` | 情绪 (仅 V3)：`happy`, `sad`, `angry`, `fearful`, `disgusted`, `surprised`, `calm`, `auto` |
| `language` | string | 否 | `auto` | 语言增强 (仅 V3)：`auto`, `zh`, `en` |
| `cache` | boolean | 否 | `false` | `false` 返回音频流；`true` 返回 JSON URL |

## 版本说明
- **传统版本**: `v1`, `v2`, `s1` (推荐 `s1` 用于基础合成)
- **V3 版本**: `v3-turbo`, `v3-hd` (支持情绪控制和语言增强)

## 响应数据 (Response)

### 1. 流式响应 (cache=false)
- **Status**: `200 OK`
- **Content-Type**: `audio/mpeg` (或其他格式)
- **Body**: 二进制音频数据

### 2. URL 响应 (cache=true)
- **Status**: `200 OK`
- **Content-Type**: `application/json`
```json
{
  "success": true,
  "audio_url": "https://...",
  "format": "mp3",
  "characters_used": 100,
  "quota_remaining": 5000
}
```

### 3. 错误响应
```json
{
  "error": "错误提示信息"
}
```

## 快速调用示例 (CLI)

### 基础调用 (s1 版本)
```bash
curl -X POST https://kittaai.com/api/open/tts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -d '{
    "reference_id": "YOUR_MODEL_ID",
    "text": "你好，世界",
    "version": "s1",
    "cache": false
  }' \
  --output output.mp3
```

### V3 高级调用 (带情绪)
```bash
curl -X POST https://kittaai.com/api/open/tts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -d '{
    "reference_id": "YOUR_MODEL_ID",
    "text": "这是一段平静的陈述。",
    "version": "v3-hd",
    "emotion": "calm",
    "language": "zh",
    "cache": false
  }' \
  --output output_v3.mp3
```