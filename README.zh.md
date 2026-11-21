# Google Gen AI SDK

[English](README.md) | [简体中文](https://github.com/googleapis/python-genai/blob/main/README.zh.md)

[![PyPI version](https://img.shields.io/pypi/v/google-genai.svg)](https://pypi.org/project/google-genai/)
![Python support](https://img.shields.io/pypi/pyversions/google-genai)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/google-genai)](https://pypistats.org/packages/google-genai)

--------
**官方文档：** https://googleapis.github.io/python-genai/
-----

> [!NOTE]
> 本文档为开源社区维护的简体中文翻译。由于上游代码库持续高速迭代，若文档存在差异或过时，请以英文原版 [README.md](README.md) 及 [官方 API 参考文档](https://googleapis.github.io/python-genai/) 为最终权威事实来源（Source of Truth）。

Google Gen AI Python SDK 为开发者提供了将 Google 生成式大模型无缝集成到 Python 应用程序中的统一开发接口。该 SDK 统一支持 [Gemini Developer API](https://aistudio.google.com/docs) 与 [Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform) 两大服务。

> [!WARNING]
>
> 3.x 大版本核心变更说明：
>
> * **默认 Gemini Developer API 版本已切换为 `v1`（原为 `v1beta`）。**
>   企业级（Vertex AI）客户端不受影响，仍默认使用 `v1beta1`。
>     * `gemini-flash-latest`、`gemini-flash-lite-latest` 与 `gemini-pro-latest` 别名仅存在于 `v1beta`。请指定具体模型版本，或切换回 `v1beta`。
>     * 如需恢复旧版默认行为，可设置环境变量 `GOOGLE_GENAI_API_VERSION=beta`（或显式指定如 `v1beta`），亦可在代码中传递 `types.HttpOptions(api_version='v1beta')`（代码配置优先级最高）。
> * **默认 HTTP 传输客户端现为 `httpx2`（原为 `httpx`），且默认不再安装 `httpx`。**
>     * 如需恢复 `httpx` 为默认客户端，需同时执行：安装 `google-genai[httpx]` 并设置环境变量 `GOOGLE_GENAI_HTTP_CLIENT=httpx`。亦可在 `HttpOptions` 中直接传入 `httpx_client` / `httpx_async_client`。
>     * 如需迁移至 `httpx2`，多数场景下仅需使用 `import httpx2 as httpx` 即可。
>     * 当未设置 `SSL_CERT_FILE` 和 `SSL_CERT_DIR` 时，`httpx2` 会直接依据操作系统信任存储验证 SSL 证书，而非依赖 `certifi`。
>     * 传入 `HttpOptions(client_args=..., async_client_args=...)` 的对象（如 `Timeout`、`Limits`、传输层、`Auth` 子类）以及捕获的传输异常（如 `TimeoutException`、`ConnectError`、`HTTPError`）必须来自于当前活跃的 HTTP 客户端包。
> * **Interactions API 变更：** `CodeExecutionResultStep.result` 类型由 `string` 调整为 `CodeExecutionResultStepResult` 联合类型。请检查具体返回的变体并从中读取字符串。仅包含文本结果的 JSON 格式保持不变。
>
> 为防止非预期的破坏性升级，可在依赖中将 SDK 版本锁定为 `< 3.0.0`。

## Agent Skills（智能体技能）

大语言模型（LLM）与生成式 AI 编程助手通常基于静态数据集进行训练。因此，它们可能无法感知最新的接口演进，并容易生成过时或遗留库的代码。

为确保 AI 编码助手（如 Antigravity、Claude Code、Cursor 或其他 IDE 插件）能够遵循最新规范生成完全准确的 SDK 语法与最佳实践代码，建议为助手配置 **Gemini API Skills**。加载这些技能可将正确的代码范式与指导原则直接注入 AI 助手的上下文环境中。

根据目标平台选择对应的 Agent Skill 代码库：

*   **Gemini Developer API**：使用 [google-gemini/gemini-skills](https://github.com/google-gemini/gemini-skills) 代码库。
*   **Gemini Enterprise Agent Platform（原 Vertex AI）**：使用 [google/skills](https://github.com/google/skills/tree/main/skills/cloud/gemini-api) 代码库。

## 安装

```sh
pip install google-genai
```

<small>使用 `uv` 安装：</small>

```sh
uv pip install google-genai
```

## 导入模块

```python
from google import genai
from google.genai import types
```

## 创建客户端

请运行以下对应代码块之一，为目标服务（[Gemini Developer API](https://aistudio.google.com/docs) 或 [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform)）创建客户端实例。

```python
from google import genai

# 仅用于 Gemini Developer API
client = genai.Client(api_key='GEMINI_API_KEY')
```

```python
from google import genai

# 仅用于 Agent Platform
client = genai.Client(
    enterprise=True, project='your-project-id', location='global'
)
```

## 使用类型系统 (Types)

所有 API 方法均同时支持 Pydantic 类型与普通字典（`dict`），均可自 `google.genai.types` 模块直接导入：

```python
from google.genai import types
```

以下为在 `generate_content()` 调用中使用 `types.Part` 的示例：

```python
response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents=types.Part.from_text(text='Why is the sky blue?')
)
```

亦可直接使用普通字典替代强类型对象：

```python
response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents={'text': 'Why is the sky blue?'}
)
```

**(可选) 使用环境变量配置：**

亦可通过配置相应的环境变量来初始化客户端。具体配置取决于所使用的是 Gemini Developer API 还是 Gemini Enterprise Agent Platform。

**Gemini Developer API：** 设置 `GEMINI_API_KEY` 或 `GOOGLE_API_KEY`。客户端会自动读取。建议仅设置其中一个；若同时设置，`GOOGLE_API_KEY` 具有更高优先级。

```bash
export GEMINI_API_KEY='your-api-key'
```

**Agent Platform 上的 Gemini API：** 设置 `GOOGLE_GENAI_USE_ENTERPRISE`、`GOOGLE_CLOUD_PROJECT` 与 `GOOGLE_CLOUD_LOCATION`，如下所示：

```bash
export GOOGLE_GENAI_USE_ENTERPRISE=true
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='global'
```

配置环境变量后即可直接无参实例化客户端：

```python
from google import genai

client = genai.Client()
```

## 关闭客户端

显式关闭同步客户端可确保底层 HTTP 连接等网络资源得到及时释放与清理：

```python
from google.genai import Client

client = Client()
response_1 = client.models.generate_content(
    model=MODEL_ID,
    contents='Hello',
)
response_2 = client.models.generate_content(
    model=MODEL_ID,
    contents='Ask a question',
)
# 关闭同步客户端以释放底层资源
client.close()
```

显式关闭异步客户端：

```python
from google.genai import Client

aclient = Client(
    enterprise=True, project='my-project-id', location='global'
).aio
response_1 = await aclient.models.generate_content(
    model=MODEL_ID,
    contents='Hello',
)
response_2 = await aclient.models.generate_content(
    model=MODEL_ID,
    contents='Ask a question',
)
# 关闭异步客户端以释放资源
await aclient.aclose()
```

## 客户端上下文管理器

使用同步客户端上下文管理器可在退出 `with` 代码块时自动关闭底层客户端，避免触发类似 [issues#1763](https://github.com/googleapis/python-genai/issues/1763) 中的 `httpx "client has been closed"` 错误：

```python
from google.genai import Client

with Client() as client:
    response_1 = client.models.generate_content(
        model=MODEL_ID,
        contents='Hello',
    )
    response_2 = client.models.generate_content(
        model=MODEL_ID,
        contents='Ask a question',
    )
```

使用异步客户端上下文管理器可在退出 `async with` 代码块时自动清理并关闭底层客户端：

```python
from google.genai import Client

async with Client().aio as aclient:
    response_1 = await aclient.models.generate_content(
        model=MODEL_ID,
        contents='Hello',
    )
    response_2 = await aclient.models.generate_content(
        model=MODEL_ID,
        contents='Ask a question',
    )
```

### API 版本选择

SDK 默认采用如下设置：
- Gemini Developer API 默认使用稳定版 `v1` API 端点。
- Gemini Enterprise Agent Platform 默认使用测试版 `v1beta1` API 端点。

可通过 `http_options` 或环境变量 `GOOGLE_GENAI_API_VERSION` 选定不同 API 版本（例如 `v1beta` 或 `v1alpha`）。`http_options` 中显式指定的版本优先级高于环境变量。设置 `GOOGLE_GENAI_API_VERSION=beta` 将自动选定当前后端对应的 Beta 版本：Gemini Developer API 对应 `v1beta`，Agent Platform 对应 `v1beta1`。

通过 `http_options` 设置 API 版本的示例如下。例如将 Agent Platform 的 API 版本设为 `v1`：

```python
from google import genai
from google.genai import types

client = genai.Client(
    enterprise=True,
    project='your-project-id',
    location='global',
    http_options=types.HttpOptions(api_version='v1')
)
```

将 Gemini Developer API 的 API 版本设置为 `v1alpha`：

```python
from google import genai
from google.genai import types

client = genai.Client(
    api_key='GEMINI_API_KEY',
    http_options=types.HttpOptions(api_version='v1alpha')
)
```

### HTTP 客户端选项：httpx

SDK 默认采用 [`httpx2`](https://github.com/pydantic/httpx2) 作为 HTTP 传输层。如需回退使用旧版 `httpx`，可安装 `google-genai[httpx]` 并设置环境变量 `GOOGLE_GENAI_HTTP_CLIENT`：

```bash
export GOOGLE_GENAI_HTTP_CLIENT=httpx
```

亦可通过 `HttpOptions` 直接注入 `httpx.Client` 或 `httpx.AsyncClient` 实例：

```python
import httpx
from google import genai
from google.genai import types

client = genai.Client(
    http_options=types.HttpOptions(
        httpx_client=httpx.Client(),
        httpx_async_client=httpx.AsyncClient(),
    )
)
```

### 极速异步客户端选项：Aiohttp

默认情况下同步与异步客户端均采用 httpx2。为获得更高吞吐性能，可安装 `google-genai[aiohttp]`。在 Gen AI SDK 中默认配置 `trust_env=True` 以与 httpx2 的默认行为对齐。可通过如下方式传递 `aiohttp.ClientSession.request()` 的扩展参数（详见 [`_RequestOptions` 参数](https://github.com/aio-libs/aiohttp/blob/v3.12.13/aiohttp/client.py#L170)）：

```python
http_options = types.HttpOptions(
    async_client_args={'cookies': ..., 'ssl': ...},
)

client=Client(..., http_options=http_options)
```

### 代理配置 (Proxy)

httpx2 与 aiohttp 均支持直接从环境变量读取 `urllib.request.getproxies`。在初始化客户端前，可通过设置环境变量指定代理（以及可选的 `SSL_CERT_FILE`）：

```bash
export HTTPS_PROXY='http://username:password@proxy_uri:port'
export SSL_CERT_FILE='client.pem'
```

若需使用 `socks5` 代理，httpx2 支持通过参数传入 `httpx2.Client()`。可安装 `httpx2[socks]` 后按如下方式进行配置：

```python
http_options = types.HttpOptions(
    client_args={'proxy': 'socks5://user:pass@host:port'},
    async_client_args={'proxy': 'socks5://user:pass@host:port'},
)

client=Client(..., http_options=http_options)
```

### 自定义 Base URL

在某些场景下可能需要接入自定义 Base URL（例如经过企业内部的 API 网关或代理服务器），并跳过针对项目、区域或 API 密钥的部分前端鉴权校验。可通过如下方式指定自定义 Base URL：

```python
client = Client(
    enterprise=True,
    http_options=types.HttpOptionsDict(
        base_url='https://test-api-gateway-proxy.com',
        base_url_resource_scope=types.ResourceScope.COLLECTION,
    ),
)

response = client.models.generate_content(
    model='gemini-3.1-pro-preview', contents='Why is the sky blue?'
)
```

若设置 `base_url_resource_scope=types.ResourceScope.COLLECTION`，请求资源名称中将不再包含 API 版本、项目或区域信息。

预期实际发起的请求 URL 为：
`https://test-api-gateway-proxy.com/publishers/google/models/gemini-3-pro-preview`

## 类型系统 (Types)

参数类型可以指定为标准字典（`TypedDict`）或 [Pydantic 模型](https://docs.pydantic.dev/latest/concepts/models/)。所有 Pydantic 模型定义均可直接在 `types` 模块中获取。

## 模型推理 (Models)

`client.models` 模块提供了模型推理调用与模型信息查询接口。请先参考上方“创建客户端”章节完成初始化。

### 生成内容 (Generate Content)

#### 文本输入（生成文本）

```python
response = client.models.generate_content(
    model='gemini-3.8-flash', contents='Why is the sky blue?'
)
print(response.text)
```

#### 文本输入（生成图像）

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-3.1-flash-lite-image',
    contents='A cartoon infographic for flying sneakers',
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio="9:16",
        ),
    ),
)

for part in response.parts:
    if part.inline_data:
        generated_image = part.as_image()
        generated_image.show()
```

#### 文本输入（生成音频 / 语音合成 TTS）

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-3.8-flash-tts',
    contents='Give me a cheerful greeting.',
    config=types.GenerateContentConfig(
        response_modalities=['AUDIO'],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name='Aoede'
                )
            )
        ),
    ),
)

for part in response.parts:
    if part.inline_data:
        with open('greeting.wav', 'wb') as f:
            f.write(part.inline_data.data)
```

#### 结合上传文件（仅限 Gemini Developer API）

在终端下载测试文件：

```sh
!wget -q https://storage.googleapis.com/generativeai-downloads/data/a11.txt
```

Python 运行代码：

```python
file = client.files.upload(file='a11.txt')
response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents=['Could you summarize this file?', file]
)
print(response.text)
```

#### 如何为 `generate_content` 构造 `contents` 参数

SDK 内部统一将 `contents` 参数转换为 `list[types.Content]`。以下列举几种常见的输入构造方式：

##### 传递 `list[types.Content]`

这是最规范的标准方式，SDK 不会做任何额外转换。

##### 传递单个 `types.Content` 实例

```python
from google.genai import types

contents = types.Content(
    role='user',
    parts=[types.Part.from_text(text='Why is the sky blue?')]
)
```

SDK 会将其自动封装为列表：

```python
[
    types.Content(
        role='user',
        parts=[types.Part.from_text(text='Why is the sky blue?')]
    )
]
```

##### 传递单个字符串

```python
contents='Why is the sky blue?'
```

SDK 默认将其视为文本 Part，并转换为如下结构：

```python
[
    types.UserContent(
        parts=[
            types.Part.from_text(text='Why is the sky blue?')
        ]
    )
]
```

其中 `types.UserContent` 是 `types.Content` 的子类，其 `role` 字段固定为 `user`。

##### 传递字符串列表

```python
contents=['Why is the sky blue?', 'Why is the cloud white?']
```

SDK 会将其视为两个文本 Part，并合并进单个 Content 中：

```python
[
    types.UserContent(
        parts=[
            types.Part.from_text(text='Why is the sky blue?'),
            types.Part.from_text(text='Why is the cloud white?'),
        ]
    )
]
```

##### 传递函数调用 Part (Function Call Part)

```python
from google.genai import types

contents = types.Part.from_function_call(
    name='get_weather_by_location',
    args={'location': 'Boston'}
)
```

SDK 会将函数调用 Part 转换为 `role` 为 `model` 的 Content：

```python
[
    types.ModelContent(
        parts=[
            types.Part.from_function_call(
                name='get_weather_by_location',
                args={'location': 'Boston'}
            )
        ]
    )
]
```

##### 传递函数调用 Part 列表

```python
from google.genai import types

contents = [
    types.Part.from_function_call(
        name='get_weather_by_location',
        args={'location': 'Boston'}
    ),
    types.Part.from_function_call(
        name='get_weather_by_location',
        args={'location': 'New York'}
    ),
]
```

SDK 将其转换为包含多个 Part 的单个 `model` Content：

```python
[
    types.ModelContent(
        parts=[
            types.Part.from_function_call(
                name='get_weather_by_location',
                args={'location': 'Boston'}
            ),
            types.Part.from_function_call(
                name='get_weather_by_location',
                args={'location': 'New York'}
            )
        ]
    )
]
```

##### 传递非函数调用 Part

```python
from google.genai import types

contents = types.Part.from_uri(
    file_uri='gs://generativeai-downloads/images/scones.jpg',
    mime_type='image/jpeg',
)
```

SDK 会将所有非函数调用的 Part 自动转换为 `role` 为 `user` 的 Content：

```python
[
    types.UserContent(parts=[
        types.Part.from_uri(
            file_uri='gs://generativeai-downloads/images/scones.jpg',
            mime_type='image/jpeg',
        )
    ])
]
```

##### 传递非函数调用 Part 列表

```python
from google.genai import types

contents = [
    types.Part.from_text('What is this image about?'),
    types.Part.from_uri(
        file_uri='gs://generativeai-downloads/images/scones.jpg',
        mime_type='image/jpeg',
    )
]
```

SDK 将该 Part 列表聚合为单个 `role` 为 `user` 的 Content：

```python
[
    types.UserContent(
        parts=[
            types.Part.from_text('What is this image about?'),
            types.Part.from_uri(
                file_uri='gs://generativeai-downloads/images/scones.jpg',
                mime_type='image/jpeg',
            )
        ]
    )
]
```

##### 混合输入类型

亦可传递包含多种 `types.ContentUnion` 的列表。SDK 会保留 `types.Content` 项的原型，并将连续出现的非函数调用 Part 聚合为单个 `types.UserContent`，将连续出现的函数调用 Part 聚合为单个 `types.ModelContent`。

若在列表中嵌套子列表，内层列表仅允许包含 `types.PartUnion` 项，SDK 会自动将内层列表合并为单个 `types.UserContent`。

### 系统指令与其他高级配置

模型的输出行为可通过 `generate_content` 中的可选 `config` 参数进行精准控制。例如，调大 `max_output_tokens` 对于获取长回复至关重要。各模型支持的功能与参数默认值可分别参考 [Gemini Enterprise Agent Platform 文档](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models) 与 [Gemini API 文档](https://aistudio.google.com/docs/models)。所有配置参数均可使用 `google.genai.types.GenerateContentConfig` 进行声明：

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents='high',
    config=types.GenerateContentConfig(
        system_instruction='I say high, you say low',
        max_output_tokens=3,
    ),
)
print(response.text)
```

### 自动接续生成 (Automatic Continuation)

SDK 默认开启自动接续生成。当模型响应因达到输出限制使得 `finish_reason` 为 `CONTINUATION` 并返回 `continuation_token` 时，SDK 会自动使用该 Token 发送后续请求，直至内容完整生成并返回合并后的完整响应。如需禁用此特性，可在 `GenerateContentConfig` 中设置 `automatic_continuation=False`。

该机制在流式生成（`generate_content_stream`）、异步调用（`client.aio.models.generate_content` 与 `client.aio.models.generate_content_stream`）以及多轮对话（`chat.send_message` 和 `chat.send_message_stream`）中同样适用。

```python
from google import genai
from google.genai import types

client = genai.Client(
    enterprise=True, project='your-project-id', location='global'
)

# 默认开启自动接续生成
response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents='Write a comprehensive multi-chapter guide on compiler design.',
)
print(response.text)

# 设置 automatic_continuation=False 禁用自动接续
single_hop_response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents='Write a comprehensive multi-chapter guide on compiler design.',
    config=types.GenerateContentConfig(
        automatic_continuation=False,
    ),
)
print(single_hop_response.text)
```

### 列出基础模型 (List Base Models)

如需查询微调后的模型，请参见[列出已微调模型](#列出已微调模型-list-tuned-models)。

```python
for model in client.models.list():
    print(model)
```

使用分页查询：

```python
pager = client.models.list(config={'page_size': 10})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

#### 异步列出基础模型

```python
async for job in await client.aio.models.list():
    print(job)
```

```python
async_pager = await client.aio.models.list(config={'page_size': 10})
print(async_pager.page_size)
print(async_pager[0])
await async_pager.next_page()
print(async_pager[0])
```

### 安全阈值配置 (Safety Settings)

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents='Say something bad.',
    config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category='HARM_CATEGORY_HATE_SPEECH',
                threshold='BLOCK_ONLY_HIGH',
            )
        ]
    ),
)
print(response.text)
```

### 工具与函数调用 (Function Calling)

#### 自动 Python 函数调用支持

可直接将标准 Python 函数作为工具传入，SDK 默认会自动执行函数调用并将结果回传给模型完成闭环应答：

```python
from google.genai import types

def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
        location: The city and state, e.g. San Francisco, CA
    """
    return 'sunny'


response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[get_current_weather]),
)

print(response.text)
```

#### 禁用自动函数调用

若直接传入 Python 函数但希望由业务代码手动处理调用过程，可显式禁用自动函数调用：

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    ),
)
```

禁用后，模型将在响应中返回函数调用 Part 列表：

```python
function_calls: Optional[List[types.FunctionCall]] = response.function_calls
```

#### 手动声明与调度函数调用

除直接传入 Python 函数外，亦可手动声明工具架构并控制调用生命周期：

```python
from google.genai import types

function = types.FunctionDeclaration(
    name='get_current_weather',
    description='Get the current weather in a given location',
    parameters_json_schema={
        'type': 'object',
        'properties': {
            'location': {
                'type': 'string',
                'description': 'The city and state, e.g. San Francisco, CA',
            }
        },
        'required': ['location'],
    },
)

tool = types.Tool(function_declarations=[function])

response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[tool]),
)

print(response.function_calls[0])
```

收到模型的函数调用请求后，执行本地函数并将结果构造成 `tool` role 回传：

```python
from google.genai import types

user_prompt_content = types.Content(
    role='user',
    parts=[types.Part.from_text(text='What is the weather like in Boston?')],
)
function_call_part = response.function_calls[0]
function_call_content = response.candidates[0].content

try:
    function_result = get_current_weather(
        **function_call_part.function_call.args
    )
    function_response = {'result': function_result}
except Exception as e:
    function_response = {'error': str(e)}

function_response_part = types.Part.from_function_response(
    name=function_call_part.name,
    response=function_response,
)
function_response_content = types.Content(
    role='tool', parts=[function_response_part]
)

response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents=[
        user_prompt_content,
        function_call_content,
        function_response_content,
    ],
    config=types.GenerateContentConfig(
        tools=[tool],
    ),
)

print(response.text)
```

#### 强制函数调用模式 (`ANY` 工具模式)

若将工具调用模式设置为 `ANY`，模型将始终返回函数调用。此时若直接传入 Python 函数，SDK 默认会自动进行多轮远程函数调用，直至达到最大调用限制（默认为 10 次）。

若在 `ANY` 模式下禁用自动函数调用：

```python
from google.genai import types

def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
        location: The city and state, e.g. San Francisco, CA
    """
    return "sunny"

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="What is the weather like in Boston?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        ),
    ),
)
```

若希望限制自动函数调用的轮数（例如仅允许 1 轮自动调用），可设置 `maximum_remote_calls = 轮数 + 1`：

```python
from google.genai import types

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="What is the weather like in Boston?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            maximum_remote_calls=2
        ),
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        ),
    ),
)
```

#### Model Context Protocol (MCP) 原生支持 (实验性特性)

##### Gemini Developer API 下的 MCP 支持

内置 [MCP](https://modelcontextprotocol.io/introduction) 支持属于实验性功能。可直接将本地运行的 MCP Server 作为工具传入 SDK：

```python
import os
import asyncio
from datetime import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai

