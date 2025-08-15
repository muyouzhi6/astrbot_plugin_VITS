
# AstrBot VITS 语音合成插件（木有知改进版）

## 功能简介
支持将指定文字自动或手动转为语音，支持自定义音色、语速、字数限制、会话控制。

## 快速用法
1. 在插件面板填写 API URL、API Key、模型名称、音色名称等参数。
2. 默认全局关闭（global_enable=false）。配置 enabled_sessions（如 user_123456,group_654321）或在对话里用指令开启，决定哪些会话自动转语音。
3. 发送指令：
	- `vits_say 你要说的话`  → 机器人直接回复语音。
	- `vits_status`  → 查询本会话 TTS 状态。
	- `vits_enable` / `vits_disable` → 在当前会话内开启/关闭自动TTS（全局关闭时可单独控制）。

## 参数说明
| 参数名            | 说明                                             | 示例                          |
|-------------------|--------------------------------------------------|-------------------------------|
| url               | API 地址                                         | https://api.siliconflow.cn/v1 |
| apikey            | API 密钥                                         | sk-xxx                        |
| name              | 模型名称                                         | siliconflow-vits-v1           |
| voice             | 音色名称/uri                                     | zhizhi-xxx                    |
| global_enable     | 全局TTS开关（默认 false；true=全部会话自动TTS）  | false                         |
| enabled_sessions  | 自动TTS会话（逗号分隔，user_/group_ 前缀）       | user_123,group_456            |
| text_limit        | 自动TTS长度限制（汉字≤80，英文≤200；无需修改）  | -                             |
| speed             | 语速（1正常，0.8慢，1.2快）                      | 1.1                           |

## 常见问题
- 语音转换失败：请检查 API Key、模型/音色参数、网络，或查看日志详细报错。
- 如何只在部分群/私聊生效？→ 默认全局关闭，配置 enabled_sessions 或在对话里用 `vits_enable` 开启即可。
- 如何自定义语速？→ 配置 speed 参数。
- 如何上传自定义音色？→ 见硅基流动 API 文档。

## 进阶
- 支持图片检测、异常捕获、详细日志输出。
- 代码已适配新版/旧版 AstrBot，适合二次开发。

---
如有问题请联系插件原作者或“木有知”，或查阅 API 官方文档。

# Astrbot_Plugin_VITS 使用说明

## 插件简介
本插件为 AstrBot 提供文本转语音（TTS）功能，支持硅基流动 API，可自定义音色、模型、API Key。

---

## 快速配置
1. **插件面板配置**：
	- URL：`https://api.siliconflow.cn/v1`
	- API Key：你的硅基流动 API Key
	- 模型名称（name）：如 `FunAudioLLM/CosyVoice2-0.5B`
	- 音色（voice）：可填官方音色（如 `FunAudioLLM/CosyVoice2-0.5B:alex`）或自定义音色 uri（如 `speech:myvoice:icwcmuszkb:eachiineltvqdwxhmkft`）

2. **自定义音色上传**：
	- 用 voice_tools 文件夹下的上传脚本，按说明上传音频，获取 uri。
	- 将 uri 填入插件 voice 字段即可。

---

## 指令说明
- `vits_enable`：开启本会话 TTS（在 global_enable=false 时用于单独控制）。
- `vits_disable`：关闭本会话 TTS（在 global_enable=false 时用于单独控制）。
- `vits_status`：查询本会话 TTS 当前状态（开启/关闭）。

提示：
- 当 global_enable=true 时，所有会话都会自动TTS；
- 当 global_enable=false 时，只有 enabled_sessions 列表内或通过指令开启的会话会自动TTS；
- 自动TTS仅在消息链全部为纯文本（Plain）时触发；
- 自动TTS长度限制：汉字≤80，英文≤200，超限则发送纯文本；
- `vits_say` 指令不受长度限制。

---

## 常见问题
- **音色无效/报错**：请确认 API Key、模型名、音色 uri 正确。
- **自定义音色上传失败**：请检查音频格式、参考文本、API Key 权限。
- **TTS无响应**：请确认本会话处于开启状态（全局或本会话），且消息为纯文本并未超出自动TTS长度限制。

---

## 其它
- 支持官方和自定义音色。
- 代码和指令均可扩展，如需更多功能请联系开发者。
