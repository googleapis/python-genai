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


"""Tests for get_function_response_parts."""

import asyncio
import time
import typing
from typing import Any
import pytest
from ..._extra_utils import (
    get_function_response_parts,
    get_function_response_parts_async,
    should_run_afc_concurrently,
)
from ...errors import UnsupportedFunctionError
from ... import types
from ...types import Candidate
from ...types import Content
from ...types import FunctionCall
from ...types import FunctionResponse
from ...types import GenerateContentResponse
from ...types import Part

_is_mcp_imported = False
if typing.TYPE_CHECKING:
  from mcp import types as mcp_types
  from mcp import ClientSession as McpClientSession
  from ..._adapters import McpToGenAiToolAdapter

  _is_mcp_imported = True
else:
  McpClientSession: typing.Type = Any
  McpToGenAiToolAdapter: typing.Type = Any
  try:
    from mcp import types as mcp_types
    from mcp import ClientSession as McpClientSession
    from ..._adapters import McpToGenAiToolAdapter

    _is_mcp_imported = True
  except ImportError:
    McpClientSession = None
    McpToGenAiToolAdapter = None


def test_integer_value():
  def func_under_test(a: int) -> int:
    return a + 1

  response = GenerateContentResponse(
      candidates=[
          Candidate(
              content=Content(
                  parts=[
                      Part(
                          function_call=FunctionCall(
                              name='func_under_test',
                              args={'a': 1},
                          )
                      )
                  ]
              )
          )
      ]
  )
  function_map = {'func_under_test': func_under_test}
  expected_parts = [
      Part(
          function_response=FunctionResponse(
              name='func_under_test',
              response={'result': 2},
          )
      )
  ]
  actual_parts = get_function_response_parts(response, function_map)

  for actual_part, expected_part in zip(actual_parts, expected_parts):
    assert actual_part.model_dump_json(
        exclude_none=True
    ) == expected_part.model_dump_json(exclude_none=True)


def test_float_value():
  def func_under_test(a: float) -> float:
    return a + 1.0

  response = GenerateContentResponse(
      candidates=[
          Candidate(
              content=Content(
                  parts=[
                      Part(
                          function_call=FunctionCall(
                              name='func_under_test',
                              args={'a': 1.0},
                          )
                      )
                  ]
              )
          )
      ]
  )
  function_map = {'func_under_test': func_under_test}
  expected_parts = [
      Part(
          function_response=FunctionResponse(
              name='func_under_test',
              response={'result': 2.0},
          )
      )
  ]
  actual_parts = get_function_response_parts(response, function_map)

  for actual_part, expected_part in zip(actual_parts, expected_parts):
    assert actual_part.model_dump_json(
        exclude_none=True
    ) == expected_part.model_dump_json(exclude_none=True)


def test_string_value():
  def func_under_test(a: str) -> str:
    return a + '1'

  response = GenerateContentResponse(
      candidates=[
          Candidate(
              content=Content(
                  parts=[
                      Part(
                          function_call=FunctionCall(
                              name='func_under_test',
                              args={'a': '1.0'},
                          )
                      )
                  ]
              )
          )
      ]
  )
  function_map = {'func_under_test': func_under_test}
  expected_parts = [
      Part(
          function_response=FunctionResponse(
              name='func_under_test',
              response={'result': '1.01'},
          )
      )
  ]
  actual_parts = get_function_response_parts(response, function_map)

  for actual_part, expected_part in zip(actual_parts, expected_parts):
    assert actual_part.model_dump_json(
        exclude_none=True
    ) == expected_part.model_dump_json(exclude_none=True)


@pytest.mark.asyncio
async def test_mcp_tool():
  if not _is_mcp_imported:
    return

  class MockMcpClientSession(McpClientSession):

    def __init__(self):
      self._read_stream = None
      self._write_stream = None

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
      return mcp_types.CallToolResult(
          content=[mcp_types.TextContent(type='text', text='1.01')]
      )

  mcp_to_genai_tool_adapter = McpToGenAiToolAdapter(
      session=MockMcpClientSession(),
      list_tools_result=mcp_types.ListToolsResult(tools=[]),
  )
  response = GenerateContentResponse(
      candidates=[
          Candidate(
              content=Content(
                  parts=[
                      Part(
                          function_call=FunctionCall(
                              name='tool',
                              args={'key1': 'value1', 'key2': 1},
                          )
                      )
                  ]
              )
          )
      ]
  )
  function_map = {'tool': mcp_to_genai_tool_adapter}
  expected_parts = [
      Part(
          function_response=FunctionResponse(
              name='tool',
              response={
                  'result': {
                      'content': [{'type': 'text', 'text': '1.01'}],
                      'isError': False,
                  }
              },
          )
      )
  ]
  actual_parts = await get_function_response_parts_async(response, function_map)

  for actual_part, expected_part in zip(actual_parts, expected_parts):
    assert actual_part.model_dump_json(
        exclude_none=True
    ) == expected_part.model_dump_json(exclude_none=True)


