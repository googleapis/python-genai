# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
from typing import AsyncIterator, Iterator, Optional, Union
from urllib.parse import urlencode
from . import _common
from . import _extra_utils
from . import _transformers as t
from . import types
from ._api_client import ApiClient
from ._common import get_value_by_path as getv
from ._common import set_value_by_path as setv
from .pagers import AsyncPager, Pager


def _Part_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['video_metadata']):
    raise ValueError('video_metadata parameter is not supported in Google AI.')

  if getv(from_object, ['code_execution_result']) is not None:
    setv(
        to_object,
        ['codeExecutionResult'],
        getv(from_object, ['code_execution_result']),
    )

  if getv(from_object, ['executable_code']) is not None:
    setv(to_object, ['executableCode'], getv(from_object, ['executable_code']))

  if getv(from_object, ['file_data']) is not None:
    setv(to_object, ['fileData'], getv(from_object, ['file_data']))

  if getv(from_object, ['function_call']) is not None:
    setv(to_object, ['functionCall'], getv(from_object, ['function_call']))

  if getv(from_object, ['function_response']) is not None:
    setv(
        to_object,
        ['functionResponse'],
        getv(from_object, ['function_response']),
    )

  if getv(from_object, ['inline_data']) is not None:
    setv(to_object, ['inlineData'], getv(from_object, ['inline_data']))

  if getv(from_object, ['text']) is not None:
    setv(to_object, ['text'], getv(from_object, ['text']))

  return to_object


def _Part_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['video_metadata']) is not None:
    setv(to_object, ['videoMetadata'], getv(from_object, ['video_metadata']))

  if getv(from_object, ['code_execution_result']) is not None:
    setv(
        to_object,
        ['codeExecutionResult'],
        getv(from_object, ['code_execution_result']),
    )

  if getv(from_object, ['executable_code']) is not None:
    setv(to_object, ['executableCode'], getv(from_object, ['executable_code']))

  if getv(from_object, ['file_data']) is not None:
    setv(to_object, ['fileData'], getv(from_object, ['file_data']))

  if getv(from_object, ['function_call']) is not None:
    setv(to_object, ['functionCall'], getv(from_object, ['function_call']))

  if getv(from_object, ['function_response']) is not None:
    setv(
        to_object,
        ['functionResponse'],
        getv(from_object, ['function_response']),
    )

  if getv(from_object, ['inline_data']) is not None:
    setv(to_object, ['inlineData'], getv(from_object, ['inline_data']))

  if getv(from_object, ['text']) is not None:
    setv(to_object, ['text'], getv(from_object, ['text']))

  return to_object


def _Content_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['parts']) is not None:
    setv(
        to_object,
        ['parts'],
        [
            _Part_to_mldev(api_client, item, to_object)
            for item in getv(from_object, ['parts'])
        ],
    )

  if getv(from_object, ['role']) is not None:
    setv(to_object, ['role'], getv(from_object, ['role']))

  return to_object


def _Content_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['parts']) is not None:
    setv(
        to_object,
        ['parts'],
        [
            _Part_to_vertex(api_client, item, to_object)
            for item in getv(from_object, ['parts'])
        ],
    )

  if getv(from_object, ['role']) is not None:
    setv(to_object, ['role'], getv(from_object, ['role']))

  return to_object


def _Schema_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['min_items']):
    raise ValueError('min_items parameter is not supported in Google AI.')

  if getv(from_object, ['example']):
    raise ValueError('example parameter is not supported in Google AI.')

  if getv(from_object, ['property_ordering']):
    raise ValueError(
        'property_ordering parameter is not supported in Google AI.'
    )

  if getv(from_object, ['pattern']):
    raise ValueError('pattern parameter is not supported in Google AI.')

  if getv(from_object, ['minimum']):
    raise ValueError('minimum parameter is not supported in Google AI.')

  if getv(from_object, ['default']):
    raise ValueError('default parameter is not supported in Google AI.')

  if getv(from_object, ['any_of']):
    raise ValueError('any_of parameter is not supported in Google AI.')

  if getv(from_object, ['max_length']):
    raise ValueError('max_length parameter is not supported in Google AI.')

  if getv(from_object, ['title']):
    raise ValueError('title parameter is not supported in Google AI.')

  if getv(from_object, ['min_length']):
    raise ValueError('min_length parameter is not supported in Google AI.')

  if getv(from_object, ['min_properties']):
    raise ValueError('min_properties parameter is not supported in Google AI.')

  if getv(from_object, ['max_items']):
    raise ValueError('max_items parameter is not supported in Google AI.')

  if getv(from_object, ['maximum']):
    raise ValueError('maximum parameter is not supported in Google AI.')

  if getv(from_object, ['nullable']):
    raise ValueError('nullable parameter is not supported in Google AI.')

  if getv(from_object, ['max_properties']):
    raise ValueError('max_properties parameter is not supported in Google AI.')

  if getv(from_object, ['type']) is not None:
    setv(to_object, ['type'], getv(from_object, ['type']))

  if getv(from_object, ['description']) is not None:
    setv(to_object, ['description'], getv(from_object, ['description']))

  if getv(from_object, ['enum']) is not None:
    setv(to_object, ['enum'], getv(from_object, ['enum']))

  if getv(from_object, ['format']) is not None:
    setv(to_object, ['format'], getv(from_object, ['format']))

  if getv(from_object, ['items']) is not None:
    setv(to_object, ['items'], getv(from_object, ['items']))

  if getv(from_object, ['properties']) is not None:
    setv(to_object, ['properties'], getv(from_object, ['properties']))

  if getv(from_object, ['required']) is not None:
    setv(to_object, ['required'], getv(from_object, ['required']))

  return to_object


def _Schema_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['min_items']) is not None:
    setv(to_object, ['minItems'], getv(from_object, ['min_items']))

  if getv(from_object, ['example']) is not None:
    setv(to_object, ['example'], getv(from_object, ['example']))

  if getv(from_object, ['property_ordering']) is not None:
    setv(
        to_object,
        ['propertyOrdering'],
        getv(from_object, ['property_ordering']),
    )

  if getv(from_object, ['pattern']) is not None:
    setv(to_object, ['pattern'], getv(from_object, ['pattern']))

  if getv(from_object, ['minimum']) is not None:
    setv(to_object, ['minimum'], getv(from_object, ['minimum']))

  if getv(from_object, ['default']) is not None:
    setv(to_object, ['default'], getv(from_object, ['default']))

  if getv(from_object, ['any_of']) is not None:
    setv(to_object, ['anyOf'], getv(from_object, ['any_of']))

  if getv(from_object, ['max_length']) is not None:
    setv(to_object, ['maxLength'], getv(from_object, ['max_length']))

  if getv(from_object, ['title']) is not None:
    setv(to_object, ['title'], getv(from_object, ['title']))

  if getv(from_object, ['min_length']) is not None:
    setv(to_object, ['minLength'], getv(from_object, ['min_length']))

  if getv(from_object, ['min_properties']) is not None:
    setv(to_object, ['minProperties'], getv(from_object, ['min_properties']))

  if getv(from_object, ['max_items']) is not None:
    setv(to_object, ['maxItems'], getv(from_object, ['max_items']))

  if getv(from_object, ['maximum']) is not None:
    setv(to_object, ['maximum'], getv(from_object, ['maximum']))

  if getv(from_object, ['nullable']) is not None:
    setv(to_object, ['nullable'], getv(from_object, ['nullable']))

  if getv(from_object, ['max_properties']) is not None:
    setv(to_object, ['maxProperties'], getv(from_object, ['max_properties']))

  if getv(from_object, ['type']) is not None:
    setv(to_object, ['type'], getv(from_object, ['type']))

  if getv(from_object, ['description']) is not None:
    setv(to_object, ['description'], getv(from_object, ['description']))

  if getv(from_object, ['enum']) is not None:
    setv(to_object, ['enum'], getv(from_object, ['enum']))

  if getv(from_object, ['format']) is not None:
    setv(to_object, ['format'], getv(from_object, ['format']))

  if getv(from_object, ['items']) is not None:
    setv(to_object, ['items'], getv(from_object, ['items']))

  if getv(from_object, ['properties']) is not None:
    setv(to_object, ['properties'], getv(from_object, ['properties']))

  if getv(from_object, ['required']) is not None:
    setv(to_object, ['required'], getv(from_object, ['required']))

  return to_object


def _SafetySetting_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['method']):
    raise ValueError('method parameter is not supported in Google AI.')

  if getv(from_object, ['category']) is not None:
    setv(to_object, ['category'], getv(from_object, ['category']))

  if getv(from_object, ['threshold']) is not None:
    setv(to_object, ['threshold'], getv(from_object, ['threshold']))

  return to_object


def _SafetySetting_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['method']) is not None:
    setv(to_object, ['method'], getv(from_object, ['method']))

  if getv(from_object, ['category']) is not None:
    setv(to_object, ['category'], getv(from_object, ['category']))

  if getv(from_object, ['threshold']) is not None:
    setv(to_object, ['threshold'], getv(from_object, ['threshold']))

  return to_object


def _FunctionDeclaration_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['response']):
    raise ValueError('response parameter is not supported in Google AI.')

  if getv(from_object, ['description']) is not None:
    setv(to_object, ['description'], getv(from_object, ['description']))

  if getv(from_object, ['name']) is not None:
    setv(to_object, ['name'], getv(from_object, ['name']))

  if getv(from_object, ['parameters']) is not None:
    setv(to_object, ['parameters'], getv(from_object, ['parameters']))

  return to_object


def _FunctionDeclaration_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['response']) is not None:
    setv(
        to_object,
        ['response'],
        _Schema_to_vertex(
            api_client, getv(from_object, ['response']), to_object
        ),
    )

  if getv(from_object, ['description']) is not None:
    setv(to_object, ['description'], getv(from_object, ['description']))

  if getv(from_object, ['name']) is not None:
    setv(to_object, ['name'], getv(from_object, ['name']))

  if getv(from_object, ['parameters']) is not None:
    setv(to_object, ['parameters'], getv(from_object, ['parameters']))

  return to_object


def _GoogleSearch_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _GoogleSearch_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _DynamicRetrievalConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['mode']) is not None:
    setv(to_object, ['mode'], getv(from_object, ['mode']))

  if getv(from_object, ['dynamic_threshold']) is not None:
    setv(
        to_object,
        ['dynamicThreshold'],
        getv(from_object, ['dynamic_threshold']),
    )

  return to_object


def _DynamicRetrievalConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['mode']) is not None:
    setv(to_object, ['mode'], getv(from_object, ['mode']))

  if getv(from_object, ['dynamic_threshold']) is not None:
    setv(
        to_object,
        ['dynamicThreshold'],
        getv(from_object, ['dynamic_threshold']),
    )

  return to_object


def _GoogleSearchRetrieval_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['dynamic_retrieval_config']) is not None:
    setv(
        to_object,
        ['dynamicRetrievalConfig'],
        _DynamicRetrievalConfig_to_mldev(
            api_client,
            getv(from_object, ['dynamic_retrieval_config']),
            to_object,
        ),
    )

  return to_object


def _GoogleSearchRetrieval_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['dynamic_retrieval_config']) is not None:
    setv(
        to_object,
        ['dynamicRetrievalConfig'],
        _DynamicRetrievalConfig_to_vertex(
            api_client,
            getv(from_object, ['dynamic_retrieval_config']),
            to_object,
        ),
    )

  return to_object


def _Tool_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['function_declarations']) is not None:
    setv(
        to_object,
        ['functionDeclarations'],
        [
            _FunctionDeclaration_to_mldev(api_client, item, to_object)
            for item in getv(from_object, ['function_declarations'])
        ],
    )

  if getv(from_object, ['retrieval']):
    raise ValueError('retrieval parameter is not supported in Google AI.')

  if getv(from_object, ['google_search']) is not None:
    setv(
        to_object,
        ['googleSearch'],
        _GoogleSearch_to_mldev(
            api_client, getv(from_object, ['google_search']), to_object
        ),
    )

  if getv(from_object, ['google_search_retrieval']) is not None:
    setv(
        to_object,
        ['googleSearchRetrieval'],
        _GoogleSearchRetrieval_to_mldev(
            api_client,
            getv(from_object, ['google_search_retrieval']),
            to_object,
        ),
    )

  if getv(from_object, ['code_execution']) is not None:
    setv(to_object, ['codeExecution'], getv(from_object, ['code_execution']))

  return to_object


