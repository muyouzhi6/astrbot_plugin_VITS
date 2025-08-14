# 兼容旧版插件加载器，显式导出主类
__all__ = ["VITSPlugin"]
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
    @filter.command("vits_enable", priority=1)
    async def vits_enable(self, event: AstrMessageEvent):
        """开启本会话TTS"""
        session_id = self._get_session_id(event)
        # 只在全局开关为false时允许动态开关
        if not getattr(self, 'global_enable', False):
            # 动态修改 enabled_sessions
            enabled_sessions = self.config.get('enabled_sessions', [])
            if isinstance(enabled_sessions, str):
                enabled_sessions = [s.strip() for s in enabled_sessions.split(',') if s.strip()]
            if session_id not in enabled_sessions:
                enabled_sessions.append(session_id)
                self.default_enabled_sessions = enabled_sessions
                # 同步回 config
                self.config['enabled_sessions'] = ','.join(enabled_sessions)
                yield event.plain_result("本会话TTS已开启")
            else:
                yield event.plain_result("本会话TTS本就已开启")
        else:
            yield event.plain_result("请先关闭全局TTS开关（global_enable=false）后再单独控制会话")

    @filter.command("vits_disable", priority=1)
    async def vits_disable(self, event: AstrMessageEvent):
        """关闭本会话TTS"""
        session_id = self._get_session_id(event)
        if not getattr(self, 'global_enable', False):
            enabled_sessions = self.config.get('enabled_sessions', [])
            if isinstance(enabled_sessions, str):
                enabled_sessions = [s.strip() for s in enabled_sessions.split(',') if s.strip()]
            if session_id in enabled_sessions:
                enabled_sessions.remove(session_id)
                self.default_enabled_sessions = enabled_sessions
                self.config['enabled_sessions'] = ','.join(enabled_sessions)
                yield event.plain_result("本会话TTS已关闭")
            else:
                yield event.plain_result("本会话TTS本就已关闭")
        else:
            yield event.plain_result("请先关闭全局TTS开关（global_enable=false）后再单独控制会话")

    @filter.command("vits_say", priority=1)
    async def vits_say(self, event: AstrMessageEvent, *, text: str = None):
        """手动指定文本转语音，格式：vits_say 你要说的话"""
        if not text:
            yield event.plain_result("请在指令后输入要转语音的内容。"); return
        # 汉字和英文分别限制：汉字≤80，英文≤200
        han_count = len(re.findall(r'[\u4e00-\u9fff]', text))
        en_count = len(re.findall(r'[A-Za-z]', text))
        if han_count > 80 or en_count > 200:
            yield Plain(text)
            return
        output_audio_path = Path(__file__).parent / "miao_say.wav"
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url
            )
            with client.audio.speech.with_streaming_response.create(
                model=self.api_name,
                voice=self.api_voice,
                input=text,
                response_format="wav",
                speed=self.speed
            ) as response:
                response.stream_to_file(output_audio_path)
                # 兼容不同bot，优先 send_audio，但无论如何都 yield Record
                if hasattr(event, 'send_audio'):
                    await event.send_audio(str(output_audio_path))
                yield Record(file=str(output_audio_path))
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logging.error(f"vits_say语音转换失败: {e}\n{tb}")
            yield event.plain_result(f"语音转换失败: {e}")

    @filter.command("vits_status", priority=1)
    async def vits_status(self, event: AstrMessageEvent):
        session_id = self._get_session_id(event)
        # enabled_sessions 可能是字符串（逗号分隔）或列表
        enabled_sessions = self.config.get('enabled_sessions', [])
        if isinstance(enabled_sessions, str):
            enabled_sessions = [s.strip() for s in enabled_sessions.split(',') if s.strip()]
        status = session_id in enabled_sessions
        if status:
            yield event.plain_result("本会话TTS当前为：开启状态")
        else:
            yield event.plain_result("本会话TTS当前为：关闭状态")
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        self.api_url = config.get('url', '')  # 提取 API URL
        self.api_key = config.get('apikey', '')  # 提取 API Key
        self.api_name = config.get('name', '')  # 提取 模型 名称
        self.api_voice = config.get('voice', '')  # 提取角色名称
        # 新增：全局TTS开关，优先级最高
    self.global_enable = config.get('global_enable', False)
        # 新增：配置默认开启的会话列表，支持字符串或列表
        enabled_sessions = config.get('enabled_sessions', [])
        if isinstance(enabled_sessions, str):
            enabled_sessions = [s.strip() for s in enabled_sessions.split(',') if s.strip()]
        self.default_enabled_sessions = enabled_sessions
        # 新增：配置字数限制，默认30
        self.text_limit = int(config.get('text_limit', 30))
        # 新增：语速参数，默认1.0
        self.speed = float(config.get('speed', 1.0))
        self.non_plain_components = []  # 初始化 non_plain_components 变量




    # 移除vits指令，全部由配置控制

    def _get_session_id(self, event: AstrMessageEvent):
        # 群聊用 group_id，私聊用 user_id
        if hasattr(event, 'group_id') and event.group_id:
            return f"group_{event.group_id}"
        return f"user_{event.get_sender_id()}"

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):


        # 优先判断全局TTS开关
        if not getattr(self, 'global_enable', True):
            return
        # 只在配置中指定的会话开启TTS
        session_id = self._get_session_id(event)
        if session_id not in self.default_enabled_sessions:
            return

        # 获取事件结果
        result = event.get_result()
        # 只在消息链全为 Plain 且有内容时才自动TTS，遇到图片、合并转发等非 Plain 组件直接跳过
        if not result.chain:
            return
        if any(not isinstance(comp, Plain) for comp in result.chain):
            return
        if not any(comp.text.strip() for comp in result.chain):
            return
        # 初始化plain_text变量
        plain_text = ""
        chain = result.chain

        #遍历组件
        for comp in result.chain:
            if isinstance(comp, Plain):
                # 只去除特殊符号，保留中英文、数字
                cleaned_text = re.sub(r'[()《》#%^&*+\-_{}]', '', comp.text)
                plain_text += cleaned_text
        # 不再处理 Image，图片由主框架正常输出

        # 汉字和英文分别限制：汉字≤80，英文≤200
        han_count = len(re.findall(r'[\u4e00-\u9fff]', plain_text))
        en_count = len(re.findall(r'[A-Za-z]', plain_text))
        if han_count > 80 or en_count > 200:
            # 超限时直接文本输出
            result.chain = [Plain(plain_text)]
            return

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
                response_format="wav",  # 支持 mp3, wav, pcm, opus 格式
                speed=self.speed
            ) as response:
                response.stream_to_file(output_audio_path)
                result.chain = [Record(file=str(output_audio_path))]
        except Exception as e:
            logging.error(f"语音转换失败: {e}")
            chain.append(Plain("语音转换失败，请稍后再试"))
