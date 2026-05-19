---
name: gpt-sovits-clone
description: "使用 GPT-SoVITS 复刻音频音色，训练专属模型。示例："复刻这个声音", "训练音色模型", "克隆声音", "用这个声音配音", "音频复刻"
---

# GPT-SoVITS 音频复刻工具

使用参考音频训练专属音色模型，之后可以用这个音色进行配音。

**本 skill 会启动完整的训练流程，需要 1-2 小时完成。**

## 功能

| 功能 | 说明 |
|------|------|
| 音色克隆 | 使用 3-10 秒参考音频训练专属模型 |
| 自动切片 | 自动将长音频切分为训练片段 |
| 自动训练 | 自动执行 S1 (GPT) 和 S2 (SoVITS) 完整训练流程 |

## 工作流程

```
参考音频 → 切片 → 文本处理 → 特征提取 → S1训练 → S2训练 → 专属模型
```

1. **音频切片** - 将参考音频切分为 3-10 秒的片段
2. **文本对应** - 每个切片配上对应文字（用户需提供）
3. **特征提取** - 提取 Hubert 和语义特征
4. **S1 训练** - 训练 GPT 模型（约 15 轮）
5. **S2 训练** - 训练 SoVITS 模型（约 8 轮）
6. **配音使用** - 使用训练好的模型进行语音合成

## 代码位置

`E:\1.work\douyin\1.shuixing\03_Assets_全局库\GPT-SoVITS\gpt_sovits_clone.py`

## 基本用法

### 方式一：提供音频和文字（推荐）

```bash
cd "E:/1.work/douyin/1.shuixing/03_Assets_全局库/GPT-SoVITS"
./venv/Scripts/python.exe gpt_sovits_clone.py \
    --audio "00_InBox_收件箱/我的声音.wav" \
    --text "这是一段示例文字，对应你的音频内容" \
    --name "my_voice"
```

### 方式二：只提供音频（需要手动编辑文本）

```bash
cd "E:/1.work/douyin/1.shuixing/03_Assets_全局库/GPT-SoVITS"
./venv/Scripts/python.exe gpt_sovits_clone.py \
    --audio "00_InBox_收件箱/我的声音.wav" \
    --name "my_voice"
```

脚本会自动创建文本文件，提示你手动编辑填入对应文字。

## 参数说明

| 参数 | 简写 | 说明 | 必填 | 默认值 |
|------|------|------|------|--------|
| --audio | -a | 参考音频路径 | 是 | - |
| --text | -t | 音频对应的文字 | 否 | 需手动编辑 |
| --name | -n | 音色名称 | 否 | voice_时间戳 |
| --s1_epochs | -e1 | GPT 训练轮数 | 否 | 15 |
| --s2_epochs | -e2 | SoVITS 训练轮数 | 否 | 8 |

## 参考音频要求

| 要求 | 说明 |
|------|------|
| 时长 | 3-10 秒（太短效果差，太长没必要） |
| 格式 | wav, mp3, m4a 等常见格式 |
| 质量 | 清晰无噪音，最好是干净的人声 |
| 内容 | 尽量是普通话或目标语种 |
| 情绪 | 平静自然即可 |

## 训练时间参考

| 阶段 | 轮数 | 预计时间 |
|------|------|----------|
| S1 (GPT) | 15 轮 | ~30-60 分钟 |
| S2 (SoVITS) | 8 轮 | ~30-60 分钟 |
| **总计** | - | **约 1-2 小时** |

（时间取决于硬件配置和音频片段数量）

## 输出位置

训练完成后，模型保存在：

```
GPT-SoVITS/
├── output/
│   ├── logs_s1_{voice_name}/ckpt/    # GPT 模型
│   │   └── epoch=14-step=xxx.ckpt     # 最佳模型
│   └── logs_s2_{voice_name}/          # SoVITS 日志
├── SoVITS_weights_v3/
│   └── {voice_name}_s2Gv3_e{xx}.pth   # SoVITS 模型
└── output/aligned/{voice_name}/       # 预处理数据
```

## 训练完成后使用

训练完成后，更新 `weight.json` 配置：

```json
{
  "GPT": {
    "v2": "output/logs_s1_{voice_name}/ckpt/epoch=14-step=xxx.ckpt"
  },
  "SoVITS": {
    "v2": "SoVITS_weights_v3/{voice_name}_s2Gv3_e8.pth"
  }
}
```

然后重启推理服务即可使用新音色。

## 完整示例

### 1. 准备参考音频

将你的参考音频放入收件箱：
```
00_InBox_收件箱/我的声音.wav
```

### 2. 执行复刻

```bash
cd "E:/1.work/douyin/1.shuixing/03_Assets_全局库/GPT-SoVITS"
./venv/Scripts/python.exe gpt_sovits_clone.py \
    -a "00_InBox_收件箱/我的声音.wav" \
    -t "今天天气真好，我们一起去公园散步吧" \
    -n "水星解说员" \
    -e1 15 \
    -e2 8
```

### 3. 等待训练完成

脚本会显示进度，训练期间可以去做其他工作。

### 4. 使用新音色配音

训练完成后，使用 gpt-sovits-tts skill 进行配音：

```
帮我把这段话转成语音，用水星解说员的音色：
"欢迎来到水星艺术馆，这里有你想要的一切。"
```

## 注意事项

1. **训练时间** - 完整训练需要 1-2 小时，请确保电脑不关机
2. **音频质量** - 参考音频质量直接影响克隆效果
3. **文字对应** - 每个切片都需要对应正确的文字，这是最重要的环节
4. **GPU 显存** - 默认配置需要约 4GB 显存，如不足请减小 batch_size
5. **训练中断** - 如训练中断，可以从最近的 checkpoint 继续

## 故障排除

### 切片失败
- 检查音频格式是否支持
- 尝试使用格式工厂转换为 wav 格式

### 文本编辑
- 打开生成的 `2-name2text.txt` 文件
- 每行格式：`文件名.wav\t对应文字\t`
- 确保每个切片都有对应的文字

### 训练显存不足
- 修改配置中的 `batch_size` 为 1 或 2
- 修改 `lora_rank` 为 8

### 模型加载失败
- 检查 `weight.json` 路径是否正确
- 确保使用的是完整路径

## 自动规则

**当用户请求复刻音色/克隆声音时，自动执行以下步骤：**

1. 询问用户提供参考音频文件路径
2. 询问音频对应的文字内容（很重要）
3. 执行 `gpt_sovits_clone.py` 脚本
4. 告知用户预计训练时间
5. 训练完成后提醒用户更新配置并重启推理服务