def _Tool_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['function_declarations']) is not None:
    setv(
        to_object,
        ['functionDeclarations'],
        [
            _FunctionDeclaration_to_vertex(api_client, item, to_object)
            for item in getv(from_object, ['function_declarations'])
        ],
    )

  if getv(from_object, ['retrieval']) is not None:
    setv(to_object, ['retrieval'], getv(from_object, ['retrieval']))

  if getv(from_object, ['google_search']) is not None:
    setv(
        to_object,
        ['googleSearch'],
        _GoogleSearch_to_vertex(
            api_client, getv(from_object, ['google_search']), to_object
        ),
    )

  if getv(from_object, ['google_search_retrieval']) is not None:
    setv(
        to_object,
        ['googleSearchRetrieval'],
        _GoogleSearchRetrieval_to_vertex(
            api_client,
            getv(from_object, ['google_search_retrieval']),
            to_object,
        ),
    )

  if getv(from_object, ['code_execution']) is not None:
    setv(to_object, ['codeExecution'], getv(from_object, ['code_execution']))

  return to_object


def _FunctionCallingConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['mode']) is not None:
    setv(to_object, ['mode'], getv(from_object, ['mode']))

  if getv(from_object, ['allowed_function_names']) is not None:
    setv(
        to_object,
        ['allowedFunctionNames'],
        getv(from_object, ['allowed_function_names']),
    )

  return to_object


def _FunctionCallingConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['mode']) is not None:
    setv(to_object, ['mode'], getv(from_object, ['mode']))

  if getv(from_object, ['allowed_function_names']) is not None:
    setv(
        to_object,
        ['allowedFunctionNames'],
        getv(from_object, ['allowed_function_names']),
    )

  return to_object


def _ToolConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['function_calling_config']) is not None:
    setv(
        to_object,
        ['functionCallingConfig'],
        _FunctionCallingConfig_to_mldev(
            api_client,
            getv(from_object, ['function_calling_config']),
            to_object,
        ),
    )

  return to_object


def _ToolConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['function_calling_config']) is not None:
    setv(
        to_object,
        ['functionCallingConfig'],
        _FunctionCallingConfig_to_vertex(
            api_client,
            getv(from_object, ['function_calling_config']),
            to_object,
        ),
    )

  return to_object


def _PrebuiltVoiceConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['voice_name']) is not None:
    setv(to_object, ['voiceName'], getv(from_object, ['voice_name']))

  return to_object


def _PrebuiltVoiceConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['voice_name']) is not None:
    setv(to_object, ['voiceName'], getv(from_object, ['voice_name']))

  return to_object


def _VoiceConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['prebuilt_voice_config']) is not None:
    setv(
        to_object,
        ['prebuiltVoiceConfig'],
        _PrebuiltVoiceConfig_to_mldev(
            api_client, getv(from_object, ['prebuilt_voice_config']), to_object
        ),
    )

  return to_object


def _VoiceConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['prebuilt_voice_config']) is not None:
    setv(
        to_object,
        ['prebuiltVoiceConfig'],
        _PrebuiltVoiceConfig_to_vertex(
            api_client, getv(from_object, ['prebuilt_voice_config']), to_object
        ),
    )

  return to_object


def _SpeechConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['voice_config']) is not None:
    setv(
        to_object,
        ['voiceConfig'],
        _VoiceConfig_to_mldev(
            api_client, getv(from_object, ['voice_config']), to_object
        ),
    )

  return to_object


def _SpeechConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['voice_config']) is not None:
    setv(
        to_object,
        ['voiceConfig'],
        _VoiceConfig_to_vertex(
            api_client, getv(from_object, ['voice_config']), to_object
        ),
    )

  return to_object


def _GenerateContentConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['system_instruction']) is not None:
    setv(
        parent_object,
        ['systemInstruction'],
        _Content_to_mldev(
            api_client,
            t.t_content(api_client, getv(from_object, ['system_instruction'])),
            to_object,
        ),
    )

  if getv(from_object, ['temperature']) is not None:
    setv(to_object, ['temperature'], getv(from_object, ['temperature']))

  if getv(from_object, ['top_p']) is not None:
    setv(to_object, ['topP'], getv(from_object, ['top_p']))

  if getv(from_object, ['top_k']) is not None:
    setv(to_object, ['topK'], getv(from_object, ['top_k']))

  if getv(from_object, ['candidate_count']) is not None:
    setv(to_object, ['candidateCount'], getv(from_object, ['candidate_count']))

  if getv(from_object, ['max_output_tokens']) is not None:
    setv(
        to_object, ['maxOutputTokens'], getv(from_object, ['max_output_tokens'])
    )

  if getv(from_object, ['stop_sequences']) is not None:
    setv(to_object, ['stopSequences'], getv(from_object, ['stop_sequences']))

  if getv(from_object, ['response_logprobs']):
    raise ValueError(
        'response_logprobs parameter is not supported in Google AI.'
    )

  if getv(from_object, ['logprobs']):
    raise ValueError('logprobs parameter is not supported in Google AI.')

  if getv(from_object, ['presence_penalty']) is not None:
    setv(
        to_object, ['presencePenalty'], getv(from_object, ['presence_penalty'])
    )

  if getv(from_object, ['frequency_penalty']) is not None:
    setv(
        to_object,
        ['frequencyPenalty'],
        getv(from_object, ['frequency_penalty']),
    )

  if getv(from_object, ['seed']) is not None:
    setv(to_object, ['seed'], getv(from_object, ['seed']))

  if getv(from_object, ['response_mime_type']) is not None:
    setv(
        to_object,
        ['responseMimeType'],
        getv(from_object, ['response_mime_type']),
    )

  if getv(from_object, ['response_schema']) is not None:
    setv(
        to_object,
        ['responseSchema'],
        _Schema_to_mldev(
            api_client,
            t.t_schema(api_client, getv(from_object, ['response_schema'])),
            to_object,
        ),
    )

  if getv(from_object, ['routing_config']):
    raise ValueError('routing_config parameter is not supported in Google AI.')

  if getv(from_object, ['safety_settings']) is not None:
    setv(
        parent_object,
        ['safetySettings'],
        [
            _SafetySetting_to_mldev(api_client, item, to_object)
            for item in getv(from_object, ['safety_settings'])
        ],
    )

  if getv(from_object, ['tools']) is not None:
    setv(
        parent_object,
        ['tools'],
        [
            _Tool_to_mldev(api_client, t.t_tool(api_client, item), to_object)
            for item in t.t_tools(api_client, getv(from_object, ['tools']))
        ],
    )

  if getv(from_object, ['tool_config']) is not None:
    setv(
        parent_object,
        ['toolConfig'],
        _ToolConfig_to_mldev(
            api_client, getv(from_object, ['tool_config']), to_object
        ),
    )

  if getv(from_object, ['cached_content']) is not None:
    setv(
        parent_object,
        ['cachedContent'],
        t.t_cached_content_name(
            api_client, getv(from_object, ['cached_content'])
        ),
    )

  if getv(from_object, ['response_modalities']) is not None:
    setv(
        to_object,
        ['responseModalities'],
        getv(from_object, ['response_modalities']),
    )

  if getv(from_object, ['media_resolution']):
    raise ValueError(
        'media_resolution parameter is not supported in Google AI.'
    )

  if getv(from_object, ['speech_config']) is not None:
    setv(
        to_object,
        ['speechConfig'],
        _SpeechConfig_to_mldev(
            api_client,
            t.t_speech_config(api_client, getv(from_object, ['speech_config'])),
            to_object,
        ),
    )

  return to_object


def _GenerateContentConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['system_instruction']) is not None:
    setv(
        parent_object,
        ['systemInstruction'],
        _Content_to_vertex(
            api_client,
            t.t_content(api_client, getv(from_object, ['system_instruction'])),
            to_object,
        ),
    )

  if getv(from_object, ['temperature']) is not None:
    setv(to_object, ['temperature'], getv(from_object, ['temperature']))

  if getv(from_object, ['top_p']) is not None:
    setv(to_object, ['topP'], getv(from_object, ['top_p']))

  if getv(from_object, ['top_k']) is not None:
    setv(to_object, ['topK'], getv(from_object, ['top_k']))

  if getv(from_object, ['candidate_count']) is not None:
    setv(to_object, ['candidateCount'], getv(from_object, ['candidate_count']))

  if getv(from_object, ['max_output_tokens']) is not None:
    setv(
        to_object, ['maxOutputTokens'], getv(from_object, ['max_output_tokens'])
    )

  if getv(from_object, ['stop_sequences']) is not None:
    setv(to_object, ['stopSequences'], getv(from_object, ['stop_sequences']))

  if getv(from_object, ['response_logprobs']) is not None:
    setv(
        to_object,
        ['responseLogprobs'],
        getv(from_object, ['response_logprobs']),
    )

  if getv(from_object, ['logprobs']) is not None:
    setv(to_object, ['logprobs'], getv(from_object, ['logprobs']))

  if getv(from_object, ['presence_penalty']) is not None:
    setv(
        to_object, ['presencePenalty'], getv(from_object, ['presence_penalty'])
    )

  if getv(from_object, ['frequency_penalty']) is not None:
    setv(
        to_object,
        ['frequencyPenalty'],
        getv(from_object, ['frequency_penalty']),
    )

  if getv(from_object, ['seed']) is not None:
    setv(to_object, ['seed'], getv(from_object, ['seed']))

  if getv(from_object, ['response_mime_type']) is not None:
    setv(
        to_object,
        ['responseMimeType'],
        getv(from_object, ['response_mime_type']),
    )

  if getv(from_object, ['response_schema']) is not None:
    setv(
        to_object,
        ['responseSchema'],
        _Schema_to_vertex(
            api_client,
            t.t_schema(api_client, getv(from_object, ['response_schema'])),
            to_object,
        ),
    )

  if getv(from_object, ['routing_config']) is not None:
    setv(to_object, ['routingConfig'], getv(from_object, ['routing_config']))

  if getv(from_object, ['safety_settings']) is not None:
    setv(
        parent_object,
        ['safetySettings'],
        [
            _SafetySetting_to_vertex(api_client, item, to_object)
            for item in getv(from_object, ['safety_settings'])
        ],
    )

  if getv(from_object, ['tools']) is not None:
    setv(
        parent_object,
        ['tools'],
        [
            _Tool_to_vertex(api_client, t.t_tool(api_client, item), to_object)
            for item in t.t_tools(api_client, getv(from_object, ['tools']))
        ],
    )

  if getv(from_object, ['tool_config']) is not None:
    setv(
        parent_object,
        ['toolConfig'],
        _ToolConfig_to_vertex(
            api_client, getv(from_object, ['tool_config']), to_object
        ),
    )

  if getv(from_object, ['cached_content']) is not None:
    setv(
        parent_object,
        ['cachedContent'],
        t.t_cached_content_name(
            api_client, getv(from_object, ['cached_content'])
        ),
    )

  if getv(from_object, ['response_modalities']) is not None:
    setv(
        to_object,
        ['responseModalities'],
        getv(from_object, ['response_modalities']),
    )

  if getv(from_object, ['media_resolution']) is not None:
    setv(
        to_object, ['mediaResolution'], getv(from_object, ['media_resolution'])
    )

  if getv(from_object, ['speech_config']) is not None:
    setv(
        to_object,
        ['speechConfig'],
        _SpeechConfig_to_vertex(
            api_client,
            t.t_speech_config(api_client, getv(from_object, ['speech_config'])),
            to_object,
        ),
    )

  return to_object