client = genai.Client()

# 创建 stdio 连接参数
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@philschmid/weather-mcp"],
    env=None,
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            prompt = f"What is the weather in London in {datetime.now().strftime('%Y-%m-%d')}?"
            await session.initialize()

            response = await client.aio.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    tools=[session],  # 传入会话，将由 SDK 自动完成 MCP 工具调用
                ),
            )
            print(response.text)

asyncio.run(run())
```

##### Gemini Enterprise Agent Platform 下的 MCP 支持

在 Agent Platform 中使用 MCP 时，在 `generate_content` 的 `Tool.mcp_servers` 中配置所需的服务。平台支持的 MCP 工具列表请参见[官方文档](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/mcp#toolsets)。需要预先安装 `mcp` 依赖（`pip install mcp`）。

```python
import asyncio
from google import genai
from google.genai import types

PROJECT_ID="your-gcp-project"
LOCATION="your-location"

client = genai.Client(enterprise=True, project=PROJECT_ID, location=LOCATION)

async def agent_platform_mcp():
    response = await client.aio.models.generate_content(
        model="gemini-3.8-flash",
        contents=f"List my endpoints in {LOCATION} for my {PROJECT_ID} project.",
        config = types.GenerateContentConfig(
            tools=[
                types.Tool(
                    mcp_servers=[
                        types.McpServer(name='endpoints')
                    ]
                )
            ]
        )
    )

    if response.text:
        print(response.text)

    # 可选：打印模型与 MCP 服务器之间的完整对话交互轨迹
    if response.automatic_function_calling_history:
        for turn in response.automatic_function_calling_history:
            print(f"Role: {turn.role}")
            for part in turn.parts:
                if part.function_call:
                    print(f"  Tool Called: {part.function_call.name}")
                    print(f"  Arguments: {part.function_call.args}")
                elif part.function_response:
                    print(f"  Tool Response: {part.function_response.response}")
            print("-" * 40)

