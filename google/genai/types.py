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

import datetime
import inspect
import json
import logging
from typing import Any, Callable, Literal, Optional, TypedDict, Union
import PIL.Image
import pydantic
from pydantic import Field
from . import _common


Outcome = Literal[
    "OUTCOME_UNSPECIFIED",
    "OUTCOME_OK",
    "OUTCOME_FAILED",
    "OUTCOME_DEADLINE_EXCEEDED",
]


Language = Literal["LANGUAGE_UNSPECIFIED", "PYTHON"]


Type = Literal[
    "TYPE_UNSPECIFIED",
    "STRING",
    "NUMBER",
    "INTEGER",
    "BOOLEAN",
    "ARRAY",
    "OBJECT",
]


HarmCategory = Literal[
    "HARM_CATEGORY_UNSPECIFIED",
    "HARM_CATEGORY_HATE_SPEECH",
    "HARM_CATEGORY_DANGEROUS_CONTENT",
    "HARM_CATEGORY_HARASSMENT",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "HARM_CATEGORY_CIVIC_INTEGRITY",
]


HarmBlockMethod = Literal[
    "HARM_BLOCK_METHOD_UNSPECIFIED", "SEVERITY", "PROBABILITY"
]


HarmBlockThreshold = Literal[
    "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
    "BLOCK_LOW_AND_ABOVE",
    "BLOCK_MEDIUM_AND_ABOVE",
    "BLOCK_ONLY_HIGH",
    "BLOCK_NONE",
    "OFF",
]


Mode = Literal["MODE_UNSPECIFIED", "MODE_DYNAMIC"]


FinishReason = Literal[
    "FINISH_REASON_UNSPECIFIED",
    "STOP",
    "MAX_TOKENS",
    "SAFETY",
    "RECITATION",
    "OTHER",
    "BLOCKLIST",
    "PROHIBITED_CONTENT",
    "SPII",
    "MALFORMED_FUNCTION_CALL",
]


HarmProbability = Literal[
    "HARM_PROBABILITY_UNSPECIFIED", "NEGLIGIBLE", "LOW", "MEDIUM", "HIGH"
]


HarmSeverity = Literal[
    "HARM_SEVERITY_UNSPECIFIED",
    "HARM_SEVERITY_NEGLIGIBLE",
    "HARM_SEVERITY_LOW",
    "HARM_SEVERITY_MEDIUM",
    "HARM_SEVERITY_HIGH",
]


BlockedReason = Literal[
    "BLOCKED_REASON_UNSPECIFIED",
    "SAFETY",
    "OTHER",
    "BLOCKLIST",
    "PROHIBITED_CONTENT",
]


DeploymentResourcesType = Literal[
    "DEPLOYMENT_RESOURCES_TYPE_UNSPECIFIED",
    "DEDICATED_RESOURCES",
    "AUTOMATIC_RESOURCES",
    "SHARED_RESOURCES",
]


JobState = Literal[
    "JOB_STATE_UNSPECIFIED",
    "JOB_STATE_QUEUED",
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_SUCCEEDED",
    "JOB_STATE_FAILED",
    "JOB_STATE_CANCELLING",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_PAUSED",
    "JOB_STATE_EXPIRED",
    "JOB_STATE_UPDATING",
    "JOB_STATE_PARTIALLY_SUCCEEDED",
]


AdapterSize = Literal[
    "ADAPTER_SIZE_UNSPECIFIED",
    "ADAPTER_SIZE_ONE",
    "ADAPTER_SIZE_FOUR",
    "ADAPTER_SIZE_EIGHT",
    "ADAPTER_SIZE_SIXTEEN",
    "ADAPTER_SIZE_THIRTY_TWO",
]


State = Literal["STATE_UNSPECIFIED", "ACTIVE", "ERROR"]


DynamicRetrievalConfigMode = Literal["MODE_UNSPECIFIED", "MODE_DYNAMIC"]


FunctionCallingConfigMode = Literal["MODE_UNSPECIFIED", "AUTO", "ANY", "NONE"]


MediaResolution = Literal[
    "MEDIA_RESOLUTION_UNSPECIFIED",
    "MEDIA_RESOLUTION_LOW",
    "MEDIA_RESOLUTION_MEDIUM",
    "MEDIA_RESOLUTION_HIGH",
]


SafetyFilterLevel = Literal[
    "BLOCK_LOW_AND_ABOVE",
    "BLOCK_MEDIUM_AND_ABOVE",
    "BLOCK_ONLY_HIGH",
    "BLOCK_NONE",
]


PersonGeneration = Literal["DONT_ALLOW", "ALLOW_ADULT", "ALLOW_ALL"]


ImagePromptLanguage = Literal["auto", "en", "ja", "ko", "hi"]


MaskReferenceMode = Literal[
    "MASK_MODE_DEFAULT",
    "MASK_MODE_USER_PROVIDED",
    "MASK_MODE_BACKGROUND",
    "MASK_MODE_FOREGROUND",
    "MASK_MODE_SEMANTIC",
]


ControlReferenceType = Literal[
    "CONTROL_TYPE_DEFAULT",
    "CONTROL_TYPE_CANNY",
    "CONTROL_TYPE_SCRIBBLE",
    "CONTROL_TYPE_FACE_MESH",
]


SubjectReferenceType = Literal[
    "SUBJECT_TYPE_DEFAULT",
    "SUBJECT_TYPE_PERSON",
    "SUBJECT_TYPE_ANIMAL",
    "SUBJECT_TYPE_PRODUCT",
]


EditMode = Literal[
    "EDIT_MODE_DEFAULT",
    "EDIT_MODE_INPAINT_REMOVAL",
    "EDIT_MODE_INPAINT_INSERTION",
    "EDIT_MODE_OUTPAINT",
    "EDIT_MODE_CONTROLLED_EDITING",
    "EDIT_MODE_STYLE",
    "EDIT_MODE_BGSWAP",
    "EDIT_MODE_PRODUCT_IMAGE",
]


FileState = Literal["STATE_UNSPECIFIED", "PROCESSING", "ACTIVE", "FAILED"]


class VideoMetadata(_common.BaseModel):
  """Metadata describes the input video content."""

  end_offset: Optional[str] = Field(
      default=None, description="""Optional. The end offset of the video."""
  )
  start_offset: Optional[str] = Field(
      default=None, description="""Optional. The start offset of the video."""
  )


class VideoMetadataDict(TypedDict, total=False):
  """Metadata describes the input video content."""

  end_offset: Optional[str]
  """Optional. The end offset of the video."""

  start_offset: Optional[str]
  """Optional. The start offset of the video."""


VideoMetadataOrDict = Union[VideoMetadata, VideoMetadataDict]


class CodeExecutionResult(_common.BaseModel):
  """Result of executing the [ExecutableCode].

  Always follows a `part` containing the [ExecutableCode].
  """

  outcome: Optional[Outcome] = Field(
      default=None, description="""Required. Outcome of the code execution."""
  )
  output: Optional[str] = Field(
      default=None,
      description="""Optional. Contains stdout when code execution is successful, stderr or other description otherwise.""",
  )


class CodeExecutionResultDict(TypedDict, total=False):
  """Result of executing the [ExecutableCode].

  Always follows a `part` containing the [ExecutableCode].
  """

  outcome: Optional[Outcome]
  """Required. Outcome of the code execution."""

  output: Optional[str]
  """Optional. Contains stdout when code execution is successful, stderr or other description otherwise."""


CodeExecutionResultOrDict = Union[CodeExecutionResult, CodeExecutionResultDict]


class ExecutableCode(_common.BaseModel):
  """Code generated by the model that is meant to be executed, and the result returned to the model.

  Generated when using the [FunctionDeclaration] tool and
  [FunctionCallingConfig] mode is set to [Mode.CODE].
  """

  code: Optional[str] = Field(
      default=None, description="""Required. The code to be executed."""
  )
  language: Optional[Language] = Field(
      default=None,
      description="""Required. Programming language of the `code`.""",
  )


class ExecutableCodeDict(TypedDict, total=False):
  """Code generated by the model that is meant to be executed, and the result returned to the model.

  Generated when using the [FunctionDeclaration] tool and
  [FunctionCallingConfig] mode is set to [Mode.CODE].
  """

  code: Optional[str]
  """Required. The code to be executed."""

  language: Optional[Language]
  """Required. Programming language of the `code`."""


ExecutableCodeOrDict = Union[ExecutableCode, ExecutableCodeDict]


class FileData(_common.BaseModel):
  """URI based data."""

  file_uri: Optional[str] = Field(
      default=None, description="""Required. URI."""
  )
  mime_type: Optional[str] = Field(
      default=None,
      description="""Required. The IANA standard MIME type of the source data.""",
  )


class FileDataDict(TypedDict, total=False):
  """URI based data."""

  file_uri: Optional[str]
  """Required. URI."""

  mime_type: Optional[str]
  """Required. The IANA standard MIME type of the source data."""


FileDataOrDict = Union[FileData, FileDataDict]


class FunctionCall(_common.BaseModel):
  """A function call."""

  id: Optional[str] = Field(
      default=None,
      description="""The unique id of the function call. If populated, the client to execute the
   `function_call` and return the response with the matching `id`.""",
  )
  args: Optional[dict[str, Any]] = Field(
      default=None,
      description="""Optional. Required. The function parameters and values in JSON object format. See [FunctionDeclaration.parameters] for parameter details.""",
  )
  name: Optional[str] = Field(
      default=None,
      description="""Required. The name of the function to call. Matches [FunctionDeclaration.name].""",
  )


class FunctionCallDict(TypedDict, total=False):
  """A function call."""

  id: Optional[str]
  """The unique id of the function call. If populated, the client to execute the
   `function_call` and return the response with the matching `id`."""

  args: Optional[dict[str, Any]]
  """Optional. Required. The function parameters and values in JSON object format. See [FunctionDeclaration.parameters] for parameter details."""

  name: Optional[str]
  """Required. The name of the function to call. Matches [FunctionDeclaration.name]."""


FunctionCallOrDict = Union[FunctionCall, FunctionCallDict]


class FunctionResponse(_common.BaseModel):
  """A function response."""

  id: Optional[str] = Field(
      default=None,
      description="""The id of the function call this response is for. Populated by the client
   to match the corresponding function call `id`.""",
  )
  name: Optional[str] = Field(
      default=None,
      description="""Required. The name of the function to call. Matches [FunctionDeclaration.name] and [FunctionCall.name].""",
  )
  response: Optional[dict[str, Any]] = Field(
      default=None,
      description="""Required. The function response in JSON object format. Use "output" key to specify function output and "error" key to specify error details (if any). If "output" and "error" keys are not specified, then whole "response" is treated as function output.""",
  )


class FunctionResponseDict(TypedDict, total=False):
  """A function response."""

  id: Optional[str]
  """The id of the function call this response is for. Populated by the client
   to match the corresponding function call `id`."""

  name: Optional[str]
  """Required. The name of the function to call. Matches [FunctionDeclaration.name] and [FunctionCall.name]."""

  response: Optional[dict[str, Any]]
  """Required. The function response in JSON object format. Use "output" key to specify function output and "error" key to specify error details (if any). If "output" and "error" keys are not specified, then whole "response" is treated as function output."""


FunctionResponseOrDict = Union[FunctionResponse, FunctionResponseDict]


class Blob(_common.BaseModel):
  """Content blob.

  It's preferred to send as text directly rather than raw bytes.
  """

  data: Optional[bytes] = Field(
      default=None, description="""Required. Raw bytes."""
  )
  mime_type: Optional[str] = Field(
      default=None,
      description="""Required. The IANA standard MIME type of the source data.""",
  )


class BlobDict(TypedDict, total=False):
  """Content blob.

  It's preferred to send as text directly rather than raw bytes.
  """

  data: Optional[bytes]
  """Required. Raw bytes."""

  mime_type: Optional[str]
  """Required. The IANA standard MIME type of the source data."""


BlobOrDict = Union[Blob, BlobDict]


class Part(_common.BaseModel):
  """A datatype containing media content.

  Exactly one field within a Part should be set, representing the specific type
  of content being conveyed. Using multiple fields within the same `Part`
  instance is considered invalid.
  """

  video_metadata: Optional[VideoMetadata] = Field(
      default=None, description="""Metadata for a given video."""
  )
  code_execution_result: Optional[CodeExecutionResult] = Field(
      default=None,
      description="""Optional. Result of executing the [ExecutableCode].""",
  )
  executable_code: Optional[ExecutableCode] = Field(
      default=None,
      description="""Optional. Code generated by the model that is meant to be executed.""",
  )
  file_data: Optional[FileData] = Field(
      default=None, description="""Optional. URI based data."""
  )
  function_call: Optional[FunctionCall] = Field(
      default=None,
      description="""Optional. A predicted [FunctionCall] returned from the model that contains a string representing the [FunctionDeclaration.name] with the parameters and their values.""",
  )
  function_response: Optional[FunctionResponse] = Field(
      default=None,
      description="""Optional. The result output of a [FunctionCall] that contains a string representing the [FunctionDeclaration.name] and a structured JSON object containing any output from the function call. It is used as context to the model.""",
  )
  inline_data: Optional[Blob] = Field(
      default=None, description="""Optional. Inlined bytes data."""
  )
  text: Optional[str] = Field(
      default=None, description="""Optional. Text part (can be code)."""
  )

  @classmethod
  def from_uri(cls, file_uri: str, mime_type: str) -> "Part":
    file_data = FileData(file_uri=file_uri, mime_type=mime_type)
    return cls(file_data=file_data)

  @classmethod
  def from_text(cls, text: str) -> "Part":
    return cls(text=text)

  @classmethod
  def from_bytes(cls, data: bytes, mime_type: str) -> "Part":
    inline_data = Blob(
        data=data,
        mime_type=mime_type,
    )
    return cls(inline_data=inline_data)

  @classmethod
  def from_function_call(cls, name: str, args: dict[str, Any]) -> "Part":
    function_call = FunctionCall(name=name, args=args)
    return cls(function_call=function_call)

  @classmethod
  def from_function_response(
      cls, name: str, response: dict[str, Any]
  ) -> "Part":
    function_response = FunctionResponse(name=name, response=response)
    return cls(function_response=function_response)

  @classmethod
  def from_video_metadata(cls, end_offset: str, start_offset: str) -> "Part":
    video_metadata = VideoMetadata(
        end_offset=end_offset, start_offset=start_offset
    )
    return cls(video_metadata=video_metadata)

  @classmethod
  def from_executable_code(cls, code: str, language: Language) -> "Part":
    executable_code = ExecutableCode(code=code, language=language)
    return cls(executable_code=executable_code)

  @classmethod
  def from_code_execution_result(cls, outcome: Outcome, output: str) -> "Part":
    code_execution_result = CodeExecutionResult(outcome=outcome, output=output)
    return cls(code_execution_result=code_execution_result)


class PartDict(TypedDict, total=False):
  """A datatype containing media content.

  Exactly one field within a Part should be set, representing the specific type
  of content being conveyed. Using multiple fields within the same `Part`
  instance is considered invalid.
  """

  video_metadata: Optional[VideoMetadataDict]
  """Metadata for a given video."""

  code_execution_result: Optional[CodeExecutionResultDict]
  """Optional. Result of executing the [ExecutableCode]."""

  executable_code: Optional[ExecutableCodeDict]
  """Optional. Code generated by the model that is meant to be executed."""

  file_data: Optional[FileDataDict]
  """Optional. URI based data."""

  function_call: Optional[FunctionCallDict]
  """Optional. A predicted [FunctionCall] returned from the model that contains a string representing the [FunctionDeclaration.name] with the parameters and their values."""

  function_response: Optional[FunctionResponseDict]
  """Optional. The result output of a [FunctionCall] that contains a string representing the [FunctionDeclaration.name] and a structured JSON object containing any output from the function call. It is used as context to the model."""

  inline_data: Optional[BlobDict]
  """Optional. Inlined bytes data."""

  text: Optional[str]
  """Optional. Text part (can be code)."""


PartOrDict = Union[Part, PartDict]
PartUnion = Union[Part, PIL.Image.Image, str]
PartUnionDict = Union[PartUnion, PartDict]


class Content(_common.BaseModel):
  """Contains the multi-part content of a message."""

  parts: Optional[list[Part]] = Field(
      default=None,
      description="""List of parts that constitute a single message. Each part may have
      a different IANA MIME type.""",
  )
  role: Optional[str] = Field(
      default=None,
      description="""Optional. The producer of the content. Must be either 'user' or 'model'. Useful to set for multi-turn conversations, otherwise can be left blank or unset.""",
  )


class ContentDict(TypedDict, total=False):
  """Contains the multi-part content of a message."""

  parts: Optional[list[PartDict]]
  """List of parts that constitute a single message. Each part may have
      a different IANA MIME type."""

  role: Optional[str]
  """Optional. The producer of the content. Must be either 'user' or 'model'. Useful to set for multi-turn conversations, otherwise can be left blank or unset."""


ContentOrDict = Union[Content, ContentDict]
ContentUnion = Union[Content, list[PartUnion], PartUnion]
ContentUnionDict = Union[ContentUnion, ContentDict]

ContentListUnion = Union[list[ContentUnion], ContentUnion]
ContentListUnionDict = Union[list[ContentUnionDict], ContentUnionDict]


class Schema(_common.BaseModel):
  """Schema that defines the format of input and output data.

  Represents a select subset of an OpenAPI 3.0 schema object.
  """

  min_items: Optional[str] = Field(
      default=None,
      description="""Optional. Minimum number of the elements for Type.ARRAY.""",
  )
  example: Optional[Any] = Field(
      default=None,
      description="""Optional. Example of the object. Will only populated when the object is the root.""",
  )
  property_ordering: Optional[list[str]] = Field(
      default=None,
      description="""Optional. The order of the properties. Not a standard field in open api spec. Only used to support the order of the properties.""",
  )
  pattern: Optional[str] = Field(
      default=None,
      description="""Optional. Pattern of the Type.STRING to restrict a string to a regular expression.""",
  )
  minimum: Optional[float] = Field(
      default=None,
      description="""Optional. SCHEMA FIELDS FOR TYPE INTEGER and NUMBER Minimum value of the Type.INTEGER and Type.NUMBER""",
  )
  default: Optional[Any] = Field(
      default=None, description="""Optional. Default value of the data."""
  )
  any_of: list["Schema"] = Field(
      default=None,
      description="""Optional. The value should be validated against any (one or more) of the subschemas in the list.""",
  )
  max_length: Optional[str] = Field(
      default=None,
      description="""Optional. Maximum length of the Type.STRING""",
  )
  title: Optional[str] = Field(
      default=None, description="""Optional. The title of the Schema."""
  )
  min_length: Optional[str] = Field(
      default=None,
      description="""Optional. SCHEMA FIELDS FOR TYPE STRING Minimum length of the Type.STRING""",
  )
  min_properties: Optional[str] = Field(
      default=None,
      description="""Optional. Minimum number of the properties for Type.OBJECT.""",
  )
  max_items: Optional[str] = Field(
      default=None,
      description="""Optional. Maximum number of the elements for Type.ARRAY.""",
  )
  maximum: Optional[float] = Field(
      default=None,
      description="""Optional. Maximum value of the Type.INTEGER and Type.NUMBER""",
  )
  nullable: Optional[bool] = Field(
      default=None,
      description="""Optional. Indicates if the value may be null.""",
  )
  max_properties: Optional[str] = Field(
      default=None,
      description="""Optional. Maximum number of the properties for Type.OBJECT.""",
  )
  type: Optional[Type] = Field(
      default=None, description="""Optional. The type of the data."""
  )
  description: Optional[str] = Field(
      default=None, description="""Optional. The description of the data."""
  )
  enum: Optional[list[str]] = Field(
      default=None,
      description="""Optional. Possible values of the element of primitive type with enum format. Examples: 1. We can define direction as : {type:STRING, format:enum, enum:["EAST", NORTH", "SOUTH", "WEST"]} 2. We can define apartment number as : {type:INTEGER, format:enum, enum:["101", "201", "301"]}""",
  )
  format: Optional[str] = Field(
      default=None,
      description="""Optional. The format of the data. Supported formats: for NUMBER type: "float", "double" for INTEGER type: "int32", "int64" for STRING type: "email", "byte", etc""",
  )
  items: "Schema" = Field(
      default=None,
      description="""Optional. SCHEMA FIELDS FOR TYPE ARRAY Schema of the elements of Type.ARRAY.""",
  )
  properties: dict[str, "Schema"] = Field(
      default=None,
      description="""Optional. SCHEMA FIELDS FOR TYPE OBJECT Properties of Type.OBJECT.""",
  )
  required: Optional[list[str]] = Field(
      default=None,
      description="""Optional. Required properties of Type.OBJECT.""",
  )


class SchemaDict(TypedDict, total=False):
  """Schema that defines the format of input and output data.

  Represents a select subset of an OpenAPI 3.0 schema object.
  """

  min_items: Optional[str]
  """Optional. Minimum number of the elements for Type.ARRAY."""

  example: Optional[Any]
  """Optional. Example of the object. Will only populated when the object is the root."""

  property_ordering: Optional[list[str]]
  """Optional. The order of the properties. Not a standard field in open api spec. Only used to support the order of the properties."""

  pattern: Optional[str]
  """Optional. Pattern of the Type.STRING to restrict a string to a regular expression."""

  minimum: Optional[float]
  """Optional. SCHEMA FIELDS FOR TYPE INTEGER and NUMBER Minimum value of the Type.INTEGER and Type.NUMBER"""

  default: Optional[Any]
  """Optional. Default value of the data."""

  any_of: list["SchemaDict"]
  """Optional. The value should be validated against any (one or more) of the subschemas in the list."""

  max_length: Optional[str]
  """Optional. Maximum length of the Type.STRING"""

  title: Optional[str]
  """Optional. The title of the Schema."""

  min_length: Optional[str]
  """Optional. SCHEMA FIELDS FOR TYPE STRING Minimum length of the Type.STRING"""

  min_properties: Optional[str]
  """Optional. Minimum number of the properties for Type.OBJECT."""

  max_items: Optional[str]
  """Optional. Maximum number of the elements for Type.ARRAY."""

  maximum: Optional[float]
  """Optional. Maximum value of the Type.INTEGER and Type.NUMBER"""

  nullable: Optional[bool]
  """Optional. Indicates if the value may be null."""

  max_properties: Optional[str]
  """Optional. Maximum number of the properties for Type.OBJECT."""

  type: Optional[Type]
  """Optional. The type of the data."""

  description: Optional[str]
  """Optional. The description of the data."""

  enum: Optional[list[str]]
  """Optional. Possible values of the element of primitive type with enum format. Examples: 1. We can define direction as : {type:STRING, format:enum, enum:["EAST", NORTH", "SOUTH", "WEST"]} 2. We can define apartment number as : {type:INTEGER, format:enum, enum:["101", "201", "301"]}"""

  format: Optional[str]
  """Optional. The format of the data. Supported formats: for NUMBER type: "float", "double" for INTEGER type: "int32", "int64" for STRING type: "email", "byte", etc"""

  items: "SchemaDict"
  """Optional. SCHEMA FIELDS FOR TYPE ARRAY Schema of the elements of Type.ARRAY."""

  properties: dict[str, "SchemaDict"]
  """Optional. SCHEMA FIELDS FOR TYPE OBJECT Properties of Type.OBJECT."""

  required: Optional[list[str]]
  """Optional. Required properties of Type.OBJECT."""


SchemaOrDict = Union[Schema, SchemaDict]
SchemaUnion = Union[dict, type, Schema]
SchemaUnionDict = Union[SchemaUnion, SchemaDict]


class SafetySetting(_common.BaseModel):
  """Safety settings."""

  method: Optional[HarmBlockMethod] = Field(
      default=None,
      description="""Determines if the harm block method uses probability or probability
      and severity scores.""",
  )
  category: Optional[HarmCategory] = Field(
      default=None, description="""Required. Harm category."""
  )
  threshold: Optional[HarmBlockThreshold] = Field(
      default=None, description="""Required. The harm block threshold."""
  )


class SafetySettingDict(TypedDict, total=False):
  """Safety settings."""

  method: Optional[HarmBlockMethod]
  """Determines if the harm block method uses probability or probability
      and severity scores."""

  category: Optional[HarmCategory]
  """Required. Harm category."""

  threshold: Optional[HarmBlockThreshold]
  """Required. The harm block threshold."""


SafetySettingOrDict = Union[SafetySetting, SafetySettingDict]


class FunctionDeclaration(_common.BaseModel):
  """Defines a function that the model can generate JSON inputs for.

  The inputs are based on `OpenAPI 3.0 specifications
  <https://spec.openapis.org/oas/v3.0.3>`_.
  """

  response: Optional[Schema] = Field(
      default=None,
      description="""Describes the output from the function in the OpenAPI JSON Schema
      Object format.""",
  )
  description: Optional[str] = Field(
      default=None,
      description="""Optional. Description and purpose of the function. Model uses it to decide how and whether to call the function.""",
  )
  name: Optional[str] = Field(
      default=None,
      description="""Required. The name of the function to call. Must start with a letter or an underscore. Must be a-z, A-Z, 0-9, or contain underscores, dots and dashes, with a maximum length of 64.""",
  )
  parameters: Optional[Schema] = Field(
      default=None,
      description="""Optional. Describes the parameters to this function in JSON Schema Object format. Reflects the Open API 3.03 Parameter Object. string Key: the name of the parameter. Parameter names are case sensitive. Schema Value: the Schema defining the type used for the parameter. For function with no parameters, this can be left unset. Parameter names must start with a letter or an underscore and must only contain chars a-z, A-Z, 0-9, or underscores with a maximum length of 64. Example with 1 required and 1 optional parameter: type: OBJECT properties: param1: type: STRING param2: type: INTEGER required: - param1""",
  )

  @staticmethod
  def from_function(client, func: Callable) -> "FunctionDeclaration":
    """Converts a function to a FunctionDeclaration."""
    from . import _automatic_function_calling_util

    parameters_properties = {}
    for name, param in inspect.signature(func).parameters.items():
      if param.kind in (
          inspect.Parameter.POSITIONAL_OR_KEYWORD,
          inspect.Parameter.KEYWORD_ONLY,
          inspect.Parameter.POSITIONAL_ONLY,
      ):
        schema = _automatic_function_calling_util._parse_schema_from_parameter(
            client, param, func.__name__
        )
        parameters_properties[name] = schema
    declaration = FunctionDeclaration(
        name=func.__name__,
        description=func.__doc__,
    )
    if parameters_properties:
      declaration.parameters = Schema(
          type="OBJECT",
          properties=parameters_properties,
      )
      if client.vertexai:
        declaration.parameters.required = (
            _automatic_function_calling_util._get_required_fields(
                declaration.parameters
            )
        )
    if not client.vertexai:
      return declaration

    return_annotation = inspect.signature(func).return_annotation
    if return_annotation is inspect._empty:
      return declaration

    declaration.response = (
        _automatic_function_calling_util._parse_schema_from_parameter(
            client,
            inspect.Parameter(
                "return_value",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=return_annotation,
            ),
            func.__name__,
        )
    )
    return declaration


class FunctionDeclarationDict(TypedDict, total=False):
  """Defines a function that the model can generate JSON inputs for.

  The inputs are based on `OpenAPI 3.0 specifications
  <https://spec.openapis.org/oas/v3.0.3>`_.
  """

  response: Optional[SchemaDict]
  """Describes the output from the function in the OpenAPI JSON Schema
      Object format."""

  description: Optional[str]
  """Optional. Description and purpose of the function. Model uses it to decide how and whether to call the function."""

  name: Optional[str]
  """Required. The name of the function to call. Must start with a letter or an underscore. Must be a-z, A-Z, 0-9, or contain underscores, dots and dashes, with a maximum length of 64."""

  parameters: Optional[SchemaDict]
  """Optional. Describes the parameters to this function in JSON Schema Object format. Reflects the Open API 3.03 Parameter Object. string Key: the name of the parameter. Parameter names are case sensitive. Schema Value: the Schema defining the type used for the parameter. For function with no parameters, this can be left unset. Parameter names must start with a letter or an underscore and must only contain chars a-z, A-Z, 0-9, or underscores with a maximum length of 64. Example with 1 required and 1 optional parameter: type: OBJECT properties: param1: type: STRING param2: type: INTEGER required: - param1"""


FunctionDeclarationOrDict = Union[FunctionDeclaration, FunctionDeclarationDict]


class GoogleSearch(_common.BaseModel):
  """Tool to support Google Search in Model. Powered by Google."""

  pass


class GoogleSearchDict(TypedDict, total=False):
  """Tool to support Google Search in Model. Powered by Google."""

  pass


GoogleSearchOrDict = Union[GoogleSearch, GoogleSearchDict]