def _GenerateContentParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['contents']) is not None:
    setv(
        to_object,
        ['contents'],
        [
            _Content_to_mldev(api_client, item, to_object)
            for item in t.t_contents(
                api_client, getv(from_object, ['contents'])
            )
        ],
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['generationConfig'],
        _GenerateContentConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _GenerateContentParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['contents']) is not None:
    setv(
        to_object,
        ['contents'],
        [
            _Content_to_vertex(api_client, item, to_object)
            for item in t.t_contents(
                api_client, getv(from_object, ['contents'])
            )
        ],
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['generationConfig'],
        _GenerateContentConfig_to_vertex(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _EmbedContentConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['task_type']) is not None:
    setv(
        parent_object,
        ['requests[]', 'taskType'],
        getv(from_object, ['task_type']),
    )

  if getv(from_object, ['title']) is not None:
    setv(parent_object, ['requests[]', 'title'], getv(from_object, ['title']))

  if getv(from_object, ['output_dimensionality']) is not None:
    setv(
        parent_object,
        ['requests[]', 'outputDimensionality'],
        getv(from_object, ['output_dimensionality']),
    )

  if getv(from_object, ['mime_type']):
    raise ValueError('mime_type parameter is not supported in Google AI.')

  if getv(from_object, ['auto_truncate']):
    raise ValueError('auto_truncate parameter is not supported in Google AI.')

  return to_object


def _EmbedContentConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['task_type']) is not None:
    setv(
        parent_object,
        ['instances[]', 'task_type'],
        getv(from_object, ['task_type']),
    )

  if getv(from_object, ['title']) is not None:
    setv(parent_object, ['instances[]', 'title'], getv(from_object, ['title']))

  if getv(from_object, ['output_dimensionality']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputDimensionality'],
        getv(from_object, ['output_dimensionality']),
    )

  if getv(from_object, ['mime_type']) is not None:
    setv(
        parent_object,
        ['instances[]', 'mimeType'],
        getv(from_object, ['mime_type']),
    )

  if getv(from_object, ['auto_truncate']) is not None:
    setv(
        parent_object,
        ['parameters', 'autoTruncate'],
        getv(from_object, ['auto_truncate']),
    )

  return to_object


def _EmbedContentParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['contents']) is not None:
    setv(
        to_object,
        ['requests[]', 'content'],
        t.t_contents_for_embed(api_client, getv(from_object, ['contents'])),
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _EmbedContentConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  setv(
      to_object,
      ['requests[]', 'model'],
      t.t_model(api_client, getv(from_object, ['model'])),
  )
  return to_object


def _EmbedContentParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['contents']) is not None:
    setv(
        to_object,
        ['instances[]', 'content'],
        t.t_contents_for_embed(api_client, getv(from_object, ['contents'])),
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _EmbedContentConfig_to_vertex(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _GenerateImageConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['output_gcs_uri']):
    raise ValueError('output_gcs_uri parameter is not supported in Google AI.')

  if getv(from_object, ['negative_prompt']) is not None:
    setv(
        parent_object,
        ['parameters', 'negativePrompt'],
        getv(from_object, ['negative_prompt']),
    )

  if getv(from_object, ['number_of_images']) is not None:
    setv(
        parent_object,
        ['parameters', 'sampleCount'],
        getv(from_object, ['number_of_images']),
    )

  if getv(from_object, ['guidance_scale']) is not None:
    setv(
        parent_object,
        ['parameters', 'guidanceScale'],
        getv(from_object, ['guidance_scale']),
    )

  if getv(from_object, ['seed']):
    raise ValueError('seed parameter is not supported in Google AI.')

  if getv(from_object, ['safety_filter_level']) is not None:
    setv(
        parent_object,
        ['parameters', 'safetySetting'],
        getv(from_object, ['safety_filter_level']),
    )

  if getv(from_object, ['person_generation']) is not None:
    setv(
        parent_object,
        ['parameters', 'personGeneration'],
        getv(from_object, ['person_generation']),
    )

  if getv(from_object, ['include_safety_attributes']) is not None:
    setv(
        parent_object,
        ['parameters', 'includeSafetyAttributes'],
        getv(from_object, ['include_safety_attributes']),
    )

  if getv(from_object, ['include_rai_reason']) is not None:
    setv(
        parent_object,
        ['parameters', 'includeRaiReason'],
        getv(from_object, ['include_rai_reason']),
    )

  if getv(from_object, ['language']) is not None:
    setv(
        parent_object,
        ['parameters', 'language'],
        getv(from_object, ['language']),
    )

  if getv(from_object, ['output_mime_type']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'mimeType'],
        getv(from_object, ['output_mime_type']),
    )

  if getv(from_object, ['output_compression_quality']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'compressionQuality'],
        getv(from_object, ['output_compression_quality']),
    )

  if getv(from_object, ['add_watermark']):
    raise ValueError('add_watermark parameter is not supported in Google AI.')

  if getv(from_object, ['aspect_ratio']) is not None:
    setv(
        parent_object,
        ['parameters', 'aspectRatio'],
        getv(from_object, ['aspect_ratio']),
    )

  return to_object


def _GenerateImageConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['output_gcs_uri']) is not None:
    setv(
        parent_object,
        ['parameters', 'storageUri'],
        getv(from_object, ['output_gcs_uri']),
    )

  if getv(from_object, ['negative_prompt']) is not None:
    setv(
        parent_object,
        ['parameters', 'negativePrompt'],
        getv(from_object, ['negative_prompt']),
    )

  if getv(from_object, ['number_of_images']) is not None:
    setv(
        parent_object,
        ['parameters', 'sampleCount'],
        getv(from_object, ['number_of_images']),
    )

  if getv(from_object, ['guidance_scale']) is not None:
    setv(
        parent_object,
        ['parameters', 'guidanceScale'],
        getv(from_object, ['guidance_scale']),
    )

  if getv(from_object, ['seed']) is not None:
    setv(parent_object, ['parameters', 'seed'], getv(from_object, ['seed']))

  if getv(from_object, ['safety_filter_level']) is not None:
    setv(
        parent_object,
        ['parameters', 'safetySetting'],
        getv(from_object, ['safety_filter_level']),
    )

  if getv(from_object, ['person_generation']) is not None:
    setv(
        parent_object,
        ['parameters', 'personGeneration'],
        getv(from_object, ['person_generation']),
    )

  if getv(from_object, ['include_safety_attributes']) is not None:
    setv(
        parent_object,
        ['parameters', 'includeSafetyAttributes'],
        getv(from_object, ['include_safety_attributes']),
    )

  if getv(from_object, ['include_rai_reason']) is not None:
    setv(
        parent_object,
        ['parameters', 'includeRaiReason'],
        getv(from_object, ['include_rai_reason']),
    )

  if getv(from_object, ['language']) is not None:
    setv(
        parent_object,
        ['parameters', 'language'],
        getv(from_object, ['language']),
    )

  if getv(from_object, ['output_mime_type']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'mimeType'],
        getv(from_object, ['output_mime_type']),
    )

  if getv(from_object, ['output_compression_quality']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'compressionQuality'],
        getv(from_object, ['output_compression_quality']),
    )

  if getv(from_object, ['add_watermark']) is not None:
    setv(
        parent_object,
        ['parameters', 'addWatermark'],
        getv(from_object, ['add_watermark']),
    )

  if getv(from_object, ['aspect_ratio']) is not None:
    setv(
        parent_object,
        ['parameters', 'aspectRatio'],
        getv(from_object, ['aspect_ratio']),
    )

  return to_object


def _GenerateImageParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['prompt']) is not None:
    setv(to_object, ['instances', 'prompt'], getv(from_object, ['prompt']))

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _GenerateImageConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _GenerateImageParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['prompt']) is not None:
    setv(to_object, ['instances', 'prompt'], getv(from_object, ['prompt']))

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _GenerateImageConfig_to_vertex(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _Image_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['gcs_uri']):
    raise ValueError('gcs_uri parameter is not supported in Google AI.')

  if getv(from_object, ['image_bytes']) is not None:
    setv(to_object, ['bytesBase64Encoded'], getv(from_object, ['image_bytes']))

  return to_object


def _Image_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['gcs_uri']) is not None:
    setv(to_object, ['gcsUri'], getv(from_object, ['gcs_uri']))

  if getv(from_object, ['image_bytes']) is not None:
    setv(to_object, ['bytesBase64Encoded'], getv(from_object, ['image_bytes']))

  return to_object


def _MaskReferenceConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['mask_mode']):
    raise ValueError('mask_mode parameter is not supported in Google AI.')

  if getv(from_object, ['segmentation_classes']):
    raise ValueError(
        'segmentation_classes parameter is not supported in Google AI.'
    )

  if getv(from_object, ['mask_dilation']):
    raise ValueError('mask_dilation parameter is not supported in Google AI.')

  return to_object


def _MaskReferenceConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['mask_mode']) is not None:
    setv(to_object, ['maskMode'], getv(from_object, ['mask_mode']))

  if getv(from_object, ['segmentation_classes']) is not None:
    setv(
        to_object, ['maskClasses'], getv(from_object, ['segmentation_classes'])
    )

  if getv(from_object, ['mask_dilation']) is not None:
    setv(to_object, ['dilation'], getv(from_object, ['mask_dilation']))

  return to_object


def _ControlReferenceConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['control_type']):
    raise ValueError('control_type parameter is not supported in Google AI.')

  if getv(from_object, ['enable_control_image_computation']):
    raise ValueError(
        'enable_control_image_computation parameter is not supported in'
        ' Google AI.'
    )

  return to_object


def _ControlReferenceConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['control_type']) is not None:
    setv(to_object, ['controlType'], getv(from_object, ['control_type']))

  if getv(from_object, ['enable_control_image_computation']) is not None:
    setv(
        to_object,
        ['computeControl'],
        getv(from_object, ['enable_control_image_computation']),
    )

  return to_object


def _StyleReferenceConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['style_description']):
    raise ValueError(
        'style_description parameter is not supported in Google AI.'
    )

  return to_object


def _StyleReferenceConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['style_description']) is not None:
    setv(
        to_object,
        ['styleDescription'],
        getv(from_object, ['style_description']),
    )

  return to_object


def _SubjectReferenceConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['subject_type']):
    raise ValueError('subject_type parameter is not supported in Google AI.')

  if getv(from_object, ['subject_description']):
    raise ValueError(
        'subject_description parameter is not supported in Google AI.'
    )

  return to_object


def _SubjectReferenceConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['subject_type']) is not None:
    setv(to_object, ['subjectType'], getv(from_object, ['subject_type']))

  if getv(from_object, ['subject_description']) is not None:
    setv(
        to_object,
        ['subjectDescription'],
        getv(from_object, ['subject_description']),
    )

  return to_object


def _ReferenceImageAPI_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['reference_image']):
    raise ValueError('reference_image parameter is not supported in Google AI.')

  if getv(from_object, ['reference_id']):
    raise ValueError('reference_id parameter is not supported in Google AI.')

  if getv(from_object, ['reference_type']):
    raise ValueError('reference_type parameter is not supported in Google AI.')

  if getv(from_object, ['mask_image_config']):
    raise ValueError(
        'mask_image_config parameter is not supported in Google AI.'
    )

  if getv(from_object, ['control_image_config']):
    raise ValueError(
        'control_image_config parameter is not supported in Google AI.'
    )

  if getv(from_object, ['style_image_config']):
    raise ValueError(
        'style_image_config parameter is not supported in Google AI.'
    )

  if getv(from_object, ['subject_image_config']):
    raise ValueError(
        'subject_image_config parameter is not supported in Google AI.'
    )

  return to_object