asyncio.run(agent_platform_mcp())
```

### 结构化 JSON 响应架构 (JSON Response Schema)

无论通过何种方式定义模式（Schema），请切勿在 Prompt 中重复给出 JSON Schema 定义或示例，以免降低生成结果的稳定性与质量。

#### 标准 JSON Schema 支持

```python
user_profile = {
    'properties': {
        'age': {
            'anyOf': [
                {'maximum': 20, 'minimum': 0, 'type': 'integer'},
                {'type': 'null'},
            ],
            'title': 'Age',
        },
        'username': {
            'description': "User's unique name",
            'title': 'Username',
            'type': 'string',
        },
    },
    'required': ['username', 'age'],
    'title': 'User Schema',
    'type': 'object',
}

response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents='Give me a random user profile.',
    config={
        'response_mime_type': 'application/json',
        'response_json_schema': user_profile
    },
)
print(response.text)
```

#### Pydantic 模型 Schema 支持

可直接将 Pydantic 数据类作为结构化输出格式：

```python
from pydantic import BaseModel
from google.genai import types

class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_json_schema=CountryInfo.model_json_schema(),
    ),
)
print(response.text)
```

### 同步流式生成 (Synchronous Streaming)

以流式方式接收模型输出，逐块返回而非等待一次性生成完毕：

#### 纯文本流式生成

```python
for chunk in client.models.generate_content_stream(
    model='gemini-3.8-flash', contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

#### 多模态图像流式生成

对于存储在 [Google Cloud Storage](https://cloud.google.com/storage) 中的图像，使用 `from_uri` 构造 `Part`：

```python
from google.genai import types

for chunk in client.models.generate_content_stream(
    model='gemini-3.8-flash',
    contents=[
        'What is this image about?',
        types.Part.from_uri(
            file_uri='gs://generativeai-downloads/images/scones.jpg',
            mime_type='image/jpeg',
        ),
    ],
):
    print(chunk.text, end='')
```

对于本地文件，可读取为字节后通过 `from_bytes` 构造：

```python
from google.genai import types

YOUR_IMAGE_PATH = 'your_image_path'
YOUR_IMAGE_MIME_TYPE = 'your_image_mime_type'
with open(YOUR_IMAGE_PATH, 'rb') as f:
    image_bytes = f.read()

for chunk in client.models.generate_content_stream(
    model='gemini-3.8-flash',
    contents=[
        'What is this image about?',
        types.Part.from_bytes(data=image_bytes, mime_type=YOUR_IMAGE_MIME_TYPE),
    ],
):
    print(chunk.text, end='')
```

### 异步非流式生成 (Asynchronous Non Streaming)

`client.aio` 为 `client` 上的所有操作模块提供了对应的 [`async` 异步方法](https://docs.python.org/3/library/asyncio.html)。

例如 `client.aio.models.generate_content` 即为 `client.models.generate_content` 的异步对应接口：

```python
response = await client.aio.models.generate_content(
    model='gemini-3.8-flash', contents='Tell me a story in 300 words.'
)

print(response.text)
```

### 异步流式生成 (Asynchronous Streaming)

```python
async for chunk in await client.aio.models.generate_content_stream(
    model='gemini-3.8-flash', contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

### Token 计数与计算 (Count & Compute Tokens)

```python
response = client.models.count_tokens(
    model='gemini-3.8-flash',
    contents='why is the sky blue?',
)
print(response)
```

#### 计算 Tokens (Compute Tokens)

该接口仅在 Gemini Enterprise Agent Platform 中受支持：

```python
response = client.models.compute_tokens(
    model='gemini-3.8-flash',
    contents='why is the sky blue?',
)
print(response)
```

#### 本地分词器离线计算 (Local Tokenizer)

本地分词计算需要安装额外的可选依赖。对于 SentencePiece 分词模型（如 `gemini-2.5-flash`），仅需安装轻量版；对于采用 Gemma 4 分词器的模型（如 `gemini-3.5-flash`），还需额外引入 Transformers 与 PyTorch：

```sh
# 仅适用于 SentencePiece 模型
pip install "google-genai[local-tokenizer]"
# 适用于使用 Gemma 4 分词器的模型（包含 Transformers 与 PyTorch）
pip install "google-genai[local-tokenizer-transformers]"
```

```python
from google.genai import local_tokenizer

tokenizer = local_tokenizer.LocalTokenizer(model_name='gemini-3.8-flash')
result = tokenizer.count_tokens("What is your name?")
print(result)
```

### 文本向量嵌入 (Embed Content)

```python
response = client.models.embed_content(
    model='gemini-embedding-001',
    contents='why is the sky blue?',
)
print(response)
```

支持批量输入与设置截断输出维度：

```python
from google.genai import types

response = client.models.embed_content(
    model='gemini-embedding-001',
    contents=['why is the sky blue?', 'What is your age?'],
    config=types.EmbedContentConfig(output_dimensionality=10),
)

print(response)
```

### Imagen 图像生成与编辑

#### 生成图像 (Generate Images)

```python
from google.genai import types

response1 = client.models.generate_images(
    model='imagen-4.0-generate-001',
    prompt='An umbrella in the foreground, and a rainy night sky in the background',
    config=types.GenerateImagesConfig(
        number_of_images=1,
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response1.generated_images[0].image.show()
```

#### 图像超分辨率放大 (Upscale Image)

仅在 Gemini Enterprise Agent Platform 中支持：

```python
from google.genai import types

response2 = client.models.upscale_image(
    model='imagen-4.0-upscale-preview',
    image=response1.generated_images[0].image,
    upscale_factor='x2',
    config=types.UpscaleImageConfig(
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response2.generated_images[0].image.show()
```

#### 图像编辑与修复 (Edit Image)

图像编辑使用独立的专用模型。仅在 Gemini Enterprise Agent Platform 中受支持：

```python
from google.genai import types
from google.genai.types import RawReferenceImage, MaskReferenceImage

raw_ref_image = RawReferenceImage(
    reference_id=1,
    reference_image=response1.generated_images[0].image,
)

# 由模型自动识别背景并计算 Mask 遮罩
mask_ref_image = MaskReferenceImage(
    reference_id=2,
    config=types.MaskReferenceConfig(
        mask_mode='MASK_MODE_BACKGROUND',
        mask_dilation=0,
    ),
)

response3 = client.models.edit_image(
    model='imagen-3.0-capability-001',
    prompt='Sunlight and clear sky',
    reference_images=[raw_ref_image, mask_ref_image],
    config=types.EditImageConfig(
        edit_mode='EDIT_MODE_INPAINT_INSERTION',
        number_of_images=1,
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response3.generated_images[0].image.show()
```

### Veo 视频生成

当前仅 Gemini Enterprise Agent Platform 支持视频生成。

#### 文生视频 (Text to Video)

```python
import time
from google import genai
from google.genai import types

client = genai.Client(vertexai=True)

# 创建异步生成任务
operation = client.models.generate_videos(
    model='veo-3.1-generate-001',
    source=types.GenerateVideosSource(
        prompt='A neon hologram of a cat driving at top speed',
    ),
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)

# 轮询直至任务完成
while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0].video
video.show()
```

#### 图生视频 (Image to Video)

```python
import time
from google import genai
from google.genai import types

client = genai.Client(vertexai=True)

image = types.Image.from_file(location="local/path/file.png")

operation = client.models.generate_videos(
    model='veo-3.1-generate-001',
    source=types.GenerateVideosSource(
        prompt='Night sky',
        image=image,
    ),
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)

while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0].video
video.show()
```

#### 视频延展 / 视频生视频 (Video to Video)

```python
import time
from google import genai
from google.genai import types

client = genai.Client(vertexai=True)

video = types.Video.from_file("local/path/video.mp4")

operation = client.models.generate_videos(
    model='veo-3.1-generate-001',
    source=types.GenerateVideosSource(
        prompt='Night sky',
        video=types.Video(
            uri="gs://bucket-name/inputs/videos/cat_driving.mp4",
        ),
    ),
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)

while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0].video
video.show()
```

## 多轮对话 (Chats)

创建对话会话即可开启与模型的多轮交互。在同一会话中多次调用 `chat.send_message` 可使模型在上下文中保留历史对话记忆。

### 同步非流式对话

```python
chat = client.chats.create(model='gemini-3.8-flash')
response = chat.send_message('tell me a story')
print(response.text)
response = chat.send_message('summarize the story you told me in 1 sentence')
print(response.text)
```

### 同步流式对话

```python
chat = client.chats.create(model='gemini-3.8-flash')
for chunk in chat.send_message_stream('tell me a story'):
    print(chunk.text)
```

### 异步非流式对话

```python
chat = client.aio.chats.create(model='gemini-3.8-flash')
response = await chat.send_message('tell me a story')
print(response.text)
```

### 异步流式对话

```python
chat = client.aio.chats.create(model='gemini-3.8-flash')
async for chunk in await chat.send_message_stream('tell me a story'):
    print(chunk.text)
```

## 文件管理 (Files)

文件管理 API 仅适用于 Gemini Developer API。

```sh
!gcloud storage cp gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf .
!gcloud storage cp gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf .
```

### 上传文件

```python
file1 = client.files.upload(file='2312.11805v3.pdf')
file2 = client.files.upload(file='2403.05530.pdf')

print(file1)
print(file2)
```

### 查询文件信息

```python
file1 = client.files.upload(file='2312.11805v3.pdf')
file_info = client.files.get(name=file1.name)
print(file_info)
```

### 删除文件

```python
file3 = client.files.upload(file='2312.11805v3.pdf')
client.files.delete(name=file3.name)
```

## 上下文缓存 (Caches)

`client.caches` 提供了缓存内容的控制平面 API，可在高频大上下文请求中显著降低推理成本与延迟。

### 创建缓存

```python
from google.genai import types

if client.enterprise:
    file_uris = [
        'gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf',
        'gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf',
    ]
else:
    file_uris = [file1.uri, file2.uri]

cached_content = client.caches.create(
    model='gemini-3.8-flash',
    config=types.CreateCachedContentConfig(
        contents=[
            types.Content(
                role='user',
                parts=[
                    types.Part.from_uri(
                        file_uri=file_uris[0], mime_type='application/pdf'
                    ),
                    types.Part.from_uri(
                        file_uri=file_uris[1],
                        mime_type='application/pdf',
                    ),
                ],
            )
        ],
        system_instruction='What is the sum of the two pdfs?',
        display_name='test cache',
        ttl='3600s',
    ),
)
```

### 获取缓存信息

```python
cached_content = client.caches.get(name=cached_content.name)
```

### 使用缓存生成内容

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents='Summarize the pdfs',
    config=types.GenerateContentConfig(
        cached_content=cached_content.name,
    ),
)
print(response.text)
```

## Interactions API（统一交互与智能体接口）

Interactions API 是与 Gemini 模型与自主智能体进行交互的统一接口。它大幅简化了状态管理、工具编排调度以及长时间运行任务的管理。

详情请参考[官方 Interactions 文档](https://aistudio.google.com/docs/interactions-overview)。

### 基础交互

```python
interaction = client.interactions.create(
    model='gemini-3.8-flash',
    input='Tell me a short joke about programming.'
)
print(interaction.output_text)
```

### 服务端有状态对话 (Stateful Conversation)

Interactions API 内置服务端状态管理，可通过传入 `previous_interaction_id` 轻松延续历史对话：

```python
# 1. 第一轮交互
interaction1 = client.interactions.create(
    model='gemini-3.8-flash',
    input='Hi, my name is Amir.'
)
print(f"Model: {interaction1.output_text}")

# 2. 第二轮交互（传递 previous_interaction_id）
interaction2 = client.interactions.create(
    model='gemini-3.8-flash',
    input='What is my name?',
    previous_interaction_id=interaction1.id
)
print(f"Model: {interaction2.output_text}")
```

### 深度调研智能体 (Agents: Deep Research)

针对复杂的调研分析任务，可直接调用专用智能体（如 `deep-research-preview-04-2026`）：

```python
import time

# 1. 启动 Deep Research 后台异步智能体任务
initial_interaction = client.interactions.create(
    input='Research the history of the Google TPUs with a focus on 2025 and 2026.',
    agent='deep-research-preview-04-2026',
    background=True
)
print(f"Research started. Interaction ID: {initial_interaction.id}")

# 2. 轮询结果
while True:
    interaction = client.interactions.get(id=initial_interaction.id)
    print(f"Status: {interaction.status}")

    if interaction.status == "completed":
        print("\nFinal Report:\n", interaction.output_text)
        break
    elif interaction.status in ["failed", "cancelled"]:
        print(f"Failed with status: {interaction.status}")
        break

    time.sleep(10)
```

### 多模态输入

可在输入列表中灵活混入多模态数据（文本、图像、音频等）：

```python
import base64

# 假设已有以字节格式载入的图像数据
# base64_image = ...

interaction = client.interactions.create(
    model='gemini-3.8-flash',
    input=[
        {'type': 'text', 'text': 'Describe the image.'},
        {'type': 'image', 'data': base64_image, 'mime_type': 'image/png'}
    ]
)
print(interaction.output_text)
```

### 函数与工具调用

可为模型定义自定义工具函数。Interactions API 会智能选择工具，并由开发者回传执行结果：

```python
# 1. 定义工具
def get_weather(location: str):
    """Gets the weather for a given location."""
    return f"The weather in {location} is sunny."

weather_tool = {
    'type': 'function',
    'name': 'get_weather',
    'description': 'Gets the weather for a given location.',
    'parameters': {
        'type': 'object',
        'properties': {
            'location': {'type': 'string', 'description': 'The city and state, e.g. San Francisco, CA'}
        },
        'required': ['location']
    }
}

# 2. 发起附带工具的请求
interaction = client.interactions.create(
    model='gemini-3.8-flash',
    input='What is the weather in Mountain View, CA?',
    tools=[weather_tool]
)

# 3. 处理工具调用
for step in (interaction.steps or []):
    if step.type == 'function_call':
        print(f"Tool Call: {step.name}({step.arguments})")

        # 执行本地业务函数
        result = get_weather(**step.arguments)

        # 将结果回传给模型
        interaction = client.interactions.create(
            model='gemini-3.8-flash',
            previous_interaction_id=interaction.id,
            input=[{
                'type': 'function_result',
                'name': step.name,
                'call_id': step.id,
                'result': result
            }]
        )
        print(f"Response: {interaction.output_text}")
```

### 原生内置工具 (Built-in Tools)

可以直接启用 Google 官方托管的原生内置工具：**Google 搜索接地**（Google Search）与**代码解释器**（Code Execution）。

#### Google Search 搜索接地

```python
interaction = client.interactions.create(
    model='gemini-3.8-flash',
    input='Who won the last Super Bowl?',
    tools=[{'type': 'google_search'}]
)
print(interaction.output_text)
```

#### 代码执行 (Code Execution)

```python
interaction = client.interactions.create(
    model='gemini-3.8-flash',
    input='Calculate the 50th Fibonacci number.',
    tools=[{'type': 'code_execution'}]
)
print(interaction.output_text)
```

### 多模态输出

Interactions API 支持直接生成多模态输出（如图像或音频），需在请求中指定 `response_modalities`。

#### 图像输出

```python
import base64

interaction = client.interactions.create(
    model='gemini-3.1-flash-lite-image',
    input='Generate an image of a futuristic city.',
    response_modalities=['IMAGE']
)

if interaction.output_image:
    print(f"Generated image with mime_type: {interaction.output_image.mime_type}")
    with open("generated_city.png", "wb") as f:
        f.write(base64.b64decode(interaction.output_image.data))
```

#### 音频输出

```python
import base64

interaction = client.interactions.create(
    model='gemini-3.8-flash-tts',
    input='Say hello and give a one sentence motivational quote.',
    response_modalities=['AUDIO']
)

if interaction.output_audio:
    print(f"Generated audio with mime_type: {interaction.output_audio.mime_type}")
    with open("greeting.wav", "wb") as f:
        f.write(base64.b64decode(interaction.output_audio.data))
```

## 模型微调 (Tunings)

`client.tunings` 提供了微调任务管理接口，并通过 `tune` 方法支持有监督微调（Supervised Fine-Tuning）。当前仅在 Gemini Enterprise Agent Platform 中支持。

### 发起微调 (Tune)

- 支持自 GCS 存储源或 [Gemini Enterprise Agent Platform 多模态数据集](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/datasets) 发起微调。

```python
from google.genai import types

model = 'gemini-3.8-flash'
training_dataset = types.TuningDataset(
    gcs_uri='gs://your-gcs-bucket/your-tuning-data.jsonl',
)

tuning_job = client.tunings.tune(
    base_model=model,
    training_dataset=training_dataset,
    config=types.CreateTuningJobConfig(
        epoch_count=1, tuned_model_display_name='test_dataset_examples model'
    ),
)
print(tuning_job)
```

### 查询微调任务 (Get Tuning Job)

```python
import time

tuning_job = client.tunings.get(name=tuning_job.name)

completed_states = set(
    [
        'JOB_STATE_SUCCEEDED',
        'JOB_STATE_FAILED',
        'JOB_STATE_CANCELLED',
    ]
)

while tuning_job.state not in completed_states:
    print(tuning_job.state)
    tuning_job = client.tunings.get(name=tuning_job.name)
    time.sleep(10)
```

#### 调用微调后的模型

```python
response = client.models.generate_content(
    model=tuning_job.tuned_model.endpoint,
    contents='why is the sky blue?',
)
print(response.text)
```

### 获取微调模型元数据 (Get Tuned Model)

```python
tuned_model = client.models.get(model=tuning_job.tuned_model.model)
print(tuned_model)
```

### 列出已微调模型 (List Tuned Models)

```python
for model in client.models.list(config={'page_size': 10, 'query_base': False}):
    print(model)
```

```python
pager = client.models.list(config={'page_size': 10, 'query_base': False})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

#### 异步列出微调模型

```python
async for job in await client.aio.models.list(config={'page_size': 10, 'query_base': False}):
    print(job)
```

### 更新微调模型信息 (Update Tuned Model)

```python
from google.genai import types

model = pager[0]

model = client.models.update(
    model=model.name,
    config=types.UpdateModelConfig(
        display_name='my tuned model', description='my tuned model description'
    ),
)
print(model)
```

### 列出微调任务 (List Tuning Jobs)

```python
for job in client.tunings.list(config={'page_size': 10}):
    print(job)
```

## 批量离线预测 (Batch Prediction)

批量预测允许对大规模请求进行高吞吐离线推理，享受大幅度的折扣计费。

### 创建批量任务

```python
from google.genai import types
import time

# 方式一：上传 JSONL 请求文件
file = client.files.upload(
    file='myrequests.json',
    config=types.UploadFileConfig(display_name='test-json')
)

# 方式二：使用已上传的文件创建批量任务
batch_job = client.batches.create(
    model="gemini-3.8-flash",
    src="files/test-json",
)

# 轮询批量任务状态
job = client.batches.get(name=batch_job.name)

completed_states = set(
    [
        'JOB_STATE_SUCCEEDED',
        'JOB_STATE_FAILED',
        'JOB_STATE_CANCELLED',
        'JOB_STATE_PAUSED',
    ]
)

while job.state not in completed_states:
    print(job.state)
    job = client.batches.get(name=job.name)
    time.sleep(30)

print("Job completed:", job)
```

### 列出批量任务 (List)

```python
for job in client.batches.list(config=types.ListBatchJobsConfig(page_size=10)):
    print(job)
```

### 删除批量任务 (Delete)

```python
delete_job = client.batches.delete(name=job.name)
print(delete_job)
```

## 异常与错误处理 (Error Handling)

为便于捕获与处理模型服务抛出的各种异常，SDK 提供了专用的 [`APIError`](https://github.com/googleapis/python-genai/blob/main/google/genai/errors.py) 错误类：

```python
from google.genai import errors

try:
    client.models.generate_content(
        model="invalid-model-name",
        contents="What is your name?",
    )
except errors.APIError as e:
    print(e.code) # 例如 404
    print(e.message)
```

## 透传额外请求体 (Extra Request Body)

`HttpOptions` 中的 `extra_body` 字段接收包含额外 JSON 属性的字典，这些属性将被原样合并进向后端发起的请求体中。该功能常用于尝鲜体验或调用 SDK 尚未正式包装的后端新特性与实验性功能。字典的层级结构必须与后端 API 的 REST 模式完全吻合：

- Gemini Enterprise Agent Platform 后端 API 文档：https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest
- Gemini API 后端 API 文档：https://aistudio.google.com/api-reference

```python
from google.genai import types

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="What is the weather in Boston? and how about Sunnyvale?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        http_options=types.HttpOptions(extra_body={'tool_config': {'function_calling_config': {'mode': 'COMPOSITIONAL'}}}),
    ),
)
```

---

## 许可证 (License)

本 SDK 遵循 [Apache 2.0 许可证](LICENSE)。