class DynamicRetrievalConfig(_common.BaseModel):
  """Describes the options to customize dynamic retrieval."""

  mode: Optional[DynamicRetrievalConfigMode] = Field(
      default=None,
      description="""The mode of the predictor to be used in dynamic retrieval.""",
  )
  dynamic_threshold: Optional[float] = Field(
      default=None,
      description="""Optional. The threshold to be used in dynamic retrieval. If not set, a system default value is used.""",
  )


class DynamicRetrievalConfigDict(TypedDict, total=False):
  """Describes the options to customize dynamic retrieval."""

  mode: Optional[DynamicRetrievalConfigMode]
  """The mode of the predictor to be used in dynamic retrieval."""

  dynamic_threshold: Optional[float]
  """Optional. The threshold to be used in dynamic retrieval. If not set, a system default value is used."""


DynamicRetrievalConfigOrDict = Union[
    DynamicRetrievalConfig, DynamicRetrievalConfigDict
]


class GoogleSearchRetrieval(_common.BaseModel):
  """Tool to retrieve public web data for grounding, powered by Google."""

  dynamic_retrieval_config: Optional[DynamicRetrievalConfig] = Field(
      default=None,
      description="""Specifies the dynamic retrieval configuration for the given source.""",
  )


class GoogleSearchRetrievalDict(TypedDict, total=False):
  """Tool to retrieve public web data for grounding, powered by Google."""

  dynamic_retrieval_config: Optional[DynamicRetrievalConfigDict]
  """Specifies the dynamic retrieval configuration for the given source."""


GoogleSearchRetrievalOrDict = Union[
    GoogleSearchRetrieval, GoogleSearchRetrievalDict
]


class VertexAISearch(_common.BaseModel):
  """Retrieve from Vertex AI Search datastore for grounding.

  See https://cloud.google.com/products/agent-builder
  """

  datastore: Optional[str] = Field(
      default=None,
      description="""Required. Fully-qualified Vertex AI Search data store resource ID. Format: `projects/{project}/locations/{location}/collections/{collection}/dataStores/{dataStore}`""",
  )


class VertexAISearchDict(TypedDict, total=False):
  """Retrieve from Vertex AI Search datastore for grounding.

  See https://cloud.google.com/products/agent-builder
  """

  datastore: Optional[str]
  """Required. Fully-qualified Vertex AI Search data store resource ID. Format: `projects/{project}/locations/{location}/collections/{collection}/dataStores/{dataStore}`"""


VertexAISearchOrDict = Union[VertexAISearch, VertexAISearchDict]


class VertexRagStoreRagResource(_common.BaseModel):
  """The definition of the Rag resource."""

  rag_corpus: Optional[str] = Field(
      default=None,
      description="""Optional. RagCorpora resource name. Format: `projects/{project}/locations/{location}/ragCorpora/{rag_corpus}`""",
  )
  rag_file_ids: Optional[list[str]] = Field(
      default=None,
      description="""Optional. rag_file_id. The files should be in the same rag_corpus set in rag_corpus field.""",
  )


class VertexRagStoreRagResourceDict(TypedDict, total=False):
  """The definition of the Rag resource."""

  rag_corpus: Optional[str]
  """Optional. RagCorpora resource name. Format: `projects/{project}/locations/{location}/ragCorpora/{rag_corpus}`"""

  rag_file_ids: Optional[list[str]]
  """Optional. rag_file_id. The files should be in the same rag_corpus set in rag_corpus field."""


VertexRagStoreRagResourceOrDict = Union[
    VertexRagStoreRagResource, VertexRagStoreRagResourceDict
]


class VertexRagStore(_common.BaseModel):
  """Retrieve from Vertex RAG Store for grounding."""

  rag_corpora: Optional[list[str]] = Field(
      default=None,
      description="""Optional. Deprecated. Please use rag_resources instead.""",
  )
  rag_resources: Optional[list[VertexRagStoreRagResource]] = Field(
      default=None,
      description="""Optional. The representation of the rag source. It can be used to specify corpus only or ragfiles. Currently only support one corpus or multiple files from one corpus. In the future we may open up multiple corpora support.""",
  )
  similarity_top_k: Optional[int] = Field(
      default=None,
      description="""Optional. Number of top k results to return from the selected corpora.""",
  )
  vector_distance_threshold: Optional[float] = Field(
      default=None,
      description="""Optional. Only return results with vector distance smaller than the threshold.""",
  )


class VertexRagStoreDict(TypedDict, total=False):
  """Retrieve from Vertex RAG Store for grounding."""

  rag_corpora: Optional[list[str]]
  """Optional. Deprecated. Please use rag_resources instead."""

  rag_resources: Optional[list[VertexRagStoreRagResourceDict]]
  """Optional. The representation of the rag source. It can be used to specify corpus only or ragfiles. Currently only support one corpus or multiple files from one corpus. In the future we may open up multiple corpora support."""

  similarity_top_k: Optional[int]
  """Optional. Number of top k results to return from the selected corpora."""

  vector_distance_threshold: Optional[float]
  """Optional. Only return results with vector distance smaller than the threshold."""


VertexRagStoreOrDict = Union[VertexRagStore, VertexRagStoreDict]


class Retrieval(_common.BaseModel):
  """Defines a retrieval tool that model can call to access external knowledge."""

  disable_attribution: Optional[bool] = Field(
      default=None,
      description="""Optional. Deprecated. This option is no longer supported.""",
  )
  vertex_ai_search: Optional[VertexAISearch] = Field(
      default=None,
      description="""Set to use data source powered by Vertex AI Search.""",
  )
  vertex_rag_store: Optional[VertexRagStore] = Field(
      default=None,
      description="""Set to use data source powered by Vertex RAG store. User data is uploaded via the VertexRagDataService.""",
  )


class RetrievalDict(TypedDict, total=False):
  """Defines a retrieval tool that model can call to access external knowledge."""

  disable_attribution: Optional[bool]
  """Optional. Deprecated. This option is no longer supported."""

  vertex_ai_search: Optional[VertexAISearchDict]
  """Set to use data source powered by Vertex AI Search."""

  vertex_rag_store: Optional[VertexRagStoreDict]
  """Set to use data source powered by Vertex RAG store. User data is uploaded via the VertexRagDataService."""


RetrievalOrDict = Union[Retrieval, RetrievalDict]


class ToolCodeExecution(_common.BaseModel):
  """Tool that executes code generated by the model, and automatically returns the result to the model.

  See also [ExecutableCode]and [CodeExecutionResult] which are input and output
  to this tool.
  """

  pass


class ToolCodeExecutionDict(TypedDict, total=False):
  """Tool that executes code generated by the model, and automatically returns the result to the model.

  See also [ExecutableCode]and [CodeExecutionResult] which are input and output
  to this tool.
  """

  pass


ToolCodeExecutionOrDict = Union[ToolCodeExecution, ToolCodeExecutionDict]


class Tool(_common.BaseModel):
  """Tool details of a tool that the model may use to generate a response."""

  function_declarations: Optional[list[FunctionDeclaration]] = Field(
      default=None,
      description="""List of function declarations that the tool supports.""",
  )
  retrieval: Optional[Retrieval] = Field(
      default=None,
      description="""Optional. Retrieval tool type. System will always execute the provided retrieval tool(s) to get external knowledge to answer the prompt. Retrieval results are presented to the model for generation.""",
  )
  google_search: Optional[GoogleSearch] = Field(
      default=None,
      description="""Optional. Google Search tool type. Specialized retrieval tool
      that is powered by Google Search.""",
  )
  google_search_retrieval: Optional[GoogleSearchRetrieval] = Field(
      default=None,
      description="""Optional. GoogleSearchRetrieval tool type. Specialized retrieval tool that is powered by Google search.""",
  )
  code_execution: Optional[ToolCodeExecution] = Field(
      default=None,
      description="""Optional. CodeExecution tool type. Enables the model to execute code as part of generation. This field is only used by the Gemini Developer API services.""",
  )


class ToolDict(TypedDict, total=False):
  """Tool details of a tool that the model may use to generate a response."""

  function_declarations: Optional[list[FunctionDeclarationDict]]
  """List of function declarations that the tool supports."""

  retrieval: Optional[RetrievalDict]
  """Optional. Retrieval tool type. System will always execute the provided retrieval tool(s) to get external knowledge to answer the prompt. Retrieval results are presented to the model for generation."""

  google_search: Optional[GoogleSearchDict]
  """Optional. Google Search tool type. Specialized retrieval tool
      that is powered by Google Search."""

  google_search_retrieval: Optional[GoogleSearchRetrievalDict]
  """Optional. GoogleSearchRetrieval tool type. Specialized retrieval tool that is powered by Google search."""

  code_execution: Optional[ToolCodeExecutionDict]
  """Optional. CodeExecution tool type. Enables the model to execute code as part of generation. This field is only used by the Gemini Developer API services."""


ToolOrDict = Union[Tool, ToolDict]
ToolListUnion = list[Union[Tool, Callable]]
ToolListUnionDict = list[Union[ToolDict, Callable]]


class FunctionCallingConfig(_common.BaseModel):
  """Function calling config."""

  mode: Optional[FunctionCallingConfigMode] = Field(
      default=None, description="""Optional. Function calling mode."""
  )
  allowed_function_names: Optional[list[str]] = Field(
      default=None,
      description="""Optional. Function names to call. Only set when the Mode is ANY. Function names should match [FunctionDeclaration.name]. With mode set to ANY, model will predict a function call from the set of function names provided.""",
  )


class FunctionCallingConfigDict(TypedDict, total=False):
  """Function calling config."""

  mode: Optional[FunctionCallingConfigMode]
  """Optional. Function calling mode."""

  allowed_function_names: Optional[list[str]]
  """Optional. Function names to call. Only set when the Mode is ANY. Function names should match [FunctionDeclaration.name]. With mode set to ANY, model will predict a function call from the set of function names provided."""


FunctionCallingConfigOrDict = Union[
    FunctionCallingConfig, FunctionCallingConfigDict
]


class ToolConfig(_common.BaseModel):
  """Tool config.

  This config is shared for all tools provided in the request.
  """

  function_calling_config: Optional[FunctionCallingConfig] = Field(
      default=None, description="""Optional. Function calling config."""
  )


class ToolConfigDict(TypedDict, total=False):
  """Tool config.

  This config is shared for all tools provided in the request.
  """

  function_calling_config: Optional[FunctionCallingConfigDict]
  """Optional. Function calling config."""


ToolConfigOrDict = Union[ToolConfig, ToolConfigDict]


class PrebuiltVoiceConfig(_common.BaseModel):
  """The configuration for the prebuilt speaker to use."""

  voice_name: Optional[str] = Field(
      default=None,
      description="""The name of the prebuilt voice to use.
      """,
  )


class PrebuiltVoiceConfigDict(TypedDict, total=False):
  """The configuration for the prebuilt speaker to use."""

  voice_name: Optional[str]
  """The name of the prebuilt voice to use.
      """


PrebuiltVoiceConfigOrDict = Union[PrebuiltVoiceConfig, PrebuiltVoiceConfigDict]


class VoiceConfig(_common.BaseModel):
  """The configuration for the voice to use."""

  prebuilt_voice_config: Optional[PrebuiltVoiceConfig] = Field(
      default=None,
      description="""The configuration for the speaker to use.
      """,
  )


class VoiceConfigDict(TypedDict, total=False):
  """The configuration for the voice to use."""

  prebuilt_voice_config: Optional[PrebuiltVoiceConfigDict]
  """The configuration for the speaker to use.
      """


VoiceConfigOrDict = Union[VoiceConfig, VoiceConfigDict]


class SpeechConfig(_common.BaseModel):
  """The speech generation configuration."""

  voice_config: Optional[VoiceConfig] = Field(
      default=None,
      description="""The configuration for the speaker to use.
      """,
  )


class SpeechConfigDict(TypedDict, total=False):
  """The speech generation configuration."""

  voice_config: Optional[VoiceConfigDict]
  """The configuration for the speaker to use.
      """


SpeechConfigOrDict = Union[SpeechConfig, SpeechConfigDict]
SpeechConfigUnion = Union[SpeechConfig, str]
SpeechConfigUnionDict = Union[SpeechConfigUnion, SpeechConfigDict]


class AutomaticFunctionCallingConfig(_common.BaseModel):
  """The configuration for automatic function calling."""

  disable: Optional[bool] = Field(
      default=None,
      description="""Whether to disable automatic function calling.
      If not set or set to False, will enable automatic function calling.
      If set to True, will disable automatic function calling.
      """,
  )
  maximum_remote_calls: Optional[int] = Field(
      default=10,
      description="""If automatic function calling is enabled,
      maximum number of remote calls for automatic function calling.
      This number should be a positive integer.
      If not set, SDK will set maximum number of remote calls to 10.
      """,
  )
  ignore_call_history: Optional[bool] = Field(
      default=None,
      description="""If automatic function calling is enabled,
      whether to ignore call history to the response.
      If not set, SDK will set ignore_call_history to false,
      and will append the call history to
      GenerateContentResponse.automatic_function_calling_history.
      """,
  )


class AutomaticFunctionCallingConfigDict(TypedDict, total=False):
  """The configuration for automatic function calling."""

  disable: Optional[bool]
  """Whether to disable automatic function calling.
      If not set or set to False, will enable automatic function calling.
      If set to True, will disable automatic function calling.
      """

  maximum_remote_calls: Optional[int]
  """If automatic function calling is enabled,
      maximum number of remote calls for automatic function calling.
      This number should be a positive integer.
      If not set, SDK will set maximum number of remote calls to 10.
      """

  ignore_call_history: Optional[bool]
  """If automatic function calling is enabled,
      whether to ignore call history to the response.
      If not set, SDK will set ignore_call_history to false,
      and will append the call history to
      GenerateContentResponse.automatic_function_calling_history.
      """


AutomaticFunctionCallingConfigOrDict = Union[
    AutomaticFunctionCallingConfig, AutomaticFunctionCallingConfigDict
]


class GenerationConfigRoutingConfigAutoRoutingMode(_common.BaseModel):
  """When automated routing is specified, the routing will be determined by the pretrained routing model and customer provided model routing preference."""

  model_routing_preference: Optional[
      Literal["UNKNOWN", "PRIORITIZE_QUALITY", "BALANCED", "PRIORITIZE_COST"]
  ] = Field(default=None, description="""The model routing preference.""")


class GenerationConfigRoutingConfigAutoRoutingModeDict(TypedDict, total=False):
  """When automated routing is specified, the routing will be determined by the pretrained routing model and customer provided model routing preference."""

  model_routing_preference: Optional[
      Literal["UNKNOWN", "PRIORITIZE_QUALITY", "BALANCED", "PRIORITIZE_COST"]
  ]
  """The model routing preference."""


GenerationConfigRoutingConfigAutoRoutingModeOrDict = Union[
    GenerationConfigRoutingConfigAutoRoutingMode,
    GenerationConfigRoutingConfigAutoRoutingModeDict,
]


class GenerationConfigRoutingConfigManualRoutingMode(_common.BaseModel):
  """When manual routing is set, the specified model will be used directly."""

  model_name: Optional[str] = Field(
      default=None,
      description="""The model name to use. Only the public LLM models are accepted. e.g. 'gemini-1.5-pro-001'.""",
  )


class GenerationConfigRoutingConfigManualRoutingModeDict(
    TypedDict, total=False
):
  """When manual routing is set, the specified model will be used directly."""

  model_name: Optional[str]
  """The model name to use. Only the public LLM models are accepted. e.g. 'gemini-1.5-pro-001'."""


GenerationConfigRoutingConfigManualRoutingModeOrDict = Union[
    GenerationConfigRoutingConfigManualRoutingMode,
    GenerationConfigRoutingConfigManualRoutingModeDict,
]


class GenerationConfigRoutingConfig(_common.BaseModel):
  """The configuration for routing the request to a specific model."""

  auto_mode: Optional[GenerationConfigRoutingConfigAutoRoutingMode] = Field(
      default=None, description="""Automated routing."""
  )
  manual_mode: Optional[GenerationConfigRoutingConfigManualRoutingMode] = Field(
      default=None, description="""Manual routing."""
  )


class GenerationConfigRoutingConfigDict(TypedDict, total=False):
  """The configuration for routing the request to a specific model."""

  auto_mode: Optional[GenerationConfigRoutingConfigAutoRoutingModeDict]
  """Automated routing."""

  manual_mode: Optional[GenerationConfigRoutingConfigManualRoutingModeDict]
  """Manual routing."""


GenerationConfigRoutingConfigOrDict = Union[
    GenerationConfigRoutingConfig, GenerationConfigRoutingConfigDict
]


class GenerateContentConfig(_common.BaseModel):
  """Class for configuring optional model parameters.

  For more information, see `Content generation parameters
  <https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/content-generation-parameters>`_.
  """

  system_instruction: Optional[ContentUnion] = Field(
      default=None,
      description="""Instructions for the model to steer it toward better performance.
      For example, "Answer as concisely as possible" or "Don't use technical
      terms in your response".
      """,
  )
  temperature: Optional[float] = Field(
      default=None,
      description="""Value that controls the degree of randomness in token selection.
      Lower temperatures are good for prompts that require a less open-ended or
      creative response, while higher temperatures can lead to more diverse or
      creative results.
      """,
  )
  top_p: Optional[float] = Field(
      default=None,
      description="""Tokens are selected from the most to least probable until the sum
      of their probabilities equals this value. Use a lower value for less
      random responses and a higher value for more random responses.
      """,
  )
  top_k: Optional[float] = Field(
      default=None,
      description="""For each token selection step, the ``top_k`` tokens with the
      highest probabilities are sampled. Then tokens are further filtered based
      on ``top_p`` with the final token selected using temperature sampling. Use
      a lower number for less random responses and a higher number for more
      random responses.
      """,
  )
  candidate_count: Optional[int] = Field(
      default=None,
      description="""Number of response variations to return.
      """,
  )
  max_output_tokens: Optional[int] = Field(
      default=None,
      description="""Maximum number of tokens that can be generated in the response.
      """,
  )
  stop_sequences: Optional[list[str]] = Field(
      default=None,
      description="""List of strings that tells the model to stop generating text if one
      of the strings is encountered in the response.
      """,
  )
  response_logprobs: Optional[bool] = Field(
      default=None,
      description="""Whether to return the log probabilities of the tokens that were
      chosen by the model at each step.
      """,
  )
  logprobs: Optional[int] = Field(
      default=None,
      description="""Number of top candidate tokens to return the log probabilities for
      at each generation step.
      """,
  )
  presence_penalty: Optional[float] = Field(
      default=None,
      description="""Positive values penalize tokens that already appear in the
      generated text, increasing the probability of generating more diverse
      content.
      """,
  )
  frequency_penalty: Optional[float] = Field(
      default=None,
      description="""Positive values penalize tokens that repeatedly appear in the
      generated text, increasing the probability of generating more diverse
      content.
      """,
  )
  seed: Optional[int] = Field(
      default=None,
      description="""When ``seed`` is fixed to a specific number, the model makes a best
      effort to provide the same response for repeated requests. By default, a
      random number is used.
      """,
  )
  response_mime_type: Optional[str] = Field(
      default=None,
      description="""Output response media type of the generated candidate text.
      """,
  )
  response_schema: Optional[SchemaUnion] = Field(
      default=None,
      description="""Schema that the generated candidate text must adhere to.
      """,
  )
  routing_config: Optional[GenerationConfigRoutingConfig] = Field(
      default=None,
      description="""Configuration for model router requests.
      """,
  )
  safety_settings: Optional[list[SafetySetting]] = Field(
      default=None,
      description="""Safety settings in the request to block unsafe content in the
      response.
      """,
  )
  tools: Optional[ToolListUnion] = Field(
      default=None,
      description="""Code that enables the system to interact with external systems to
      perform an action outside of the knowledge and scope of the model.
      """,
  )
  tool_config: Optional[ToolConfig] = Field(
      default=None,
      description="""Associates model output to a specific function call.
      """,
  )
  cached_content: Optional[str] = Field(
      default=None,
      description="""Resource name of a context cache that can be used in subsequent
      requests.
      """,
  )
  response_modalities: Optional[list[str]] = Field(
      default=None,
      description="""The requested modalities of the response. Represents the set of
      modalities that the model can return.
      """,
  )
  media_resolution: Optional[MediaResolution] = Field(
      default=None,
      description="""If specified, the media resolution specified will be used.
    """,
  )
  speech_config: Optional[SpeechConfigUnion] = Field(
      default=None,
      description="""The speech generation configuration.
      """,
  )
  automatic_function_calling: Optional[AutomaticFunctionCallingConfig] = Field(
      default=None,
      description="""The configuration for automatic function calling.
      """,
  )


class GenerateContentConfigDict(TypedDict, total=False):
  """Class for configuring optional model parameters.

  For more information, see `Content generation parameters
  <https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/content-generation-parameters>`_.
  """

  system_instruction: Optional[ContentUnionDict]
  """Instructions for the model to steer it toward better performance.
      For example, "Answer as concisely as possible" or "Don't use technical
      terms in your response".
      """

  temperature: Optional[float]
  """Value that controls the degree of randomness in token selection.
      Lower temperatures are good for prompts that require a less open-ended or
      creative response, while higher temperatures can lead to more diverse or
      creative results.
      """

  top_p: Optional[float]
  """Tokens are selected from the most to least probable until the sum
      of their probabilities equals this value. Use a lower value for less
      random responses and a higher value for more random responses.
      """

  top_k: Optional[float]
  """For each token selection step, the ``top_k`` tokens with the
      highest probabilities are sampled. Then tokens are further filtered based
      on ``top_p`` with the final token selected using temperature sampling. Use
      a lower number for less random responses and a higher number for more
      random responses.
      """

  candidate_count: Optional[int]
  """Number of response variations to return.
      """

  max_output_tokens: Optional[int]
  """Maximum number of tokens that can be generated in the response.
      """

  stop_sequences: Optional[list[str]]
  """List of strings that tells the model to stop generating text if one
      of the strings is encountered in the response.
      """

  response_logprobs: Optional[bool]
  """Whether to return the log probabilities of the tokens that were
      chosen by the model at each step.
      """

  logprobs: Optional[int]
  """Number of top candidate tokens to return the log probabilities for
      at each generation step.
      """

  presence_penalty: Optional[float]
  """Positive values penalize tokens that already appear in the
      generated text, increasing the probability of generating more diverse
      content.
      """

  frequency_penalty: Optional[float]
  """Positive values penalize tokens that repeatedly appear in the
      generated text, increasing the probability of generating more diverse
      content.
      """

  seed: Optional[int]
  """When ``seed`` is fixed to a specific number, the model makes a best
      effort to provide the same response for repeated requests. By default, a
      random number is used.
      """

  response_mime_type: Optional[str]
  """Output response media type of the generated candidate text.
      """

  response_schema: Optional[SchemaUnionDict]
  """Schema that the generated candidate text must adhere to.
      """

  routing_config: Optional[GenerationConfigRoutingConfigDict]
  """Configuration for model router requests.
      """

  safety_settings: Optional[list[SafetySettingDict]]
  """Safety settings in the request to block unsafe content in the
      response.
      """

  tools: Optional[ToolListUnionDict]
  """Code that enables the system to interact with external systems to
      perform an action outside of the knowledge and scope of the model.
      """

  tool_config: Optional[ToolConfigDict]
  """Associates model output to a specific function call.
      """

  cached_content: Optional[str]
  """Resource name of a context cache that can be used in subsequent
      requests.
      """

  response_modalities: Optional[list[str]]
  """The requested modalities of the response. Represents the set of
      modalities that the model can return.
      """

  media_resolution: Optional[MediaResolution]
  """If specified, the media resolution specified will be used.
    """

  speech_config: Optional[SpeechConfigUnionDict]
  """The speech generation configuration.
      """

  automatic_function_calling: Optional[AutomaticFunctionCallingConfigDict]
  """The configuration for automatic function calling.
      """


GenerateContentConfigOrDict = Union[
    GenerateContentConfig, GenerateContentConfigDict
]


class _GenerateContentParameters(_common.BaseModel):
  """Class for configuring the content of the request to the model."""

  model: Optional[str] = Field(
      default=None,
      description="""ID of the model to use. For a list of models, see `Google models
    <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models>`_.""",
  )
  contents: Optional[ContentListUnion] = Field(
      default=None,
      description="""Content of the request.
      """,
  )
  config: Optional[GenerateContentConfig] = Field(
      default=None,
      description="""Configuration that contains optional model parameters.
      """,
  )


class _GenerateContentParametersDict(TypedDict, total=False):
  """Class for configuring the content of the request to the model."""

  model: Optional[str]
  """ID of the model to use. For a list of models, see `Google models
    <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models>`_."""

  contents: Optional[ContentListUnionDict]
  """Content of the request.
      """

  config: Optional[GenerateContentConfigDict]
  """Configuration that contains optional model parameters.
      """


_GenerateContentParametersOrDict = Union[
    _GenerateContentParameters, _GenerateContentParametersDict
]


class GoogleTypeDate(_common.BaseModel):
  """Represents a whole or partial calendar date, such as a birthday.

  The time of day and time zone are either specified elsewhere or are
  insignificant. The date is relative to the Gregorian Calendar. This can
  represent one of the following: * A full date, with non-zero year, month, and
  day values. * A month and day, with a zero year (for example, an anniversary).
  * A year on its own, with a zero month and a zero day. * A year and month,
  with a zero day (for example, a credit card expiration date). Related types: *
  google.type.TimeOfDay * google.type.DateTime * google.protobuf.Timestamp
  """

  day: Optional[int] = Field(
      default=None,
      description="""Day of a month. Must be from 1 to 31 and valid for the year and month, or 0 to specify a year by itself or a year and month where the day isn't significant.""",
  )
  month: Optional[int] = Field(
      default=None,
      description="""Month of a year. Must be from 1 to 12, or 0 to specify a year without a month and day.""",
  )
  year: Optional[int] = Field(
      default=None,
      description="""Year of the date. Must be from 1 to 9999, or 0 to specify a date without a year.""",
  )


class GoogleTypeDateDict(TypedDict, total=False):
  """Represents a whole or partial calendar date, such as a birthday.

  The time of day and time zone are either specified elsewhere or are
  insignificant. The date is relative to the Gregorian Calendar. This can
  represent one of the following: * A full date, with non-zero year, month, and
  day values. * A month and day, with a zero year (for example, an anniversary).
  * A year on its own, with a zero month and a zero day. * A year and month,
  with a zero day (for example, a credit card expiration date). Related types: *
  google.type.TimeOfDay * google.type.DateTime * google.protobuf.Timestamp
  """

  day: Optional[int]
  """Day of a month. Must be from 1 to 31 and valid for the year and month, or 0 to specify a year by itself or a year and month where the day isn't significant."""

  month: Optional[int]
  """Month of a year. Must be from 1 to 12, or 0 to specify a year without a month and day."""

  year: Optional[int]
  """Year of the date. Must be from 1 to 9999, or 0 to specify a date without a year."""


GoogleTypeDateOrDict = Union[GoogleTypeDate, GoogleTypeDateDict]


class Citation(_common.BaseModel):
  """Source attributions for content."""

  end_index: Optional[int] = Field(
      default=None, description="""Output only. End index into the content."""
  )
  license: Optional[str] = Field(
      default=None, description="""Output only. License of the attribution."""
  )
  publication_date: Optional[GoogleTypeDate] = Field(
      default=None,
      description="""Output only. Publication date of the attribution.""",
  )
  start_index: Optional[int] = Field(
      default=None, description="""Output only. Start index into the content."""
  )
  title: Optional[str] = Field(
      default=None, description="""Output only. Title of the attribution."""
  )
  uri: Optional[str] = Field(
      default=None,
      description="""Output only. Url reference of the attribution.""",
  )


class CitationDict(TypedDict, total=False):
  """Source attributions for content."""

  end_index: Optional[int]
  """Output only. End index into the content."""

  license: Optional[str]
  """Output only. License of the attribution."""

  publication_date: Optional[GoogleTypeDateDict]
  """Output only. Publication date of the attribution."""

  start_index: Optional[int]
  """Output only. Start index into the content."""

  title: Optional[str]
  """Output only. Title of the attribution."""

  uri: Optional[str]
  """Output only. Url reference of the attribution."""


CitationOrDict = Union[Citation, CitationDict]


class CitationMetadata(_common.BaseModel):
  """Class for citation information when the model quotes another source."""

  citations: Optional[list[Citation]] = Field(
      default=None,
      description="""Contains citation information when the model directly quotes, at
      length, from another source. Can include traditional websites and code
      repositories.
      """,
  )


class CitationMetadataDict(TypedDict, total=False):
  """Class for citation information when the model quotes another source."""

  citations: Optional[list[CitationDict]]
  """Contains citation information when the model directly quotes, at
      length, from another source. Can include traditional websites and code
      repositories.
      """


CitationMetadataOrDict = Union[CitationMetadata, CitationMetadataDict]


class GroundingChunkRetrievedContext(_common.BaseModel):
  """Chunk from context retrieved by the retrieval tools."""

  text: Optional[str] = Field(
      default=None, description="""Text of the attribution."""
  )
  title: Optional[str] = Field(
      default=None, description="""Title of the attribution."""
  )
  uri: Optional[str] = Field(
      default=None, description="""URI reference of the attribution."""
  )