def _ReferenceImageAPI_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['reference_image']) is not None:
    setv(
        to_object,
        ['referenceImage'],
        _Image_to_vertex(
            api_client, getv(from_object, ['reference_image']), to_object
        ),
    )

  if getv(from_object, ['reference_id']) is not None:
    setv(to_object, ['referenceId'], getv(from_object, ['reference_id']))

  if getv(from_object, ['reference_type']) is not None:
    setv(to_object, ['referenceType'], getv(from_object, ['reference_type']))

  if getv(from_object, ['mask_image_config']) is not None:
    setv(
        to_object,
        ['maskImageConfig'],
        _MaskReferenceConfig_to_vertex(
            api_client, getv(from_object, ['mask_image_config']), to_object
        ),
    )

  if getv(from_object, ['control_image_config']) is not None:
    setv(
        to_object,
        ['controlImageConfig'],
        _ControlReferenceConfig_to_vertex(
            api_client, getv(from_object, ['control_image_config']), to_object
        ),
    )

  if getv(from_object, ['style_image_config']) is not None:
    setv(
        to_object,
        ['styleImageConfig'],
        _StyleReferenceConfig_to_vertex(
            api_client, getv(from_object, ['style_image_config']), to_object
        ),
    )

  if getv(from_object, ['subject_image_config']) is not None:
    setv(
        to_object,
        ['subjectImageConfig'],
        _SubjectReferenceConfig_to_vertex(
            api_client, getv(from_object, ['subject_image_config']), to_object
        ),
    )

  return to_object


def _EditImageConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['output_gcs_uri']):
    raise ValueError('output_gcs_uri parameter is not supported in Google AI.')

  if getv(from_object, ['negative_prompt']) is not None:
    setv(
        parent_object,
        ['parameters', 'negativePrompt'],
        getv(from_object, ['negative_prompt']),
    )

  if getv(from_object, ['number_of_images']) is not None:
    setv(
        parent_object,
        ['parameters', 'sampleCount'],
        getv(from_object, ['number_of_images']),
    )

  if getv(from_object, ['guidance_scale']) is not None:
    setv(
        parent_object,
        ['parameters', 'guidanceScale'],
        getv(from_object, ['guidance_scale']),
    )

  if getv(from_object, ['seed']):
    raise ValueError('seed parameter is not supported in Google AI.')

  if getv(from_object, ['safety_filter_level']) is not None:
    setv(
        parent_object,
        ['parameters', 'safetySetting'],
        getv(from_object, ['safety_filter_level']),
    )

  if getv(from_object, ['person_generation']) is not None:
    setv(
        parent_object,
        ['parameters', 'personGeneration'],
        getv(from_object, ['person_generation']),
    )

  if getv(from_object, ['include_safety_attributes']) is not None:
    setv(
        parent_object,
        ['parameters', 'includeSafetyAttributes'],
        getv(from_object, ['include_safety_attributes']),
    )

  if getv(from_object, ['include_rai_reason']) is not None:
    setv(
        parent_object,
        ['parameters', 'includeRaiReason'],
        getv(from_object, ['include_rai_reason']),
    )

  if getv(from_object, ['language']) is not None:
    setv(
        parent_object,
        ['parameters', 'language'],
        getv(from_object, ['language']),
    )

  if getv(from_object, ['output_mime_type']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'mimeType'],
        getv(from_object, ['output_mime_type']),
    )

  if getv(from_object, ['output_compression_quality']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'compressionQuality'],
        getv(from_object, ['output_compression_quality']),
    )

  if getv(from_object, ['edit_mode']) is not None:
    setv(
        parent_object,
        ['parameters', 'editMode'],
        getv(from_object, ['edit_mode']),
    )

  return to_object


def _EditImageConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['output_gcs_uri']) is not None:
    setv(
        parent_object,
        ['parameters', 'storageUri'],
        getv(from_object, ['output_gcs_uri']),
    )

  if getv(from_object, ['negative_prompt']) is not None:
    setv(
        parent_object,
        ['parameters', 'negativePrompt'],
        getv(from_object, ['negative_prompt']),
    )

  if getv(from_object, ['number_of_images']) is not None:
    setv(
        parent_object,
        ['parameters', 'sampleCount'],
        getv(from_object, ['number_of_images']),
    )

  if getv(from_object, ['guidance_scale']) is not None:
    setv(
        parent_object,
        ['parameters', 'guidanceScale'],
        getv(from_object, ['guidance_scale']),
    )

  if getv(from_object, ['seed']) is not None:
    setv(parent_object, ['parameters', 'seed'], getv(from_object, ['seed']))

  if getv(from_object, ['safety_filter_level']) is not None:
    setv(
        parent_object,
        ['parameters', 'safetySetting'],
        getv(from_object, ['safety_filter_level']),
    )

  if getv(from_object, ['person_generation']) is not None:
    setv(
        parent_object,
        ['parameters', 'personGeneration'],
        getv(from_object, ['person_generation']),
    )

  if getv(from_object, ['include_safety_attributes']) is not None:
    setv(
        parent_object,
        ['parameters', 'includeSafetyAttributes'],
        getv(from_object, ['include_safety_attributes']),
    )

  if getv(from_object, ['include_rai_reason']) is not None:
    setv(
        parent_object,
        ['parameters', 'includeRaiReason'],
        getv(from_object, ['include_rai_reason']),
    )

  if getv(from_object, ['language']) is not None:
    setv(
        parent_object,
        ['parameters', 'language'],
        getv(from_object, ['language']),
    )

  if getv(from_object, ['output_mime_type']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'mimeType'],
        getv(from_object, ['output_mime_type']),
    )

  if getv(from_object, ['output_compression_quality']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'compressionQuality'],
        getv(from_object, ['output_compression_quality']),
    )

  if getv(from_object, ['edit_mode']) is not None:
    setv(
        parent_object,
        ['parameters', 'editMode'],
        getv(from_object, ['edit_mode']),
    )

  return to_object


def _EditImageParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['prompt']) is not None:
    setv(to_object, ['instances', 'prompt'], getv(from_object, ['prompt']))

  if getv(from_object, ['reference_images']) is not None:
    setv(
        to_object,
        ['instances', 'referenceImages'],
        [
            _ReferenceImageAPI_to_mldev(api_client, item, to_object)
            for item in getv(from_object, ['reference_images'])
        ],
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _EditImageConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _EditImageParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['prompt']) is not None:
    setv(to_object, ['instances', 'prompt'], getv(from_object, ['prompt']))

  if getv(from_object, ['reference_images']) is not None:
    setv(
        to_object,
        ['instances', 'referenceImages'],
        [
            _ReferenceImageAPI_to_vertex(api_client, item, to_object)
            for item in getv(from_object, ['reference_images'])
        ],
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _EditImageConfig_to_vertex(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _UpscaleImageAPIConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['upscale_factor']) is not None:
    setv(
        parent_object,
        ['parameters', 'upscaleConfig', 'upscaleFactor'],
        getv(from_object, ['upscale_factor']),
    )

  if getv(from_object, ['include_rai_reason']) is not None:
    setv(
        parent_object,
        ['parameters', 'includeRaiReason'],
        getv(from_object, ['include_rai_reason']),
    )

  if getv(from_object, ['output_mime_type']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'mimeType'],
        getv(from_object, ['output_mime_type']),
    )

  if getv(from_object, ['output_compression_quality']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'compressionQuality'],
        getv(from_object, ['output_compression_quality']),
    )

  if getv(from_object, ['number_of_images']) is not None:
    setv(
        parent_object,
        ['parameters', 'sampleCount'],
        getv(from_object, ['number_of_images']),
    )

  if getv(from_object, ['mode']) is not None:
    setv(parent_object, ['parameters', 'mode'], getv(from_object, ['mode']))

  return to_object


def _UpscaleImageAPIConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['upscale_factor']) is not None:
    setv(
        parent_object,
        ['parameters', 'upscaleConfig', 'upscaleFactor'],
        getv(from_object, ['upscale_factor']),
    )

  if getv(from_object, ['include_rai_reason']) is not None:
    setv(
        parent_object,
        ['parameters', 'includeRaiReason'],
        getv(from_object, ['include_rai_reason']),
    )

  if getv(from_object, ['output_mime_type']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'mimeType'],
        getv(from_object, ['output_mime_type']),
    )

  if getv(from_object, ['output_compression_quality']) is not None:
    setv(
        parent_object,
        ['parameters', 'outputOptions', 'compressionQuality'],
        getv(from_object, ['output_compression_quality']),
    )

  if getv(from_object, ['number_of_images']) is not None:
    setv(
        parent_object,
        ['parameters', 'sampleCount'],
        getv(from_object, ['number_of_images']),
    )

  if getv(from_object, ['mode']) is not None:
    setv(parent_object, ['parameters', 'mode'], getv(from_object, ['mode']))

  return to_object


def _UpscaleImageAPIParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['image']) is not None:
    setv(
        to_object,
        ['instances', 'image'],
        _Image_to_mldev(api_client, getv(from_object, ['image']), to_object),
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _UpscaleImageAPIConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _UpscaleImageAPIParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['image']) is not None:
    setv(
        to_object,
        ['instances', 'image'],
        _Image_to_vertex(api_client, getv(from_object, ['image']), to_object),
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _UpscaleImageAPIConfig_to_vertex(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _GetModelParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'name'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  return to_object


def _GetModelParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'name'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  return to_object


def _ListModelsConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['page_size']) is not None:
    setv(
        parent_object, ['_query', 'pageSize'], getv(from_object, ['page_size'])
    )

  if getv(from_object, ['page_token']) is not None:
    setv(
        parent_object,
        ['_query', 'pageToken'],
        getv(from_object, ['page_token']),
    )

  if getv(from_object, ['filter']) is not None:
    setv(parent_object, ['_query', 'filter'], getv(from_object, ['filter']))

  return to_object


def _ListModelsConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['page_size']) is not None:
    setv(
        parent_object, ['_query', 'pageSize'], getv(from_object, ['page_size'])
    )

  if getv(from_object, ['page_token']) is not None:
    setv(
        parent_object,
        ['_query', 'pageToken'],
        getv(from_object, ['page_token']),
    )

  if getv(from_object, ['filter']) is not None:
    setv(parent_object, ['_query', 'filter'], getv(from_object, ['filter']))

  return to_object


def _ListModelsParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _ListModelsConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _ListModelsParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _ListModelsConfig_to_vertex(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _UpdateModelConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['display_name']) is not None:
    setv(parent_object, ['displayName'], getv(from_object, ['display_name']))

  if getv(from_object, ['description']) is not None:
    setv(parent_object, ['description'], getv(from_object, ['description']))

  return to_object


def _UpdateModelConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['display_name']) is not None:
    setv(parent_object, ['displayName'], getv(from_object, ['display_name']))

  if getv(from_object, ['description']) is not None:
    setv(parent_object, ['description'], getv(from_object, ['description']))

  return to_object


def _UpdateModelParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'name'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _UpdateModelConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _UpdateModelParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _UpdateModelConfig_to_vertex(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _DeleteModelParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'name'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  return to_object


def _DeleteModelParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'name'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  return to_object


def _CountTokensConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['system_instruction']) is not None:
    setv(
        parent_object,
        ['generateContentRequest', 'systemInstruction'],
        _Content_to_mldev(
            api_client,
            t.t_content(api_client, getv(from_object, ['system_instruction'])),
            to_object,
        ),
    )

  if getv(from_object, ['tools']) is not None:
    setv(
        parent_object,
        ['generateContentRequest', 'tools'],
        [
            _Tool_to_mldev(api_client, item, to_object)
            for item in getv(from_object, ['tools'])
        ],
    )

  if getv(from_object, ['generation_config']):
    raise ValueError(
        'generation_config parameter is not supported in Google AI.'
    )

  return to_object


