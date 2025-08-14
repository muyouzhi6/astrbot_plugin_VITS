
# AstrBot VITS 语音合成插件（木有知改进版）

## 功能简介
支持将指定文字自动或手动转为语音，支持自定义音色、语速、字数限制、会话控制。

## 快速用法
1. 在插件面板填写 API URL、API Key、模型名称、音色名称等参数。
2. 配置 enabled_sessions（如 user_123456,group_654321）决定哪些会话自动转语音。
3. 发送指令：
	- `vits_say 你要说的话`  → 机器人直接回复语音。
	- `vits_status`  → 查询本会话 TTS 状态。

## 参数说明
| 参数名            | 说明                       | 示例                      |
|-------------------|----------------------------|---------------------------|
| url               | API 地址                   | https://api.siliconflow.cn/v1 |
| apikey            | API 密钥                   | sk-xxx                    |
| name              | 模型名称                   | siliconflow-vits-v1       |
| voice             | 音色名称/uri               | zhizhi-xxx                |
| enabled_sessions  | 自动TTS会话（逗号分隔）    | user_123,group_456        |
| text_limit        | 最大字数                   | 30                        |
| speed             | 语速（1正常，0.8慢，1.2快）| 1.1                       |

## 常见问题
- 语音转换失败：请检查 API Key、模型/音色参数、网络，或查看日志详细报错。
- 如何只在部分群/私聊生效？→ 配置 enabled_sessions。
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
- `vits_enable`：开启本会话 TTS（仅在 global_enable=false 时生效）。
- `vits_disable`：关闭本会话 TTS（仅在 global_enable=false 时生效）。
- `vits_status`：查询本会话 TTS 当前状态（开启/关闭）。

| global_enable     | 全局TTS开关（优先级最高，默认关闭，false=全部关闭，true=全部开启） | false |
| enabled_sessions  | 自动TTS会话（user_用户ID,group_群号，逗号分隔，仅在全局开关为true时生效） | user_123,group_456        |
---
2. 配置 global_enable=false（默认），所有会话都不自动TTS。仅当 global_enable=true 时，enabled_sessions 配置的会话才会自动TTS。

 - 如何只在部分群/私聊生效？→ 默认全局关闭（global_enable=false），只需在 enabled_sessions 配置需要自动TTS的会话ID。
 - 如何全局一键开启/关闭？→ 设置 global_enable=true/false 即可。
- 插件默认关闭，需用 `vits` 指令开启。
- 只对当前会话（群聊/私聊）生效，互不影响。
- 仅当文本内容不超过30字时才会进行语音合成，超出则无语音输出。
- 检测到图片时不进行语音合成。

---

## 常见问题
- **音色无效/报错**：请确认 API Key、模型名、音色 uri 正确。
- **自定义音色上传失败**：请检查音频格式、参考文本、API Key 权限。
- **TTS无响应**：请确认本会话已用 `vits` 开启，且文本不超过30字。

---

## 其它
- 支持官方和自定义音色。
- 代码和指令均可扩展，如需更多功能请联系开发者。
