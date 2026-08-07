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


"""Tests for raise_error_for_afc_incompatible_config."""

import pytest
from ... import types
from ..._extra_utils import raise_error_for_afc_incompatible_config


def test_config_is_none():
  assert raise_error_for_afc_incompatible_config(None) is None


def test_tool_config_config_unset():
  assert (
      raise_error_for_afc_incompatible_config(types.ChatConfig(
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True,
              maximum_remote_calls=1,
          ),
      ))
      is None
  )


def test_function_calling_config_unset():
  assert (
      raise_error_for_afc_incompatible_config(types.ChatConfig(
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True,
              maximum_remote_calls=1,
          ),
          tool_config=types.ToolConfig(),
      ))
      is None
  )


def test_compatible_config_afc_disabled():
  assert (
      raise_error_for_afc_incompatible_config(
          types.ChatConfig(
              tool_config=types.ToolConfig(
                  function_calling_config=types.FunctionCallingConfig(
                      stream_function_call_arguments=False,
                  ),
              ),
          )
      )
      is None
  )


def test_compatible_config_stream_function_call_arguments_unset_afc_unset():
  assert (
      raise_error_for_afc_incompatible_config(
          types.ChatConfig(
              tool_config=types.ToolConfig(
                  function_calling_config=types.FunctionCallingConfig(
                  ),
              ),
          )
      )
      is None
  )


def test_compatible_config_stream_function_call_arguments_unset_enable_afc_false():
  assert (
      raise_error_for_afc_incompatible_config(
          types.ChatConfig(
              automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                  enable=False,
              ),
              tool_config=types.ToolConfig(
                  function_calling_config=types.FunctionCallingConfig(
                  ),
              ),
          )
      )
      is None
  )


def test_compatible_config_stream_function_call_arguments_unset_disable_afc_true():
  assert (
      raise_error_for_afc_incompatible_config(
          types.ChatConfig(
              automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              ),
              tool_config=types.ToolConfig(
                  function_calling_config=types.FunctionCallingConfig(
                  ),
              ),
          )
      )
      is None
  )


def test_incompatible_config_stream_function_call_arguments_set_enable_afc():
  with pytest.raises(ValueError):
    raise_error_for_afc_incompatible_config(
        types.ChatConfig(
            automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                enable=True,
            ),
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    stream_function_call_arguments=True,
                ),
            ),
        )
    )


def test_incompatible_config_stream_function_call_arguments_set_no_afc_config():
  assert raise_error_for_afc_incompatible_config(
        types.ChatConfig(
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    stream_function_call_arguments=True,
                ),
            ),
        )
    ) is None