def _CountTokensConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['system_instruction']) is not None:
    setv(
        to_object,
        ['systemInstruction'],
        _Content_to_vertex(
            api_client,
            t.t_content(api_client, getv(from_object, ['system_instruction'])),
            to_object,
        ),
    )

  if getv(from_object, ['tools']) is not None:
    setv(
        to_object,
        ['tools'],
        [
            _Tool_to_vertex(api_client, item, to_object)
            for item in getv(from_object, ['tools'])
        ],
    )

  if getv(from_object, ['generation_config']) is not None:
    setv(
        parent_object,
        ['generationConfig'],
        getv(from_object, ['generation_config']),
    )

  return to_object


def _CountTokensParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['contents']) is not None:
    setv(
        to_object,
        ['contents'],
        [
            _Content_to_mldev(api_client, item, to_object)
            for item in t.t_contents(
                api_client, getv(from_object, ['contents'])
            )
        ],
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _CountTokensConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _CountTokensParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['contents']) is not None:
    setv(
        to_object,
        ['contents'],
        [
            _Content_to_vertex(api_client, item, to_object)
            for item in t.t_contents(
                api_client, getv(from_object, ['contents'])
            )
        ],
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _CountTokensConfig_to_vertex(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _ComputeTokensConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  return to_object


def _ComputeTokensConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  return to_object


def _ComputeTokensParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['contents']):
    raise ValueError('contents parameter is not supported in Google AI.')

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _ComputeTokensConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _ComputeTokensParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['_url', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['contents']) is not None:
    setv(
        to_object,
        ['contents'],
        [
            _Content_to_vertex(api_client, item, to_object)
            for item in t.t_contents(
                api_client, getv(from_object, ['contents'])
            )
        ],
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _ComputeTokensConfig_to_vertex(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _Part_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  if getv(from_object, ['codeExecutionResult']) is not None:
    setv(
        to_object,
        ['code_execution_result'],
        getv(from_object, ['codeExecutionResult']),
    )

  if getv(from_object, ['executableCode']) is not None:
    setv(to_object, ['executable_code'], getv(from_object, ['executableCode']))

  if getv(from_object, ['fileData']) is not None:
    setv(to_object, ['file_data'], getv(from_object, ['fileData']))

  if getv(from_object, ['functionCall']) is not None:
    setv(to_object, ['function_call'], getv(from_object, ['functionCall']))

  if getv(from_object, ['functionResponse']) is not None:
    setv(
        to_object,
        ['function_response'],
        getv(from_object, ['functionResponse']),
    )

  if getv(from_object, ['inlineData']) is not None:
    setv(to_object, ['inline_data'], getv(from_object, ['inlineData']))

  if getv(from_object, ['text']) is not None:
    setv(to_object, ['text'], getv(from_object, ['text']))

  return to_object


def _Part_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['videoMetadata']) is not None:
    setv(to_object, ['video_metadata'], getv(from_object, ['videoMetadata']))

  if getv(from_object, ['codeExecutionResult']) is not None:
    setv(
        to_object,
        ['code_execution_result'],
        getv(from_object, ['codeExecutionResult']),
    )

  if getv(from_object, ['executableCode']) is not None:
    setv(to_object, ['executable_code'], getv(from_object, ['executableCode']))

  if getv(from_object, ['fileData']) is not None:
    setv(to_object, ['file_data'], getv(from_object, ['fileData']))

  if getv(from_object, ['functionCall']) is not None:
    setv(to_object, ['function_call'], getv(from_object, ['functionCall']))

  if getv(from_object, ['functionResponse']) is not None:
    setv(
        to_object,
        ['function_response'],
        getv(from_object, ['functionResponse']),
    )

  if getv(from_object, ['inlineData']) is not None:
    setv(to_object, ['inline_data'], getv(from_object, ['inlineData']))

  if getv(from_object, ['text']) is not None:
    setv(to_object, ['text'], getv(from_object, ['text']))

  return to_object


def _Content_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['parts']) is not None:
    setv(
        to_object,
        ['parts'],
        [
            _Part_from_mldev(api_client, item, to_object)
            for item in getv(from_object, ['parts'])
        ],
    )

  if getv(from_object, ['role']) is not None:
    setv(to_object, ['role'], getv(from_object, ['role']))

  return to_object


def _Content_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['parts']) is not None:
    setv(
        to_object,
        ['parts'],
        [
            _Part_from_vertex(api_client, item, to_object)
            for item in getv(from_object, ['parts'])
        ],
    )

  if getv(from_object, ['role']) is not None:
    setv(to_object, ['role'], getv(from_object, ['role']))

  return to_object


def _CitationMetadata_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['citationSources']) is not None:
    setv(to_object, ['citations'], getv(from_object, ['citationSources']))

  return to_object


def _CitationMetadata_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['citations']) is not None:
    setv(to_object, ['citations'], getv(from_object, ['citations']))

  return to_object


def _Candidate_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['content']) is not None:
    setv(
        to_object,
        ['content'],
        _Content_from_mldev(
            api_client, getv(from_object, ['content']), to_object
        ),
    )

  if getv(from_object, ['citationMetadata']) is not None:
    setv(
        to_object,
        ['citation_metadata'],
        _CitationMetadata_from_mldev(
            api_client, getv(from_object, ['citationMetadata']), to_object
        ),
    )

  if getv(from_object, ['tokenCount']) is not None:
    setv(to_object, ['token_count'], getv(from_object, ['tokenCount']))

  if getv(from_object, ['avgLogprobs']) is not None:
    setv(to_object, ['avg_logprobs'], getv(from_object, ['avgLogprobs']))

  if getv(from_object, ['finishReason']) is not None:
    setv(to_object, ['finish_reason'], getv(from_object, ['finishReason']))

  if getv(from_object, ['groundingMetadata']) is not None:
    setv(
        to_object,
        ['grounding_metadata'],
        getv(from_object, ['groundingMetadata']),
    )

  if getv(from_object, ['index']) is not None:
    setv(to_object, ['index'], getv(from_object, ['index']))

  if getv(from_object, ['logprobsResult']) is not None:
    setv(to_object, ['logprobs_result'], getv(from_object, ['logprobsResult']))

  if getv(from_object, ['safetyRatings']) is not None:
    setv(to_object, ['safety_ratings'], getv(from_object, ['safetyRatings']))

  return to_object


def _Candidate_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['content']) is not None:
    setv(
        to_object,
        ['content'],
        _Content_from_vertex(
            api_client, getv(from_object, ['content']), to_object
        ),
    )

  if getv(from_object, ['citationMetadata']) is not None:
    setv(
        to_object,
        ['citation_metadata'],
        _CitationMetadata_from_vertex(
            api_client, getv(from_object, ['citationMetadata']), to_object
        ),
    )

  if getv(from_object, ['finishMessage']) is not None:
    setv(to_object, ['finish_message'], getv(from_object, ['finishMessage']))

  if getv(from_object, ['avgLogprobs']) is not None:
    setv(to_object, ['avg_logprobs'], getv(from_object, ['avgLogprobs']))

  if getv(from_object, ['finishReason']) is not None:
    setv(to_object, ['finish_reason'], getv(from_object, ['finishReason']))

  if getv(from_object, ['groundingMetadata']) is not None:
    setv(
        to_object,
        ['grounding_metadata'],
        getv(from_object, ['groundingMetadata']),
    )

  if getv(from_object, ['index']) is not None:
    setv(to_object, ['index'], getv(from_object, ['index']))

  if getv(from_object, ['logprobsResult']) is not None:
    setv(to_object, ['logprobs_result'], getv(from_object, ['logprobsResult']))

  if getv(from_object, ['safetyRatings']) is not None:
    setv(to_object, ['safety_ratings'], getv(from_object, ['safetyRatings']))

  return to_object


def _GenerateContentResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['candidates']) is not None:
    setv(
        to_object,
        ['candidates'],
        [
            _Candidate_from_mldev(api_client, item, to_object)
            for item in getv(from_object, ['candidates'])
        ],
    )

  if getv(from_object, ['modelVersion']) is not None:
    setv(to_object, ['model_version'], getv(from_object, ['modelVersion']))

  if getv(from_object, ['promptFeedback']) is not None:
    setv(to_object, ['prompt_feedback'], getv(from_object, ['promptFeedback']))

  if getv(from_object, ['usageMetadata']) is not None:
    setv(to_object, ['usage_metadata'], getv(from_object, ['usageMetadata']))

  return to_object


def _GenerateContentResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['candidates']) is not None:
    setv(
        to_object,
        ['candidates'],
        [
            _Candidate_from_vertex(api_client, item, to_object)
            for item in getv(from_object, ['candidates'])
        ],
    )

  if getv(from_object, ['modelVersion']) is not None:
    setv(to_object, ['model_version'], getv(from_object, ['modelVersion']))

  if getv(from_object, ['promptFeedback']) is not None:
    setv(to_object, ['prompt_feedback'], getv(from_object, ['promptFeedback']))

  if getv(from_object, ['usageMetadata']) is not None:
    setv(to_object, ['usage_metadata'], getv(from_object, ['usageMetadata']))

  return to_object


def _ContentEmbeddingStatistics_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _ContentEmbeddingStatistics_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['truncated']) is not None:
    setv(to_object, ['truncated'], getv(from_object, ['truncated']))

  if getv(from_object, ['token_count']) is not None:
    setv(to_object, ['token_count'], getv(from_object, ['token_count']))

  return to_object


def _ContentEmbedding_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['values']) is not None:
    setv(to_object, ['values'], getv(from_object, ['values']))

  return to_object


def _ContentEmbedding_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['values']) is not None:
    setv(to_object, ['values'], getv(from_object, ['values']))

  if getv(from_object, ['statistics']) is not None:
    setv(
        to_object,
        ['statistics'],
        _ContentEmbeddingStatistics_from_vertex(
            api_client, getv(from_object, ['statistics']), to_object
        ),
    )

  return to_object


def _EmbedContentMetadata_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _EmbedContentMetadata_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['billableCharacterCount']) is not None:
    setv(
        to_object,
        ['billable_character_count'],
        getv(from_object, ['billableCharacterCount']),
    )

  return to_object


def _EmbedContentResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['embeddings']) is not None:
    setv(
        to_object,
        ['embeddings'],
        [
            _ContentEmbedding_from_mldev(api_client, item, to_object)
            for item in getv(from_object, ['embeddings'])
        ],
    )

  if getv(from_object, ['metadata']) is not None:
    setv(
        to_object,
        ['metadata'],
        _EmbedContentMetadata_from_mldev(
            api_client, getv(from_object, ['metadata']), to_object
        ),
    )

  return to_object


def _EmbedContentResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['predictions[]', 'embeddings']) is not None:
    setv(
        to_object,
        ['embeddings'],
        [
            _ContentEmbedding_from_vertex(api_client, item, to_object)
            for item in getv(from_object, ['predictions[]', 'embeddings'])
        ],
    )

  if getv(from_object, ['metadata']) is not None:
    setv(
        to_object,
        ['metadata'],
        _EmbedContentMetadata_from_vertex(
            api_client, getv(from_object, ['metadata']), to_object
        ),
    )

  return to_object


def _Image_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  if getv(from_object, ['bytesBase64Encoded']) is not None:
    setv(to_object, ['image_bytes'], getv(from_object, ['bytesBase64Encoded']))

  return to_object


def _Image_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['gcsUri']) is not None:
    setv(to_object, ['gcs_uri'], getv(from_object, ['gcsUri']))

  if getv(from_object, ['bytesBase64Encoded']) is not None:
    setv(to_object, ['image_bytes'], getv(from_object, ['bytesBase64Encoded']))

  return to_object


def _GeneratedImage_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['_self']) is not None:
    setv(
        to_object,
        ['image'],
        _Image_from_mldev(api_client, getv(from_object, ['_self']), to_object),
    )

  if getv(from_object, ['raiFilteredReason']) is not None:
    setv(
        to_object,
        ['rai_filtered_reason'],
        getv(from_object, ['raiFilteredReason']),
    )

  return to_object


