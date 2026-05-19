"""
Kitta AI TTS 重构版 - 支持情感标签与停顿控制
集成 TextPreprocessor 预处理引擎
"""
import requests
import os
import sys
import io
from typing import Optional
from tts_text_preprocessor import TextPreprocessor

# 修复 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Kitta AI API配置
API_TOKEN = "93a023b1b6baae2e6b5876705d666ffe4deee67a343fb3cf55a354ef9b24d2c6"
API_URL = "https://kittaai.com/api/open/tts"


class KittaTTS:
    """Kitta AI TTS 客户端"""

    def __init__(self, api_token: str = API_TOKEN, reference_id: Optional[str] = None):
        """
        初始化 TTS 客户端

        Args:
            api_token: API 令牌
            reference_id: 音色参考 ID
        """
        self.api_token = api_token
        self.reference_id = reference_id
        self.api_url = API_URL
        self.preprocessor = TextPreprocessor(model="s2_english")  # 默认使用 S2 英文系

    def set_model(self, model: str):
        """切换预处理器模型"""
        self.preprocessor = TextPreprocessor(model=model)

    def generate(
        self,
        text: str,
        output_path: str,
        version: str = "s1",
        format: str = "wav",
        strict_mode: bool = True
    ) -> bool:
        """
        生成语音

        Args:
            text: 原始文本（可包含情感标签和停顿标签）
            output_path: 输出文件路径
            version: API 版本 (s1/s2)
            format: 音频格式 (wav/mp3)
            strict_mode: 严格模式（遇到标签错误时抛出异常）

        Returns:
            bool: 是否成功
        """
        # Step 1: 预处理文本
        print(f'[INFO] 预处理文本...')
        try:
            result = self.preprocessor.preprocess(text, strict_mode=strict_mode)
            processed_text = result["processed_text"]

            if result["errors"]:
                print(f'[WARNING] 预处理发现错误: {result["errors"]}')
            if result["warnings"]:
                print(f'[WARNING] 预处理警告: {result["warnings"]}')

            print(f'[DEBUG] 原始文本长度: {len(text)} 字符')
            print(f'[DEBUG] 处理后长度: {len(processed_text)} 字符')

        except ValueError as e:
            print(f'[ERROR] 文本预处理失败: {e}')
            return False

        # Step 2: 构建 API 请求
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "text": processed_text,
            "version": version,
            "format": format
        }

        if self.reference_id:
            payload["reference_id"] = self.reference_id

        # Step 3: 调用 API
        print(f'[INFO] 正在生成语音...')
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=180
            )

            print(f'[DEBUG] 状态码: {response.status_code}')

            if response.status_code == 200:
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                with open(output_path, 'wb') as f:
                    f.write(response.content)

                file_size = os.path.getsize(output_path) / 1024  # KB
                print(f'[SUCCESS] 已保存: {output_path} ({file_size:.2f} KB)')
                return True
            else:
                print(f'[ERROR] API返回 {response.status_code}: {response.text}')
                return False

        except requests.exceptions.Timeout:
            print(f'[ERROR] 请求超时（180秒）')
            return False
        except Exception as e:
            print(f'[ERROR] 请求失败: {e}')
            return False


# 便捷函数
def generate_tts(
    text: str,
    output_path: str,
    reference_id: Optional[str] = None,
    version: str = "s1",
    format: str = "wav",
    model: str = "s2_english"
) -> bool:
    """
    快速生成 TTS

    Args:
        text: 原始文本
        output_path: 输出路径
        reference_id: 音色 ID
        version: API 版本
        format: 音频格式
        model: 预处理模型

    Returns:
        bool: 是否成功
    """
    client = KittaTTS(reference_id=reference_id)
    client.set_model(model)
    return client.generate(text, output_path, version=version, format=format)


if __name__ == "__main__":
    # 测试用例
    test_text = """
    {emotion:excited}大家好！<#0.5#>今天我要给大家介绍一本神奇的书。

    {emotion:sighing}这本书啊<#1.0#>真的让我感慨万千。

    {emotion:laughing}你们猜猜看<#0.3#>这只鸟为什么会动？<#0.8#>

    因为这是商务印书馆的物理结构设计<#0.5#>不是特效！
    """

    output_dir = r'E:\1.work\douyin\1.shuixing\06_Python Scripts\06_工具\test_output'
    output_path = os.path.join(output_dir, 'test_emotion_tags.wav')

    print("=" * 60)
    print("TTS 情感标签测试")
    print("=" * 60)

    success = generate_tts(
        text=test_text,
        output_path=output_path,
        reference_id="bc9fced8-266a-47fd-b86f-0eb0c9b71d68",
        version="s1",
        format="wav",
        model="s2_english"
    )

    if success:
        print("\n[完成] 测试成功！")
    else:
        print("\n[失败] 测试失败，请检查日志")