class GroundingChunkRetrievedContextDict(TypedDict, total=False):
  """Chunk from context retrieved by the retrieval tools."""

  text: Optional[str]
  """Text of the attribution."""

  title: Optional[str]
  """Title of the attribution."""

  uri: Optional[str]
  """URI reference of the attribution."""


GroundingChunkRetrievedContextOrDict = Union[
    GroundingChunkRetrievedContext, GroundingChunkRetrievedContextDict
]


class GroundingChunkWeb(_common.BaseModel):
  """Chunk from the web."""

  title: Optional[str] = Field(
      default=None, description="""Title of the chunk."""
  )
  uri: Optional[str] = Field(
      default=None, description="""URI reference of the chunk."""
  )


class GroundingChunkWebDict(TypedDict, total=False):
  """Chunk from the web."""

  title: Optional[str]
  """Title of the chunk."""

  uri: Optional[str]
  """URI reference of the chunk."""


GroundingChunkWebOrDict = Union[GroundingChunkWeb, GroundingChunkWebDict]


class GroundingChunk(_common.BaseModel):
  """Grounding chunk."""

  retrieved_context: Optional[GroundingChunkRetrievedContext] = Field(
      default=None,
      description="""Grounding chunk from context retrieved by the retrieval tools.""",
  )
  web: Optional[GroundingChunkWeb] = Field(
      default=None, description="""Grounding chunk from the web."""
  )


class GroundingChunkDict(TypedDict, total=False):
  """Grounding chunk."""

  retrieved_context: Optional[GroundingChunkRetrievedContextDict]
  """Grounding chunk from context retrieved by the retrieval tools."""

  web: Optional[GroundingChunkWebDict]
  """Grounding chunk from the web."""


GroundingChunkOrDict = Union[GroundingChunk, GroundingChunkDict]


class Segment(_common.BaseModel):
  """Segment of the content."""

  end_index: Optional[int] = Field(
      default=None,
      description="""Output only. End index in the given Part, measured in bytes. Offset from the start of the Part, exclusive, starting at zero.""",
  )
  part_index: Optional[int] = Field(
      default=None,
      description="""Output only. The index of a Part object within its parent Content object.""",
  )
  start_index: Optional[int] = Field(
      default=None,
      description="""Output only. Start index in the given Part, measured in bytes. Offset from the start of the Part, inclusive, starting at zero.""",
  )
  text: Optional[str] = Field(
      default=None,
      description="""Output only. The text corresponding to the segment from the response.""",
  )


class SegmentDict(TypedDict, total=False):
  """Segment of the content."""

  end_index: Optional[int]
  """Output only. End index in the given Part, measured in bytes. Offset from the start of the Part, exclusive, starting at zero."""

  part_index: Optional[int]
  """Output only. The index of a Part object within its parent Content object."""

  start_index: Optional[int]
  """Output only. Start index in the given Part, measured in bytes. Offset from the start of the Part, inclusive, starting at zero."""

  text: Optional[str]
  """Output only. The text corresponding to the segment from the response."""


SegmentOrDict = Union[Segment, SegmentDict]


class GroundingSupport(_common.BaseModel):
  """Grounding support."""

  confidence_scores: Optional[list[float]] = Field(
      default=None,
      description="""Confidence score of the support references. Ranges from 0 to 1. 1 is the most confident. This list must have the same size as the grounding_chunk_indices.""",
  )
  grounding_chunk_indices: Optional[list[int]] = Field(
      default=None,
      description="""A list of indices (into 'grounding_chunk') specifying the citations associated with the claim. For instance [1,3,4] means that grounding_chunk[1], grounding_chunk[3], grounding_chunk[4] are the retrieved content attributed to the claim.""",
  )
  segment: Optional[Segment] = Field(
      default=None,
      description="""Segment of the content this support belongs to.""",
  )


class GroundingSupportDict(TypedDict, total=False):
  """Grounding support."""

  confidence_scores: Optional[list[float]]
  """Confidence score of the support references. Ranges from 0 to 1. 1 is the most confident. This list must have the same size as the grounding_chunk_indices."""

  grounding_chunk_indices: Optional[list[int]]
  """A list of indices (into 'grounding_chunk') specifying the citations associated with the claim. For instance [1,3,4] means that grounding_chunk[1], grounding_chunk[3], grounding_chunk[4] are the retrieved content attributed to the claim."""

  segment: Optional[SegmentDict]
  """Segment of the content this support belongs to."""


GroundingSupportOrDict = Union[GroundingSupport, GroundingSupportDict]


class RetrievalMetadata(_common.BaseModel):
  """Metadata related to retrieval in the grounding flow."""

  google_search_dynamic_retrieval_score: Optional[float] = Field(
      default=None,
      description="""Optional. Score indicating how likely information from Google Search could help answer the prompt. The score is in the range `[0, 1]`, where 0 is the least likely and 1 is the most likely. This score is only populated when Google Search grounding and dynamic retrieval is enabled. It will be compared to the threshold to determine whether to trigger Google Search.""",
  )


class RetrievalMetadataDict(TypedDict, total=False):
  """Metadata related to retrieval in the grounding flow."""

  google_search_dynamic_retrieval_score: Optional[float]
  """Optional. Score indicating how likely information from Google Search could help answer the prompt. The score is in the range `[0, 1]`, where 0 is the least likely and 1 is the most likely. This score is only populated when Google Search grounding and dynamic retrieval is enabled. It will be compared to the threshold to determine whether to trigger Google Search."""


RetrievalMetadataOrDict = Union[RetrievalMetadata, RetrievalMetadataDict]


class SearchEntryPoint(_common.BaseModel):
  """Google search entry point."""

  rendered_content: Optional[str] = Field(
      default=None,
      description="""Optional. Web content snippet that can be embedded in a web page or an app webview.""",
  )
  sdk_blob: Optional[bytes] = Field(
      default=None,
      description="""Optional. Base64 encoded JSON representing array of tuple.""",
  )


class SearchEntryPointDict(TypedDict, total=False):
  """Google search entry point."""

  rendered_content: Optional[str]
  """Optional. Web content snippet that can be embedded in a web page or an app webview."""

  sdk_blob: Optional[bytes]
  """Optional. Base64 encoded JSON representing array of tuple."""


SearchEntryPointOrDict = Union[SearchEntryPoint, SearchEntryPointDict]


class GroundingMetadata(_common.BaseModel):
  """Metadata returned to client when grounding is enabled."""

  grounding_chunks: Optional[list[GroundingChunk]] = Field(
      default=None,
      description="""List of supporting references retrieved from specified grounding source.""",
  )
  grounding_supports: Optional[list[GroundingSupport]] = Field(
      default=None, description="""Optional. List of grounding support."""
  )
  retrieval_metadata: Optional[RetrievalMetadata] = Field(
      default=None, description="""Optional. Output only. Retrieval metadata."""
  )
  retrieval_queries: Optional[list[str]] = Field(
      default=None,
      description="""Optional. Queries executed by the retrieval tools.""",
  )
  search_entry_point: Optional[SearchEntryPoint] = Field(
      default=None,
      description="""Optional. Google search entry for the following-up web searches.""",
  )
  web_search_queries: Optional[list[str]] = Field(
      default=None,
      description="""Optional. Web search queries for the following-up web search.""",
  )


class GroundingMetadataDict(TypedDict, total=False):
  """Metadata returned to client when grounding is enabled."""

  grounding_chunks: Optional[list[GroundingChunkDict]]
  """List of supporting references retrieved from specified grounding source."""

  grounding_supports: Optional[list[GroundingSupportDict]]
  """Optional. List of grounding support."""

  retrieval_metadata: Optional[RetrievalMetadataDict]
  """Optional. Output only. Retrieval metadata."""

  retrieval_queries: Optional[list[str]]
  """Optional. Queries executed by the retrieval tools."""

  search_entry_point: Optional[SearchEntryPointDict]
  """Optional. Google search entry for the following-up web searches."""

  web_search_queries: Optional[list[str]]
  """Optional. Web search queries for the following-up web search."""


GroundingMetadataOrDict = Union[GroundingMetadata, GroundingMetadataDict]


class LogprobsResultCandidate(_common.BaseModel):
  """Candidate for the logprobs token and score."""

  log_probability: Optional[float] = Field(
      default=None, description="""The candidate's log probability."""
  )
  token: Optional[str] = Field(
      default=None, description="""The candidate's token string value."""
  )
  token_id: Optional[int] = Field(
      default=None, description="""The candidate's token id value."""
  )


class LogprobsResultCandidateDict(TypedDict, total=False):
  """Candidate for the logprobs token and score."""

  log_probability: Optional[float]
  """The candidate's log probability."""

  token: Optional[str]
  """The candidate's token string value."""

  token_id: Optional[int]
  """The candidate's token id value."""


LogprobsResultCandidateOrDict = Union[
    LogprobsResultCandidate, LogprobsResultCandidateDict
]


class LogprobsResultTopCandidates(_common.BaseModel):
  """Candidates with top log probabilities at each decoding step."""

  candidates: Optional[list[LogprobsResultCandidate]] = Field(
      default=None,
      description="""Sorted by log probability in descending order.""",
  )


class LogprobsResultTopCandidatesDict(TypedDict, total=False):
  """Candidates with top log probabilities at each decoding step."""

  candidates: Optional[list[LogprobsResultCandidateDict]]
  """Sorted by log probability in descending order."""


LogprobsResultTopCandidatesOrDict = Union[
    LogprobsResultTopCandidates, LogprobsResultTopCandidatesDict
]


class LogprobsResult(_common.BaseModel):
  """Logprobs Result"""

  chosen_candidates: Optional[list[LogprobsResultCandidate]] = Field(
      default=None,
      description="""Length = total number of decoding steps. The chosen candidates may or may not be in top_candidates.""",
  )
  top_candidates: Optional[list[LogprobsResultTopCandidates]] = Field(
      default=None, description="""Length = total number of decoding steps."""
  )


class LogprobsResultDict(TypedDict, total=False):
  """Logprobs Result"""

  chosen_candidates: Optional[list[LogprobsResultCandidateDict]]
  """Length = total number of decoding steps. The chosen candidates may or may not be in top_candidates."""

  top_candidates: Optional[list[LogprobsResultTopCandidatesDict]]
  """Length = total number of decoding steps."""


LogprobsResultOrDict = Union[LogprobsResult, LogprobsResultDict]


class SafetyRating(_common.BaseModel):
  """Safety rating corresponding to the generated content."""

  blocked: Optional[bool] = Field(
      default=None,
      description="""Output only. Indicates whether the content was filtered out because of this rating.""",
  )
  category: Optional[HarmCategory] = Field(
      default=None, description="""Output only. Harm category."""
  )
  probability: Optional[HarmProbability] = Field(
      default=None,
      description="""Output only. Harm probability levels in the content.""",
  )
  probability_score: Optional[float] = Field(
      default=None, description="""Output only. Harm probability score."""
  )
  severity: Optional[HarmSeverity] = Field(
      default=None,
      description="""Output only. Harm severity levels in the content.""",
  )
  severity_score: Optional[float] = Field(
      default=None, description="""Output only. Harm severity score."""
  )


class SafetyRatingDict(TypedDict, total=False):
  """Safety rating corresponding to the generated content."""

  blocked: Optional[bool]
  """Output only. Indicates whether the content was filtered out because of this rating."""

  category: Optional[HarmCategory]
  """Output only. Harm category."""

  probability: Optional[HarmProbability]
  """Output only. Harm probability levels in the content."""

  probability_score: Optional[float]
  """Output only. Harm probability score."""

  severity: Optional[HarmSeverity]
  """Output only. Harm severity levels in the content."""

  severity_score: Optional[float]
  """Output only. Harm severity score."""


SafetyRatingOrDict = Union[SafetyRating, SafetyRatingDict]


class Candidate(_common.BaseModel):
  """Class containing a response candidate generated from the model."""

  content: Optional[Content] = Field(
      default=None,
      description="""Contains the multi-part content of the response.
      """,
  )
  citation_metadata: Optional[CitationMetadata] = Field(
      default=None,
      description="""Source attribution of the generated content.
      """,
  )
  finish_message: Optional[str] = Field(
      default=None,
      description="""Describes the reason the model stopped generating tokens.
      """,
  )
  token_count: Optional[int] = Field(
      default=None,
      description="""Number of tokens for this candidate.
      """,
  )
  avg_logprobs: Optional[float] = Field(
      default=None,
      description="""Output only. Average log probability score of the candidate.""",
  )
  finish_reason: Optional[FinishReason] = Field(
      default=None,
      description="""Output only. The reason why the model stopped generating tokens. If empty, the model has not stopped generating the tokens.""",
  )
  grounding_metadata: Optional[GroundingMetadata] = Field(
      default=None,
      description="""Output only. Metadata specifies sources used to ground generated content.""",
  )
  index: Optional[int] = Field(
      default=None, description="""Output only. Index of the candidate."""
  )
  logprobs_result: Optional[LogprobsResult] = Field(
      default=None,
      description="""Output only. Log-likelihood scores for the response tokens and top tokens""",
  )
  safety_ratings: Optional[list[SafetyRating]] = Field(
      default=None,
      description="""Output only. List of ratings for the safety of a response candidate. There is at most one rating per category.""",
  )


class CandidateDict(TypedDict, total=False):
  """Class containing a response candidate generated from the model."""

  content: Optional[ContentDict]
  """Contains the multi-part content of the response.
      """

  citation_metadata: Optional[CitationMetadataDict]
  """Source attribution of the generated content.
      """

  finish_message: Optional[str]
  """Describes the reason the model stopped generating tokens.
      """

  token_count: Optional[int]
  """Number of tokens for this candidate.
      """

  avg_logprobs: Optional[float]
  """Output only. Average log probability score of the candidate."""

  finish_reason: Optional[FinishReason]
  """Output only. The reason why the model stopped generating tokens. If empty, the model has not stopped generating the tokens."""

  grounding_metadata: Optional[GroundingMetadataDict]
  """Output only. Metadata specifies sources used to ground generated content."""

  index: Optional[int]
  """Output only. Index of the candidate."""

  logprobs_result: Optional[LogprobsResultDict]
  """Output only. Log-likelihood scores for the response tokens and top tokens"""

  safety_ratings: Optional[list[SafetyRatingDict]]
  """Output only. List of ratings for the safety of a response candidate. There is at most one rating per category."""


CandidateOrDict = Union[Candidate, CandidateDict]


class GenerateContentResponsePromptFeedback(_common.BaseModel):
  """Content filter results for a prompt sent in the request."""

  block_reason: Optional[BlockedReason] = Field(
      default=None, description="""Output only. Blocked reason."""
  )
  block_reason_message: Optional[str] = Field(
      default=None,
      description="""Output only. A readable block reason message.""",
  )
  safety_ratings: Optional[list[SafetyRating]] = Field(
      default=None, description="""Output only. Safety ratings."""
  )


class GenerateContentResponsePromptFeedbackDict(TypedDict, total=False):
  """Content filter results for a prompt sent in the request."""

  block_reason: Optional[BlockedReason]
  """Output only. Blocked reason."""

  block_reason_message: Optional[str]
  """Output only. A readable block reason message."""

  safety_ratings: Optional[list[SafetyRatingDict]]
  """Output only. Safety ratings."""


GenerateContentResponsePromptFeedbackOrDict = Union[
    GenerateContentResponsePromptFeedback,
    GenerateContentResponsePromptFeedbackDict,
]


class GenerateContentResponseUsageMetadata(_common.BaseModel):
  """Usage metadata about response(s)."""

  cached_content_token_count: Optional[int] = Field(
      default=None,
      description="""Output only. Number of tokens in the cached part in the input (the cached content).""",
  )
  candidates_token_count: Optional[int] = Field(
      default=None, description="""Number of tokens in the response(s)."""
  )
  prompt_token_count: Optional[int] = Field(
      default=None,
      description="""Number of tokens in the request. When `cached_content` is set, this is still the total effective prompt size meaning this includes the number of tokens in the cached content.""",
  )
  total_token_count: Optional[int] = Field(
      default=None,
      description="""Total token count for prompt and response candidates.""",
  )


class GenerateContentResponseUsageMetadataDict(TypedDict, total=False):
  """Usage metadata about response(s)."""

  cached_content_token_count: Optional[int]
  """Output only. Number of tokens in the cached part in the input (the cached content)."""

  candidates_token_count: Optional[int]
  """Number of tokens in the response(s)."""

  prompt_token_count: Optional[int]
  """Number of tokens in the request. When `cached_content` is set, this is still the total effective prompt size meaning this includes the number of tokens in the cached content."""

  total_token_count: Optional[int]
  """Total token count for prompt and response candidates."""


GenerateContentResponseUsageMetadataOrDict = Union[
    GenerateContentResponseUsageMetadata,
    GenerateContentResponseUsageMetadataDict,
]


class GenerateContentResponse(_common.BaseModel):
  """Response message for PredictionService.GenerateContent."""

  candidates: Optional[list[Candidate]] = Field(
      default=None,
      description="""Response variations returned by the model.
      """,
  )
  model_version: Optional[str] = Field(
      default=None,
      description="""Output only. The model version used to generate the response.""",
  )
  prompt_feedback: Optional[GenerateContentResponsePromptFeedback] = Field(
      default=None,
      description="""Output only. Content filter results for a prompt sent in the request. Note: Sent only in the first stream chunk. Only happens when no candidates were generated due to content violations.""",
  )
  usage_metadata: Optional[GenerateContentResponseUsageMetadata] = Field(
      default=None, description="""Usage metadata about the response(s)."""
  )
  automatic_function_calling_history: Optional[list[Content]] = None
  parsed: Union[pydantic.BaseModel, dict] = None

  @property
  def text(self) -> Optional[str]:
    """Returns the concatenation of all text parts in the response."""
    if (
        not self.candidates
        or not self.candidates[0].content
        or not self.candidates[0].content.parts
    ):
      return None
    if len(self.candidates) > 1:
      logging.warning(
          f"there are {len(self.candidates)} candidates, returning text from"
          " the first candidate.Access response.candidates directly to get"
          " text from other candidates."
      )
    text = ""
    any_text_part_text = False
    for part in self.candidates[0].content.parts:
      for field_name, field_value in part.dict(exclude={"text"}).items():
        if field_value is not None:
          raise ValueError(
              "GenerateContentResponse.text only supports text parts, but got"
              f" {field_name} part{part}"
          )
      if isinstance(part.text, str):
        any_text_part_text = True
        text += part.text
    # part.text == '' is different from part.text is None
    return text if any_text_part_text else None

  @classmethod
  def _from_response(
      cls, response: dict[str, object], kwargs: dict[str, object]
  ):
    result = super()._from_response(response, kwargs)

    # Handles response schema.
    response_schema = _common.get_value_by_path(
        kwargs, ["config", "response_schema"]
    )
    if inspect.isclass(response_schema) and issubclass(
        response_schema, pydantic.BaseModel
    ):
      # Pydantic schema.
      result.parsed = response_schema.model_validate_json(result.text)
    elif isinstance(response_schema, dict) or isinstance(
        response_schema, pydantic.BaseModel
    ):
      # JSON schema.
      result.parsed = json.loads(result.text)

    return result


class GenerateContentResponseDict(TypedDict, total=False):
  """Response message for PredictionService.GenerateContent."""

  candidates: Optional[list[CandidateDict]]
  """Response variations returned by the model.
      """

  model_version: Optional[str]
  """Output only. The model version used to generate the response."""

  prompt_feedback: Optional[GenerateContentResponsePromptFeedbackDict]
  """Output only. Content filter results for a prompt sent in the request. Note: Sent only in the first stream chunk. Only happens when no candidates were generated due to content violations."""

  usage_metadata: Optional[GenerateContentResponseUsageMetadataDict]
  """Usage metadata about the response(s)."""


GenerateContentResponseOrDict = Union[
    GenerateContentResponse, GenerateContentResponseDict
]


class EmbedContentConfig(_common.BaseModel):
  """Class for configuring optional parameters for the embed_content method."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  task_type: Optional[str] = Field(
      default=None,
      description="""Type of task for which the embedding will be used.
      """,
  )
  title: Optional[str] = Field(
      default=None,
      description="""Title for the text. Only applicable when TaskType is
      `RETRIEVAL_DOCUMENT`.
      """,
  )
  output_dimensionality: Optional[int] = Field(
      default=None,
      description="""Reduced dimension for the output embedding. If set,
      excessive values in the output embedding are truncated from the end.
      Supported by newer models since 2024 only. You cannot set this value if
      using the earlier model (`models/embedding-001`).
      """,
  )
  mime_type: Optional[str] = Field(
      default=None,
      description="""Vertex API only. The MIME type of the input.
      """,
  )
  auto_truncate: Optional[bool] = Field(
      default=None,
      description="""Vertex API only. Whether to silently truncate inputs longer than
      the max sequence length. If this option is set to false, oversized inputs
      will lead to an INVALID_ARGUMENT error, similar to other text APIs.
      """,
  )


class EmbedContentConfigDict(TypedDict, total=False):
  """Class for configuring optional parameters for the embed_content method."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  task_type: Optional[str]
  """Type of task for which the embedding will be used.
      """

  title: Optional[str]
  """Title for the text. Only applicable when TaskType is
      `RETRIEVAL_DOCUMENT`.
      """

  output_dimensionality: Optional[int]
  """Reduced dimension for the output embedding. If set,
      excessive values in the output embedding are truncated from the end.
      Supported by newer models since 2024 only. You cannot set this value if
      using the earlier model (`models/embedding-001`).
      """

  mime_type: Optional[str]
  """Vertex API only. The MIME type of the input.
      """

  auto_truncate: Optional[bool]
  """Vertex API only. Whether to silently truncate inputs longer than
      the max sequence length. If this option is set to false, oversized inputs
      will lead to an INVALID_ARGUMENT error, similar to other text APIs.
      """


EmbedContentConfigOrDict = Union[EmbedContentConfig, EmbedContentConfigDict]


class _EmbedContentParameters(_common.BaseModel):
  """Parameters for the embed_content method."""

  model: Optional[str] = Field(
      default=None,
      description="""ID of the model to use. For a list of models, see `Google models
    <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models>`_.""",
  )
  contents: Optional[ContentListUnion] = Field(
      default=None,
      description="""The content to embed. Only the `parts.text` fields will be counted.
      """,
  )
  config: Optional[EmbedContentConfig] = Field(
      default=None,
      description="""Configuration that contains optional parameters.
      """,
  )


class _EmbedContentParametersDict(TypedDict, total=False):
  """Parameters for the embed_content method."""

  model: Optional[str]
  """ID of the model to use. For a list of models, see `Google models
    <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models>`_."""

  contents: Optional[ContentListUnionDict]
  """The content to embed. Only the `parts.text` fields will be counted.
      """

  config: Optional[EmbedContentConfigDict]
  """Configuration that contains optional parameters.
      """


_EmbedContentParametersOrDict = Union[
    _EmbedContentParameters, _EmbedContentParametersDict
]


class ContentEmbeddingStatistics(_common.BaseModel):
  """Statistics of the input text associated with the result of content embedding."""

  truncated: Optional[bool] = Field(
      default=None,
      description="""Vertex API only. If the input text was truncated due to having
      a length longer than the allowed maximum input.
      """,
  )
  token_count: Optional[float] = Field(
      default=None,
      description="""Vertex API only. Number of tokens of the input text.
      """,
  )


class ContentEmbeddingStatisticsDict(TypedDict, total=False):
  """Statistics of the input text associated with the result of content embedding."""

  truncated: Optional[bool]
  """Vertex API only. If the input text was truncated due to having
      a length longer than the allowed maximum input.
      """

  token_count: Optional[float]
  """Vertex API only. Number of tokens of the input text.
      """


ContentEmbeddingStatisticsOrDict = Union[
    ContentEmbeddingStatistics, ContentEmbeddingStatisticsDict
]


class ContentEmbedding(_common.BaseModel):
  """The embedding generated from an input content."""

  values: Optional[list[float]] = Field(
      default=None,
      description="""A list of floats representing an embedding.
      """,
  )
  statistics: Optional[ContentEmbeddingStatistics] = Field(
      default=None,
      description="""Vertex API only. Statistics of the input text associated with this
      embedding.
      """,
  )


class ContentEmbeddingDict(TypedDict, total=False):
  """The embedding generated from an input content."""

  values: Optional[list[float]]
  """A list of floats representing an embedding.
      """

  statistics: Optional[ContentEmbeddingStatisticsDict]
  """Vertex API only. Statistics of the input text associated with this
      embedding.
      """


ContentEmbeddingOrDict = Union[ContentEmbedding, ContentEmbeddingDict]


class EmbedContentMetadata(_common.BaseModel):
  """Request-level metadata for the Vertex Embed Content API."""

  billable_character_count: Optional[int] = Field(
      default=None,
      description="""Vertex API only. The total number of billable characters included
      in the request.
      """,
  )


class EmbedContentMetadataDict(TypedDict, total=False):
  """Request-level metadata for the Vertex Embed Content API."""

  billable_character_count: Optional[int]
  """Vertex API only. The total number of billable characters included
      in the request.
      """


EmbedContentMetadataOrDict = Union[
    EmbedContentMetadata, EmbedContentMetadataDict
]


class EmbedContentResponse(_common.BaseModel):
  """Response for the embed_content method."""

  embeddings: Optional[list[ContentEmbedding]] = Field(
      default=None,
      description="""The embeddings for each request, in the same order as provided in
      the batch request.
      """,
  )
  metadata: Optional[EmbedContentMetadata] = Field(
      default=None,
      description="""Vertex API only. Metadata about the request.
      """,
  )


class EmbedContentResponseDict(TypedDict, total=False):
  """Response for the embed_content method."""

  embeddings: Optional[list[ContentEmbeddingDict]]
  """The embeddings for each request, in the same order as provided in
      the batch request.
      """

  metadata: Optional[EmbedContentMetadataDict]
  """Vertex API only. Metadata about the request.
      """


EmbedContentResponseOrDict = Union[
    EmbedContentResponse, EmbedContentResponseDict
]


class GenerateImageConfig(_common.BaseModel):
  """Class that represents the config for generating an image."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  output_gcs_uri: Optional[str] = Field(
      default=None,
      description="""Cloud Storage URI used to store the generated images.
      """,
  )
  negative_prompt: Optional[str] = Field(
      default=None,
      description="""Description of what to discourage in the generated images.
      """,
  )
  number_of_images: Optional[int] = Field(
      default=None,
      description="""Number of images to generate.
      """,
  )
  guidance_scale: Optional[float] = Field(
      default=None,
      description="""Controls how much the model adheres to the text prompt. Large
      values increase output and prompt alignment, but may compromise image
      quality.
      """,
  )
  seed: Optional[int] = Field(
      default=None,
      description="""Random seed for image generation. This is not available when
      ``add_watermark`` is set to true.
      """,
  )
  safety_filter_level: Optional[SafetyFilterLevel] = Field(
      default=None,
      description="""Filter level for safety filtering.
      """,
  )
  person_generation: Optional[PersonGeneration] = Field(
      default=None,
      description="""Allows generation of people by the model.
      """,
  )
  include_safety_attributes: Optional[bool] = Field(
      default=None,
      description="""Whether to report the safety scores of each image in the response.
      """,
  )
  include_rai_reason: Optional[bool] = Field(
      default=None,
      description="""Whether to include the Responsible AI filter reason if the image
      is filtered out of the response.
      """,
  )
  language: Optional[ImagePromptLanguage] = Field(
      default=None,
      description="""Language of the text in the prompt.
      """,
  )
  output_mime_type: Optional[str] = Field(
      default=None,
      description="""MIME type of the generated image.
      """,
  )
  output_compression_quality: Optional[int] = Field(
      default=None,
      description="""Compression quality of the generated image (for ``image/jpeg``
      only).
      """,
  )
  add_watermark: Optional[bool] = Field(
      default=None,
      description="""Whether to add a watermark to the generated image.
      """,
  )
  aspect_ratio: Optional[str] = Field(
      default=None,
      description="""Aspect ratio of the generated image.
      """,
  )


class GenerateImageConfigDict(TypedDict, total=False):
  """Class that represents the config for generating an image."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  output_gcs_uri: Optional[str]
  """Cloud Storage URI used to store the generated images.
      """

  negative_prompt: Optional[str]
  """Description of what to discourage in the generated images.
      """

  number_of_images: Optional[int]
  """Number of images to generate.
      """

  guidance_scale: Optional[float]
  """Controls how much the model adheres to the text prompt. Large
      values increase output and prompt alignment, but may compromise image
      quality.
      """

  seed: Optional[int]
  """Random seed for image generation. This is not available when
      ``add_watermark`` is set to true.
      """

  safety_filter_level: Optional[SafetyFilterLevel]
  """Filter level for safety filtering.
      """

  person_generation: Optional[PersonGeneration]
  """Allows generation of people by the model.
      """

  include_safety_attributes: Optional[bool]
  """Whether to report the safety scores of each image in the response.
      """

  include_rai_reason: Optional[bool]
  """Whether to include the Responsible AI filter reason if the image
      is filtered out of the response.
      """

  language: Optional[ImagePromptLanguage]
  """Language of the text in the prompt.
      """

  output_mime_type: Optional[str]
  """MIME type of the generated image.
      """

  output_compression_quality: Optional[int]
  """Compression quality of the generated image (for ``image/jpeg``
      only).
      """

  add_watermark: Optional[bool]
  """Whether to add a watermark to the generated image.
      """

  aspect_ratio: Optional[str]
  """Aspect ratio of the generated image.
      """