def _GeneratedImage_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['_self']) is not None:
    setv(
        to_object,
        ['image'],
        _Image_from_vertex(api_client, getv(from_object, ['_self']), to_object),
    )

  if getv(from_object, ['raiFilteredReason']) is not None:
    setv(
        to_object,
        ['rai_filtered_reason'],
        getv(from_object, ['raiFilteredReason']),
    )

  return to_object


def _GenerateImageResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['predictions']) is not None:
    setv(
        to_object,
        ['generated_images'],
        [
            _GeneratedImage_from_mldev(api_client, item, to_object)
            for item in getv(from_object, ['predictions'])
        ],
    )

  return to_object


def _GenerateImageResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['predictions']) is not None:
    setv(
        to_object,
        ['generated_images'],
        [
            _GeneratedImage_from_vertex(api_client, item, to_object)
            for item in getv(from_object, ['predictions'])
        ],
    )

  return to_object


def _EditImageResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['predictions']) is not None:
    setv(
        to_object,
        ['generated_images'],
        [
            _GeneratedImage_from_mldev(api_client, item, to_object)
            for item in getv(from_object, ['predictions'])
        ],
    )

  return to_object


def _EditImageResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['predictions']) is not None:
    setv(
        to_object,
        ['generated_images'],
        [
            _GeneratedImage_from_vertex(api_client, item, to_object)
            for item in getv(from_object, ['predictions'])
        ],
    )

  return to_object


def _UpscaleImageResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['predictions']) is not None:
    setv(
        to_object,
        ['generated_images'],
        [
            _GeneratedImage_from_mldev(api_client, item, to_object)
            for item in getv(from_object, ['predictions'])
        ],
    )

  return to_object


def _UpscaleImageResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['predictions']) is not None:
    setv(
        to_object,
        ['generated_images'],
        [
            _GeneratedImage_from_vertex(api_client, item, to_object)
            for item in getv(from_object, ['predictions'])
        ],
    )

  return to_object


def _Endpoint_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _Endpoint_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['endpoint']) is not None:
    setv(to_object, ['name'], getv(from_object, ['endpoint']))

  if getv(from_object, ['deployedModelId']) is not None:
    setv(
        to_object, ['deployed_model_id'], getv(from_object, ['deployedModelId'])
    )

  return to_object


def _TunedModelInfo_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['baseModel']) is not None:
    setv(to_object, ['base_model'], getv(from_object, ['baseModel']))

  if getv(from_object, ['createTime']) is not None:
    setv(to_object, ['create_time'], getv(from_object, ['createTime']))

  if getv(from_object, ['updateTime']) is not None:
    setv(to_object, ['update_time'], getv(from_object, ['updateTime']))

  return to_object


def _TunedModelInfo_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if (
      getv(from_object, ['labels', 'google-vertex-llm-tuning-base-model-id'])
      is not None
  ):
    setv(
        to_object,
        ['base_model'],
        getv(from_object, ['labels', 'google-vertex-llm-tuning-base-model-id']),
    )

  if getv(from_object, ['createTime']) is not None:
    setv(to_object, ['create_time'], getv(from_object, ['createTime']))

  if getv(from_object, ['updateTime']) is not None:
    setv(to_object, ['update_time'], getv(from_object, ['updateTime']))

  return to_object


def _Model_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['name']) is not None:
    setv(to_object, ['name'], getv(from_object, ['name']))

  if getv(from_object, ['displayName']) is not None:
    setv(to_object, ['display_name'], getv(from_object, ['displayName']))

  if getv(from_object, ['description']) is not None:
    setv(to_object, ['description'], getv(from_object, ['description']))

  if getv(from_object, ['version']) is not None:
    setv(to_object, ['version'], getv(from_object, ['version']))

  if getv(from_object, ['_self']) is not None:
    setv(
        to_object,
        ['tuned_model_info'],
        _TunedModelInfo_from_mldev(
            api_client, getv(from_object, ['_self']), to_object
        ),
    )

  if getv(from_object, ['inputTokenLimit']) is not None:
    setv(
        to_object, ['input_token_limit'], getv(from_object, ['inputTokenLimit'])
    )

  if getv(from_object, ['outputTokenLimit']) is not None:
    setv(
        to_object,
        ['output_token_limit'],
        getv(from_object, ['outputTokenLimit']),
    )

  if getv(from_object, ['supportedGenerationMethods']) is not None:
    setv(
        to_object,
        ['supported_actions'],
        getv(from_object, ['supportedGenerationMethods']),
    )

  return to_object


def _Model_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['name']) is not None:
    setv(to_object, ['name'], getv(from_object, ['name']))

  if getv(from_object, ['displayName']) is not None:
    setv(to_object, ['display_name'], getv(from_object, ['displayName']))

  if getv(from_object, ['description']) is not None:
    setv(to_object, ['description'], getv(from_object, ['description']))

  if getv(from_object, ['versionId']) is not None:
    setv(to_object, ['version'], getv(from_object, ['versionId']))

  if getv(from_object, ['deployedModels']) is not None:
    setv(
        to_object,
        ['endpoints'],
        [
            _Endpoint_from_vertex(api_client, item, to_object)
            for item in getv(from_object, ['deployedModels'])
        ],
    )

  if getv(from_object, ['labels']) is not None:
    setv(to_object, ['labels'], getv(from_object, ['labels']))

  if getv(from_object, ['_self']) is not None:
    setv(
        to_object,
        ['tuned_model_info'],
        _TunedModelInfo_from_vertex(
            api_client, getv(from_object, ['_self']), to_object
        ),
    )

  return to_object


def _ListModelsResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['nextPageToken']) is not None:
    setv(to_object, ['next_page_token'], getv(from_object, ['nextPageToken']))

  if getv(from_object, ['tunedModels']) is not None:
    setv(
        to_object,
        ['models'],
        [
            _Model_from_mldev(api_client, item, to_object)
            for item in getv(from_object, ['tunedModels'])
        ],
    )

  return to_object


def _ListModelsResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['nextPageToken']) is not None:
    setv(to_object, ['next_page_token'], getv(from_object, ['nextPageToken']))

  if getv(from_object, ['models']) is not None:
    setv(
        to_object,
        ['models'],
        [
            _Model_from_vertex(api_client, item, to_object)
            for item in getv(from_object, ['models'])
        ],
    )

  return to_object


def _DeleteModelResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _DeleteModelResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _CountTokensResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['totalTokens']) is not None:
    setv(to_object, ['total_tokens'], getv(from_object, ['totalTokens']))

  if getv(from_object, ['cachedContentTokenCount']) is not None:
    setv(
        to_object,
        ['cached_content_token_count'],
        getv(from_object, ['cachedContentTokenCount']),
    )

  return to_object


def _CountTokensResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['totalTokens']) is not None:
    setv(to_object, ['total_tokens'], getv(from_object, ['totalTokens']))

  return to_object


def _ComputeTokensResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['tokensInfo']) is not None:
    setv(to_object, ['tokens_info'], getv(from_object, ['tokensInfo']))

  return to_object


def _ComputeTokensResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['tokensInfo']) is not None:
    setv(to_object, ['tokens_info'], getv(from_object, ['tokensInfo']))

  return to_object


