---
name: gpt-sovits-tts
description: "使用 GPT-SoVITS 进行文字转语音。示例：\"帮我把这段话转成语音\", \"TTS\", \"文字转语音\", \"配音\", \"生成音频\""
---

# GPT-SoVITS 文字转语音工具

使用本地的 GPT-SoVITS 模型进行文字转语音合成。

**本 skill 只做一件事：文字转语音。不负责其他任何任务。**

## 功能

| 功能 | 说明 |
|------|------|
| 文字转语音 | 将文本转换为语音 |
| 参考音色 | 使用参考音频控制音色 |
| 语速调节 | 可调整语速快慢 |
| 多语种支持 | 支持中文、英文、日文等多种语种 |

## 前提条件

**推理服务必须先启动**：

```bash
cd "E:/1.work/douyin/1.shuixing/03_Assets_全局库/GPT-SoVITS"
./venv/Scripts/python.exe GPT_SoVITS/inference_webui.py
```

服务地址: http://127.0.0.1:9872

## 代码位置

`E:\1.work\douyin\1.shuixing\03_Assets_全局库\GPT-SoVITS\gpt_sovits_tts.py`

## 基本用法

### 命令行方式

```bash
cd "E:/1.work/douyin/1.shuixing/03_Assets_全局库/GPT-SoVITS"
./venv/Scripts/python.exe gpt_sovits_tts.py --text "要转换的文字"
```

### 参数说明

| 参数 | 简写 | 说明 | 必填 | 默认值 |
|------|------|------|------|--------|
| --text | -t | 要转换的文本 | 是 | - |
| --ref_audio | -r | 参考音频路径 | 否 | 训练数据音色 |
| --ref_text | -rt | 参考音频文本 | 否 | 自动填充 |
| --prompt_lang | -pl | 参考音频语种 | 否 | 中文 |
| --text_lang | -tl | 待合成语种 | 否 | 中文 |
| --output | -o | 输出文件路径 | 否 | 自动生成 |
| --speed | -s | 语速 | 否 | 1.0 |
| --top_k | -k | top_k | 否 | 15 |
| --top_p | -p | top_p | 否 | 1.0 |
| --temperature | -temp | temperature | 否 | 1.0 |
| --steps | -st | 采样步数 | 否 | 32 |
| --cut | -c | 切割方式 | 否 | 凑四句一切 |
| --pause | 无 | 句间停顿秒数 | 否 | 0.3 |

## 使用示例

### 1. 最简单用法（使用默认训练音色）

```bash
./venv/Scripts/python.exe gpt_sovits_tts.py --text "今天天气真好，我们一起去公园散步吧。"
```

### 2. 指定语种

```bash
./venv/Scripts/python.exe gpt_sovits_tts.py --text "Hello, how are you?" --text_lang "英文"
```

### 3. 调整语速

```bash
./venv/Scripts/python.exe gpt_sovits_tts.py --text "这是一段快速播报的语音" --speed 1.5
```

### 4. 使用自定义参考音频

```bash
./venv/Scripts/python.exe gpt_sovits_tts.py \
    --text "请用这个音色朗读这段文字" \
    --ref_audio "E:/1.work/douyin/1.shuixing/03_Assets_全局库/GPT-SoVITS/output/slicer_opt/douyin_vocal_01.wav_seg0001.wav" \
    --ref_text "他被吓得心脏猛的一颤，大脑随即高速运转"
```

### 5. 完整参数示例

```bash
./venv/Scripts/python.exe gpt_sovits_tts.py \
    --text "欢迎来到水星艺术馆" \
    --text_lang "中文" \
    --speed 1.0 \
    --top_k 15 \
    --top_p 1.0 \
    --steps 32 \
    --cut "凑四句一切" \
    --pause 0.3 \
    --output "E:/1.work/douyin/1.shuixing/output/水星艺术馆_欢迎.wav"
```

## 语种选项

| 语种 | 说明 |
|------|------|
| 中文 | 简体中文 |
| 英文 | 英语 |
| 日文 | 日语 |
| 粤语 | 粤语 |
| 韩文 | 韩语 |
| 中英混合 | 中英文混合 |
| 日英混合 | 日英文混合 |
| 粤英混合 | 粤英文混合 |
| 韩英混合 | 韩英文混合 |
| 多语种混合 | 多种语言混合 |

## 切割方式选项

| 方式 | 说明 |
|------|------|
| 凑四句一切 | 每4句切一次（默认） |
| 凑50字一切 | 每50字切一次 |
| 不切 | 不切割 |
| 按中文句号。切 | 按中文句号切割 |
| 按英文句号.切 | 按英文句号切割 |
| 按标点符号切 | 按所有标点切割 |

## 输出说明

- 输出格式：WAV 音频文件
- 输出目录：`E:/1.work/douyin/1.shuixing/03_Assets_全局库/GPT-SoVITS/output/`
- 文件命名：`tts_YYYYMMDD_HHMMSS.wav`（或自定义路径）

## 训练数据参考

项目已训练好的模型使用 douyin_vocal 数据集。训练数据切分音频位于：

```
E:/1.work/douyin/1.shuixing/03_Assets_全局库/GPT-SoVITS/output/slicer_opt/
```

可用参考音频示例：

| 文件名 | 对应文本 |
|--------|----------|
| douyin_vocal_01.wav_seg0000.wav | 只因想试试刚到的新货究竟猛不猛,独裁总统竟瞄准了自己的卫兵. |
| douyin_vocal_01.wav_seg0001.wav | 他被吓得心脏猛的一颤,大脑随即高速运转 |
| douyin_vocal_01.wav_seg0002.wav | 只怕自己不死,也得脱层皮 |

## 依赖

无需额外安装（已在项目中包含）：
```bash
pip install gradio_client
```

## 注意事项

1. **服务状态**：使用前确保推理服务已启动（http://127.0.0.1:9872）
2. **参考音频**：如果不提供参考音频，将使用训练数据的第一段作为音色参考
3. **语种匹配**：参考音频语种和待合成语种尽量匹配效果更好
4. **采样步数**：步数越高音质越好但速度越慢，建议 32
5. **输出覆盖**：同名输出文件会被覆盖

## 故障排除

### 服务未启动

如果报错 `Connection refused`，需要先启动推理服务：

```bash
cd "E:/1.work/douyin/1.shuixing/03_Assets_全局库/GPT-SoVITS"
./venv/Scripts/python.exe GPT_SoVITS/inference_webui.py
```

### 端口被占用

如果 9872 端口被占用，检查是否有其他进程：

```bash
netstat -ano | grep 9872
```

### 模型加载失败

确保 `weight.json` 配置正确，推理服务已正常加载模型。

## 自动规则

**当用户请求文字转语音时，自动执行以下步骤：**

1. 检查推理服务是否运行（端口 9872）
2. 如果服务未运行，自动启动服务
3. 使用 `gpt_sovits_tts.py` 执行转换
4. 输出完成后告知用户文件路径