GenerateImageConfigOrDict = Union[GenerateImageConfig, GenerateImageConfigDict]


class _GenerateImageParameters(_common.BaseModel):
  """Class that represents the parameters for generating an image."""

  model: Optional[str] = Field(
      default=None,
      description="""ID of the model to use. For a list of models, see `Google models
    <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models>`_.""",
  )
  prompt: Optional[str] = Field(
      default=None,
      description="""Text prompt that typically describes the image to output.
      """,
  )
  config: Optional[GenerateImageConfig] = Field(
      default=None,
      description="""Configuration for generating an image.
      """,
  )


class _GenerateImageParametersDict(TypedDict, total=False):
  """Class that represents the parameters for generating an image."""

  model: Optional[str]
  """ID of the model to use. For a list of models, see `Google models
    <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models>`_."""

  prompt: Optional[str]
  """Text prompt that typically describes the image to output.
      """

  config: Optional[GenerateImageConfigDict]
  """Configuration for generating an image.
      """


_GenerateImageParametersOrDict = Union[
    _GenerateImageParameters, _GenerateImageParametersDict
]


class Image(_common.BaseModel):
  """Class that represents an image."""

  gcs_uri: Optional[str] = Field(
      default=None,
      description="""The Cloud Storage URI of the image. ``Image`` can contain a value
      for this field or the ``image_bytes`` field but not both.
      """,
  )
  image_bytes: Optional[bytes] = Field(
      default=None,
      description="""The image bytes data. ``Image`` can contain a value for this field
      or the ``gcs_uri`` field but not both.
      """,
  )

  _loaded_image = None

  """Image."""

  @staticmethod
  def from_file(location: str) -> "Image":
    """Lazy-loads an image from a local file or Google Cloud Storage.

    Args:
        location: The local path or Google Cloud Storage URI from which to load
          the image.

    Returns:
        A loaded image as an `Image` object.
    """
    import urllib
    import pathlib

    parsed_url = urllib.parse.urlparse(location)
    if (
        parsed_url.scheme == "https"
        and parsed_url.netloc == "storage.googleapis.com"
    ):
      parsed_url = parsed_url._replace(
          scheme="gs",
          netloc="",
          path=f"/{urllib.parse.unquote(parsed_url.path)}",
      )
      location = urllib.parse.urlunparse(parsed_url)

    if parsed_url.scheme == "gs":
      return Image(gcs_uri=location)

    # Load image from local path
    image_bytes = pathlib.Path(location).read_bytes()
    image = Image(image_bytes=image_bytes)
    return image

  def show(self):
    """Shows the image.

    This method only works in a notebook environment.
    """
    try:
      from IPython import display as IPython_display
    except ImportError:
      IPython_display = None

    try:
      from PIL import Image as PIL_Image
    except ImportError:
      PIL_Image = None
    if PIL_Image and IPython_display:
      IPython_display.display(self._pil_image)

  @property
  def _pil_image(self) -> "PIL_Image.Image":
    try:
      from PIL import Image as PIL_Image
    except ImportError:
      PIL_Image = None
    import io

    if self._loaded_image is None:
      if not PIL_Image:
        raise RuntimeError(
            "The PIL module is not available. Please install the Pillow"
            " package."
        )
      self._loaded_image = PIL_Image.open(io.BytesIO(self.image_bytes))
    return self._loaded_image

  def save(self, location: str):
    """Saves the image to a file.

    Args:
        location: Local path where to save the image.
    """
    import pathlib

    pathlib.Path(location).write_bytes(self.image_bytes)


Modality = Literal["MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "AUDIO"]

JOB_STATES_SUCCEEDED_VERTEX = [
    "JOB_STATE_SUCCEEDED",
]

JOB_STATES_SUCCEEDED_MLDEV = [
    "ACTIVE",
]

JOB_STATES_SUCCEEDED = JOB_STATES_SUCCEEDED_VERTEX + JOB_STATES_SUCCEEDED_MLDEV


JOB_STATES_ENDED_VERTEX = [
    "JOB_STATE_SUCCEEDED",
    "JOB_STATE_FAILED",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_EXPIRED",
]

JOB_STATES_ENDED_MLDEV = [
    "ACTIVE",
    "FAILED",
]

JOB_STATES_ENDED = JOB_STATES_ENDED_VERTEX + JOB_STATES_ENDED_MLDEV


class ImageDict(TypedDict, total=False):
  """Class that represents an image."""

  gcs_uri: Optional[str]
  """The Cloud Storage URI of the image. ``Image`` can contain a value
      for this field or the ``image_bytes`` field but not both.
      """

  image_bytes: Optional[bytes]
  """The image bytes data. ``Image`` can contain a value for this field
      or the ``gcs_uri`` field but not both.
      """


ImageOrDict = Union[Image, ImageDict]


class GeneratedImage(_common.BaseModel):
  """Class that represents an output image."""

  image: Optional[Image] = Field(
      default=None,
      description="""The output image data.
      """,
  )
  rai_filtered_reason: Optional[str] = Field(
      default=None,
      description="""Responsible AI filter reason if the image is filtered out of the
      response.
      """,
  )


class GeneratedImageDict(TypedDict, total=False):
  """Class that represents an output image."""

  image: Optional[ImageDict]
  """The output image data.
      """

  rai_filtered_reason: Optional[str]
  """Responsible AI filter reason if the image is filtered out of the
      response.
      """


GeneratedImageOrDict = Union[GeneratedImage, GeneratedImageDict]


class GenerateImageResponse(_common.BaseModel):
  """Class that represents the output image response."""

  generated_images: Optional[list[GeneratedImage]] = Field(
      default=None,
      description="""List of generated images.
      """,
  )


class GenerateImageResponseDict(TypedDict, total=False):
  """Class that represents the output image response."""

  generated_images: Optional[list[GeneratedImageDict]]
  """List of generated images.
      """


GenerateImageResponseOrDict = Union[
    GenerateImageResponse, GenerateImageResponseDict
]


class MaskReferenceConfig(_common.BaseModel):
  """Configuration for a Mask reference image."""

  mask_mode: Optional[MaskReferenceMode] = Field(
      default=None,
      description="""Prompts the model to generate a mask instead of you needing to
      provide one (unless MASK_MODE_USER_PROVIDED is used).""",
  )
  segmentation_classes: Optional[list[int]] = Field(
      default=None,
      description="""A list of up to 5 class ids to use for semantic segmentation.
      Automatically creates an image mask based on specific objects.""",
  )
  mask_dilation: Optional[float] = Field(
      default=None,
      description="""Dilation percentage of the mask provided.
      Float between 0 and 1.""",
  )


class MaskReferenceConfigDict(TypedDict, total=False):
  """Configuration for a Mask reference image."""

  mask_mode: Optional[MaskReferenceMode]
  """Prompts the model to generate a mask instead of you needing to
      provide one (unless MASK_MODE_USER_PROVIDED is used)."""

  segmentation_classes: Optional[list[int]]
  """A list of up to 5 class ids to use for semantic segmentation.
      Automatically creates an image mask based on specific objects."""

  mask_dilation: Optional[float]
  """Dilation percentage of the mask provided.
      Float between 0 and 1."""


MaskReferenceConfigOrDict = Union[MaskReferenceConfig, MaskReferenceConfigDict]


class ControlReferenceConfig(_common.BaseModel):
  """Configuration for a Control reference image."""

  control_type: Optional[ControlReferenceType] = Field(
      default=None,
      description="""The type of control reference image to use.""",
  )
  enable_control_image_computation: Optional[bool] = Field(
      default=None,
      description="""Defaults to False. When set to True, the control image will be
      computed by the model based on the control type. When set to False,
      the control image must be provided by the user.""",
  )


class ControlReferenceConfigDict(TypedDict, total=False):
  """Configuration for a Control reference image."""

  control_type: Optional[ControlReferenceType]
  """The type of control reference image to use."""

  enable_control_image_computation: Optional[bool]
  """Defaults to False. When set to True, the control image will be
      computed by the model based on the control type. When set to False,
      the control image must be provided by the user."""


ControlReferenceConfigOrDict = Union[
    ControlReferenceConfig, ControlReferenceConfigDict
]


class StyleReferenceConfig(_common.BaseModel):
  """Configuration for a Style reference image."""

  style_description: Optional[str] = Field(
      default=None,
      description="""A text description of the style to use for the generated image.""",
  )


class StyleReferenceConfigDict(TypedDict, total=False):
  """Configuration for a Style reference image."""

  style_description: Optional[str]
  """A text description of the style to use for the generated image."""


StyleReferenceConfigOrDict = Union[
    StyleReferenceConfig, StyleReferenceConfigDict
]


class SubjectReferenceConfig(_common.BaseModel):
  """Configuration for a Subject reference image."""

  subject_type: Optional[SubjectReferenceType] = Field(
      default=None,
      description="""The subject type of a subject reference image.""",
  )
  subject_description: Optional[str] = Field(
      default=None, description="""Subject description for the image."""
  )


class SubjectReferenceConfigDict(TypedDict, total=False):
  """Configuration for a Subject reference image."""

  subject_type: Optional[SubjectReferenceType]
  """The subject type of a subject reference image."""

  subject_description: Optional[str]
  """Subject description for the image."""


SubjectReferenceConfigOrDict = Union[
    SubjectReferenceConfig, SubjectReferenceConfigDict
]


class _ReferenceImageAPI(_common.BaseModel):
  """Private class that represents a Reference image that is sent to API."""

  reference_image: Optional[Image] = Field(
      default=None,
      description="""The reference image for the editing operation.""",
  )
  reference_id: Optional[int] = Field(
      default=None, description="""The id of the reference image."""
  )
  reference_type: Optional[str] = Field(
      default=None, description="""The type of the reference image."""
  )
  mask_image_config: Optional[MaskReferenceConfig] = Field(
      default=None,
      description="""Configuration for the mask reference image.""",
  )
  control_image_config: Optional[ControlReferenceConfig] = Field(
      default=None,
      description="""Configuration for the control reference image.""",
  )
  style_image_config: Optional[StyleReferenceConfig] = Field(
      default=None,
      description="""Configuration for the style reference image.""",
  )
  subject_image_config: Optional[SubjectReferenceConfig] = Field(
      default=None,
      description="""Configuration for the subject reference image.""",
  )


class _ReferenceImageAPIDict(TypedDict, total=False):
  """Private class that represents a Reference image that is sent to API."""

  reference_image: Optional[ImageDict]
  """The reference image for the editing operation."""

  reference_id: Optional[int]
  """The id of the reference image."""

  reference_type: Optional[str]
  """The type of the reference image."""

  mask_image_config: Optional[MaskReferenceConfigDict]
  """Configuration for the mask reference image."""

  control_image_config: Optional[ControlReferenceConfigDict]
  """Configuration for the control reference image."""

  style_image_config: Optional[StyleReferenceConfigDict]
  """Configuration for the style reference image."""

  subject_image_config: Optional[SubjectReferenceConfigDict]
  """Configuration for the subject reference image."""


_ReferenceImageAPIOrDict = Union[_ReferenceImageAPI, _ReferenceImageAPIDict]


class EditImageConfig(_common.BaseModel):
  """Configuration for editing an image."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  output_gcs_uri: Optional[str] = Field(
      default=None,
      description="""Cloud Storage URI used to store the generated images.
      """,
  )
  negative_prompt: Optional[str] = Field(
      default=None,
      description="""Description of what to discourage in the generated images.
      """,
  )
  number_of_images: Optional[int] = Field(
      default=None,
      description="""Number of images to generate.
      """,
  )
  guidance_scale: Optional[float] = Field(
      default=None,
      description="""Controls how much the model adheres to the text prompt. Large
      values increase output and prompt alignment, but may compromise image
      quality.
      """,
  )
  seed: Optional[int] = Field(
      default=None,
      description="""Random seed for image generation. This is not available when
      ``add_watermark`` is set to true.
      """,
  )
  safety_filter_level: Optional[SafetyFilterLevel] = Field(
      default=None,
      description="""Filter level for safety filtering.
      """,
  )
  person_generation: Optional[PersonGeneration] = Field(
      default=None,
      description="""Allows generation of people by the model.
      """,
  )
  include_safety_attributes: Optional[bool] = Field(
      default=None,
      description="""Whether to report the safety scores of each image in the response.
      """,
  )
  include_rai_reason: Optional[bool] = Field(
      default=None,
      description="""Whether to include the Responsible AI filter reason if the image
      is filtered out of the response.
      """,
  )
  language: Optional[ImagePromptLanguage] = Field(
      default=None,
      description="""Language of the text in the prompt.
      """,
  )
  output_mime_type: Optional[str] = Field(
      default=None,
      description="""MIME type of the generated image.
      """,
  )
  output_compression_quality: Optional[int] = Field(
      default=None,
      description="""Compression quality of the generated image (for ``image/jpeg``
      only).
      """,
  )
  edit_mode: Optional[EditMode] = Field(
      default=None,
      description="""Describes the editing mode for the request.""",
  )


class EditImageConfigDict(TypedDict, total=False):
  """Configuration for editing an image."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  output_gcs_uri: Optional[str]
  """Cloud Storage URI used to store the generated images.
      """

  negative_prompt: Optional[str]
  """Description of what to discourage in the generated images.
      """

  number_of_images: Optional[int]
  """Number of images to generate.
      """

  guidance_scale: Optional[float]
  """Controls how much the model adheres to the text prompt. Large
      values increase output and prompt alignment, but may compromise image
      quality.
      """

  seed: Optional[int]
  """Random seed for image generation. This is not available when
      ``add_watermark`` is set to true.
      """

  safety_filter_level: Optional[SafetyFilterLevel]
  """Filter level for safety filtering.
      """

  person_generation: Optional[PersonGeneration]
  """Allows generation of people by the model.
      """

  include_safety_attributes: Optional[bool]
  """Whether to report the safety scores of each image in the response.
      """

  include_rai_reason: Optional[bool]
  """Whether to include the Responsible AI filter reason if the image
      is filtered out of the response.
      """

  language: Optional[ImagePromptLanguage]
  """Language of the text in the prompt.
      """

  output_mime_type: Optional[str]
  """MIME type of the generated image.
      """

  output_compression_quality: Optional[int]
  """Compression quality of the generated image (for ``image/jpeg``
      only).
      """

  edit_mode: Optional[EditMode]
  """Describes the editing mode for the request."""


EditImageConfigOrDict = Union[EditImageConfig, EditImageConfigDict]


class _EditImageParameters(_common.BaseModel):
  """Parameters for the request to edit an image."""

  model: Optional[str] = Field(
      default=None, description="""The model to use."""
  )
  prompt: Optional[str] = Field(
      default=None,
      description="""A text description of the edit to apply to the image.""",
  )
  reference_images: Optional[list[_ReferenceImageAPI]] = Field(
      default=None, description="""The reference images for Imagen 3 editing."""
  )
  config: Optional[EditImageConfig] = Field(
      default=None, description="""Configuration for editing."""
  )


class _EditImageParametersDict(TypedDict, total=False):
  """Parameters for the request to edit an image."""

  model: Optional[str]
  """The model to use."""

  prompt: Optional[str]
  """A text description of the edit to apply to the image."""

  reference_images: Optional[list[_ReferenceImageAPIDict]]
  """The reference images for Imagen 3 editing."""

  config: Optional[EditImageConfigDict]
  """Configuration for editing."""


_EditImageParametersOrDict = Union[
    _EditImageParameters, _EditImageParametersDict
]


class EditImageResponse(_common.BaseModel):
  """Response for the request to edit an image."""

  generated_images: Optional[list[GeneratedImage]] = Field(
      default=None, description="""Generated images."""
  )


class EditImageResponseDict(TypedDict, total=False):
  """Response for the request to edit an image."""

  generated_images: Optional[list[GeneratedImageDict]]
  """Generated images."""


EditImageResponseOrDict = Union[EditImageResponse, EditImageResponseDict]


class _UpscaleImageAPIConfig(_common.BaseModel):
  """API config for UpscaleImage with fields not exposed to users.

  These fields require default values sent to the API which are not intended
  to be modifiable or exposed to users in the SDK method.
  """

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  upscale_factor: Optional[str] = Field(
      default=None,
      description="""The factor to which the image will be upscaled.""",
  )
  include_rai_reason: Optional[bool] = Field(
      default=None,
      description="""Whether to include a reason for filtered-out images in the
      response.""",
  )
  output_mime_type: Optional[str] = Field(
      default=None,
      description="""The image format that the output should be saved as.""",
  )
  output_compression_quality: Optional[int] = Field(
      default=None,
      description="""The level of compression if the ``output_mime_type`` is
      ``image/jpeg``.""",
  )
  number_of_images: Optional[int] = Field(default=None, description="""""")
  mode: Optional[str] = Field(default=None, description="""""")


class _UpscaleImageAPIConfigDict(TypedDict, total=False):
  """API config for UpscaleImage with fields not exposed to users.

  These fields require default values sent to the API which are not intended
  to be modifiable or exposed to users in the SDK method.
  """

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  upscale_factor: Optional[str]
  """The factor to which the image will be upscaled."""

  include_rai_reason: Optional[bool]
  """Whether to include a reason for filtered-out images in the
      response."""

  output_mime_type: Optional[str]
  """The image format that the output should be saved as."""

  output_compression_quality: Optional[int]
  """The level of compression if the ``output_mime_type`` is
      ``image/jpeg``."""

  number_of_images: Optional[int]
  """"""

  mode: Optional[str]
  """"""


_UpscaleImageAPIConfigOrDict = Union[
    _UpscaleImageAPIConfig, _UpscaleImageAPIConfigDict
]


class _UpscaleImageAPIParameters(_common.BaseModel):
  """API parameters for UpscaleImage."""

  model: Optional[str] = Field(
      default=None, description="""The model to use."""
  )
  image: Optional[Image] = Field(
      default=None, description="""The input image to upscale."""
  )
  config: Optional[_UpscaleImageAPIConfig] = Field(
      default=None, description="""Configuration for upscaling."""
  )


class _UpscaleImageAPIParametersDict(TypedDict, total=False):
  """API parameters for UpscaleImage."""

  model: Optional[str]
  """The model to use."""

  image: Optional[ImageDict]
  """The input image to upscale."""

  config: Optional[_UpscaleImageAPIConfigDict]
  """Configuration for upscaling."""


_UpscaleImageAPIParametersOrDict = Union[
    _UpscaleImageAPIParameters, _UpscaleImageAPIParametersDict
]


class UpscaleImageResponse(_common.BaseModel):

  generated_images: Optional[list[GeneratedImage]] = Field(
      default=None, description="""Generated images."""
  )


class UpscaleImageResponseDict(TypedDict, total=False):

  generated_images: Optional[list[GeneratedImageDict]]
  """Generated images."""


UpscaleImageResponseOrDict = Union[
    UpscaleImageResponse, UpscaleImageResponseDict
]


class _GetModelParameters(_common.BaseModel):

  model: Optional[str] = Field(default=None, description="""""")


class _GetModelParametersDict(TypedDict, total=False):

  model: Optional[str]
  """"""


_GetModelParametersOrDict = Union[_GetModelParameters, _GetModelParametersDict]


class Endpoint(_common.BaseModel):
  """An endpoint where you deploy models."""

  name: Optional[str] = Field(
      default=None, description="""Resource name of the endpoint."""
  )
  deployed_model_id: Optional[str] = Field(
      default=None,
      description="""ID of the model that's deployed to the endpoint.""",
  )


class EndpointDict(TypedDict, total=False):
  """An endpoint where you deploy models."""

  name: Optional[str]
  """Resource name of the endpoint."""

  deployed_model_id: Optional[str]
  """ID of the model that's deployed to the endpoint."""


EndpointOrDict = Union[Endpoint, EndpointDict]


class TunedModelInfo(_common.BaseModel):
  """A tuned machine learning model."""

  base_model: Optional[str] = Field(
      default=None,
      description="""ID of the base model that you want to tune.""",
  )
  create_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Date and time when the base model was created.""",
  )
  update_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Date and time when the base model was last updated.""",
  )


class TunedModelInfoDict(TypedDict, total=False):
  """A tuned machine learning model."""

  base_model: Optional[str]
  """ID of the base model that you want to tune."""

  create_time: Optional[datetime.datetime]
  """Date and time when the base model was created."""

  update_time: Optional[datetime.datetime]
  """Date and time when the base model was last updated."""


TunedModelInfoOrDict = Union[TunedModelInfo, TunedModelInfoDict]


class Model(_common.BaseModel):
  """A trained machine learning model."""

  name: Optional[str] = Field(
      default=None, description="""Resource name of the model."""
  )
  display_name: Optional[str] = Field(
      default=None, description="""Display name of the model."""
  )
  description: Optional[str] = Field(
      default=None, description="""Description of the model."""
  )
  version: Optional[str] = Field(
      default=None,
      description="""Version ID of the model. A new version is committed when a new
      model version is uploaded or trained under an existing model ID. The
      version ID is an auto-incrementing decimal number in string
      representation.""",
  )
  endpoints: Optional[list[Endpoint]] = Field(
      default=None,
      description="""List of deployed models created from this base model. Note that a
      model could have been deployed to endpoints in different locations.""",
  )
  labels: Optional[dict[str, str]] = Field(
      default=None,
      description="""Labels with user-defined metadata to organize your models.""",
  )
  tuned_model_info: Optional[TunedModelInfo] = Field(
      default=None,
      description="""Information about the tuned model from the base model.""",
  )
  input_token_limit: Optional[int] = Field(
      default=None,
      description="""The maximum number of input tokens that the model can handle.""",
  )
  output_token_limit: Optional[int] = Field(
      default=None,
      description="""The maximum number of output tokens that the model can generate.""",
  )
  supported_actions: Optional[list[str]] = Field(
      default=None,
      description="""List of actions that are supported by the model.""",
  )


class ModelDict(TypedDict, total=False):
  """A trained machine learning model."""

  name: Optional[str]
  """Resource name of the model."""

  display_name: Optional[str]
  """Display name of the model."""

  description: Optional[str]
  """Description of the model."""

  version: Optional[str]
  """Version ID of the model. A new version is committed when a new
      model version is uploaded or trained under an existing model ID. The
      version ID is an auto-incrementing decimal number in string
      representation."""

  endpoints: Optional[list[EndpointDict]]
  """List of deployed models created from this base model. Note that a
      model could have been deployed to endpoints in different locations."""

  labels: Optional[dict[str, str]]
  """Labels with user-defined metadata to organize your models."""

  tuned_model_info: Optional[TunedModelInfoDict]
  """Information about the tuned model from the base model."""

  input_token_limit: Optional[int]
  """The maximum number of input tokens that the model can handle."""

  output_token_limit: Optional[int]
  """The maximum number of output tokens that the model can generate."""

  supported_actions: Optional[list[str]]
  """List of actions that are supported by the model."""


ModelOrDict = Union[Model, ModelDict]


class ListModelsConfig(_common.BaseModel):

  page_size: Optional[int] = Field(default=None, description="""""")
  page_token: Optional[str] = Field(default=None, description="""""")
  filter: Optional[str] = Field(default=None, description="""""")


class ListModelsConfigDict(TypedDict, total=False):

  page_size: Optional[int]
  """"""

  page_token: Optional[str]
  """"""

  filter: Optional[str]
  """"""


ListModelsConfigOrDict = Union[ListModelsConfig, ListModelsConfigDict]


class _ListModelsParameters(_common.BaseModel):

  config: Optional[ListModelsConfig] = Field(default=None, description="""""")


class _ListModelsParametersDict(TypedDict, total=False):

  config: Optional[ListModelsConfigDict]
  """"""


_ListModelsParametersOrDict = Union[
    _ListModelsParameters, _ListModelsParametersDict
]


class ListModelsResponse(_common.BaseModel):

  next_page_token: Optional[str] = Field(default=None, description="""""")
  models: Optional[list[Model]] = Field(default=None, description="""""")


class ListModelsResponseDict(TypedDict, total=False):

  next_page_token: Optional[str]
  """"""

  models: Optional[list[ModelDict]]
  """"""


ListModelsResponseOrDict = Union[ListModelsResponse, ListModelsResponseDict]


class UpdateModelConfig(_common.BaseModel):

  display_name: Optional[str] = Field(default=None, description="""""")
  description: Optional[str] = Field(default=None, description="""""")


class UpdateModelConfigDict(TypedDict, total=False):

  display_name: Optional[str]
  """"""

  description: Optional[str]
  """"""


UpdateModelConfigOrDict = Union[UpdateModelConfig, UpdateModelConfigDict]


class _UpdateModelParameters(_common.BaseModel):

  model: Optional[str] = Field(default=None, description="""""")
  config: Optional[UpdateModelConfig] = Field(default=None, description="""""")


class _UpdateModelParametersDict(TypedDict, total=False):

  model: Optional[str]
  """"""

  config: Optional[UpdateModelConfigDict]
  """"""


_UpdateModelParametersOrDict = Union[
    _UpdateModelParameters, _UpdateModelParametersDict
]


class _DeleteModelParameters(_common.BaseModel):

  model: Optional[str] = Field(default=None, description="""""")


class _DeleteModelParametersDict(TypedDict, total=False):

  model: Optional[str]
  """"""


_DeleteModelParametersOrDict = Union[
    _DeleteModelParameters, _DeleteModelParametersDict
]


class DeleteModelResponse(_common.BaseModel):

  pass


class DeleteModelResponseDict(TypedDict, total=False):

  pass


DeleteModelResponseOrDict = Union[DeleteModelResponse, DeleteModelResponseDict]


class GenerationConfig(_common.BaseModel):
  """Generation config."""

  audio_timestamp: Optional[bool] = Field(
      default=None,
      description="""Optional. If enabled, audio timestamp will be included in the request to the model.""",
  )
  candidate_count: Optional[int] = Field(
      default=None,
      description="""Optional. Number of candidates to generate.""",
  )
  frequency_penalty: Optional[float] = Field(
      default=None, description="""Optional. Frequency penalties."""
  )
  logprobs: Optional[int] = Field(
      default=None, description="""Optional. Logit probabilities."""
  )
  max_output_tokens: Optional[int] = Field(
      default=None,
      description="""Optional. The maximum number of output tokens to generate per message.""",
  )
  presence_penalty: Optional[float] = Field(
      default=None, description="""Optional. Positive penalties."""
  )
  response_logprobs: Optional[bool] = Field(
      default=None,
      description="""Optional. If true, export the logprobs results in response.""",
  )
  response_mime_type: Optional[str] = Field(
      default=None,
      description="""Optional. Output response mimetype of the generated candidate text. Supported mimetype: - `text/plain`: (default) Text output. - `application/json`: JSON response in the candidates. The model needs to be prompted to output the appropriate response type, otherwise the behavior is undefined. This is a preview feature.""",
  )
  response_schema: Optional[Schema] = Field(
      default=None,
      description="""Optional. The `Schema` object allows the definition of input and output data types. These types can be objects, but also primitives and arrays. Represents a select subset of an [OpenAPI 3.0 schema object](https://spec.openapis.org/oas/v3.0.3#schema). If set, a compatible response_mime_type must also be set. Compatible mimetypes: `application/json`: Schema for JSON response.""",
  )
  routing_config: Optional[GenerationConfigRoutingConfig] = Field(
      default=None, description="""Optional. Routing configuration."""
  )
  seed: Optional[int] = Field(default=None, description="""Optional. Seed.""")
  stop_sequences: Optional[list[str]] = Field(
      default=None, description="""Optional. Stop sequences."""
  )
  temperature: Optional[float] = Field(
      default=None,
      description="""Optional. Controls the randomness of predictions.""",
  )
  top_k: Optional[float] = Field(
      default=None,
      description="""Optional. If specified, top-k sampling will be used.""",
  )
  top_p: Optional[float] = Field(
      default=None,
      description="""Optional. If specified, nucleus sampling will be used.""",
  )