class Models(_common.BaseModule):

  def _generate_content(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.GenerateContentConfigOrDict] = None,
  ) -> types.GenerateContentResponse:
    parameter_model = types._GenerateContentParameters(
        model=model,
        contents=contents,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _GenerateContentParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:generateContent'.format_map(request_dict.get('_url'))
    else:
      request_dict = _GenerateContentParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{model}:generateContent'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _GenerateContentResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _GenerateContentResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.GenerateContentResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def generate_content_stream(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.GenerateContentConfigOrDict] = None,
  ) -> Iterator[types.GenerateContentResponse]:
    parameter_model = types._GenerateContentParameters(
        model=model,
        contents=contents,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _GenerateContentParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:streamGenerateContent?alt=sse'.format_map(
          request_dict.get('_url')
      )
    else:
      request_dict = _GenerateContentParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{model}:streamGenerateContent?alt=sse'.format_map(
          request_dict.get('_url')
      )
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    for response_dict in self.api_client.request_streamed(
        'post', path, request_dict, http_options
    ):

      if self.api_client.vertexai:
        response_dict = _GenerateContentResponse_from_vertex(
            self.api_client, response_dict
        )
      else:
        response_dict = _GenerateContentResponse_from_mldev(
            self.api_client, response_dict
        )

      return_value = types.GenerateContentResponse._from_response(
          response_dict, parameter_model
      )
      self.api_client._verify_response(return_value)
      yield return_value

  def embed_content(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.EmbedContentConfigOrDict] = None,
  ) -> types.EmbedContentResponse:
    """Calculates embeddings for the given contents(only text is supported).

    Args:
      model (str): The model to use.
      contents (list[Content]): The contents to embed.
      config (EmbedContentConfig): Optional configuration for embeddings.

    Usage:

    .. code-block:: python

      embeddings = client.models.embed_content(
          model= 'text-embedding-004',
          contents=[
              'What is your name?',
              'What is your favorite color?',
          ],
          config={
              'output_dimensionality': 64
          },
      )
    """

    parameter_model = types._EmbedContentParameters(
        model=model,
        contents=contents,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _EmbedContentParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:predict'.format_map(request_dict.get('_url'))
    else:
      request_dict = _EmbedContentParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{model}:batchEmbedContents'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _EmbedContentResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _EmbedContentResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.EmbedContentResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def generate_image(
      self,
      *,
      model: str,
      prompt: str,
      config: Optional[types.GenerateImageConfigOrDict] = None,
  ) -> types.GenerateImageResponse:
    """Generates an image based on a text description and configuration.

    Args:
      model (str): The model to use.
      prompt (str): A text description of the image to generate.
      config (GenerateImageConfig): Configuration for generation.

    Usage:

    .. code-block:: python

      response = client.models.generate_image(
        model='imagen-3.0-generate-001',
        prompt='Man with a dog',
        config=types.GenerateImageConfig(
            number_of_images= 1,
            include_rai_reason= True,
        )
      )
      response.generated_images[0].image.show()
      # Shows a man with a dog.
    """

    parameter_model = types._GenerateImageParameters(
        model=model,
        prompt=prompt,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _GenerateImageParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:predict'.format_map(request_dict.get('_url'))
    else:
      request_dict = _GenerateImageParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{model}:predict'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _GenerateImageResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _GenerateImageResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.GenerateImageResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def edit_image(
      self,
      *,
      model: str,
      prompt: str,
      reference_images: list[types._ReferenceImageAPIOrDict],
      config: Optional[types.EditImageConfigOrDict] = None,
  ) -> types.EditImageResponse:
    """Edits an image based on a text description and configuration.

    Args:
      model (str): The model to use.
      prompt (str): A text description of the edit to apply to the image.
        reference_images (list[Union[RawReferenceImage, MaskReferenceImage,
        ControlReferenceImage, StyleReferenceImage, SubjectReferenceImage]): The
        reference images for editing.
      config (EditImageConfig): Configuration for editing.

    Usage:

    .. code-block:: python

      from google.genai.types import RawReferenceImage, MaskReferenceImage

      raw_ref_image = RawReferenceImage(
        reference_id=1,
        reference_image=types.Image.from_file(IMAGE_FILE_PATH),
      )

      mask_ref_image = MaskReferenceImage(
        reference_id=2,
        config=types.MaskReferenceConfig(
            mask_mode='MASK_MODE_FOREGROUND',
            mask_dilation=0.06,
        ),
      )
      response = client.models.edit_image(
        model='imagen-3.0-capability-preview-0930',
        prompt='man with dog',
        reference_images=[raw_ref_image, mask_ref_image],
        config=types.EditImageConfig(
            edit_mode= "EDIT_MODE_INPAINT_INSERTION",
            number_of_images= 1,
            include_rai_reason= True,
        )
      )
      response.generated_images[0].image.show()
      # Shows a man with a dog instead of a cat.
    """

    parameter_model = types._EditImageParameters(
        model=model,
        prompt=prompt,
        reference_images=reference_images,
        config=config,
    )

    if not self.api_client.vertexai:
      raise ValueError('This method is only supported in the Vertex AI client.')
    else:
      request_dict = _EditImageParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:predict'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _EditImageResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _EditImageResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.EditImageResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def _upscale_image(
      self,
      *,
      model: str,
      image: types.ImageOrDict,
      config: Optional[types._UpscaleImageAPIConfigOrDict] = None,
  ) -> types.UpscaleImageResponse:
    """Upscales an image.

    Args:
      model (str): The model to use.
      image (Image): The input image for upscaling.
      config (_UpscaleImageAPIConfig): Configuration for upscaling.
    """

    parameter_model = types._UpscaleImageAPIParameters(
        model=model,
        image=image,
        config=config,
    )

    if not self.api_client.vertexai:
      raise ValueError('This method is only supported in the Vertex AI client.')
    else:
      request_dict = _UpscaleImageAPIParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:predict'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _UpscaleImageResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _UpscaleImageResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.UpscaleImageResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def get(self, *, model: str) -> types.Model:
    parameter_model = types._GetModelParameters(
        model=model,
    )

    if self.api_client.vertexai:
      request_dict = _GetModelParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{name}'.format_map(request_dict.get('_url'))
    else:
      request_dict = _GetModelParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{name}'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'get', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _Model_from_vertex(self.api_client, response_dict)
    else:
      response_dict = _Model_from_mldev(self.api_client, response_dict)

    return_value = types.Model._from_response(response_dict, parameter_model)
    self.api_client._verify_response(return_value)
    return return_value

  def _list(
      self, *, config: Optional[types.ListModelsConfigOrDict] = None
  ) -> types.ListModelsResponse:
    parameter_model = types._ListModelsParameters(
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _ListModelsParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = 'models'.format_map(request_dict.get('_url'))
    else:
      request_dict = _ListModelsParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = 'tunedModels'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'get', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _ListModelsResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _ListModelsResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.ListModelsResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def update(
      self,
      *,
      model: str,
      config: Optional[types.UpdateModelConfigOrDict] = None,
  ) -> types.Model:
    parameter_model = types._UpdateModelParameters(
        model=model,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _UpdateModelParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}'.format_map(request_dict.get('_url'))
    else:
      request_dict = _UpdateModelParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{name}'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'patch', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _Model_from_vertex(self.api_client, response_dict)
    else:
      response_dict = _Model_from_mldev(self.api_client, response_dict)

    return_value = types.Model._from_response(response_dict, parameter_model)
    self.api_client._verify_response(return_value)
    return return_value

  def delete(self, *, model: str) -> types.DeleteModelResponse:
    parameter_model = types._DeleteModelParameters(
        model=model,
    )

    if self.api_client.vertexai:
      request_dict = _DeleteModelParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{name}'.format_map(request_dict.get('_url'))
    else:
      request_dict = _DeleteModelParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{name}'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'delete', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _DeleteModelResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _DeleteModelResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.DeleteModelResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def count_tokens(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.CountTokensConfigOrDict] = None,
  ) -> types.CountTokensResponse:
    """Counts the number of tokens in the given content.

    Args:
      model (str): The model to use for counting tokens.
      contents (list[types.Content]): The content to count tokens for.
        Multimodal input is supported for Gemini models.
      config (CountTokensConfig): The configuration for counting tokens.

    Usage:

    .. code-block:: python

      response = client.models.count_tokens(
          model='gemini-1.5-flash',
          contents='What is your name?',
      )
      print(response)
      # total_tokens=5 cached_content_token_count=None
    """

    parameter_model = types._CountTokensParameters(
        model=model,
        contents=contents,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _CountTokensParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:countTokens'.format_map(request_dict.get('_url'))
    else:
      request_dict = _CountTokensParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{model}:countTokens'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _CountTokensResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _CountTokensResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.CountTokensResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def compute_tokens(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.ComputeTokensConfigOrDict] = None,
  ) -> types.ComputeTokensResponse:
    """Return a list of tokens based on the input text.

    This method is not supported by the Gemini Developer API.

    Args:
      model (str): The model to use.
      contents (list[shared.Content]): The content to compute tokens for. Only
        text is supported.

    Usage:

    .. code-block:: python

      response = client.models.compute_tokens(
          model='gemini-1.5-flash',
          contents='What is your name?',
      )
      print(response)
      # tokens_info=[TokensInfo(role='user', token_ids=['1841', ...],
      # tokens=[b'What', b' is', b' your', b' name', b'?'])]
    """

    parameter_model = types._ComputeTokensParameters(
        model=model,
        contents=contents,
        config=config,
    )

    if not self.api_client.vertexai:
      raise ValueError('This method is only supported in the Vertex AI client.')
    else:
      request_dict = _ComputeTokensParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:computeTokens'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _ComputeTokensResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _ComputeTokensResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.ComputeTokensResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def generate_content(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.GenerateContentConfigOrDict] = None,
  ) -> types.GenerateContentResponse:
    """Makes an API request to generate content using a model.

    Some models support multimodal input and output.

    Usage:

    .. code-block:: python

      from google.genai import types
      from google import genai

      client = genai.Client(
          vertexai=True, project='my-project-id', location='us-central1'
      )

      response = client.models.generate_content(
        model='gemini-1.5-flash-002',
        contents='''What is a good name for a flower shop that specializes in
          selling bouquets of dried flowers?'''
      )
      print(response.text)
      # **Elegant & Classic:**
      # * The Dried Bloom
      # * Everlasting Florals
      # * Timeless Petals

      response = client.models.generate_content(
        model='gemini-1.5-flash-002',
        contents=[
          types.Part.from_text('What is shown in this image?'),
          types.Part.from_uri('gs://generativeai-downloads/images/scones.jpg',
          'image/jpeg')
        ]
      )
      print(response.text)
      # The image shows a flat lay arrangement of freshly baked blueberry
      # scones.
    """

    if _extra_utils.should_disable_afc(config):
      return self._generate_content(
          model=model, contents=contents, config=config
      )
    remaining_remote_calls_afc = _extra_utils.get_max_remote_calls_afc(config)
    logging.info(
        f'AFC is enabled with max remote calls: {remaining_remote_calls_afc}.'
    )
    automatic_function_calling_history = []
    while remaining_remote_calls_afc > 0:
      response = self._generate_content(
          model=model, contents=contents, config=config
      )
      remaining_remote_calls_afc -= 1
      if remaining_remote_calls_afc == 0:
        logging.info('Reached max remote calls for automatic function calling.')

      function_map = _extra_utils.get_function_map(config)
      if not function_map:
        break
      if (
          not response.candidates
          or not response.candidates[0].content
          or not response.candidates[0].content.parts
      ):
        break
      func_response_parts = _extra_utils.get_function_response_parts(
          response, function_map
      )
      if not func_response_parts:
        break
      contents = t.t_contents(self.api_client, contents)
      contents.append(response.candidates[0].content)
      contents.append(
          types.Content(
              role='user',
              parts=func_response_parts,
          )
      )
      automatic_function_calling_history.extend(contents)
    if _extra_utils.should_append_afc_history(config):
      response.automatic_function_calling_history = (
          automatic_function_calling_history
      )
    return response

  def upscale_image(
      self,
      *,
      model: str,
      image: types.ImageOrDict,
      config: types.UpscaleImageConfigOrDict,
  ) -> types.UpscaleImageResponse:
    """Makes an API request to upscale a provided image.

    Args:
      model (str): The model to use.
      image (Image): The input image for upscaling.
      config (UpscaleImageConfig): Configuration for upscaling.

    Usage:

    .. code-block:: python

      from google.genai.types import Image

      IMAGE_FILE_PATH="my-image.png"
      response=client.models.upscale_image(
          model='imagen-3.0-generate-001',
          image=types.Image.from_file(IMAGE_FILE_PATH),
                  config={
                    'upscale_factor': 'x2',
                  }
      )
      response.generated_images[0].image.show()
      # Opens my-image.png which is upscaled by a factor of 2.
    """

    # Validate config.
    types.UpscaleImageParameters(
        model=model,
        image=image,
        config=config,
    )

    # Convert to API config.
    config_dct = config if isinstance(config, dict) else config.dict()
    api_config = types._UpscaleImageAPIConfigDict(**config_dct)  # pylint: disable=protected-access

    # Provide default values through API config.
    api_config['mode'] = 'upscale'
    api_config['number_of_images'] = 1

    return self._upscale_image(model=model, image=image, config=api_config)

  def list(
      self,
      *,
      config: Optional[types.ListModelsConfigOrDict] = None,
  ) -> Pager[types.Model]:
    """Makes an API request to list the tuned models available to your project.

    This method only lists tuned models for the Vertex AI API.

    Usage:

    .. code-block:: python

      response=client.models.list(config={'page_size': 5})
      print(response.page)
      # [Model(name='projects/./locations/./models/123', display_name='my_model'
    """

    config = (
        types._ListModelsParameters(config=config).config
        or types.ListModelsConfig()
    )

    if self.api_client.vertexai:
      # Filter for tuning jobs artifacts by labels.
      config = config.copy()
      filter_value = config.filter
      config.filter = (
          filter_value + '&filter=labels.tune-type:*'
          if filter_value
          else 'labels.tune-type:*'
      )

    return Pager(
        'models',
        self._list,
        self._list(config=config),
        config,
    )


