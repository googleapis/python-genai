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

import os
from typing import Optional

from .types import HttpOptions

_default_base_gemini_url = None
_default_base_vertex_url = None


class BaseUrlParameters:
  """Parameters for setting the base URLs for the Gemini API and Vertex AI API."""

  gemini_url: str | None = None
  vertex_url: str | None = None

  def __init__(
      self,
      gemini_url: str | None = None,
      vertex_url: str | None = None,
  ):
    self.gemini_url = gemini_url
    self.vertex_url = vertex_url


def set_default_base_urls(base_url_params: BaseUrlParameters) -> None:
  """Overrides the base URLs for the Gemini API and Vertex AI API."""
  global _default_base_gemini_url, _default_base_vertex_url
  _default_base_gemini_url = base_url_params.gemini_url
  _default_base_vertex_url = base_url_params.vertex_url


def get_default_base_urls() -> BaseUrlParameters:
  """Overrides the base URLs for the Gemini API and Vertex AI API."""
  return BaseUrlParameters(
      gemini_url=_default_base_gemini_url, vertex_url=_default_base_vertex_url
  )


def get_base_url(
    vertexai: bool,
    http_options: Optional[HttpOptions] = None,
) -> str | None:
  """Returns the default base URL based on the following priority.

  1. Base URLs set via HttpOptions.
  2. Base URLs set via the latest call to setDefaultBaseUrls.
  3. Base URLs set via environment variables.
  """
  if http_options and http_options.base_url:
    return http_options.base_url

  if vertexai:
    return _default_base_vertex_url or os.getenv('GOOGLE_VERTEX_BASE_URL')
  else:
    return _default_base_gemini_url or os.getenv('GOOGLE_GEMINI_BASE_URL')