class GenerationConfigDict(TypedDict, total=False):
  """Generation config."""

  audio_timestamp: Optional[bool]
  """Optional. If enabled, audio timestamp will be included in the request to the model."""

  candidate_count: Optional[int]
  """Optional. Number of candidates to generate."""

  frequency_penalty: Optional[float]
  """Optional. Frequency penalties."""

  logprobs: Optional[int]
  """Optional. Logit probabilities."""

  max_output_tokens: Optional[int]
  """Optional. The maximum number of output tokens to generate per message."""

  presence_penalty: Optional[float]
  """Optional. Positive penalties."""

  response_logprobs: Optional[bool]
  """Optional. If true, export the logprobs results in response."""

  response_mime_type: Optional[str]
  """Optional. Output response mimetype of the generated candidate text. Supported mimetype: - `text/plain`: (default) Text output. - `application/json`: JSON response in the candidates. The model needs to be prompted to output the appropriate response type, otherwise the behavior is undefined. This is a preview feature."""

  response_schema: Optional[SchemaDict]
  """Optional. The `Schema` object allows the definition of input and output data types. These types can be objects, but also primitives and arrays. Represents a select subset of an [OpenAPI 3.0 schema object](https://spec.openapis.org/oas/v3.0.3#schema). If set, a compatible response_mime_type must also be set. Compatible mimetypes: `application/json`: Schema for JSON response."""

  routing_config: Optional[GenerationConfigRoutingConfigDict]
  """Optional. Routing configuration."""

  seed: Optional[int]
  """Optional. Seed."""

  stop_sequences: Optional[list[str]]
  """Optional. Stop sequences."""

  temperature: Optional[float]
  """Optional. Controls the randomness of predictions."""

  top_k: Optional[float]
  """Optional. If specified, top-k sampling will be used."""

  top_p: Optional[float]
  """Optional. If specified, nucleus sampling will be used."""


GenerationConfigOrDict = Union[GenerationConfig, GenerationConfigDict]


class CountTokensConfig(_common.BaseModel):
  """Config for the count_tokens method."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  system_instruction: Optional[ContentUnion] = Field(
      default=None,
      description="""Instructions for the model to steer it toward better performance.
      """,
  )
  tools: Optional[list[Tool]] = Field(
      default=None,
      description="""Code that enables the system to interact with external systems to
      perform an action outside of the knowledge and scope of the model.
      """,
  )
  generation_config: Optional[GenerationConfig] = Field(
      default=None,
      description="""Configuration that the model uses to generate the response. Not
      supported by the Gemini Developer API.
      """,
  )


class CountTokensConfigDict(TypedDict, total=False):
  """Config for the count_tokens method."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  system_instruction: Optional[ContentUnionDict]
  """Instructions for the model to steer it toward better performance.
      """

  tools: Optional[list[ToolDict]]
  """Code that enables the system to interact with external systems to
      perform an action outside of the knowledge and scope of the model.
      """

  generation_config: Optional[GenerationConfigDict]
  """Configuration that the model uses to generate the response. Not
      supported by the Gemini Developer API.
      """


CountTokensConfigOrDict = Union[CountTokensConfig, CountTokensConfigDict]


class _CountTokensParameters(_common.BaseModel):
  """Parameters for counting tokens."""

  model: Optional[str] = Field(
      default=None,
      description="""ID of the model to use. For a list of models, see `Google models
    <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models>`_.""",
  )
  contents: Optional[ContentListUnion] = Field(
      default=None, description="""Input content."""
  )
  config: Optional[CountTokensConfig] = Field(
      default=None, description="""Configuration for counting tokens."""
  )


class _CountTokensParametersDict(TypedDict, total=False):
  """Parameters for counting tokens."""

  model: Optional[str]
  """ID of the model to use. For a list of models, see `Google models
    <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models>`_."""

  contents: Optional[ContentListUnionDict]
  """Input content."""

  config: Optional[CountTokensConfigDict]
  """Configuration for counting tokens."""


_CountTokensParametersOrDict = Union[
    _CountTokensParameters, _CountTokensParametersDict
]


class CountTokensResponse(_common.BaseModel):
  """Response for counting tokens."""

  total_tokens: Optional[int] = Field(
      default=None, description="""Total number of tokens."""
  )
  cached_content_token_count: Optional[int] = Field(
      default=None,
      description="""Number of tokens in the cached part of the prompt (the cached content).""",
  )


class CountTokensResponseDict(TypedDict, total=False):
  """Response for counting tokens."""

  total_tokens: Optional[int]
  """Total number of tokens."""

  cached_content_token_count: Optional[int]
  """Number of tokens in the cached part of the prompt (the cached content)."""


CountTokensResponseOrDict = Union[CountTokensResponse, CountTokensResponseDict]


class ComputeTokensConfig(_common.BaseModel):
  """Optional parameters for computing tokens."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )


class ComputeTokensConfigDict(TypedDict, total=False):
  """Optional parameters for computing tokens."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""


ComputeTokensConfigOrDict = Union[ComputeTokensConfig, ComputeTokensConfigDict]


class _ComputeTokensParameters(_common.BaseModel):
  """Parameters for computing tokens."""

  model: Optional[str] = Field(
      default=None,
      description="""ID of the model to use. For a list of models, see `Google models
    <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models>`_.""",
  )
  contents: Optional[ContentListUnion] = Field(
      default=None, description="""Input content."""
  )
  config: Optional[ComputeTokensConfig] = Field(
      default=None,
      description="""Optional parameters for the request.
      """,
  )


class _ComputeTokensParametersDict(TypedDict, total=False):
  """Parameters for computing tokens."""

  model: Optional[str]
  """ID of the model to use. For a list of models, see `Google models
    <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models>`_."""

  contents: Optional[ContentListUnionDict]
  """Input content."""

  config: Optional[ComputeTokensConfigDict]
  """Optional parameters for the request.
      """


_ComputeTokensParametersOrDict = Union[
    _ComputeTokensParameters, _ComputeTokensParametersDict
]


class TokensInfo(_common.BaseModel):
  """Tokens info with a list of tokens and the corresponding list of token ids."""

  role: Optional[str] = Field(
      default=None,
      description="""Optional. Optional fields for the role from the corresponding Content.""",
  )
  token_ids: Optional[list[str]] = Field(
      default=None, description="""A list of token ids from the input."""
  )
  tokens: Optional[list[bytes]] = Field(
      default=None, description="""A list of tokens from the input."""
  )


class TokensInfoDict(TypedDict, total=False):
  """Tokens info with a list of tokens and the corresponding list of token ids."""

  role: Optional[str]
  """Optional. Optional fields for the role from the corresponding Content."""

  token_ids: Optional[list[str]]
  """A list of token ids from the input."""

  tokens: Optional[list[bytes]]
  """A list of tokens from the input."""


TokensInfoOrDict = Union[TokensInfo, TokensInfoDict]


class ComputeTokensResponse(_common.BaseModel):
  """Response for computing tokens."""

  tokens_info: Optional[list[TokensInfo]] = Field(
      default=None,
      description="""Lists of tokens info from the input. A ComputeTokensRequest could have multiple instances with a prompt in each instance. We also need to return lists of tokens info for the request with multiple instances.""",
  )


class ComputeTokensResponseDict(TypedDict, total=False):
  """Response for computing tokens."""

  tokens_info: Optional[list[TokensInfoDict]]
  """Lists of tokens info from the input. A ComputeTokensRequest could have multiple instances with a prompt in each instance. We also need to return lists of tokens info for the request with multiple instances."""


ComputeTokensResponseOrDict = Union[
    ComputeTokensResponse, ComputeTokensResponseDict
]


class GetTuningJobConfig(_common.BaseModel):
  """Optional parameters for tunings.get method."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )


class GetTuningJobConfigDict(TypedDict, total=False):
  """Optional parameters for tunings.get method."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""


GetTuningJobConfigOrDict = Union[GetTuningJobConfig, GetTuningJobConfigDict]


class _GetTuningJobParameters(_common.BaseModel):
  """Parameters for the get method."""

  name: Optional[str] = Field(default=None, description="""""")
  config: Optional[GetTuningJobConfig] = Field(
      default=None, description="""Optional parameters for the request."""
  )


class _GetTuningJobParametersDict(TypedDict, total=False):
  """Parameters for the get method."""

  name: Optional[str]
  """"""

  config: Optional[GetTuningJobConfigDict]
  """Optional parameters for the request."""


_GetTuningJobParametersOrDict = Union[
    _GetTuningJobParameters, _GetTuningJobParametersDict
]


class TunedModel(_common.BaseModel):

  model: Optional[str] = Field(
      default=None,
      description="""Output only. The resource name of the TunedModel. Format: `projects/{project}/locations/{location}/models/{model}`.""",
  )
  endpoint: Optional[str] = Field(
      default=None,
      description="""Output only. A resource name of an Endpoint. Format: `projects/{project}/locations/{location}/endpoints/{endpoint}`.""",
  )


class TunedModelDict(TypedDict, total=False):

  model: Optional[str]
  """Output only. The resource name of the TunedModel. Format: `projects/{project}/locations/{location}/models/{model}`."""

  endpoint: Optional[str]
  """Output only. A resource name of an Endpoint. Format: `projects/{project}/locations/{location}/endpoints/{endpoint}`."""


TunedModelOrDict = Union[TunedModel, TunedModelDict]


class GoogleRpcStatus(_common.BaseModel):
  """The `Status` type defines a logical error model that is suitable for different programming environments, including REST APIs and RPC APIs.

  It is used by [gRPC](https://github.com/grpc). Each `Status` message contains
  three pieces of data: error code, error message, and error details. You can
  find out more about this error model and how to work with it in the [API
  Design Guide](https://cloud.google.com/apis/design/errors).
  """

  code: Optional[int] = Field(
      default=None,
      description="""The status code, which should be an enum value of google.rpc.Code.""",
  )
  details: Optional[list[dict[str, Any]]] = Field(
      default=None,
      description="""A list of messages that carry the error details. There is a common set of message types for APIs to use.""",
  )
  message: Optional[str] = Field(
      default=None,
      description="""A developer-facing error message, which should be in English. Any user-facing error message should be localized and sent in the google.rpc.Status.details field, or localized by the client.""",
  )


class GoogleRpcStatusDict(TypedDict, total=False):
  """The `Status` type defines a logical error model that is suitable for different programming environments, including REST APIs and RPC APIs.

  It is used by [gRPC](https://github.com/grpc). Each `Status` message contains
  three pieces of data: error code, error message, and error details. You can
  find out more about this error model and how to work with it in the [API
  Design Guide](https://cloud.google.com/apis/design/errors).
  """

  code: Optional[int]
  """The status code, which should be an enum value of google.rpc.Code."""

  details: Optional[list[dict[str, Any]]]
  """A list of messages that carry the error details. There is a common set of message types for APIs to use."""

  message: Optional[str]
  """A developer-facing error message, which should be in English. Any user-facing error message should be localized and sent in the google.rpc.Status.details field, or localized by the client."""


GoogleRpcStatusOrDict = Union[GoogleRpcStatus, GoogleRpcStatusDict]


class SupervisedHyperParameters(_common.BaseModel):
  """Hyperparameters for SFT."""

  adapter_size: Optional[AdapterSize] = Field(
      default=None, description="""Optional. Adapter size for tuning."""
  )
  epoch_count: Optional[str] = Field(
      default=None,
      description="""Optional. Number of complete passes the model makes over the entire training dataset during training.""",
  )
  learning_rate_multiplier: Optional[float] = Field(
      default=None,
      description="""Optional. Multiplier for adjusting the default learning rate.""",
  )


class SupervisedHyperParametersDict(TypedDict, total=False):
  """Hyperparameters for SFT."""

  adapter_size: Optional[AdapterSize]
  """Optional. Adapter size for tuning."""

  epoch_count: Optional[str]
  """Optional. Number of complete passes the model makes over the entire training dataset during training."""

  learning_rate_multiplier: Optional[float]
  """Optional. Multiplier for adjusting the default learning rate."""


SupervisedHyperParametersOrDict = Union[
    SupervisedHyperParameters, SupervisedHyperParametersDict
]


class SupervisedTuningSpec(_common.BaseModel):
  """Tuning Spec for Supervised Tuning for first party models."""

  hyper_parameters: Optional[SupervisedHyperParameters] = Field(
      default=None, description="""Optional. Hyperparameters for SFT."""
  )
  training_dataset_uri: Optional[str] = Field(
      default=None,
      description="""Required. Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file.""",
  )
  validation_dataset_uri: Optional[str] = Field(
      default=None,
      description="""Optional. Cloud Storage path to file containing validation dataset for tuning. The dataset must be formatted as a JSONL file.""",
  )


class SupervisedTuningSpecDict(TypedDict, total=False):
  """Tuning Spec for Supervised Tuning for first party models."""

  hyper_parameters: Optional[SupervisedHyperParametersDict]
  """Optional. Hyperparameters for SFT."""

  training_dataset_uri: Optional[str]
  """Required. Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file."""

  validation_dataset_uri: Optional[str]
  """Optional. Cloud Storage path to file containing validation dataset for tuning. The dataset must be formatted as a JSONL file."""


SupervisedTuningSpecOrDict = Union[
    SupervisedTuningSpec, SupervisedTuningSpecDict
]


class DatasetDistributionDistributionBucket(_common.BaseModel):
  """Dataset bucket used to create a histogram for the distribution given a population of values."""

  count: Optional[str] = Field(
      default=None,
      description="""Output only. Number of values in the bucket.""",
  )
  left: Optional[float] = Field(
      default=None, description="""Output only. Left bound of the bucket."""
  )
  right: Optional[float] = Field(
      default=None, description="""Output only. Right bound of the bucket."""
  )


class DatasetDistributionDistributionBucketDict(TypedDict, total=False):
  """Dataset bucket used to create a histogram for the distribution given a population of values."""

  count: Optional[str]
  """Output only. Number of values in the bucket."""

  left: Optional[float]
  """Output only. Left bound of the bucket."""

  right: Optional[float]
  """Output only. Right bound of the bucket."""


DatasetDistributionDistributionBucketOrDict = Union[
    DatasetDistributionDistributionBucket,
    DatasetDistributionDistributionBucketDict,
]


class DatasetDistribution(_common.BaseModel):
  """Distribution computed over a tuning dataset."""

  buckets: Optional[list[DatasetDistributionDistributionBucket]] = Field(
      default=None, description="""Output only. Defines the histogram bucket."""
  )
  max: Optional[float] = Field(
      default=None,
      description="""Output only. The maximum of the population values.""",
  )
  mean: Optional[float] = Field(
      default=None,
      description="""Output only. The arithmetic mean of the values in the population.""",
  )
  median: Optional[float] = Field(
      default=None,
      description="""Output only. The median of the values in the population.""",
  )
  min: Optional[float] = Field(
      default=None,
      description="""Output only. The minimum of the population values.""",
  )
  p5: Optional[float] = Field(
      default=None,
      description="""Output only. The 5th percentile of the values in the population.""",
  )
  p95: Optional[float] = Field(
      default=None,
      description="""Output only. The 95th percentile of the values in the population.""",
  )
  sum: Optional[float] = Field(
      default=None,
      description="""Output only. Sum of a given population of values.""",
  )


class DatasetDistributionDict(TypedDict, total=False):
  """Distribution computed over a tuning dataset."""

  buckets: Optional[list[DatasetDistributionDistributionBucketDict]]
  """Output only. Defines the histogram bucket."""

  max: Optional[float]
  """Output only. The maximum of the population values."""

  mean: Optional[float]
  """Output only. The arithmetic mean of the values in the population."""

  median: Optional[float]
  """Output only. The median of the values in the population."""

  min: Optional[float]
  """Output only. The minimum of the population values."""

  p5: Optional[float]
  """Output only. The 5th percentile of the values in the population."""

  p95: Optional[float]
  """Output only. The 95th percentile of the values in the population."""

  sum: Optional[float]
  """Output only. Sum of a given population of values."""


DatasetDistributionOrDict = Union[DatasetDistribution, DatasetDistributionDict]


class DatasetStats(_common.BaseModel):
  """Statistics computed over a tuning dataset."""

  total_billable_character_count: Optional[str] = Field(
      default=None,
      description="""Output only. Number of billable characters in the tuning dataset.""",
  )
  total_tuning_character_count: Optional[str] = Field(
      default=None,
      description="""Output only. Number of tuning characters in the tuning dataset.""",
  )
  tuning_dataset_example_count: Optional[str] = Field(
      default=None,
      description="""Output only. Number of examples in the tuning dataset.""",
  )
  tuning_step_count: Optional[str] = Field(
      default=None,
      description="""Output only. Number of tuning steps for this Tuning Job.""",
  )
  user_dataset_examples: Optional[list[Content]] = Field(
      default=None,
      description="""Output only. Sample user messages in the training dataset uri.""",
  )
  user_input_token_distribution: Optional[DatasetDistribution] = Field(
      default=None,
      description="""Output only. Dataset distributions for the user input tokens.""",
  )
  user_message_per_example_distribution: Optional[DatasetDistribution] = Field(
      default=None,
      description="""Output only. Dataset distributions for the messages per example.""",
  )
  user_output_token_distribution: Optional[DatasetDistribution] = Field(
      default=None,
      description="""Output only. Dataset distributions for the user output tokens.""",
  )


class DatasetStatsDict(TypedDict, total=False):
  """Statistics computed over a tuning dataset."""

  total_billable_character_count: Optional[str]
  """Output only. Number of billable characters in the tuning dataset."""

  total_tuning_character_count: Optional[str]
  """Output only. Number of tuning characters in the tuning dataset."""

  tuning_dataset_example_count: Optional[str]
  """Output only. Number of examples in the tuning dataset."""

  tuning_step_count: Optional[str]
  """Output only. Number of tuning steps for this Tuning Job."""

  user_dataset_examples: Optional[list[ContentDict]]
  """Output only. Sample user messages in the training dataset uri."""

  user_input_token_distribution: Optional[DatasetDistributionDict]
  """Output only. Dataset distributions for the user input tokens."""

  user_message_per_example_distribution: Optional[DatasetDistributionDict]
  """Output only. Dataset distributions for the messages per example."""

  user_output_token_distribution: Optional[DatasetDistributionDict]
  """Output only. Dataset distributions for the user output tokens."""


DatasetStatsOrDict = Union[DatasetStats, DatasetStatsDict]


class DistillationDataStats(_common.BaseModel):
  """Statistics computed for datasets used for distillation."""

  training_dataset_stats: Optional[DatasetStats] = Field(
      default=None,
      description="""Output only. Statistics computed for the training dataset.""",
  )


class DistillationDataStatsDict(TypedDict, total=False):
  """Statistics computed for datasets used for distillation."""

  training_dataset_stats: Optional[DatasetStatsDict]
  """Output only. Statistics computed for the training dataset."""


DistillationDataStatsOrDict = Union[
    DistillationDataStats, DistillationDataStatsDict
]


class SupervisedTuningDatasetDistributionDatasetBucket(_common.BaseModel):
  """Dataset bucket used to create a histogram for the distribution given a population of values."""

  count: Optional[float] = Field(
      default=None,
      description="""Output only. Number of values in the bucket.""",
  )
  left: Optional[float] = Field(
      default=None, description="""Output only. Left bound of the bucket."""
  )
  right: Optional[float] = Field(
      default=None, description="""Output only. Right bound of the bucket."""
  )


class SupervisedTuningDatasetDistributionDatasetBucketDict(
    TypedDict, total=False
):
  """Dataset bucket used to create a histogram for the distribution given a population of values."""

  count: Optional[float]
  """Output only. Number of values in the bucket."""

  left: Optional[float]
  """Output only. Left bound of the bucket."""

  right: Optional[float]
  """Output only. Right bound of the bucket."""


SupervisedTuningDatasetDistributionDatasetBucketOrDict = Union[
    SupervisedTuningDatasetDistributionDatasetBucket,
    SupervisedTuningDatasetDistributionDatasetBucketDict,
]


class SupervisedTuningDatasetDistribution(_common.BaseModel):
  """Dataset distribution for Supervised Tuning."""

  billable_sum: Optional[str] = Field(
      default=None,
      description="""Output only. Sum of a given population of values that are billable.""",
  )
  buckets: Optional[list[SupervisedTuningDatasetDistributionDatasetBucket]] = (
      Field(
          default=None,
          description="""Output only. Defines the histogram bucket.""",
      )
  )
  max: Optional[float] = Field(
      default=None,
      description="""Output only. The maximum of the population values.""",
  )
  mean: Optional[float] = Field(
      default=None,
      description="""Output only. The arithmetic mean of the values in the population.""",
  )
  median: Optional[float] = Field(
      default=None,
      description="""Output only. The median of the values in the population.""",
  )
  min: Optional[float] = Field(
      default=None,
      description="""Output only. The minimum of the population values.""",
  )
  p5: Optional[float] = Field(
      default=None,
      description="""Output only. The 5th percentile of the values in the population.""",
  )
  p95: Optional[float] = Field(
      default=None,
      description="""Output only. The 95th percentile of the values in the population.""",
  )
  sum: Optional[str] = Field(
      default=None,
      description="""Output only. Sum of a given population of values.""",
  )


class SupervisedTuningDatasetDistributionDict(TypedDict, total=False):
  """Dataset distribution for Supervised Tuning."""

  billable_sum: Optional[str]
  """Output only. Sum of a given population of values that are billable."""

  buckets: Optional[list[SupervisedTuningDatasetDistributionDatasetBucketDict]]
  """Output only. Defines the histogram bucket."""

  max: Optional[float]
  """Output only. The maximum of the population values."""

  mean: Optional[float]
  """Output only. The arithmetic mean of the values in the population."""

  median: Optional[float]
  """Output only. The median of the values in the population."""

  min: Optional[float]
  """Output only. The minimum of the population values."""

  p5: Optional[float]
  """Output only. The 5th percentile of the values in the population."""

  p95: Optional[float]
  """Output only. The 95th percentile of the values in the population."""

  sum: Optional[str]
  """Output only. Sum of a given population of values."""


SupervisedTuningDatasetDistributionOrDict = Union[
    SupervisedTuningDatasetDistribution, SupervisedTuningDatasetDistributionDict
]


class SupervisedTuningDataStats(_common.BaseModel):
  """Tuning data statistics for Supervised Tuning."""

  total_billable_character_count: Optional[str] = Field(
      default=None,
      description="""Output only. Number of billable characters in the tuning dataset.""",
  )
  total_billable_token_count: Optional[str] = Field(
      default=None,
      description="""Output only. Number of billable tokens in the tuning dataset.""",
  )
  total_truncated_example_count: Optional[str] = Field(
      default=None,
      description="""The number of examples in the dataset that have been truncated by any amount.""",
  )
  total_tuning_character_count: Optional[str] = Field(
      default=None,
      description="""Output only. Number of tuning characters in the tuning dataset.""",
  )
  truncated_example_indices: Optional[list[str]] = Field(
      default=None,
      description="""A partial sample of the indices (starting from 1) of the truncated examples.""",
  )
  tuning_dataset_example_count: Optional[str] = Field(
      default=None,
      description="""Output only. Number of examples in the tuning dataset.""",
  )
  tuning_step_count: Optional[str] = Field(
      default=None,
      description="""Output only. Number of tuning steps for this Tuning Job.""",
  )
  user_dataset_examples: Optional[list[Content]] = Field(
      default=None,
      description="""Output only. Sample user messages in the training dataset uri.""",
  )
  user_input_token_distribution: Optional[
      SupervisedTuningDatasetDistribution
  ] = Field(
      default=None,
      description="""Output only. Dataset distributions for the user input tokens.""",
  )
  user_message_per_example_distribution: Optional[
      SupervisedTuningDatasetDistribution
  ] = Field(
      default=None,
      description="""Output only. Dataset distributions for the messages per example.""",
  )
  user_output_token_distribution: Optional[
      SupervisedTuningDatasetDistribution
  ] = Field(
      default=None,
      description="""Output only. Dataset distributions for the user output tokens.""",
  )


class SupervisedTuningDataStatsDict(TypedDict, total=False):
  """Tuning data statistics for Supervised Tuning."""

  total_billable_character_count: Optional[str]
  """Output only. Number of billable characters in the tuning dataset."""

  total_billable_token_count: Optional[str]
  """Output only. Number of billable tokens in the tuning dataset."""

  total_truncated_example_count: Optional[str]
  """The number of examples in the dataset that have been truncated by any amount."""

  total_tuning_character_count: Optional[str]
  """Output only. Number of tuning characters in the tuning dataset."""

  truncated_example_indices: Optional[list[str]]
  """A partial sample of the indices (starting from 1) of the truncated examples."""

  tuning_dataset_example_count: Optional[str]
  """Output only. Number of examples in the tuning dataset."""

  tuning_step_count: Optional[str]
  """Output only. Number of tuning steps for this Tuning Job."""

  user_dataset_examples: Optional[list[ContentDict]]
  """Output only. Sample user messages in the training dataset uri."""

  user_input_token_distribution: Optional[
      SupervisedTuningDatasetDistributionDict
  ]
  """Output only. Dataset distributions for the user input tokens."""

  user_message_per_example_distribution: Optional[
      SupervisedTuningDatasetDistributionDict
  ]
  """Output only. Dataset distributions for the messages per example."""

  user_output_token_distribution: Optional[
      SupervisedTuningDatasetDistributionDict
  ]
  """Output only. Dataset distributions for the user output tokens."""


SupervisedTuningDataStatsOrDict = Union[
    SupervisedTuningDataStats, SupervisedTuningDataStatsDict
]


class TuningDataStats(_common.BaseModel):
  """The tuning data statistic values for TuningJob."""

  distillation_data_stats: Optional[DistillationDataStats] = Field(
      default=None, description="""Output only. Statistics for distillation."""
  )
  supervised_tuning_data_stats: Optional[SupervisedTuningDataStats] = Field(
      default=None, description="""The SFT Tuning data stats."""
  )


class TuningDataStatsDict(TypedDict, total=False):
  """The tuning data statistic values for TuningJob."""

  distillation_data_stats: Optional[DistillationDataStatsDict]
  """Output only. Statistics for distillation."""

  supervised_tuning_data_stats: Optional[SupervisedTuningDataStatsDict]
  """The SFT Tuning data stats."""


TuningDataStatsOrDict = Union[TuningDataStats, TuningDataStatsDict]


class EncryptionSpec(_common.BaseModel):
  """Represents a customer-managed encryption key spec that can be applied to a top-level resource."""

  kms_key_name: Optional[str] = Field(
      default=None,
      description="""Required. The Cloud KMS resource identifier of the customer managed encryption key used to protect a resource. Has the form: `projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key`. The key needs to be in the same region as where the compute resource is created.""",
  )


class EncryptionSpecDict(TypedDict, total=False):
  """Represents a customer-managed encryption key spec that can be applied to a top-level resource."""

  kms_key_name: Optional[str]
  """Required. The Cloud KMS resource identifier of the customer managed encryption key used to protect a resource. Has the form: `projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key`. The key needs to be in the same region as where the compute resource is created."""


EncryptionSpecOrDict = Union[EncryptionSpec, EncryptionSpecDict]


class DistillationHyperParameters(_common.BaseModel):
  """Hyperparameters for Distillation."""

  adapter_size: Optional[AdapterSize] = Field(
      default=None, description="""Optional. Adapter size for distillation."""
  )
  epoch_count: Optional[str] = Field(
      default=None,
      description="""Optional. Number of complete passes the model makes over the entire training dataset during training.""",
  )
  learning_rate_multiplier: Optional[float] = Field(
      default=None,
      description="""Optional. Multiplier for adjusting the default learning rate.""",
  )


class DistillationHyperParametersDict(TypedDict, total=False):
  """Hyperparameters for Distillation."""

  adapter_size: Optional[AdapterSize]
  """Optional. Adapter size for distillation."""

  epoch_count: Optional[str]
  """Optional. Number of complete passes the model makes over the entire training dataset during training."""

  learning_rate_multiplier: Optional[float]
  """Optional. Multiplier for adjusting the default learning rate."""


DistillationHyperParametersOrDict = Union[
    DistillationHyperParameters, DistillationHyperParametersDict
]


class DistillationSpec(_common.BaseModel):
  """Tuning Spec for Distillation."""

  base_teacher_model: Optional[str] = Field(
      default=None,
      description="""The base teacher model that is being distilled, e.g., "gemini-1.0-pro-002".""",
  )
  hyper_parameters: Optional[DistillationHyperParameters] = Field(
      default=None,
      description="""Optional. Hyperparameters for Distillation.""",
  )
  pipeline_root_directory: Optional[str] = Field(
      default=None,
      description="""Required. A path in a Cloud Storage bucket, which will be treated as the root output directory of the distillation pipeline. It is used by the system to generate the paths of output artifacts.""",
  )
  student_model: Optional[str] = Field(
      default=None,
      description="""The student model that is being tuned, e.g., "google/gemma-2b-1.1-it".""",
  )
  training_dataset_uri: Optional[str] = Field(
      default=None,
      description="""Required. Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file.""",
  )
  tuned_teacher_model_source: Optional[str] = Field(
      default=None,
      description="""The resource name of the Tuned teacher model. Format: `projects/{project}/locations/{location}/models/{model}`.""",
  )
  validation_dataset_uri: Optional[str] = Field(
      default=None,
      description="""Optional. Cloud Storage path to file containing validation dataset for tuning. The dataset must be formatted as a JSONL file.""",
  )


