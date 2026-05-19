"""
TTS 情感标签配置字典
支持多模型标签映射与停顿控制
"""

# 标签映射字典 - 按模型分类
TTS_TAGS_MAP = {
    # 模型 A: S2 英文系
    "s2_english": {
        "angry": "[angry]",
        "sad": "[sad]",
        "excited": "[excited]",
        "laughing": "[laughing]",
        "sighing": "[sighing]",
        "pause": "[pause]"
    },

    # 模型 B: 中文系
    "chinese": {
        "开心": "(开心)",
        "生气": "(生气)",
        "讽刺": "(讽刺)",
        "语速加快": "(语速加快)",
        "大声": "(大声)"
    },

    # 模型 C: Speech-2.8 拟声系
    "speech28": {
        "laughs": "[laughs]",
        "inhale": "[inhale]",
        "exhale": "[exhale]",
        "gasps": "[gasps]",
        "lip_smacking": "[lip-smacking]"
    }
}

# 停顿标签配置
PAUSE_TAG_CONFIG = {
    "min_duration": 0.01,
    "max_duration": 98.99,
    "pattern": r"<#([\d.]+)#>",  # 匹配 <#1.5#> 格式
    "max_consecutive": 3  # 最多连续停顿次数
}

# 默认模型选择
DEFAULT_MODEL = "s2_english"