class AsyncModels(_common.BaseModule):

  async def _generate_content(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.GenerateContentConfigOrDict] = None,
  ) -> types.GenerateContentResponse:
    parameter_model = types._GenerateContentParameters(
        model=model,
        contents=contents,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _GenerateContentParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:generateContent'.format_map(request_dict.get('_url'))
    else:
      request_dict = _GenerateContentParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{model}:generateContent'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _GenerateContentResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _GenerateContentResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.GenerateContentResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def generate_content_stream(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.GenerateContentConfigOrDict] = None,
  ) -> AsyncIterator[types.GenerateContentResponse]:
    parameter_model = types._GenerateContentParameters(
        model=model,
        contents=contents,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _GenerateContentParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:streamGenerateContent?alt=sse'.format_map(
          request_dict.get('_url')
      )
    else:
      request_dict = _GenerateContentParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{model}:streamGenerateContent?alt=sse'.format_map(
          request_dict.get('_url')
      )
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    async for response_dict in self.api_client.async_request_streamed(
        'post', path, request_dict, http_options
    ):

      if self.api_client.vertexai:
        response_dict = _GenerateContentResponse_from_vertex(
            self.api_client, response_dict
        )
      else:
        response_dict = _GenerateContentResponse_from_mldev(
            self.api_client, response_dict
        )

      return_value = types.GenerateContentResponse._from_response(
          response_dict, parameter_model
      )
      self.api_client._verify_response(return_value)
      yield return_value

  async def embed_content(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.EmbedContentConfigOrDict] = None,
  ) -> types.EmbedContentResponse:
    """Calculates embeddings for the given contents(only text is supported).

    Args:
      model (str): The model to use.
      contents (list[Content]): The contents to embed.
      config (EmbedContentConfig): Optional configuration for embeddings.

    Usage:

    .. code-block:: python

      embeddings = client.models.embed_content(
          model= 'text-embedding-004',
          contents=[
              'What is your name?',
              'What is your favorite color?',
          ],
          config={
              'output_dimensionality': 64
          },
      )
    """

    parameter_model = types._EmbedContentParameters(
        model=model,
        contents=contents,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _EmbedContentParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:predict'.format_map(request_dict.get('_url'))
    else:
      request_dict = _EmbedContentParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{model}:batchEmbedContents'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _EmbedContentResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _EmbedContentResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.EmbedContentResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def generate_image(
      self,
      *,
      model: str,
      prompt: str,
      config: Optional[types.GenerateImageConfigOrDict] = None,
  ) -> types.GenerateImageResponse:
    """Generates an image based on a text description and configuration.

    Args:
      model (str): The model to use.
      prompt (str): A text description of the image to generate.
      config (GenerateImageConfig): Configuration for generation.

    Usage:

    .. code-block:: python

      response = client.models.generate_image(
        model='imagen-3.0-generate-001',
        prompt='Man with a dog',
        config=types.GenerateImageConfig(
            number_of_images= 1,
            include_rai_reason= True,
        )
      )
      response.generated_images[0].image.show()
      # Shows a man with a dog.
    """

    parameter_model = types._GenerateImageParameters(
        model=model,
        prompt=prompt,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _GenerateImageParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:predict'.format_map(request_dict.get('_url'))
    else:
      request_dict = _GenerateImageParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{model}:predict'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _GenerateImageResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _GenerateImageResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.GenerateImageResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def edit_image(
      self,
      *,
      model: str,
      prompt: str,
      reference_images: list[types._ReferenceImageAPIOrDict],
      config: Optional[types.EditImageConfigOrDict] = None,
  ) -> types.EditImageResponse:
    """Edits an image based on a text description and configuration.

    Args:
      model (str): The model to use.
      prompt (str): A text description of the edit to apply to the image.
        reference_images (list[Union[RawReferenceImage, MaskReferenceImage,
        ControlReferenceImage, StyleReferenceImage, SubjectReferenceImage]): The
        reference images for editing.
      config (EditImageConfig): Configuration for editing.

    Usage:

    .. code-block:: python

      from google.genai.types import RawReferenceImage, MaskReferenceImage

      raw_ref_image = RawReferenceImage(
        reference_id=1,
        reference_image=types.Image.from_file(IMAGE_FILE_PATH),
      )

      mask_ref_image = MaskReferenceImage(
        reference_id=2,
        config=types.MaskReferenceConfig(
            mask_mode='MASK_MODE_FOREGROUND',
            mask_dilation=0.06,
        ),
      )
      response = client.models.edit_image(
        model='imagen-3.0-capability-preview-0930',
        prompt='man with dog',
        reference_images=[raw_ref_image, mask_ref_image],
        config=types.EditImageConfig(
            edit_mode= "EDIT_MODE_INPAINT_INSERTION",
            number_of_images= 1,
            include_rai_reason= True,
        )
      )
      response.generated_images[0].image.show()
      # Shows a man with a dog instead of a cat.
    """

    parameter_model = types._EditImageParameters(
        model=model,
        prompt=prompt,
        reference_images=reference_images,
        config=config,
    )

    if not self.api_client.vertexai:
      raise ValueError('This method is only supported in the Vertex AI client.')
    else:
      request_dict = _EditImageParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:predict'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _EditImageResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _EditImageResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.EditImageResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def _upscale_image(
      self,
      *,
      model: str,
      image: types.ImageOrDict,
      config: Optional[types._UpscaleImageAPIConfigOrDict] = None,
  ) -> types.UpscaleImageResponse:
    """Upscales an image.

    Args:
      model (str): The model to use.
      image (Image): The input image for upscaling.
      config (_UpscaleImageAPIConfig): Configuration for upscaling.
    """

    parameter_model = types._UpscaleImageAPIParameters(
        model=model,
        image=image,
        config=config,
    )

    if not self.api_client.vertexai:
      raise ValueError('This method is only supported in the Vertex AI client.')
    else:
      request_dict = _UpscaleImageAPIParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:predict'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _UpscaleImageResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _UpscaleImageResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.UpscaleImageResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def get(self, *, model: str) -> types.Model:
    parameter_model = types._GetModelParameters(
        model=model,
    )

    if self.api_client.vertexai:
      request_dict = _GetModelParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{name}'.format_map(request_dict.get('_url'))
    else:
      request_dict = _GetModelParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{name}'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'get', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _Model_from_vertex(self.api_client, response_dict)
    else:
      response_dict = _Model_from_mldev(self.api_client, response_dict)

    return_value = types.Model._from_response(response_dict, parameter_model)
    self.api_client._verify_response(return_value)
    return return_value

  async def _list(
      self, *, config: Optional[types.ListModelsConfigOrDict] = None
  ) -> types.ListModelsResponse:
    parameter_model = types._ListModelsParameters(
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _ListModelsParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = 'models'.format_map(request_dict.get('_url'))
    else:
      request_dict = _ListModelsParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = 'tunedModels'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'get', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _ListModelsResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _ListModelsResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.ListModelsResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def update(
      self,
      *,
      model: str,
      config: Optional[types.UpdateModelConfigOrDict] = None,
  ) -> types.Model:
    parameter_model = types._UpdateModelParameters(
        model=model,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _UpdateModelParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}'.format_map(request_dict.get('_url'))
    else:
      request_dict = _UpdateModelParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{name}'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'patch', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _Model_from_vertex(self.api_client, response_dict)
    else:
      response_dict = _Model_from_mldev(self.api_client, response_dict)

    return_value = types.Model._from_response(response_dict, parameter_model)
    self.api_client._verify_response(return_value)
    return return_value

  async def delete(self, *, model: str) -> types.DeleteModelResponse:
    parameter_model = types._DeleteModelParameters(
        model=model,
    )

    if self.api_client.vertexai:
      request_dict = _DeleteModelParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{name}'.format_map(request_dict.get('_url'))
    else:
      request_dict = _DeleteModelParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{name}'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'delete', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _DeleteModelResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _DeleteModelResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.DeleteModelResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def count_tokens(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.CountTokensConfigOrDict] = None,
  ) -> types.CountTokensResponse:
    """Counts the number of tokens in the given content.

    Args:
      model (str): The model to use for counting tokens.
      contents (list[types.Content]): The content to count tokens for.
        Multimodal input is supported for Gemini models.
      config (CountTokensConfig): The configuration for counting tokens.

    Usage:

    .. code-block:: python

      response = client.models.count_tokens(
          model='gemini-1.5-flash',
          contents='What is your name?',
      )
      print(response)
      # total_tokens=5 cached_content_token_count=None
    """

    parameter_model = types._CountTokensParameters(
        model=model,
        contents=contents,
        config=config,
    )

    if self.api_client.vertexai:
      request_dict = _CountTokensParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:countTokens'.format_map(request_dict.get('_url'))
    else:
      request_dict = _CountTokensParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = '{model}:countTokens'.format_map(request_dict.get('_url'))
    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _CountTokensResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _CountTokensResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.CountTokensResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def compute_tokens(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.ComputeTokensConfigOrDict] = None,
  ) -> types.ComputeTokensResponse:
    """Return a list of tokens based on the input text.

    This method is not supported by the Gemini Developer API.

    Args:
      model (str): The model to use.
      contents (list[shared.Content]): The content to compute tokens for. Only
        text is supported.

    Usage:

    .. code-block:: python

      response = client.models.compute_tokens(
          model='gemini-1.5-flash',
          contents='What is your name?',
      )
      print(response)
      # tokens_info=[TokensInfo(role='user', token_ids=['1841', ...],
      # tokens=[b'What', b' is', b' your', b' name', b'?'])]
    """

    parameter_model = types._ComputeTokensParameters(
        model=model,
        contents=contents,
        config=config,
    )

    if not self.api_client.vertexai:
      raise ValueError('This method is only supported in the Vertex AI client.')
    else:
      request_dict = _ComputeTokensParameters_to_vertex(
          self.api_client, parameter_model
      )
      path = '{model}:computeTokens'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _ComputeTokensResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _ComputeTokensResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.ComputeTokensResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def generate_content(
      self,
      *,
      model: str,
      contents: Union[types.ContentListUnion, types.ContentListUnionDict],
      config: Optional[types.GenerateContentConfigOrDict] = None,
  ) -> types.GenerateContentResponse:
    """Makes an API request to generate content using a model.

    Some models support multimodal input and output.

    Usage:

    .. code-block:: python

      from google.genai import types
      from google import genai

      client = genai.Client(
          vertexai=True, project='my-project-id', location='us-central1'
      )

      response = await client.aio.models.generate_content(
          model='gemini-1.5-flash-002',
          contents='User input: I like bagels. Answer:',
          config=types.GenerateContentConfig(
              system_instruction=
                [
                  'You are a helpful language translator.',
                  'Your mission is to translate text in English to French.'
                ]
          ),
      )
      print(response.text)
      # J'aime les bagels.
    """
    if _extra_utils.should_disable_afc(config):
      return await self._generate_content(
          model=model, contents=contents, config=config
      )
    remaining_remote_calls_afc = _extra_utils.get_max_remote_calls_afc(config)
    logging.info(
        f'AFC is enabled with max remote calls: {remaining_remote_calls_afc}.'
    )
    automatic_function_calling_history = []
    while remaining_remote_calls_afc > 0:
      response = await self._generate_content(
          model=model, contents=contents, config=config
      )
      remaining_remote_calls_afc -= 1
      if remaining_remote_calls_afc == 0:
        logging.info('Reached max remote calls for automatic function calling.')

      function_map = _extra_utils.get_function_map(config)
      if not function_map:
        break
      if (
          not response.candidates
          or not response.candidates[0].content
          or not response.candidates[0].content.parts
      ):
        break
      func_response_parts = _extra_utils.get_function_response_parts(
          response, function_map
      )
      if not func_response_parts:
        break
      contents = t.t_contents(self.api_client, contents)
      contents.append(response.candidates[0].content)
      contents.append(
          types.Content(
              role='user',
              parts=func_response_parts,
          )
      )
      automatic_function_calling_history.extend(contents)

    if _extra_utils.should_append_afc_history(config):
      response.automatic_function_calling_history = (
          automatic_function_calling_history
      )
    return response

  async def list(
      self,
      *,
      config: Optional[types.ListModelsConfigOrDict] = None,
  ) -> AsyncPager[types.Model]:
    """Makes an API request to list the tuned models available to your project.

    This method only lists tuned models for the Vertex AI API.

    Usage:

    .. code-block:: python

      response = await client.aio.models.list(config={'page_size': 5})
      print(response.page)
      # [Model(name='projects/./locations/./models/123', display_name='my_model'
    """

    config = (
        types._ListModelsParameters(config=config).config
        or types.ListModelsConfig()
    )

    if self.api_client.vertexai:
      # Filter for tuning jobs artifacts by labels.
      config = config.copy()
      filter_value = config.filter
      config.filter = (
          filter_value + '&filter=labels.tune-type:*'
          if filter_value
          else 'labels.tune-type:*'
      )
    return AsyncPager(
        'models',
        self._list,
        await self._list(config=config),
        config,
    )

  async def upscale_image(
      self,
      *,
      model: str,
      image: types.ImageOrDict,
      config: types.UpscaleImageConfigOrDict,
  ) -> types.UpscaleImageResponse:
    """Makes an API request to upscale a provided image.

    Args:
      model (str): The model to use.
      image (Image): The input image for upscaling.
      config (UpscaleImageConfig): Configuration for upscaling.

    Usage:

    .. code-block:: python

      from google.genai.types import Image

      IMAGE_FILE_PATH="my-image.png"
      response = await client.aio.models.upscale_image(
          model = 'imagen-3.0-generate-001',
          image = types.Image.from_file(IMAGE_FILE_PATH),
                  config = {
                    'upscale_factor': 'x2',
                  }
      )
      response.generated_images[0].image.show()
      # Opens my-image.png which is upscaled by a factor of 2.
    """

    # Validate config.
    types.UpscaleImageParameters(
        model=model,
        image=image,
        config=config,
    )

    # Convert to API config.
    config_dct = config if isinstance(config, dict) else config.dict()
    api_config = types._UpscaleImageAPIConfigDict(**config_dct)  # pylint: disable=protected-access

    # Provide default values through API config.
    api_config['mode'] = 'upscale'
    api_config['number_of_images'] = 1

    return await self._upscale_image(
        model=model, image=image, config=api_config
    )
