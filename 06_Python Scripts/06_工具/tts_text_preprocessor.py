"""
TTS 文本预处理器 - 情感标签与停顿控制
支持多模型标签映射、停顿校验、安全熔断
"""
import re
from typing import Dict, List, Tuple
from tts_tags_config import TTS_TAGS_MAP, PAUSE_TAG_CONFIG, DEFAULT_MODEL


class TextPreprocessor:
    """TTS 文本预处理引擎"""

    def __init__(self, model: str = DEFAULT_MODEL):
        """
        初始化预处理器

        Args:
            model: 模型类型 (s2_english/chinese/speech28)
        """
        self.model = model
        self.tags_map = TTS_TAGS_MAP.get(model, {})
        self.pause_config = PAUSE_TAG_CONFIG

    def validate_pause_duration(self, duration: float) -> bool:
        """
        校验停顿时长是否合法

        Args:
            duration: 停顿时长（秒）

        Returns:
            bool: 是否合法
        """
        min_dur = self.pause_config["min_duration"]
        max_dur = self.pause_config["max_duration"]
        return min_dur <= duration <= max_dur

    def process_pause_tags(self, text: str) -> Tuple[str, List[str]]:
        """
        处理停顿标签 <#x#>

        注意：Kitta AI API 不支持停顿标签，所以这里只做校验后移除

        Args:
            text: 原始文本

        Returns:
            (处理后文本, 错误列表)
        """
        errors = []
        warnings = []
        pattern = self.pause_config["pattern"]

        # 先校验所有停顿标签
        matches = re.finditer(pattern, text)
        for match in matches:
            duration_str = match.group(1)
            try:
                duration = float(duration_str)
                if not self.validate_pause_duration(duration):
                    errors.append(
                        f"停顿时长 {duration} 超出范围 "
                        f"[{self.pause_config['min_duration']}, {self.pause_config['max_duration']}]"
                    )
            except ValueError:
                errors.append(f"无效的停顿时长: {duration_str}")

        # 检测连续停顿标签
        consecutive_pauses = re.findall(r"(<#[\d.]+#>\s*){2,}", text)
        if len(consecutive_pauses) > self.pause_config["max_consecutive"]:
            warnings.append(
                f"检测到 {len(consecutive_pauses)} 处连续停顿标签，"
                f"超过最大允许值 {self.pause_config['max_consecutive']}"
            )

        # 移除所有停顿标签（Kitta AI 不支持）
        processed = re.sub(pattern, " ", text)

        # 规范化多余空格
        processed = re.sub(r"\s+", " ", processed)

        return processed, errors

    def process_emotion_tags(self, text: str) -> str:
        """
        处理情感标签（根据模型映射）

        Args:
            text: 原始文本

        Returns:
            处理后文本
        """
        # 这里假设用户使用统一的自定义标记，如 {emotion:angry}
        # 然后根据模型映射到对应格式

        # 示例：{emotion:angry} -> [angry] (s2_english)
        #       {emotion:开心} -> (开心) (chinese)

        pattern = r"\{emotion:(\w+)\}"

        def replace_emotion(match):
            emotion_key = match.group(1)
            if emotion_key in self.tags_map:
                return self.tags_map[emotion_key]
            else:
                # 如果找不到映射，保留原标签
                return match.group(0)

        return re.sub(pattern, replace_emotion, text)

    def clean_for_tts(self, text: str) -> str:
        """
        清理文本中的注释和多余空白

        Args:
            text: 原始文本

        Returns:
            清理后文本
        """
        # 移除括号注释（但保留情感标签）
        cleaned = re.sub(r"[\(\[（【][^情感]*?[\)\]）】]", "", text)
        # 规范化换行和空格
        cleaned = re.sub(r"\n+", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    def preprocess(self, text: str, strict_mode: bool = True) -> Dict:
        """
        完整预处理流程

        Args:
            text: 原始文本
            strict_mode: 严格模式（遇到错误时抛出异常）

        Returns:
            {
                "processed_text": str,
                "errors": List[str],
                "warnings": List[str]
            }
        """
        errors = []
        warnings = []

        # Step 1: 处理停顿标签
        text, pause_errors = self.process_pause_tags(text)
        errors.extend(pause_errors)

        # Step 2: 处理情感标签
        text = self.process_emotion_tags(text)

        # Step 3: 清理文本
        text = self.clean_for_tts(text)

        # 严格模式下遇到错误直接抛出
        if strict_mode and errors:
            raise ValueError(f"文本预处理失败: {'; '.join(errors)}")

        return {
            "processed_text": text,
            "errors": errors,
            "warnings": warnings
        }


# 便捷函数
def preprocess_text(text: str, model: str = DEFAULT_MODEL, strict: bool = True) -> str:
    """
    快速预处理文本

    Args:
        text: 原始文本
        model: 模型类型
        strict: 严格模式

    Returns:
        处理后文本
    """
    preprocessor = TextPreprocessor(model=model)
    result = preprocessor.preprocess(text, strict_mode=strict)
    return result["processed_text"]
