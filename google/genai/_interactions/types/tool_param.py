# Copyright 2025 Google LLC
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

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .function_param import FunctionParam
from .allowed_tools_param import AllowedToolsParam

__all__ = [
    "ToolParam",
    "CodeExecution",
    "URLContext",
    "ComputerUse",
    "MCPServer",
    "GoogleSearch",
    "FileSearch",
    "GoogleMaps",
    "Retrieval",
    "RetrievalExaAISearchConfig",
    "RetrievalParallelAISearchConfig",
    "RetrievalRagStoreConfig",
    "RetrievalRagStoreConfigRagResource",
    "RetrievalRagStoreConfigRagRetrievalConfig",
    "RetrievalRagStoreConfigRagRetrievalConfigFilter",
    "RetrievalRagStoreConfigRagRetrievalConfigHybridSearch",
    "RetrievalRagStoreConfigRagRetrievalConfigRanking",
    "RetrievalVertexAISearchConfig",
]


class CodeExecution(TypedDict, total=False):
    """A tool that can be used by the model to execute code."""

    type: Required[Literal["code_execution"]]


class URLContext(TypedDict, total=False):
    """A tool that can be used by the model to fetch URL context."""

    type: Required[Literal["url_context"]]


class ComputerUse(TypedDict, total=False):
    """A tool that can be used by the model to interact with the computer."""

    type: Required[Literal["computer_use"]]

    environment: Literal["browser"]
    """The environment being operated."""

    excluded_predefined_functions: SequenceNotStr[str]
    """The list of predefined functions that are excluded from the model call."""


class MCPServer(TypedDict, total=False):
    """A MCPServer is a server that can be called by the model to perform actions."""

    type: Required[Literal["mcp_server"]]

    allowed_tools: Iterable[AllowedToolsParam]
    """The allowed tools."""

    headers: Dict[str, str]
    """Optional: Fields for authentication headers, timeouts, etc., if needed."""

    name: str
    """The name of the MCPServer."""

    url: str
    """The full URL for the MCPServer endpoint. Example: "https://api.example.com/mcp" """


class GoogleSearch(TypedDict, total=False):
    """A tool that can be used by the model to search Google."""

    type: Required[Literal["google_search"]]

    search_types: List[Literal["web_search", "image_search", "enterprise_web_search"]]
    """The types of search grounding to enable."""


class FileSearch(TypedDict, total=False):
    """A tool that can be used by the model to search files."""

    type: Required[Literal["file_search"]]

    file_search_store_names: SequenceNotStr[str]
    """The file search store names to search."""

    metadata_filter: str
    """Metadata filter to apply to the semantic retrieval documents and chunks."""

    top_k: int
    """The number of semantic retrieval chunks to retrieve."""


class GoogleMaps(TypedDict, total=False):
    """A tool that can be used by the model to call Google Maps."""

    type: Required[Literal["google_maps"]]

    enable_widget: bool
    """
    Whether to return a widget context token in the tool call result of the
    response.
    """

    latitude: float
    """The latitude of the user's location."""

    longitude: float
    """The longitude of the user's location."""


class RetrievalExaAISearchConfig(TypedDict, total=False):
    """Used to specify configuration for ExaAISearch."""

    api_key: Required[str]
    """Required. The API key for ExaAiSearch."""

    custom_config: Dict[str, object]
    """Optional.

    This field can be used to pass any parameter from the Exa.ai Search API.
    """


class RetrievalParallelAISearchConfig(TypedDict, total=False):
    """Used to specify configuration for ParallelAISearch."""

    api_key: str
    """Optional. The API key for ParallelAiSearch."""

    custom_config: Dict[str, object]
    """Optional. Custom configs for ParallelAiSearch."""


class RetrievalRagStoreConfigRagResource(TypedDict, total=False):
    """The definition of the Rag resource."""

    rag_corpus: str
    """Optional. RagCorpora resource name."""

    rag_file_ids: SequenceNotStr[str]
    """Optional.

    rag_file_id. The files should be in the same rag_corpus set in rag_corpus field.
    """


class RetrievalRagStoreConfigRagRetrievalConfigFilter(TypedDict, total=False):
    """Optional. Config for filters."""

    metadata_filter: str
    """Optional. String for metadata filtering."""

    vector_distance_threshold: float
    """Optional.

    Only returns contexts with vector distance smaller than the threshold.
    """

    vector_similarity_threshold: float
    """Optional.

    Only returns contexts with vector similarity larger than the threshold.
    """


class RetrievalRagStoreConfigRagRetrievalConfigHybridSearch(TypedDict, total=False):
    """Optional. Config for Hybrid Search."""

    alpha: float
    """Optional.

    Alpha value controls the weight between dense and sparse vector search results.
    """


class RetrievalRagStoreConfigRagRetrievalConfigRanking(TypedDict, total=False):
    """Optional. Config for ranking and reranking."""

    ranking_config: Required[Literal["rank_service"]]

    model_name: str
    """Optional. The model name of the rank service."""


class RetrievalRagStoreConfigRagRetrievalConfig(TypedDict, total=False):
    """Optional. The retrieval config for the Rag query."""

    filter: RetrievalRagStoreConfigRagRetrievalConfigFilter
    """Optional. Config for filters."""

    hybrid_search: RetrievalRagStoreConfigRagRetrievalConfigHybridSearch
    """Optional. Config for Hybrid Search."""

    ranking: RetrievalRagStoreConfigRagRetrievalConfigRanking
    """Optional. Config for ranking and reranking."""

    top_k: int
    """Optional. The number of contexts to retrieve."""


class RetrievalRagStoreConfig(TypedDict, total=False):
    """Used to specify configuration for RagStore."""

    rag_resources: Iterable[RetrievalRagStoreConfigRagResource]
    """Optional. The representation of the rag source."""

    rag_retrieval_config: RetrievalRagStoreConfigRagRetrievalConfig
    """Optional. The retrieval config for the Rag query."""

    similarity_top_k: int
    """Optional. Number of top k results to return from the selected corpora."""

    vector_distance_threshold: float
    """Optional. Only return results with vector distance smaller than the threshold."""


class RetrievalVertexAISearchConfig(TypedDict, total=False):
    """Used to specify configuration for VertexAISearch."""

    datastores: SequenceNotStr[str]
    """Optional. Used to specify Vertex AI Search datastores."""

    engine: str
    """Optional. Used to specify Vertex AI Search engine."""


class Retrieval(TypedDict, total=False):
    """A tool that can be used by the model to retrieve files."""

    type: Required[Literal["retrieval"]]

    exa_ai_search_config: RetrievalExaAISearchConfig
    """Used to specify configuration for ExaAISearch."""

    parallel_ai_search_config: RetrievalParallelAISearchConfig
    """Used to specify configuration for ParallelAISearch."""

    rag_store_config: RetrievalRagStoreConfig
    """Used to specify configuration for RagStore."""

    retrieval_types: List[Literal["vertex_ai_search", "rag_store", "exa_ai_search", "parallel_ai_search"]]
    """The types of file retrieval to enable."""

    vertex_ai_search_config: RetrievalVertexAISearchConfig
    """Used to specify configuration for VertexAISearch."""


ToolParam: TypeAlias = Union[
    FunctionParam, CodeExecution, URLContext, ComputerUse, MCPServer, GoogleSearch, FileSearch, GoogleMaps, Retrieval
]
