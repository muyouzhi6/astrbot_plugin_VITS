from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Record, Plain, Image
from pathlib import Path
from openai import OpenAI
import logging
import re

# 注册插件的装饰器
@register("VITSPlugin", "第九位魔神", "语音合成插件", "1.2.0")
class VITSPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        self.api_url = config.get('url', '')  # 提取 API URL
        self.api_key = config.get('apikey', '')  # 提取 API Key
        self.api_name = config.get('name', '')  # 提取 模型 名称
        self.api_voice = config.get('voice', '')  # 提取角色名称
        self.enabled = False  # 初始化插件开关为关闭状态
        self.non_plain_components = []  # 初始化 non_plain_components 变量

    @filter.command("vits", priority=1)
    async def vits(self, event: AstrMessageEvent):
        user_name = event.get_sender_name()
        self.enabled = not self.enabled
        if self.enabled:
            yield event.plain_result(f"启用语音插件, {user_name}")
        else:
            yield event.plain_result(f"禁用语音插件, {user_name}")

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        # 插件是否启用
        if not self.enabled:
            return

        # 获取事件结果
        result = event.get_result()
        # 初始化plain_text变量
        plain_text = ""
        chain = result.chain

        #遍历组件
        for comp in result.chain:
            if isinstance(comp, Image):  # 检测是否有Image组件
                chain.append(Plain("检测到图片冲突，终止语音转换"))
                return
            if isinstance(comp, Plain):
                cleaned_text = re.sub(r'[()《》#%^&*+-_{}]', '', comp.text)
                plain_text += cleaned_text

        # 初始化输出音频路径
        output_audio_path = Path(__file__).parent / "miao.wav"

        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url
            )

            with client.audio.speech.with_streaming_response.create(
                    model=self.api_name,  # 发送模型名称
                    voice=self.api_voice,  # 系统预置音色
                    input=plain_text,
                    response_format="wav"  # 支持 mp3, wav, pcm, opus 格式
            ) as response:
                response.stream_to_file(output_audio_path)
                result.chain = [Record(file=str(output_audio_path))]
        except Exception as e:
            logging.error(f"语音转换失败: {e}")
            chain.append(Plain("语音转换失败，请稍后再试"))