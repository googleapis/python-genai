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
import pytest
from ... import types
from .. import pytest_helper


def get_current_weather(location: str) -> str:
  """Returns the current weather.

  Args:
    location: The location of a city and state, e.g. "San Francisco, CA".
  """
  return 'windy'


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
)
pytest_plugins = ('pytest_asyncio',)


def test_generate_content_stream_with_function_and_thought_summaries(client):
  """Test when function tools are provided and thought summaries are enabled.

  Expected to answer weather based on function response.
  """
  config = types.GenerateContentConfig(
      tools=[get_current_weather],
      thinking_config=types.ThinkingConfig(include_thoughts=True),
  )
  stream = client.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='what is the weather in San Francisco, CA?',
      config=config,
  )

  chunk = None
  for chunk in stream:
    assert chunk is not None


@pytest.mark.asyncio
async def test_generate_content_stream_with_function_and_thought_summaries_async(
    client,
):
  """Test when function tools are provided and thought summaries are enabled.

  Expected to answer weather based on function response.
  """
  config = types.GenerateContentConfig(
      tools=[get_current_weather],
      thinking_config=types.ThinkingConfig(include_thoughts=True),
  )
  stream = await client.aio.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='what is the weather in San Francisco, CA?',
      config=config,
  )

  chunk = None
  async for chunk in stream:
    assert chunk is not None
