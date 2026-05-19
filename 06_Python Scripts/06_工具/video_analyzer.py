"""
视频分析中间件
功能：
1. 使用 OpenCV 提取视频关键帧
2. 使用 Whisper 提取音频文本
3. 打包数据并调用大模型进行多模态推理
"""

import os
import sys
import io
import json
import argparse
import base64
from pathlib import Path
from datetime import datetime

# 设置 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 依赖导入 (延迟到具体方法中)


class VideoAnalyzer:
    """视频分析中间件类"""

    def __init__(self, video_path: str, output_dir: str = None):
        """
        初始化分析器

        Args:
            video_path: 视频文件路径
            output_dir: 输出目录，默认为视频同目录下的 analysis_result
        """
        import tempfile
        import shutil

        self.video_path = video_path
        self.video_name = Path(video_path).stem

        if output_dir is None:
            self.output_dir = Path(video_path).parent / f"{self.video_name}_analysis"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 关键帧输出目录 - 使用临时目录避免中文路径问题
        self._temp_frames_dir = Path(tempfile.gettempdir()) / f"video_analyzer_frames_{id(self)}"
        self._temp_frames_dir.mkdir(parents=True, exist_ok=True)

        self.frames_dir = self.output_dir / "frames"
        self.frames_dir.mkdir(exist_ok=True)

        # 音频输出路径
        self.audio_path = self.output_dir / "audio.wav"

        # 转换为绝对路径以避免中文路径问题
        self._video_path_abs = str(Path(video_path).resolve())
        self._frames_dir_abs = str(self._temp_frames_dir.resolve())
        self._output_dir_abs = str(self.output_dir.resolve())

    def extract_keyframes(self, max_frames: int = 10, interval: int = None) -> list:
        """
        提取视频关键帧

        Args:
            max_frames: 最大提取帧数
            interval: 固定间隔提取（帧数），如果为None则使用场景检测

        Returns:
            提取的帧路径列表
        """
        # 延迟导入 cv2
        try:
            import cv2
        except ImportError:
            print("[错误] 请安装 opencv-python: pip install opencv-python")
            return []

        print(f"[INFO] 开始提取关键帧: {self.video_path}")

        cap = cv2.VideoCapture(self._video_path_abs)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        print(f"[INFO] 视频信息: FPS={fps:.2f}, 总帧数={total_frames}, 时长={duration:.2f}秒")

        frame_paths = []

        if interval is None:
            # 智能关键帧提取：均匀分布
            step = max(1, total_frames // max_frames)
            frame_count = 0

            while frame_count < total_frames and len(frame_paths) < max_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
                ret, frame = cap.read()

                if not ret:
                    break

                # 保存帧
                frame_name = f"frame_{len(frame_paths):03d}_{int(frame_count/fps):.1f}s.jpg"
                frame_path = Path(self._frames_dir_abs) / frame_name
                success = cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if success:
                    frame_paths.append(frame_path)

                frame_count += step
        else:
            # 固定间隔提取
            frame_count = 0
            while frame_count < total_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
                ret, frame = cap.read()

                if not ret:
                    break

                frame_name = f"frame_{len(frame_paths):03d}_{int(frame_count/fps):.1f}s.jpg"
                frame_path = Path(self._frames_dir_abs) / frame_name
                success = cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if success:
                    frame_paths.append(frame_path)

                frame_count += interval

                if len(frame_paths) >= max_frames:
                    break

        cap.release()

        # 将临时目录的文件复制到目标目录
        import shutil
        final_frame_paths = []
        for temp_path in frame_paths:
            final_path = self.frames_dir / temp_path.name
            shutil.copy2(temp_path, final_path)
            final_frame_paths.append(final_path)

        # 清理临时目录
        shutil.rmtree(self._temp_frames_dir, ignore_errors=True)

        print(f"[INFO] 已提取 {len(final_frame_paths)} 张关键帧到: {self.frames_dir}")
        return final_frame_paths

    def extract_audio(self) -> str:
        """
        从视频中提取音频

        Returns:
            音频文件路径
        """
        # 延迟导入 moviepy (v2.x 版本结构不同)
        try:
            import moviepy as mp
        except ImportError:
            print("[错误] 请安装 moviepy: pip install moviepy")
            return None

        # 设置 FFmpeg 路径
        try:
            import imageio_ffmpeg
            import os
            os.environ['FFMPEG_BINARY'] = imageio_ffmpeg.get_ffmpeg_exe()
        except:
            pass

        print(f"[INFO] 提取音频: {self.video_path}")

        try:
            video = mp.VideoFileClip(self._video_path_abs)
            audio = video.audio
            audio_path_abs = Path(self._output_dir_abs) / "audio.wav"
            audio.write_audiofile(str(audio_path_abs), codec='pcm_s16le', logger=None)
            video.close()
            audio.close()
            print(f"[INFO] 音频已提取到: {audio_path_abs}")
            return str(audio_path_abs)
        except Exception as e:
            print(f"[警告] 音频提取失败: {e}")
            return None

    def transcribe_audio(self, model_size: str = "base") -> dict:
        """
        使用 Whisper 转写音频

        Args:
            model_size: Whisper 模型大小 (tiny, base, small, medium, large)

        Returns:
            转写结果字典
        """
        # 延迟导入 whisper
        try:
            import whisper
        except ImportError:
            print("[错误] 请安装 whisper: pip install openai-whisper")
            return {"text": "", "language": "zh", "segments": [], "duration": 0}

        # 设置 FFmpeg 路径
        try:
            import imageio_ffmpeg
            import os
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            os.environ['FFMPEG_BINARY'] = ffmpeg_path
            # 将 FFmpeg 所在目录添加到 PATH
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
            os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
        except:
            pass

        print(f"[INFO] 开始转写音频 (模型: {model_size})...")

        # 加载模型
        model = whisper.load_model(model_size)

        # 使用绝对路径的音频文件
        audio_path_abs = Path(self._output_dir_abs) / "audio.wav"

        # 转写
        try:
            result = model.transcribe(str(audio_path_abs), language="zh")
        except Exception as e:
            print(f"[警告] 直接转写失败，尝试手动加载音频: {e}")
            # 尝试手动加载音频
            try:
                import numpy as np
                import wave

                # 使用 wave 读取 wav 文件
                with wave.open(str(audio_path_abs), 'rb') as wf:
                    channels = wf.getnchannels()
                    frames = wf.readframes(wf.getnframes())

                audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

                # 如果是立体声，转换为单声道
                if channels == 2:
                    audio_data = audio_data.reshape(-1, 2).mean(axis=1)

                result = model.transcribe(audio_data, language="zh")
            except Exception as e2:
                print(f"[错误] 手动加载音频也失败: {e2}")
                return {"text": "", "language": "zh", "segments": [], "duration": 0}

        # 提取文本
        text = result["text"].strip()

        # 保存转写结果
        transcript_path = Path(self._output_dir_abs) / "transcript.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"[INFO] 音频转写完成，保存到: {transcript_path}")
        print(f"[INFO] 转写文本预览: {text[:200]}..." if len(text) > 200 else f"[INFO] 转写文本: {text}")

        return {
            "text": text,
            "language": result.get("language", "zh"),
            "segments": result.get("segments", []),
            "duration": result.get("duration", 0)
        }

    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为 base64 字符串"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def prepare_data_for_llm(self, frame_paths: list, transcript: dict) -> dict:
        """
        准备数据供大模型使用

        Returns:
            包含图片和文本的字典
        """
        print("[INFO] 准备大模型输入数据...")

        data = {
            "video_name": self.video_name,
            "analysis_time": datetime.now().isoformat(),
            "frames": [],
            "transcript": transcript
        }

        # 编码关键帧
        for i, frame_path in enumerate(frame_paths):
            print(f"[INFO] 编码帧 {i+1}/{len(frame_paths)}: {frame_path.name}")
            # 转换为绝对路径
            abs_path = frame_path.resolve() if not frame_path.is_absolute() else frame_path
            data["frames"].append({
                "filename": frame_path.name,
                "path": str(abs_path),
                "base64": self.encode_image_to_base64(str(abs_path))
            })

        # 保存完整数据到 JSON
        output_file = self.output_dir / "llm_input_data.json"

        # 移除 base64 数据以减小文件体积（可选）
        data_summary = {
            "video_name": data["video_name"],
            "analysis_time": data["analysis_time"],
            "frame_count": len(data["frames"]),
            "frame_filenames": [f["filename"] for f in data["frames"]],
            "transcript": data["transcript"]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_summary, f, ensure_ascii=False, indent=2)

        print(f"[INFO] 数据已保存到: {output_file}")
        return data

    def generate_prompt_for_llm(self, transcript: dict, frame_count: int) -> str:
        """生成大模型提示词"""
        prompt = f"""请分析以下视频内容：

## 视频信息
- 视频名称: {self.video_name}
- 提取关键帧数量: {frame_count}

## 音频转写内容:
{transcript.get('text', '无')}

## 关键帧
视频中已提取 {frame_count} 张关键帧（见附件图片）。

## 请分析并提供:
1. 视频主要内容概述
2. 视频风格和情感基调
3. 推荐bgm音乐风格
4. 推荐音效
5. 可能的受众群体
6. 改进建议

请基于视频画面和音频内容进行综合分析。"""

        return prompt


def call_anthropic_api(prompt: str, images: list = None, api_key: str = None) -> str:
    """
    调用 Anthropic Claude API 进行多模态推理

    Args:
        prompt: 提示词
        images: base64 编码的图片列表
        api_key: API 密钥

    Returns:
        API 响应文本
    """
    try:
        import anthropic
    except ImportError:
        print("[错误] 请安装 anthropic: pip install anthropic")
        return None

    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")

    if api_key is None:
        print("[错误] 未设置 ANTHROPIC_API_KEY 环境变量")
        return None

    client = anthropic.Anthropic(api_key=api_key)

    # 构建消息内容
    content = [{"type": "text", "text": prompt}]

    # 添加图片（如果有）
    if images:
        for img in images[:5]:  # 限制图片数量
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": img["base64"][:100000]  # 限制大小
                }
            })

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{"role": "user", "content": content}]
    )

    return message.content[0].text