class DistillationSpecDict(TypedDict, total=False):
  """Tuning Spec for Distillation."""

  base_teacher_model: Optional[str]
  """The base teacher model that is being distilled, e.g., "gemini-1.0-pro-002"."""

  hyper_parameters: Optional[DistillationHyperParametersDict]
  """Optional. Hyperparameters for Distillation."""

  pipeline_root_directory: Optional[str]
  """Required. A path in a Cloud Storage bucket, which will be treated as the root output directory of the distillation pipeline. It is used by the system to generate the paths of output artifacts."""

  student_model: Optional[str]
  """The student model that is being tuned, e.g., "google/gemma-2b-1.1-it"."""

  training_dataset_uri: Optional[str]
  """Required. Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file."""

  tuned_teacher_model_source: Optional[str]
  """The resource name of the Tuned teacher model. Format: `projects/{project}/locations/{location}/models/{model}`."""

  validation_dataset_uri: Optional[str]
  """Optional. Cloud Storage path to file containing validation dataset for tuning. The dataset must be formatted as a JSONL file."""


DistillationSpecOrDict = Union[DistillationSpec, DistillationSpecDict]


class PartnerModelTuningSpec(_common.BaseModel):
  """Tuning spec for Partner models."""

  hyper_parameters: Optional[dict[str, Any]] = Field(
      default=None,
      description="""Hyperparameters for tuning. The accepted hyper_parameters and their valid range of values will differ depending on the base model.""",
  )
  training_dataset_uri: Optional[str] = Field(
      default=None,
      description="""Required. Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file.""",
  )
  validation_dataset_uri: Optional[str] = Field(
      default=None,
      description="""Optional. Cloud Storage path to file containing validation dataset for tuning. The dataset must be formatted as a JSONL file.""",
  )


class PartnerModelTuningSpecDict(TypedDict, total=False):
  """Tuning spec for Partner models."""

  hyper_parameters: Optional[dict[str, Any]]
  """Hyperparameters for tuning. The accepted hyper_parameters and their valid range of values will differ depending on the base model."""

  training_dataset_uri: Optional[str]
  """Required. Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file."""

  validation_dataset_uri: Optional[str]
  """Optional. Cloud Storage path to file containing validation dataset for tuning. The dataset must be formatted as a JSONL file."""


PartnerModelTuningSpecOrDict = Union[
    PartnerModelTuningSpec, PartnerModelTuningSpecDict
]


class TuningJob(_common.BaseModel):
  """A tuning job."""

  name: Optional[str] = Field(
      default=None,
      description="""Output only. Identifier. Resource name of a TuningJob. Format: `projects/{project}/locations/{location}/tuningJobs/{tuning_job}`""",
  )
  state: Optional[JobState] = Field(
      default=None,
      description="""Output only. The detailed state of the job.""",
  )
  create_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Output only. Time when the TuningJob was created.""",
  )
  start_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Output only. Time when the TuningJob for the first time entered the `JOB_STATE_RUNNING` state.""",
  )
  end_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Output only. Time when the TuningJob entered any of the following JobStates: `JOB_STATE_SUCCEEDED`, `JOB_STATE_FAILED`, `JOB_STATE_CANCELLED`, `JOB_STATE_EXPIRED`.""",
  )
  update_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Output only. Time when the TuningJob was most recently updated.""",
  )
  error: Optional[GoogleRpcStatus] = Field(
      default=None,
      description="""Output only. Only populated when job's state is `JOB_STATE_FAILED` or `JOB_STATE_CANCELLED`.""",
  )
  description: Optional[str] = Field(
      default=None,
      description="""Optional. The description of the TuningJob.""",
  )
  base_model: Optional[str] = Field(
      default=None,
      description="""The base model that is being tuned, e.g., "gemini-1.0-pro-002". .""",
  )
  tuned_model: Optional[TunedModel] = Field(
      default=None,
      description="""Output only. The tuned model resources assiociated with this TuningJob.""",
  )
  supervised_tuning_spec: Optional[SupervisedTuningSpec] = Field(
      default=None, description="""Tuning Spec for Supervised Fine Tuning."""
  )
  tuning_data_stats: Optional[TuningDataStats] = Field(
      default=None,
      description="""Output only. The tuning data statistics associated with this TuningJob.""",
  )
  encryption_spec: Optional[EncryptionSpec] = Field(
      default=None,
      description="""Customer-managed encryption key options for a TuningJob. If this is set, then all resources created by the TuningJob will be encrypted with the provided encryption key.""",
  )
  distillation_spec: Optional[DistillationSpec] = Field(
      default=None, description="""Tuning Spec for Distillation."""
  )
  partner_model_tuning_spec: Optional[PartnerModelTuningSpec] = Field(
      default=None,
      description="""Tuning Spec for open sourced and third party Partner models.""",
  )
  pipeline_job: Optional[str] = Field(
      default=None,
      description="""Output only. The resource name of the PipelineJob associated with the TuningJob. Format: `projects/{project}/locations/{location}/pipelineJobs/{pipeline_job}`.""",
  )
  experiment: Optional[str] = Field(
      default=None,
      description="""Output only. The Experiment associated with this TuningJob.""",
  )
  labels: Optional[dict[str, str]] = Field(
      default=None,
      description="""Optional. The labels with user-defined metadata to organize TuningJob and generated resources such as Model and Endpoint. Label keys and values can be no longer than 64 characters (Unicode codepoints), can only contain lowercase letters, numeric characters, underscores and dashes. International characters are allowed. See https://goo.gl/xmQnxf for more information and examples of labels.""",
  )
  tuned_model_display_name: Optional[str] = Field(
      default=None,
      description="""Optional. The display name of the TunedModel. The name can be up to 128 characters long and can consist of any UTF-8 characters.""",
  )

  @property
  def has_ended(self) -> bool:
    """Whether the tuning job has ended."""
    return self.state in JOB_STATES_ENDED

  @property
  def has_succeeded(self) -> bool:
    """Whether the tuning job has succeeded."""
    return self.state in JOB_STATES_SUCCEEDED


class TuningJobDict(TypedDict, total=False):
  """A tuning job."""

  name: Optional[str]
  """Output only. Identifier. Resource name of a TuningJob. Format: `projects/{project}/locations/{location}/tuningJobs/{tuning_job}`"""

  state: Optional[JobState]
  """Output only. The detailed state of the job."""

  create_time: Optional[datetime.datetime]
  """Output only. Time when the TuningJob was created."""

  start_time: Optional[datetime.datetime]
  """Output only. Time when the TuningJob for the first time entered the `JOB_STATE_RUNNING` state."""

  end_time: Optional[datetime.datetime]
  """Output only. Time when the TuningJob entered any of the following JobStates: `JOB_STATE_SUCCEEDED`, `JOB_STATE_FAILED`, `JOB_STATE_CANCELLED`, `JOB_STATE_EXPIRED`."""

  update_time: Optional[datetime.datetime]
  """Output only. Time when the TuningJob was most recently updated."""

  error: Optional[GoogleRpcStatusDict]
  """Output only. Only populated when job's state is `JOB_STATE_FAILED` or `JOB_STATE_CANCELLED`."""

  description: Optional[str]
  """Optional. The description of the TuningJob."""

  base_model: Optional[str]
  """The base model that is being tuned, e.g., "gemini-1.0-pro-002". ."""

  tuned_model: Optional[TunedModelDict]
  """Output only. The tuned model resources assiociated with this TuningJob."""

  supervised_tuning_spec: Optional[SupervisedTuningSpecDict]
  """Tuning Spec for Supervised Fine Tuning."""

  tuning_data_stats: Optional[TuningDataStatsDict]
  """Output only. The tuning data statistics associated with this TuningJob."""

  encryption_spec: Optional[EncryptionSpecDict]
  """Customer-managed encryption key options for a TuningJob. If this is set, then all resources created by the TuningJob will be encrypted with the provided encryption key."""

  distillation_spec: Optional[DistillationSpecDict]
  """Tuning Spec for Distillation."""

  partner_model_tuning_spec: Optional[PartnerModelTuningSpecDict]
  """Tuning Spec for open sourced and third party Partner models."""

  pipeline_job: Optional[str]
  """Output only. The resource name of the PipelineJob associated with the TuningJob. Format: `projects/{project}/locations/{location}/pipelineJobs/{pipeline_job}`."""

  experiment: Optional[str]
  """Output only. The Experiment associated with this TuningJob."""

  labels: Optional[dict[str, str]]
  """Optional. The labels with user-defined metadata to organize TuningJob and generated resources such as Model and Endpoint. Label keys and values can be no longer than 64 characters (Unicode codepoints), can only contain lowercase letters, numeric characters, underscores and dashes. International characters are allowed. See https://goo.gl/xmQnxf for more information and examples of labels."""

  tuned_model_display_name: Optional[str]
  """Optional. The display name of the TunedModel. The name can be up to 128 characters long and can consist of any UTF-8 characters."""


TuningJobOrDict = Union[TuningJob, TuningJobDict]


class ListTuningJobsConfig(_common.BaseModel):
  """Configuration for the list tuning jobs method."""

  page_size: Optional[int] = Field(default=None, description="""""")
  page_token: Optional[str] = Field(default=None, description="""""")
  filter: Optional[str] = Field(default=None, description="""""")


class ListTuningJobsConfigDict(TypedDict, total=False):
  """Configuration for the list tuning jobs method."""

  page_size: Optional[int]
  """"""

  page_token: Optional[str]
  """"""

  filter: Optional[str]
  """"""


ListTuningJobsConfigOrDict = Union[
    ListTuningJobsConfig, ListTuningJobsConfigDict
]


class _ListTuningJobsParameters(_common.BaseModel):
  """Parameters for the list tuning jobs method."""

  config: Optional[ListTuningJobsConfig] = Field(
      default=None, description=""""""
  )


class _ListTuningJobsParametersDict(TypedDict, total=False):
  """Parameters for the list tuning jobs method."""

  config: Optional[ListTuningJobsConfigDict]
  """"""


_ListTuningJobsParametersOrDict = Union[
    _ListTuningJobsParameters, _ListTuningJobsParametersDict
]


class ListTuningJobsResponse(_common.BaseModel):
  """Response for the list tuning jobs method."""

  next_page_token: Optional[str] = Field(
      default=None,
      description="""A token to retrieve the next page of results. Pass to ListTuningJobsRequest.page_token to obtain that page.""",
  )
  tuning_jobs: Optional[list[TuningJob]] = Field(
      default=None, description="""List of TuningJobs in the requested page."""
  )


class ListTuningJobsResponseDict(TypedDict, total=False):
  """Response for the list tuning jobs method."""

  next_page_token: Optional[str]
  """A token to retrieve the next page of results. Pass to ListTuningJobsRequest.page_token to obtain that page."""

  tuning_jobs: Optional[list[TuningJobDict]]
  """List of TuningJobs in the requested page."""


ListTuningJobsResponseOrDict = Union[
    ListTuningJobsResponse, ListTuningJobsResponseDict
]


class TuningExample(_common.BaseModel):

  text_input: Optional[str] = Field(
      default=None, description="""Text model input."""
  )
  output: Optional[str] = Field(
      default=None, description="""The expected model output."""
  )


class TuningExampleDict(TypedDict, total=False):

  text_input: Optional[str]
  """Text model input."""

  output: Optional[str]
  """The expected model output."""


TuningExampleOrDict = Union[TuningExample, TuningExampleDict]


class TuningDataset(_common.BaseModel):
  """Supervised fune-tuning training dataset."""

  gcs_uri: Optional[str] = Field(
      default=None,
      description="""GCS URI of the file containing training dataset in JSONL format.""",
  )
  examples: Optional[list[TuningExample]] = Field(
      default=None,
      description="""Inline examples with simple input/output text.""",
  )


class TuningDatasetDict(TypedDict, total=False):
  """Supervised fune-tuning training dataset."""

  gcs_uri: Optional[str]
  """GCS URI of the file containing training dataset in JSONL format."""

  examples: Optional[list[TuningExampleDict]]
  """Inline examples with simple input/output text."""


TuningDatasetOrDict = Union[TuningDataset, TuningDatasetDict]


class TuningValidationDataset(_common.BaseModel):

  gcs_uri: Optional[str] = Field(
      default=None,
      description="""GCS URI of the file containing validation dataset in JSONL format.""",
  )


class TuningValidationDatasetDict(TypedDict, total=False):

  gcs_uri: Optional[str]
  """GCS URI of the file containing validation dataset in JSONL format."""


TuningValidationDatasetOrDict = Union[
    TuningValidationDataset, TuningValidationDatasetDict
]


class CreateTuningJobConfig(_common.BaseModel):
  """Supervised fine-tuning job creation request - optional fields."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  validation_dataset: Optional[TuningValidationDataset] = Field(
      default=None,
      description="""Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file.""",
  )
  tuned_model_display_name: Optional[str] = Field(
      default=None,
      description="""The display name of the tuned Model. The name can be up to 128 characters long and can consist of any UTF-8 characters.""",
  )
  description: Optional[str] = Field(
      default=None, description="""The description of the TuningJob"""
  )
  epoch_count: Optional[int] = Field(
      default=None,
      description="""Number of complete passes the model makes over the entire training dataset during training.""",
  )
  learning_rate_multiplier: Optional[float] = Field(
      default=None,
      description="""Multiplier for adjusting the default learning rate.""",
  )
  adapter_size: Optional[AdapterSize] = Field(
      default=None, description="""Adapter size for tuning."""
  )
  batch_size: Optional[int] = Field(
      default=None,
      description="""The batch size hyperparameter for tuning. If not set, a default of 4 or 16 will be used based on the number of training examples.""",
  )
  learning_rate: Optional[float] = Field(
      default=None,
      description="""The learning rate hyperparameter for tuning. If not set, a default of 0.001 or 0.0002 will be calculated based on the number of training examples.""",
  )


class CreateTuningJobConfigDict(TypedDict, total=False):
  """Supervised fine-tuning job creation request - optional fields."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  validation_dataset: Optional[TuningValidationDatasetDict]
  """Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file."""

  tuned_model_display_name: Optional[str]
  """The display name of the tuned Model. The name can be up to 128 characters long and can consist of any UTF-8 characters."""

  description: Optional[str]
  """The description of the TuningJob"""

  epoch_count: Optional[int]
  """Number of complete passes the model makes over the entire training dataset during training."""

  learning_rate_multiplier: Optional[float]
  """Multiplier for adjusting the default learning rate."""

  adapter_size: Optional[AdapterSize]
  """Adapter size for tuning."""

  batch_size: Optional[int]
  """The batch size hyperparameter for tuning. If not set, a default of 4 or 16 will be used based on the number of training examples."""

  learning_rate: Optional[float]
  """The learning rate hyperparameter for tuning. If not set, a default of 0.001 or 0.0002 will be calculated based on the number of training examples."""


CreateTuningJobConfigOrDict = Union[
    CreateTuningJobConfig, CreateTuningJobConfigDict
]


class _CreateTuningJobParameters(_common.BaseModel):
  """Supervised fine-tuning job creation parameters - optional fields."""

  base_model: Optional[str] = Field(
      default=None,
      description="""The base model that is being tuned, e.g., "gemini-1.0-pro-002".""",
  )
  training_dataset: Optional[TuningDataset] = Field(
      default=None,
      description="""Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file.""",
  )
  config: Optional[CreateTuningJobConfig] = Field(
      default=None, description="""Configuration for the tuning job."""
  )


class _CreateTuningJobParametersDict(TypedDict, total=False):
  """Supervised fine-tuning job creation parameters - optional fields."""

  base_model: Optional[str]
  """The base model that is being tuned, e.g., "gemini-1.0-pro-002"."""

  training_dataset: Optional[TuningDatasetDict]
  """Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file."""

  config: Optional[CreateTuningJobConfigDict]
  """Configuration for the tuning job."""


_CreateTuningJobParametersOrDict = Union[
    _CreateTuningJobParameters, _CreateTuningJobParametersDict
]


class TuningJobOrOperation(_common.BaseModel):
  """A tuning job or an long-running-operation that resolves to a tuning job."""

  tuning_job: Optional[TuningJob] = Field(default=None, description="""""")


class TuningJobOrOperationDict(TypedDict, total=False):
  """A tuning job or an long-running-operation that resolves to a tuning job."""

  tuning_job: Optional[TuningJobDict]
  """"""


TuningJobOrOperationOrDict = Union[
    TuningJobOrOperation, TuningJobOrOperationDict
]


class DistillationDataset(_common.BaseModel):
  """Training dataset."""

  gcs_uri: Optional[str] = Field(
      default=None,
      description="""GCS URI of the file containing training dataset in JSONL format.""",
  )


class DistillationDatasetDict(TypedDict, total=False):
  """Training dataset."""

  gcs_uri: Optional[str]
  """GCS URI of the file containing training dataset in JSONL format."""


DistillationDatasetOrDict = Union[DistillationDataset, DistillationDatasetDict]


class DistillationValidationDataset(_common.BaseModel):
  """Validation dataset."""

  gcs_uri: Optional[str] = Field(
      default=None,
      description="""GCS URI of the file containing validation dataset in JSONL format.""",
  )


class DistillationValidationDatasetDict(TypedDict, total=False):
  """Validation dataset."""

  gcs_uri: Optional[str]
  """GCS URI of the file containing validation dataset in JSONL format."""


DistillationValidationDatasetOrDict = Union[
    DistillationValidationDataset, DistillationValidationDatasetDict
]


class CreateDistillationJobConfig(_common.BaseModel):
  """Distillation job creation request - optional fields."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  validation_dataset: Optional[DistillationValidationDataset] = Field(
      default=None,
      description="""Cloud Storage path to file containing validation dataset for tuning. The dataset must be formatted as a JSONL file.""",
  )
  tuned_model_display_name: Optional[str] = Field(
      default=None,
      description="""The display name of the tuned Model. The name can be up to 128 characters long and can consist of any UTF-8 characters.""",
  )
  epoch_count: Optional[int] = Field(
      default=None,
      description="""Number of complete passes the model makes over the entire training dataset during training.""",
  )
  learning_rate_multiplier: Optional[float] = Field(
      default=None,
      description="""Multiplier for adjusting the default learning rate.""",
  )
  adapter_size: Optional[AdapterSize] = Field(
      default=None, description="""Adapter size for tuning."""
  )
  pipeline_root_directory: Optional[str] = Field(
      default=None,
      description="""The resource name of the PipelineJob associated with the TuningJob. Format:`projects/{project}/locations/{location}/pipelineJobs/{pipeline_job}`.""",
  )


class CreateDistillationJobConfigDict(TypedDict, total=False):
  """Distillation job creation request - optional fields."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  validation_dataset: Optional[DistillationValidationDatasetDict]
  """Cloud Storage path to file containing validation dataset for tuning. The dataset must be formatted as a JSONL file."""

  tuned_model_display_name: Optional[str]
  """The display name of the tuned Model. The name can be up to 128 characters long and can consist of any UTF-8 characters."""

  epoch_count: Optional[int]
  """Number of complete passes the model makes over the entire training dataset during training."""

  learning_rate_multiplier: Optional[float]
  """Multiplier for adjusting the default learning rate."""

  adapter_size: Optional[AdapterSize]
  """Adapter size for tuning."""

  pipeline_root_directory: Optional[str]
  """The resource name of the PipelineJob associated with the TuningJob. Format:`projects/{project}/locations/{location}/pipelineJobs/{pipeline_job}`."""


CreateDistillationJobConfigOrDict = Union[
    CreateDistillationJobConfig, CreateDistillationJobConfigDict
]


class _CreateDistillationJobParameters(_common.BaseModel):
  """Distillation job creation parameters - optional fields."""

  student_model: Optional[str] = Field(
      default=None,
      description="""The student model that is being tuned, e.g. ``google/gemma-2b-1.1-it``.""",
  )
  teacher_model: Optional[str] = Field(
      default=None,
      description="""The teacher model that is being distilled from, e.g. ``gemini-1.0-pro-002``.""",
  )
  training_dataset: Optional[DistillationDataset] = Field(
      default=None,
      description="""Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file.""",
  )
  config: Optional[CreateDistillationJobConfig] = Field(
      default=None, description="""Configuration for the distillation job."""
  )


class _CreateDistillationJobParametersDict(TypedDict, total=False):
  """Distillation job creation parameters - optional fields."""

  student_model: Optional[str]
  """The student model that is being tuned, e.g. ``google/gemma-2b-1.1-it``."""

  teacher_model: Optional[str]
  """The teacher model that is being distilled from, e.g. ``gemini-1.0-pro-002``."""

  training_dataset: Optional[DistillationDatasetDict]
  """Cloud Storage path to file containing training dataset for tuning. The dataset must be formatted as a JSONL file."""

  config: Optional[CreateDistillationJobConfigDict]
  """Configuration for the distillation job."""


_CreateDistillationJobParametersOrDict = Union[
    _CreateDistillationJobParameters, _CreateDistillationJobParametersDict
]


class CreateCachedContentConfig(_common.BaseModel):
  """Class for configuring optional cached content creation parameters."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  ttl: Optional[str] = Field(
      default=None,
      description="""The TTL for this resource. The expiration time is computed: now + TTL.""",
  )
  expire_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Timestamp of when this resource is considered expired.""",
  )
  display_name: Optional[str] = Field(
      default=None,
      description="""The user-generated meaningful display name of the cached content.
      """,
  )
  system_instruction: Optional[ContentUnion] = Field(
      default=None,
      description="""Developer set system instruction.
      """,
  )
  tools: Optional[list[Tool]] = Field(
      default=None,
      description="""A list of `Tools` the model may use to generate the next response.
      """,
  )
  tool_config: Optional[ToolConfig] = Field(
      default=None,
      description="""Configuration for the tools to use. This config is shared for all tools.
      """,
  )


class CreateCachedContentConfigDict(TypedDict, total=False):
  """Class for configuring optional cached content creation parameters."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  ttl: Optional[str]
  """The TTL for this resource. The expiration time is computed: now + TTL."""

  expire_time: Optional[datetime.datetime]
  """Timestamp of when this resource is considered expired."""

  display_name: Optional[str]
  """The user-generated meaningful display name of the cached content.
      """

  system_instruction: Optional[ContentUnionDict]
  """Developer set system instruction.
      """

  tools: Optional[list[ToolDict]]
  """A list of `Tools` the model may use to generate the next response.
      """

  tool_config: Optional[ToolConfigDict]
  """Configuration for the tools to use. This config is shared for all tools.
      """


CreateCachedContentConfigOrDict = Union[
    CreateCachedContentConfig, CreateCachedContentConfigDict
]


class _CreateCachedContentParameters(_common.BaseModel):
  """Parameters for caches.create method."""

  model: Optional[str] = Field(
      default=None,
      description="""ID of the model to use. Example: gemini-1.5-flash""",
  )
  contents: Optional[ContentListUnion] = Field(
      default=None,
      description="""The content to cache.
      """,
  )
  config: Optional[CreateCachedContentConfig] = Field(
      default=None,
      description="""Configuration that contains optional parameters.
      """,
  )


class _CreateCachedContentParametersDict(TypedDict, total=False):
  """Parameters for caches.create method."""

  model: Optional[str]
  """ID of the model to use. Example: gemini-1.5-flash"""

  contents: Optional[ContentListUnionDict]
  """The content to cache.
      """

  config: Optional[CreateCachedContentConfigDict]
  """Configuration that contains optional parameters.
      """


_CreateCachedContentParametersOrDict = Union[
    _CreateCachedContentParameters, _CreateCachedContentParametersDict
]


class CachedContentUsageMetadata(_common.BaseModel):
  """Metadata on the usage of the cached content."""

  audio_duration_seconds: Optional[int] = Field(
      default=None, description="""Duration of audio in seconds."""
  )
  image_count: Optional[int] = Field(
      default=None, description="""Number of images."""
  )
  text_count: Optional[int] = Field(
      default=None, description="""Number of text characters."""
  )
  total_token_count: Optional[int] = Field(
      default=None,
      description="""Total number of tokens that the cached content consumes.""",
  )
  video_duration_seconds: Optional[int] = Field(
      default=None, description="""Duration of video in seconds."""
  )


class CachedContentUsageMetadataDict(TypedDict, total=False):
  """Metadata on the usage of the cached content."""

  audio_duration_seconds: Optional[int]
  """Duration of audio in seconds."""

  image_count: Optional[int]
  """Number of images."""

  text_count: Optional[int]
  """Number of text characters."""

  total_token_count: Optional[int]
  """Total number of tokens that the cached content consumes."""

  video_duration_seconds: Optional[int]
  """Duration of video in seconds."""


CachedContentUsageMetadataOrDict = Union[
    CachedContentUsageMetadata, CachedContentUsageMetadataDict
]


class CachedContent(_common.BaseModel):
  """A resource used in LLM queries for users to explicitly specify what to cache."""

  name: Optional[str] = Field(
      default=None,
      description="""The server-generated resource name of the cached content.""",
  )
  display_name: Optional[str] = Field(
      default=None,
      description="""The user-generated meaningful display name of the cached content.""",
  )
  model: Optional[str] = Field(
      default=None,
      description="""The name of the publisher model to use for cached content.""",
  )
  create_time: Optional[datetime.datetime] = Field(
      default=None, description="""Creatation time of the cache entry."""
  )
  update_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""When the cache entry was last updated in UTC time.""",
  )
  expire_time: Optional[datetime.datetime] = Field(
      default=None, description="""Expiration time of the cached content."""
  )
  usage_metadata: Optional[CachedContentUsageMetadata] = Field(
      default=None,
      description="""Metadata on the usage of the cached content.""",
  )


class CachedContentDict(TypedDict, total=False):
  """A resource used in LLM queries for users to explicitly specify what to cache."""

  name: Optional[str]
  """The server-generated resource name of the cached content."""

  display_name: Optional[str]
  """The user-generated meaningful display name of the cached content."""

  model: Optional[str]
  """The name of the publisher model to use for cached content."""

  create_time: Optional[datetime.datetime]
  """Creatation time of the cache entry."""

  update_time: Optional[datetime.datetime]
  """When the cache entry was last updated in UTC time."""

  expire_time: Optional[datetime.datetime]
  """Expiration time of the cached content."""

  usage_metadata: Optional[CachedContentUsageMetadataDict]
  """Metadata on the usage of the cached content."""


CachedContentOrDict = Union[CachedContent, CachedContentDict]


class GetCachedContentConfig(_common.BaseModel):
  """Optional parameters for caches.get method."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )


class GetCachedContentConfigDict(TypedDict, total=False):
  """Optional parameters for caches.get method."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""


GetCachedContentConfigOrDict = Union[
    GetCachedContentConfig, GetCachedContentConfigDict
]


class _GetCachedContentParameters(_common.BaseModel):
  """Parameters for caches.get method."""

  name: Optional[str] = Field(
      default=None,
      description="""The server-generated resource name of the cached content.
      """,
  )
  config: Optional[GetCachedContentConfig] = Field(
      default=None,
      description="""Optional parameters for the request.
      """,
  )


class _GetCachedContentParametersDict(TypedDict, total=False):
  """Parameters for caches.get method."""

  name: Optional[str]
  """The server-generated resource name of the cached content.
      """

  config: Optional[GetCachedContentConfigDict]
  """Optional parameters for the request.
      """


_GetCachedContentParametersOrDict = Union[
    _GetCachedContentParameters, _GetCachedContentParametersDict
]


class DeleteCachedContentConfig(_common.BaseModel):
  """Optional parameters for caches.delete method."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )


class DeleteCachedContentConfigDict(TypedDict, total=False):
  """Optional parameters for caches.delete method."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""


DeleteCachedContentConfigOrDict = Union[
    DeleteCachedContentConfig, DeleteCachedContentConfigDict
]


class _DeleteCachedContentParameters(_common.BaseModel):
  """Parameters for caches.delete method."""

  name: Optional[str] = Field(
      default=None,
      description="""The server-generated resource name of the cached content.
      """,
  )
  config: Optional[DeleteCachedContentConfig] = Field(
      default=None,
      description="""Optional parameters for the request.
      """,
  )


class _DeleteCachedContentParametersDict(TypedDict, total=False):
  """Parameters for caches.delete method."""

  name: Optional[str]
  """The server-generated resource name of the cached content.
      """

  config: Optional[DeleteCachedContentConfigDict]
  """Optional parameters for the request.
      """


_DeleteCachedContentParametersOrDict = Union[
    _DeleteCachedContentParameters, _DeleteCachedContentParametersDict
]


class DeleteCachedContentResponse(_common.BaseModel):
  """Empty response for caches.delete method."""

  pass


class DeleteCachedContentResponseDict(TypedDict, total=False):
  """Empty response for caches.delete method."""

  pass


DeleteCachedContentResponseOrDict = Union[
    DeleteCachedContentResponse, DeleteCachedContentResponseDict
]


