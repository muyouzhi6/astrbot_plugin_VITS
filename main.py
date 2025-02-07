from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Record, Plain
from pathlib import Path
from openai import OpenAI



# 注册插件的装饰器
@register("VITSPlugin", "第九位魔神", "语音合成插件", "1.1.0")
class VITSPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        self.api_url = config.get('url', 'https://api.siliconflow.cn/v1')  # 提取 API URL
        self.api_key = config.get('apikey', '')  # 提取 API Key
        self.api_name = config.get('name', 'FunAudioLLM/CosyVoice2-0.5B')  # 提取 模型 名称
        self.api_voice = config.get('voice', 'FunAudioLLM/CosyVoice2-0.5B:alex')  # 提取角色名称
        self.enabled = False  # 初始化插件开关为关闭状态


    @filter.command("vits", priority=1)
    async def vits(self, event: AstrMessageEvent):
        user_name = event.get_sender_name()
        self.enabled = not self.enabled
        if self.enabled:
            yield event.plain_result(f"启用语音插件, {user_name}")
        else:
            yield event.plain_result(f"禁用语音插件, {user_name}")


    @filter.on_decorating_result()
    async def on_decorate_result(self, event: AstrMessageEvent):
        # 插件是否启用
        if not self.enabled:
            return

        # 检查配置项是否为空
        if not self.api_url or not self.api_key or not self.api_name or not self.api_voice:
            return event.plain_result("\n插件未配置")


        # 检查模型是否填错
        if self.api_name not in self.api_voice:
            return event.plain_result("\n模型配置错误")


        # 获取事件结果
        result = event.get_result()
        # 初始化plain_text变量
        plain_text = ""
        # 初始化non_plain_components列表
        non_plain_components = []
        # 遍历结果链中的每个组件
        for comp in result.chain:
            # 如果组件是Plain类型，则将其文本内容添加到plain_text中
            if isinstance(comp, Plain):
                plain_text += comp.text

        # 初始化输出音频路径
        output_audio_path = "data/plugins/astrbot_plugin_VITS/miao.wav"

        client = OpenAI(
            api_key=(self.api_key),
            base_url=(self.api_url)
        )

        with client.audio.speech.with_streaming_response.create(
                model=(self.api_name),  # 发送模型名称
                voice=(self.api_voice),  # 系统预置音色
                # 用户输入信息
                input=plain_text,
                response_format="mp3"  # 支持 mp3, wav, pcm, opus 格式
        ) as response:
            response.stream_to_file(output_audio_path)
            result.chain = [Record(file=output_audio_path)]