def call_openai_vision_api(prompt: str, images: list = None, api_key: str = None) -> str:
    """
    调用 OpenAI GPT-4 Vision API 进行多模态推理

    Args:
        prompt: 提示词
        images: base64 编码的图片列表
        api_key: API 密钥

    Returns:
        API 响应文本
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("[错误] 请安装 openai: pip install openai")
        return None

    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY")

    if api_key is None:
        print("[错误] 未设置 OPENAI_API_KEY 环境变量")
        return None

    client = OpenAI(api_key=api_key)

    # 构建消息内容
    content = [{"type": "text", "text": prompt}]

    # 添加图片
    if images:
        for img in images[:5]:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img['base64'][:100000]}"
                }
            })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=2000
    )

    return response.choices[0].message.content


def analyze_video(video_path: str, max_frames: int = 10, whisper_model: str = "base",
                  use_api: str = None, api_key: str = None):
    """
    完整分析视频流程

    Args:
        video_path: 视频文件路径
        max_frames: 最大关键帧数量
        whisper_model: Whisper 模型大小
        use_api: 使用的API (anthropic/openai/none)
        api_key: API 密钥
    """
    print("=" * 60)
    print("视频分析中间件")
    print("=" * 60)

    # 初始化分析器
    analyzer = VideoAnalyzer(video_path)

    # 1. 提取关键帧
    frame_paths = analyzer.extract_keyframes(max_frames=max_frames)

    # 2. 提取音频
    audio_path = analyzer.extract_audio()

    if audio_path is None:
        print("[警告] 无法提取音频，跳过转写")
        transcript = {"text": "", "language": "zh", "segments": [], "duration": 0}
    else:
        # 3. 转写音频
        transcript = analyzer.transcribe_audio(model_size=whisper_model)

    # 4. 准备数据
    data = analyzer.prepare_data_for_llm(frame_paths, transcript)

    # 5. 生成提示词
    prompt = analyzer.generate_prompt_for_llm(transcript, len(frame_paths))

    # 保存提示词
    prompt_path = analyzer.output_dir / "prompt.txt"
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    print(f"[INFO] 提示词已保存到: {prompt_path}")

    # 6. 调用大模型API（可选）
    if use_api:
        print(f"[INFO] 正在调用 {use_api} API 进行多模态分析...")

        if use_api == "anthropic":
            result = call_anthropic_api(prompt, data["frames"], api_key)
        elif use_api == "openai":
            result = call_openai_vision_api(prompt, data["frames"], api_key)
        else:
            print(f"[错误] 不支持的 API: {use_api}")
            return

        if result:
            # 保存分析结果
            result_path = analyzer.output_dir / "analysis_result.txt"
            with open(result_path, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"[INFO] 分析结果已保存到: {result_path}")
            print("\n" + "=" * 60)
            print("分析结果:")
            print("=" * 60)
            print(result)

    print("\n[完成] 分析完成！所有结果保存在:", analyzer.output_dir)


def main():
    parser = argparse.ArgumentParser(description="视频分析中间件 - 提取关键帧和音频转写")
    parser.add_argument("video", help="视频文件路径")
    parser.add_argument("-o", "--output", help="输出目录", default=None)
    parser.add_argument("-f", "--frames", type=int, default=10, help="最大关键帧数量 (默认10)")
    parser.add_argument("-m", "--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper 模型大小 (默认base)")
    parser.add_argument("--api", choices=["anthropic", "openai", "none"], default="none",
                        help="调用的大模型API (默认不调用)")
    parser.add_argument("--api-key", help="API 密钥 (也可通过环境变量设置)")

    args = parser.parse_args()

    # 检查视频文件
    if not os.path.exists(args.video):
        print(f"[错误] 视频文件不存在: {args.video}")
        sys.exit(1)

    # 运行分析
    analyze_video(
        video_path=args.video,
        max_frames=args.frames,
        whisper_model=args.model,
        use_api=args.api,
        api_key=args.api_key
    )


if __name__ == "__main__":
    main()