class UpdateCachedContentConfig(_common.BaseModel):
  """Optional parameters for caches.update method."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  ttl: Optional[str] = Field(
      default=None,
      description="""The TTL for this resource. The expiration time is computed: now + TTL.""",
  )
  expire_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Timestamp of when this resource is considered expired.""",
  )


class UpdateCachedContentConfigDict(TypedDict, total=False):
  """Optional parameters for caches.update method."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  ttl: Optional[str]
  """The TTL for this resource. The expiration time is computed: now + TTL."""

  expire_time: Optional[datetime.datetime]
  """Timestamp of when this resource is considered expired."""


UpdateCachedContentConfigOrDict = Union[
    UpdateCachedContentConfig, UpdateCachedContentConfigDict
]


class _UpdateCachedContentParameters(_common.BaseModel):

  name: Optional[str] = Field(
      default=None,
      description="""The server-generated resource name of the cached content.
      """,
  )
  config: Optional[UpdateCachedContentConfig] = Field(
      default=None,
      description="""Configuration that contains optional parameters.
      """,
  )


class _UpdateCachedContentParametersDict(TypedDict, total=False):

  name: Optional[str]
  """The server-generated resource name of the cached content.
      """

  config: Optional[UpdateCachedContentConfigDict]
  """Configuration that contains optional parameters.
      """


_UpdateCachedContentParametersOrDict = Union[
    _UpdateCachedContentParameters, _UpdateCachedContentParametersDict
]


class ListCachedContentsConfig(_common.BaseModel):
  """Config for caches.list method."""

  page_size: Optional[int] = Field(default=None, description="""""")
  page_token: Optional[str] = Field(default=None, description="""""")


class ListCachedContentsConfigDict(TypedDict, total=False):
  """Config for caches.list method."""

  page_size: Optional[int]
  """"""

  page_token: Optional[str]
  """"""


ListCachedContentsConfigOrDict = Union[
    ListCachedContentsConfig, ListCachedContentsConfigDict
]


class _ListCachedContentsParameters(_common.BaseModel):
  """Parameters for caches.list method."""

  config: Optional[ListCachedContentsConfig] = Field(
      default=None,
      description="""Configuration that contains optional parameters.
      """,
  )


class _ListCachedContentsParametersDict(TypedDict, total=False):
  """Parameters for caches.list method."""

  config: Optional[ListCachedContentsConfigDict]
  """Configuration that contains optional parameters.
      """


_ListCachedContentsParametersOrDict = Union[
    _ListCachedContentsParameters, _ListCachedContentsParametersDict
]


class ListCachedContentsResponse(_common.BaseModel):

  next_page_token: Optional[str] = Field(default=None, description="""""")
  cached_contents: Optional[list[CachedContent]] = Field(
      default=None,
      description="""List of cached contents.
      """,
  )


class ListCachedContentsResponseDict(TypedDict, total=False):

  next_page_token: Optional[str]
  """"""

  cached_contents: Optional[list[CachedContentDict]]
  """List of cached contents.
      """


ListCachedContentsResponseOrDict = Union[
    ListCachedContentsResponse, ListCachedContentsResponseDict
]


class ListFilesConfig(_common.BaseModel):
  """Used to override the default configuration."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  page_size: Optional[int] = Field(default=None, description="""""")
  page_token: Optional[str] = Field(default=None, description="""""")


class ListFilesConfigDict(TypedDict, total=False):
  """Used to override the default configuration."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  page_size: Optional[int]
  """"""

  page_token: Optional[str]
  """"""


ListFilesConfigOrDict = Union[ListFilesConfig, ListFilesConfigDict]


class _ListFilesParameters(_common.BaseModel):
  """Generates the parameters for the list method."""

  config: Optional[ListFilesConfig] = Field(
      default=None,
      description="""Used to override the default configuration.""",
  )


class _ListFilesParametersDict(TypedDict, total=False):
  """Generates the parameters for the list method."""

  config: Optional[ListFilesConfigDict]
  """Used to override the default configuration."""


_ListFilesParametersOrDict = Union[
    _ListFilesParameters, _ListFilesParametersDict
]


class FileStatus(_common.BaseModel):
  """Status of a File that uses a common error model."""

  details: Optional[list[dict[str, Any]]] = Field(
      default=None,
      description="""A list of messages that carry the error details. There is a common set of message types for APIs to use.""",
  )
  message: Optional[str] = Field(
      default=None,
      description="""A list of messages that carry the error details. There is a common set of message types for APIs to use.""",
  )
  code: Optional[int] = Field(
      default=None, description="""The status code. 0 for OK, 1 for CANCELLED"""
  )


class FileStatusDict(TypedDict, total=False):
  """Status of a File that uses a common error model."""

  details: Optional[list[dict[str, Any]]]
  """A list of messages that carry the error details. There is a common set of message types for APIs to use."""

  message: Optional[str]
  """A list of messages that carry the error details. There is a common set of message types for APIs to use."""

  code: Optional[int]
  """The status code. 0 for OK, 1 for CANCELLED"""


FileStatusOrDict = Union[FileStatus, FileStatusDict]


class File(_common.BaseModel):
  """A file uploaded to the API."""

  name: Optional[str] = Field(
      default=None,
      description="""The `File` resource name. The ID (name excluding the "files/" prefix) can contain up to 40 characters that are lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If the name is empty on create, a unique name will be generated. Example: `files/123-456`""",
  )
  display_name: Optional[str] = Field(
      default=None,
      description="""Optional. The human-readable display name for the `File`. The display name must be no more than 512 characters in length, including spaces. Example: 'Welcome Image'""",
  )
  mime_type: Optional[str] = Field(
      default=None, description="""Output only. MIME type of the file."""
  )
  size_bytes: Optional[int] = Field(
      default=None, description="""Output only. Size of the file in bytes."""
  )
  create_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Output only. The timestamp of when the `File` was created.""",
  )
  expiration_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Optional. The human-readable display name for the `File`. The display name must be no more than 512 characters in length, including spaces. Example: 'Welcome Image'""",
  )
  update_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Output only. The timestamp of when the `File` was last updated.""",
  )
  sha256_hash: Optional[bytes] = Field(
      default=None,
      description="""Output only. SHA-256 hash of the uploaded bytes.""",
  )
  uri: Optional[str] = Field(
      default=None, description="""Output only. The URI of the `File`."""
  )
  state: Optional[FileState] = Field(
      default=None, description="""Output only. Processing state of the File."""
  )
  video_metadata: Optional[dict[str, Any]] = Field(
      default=None, description="""Output only. Metadata for a video."""
  )
  error: Optional[FileStatus] = Field(
      default=None,
      description="""Output only. Error status if File processing failed.""",
  )


class FileDict(TypedDict, total=False):
  """A file uploaded to the API."""

  name: Optional[str]
  """The `File` resource name. The ID (name excluding the "files/" prefix) can contain up to 40 characters that are lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If the name is empty on create, a unique name will be generated. Example: `files/123-456`"""

  display_name: Optional[str]
  """Optional. The human-readable display name for the `File`. The display name must be no more than 512 characters in length, including spaces. Example: 'Welcome Image'"""

  mime_type: Optional[str]
  """Output only. MIME type of the file."""

  size_bytes: Optional[int]
  """Output only. Size of the file in bytes."""

  create_time: Optional[datetime.datetime]
  """Output only. The timestamp of when the `File` was created."""

  expiration_time: Optional[datetime.datetime]
  """Optional. The human-readable display name for the `File`. The display name must be no more than 512 characters in length, including spaces. Example: 'Welcome Image'"""

  update_time: Optional[datetime.datetime]
  """Output only. The timestamp of when the `File` was last updated."""

  sha256_hash: Optional[bytes]
  """Output only. SHA-256 hash of the uploaded bytes."""

  uri: Optional[str]
  """Output only. The URI of the `File`."""

  state: Optional[FileState]
  """Output only. Processing state of the File."""

  video_metadata: Optional[dict[str, Any]]
  """Output only. Metadata for a video."""

  error: Optional[FileStatusDict]
  """Output only. Error status if File processing failed."""


FileOrDict = Union[File, FileDict]


class ListFilesResponse(_common.BaseModel):
  """Response for the list files method."""

  next_page_token: Optional[str] = Field(
      default=None, description="""A token to retrieve next page of results."""
  )
  files: Optional[list[File]] = Field(
      default=None, description="""The list of files."""
  )


class ListFilesResponseDict(TypedDict, total=False):
  """Response for the list files method."""

  next_page_token: Optional[str]
  """A token to retrieve next page of results."""

  files: Optional[list[FileDict]]
  """The list of files."""


ListFilesResponseOrDict = Union[ListFilesResponse, ListFilesResponseDict]


class CreateFileConfig(_common.BaseModel):
  """Used to override the default configuration."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )


class CreateFileConfigDict(TypedDict, total=False):
  """Used to override the default configuration."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""


CreateFileConfigOrDict = Union[CreateFileConfig, CreateFileConfigDict]


class _CreateFileParameters(_common.BaseModel):
  """Generates the parameters for the private _create method."""

  file: Optional[File] = Field(
      default=None,
      description="""The file to be uploaded.
            mime_type: (Required) The MIME type of the file. Must be provided.
            name: (Optional) The name of the file in the destination (e.g.
            'files/sample-image').
            display_name: (Optional) The display name of the file.
      """,
  )
  config: Optional[CreateFileConfig] = Field(
      default=None,
      description="""Used to override the default configuration.""",
  )


class _CreateFileParametersDict(TypedDict, total=False):
  """Generates the parameters for the private _create method."""

  file: Optional[FileDict]
  """The file to be uploaded.
            mime_type: (Required) The MIME type of the file. Must be provided.
            name: (Optional) The name of the file in the destination (e.g.
            'files/sample-image').
            display_name: (Optional) The display name of the file.
      """

  config: Optional[CreateFileConfigDict]
  """Used to override the default configuration."""


_CreateFileParametersOrDict = Union[
    _CreateFileParameters, _CreateFileParametersDict
]


class CreateFileResponse(_common.BaseModel):
  """Response for the create file method."""

  pass


class CreateFileResponseDict(TypedDict, total=False):
  """Response for the create file method."""

  pass


CreateFileResponseOrDict = Union[CreateFileResponse, CreateFileResponseDict]


class GetFileConfig(_common.BaseModel):
  """Used to override the default configuration."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )


class GetFileConfigDict(TypedDict, total=False):
  """Used to override the default configuration."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""


GetFileConfigOrDict = Union[GetFileConfig, GetFileConfigDict]


class _GetFileParameters(_common.BaseModel):
  """Generates the parameters for the get method."""

  name: Optional[str] = Field(
      default=None,
      description="""The name identifier for the file to retrieve.""",
  )
  config: Optional[GetFileConfig] = Field(
      default=None,
      description="""Used to override the default configuration.""",
  )


class _GetFileParametersDict(TypedDict, total=False):
  """Generates the parameters for the get method."""

  name: Optional[str]
  """The name identifier for the file to retrieve."""

  config: Optional[GetFileConfigDict]
  """Used to override the default configuration."""


_GetFileParametersOrDict = Union[_GetFileParameters, _GetFileParametersDict]


class DeleteFileConfig(_common.BaseModel):
  """Used to override the default configuration."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )


class DeleteFileConfigDict(TypedDict, total=False):
  """Used to override the default configuration."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""


DeleteFileConfigOrDict = Union[DeleteFileConfig, DeleteFileConfigDict]


class _DeleteFileParameters(_common.BaseModel):
  """Generates the parameters for the get method."""

  name: Optional[str] = Field(
      default=None,
      description="""The name identifier for the file to be deleted.""",
  )
  config: Optional[DeleteFileConfig] = Field(
      default=None,
      description="""Used to override the default configuration.""",
  )


class _DeleteFileParametersDict(TypedDict, total=False):
  """Generates the parameters for the get method."""

  name: Optional[str]
  """The name identifier for the file to be deleted."""

  config: Optional[DeleteFileConfigDict]
  """Used to override the default configuration."""


_DeleteFileParametersOrDict = Union[
    _DeleteFileParameters, _DeleteFileParametersDict
]


class DeleteFileResponse(_common.BaseModel):
  """Response for the delete file method."""

  pass


class DeleteFileResponseDict(TypedDict, total=False):
  """Response for the delete file method."""

  pass


DeleteFileResponseOrDict = Union[DeleteFileResponse, DeleteFileResponseDict]


class BatchJobSource(_common.BaseModel):
  """Config class for `src` parameter."""

  format: Optional[str] = Field(
      default=None,
      description="""Storage format of the input files. Must be one of:
      'jsonl', 'bigquery'.
      """,
  )
  gcs_uri: Optional[list[str]] = Field(
      default=None,
      description="""The Google Cloud Storage URIs to input files.
      """,
  )
  bigquery_uri: Optional[str] = Field(
      default=None,
      description="""The BigQuery URI to input table.
      """,
  )


class BatchJobSourceDict(TypedDict, total=False):
  """Config class for `src` parameter."""

  format: Optional[str]
  """Storage format of the input files. Must be one of:
      'jsonl', 'bigquery'.
      """

  gcs_uri: Optional[list[str]]
  """The Google Cloud Storage URIs to input files.
      """

  bigquery_uri: Optional[str]
  """The BigQuery URI to input table.
      """


BatchJobSourceOrDict = Union[BatchJobSource, BatchJobSourceDict]


class BatchJobDestination(_common.BaseModel):
  """Config class for `des` parameter."""

  format: Optional[str] = Field(
      default=None,
      description="""Storage format of the output files. Must be one of:
      'jsonl', 'bigquery'.
      """,
  )
  gcs_uri: Optional[str] = Field(
      default=None,
      description="""The Google Cloud Storage URI to the output file.
      """,
  )
  bigquery_uri: Optional[str] = Field(
      default=None,
      description="""The BigQuery URI to the output table.
      """,
  )


class BatchJobDestinationDict(TypedDict, total=False):
  """Config class for `des` parameter."""

  format: Optional[str]
  """Storage format of the output files. Must be one of:
      'jsonl', 'bigquery'.
      """

  gcs_uri: Optional[str]
  """The Google Cloud Storage URI to the output file.
      """

  bigquery_uri: Optional[str]
  """The BigQuery URI to the output table.
      """


BatchJobDestinationOrDict = Union[BatchJobDestination, BatchJobDestinationDict]


class CreateBatchJobConfig(_common.BaseModel):
  """Config class for optional parameters."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  display_name: Optional[str] = Field(
      default=None,
      description="""The user-defined name of this BatchJob.
      """,
  )
  dest: Optional[str] = Field(
      default=None,
      description="""GCS or Bigquery URI prefix for the output predictions. Example:
      "gs://path/to/output/data" or "bq://projectId.bqDatasetId.bqTableId".
      """,
  )


class CreateBatchJobConfigDict(TypedDict, total=False):
  """Config class for optional parameters."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  display_name: Optional[str]
  """The user-defined name of this BatchJob.
      """

  dest: Optional[str]
  """GCS or Bigquery URI prefix for the output predictions. Example:
      "gs://path/to/output/data" or "bq://projectId.bqDatasetId.bqTableId".
      """


CreateBatchJobConfigOrDict = Union[
    CreateBatchJobConfig, CreateBatchJobConfigDict
]


class _CreateBatchJobParameters(_common.BaseModel):
  """Config class for batches.create parameters."""

  model: Optional[str] = Field(
      default=None,
      description="""The name of the model to produces the predictions via the BatchJob.
      """,
  )
  src: Optional[str] = Field(
      default=None,
      description="""GCS URI(-s) or Bigquery URI to your input data to run batch job.
      Example: "gs://path/to/input/data" or "bq://projectId.bqDatasetId.bqTableId".
      """,
  )
  config: Optional[CreateBatchJobConfig] = Field(
      default=None,
      description="""Optional parameters for creating a BatchJob.
      """,
  )


class _CreateBatchJobParametersDict(TypedDict, total=False):
  """Config class for batches.create parameters."""

  model: Optional[str]
  """The name of the model to produces the predictions via the BatchJob.
      """

  src: Optional[str]
  """GCS URI(-s) or Bigquery URI to your input data to run batch job.
      Example: "gs://path/to/input/data" or "bq://projectId.bqDatasetId.bqTableId".
      """

  config: Optional[CreateBatchJobConfigDict]
  """Optional parameters for creating a BatchJob.
      """


_CreateBatchJobParametersOrDict = Union[
    _CreateBatchJobParameters, _CreateBatchJobParametersDict
]


class JobError(_common.BaseModel):
  """Config class for the job error."""

  details: Optional[list[str]] = Field(
      default=None,
      description="""A list of messages that carry the error details. There is a common set of message types for APIs to use.""",
  )
  code: Optional[int] = Field(default=None, description="""The status code.""")
  message: Optional[str] = Field(
      default=None,
      description="""A developer-facing error message, which should be in English. Any user-facing error message should be localized and sent in the `details` field.""",
  )


class JobErrorDict(TypedDict, total=False):
  """Config class for the job error."""

  details: Optional[list[str]]
  """A list of messages that carry the error details. There is a common set of message types for APIs to use."""

  code: Optional[int]
  """The status code."""

  message: Optional[str]
  """A developer-facing error message, which should be in English. Any user-facing error message should be localized and sent in the `details` field."""


JobErrorOrDict = Union[JobError, JobErrorDict]


class BatchJob(_common.BaseModel):
  """Config class for batches.create return value."""

  name: Optional[str] = Field(
      default=None, description="""Output only. Resource name of the Job."""
  )
  display_name: Optional[str] = Field(
      default=None, description="""The user-defined name of this Job."""
  )
  state: Optional[JobState] = Field(
      default=None,
      description="""Output only. The detailed state of the job.""",
  )
  error: Optional[JobError] = Field(
      default=None,
      description="""Output only. Only populated when the job's state is JOB_STATE_FAILED or JOB_STATE_CANCELLED.""",
  )
  create_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Output only. Time when the Job was created.""",
  )
  start_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Output only. Time when the Job for the first time entered the `JOB_STATE_RUNNING` state.""",
  )
  end_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Output only. Time when the Job entered any of the following states: `JOB_STATE_SUCCEEDED`, `JOB_STATE_FAILED`, `JOB_STATE_CANCELLED`.""",
  )
  update_time: Optional[datetime.datetime] = Field(
      default=None,
      description="""Output only. Time when the Job was most recently updated.""",
  )
  model: Optional[str] = Field(
      default=None,
      description="""The name of the model that produces the predictions via the BatchJob.
      """,
  )
  src: Optional[BatchJobSource] = Field(
      default=None,
      description="""Configuration for the input data.
      """,
  )
  dest: Optional[BatchJobDestination] = Field(
      default=None,
      description="""Configuration for the output data.
      """,
  )


class BatchJobDict(TypedDict, total=False):
  """Config class for batches.create return value."""

  name: Optional[str]
  """Output only. Resource name of the Job."""

  display_name: Optional[str]
  """The user-defined name of this Job."""

  state: Optional[JobState]
  """Output only. The detailed state of the job."""

  error: Optional[JobErrorDict]
  """Output only. Only populated when the job's state is JOB_STATE_FAILED or JOB_STATE_CANCELLED."""

  create_time: Optional[datetime.datetime]
  """Output only. Time when the Job was created."""

  start_time: Optional[datetime.datetime]
  """Output only. Time when the Job for the first time entered the `JOB_STATE_RUNNING` state."""

  end_time: Optional[datetime.datetime]
  """Output only. Time when the Job entered any of the following states: `JOB_STATE_SUCCEEDED`, `JOB_STATE_FAILED`, `JOB_STATE_CANCELLED`."""

  update_time: Optional[datetime.datetime]
  """Output only. Time when the Job was most recently updated."""

  model: Optional[str]
  """The name of the model that produces the predictions via the BatchJob.
      """

  src: Optional[BatchJobSourceDict]
  """Configuration for the input data.
      """

  dest: Optional[BatchJobDestinationDict]
  """Configuration for the output data.
      """


BatchJobOrDict = Union[BatchJob, BatchJobDict]


class GetBatchJobConfig(_common.BaseModel):
  """Optional parameters."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )


class GetBatchJobConfigDict(TypedDict, total=False):
  """Optional parameters."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""


GetBatchJobConfigOrDict = Union[GetBatchJobConfig, GetBatchJobConfigDict]


class _GetBatchJobParameters(_common.BaseModel):
  """Config class for batches.get parameters."""

  name: Optional[str] = Field(
      default=None,
      description="""A fully-qualified BatchJob resource name or ID.
    Example: "projects/.../locations/.../batchPredictionJobs/456"
    or "456" when project and location are initialized in the client.
    """,
  )
  config: Optional[GetBatchJobConfig] = Field(
      default=None, description="""Optional parameters for the request."""
  )


class _GetBatchJobParametersDict(TypedDict, total=False):
  """Config class for batches.get parameters."""

  name: Optional[str]
  """A fully-qualified BatchJob resource name or ID.
    Example: "projects/.../locations/.../batchPredictionJobs/456"
    or "456" when project and location are initialized in the client.
    """

  config: Optional[GetBatchJobConfigDict]
  """Optional parameters for the request."""


_GetBatchJobParametersOrDict = Union[
    _GetBatchJobParameters, _GetBatchJobParametersDict
]


class CancelBatchJobConfig(_common.BaseModel):
  """Optional parameters."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )


class CancelBatchJobConfigDict(TypedDict, total=False):
  """Optional parameters."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""


CancelBatchJobConfigOrDict = Union[
    CancelBatchJobConfig, CancelBatchJobConfigDict
]


class _CancelBatchJobParameters(_common.BaseModel):
  """Config class for batches.cancel parameters."""

  name: Optional[str] = Field(
      default=None,
      description="""A fully-qualified BatchJob resource name or ID.
    Example: "projects/.../locations/.../batchPredictionJobs/456"
    or "456" when project and location are initialized in the client.
    """,
  )
  config: Optional[CancelBatchJobConfig] = Field(
      default=None, description="""Optional parameters for the request."""
  )


class _CancelBatchJobParametersDict(TypedDict, total=False):
  """Config class for batches.cancel parameters."""

  name: Optional[str]
  """A fully-qualified BatchJob resource name or ID.
    Example: "projects/.../locations/.../batchPredictionJobs/456"
    or "456" when project and location are initialized in the client.
    """

  config: Optional[CancelBatchJobConfigDict]
  """Optional parameters for the request."""


_CancelBatchJobParametersOrDict = Union[
    _CancelBatchJobParameters, _CancelBatchJobParametersDict
]


class ListBatchJobConfig(_common.BaseModel):
  """Config class for optional parameters."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  page_size: Optional[int] = Field(default=None, description="""""")
  page_token: Optional[str] = Field(default=None, description="""""")
  filter: Optional[str] = Field(default=None, description="""""")


class ListBatchJobConfigDict(TypedDict, total=False):
  """Config class for optional parameters."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  page_size: Optional[int]
  """"""

  page_token: Optional[str]
  """"""

  filter: Optional[str]
  """"""


ListBatchJobConfigOrDict = Union[ListBatchJobConfig, ListBatchJobConfigDict]


class _ListBatchJobParameters(_common.BaseModel):
  """Config class for batches.list parameters."""

  config: Optional[ListBatchJobConfig] = Field(default=None, description="""""")


class _ListBatchJobParametersDict(TypedDict, total=False):
  """Config class for batches.list parameters."""

  config: Optional[ListBatchJobConfigDict]
  """"""


_ListBatchJobParametersOrDict = Union[
    _ListBatchJobParameters, _ListBatchJobParametersDict
]


class ListBatchJobResponse(_common.BaseModel):
  """Config class for batches.list return value."""

  next_page_token: Optional[str] = Field(default=None, description="""""")
  batch_jobs: Optional[list[BatchJob]] = Field(default=None, description="""""")


class ListBatchJobResponseDict(TypedDict, total=False):
  """Config class for batches.list return value."""

  next_page_token: Optional[str]
  """"""

  batch_jobs: Optional[list[BatchJobDict]]
  """"""


ListBatchJobResponseOrDict = Union[
    ListBatchJobResponse, ListBatchJobResponseDict
]


class _DeleteBatchJobParameters(_common.BaseModel):
  """Config class for batches.delete parameters."""

  name: Optional[str] = Field(
      default=None,
      description="""A fully-qualified BatchJob resource name or ID.
    Example: "projects/.../locations/.../batchPredictionJobs/456"
    or "456" when project and location are initialized in the client.
    """,
  )


class _DeleteBatchJobParametersDict(TypedDict, total=False):
  """Config class for batches.delete parameters."""

  name: Optional[str]
  """A fully-qualified BatchJob resource name or ID.
    Example: "projects/.../locations/.../batchPredictionJobs/456"
    or "456" when project and location are initialized in the client.
    """


_DeleteBatchJobParametersOrDict = Union[
    _DeleteBatchJobParameters, _DeleteBatchJobParametersDict
]


class DeleteResourceJob(_common.BaseModel):
  """Config class for the return value of delete operation."""

  name: Optional[str] = Field(default=None, description="""""")
  done: Optional[bool] = Field(default=None, description="""""")
  error: Optional[JobError] = Field(default=None, description="""""")


class DeleteResourceJobDict(TypedDict, total=False):
  """Config class for the return value of delete operation."""

  name: Optional[str]
  """"""

  done: Optional[bool]
  """"""

  error: Optional[JobErrorDict]
  """"""


DeleteResourceJobOrDict = Union[DeleteResourceJob, DeleteResourceJobDict]


class TestTableItem(_common.BaseModel):

  name: Optional[str] = Field(
      default=None,
      description="""The name of the test. This is used to derive the replay id.""",
  )
  parameters: Optional[dict[str, Any]] = Field(
      default=None,
      description="""The parameters to the test. Use pydantic models.""",
  )
  exception_if_mldev: Optional[str] = Field(
      default=None,
      description="""Expects an exception for MLDev matching the string.""",
  )
  exception_if_vertex: Optional[str] = Field(
      default=None,
      description="""Expects an exception for Vertex matching the string.""",
  )
  override_replay_id: Optional[str] = Field(
      default=None,
      description="""Use if you don't want to use the default replay id which is derived from the test name.""",
  )
  has_union: Optional[bool] = Field(
      default=None,
      description="""True if the parameters contain an unsupported union type. This test  will be skipped for languages that do not support the union type.""",
  )
  skip_in_api_mode: Optional[str] = Field(
      default=None,
      description="""When set to a reason string, this test will be skipped in the API mode. Use this flag for tests that can not be reproduced with the real API. E.g. a test that deletes a resource.""",
  )


class TestTableItemDict(TypedDict, total=False):

  name: Optional[str]
  """The name of the test. This is used to derive the replay id."""

  parameters: Optional[dict[str, Any]]
  """The parameters to the test. Use pydantic models."""

  exception_if_mldev: Optional[str]
  """Expects an exception for MLDev matching the string."""

  exception_if_vertex: Optional[str]
  """Expects an exception for Vertex matching the string."""

  override_replay_id: Optional[str]
  """Use if you don't want to use the default replay id which is derived from the test name."""

  has_union: Optional[bool]
  """True if the parameters contain an unsupported union type. This test  will be skipped for languages that do not support the union type."""

  skip_in_api_mode: Optional[str]
  """When set to a reason string, this test will be skipped in the API mode. Use this flag for tests that can not be reproduced with the real API. E.g. a test that deletes a resource."""


TestTableItemOrDict = Union[TestTableItem, TestTableItemDict]


class TestTableFile(_common.BaseModel):

  comment: Optional[str] = Field(default=None, description="""""")
  test_method: Optional[str] = Field(default=None, description="""""")
  parameter_names: Optional[list[str]] = Field(default=None, description="""""")
  test_table: Optional[list[TestTableItem]] = Field(
      default=None, description=""""""
  )


class TestTableFileDict(TypedDict, total=False):

  comment: Optional[str]
  """"""

  test_method: Optional[str]
  """"""

  parameter_names: Optional[list[str]]
  """"""

  test_table: Optional[list[TestTableItemDict]]
  """"""


TestTableFileOrDict = Union[TestTableFile, TestTableFileDict]


class ReplayRequest(_common.BaseModel):
  """Represents a single request in a replay."""

  method: Optional[str] = Field(default=None, description="""""")
  url: Optional[str] = Field(default=None, description="""""")
  headers: Optional[dict[str, str]] = Field(default=None, description="""""")
  body_segments: Optional[list[dict[str, Any]]] = Field(
      default=None, description=""""""
  )


class ReplayRequestDict(TypedDict, total=False):
  """Represents a single request in a replay."""

  method: Optional[str]
  """"""

  url: Optional[str]
  """"""

  headers: Optional[dict[str, str]]
  """"""

  body_segments: Optional[list[dict[str, Any]]]
  """"""


ReplayRequestOrDict = Union[ReplayRequest, ReplayRequestDict]


class ReplayResponse(_common.BaseModel):
  """Represents a single response in a replay."""

  status_code: Optional[int] = Field(default=None, description="""""")
  headers: Optional[dict[str, str]] = Field(default=None, description="""""")
  body_segments: Optional[list[dict[str, Any]]] = Field(
      default=None, description=""""""
  )
  sdk_response_segments: Optional[list[dict[str, Any]]] = Field(
      default=None, description=""""""
  )