@pytest.mark.asyncio
async def test_mcp_tool_error():
  if not _is_mcp_imported:
    return

  class MockMcpClientSession(McpClientSession):

    def __init__(self):
      self._read_stream = None
      self._write_stream = None

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
      return mcp_types.CallToolResult(
          content=[mcp_types.TextContent(type='text', text='Internal error')],
          isError=True,
      )

  mcp_to_genai_tool_adapter = McpToGenAiToolAdapter(
      session=MockMcpClientSession(),
      list_tools_result=mcp_types.ListToolsResult(tools=[]),
  )
  response = GenerateContentResponse(
      candidates=[
          Candidate(
              content=Content(
                  parts=[
                      Part(
                          function_call=FunctionCall(
                              name='tool',
                              args={'key1': 'value1', 'key2': 1},
                          )
                      )
                  ]
              )
          )
      ]
  )
  function_map = {'tool': mcp_to_genai_tool_adapter}
  expected_parts = [
      Part(
          function_response=FunctionResponse(
              name='tool',
              response={
                  'error': {
                      'content': [{'type': 'text', 'text': 'Internal error'}],
                      'isError': True,
                  }
              },
          )
      )
  ]
  actual_parts = await get_function_response_parts_async(response, function_map)

  for actual_part, expected_part in zip(actual_parts, expected_parts):
    assert actual_part.model_dump_json(
        exclude_none=True
    ) == expected_part.model_dump_json(exclude_none=True)


def test_should_run_afc_concurrently():
  assert should_run_afc_concurrently(None) is False
  assert should_run_afc_concurrently(types.GenerateContentConfig()) is False
  assert (
      should_run_afc_concurrently(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig()
          )
      )
      is False
  )
  assert (
      should_run_afc_concurrently(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  run_concurrently=True
              )
          )
      )
      is True
  )


def _multi_function_response() -> GenerateContentResponse:
  return GenerateContentResponse(
      candidates=[
          Candidate(
              content=Content(
                  parts=[
                      Part(
                          function_call=FunctionCall(
                              name='slow_a',
                              args={},
                          )
                      ),
                      Part(
                          function_call=FunctionCall(
                              name='slow_b',
                              args={},
                          )
                      ),
                  ]
              )
          )
      ]
  )


@pytest.mark.asyncio
async def test_async_run_concurrently_preserves_order_and_results():
  async def slow_a() -> str:
    await asyncio.sleep(0.05)
    return 'a'

  async def slow_b() -> str:
    await asyncio.sleep(0.01)
    return 'b'

  response = _multi_function_response()
  function_map = {'slow_a': slow_a, 'slow_b': slow_b}
  config = types.GenerateContentConfig(
      automatic_function_calling=types.AutomaticFunctionCallingConfig(
          run_concurrently=True
      )
  )
  actual_parts = await get_function_response_parts_async(
      response, function_map, config
  )
  assert [p.function_response.name for p in actual_parts] == [
      'slow_a',
      'slow_b',
  ]
  assert actual_parts[0].function_response is not None
  assert actual_parts[1].function_response is not None
  assert actual_parts[0].function_response.response == {'result': 'a'}
  assert actual_parts[1].function_response.response == {'result': 'b'}


@pytest.mark.asyncio
async def test_async_run_concurrently_is_faster_than_sequential():
  async def slow_a() -> str:
    await asyncio.sleep(0.1)
    return 'a'

  async def slow_b() -> str:
    await asyncio.sleep(0.1)
    return 'b'

  response = _multi_function_response()
  function_map = {'slow_a': slow_a, 'slow_b': slow_b}
  concurrent_config = types.GenerateContentConfig(
      automatic_function_calling=types.AutomaticFunctionCallingConfig(
          run_concurrently=True
      )
  )
  sequential_config = types.GenerateContentConfig(
      automatic_function_calling=types.AutomaticFunctionCallingConfig(
          run_concurrently=False
      )
  )

  start = time.perf_counter()
  await get_function_response_parts_async(
      response, function_map, sequential_config
  )
  sequential_elapsed = time.perf_counter() - start

  start = time.perf_counter()
  await get_function_response_parts_async(
      response, function_map, concurrent_config
  )
  concurrent_elapsed = time.perf_counter() - start

  # Concurrent should finish near one sleep; sequential near the sum.
  assert concurrent_elapsed < sequential_elapsed
  assert concurrent_elapsed < 0.18
  assert sequential_elapsed >= 0.18


@pytest.mark.asyncio
async def test_async_run_concurrently_default_remains_sequential():
  in_flight = 0
  max_in_flight = 0
  lock = asyncio.Lock()

  async def tracked(name: str) -> str:
    nonlocal in_flight, max_in_flight
    async with lock:
      in_flight += 1
      max_in_flight = max(max_in_flight, in_flight)
    await asyncio.sleep(0.05)
    async with lock:
      in_flight -= 1
    return name

  async def slow_a() -> str:
    return await tracked('a')

  async def slow_b() -> str:
    return await tracked('b')

  response = _multi_function_response()
  await get_function_response_parts_async(
      response, {'slow_a': slow_a, 'slow_b': slow_b}
  )
  assert max_in_flight == 1