class ReplayResponseDict(TypedDict, total=False):
  """Represents a single response in a replay."""

  status_code: Optional[int]
  """"""

  headers: Optional[dict[str, str]]
  """"""

  body_segments: Optional[list[dict[str, Any]]]
  """"""

  sdk_response_segments: Optional[list[dict[str, Any]]]
  """"""


ReplayResponseOrDict = Union[ReplayResponse, ReplayResponseDict]


class ReplayInteraction(_common.BaseModel):
  """Represents a single interaction, request and response in a replay."""

  request: Optional[ReplayRequest] = Field(default=None, description="""""")
  response: Optional[ReplayResponse] = Field(default=None, description="""""")


class ReplayInteractionDict(TypedDict, total=False):
  """Represents a single interaction, request and response in a replay."""

  request: Optional[ReplayRequestDict]
  """"""

  response: Optional[ReplayResponseDict]
  """"""


ReplayInteractionOrDict = Union[ReplayInteraction, ReplayInteractionDict]


class ReplayFile(_common.BaseModel):
  """Represents a recorded session."""

  replay_id: Optional[str] = Field(default=None, description="""""")
  interactions: Optional[list[ReplayInteraction]] = Field(
      default=None, description=""""""
  )


class ReplayFileDict(TypedDict, total=False):
  """Represents a recorded session."""

  replay_id: Optional[str]
  """"""

  interactions: Optional[list[ReplayInteractionDict]]
  """"""


ReplayFileOrDict = Union[ReplayFile, ReplayFileDict]


class UploadFileConfig(_common.BaseModel):
  """Used to override the default configuration."""

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  name: Optional[str] = Field(
      default=None,
      description="""The name of the file in the destination (e.g., 'files/sample-image'. If not provided one will be generated.""",
  )
  mime_type: Optional[str] = Field(
      default=None,
      description="""mime_type: The MIME type of the file. If not provided, it will be inferred from the file extension.""",
  )
  display_name: Optional[str] = Field(
      default=None, description="""Optional display name of the file."""
  )


class UploadFileConfigDict(TypedDict, total=False):
  """Used to override the default configuration."""

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  name: Optional[str]
  """The name of the file in the destination (e.g., 'files/sample-image'. If not provided one will be generated."""

  mime_type: Optional[str]
  """mime_type: The MIME type of the file. If not provided, it will be inferred from the file extension."""

  display_name: Optional[str]
  """Optional display name of the file."""


UploadFileConfigOrDict = Union[UploadFileConfig, UploadFileConfigDict]


class UpscaleImageConfig(_common.BaseModel):
  """Configuration for upscaling an image.

  For more information on this configuration, refer to
  the `Imagen API reference documentation
  <https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api>`_.
  """

  http_options: Optional[dict[str, Any]] = Field(
      default=None, description="""Used to override HTTP request options."""
  )
  upscale_factor: Optional[str] = Field(
      default=None,
      description="""The factor to which the image will be upscaled.""",
  )
  include_rai_reason: Optional[bool] = Field(
      default=None,
      description="""Whether to include a reason for filtered-out images in the
      response.""",
  )
  output_mime_type: Optional[str] = Field(
      default=None,
      description="""The image format that the output should be saved as.""",
  )
  output_compression_quality: Optional[int] = Field(
      default=None,
      description="""The level of compression if the ``output_mime_type`` is
      ``image/jpeg``.""",
  )


class UpscaleImageConfigDict(TypedDict, total=False):
  """Configuration for upscaling an image.

  For more information on this configuration, refer to
  the `Imagen API reference documentation
  <https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api>`_.
  """

  http_options: Optional[dict[str, Any]]
  """Used to override HTTP request options."""

  upscale_factor: Optional[str]
  """The factor to which the image will be upscaled."""

  include_rai_reason: Optional[bool]
  """Whether to include a reason for filtered-out images in the
      response."""

  output_mime_type: Optional[str]
  """The image format that the output should be saved as."""

  output_compression_quality: Optional[int]
  """The level of compression if the ``output_mime_type`` is
      ``image/jpeg``."""


UpscaleImageConfigOrDict = Union[UpscaleImageConfig, UpscaleImageConfigDict]


class UpscaleImageParameters(_common.BaseModel):
  """User-facing config UpscaleImageParameters."""

  model: Optional[str] = Field(
      default=None, description="""The model to use."""
  )
  image: Optional[Image] = Field(
      default=None, description="""The input image to upscale."""
  )
  config: Optional[UpscaleImageConfig] = Field(
      default=None, description="""Configuration for upscaling."""
  )


class UpscaleImageParametersDict(TypedDict, total=False):
  """User-facing config UpscaleImageParameters."""

  model: Optional[str]
  """The model to use."""

  image: Optional[ImageDict]
  """The input image to upscale."""

  config: Optional[UpscaleImageConfigDict]
  """Configuration for upscaling."""


UpscaleImageParametersOrDict = Union[
    UpscaleImageParameters, UpscaleImageParametersDict
]


class RawReferenceImage(_common.BaseModel):
  """Class that represents a Raw reference image.

  A raw reference image represents the base image to edit, provided by the user.
  It can optionally be provided in addition to a mask reference image or
  a style reference image.
  """

  reference_image: Optional[Image] = Field(
      default=None,
      description="""The reference image for the editing operation.""",
  )
  reference_id: Optional[int] = Field(
      default=None, description="""The id of the reference image."""
  )
  reference_type: Optional[str] = Field(
      default=None, description="""The type of the reference image."""
  )

  def __init__(
      self,
      reference_image: Optional[Image] = None,
      reference_id: Optional[int] = None,
  ):
    super().__init__(
        reference_image=reference_image,
        reference_id=reference_id,
        reference_type="REFERENCE_TYPE_RAW",
    )


class RawReferenceImageDict(TypedDict, total=False):
  """Class that represents a Raw reference image.

  A raw reference image represents the base image to edit, provided by the user.
  It can optionally be provided in addition to a mask reference image or
  a style reference image.
  """

  reference_image: Optional[ImageDict]
  """The reference image for the editing operation."""

  reference_id: Optional[int]
  """The id of the reference image."""

  reference_type: Optional[str]
  """The type of the reference image."""


RawReferenceImageOrDict = Union[RawReferenceImage, RawReferenceImageDict]


class MaskReferenceImage(_common.BaseModel):
  """Class that represents a Mask reference image.

  This encapsulates either a mask image provided by the user and configs for
  the user provided mask, or only config parameters for the model to generate
  a mask.

  A mask image is an image whose non-zero values indicate where to edit the base
  image. If the user provides a mask image, the mask must be in the same
  dimensions as the raw image.
  """

  reference_image: Optional[Image] = Field(
      default=None,
      description="""The reference image for the editing operation.""",
  )
  reference_id: Optional[int] = Field(
      default=None, description="""The id of the reference image."""
  )
  reference_type: Optional[str] = Field(
      default=None, description="""The type of the reference image."""
  )
  config: Optional[MaskReferenceConfig] = Field(
      default=None,
      description="""Configuration for the mask reference image.""",
  )
  """Re-map config to mask_reference_config to send to API."""
  mask_image_config: Optional["MaskReferenceConfig"] = Field(
      default=None, description=""""""
  )

  def __init__(
      self,
      reference_image: Optional[Image] = None,
      reference_id: Optional[int] = None,
      config: Optional["MaskReferenceConfig"] = None,
  ):
    super().__init__(
        reference_image=reference_image,
        reference_id=reference_id,
        reference_type="REFERENCE_TYPE_MASK",
    )
    self.mask_image_config = config


class MaskReferenceImageDict(TypedDict, total=False):
  """Class that represents a Mask reference image.

  This encapsulates either a mask image provided by the user and configs for
  the user provided mask, or only config parameters for the model to generate
  a mask.

  A mask image is an image whose non-zero values indicate where to edit the base
  image. If the user provides a mask image, the mask must be in the same
  dimensions as the raw image.
  """

  reference_image: Optional[ImageDict]
  """The reference image for the editing operation."""

  reference_id: Optional[int]
  """The id of the reference image."""

  reference_type: Optional[str]
  """The type of the reference image."""

  config: Optional[MaskReferenceConfigDict]
  """Configuration for the mask reference image."""


MaskReferenceImageOrDict = Union[MaskReferenceImage, MaskReferenceImageDict]


class ControlReferenceImage(_common.BaseModel):
  """Class that represents a Control reference image.

  The image of the control reference image is either a control image provided
  by the user, or a regular image which the backend will use to generate a
  control image of. In the case of the latter, the
  enable_control_image_computation field in the config should be set to True.

  A control image is an image that represents a sketch image of areas for the
  model to fill in based on the prompt.
  """

  reference_image: Optional[Image] = Field(
      default=None,
      description="""The reference image for the editing operation.""",
  )
  reference_id: Optional[int] = Field(
      default=None, description="""The id of the reference image."""
  )
  reference_type: Optional[str] = Field(
      default=None, description="""The type of the reference image."""
  )
  config: Optional[ControlReferenceConfig] = Field(
      default=None,
      description="""Configuration for the control reference image.""",
  )
  """Re-map config to control_reference_config to send to API."""
  control_image_config: Optional["ControlReferenceConfig"] = Field(
      default=None, description=""""""
  )

  def __init__(
      self,
      reference_image: Optional[Image] = None,
      reference_id: Optional[int] = None,
      config: Optional["ControlReferenceConfig"] = None,
  ):
    super().__init__(
        reference_image=reference_image,
        reference_id=reference_id,
        reference_type="REFERENCE_TYPE_CONTROL",
    )
    self.control_image_config = config


class ControlReferenceImageDict(TypedDict, total=False):
  """Class that represents a Control reference image.

  The image of the control reference image is either a control image provided
  by the user, or a regular image which the backend will use to generate a
  control image of. In the case of the latter, the
  enable_control_image_computation field in the config should be set to True.

  A control image is an image that represents a sketch image of areas for the
  model to fill in based on the prompt.
  """

  reference_image: Optional[ImageDict]
  """The reference image for the editing operation."""

  reference_id: Optional[int]
  """The id of the reference image."""

  reference_type: Optional[str]
  """The type of the reference image."""

  config: Optional[ControlReferenceConfigDict]
  """Configuration for the control reference image."""


ControlReferenceImageOrDict = Union[
    ControlReferenceImage, ControlReferenceImageDict
]


class StyleReferenceImage(_common.BaseModel):
  """Class that represents a Style reference image.

  This encapsulates a style reference image provided by the user, and
  additionally optional config parameters for the style reference image.

  A raw reference image can also be provided as a destination for the style to
  be applied to.
  """

  reference_image: Optional[Image] = Field(
      default=None,
      description="""The reference image for the editing operation.""",
  )
  reference_id: Optional[int] = Field(
      default=None, description="""The id of the reference image."""
  )
  reference_type: Optional[str] = Field(
      default=None, description="""The type of the reference image."""
  )
  config: Optional[StyleReferenceConfig] = Field(
      default=None,
      description="""Configuration for the style reference image.""",
  )
  """Re-map config to style_reference_config to send to API."""
  style_image_config: Optional["StyleReferenceConfig"] = Field(
      default=None, description=""""""
  )

  def __init__(
      self,
      reference_image: Optional[Image] = None,
      reference_id: Optional[int] = None,
      config: Optional["StyleReferenceConfig"] = None,
  ):
    super().__init__(
        reference_image=reference_image,
        reference_id=reference_id,
        reference_type="REFERENCE_TYPE_STYLE",
    )
    self.style_image_config = config


class StyleReferenceImageDict(TypedDict, total=False):
  """Class that represents a Style reference image.

  This encapsulates a style reference image provided by the user, and
  additionally optional config parameters for the style reference image.

  A raw reference image can also be provided as a destination for the style to
  be applied to.
  """

  reference_image: Optional[ImageDict]
  """The reference image for the editing operation."""

  reference_id: Optional[int]
  """The id of the reference image."""

  reference_type: Optional[str]
  """The type of the reference image."""

  config: Optional[StyleReferenceConfigDict]
  """Configuration for the style reference image."""


StyleReferenceImageOrDict = Union[StyleReferenceImage, StyleReferenceImageDict]


class SubjectReferenceImage(_common.BaseModel):
  """Class that represents a Subject reference image.

  This encapsulates a subject reference image provided by the user, and
  additionally optional config parameters for the subject reference image.

  A raw reference image can also be provided as a destination for the subject to
  be applied to.
  """

  reference_image: Optional[Image] = Field(
      default=None,
      description="""The reference image for the editing operation.""",
  )
  reference_id: Optional[int] = Field(
      default=None, description="""The id of the reference image."""
  )
  reference_type: Optional[str] = Field(
      default=None, description="""The type of the reference image."""
  )
  config: Optional[SubjectReferenceConfig] = Field(
      default=None,
      description="""Configuration for the subject reference image.""",
  )
  """Re-map config to subject_reference_config to send to API."""
  subject_image_config: Optional["SubjectReferenceConfig"] = Field(
      default=None, description=""""""
  )

  def __init__(
      self,
      reference_image: Optional[Image] = None,
      reference_id: Optional[int] = None,
      config: Optional["SubjectReferenceConfig"] = None,
  ):
    super().__init__(
        reference_image=reference_image,
        reference_id=reference_id,
        reference_type="REFERENCE_TYPE_SUBJECT",
    )
    self.subject_image_config = config


class SubjectReferenceImageDict(TypedDict, total=False):
  """Class that represents a Subject reference image.

  This encapsulates a subject reference image provided by the user, and
  additionally optional config parameters for the subject reference image.

  A raw reference image can also be provided as a destination for the subject to
  be applied to.
  """

  reference_image: Optional[ImageDict]
  """The reference image for the editing operation."""

  reference_id: Optional[int]
  """The id of the reference image."""

  reference_type: Optional[str]
  """The type of the reference image."""

  config: Optional[SubjectReferenceConfigDict]
  """Configuration for the subject reference image."""


SubjectReferenceImageOrDict = Union[
    SubjectReferenceImage, SubjectReferenceImageDict
]


class LiveServerSetupComplete(_common.BaseModel):
  """Sent in response to a `LiveGenerateContentSetup` message from the client."""

  pass


class LiveServerSetupCompleteDict(TypedDict, total=False):
  """Sent in response to a `LiveGenerateContentSetup` message from the client."""

  pass


LiveServerSetupCompleteOrDict = Union[
    LiveServerSetupComplete, LiveServerSetupCompleteDict
]


class LiveServerContent(_common.BaseModel):
  """Incremental server update generated by the model in response to client messages.

  Content is generated as quickly as possible, and not in real time. Clients
  may choose to buffer and play it out in real time.
  """

  model_turn: Optional[Content] = Field(
      default=None,
      description="""The content that the model has generated as part of the current conversation with the user.""",
  )
  turn_complete: Optional[bool] = Field(
      default=None,
      description="""If true, indicates that the model is done generating. Generation will only start in response to additional client messages. Can be set alongside `content`, indicating that the `content` is the last in the turn.""",
  )
  interrupted: Optional[bool] = Field(
      default=None,
      description="""If true, indicates that a client message has interrupted current model generation. If the client is playing out the content in realtime, this is a good signal to stop and empty the current queue. If the client is playing out the content in realtime, this is a good signal to stop and empty the current playback queue.""",
  )


class LiveServerContentDict(TypedDict, total=False):
  """Incremental server update generated by the model in response to client messages.

  Content is generated as quickly as possible, and not in real time. Clients
  may choose to buffer and play it out in real time.
  """

  model_turn: Optional[ContentDict]
  """The content that the model has generated as part of the current conversation with the user."""

  turn_complete: Optional[bool]
  """If true, indicates that the model is done generating. Generation will only start in response to additional client messages. Can be set alongside `content`, indicating that the `content` is the last in the turn."""

  interrupted: Optional[bool]
  """If true, indicates that a client message has interrupted current model generation. If the client is playing out the content in realtime, this is a good signal to stop and empty the current queue. If the client is playing out the content in realtime, this is a good signal to stop and empty the current playback queue."""


LiveServerContentOrDict = Union[LiveServerContent, LiveServerContentDict]


class LiveServerToolCall(_common.BaseModel):
  """Request for the client to execute the `function_calls` and return the responses with the matching `id`s."""

  function_calls: Optional[list[FunctionCall]] = Field(
      default=None, description="""The function call to be executed."""
  )


class LiveServerToolCallDict(TypedDict, total=False):
  """Request for the client to execute the `function_calls` and return the responses with the matching `id`s."""

  function_calls: Optional[list[FunctionCallDict]]
  """The function call to be executed."""


LiveServerToolCallOrDict = Union[LiveServerToolCall, LiveServerToolCallDict]


class LiveServerToolCallCancellation(_common.BaseModel):
  """Notification for the client that a previously issued `ToolCallMessage` with the specified `id`s should have been not executed and should be cancelled.

  If there were side-effects to those tool calls, clients may attempt to undo
  the tool calls. This message occurs only in cases where the clients interrupt
  server turns.
  """

  ids: Optional[list[int]] = Field(
      default=None, description="""The ids of the tool calls to be cancelled."""
  )


class LiveServerToolCallCancellationDict(TypedDict, total=False):
  """Notification for the client that a previously issued `ToolCallMessage` with the specified `id`s should have been not executed and should be cancelled.

  If there were side-effects to those tool calls, clients may attempt to undo
  the tool calls. This message occurs only in cases where the clients interrupt
  server turns.
  """

  ids: Optional[list[int]]
  """The ids of the tool calls to be cancelled."""


LiveServerToolCallCancellationOrDict = Union[
    LiveServerToolCallCancellation, LiveServerToolCallCancellationDict
]


class LiveServerMessage(_common.BaseModel):
  """Response message for API call."""

  setup_complete: Optional[LiveServerSetupComplete] = Field(
      default=None,
      description="""Sent in response to a `LiveClientSetup` message from the client.""",
  )
  server_content: Optional[LiveServerContent] = Field(
      default=None,
      description="""Content generated by the model in response to client messages.""",
  )
  tool_call: Optional[LiveServerToolCall] = Field(
      default=None,
      description="""Request for the client to execute the `function_calls` and return the responses with the matching `id`s.""",
  )
  tool_call_cancellation: Optional[LiveServerToolCallCancellation] = Field(
      default=None,
      description="""Notification for the client that a previously issued `ToolCallMessage` with the specified `id`s should have been not executed and should be cancelled.""",
  )

  @property
  def text(self) -> Optional[str]:
    """Returns the concatenation of all text parts in the response."""
    if (
        not self.server_content
        or not self.server_content
        or not self.server_content.model_turn
        or not self.server_content.model_turn.parts
    ):
      return None
    text = ""
    for part in self.server_content.model_turn.parts:
      if isinstance(part.text, str):
        text += part.text
    return text if text else None

  @property
  def data(self) -> Optional[bytes]:
    """Returns the concatenation of all inline data parts in the response."""
    if (
        not self.server_content
        or not self.server_content
        or not self.server_content.model_turn
        or not self.server_content.model_turn.parts
    ):
      return None
    concatenated_data = b""
    for part in self.server_content.model_turn.parts:
      if part.inline_data and isinstance(part.inline_data.data, bytes):
        concatenated_data += part.inline_data.data
    return concatenated_data if len(concatenated_data) > 0 else None


class LiveServerMessageDict(TypedDict, total=False):
  """Response message for API call."""

  setup_complete: Optional[LiveServerSetupCompleteDict]
  """Sent in response to a `LiveClientSetup` message from the client."""

  server_content: Optional[LiveServerContentDict]
  """Content generated by the model in response to client messages."""

  tool_call: Optional[LiveServerToolCallDict]
  """Request for the client to execute the `function_calls` and return the responses with the matching `id`s."""

  tool_call_cancellation: Optional[LiveServerToolCallCancellationDict]
  """Notification for the client that a previously issued `ToolCallMessage` with the specified `id`s should have been not executed and should be cancelled."""


LiveServerMessageOrDict = Union[LiveServerMessage, LiveServerMessageDict]


class LiveClientSetup(_common.BaseModel):
  """Message contains configuration that will apply for the duration of the streaming session."""

  model: Optional[str] = Field(
      default=None,
      description="""
      The fully qualified name of the publisher model or tuned model endpoint to
      use.
      """,
  )
  generation_config: Optional[GenerationConfig] = Field(
      default=None,
      description="""The generation configuration for the session.""",
  )
  system_instruction: Optional[Content] = Field(
      default=None,
      description="""The user provided system instructions for the model.
      Note: only text should be used in parts and content in each part will be
      in a separate paragraph.""",
  )
  tools: Optional[list[Tool]] = Field(
      default=None,
      description=""" A list of `Tools` the model may use to generate the next response.

      A `Tool` is a piece of code that enables the system to interact with
      external systems to perform an action, or set of actions, outside of
      knowledge and scope of the model.""",
  )


class LiveClientSetupDict(TypedDict, total=False):
  """Message contains configuration that will apply for the duration of the streaming session."""

  model: Optional[str]
  """
      The fully qualified name of the publisher model or tuned model endpoint to
      use.
      """

  generation_config: Optional[GenerationConfigDict]
  """The generation configuration for the session."""

  system_instruction: Optional[ContentDict]
  """The user provided system instructions for the model.
      Note: only text should be used in parts and content in each part will be
      in a separate paragraph."""

  tools: Optional[list[ToolDict]]
  """ A list of `Tools` the model may use to generate the next response.

      A `Tool` is a piece of code that enables the system to interact with
      external systems to perform an action, or set of actions, outside of
      knowledge and scope of the model."""


LiveClientSetupOrDict = Union[LiveClientSetup, LiveClientSetupDict]


class LiveClientContent(_common.BaseModel):
  """Incremental update of the current conversation delivered from the client.

  All the content here will unconditionally be appended to the conversation
  history and used as part of the prompt to the model to generate content.

  A message here will interrupt any current model generation.
  """

  turns: Optional[list[Content]] = Field(
      default=None,
      description="""The content appended to the current conversation with the model.

      For single-turn queries, this is a single instance. For multi-turn
      queries, this is a repeated field that contains conversation history +
      latest request.
      """,
  )
  turn_complete: Optional[bool] = Field(
      default=None,
      description="""If true, indicates that the server content generation should start with
  the currently accumulated prompt. Otherwise, the server will await
  additional messages before starting generation.""",
  )


class LiveClientContentDict(TypedDict, total=False):
  """Incremental update of the current conversation delivered from the client.

  All the content here will unconditionally be appended to the conversation
  history and used as part of the prompt to the model to generate content.

  A message here will interrupt any current model generation.
  """

  turns: Optional[list[ContentDict]]
  """The content appended to the current conversation with the model.

      For single-turn queries, this is a single instance. For multi-turn
      queries, this is a repeated field that contains conversation history +
      latest request.
      """

  turn_complete: Optional[bool]
  """If true, indicates that the server content generation should start with
  the currently accumulated prompt. Otherwise, the server will await
  additional messages before starting generation."""


LiveClientContentOrDict = Union[LiveClientContent, LiveClientContentDict]


class LiveClientRealtimeInput(_common.BaseModel):
  """User input that is sent in real time.

  This is different from `ClientContentUpdate` in a few ways:
  - Can be sent continuously without interruption the model generation.
  - If there is a need to mix data interleaved across the
    `ClientContentUpdate` and the `RealtimeUpdate`, server will attempt to
    optimize for best response, but there are no guarantees.
  - End of turn is not explicitly specified, but is rather derived from user
    activity, e.g. end of speech.
  - Even before the end of turn, the data will be processed incrementally
    to optimize for a fast start of the response from the model.
  - Is always assumed to be the user's input (cannot be used to populate
    conversation history).
  """

  media_chunks: Optional[list[Blob]] = Field(
      default=None, description="""Inlined bytes data for media input."""
  )


class LiveClientRealtimeInputDict(TypedDict, total=False):
  """User input that is sent in real time.

  This is different from `ClientContentUpdate` in a few ways:
  - Can be sent continuously without interruption the model generation.
  - If there is a need to mix data interleaved across the
    `ClientContentUpdate` and the `RealtimeUpdate`, server will attempt to
    optimize for best response, but there are no guarantees.
  - End of turn is not explicitly specified, but is rather derived from user
    activity, e.g. end of speech.
  - Even before the end of turn, the data will be processed incrementally
    to optimize for a fast start of the response from the model.
  - Is always assumed to be the user's input (cannot be used to populate
    conversation history).
  """

  media_chunks: Optional[list[BlobDict]]
  """Inlined bytes data for media input."""


LiveClientRealtimeInputOrDict = Union[
    LiveClientRealtimeInput, LiveClientRealtimeInputDict
]


class LiveClientToolResponse(_common.BaseModel):
  """Client generated response to a `ToolCall` received from the server.

  Individual `FunctionResponse` objects are matched to the respective
  `FunctionCall` objects by the `id` field.

  Note that in the unary and server-streaming GenerateContent APIs function
  calling happens by exchanging the `Content` parts, while in the bidi
  GenerateContent APIs function calling happens over this dedicated set of
  messages.
  """

  function_responses: Optional[list[FunctionResponse]] = Field(
      default=None, description="""The response to the function calls."""
  )


class LiveClientToolResponseDict(TypedDict, total=False):
  """Client generated response to a `ToolCall` received from the server.

  Individual `FunctionResponse` objects are matched to the respective
  `FunctionCall` objects by the `id` field.

  Note that in the unary and server-streaming GenerateContent APIs function
  calling happens by exchanging the `Content` parts, while in the bidi
  GenerateContent APIs function calling happens over this dedicated set of
  messages.
  """

  function_responses: Optional[list[FunctionResponseDict]]
  """The response to the function calls."""


LiveClientToolResponseOrDict = Union[
    LiveClientToolResponse, LiveClientToolResponseDict
]


class LiveClientMessage(_common.BaseModel):
  """Messages sent by the client in the API call."""

  setup: Optional[LiveClientSetup] = Field(
      default=None,
      description="""Message to be sent in the first and only first client message.""",
  )
  client_content: Optional[LiveClientContent] = Field(
      default=None,
      description="""Incremental update of the current conversation delivered from the client.""",
  )
  realtime_update: Optional[LiveClientRealtimeInput] = Field(
      default=None, description="""User input that is sent in real time."""
  )
  tool_response: Optional[LiveClientToolResponse] = Field(
      default=None,
      description="""Response to a `ToolCallMessage` received from the server.""",
  )


class LiveClientMessageDict(TypedDict, total=False):
  """Messages sent by the client in the API call."""

  setup: Optional[LiveClientSetupDict]
  """Message to be sent in the first and only first client message."""

  client_content: Optional[LiveClientContentDict]
  """Incremental update of the current conversation delivered from the client."""

  realtime_update: Optional[LiveClientRealtimeInputDict]
  """User input that is sent in real time."""

  tool_response: Optional[LiveClientToolResponseDict]
  """Response to a `ToolCallMessage` received from the server."""


LiveClientMessageOrDict = Union[LiveClientMessage, LiveClientMessageDict]


class LiveConnectConfig(_common.BaseModel):
  """Config class for the session."""

  generation_config: Optional[GenerationConfig] = Field(
      default=None,
      description="""The generation configuration for the session.""",
  )
  response_modalities: Optional[list[Modality]] = Field(
      default=None,
      description="""The requested modalities of the response. Represents the set of
      modalities that the model can return. Defaults to AUDIO if not specified.
      """,
  )
  speech_config: Optional[SpeechConfig] = Field(
      default=None,
      description="""The speech generation configuration.
      """,
  )
  system_instruction: Optional[Content] = Field(
      default=None,
      description="""The user provided system instructions for the model.
      Note: only text should be used in parts and content in each part will be
      in a separate paragraph.""",
  )
  tools: Optional[list[Tool]] = Field(
      default=None,
      description="""A list of `Tools` the model may use to generate the next response.

      A `Tool` is a piece of code that enables the system to interact with
      external systems to perform an action, or set of actions, outside of
      knowledge and scope of the model.""",
  )


class LiveConnectConfigDict(TypedDict, total=False):
  """Config class for the session."""

  generation_config: Optional[GenerationConfigDict]
  """The generation configuration for the session."""

  response_modalities: Optional[list[Modality]]
  """The requested modalities of the response. Represents the set of
      modalities that the model can return. Defaults to AUDIO if not specified.
      """

  speech_config: Optional[SpeechConfigDict]
  """The speech generation configuration.
      """

  system_instruction: Optional[ContentDict]
  """The user provided system instructions for the model.
      Note: only text should be used in parts and content in each part will be
      in a separate paragraph."""

  tools: Optional[list[ToolDict]]
  """A list of `Tools` the model may use to generate the next response.

      A `Tool` is a piece of code that enables the system to interact with
      external systems to perform an action, or set of actions, outside of
      knowledge and scope of the model."""


LiveConnectConfigOrDict = Union[LiveConnectConfig, LiveConnectConfigDict]
