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

"""Tests to verify both LiveClient classes and list[pydantic.BaseModel] support."""

import inspect
from typing import List, Optional

from pydantic import BaseModel

from google.genai import types


def test_live_client_classes_exist():
    """Verify that LiveClient classes exist and have expected attributes."""
    # Check that LiveClientMessage exists
    assert hasattr(types, "LiveClientMessage")
    assert inspect.isclass(types.LiveClientMessage)

    # Check that LiveClientContent exists
    assert hasattr(types, "LiveClientContent")
    assert inspect.isclass(types.LiveClientContent)

    # Check that LiveClientRealtimeInput exists
    assert hasattr(types, "LiveClientRealtimeInput")
    assert inspect.isclass(types.LiveClientRealtimeInput)

    # Check that LiveClientSetup exists
    assert hasattr(types, "LiveClientSetup")
    assert inspect.isclass(types.LiveClientSetup)

    # Check for Dict versions
    assert hasattr(types, "LiveClientMessageDict")
    assert hasattr(types, "LiveClientContentDict")
    assert hasattr(types, "LiveClientRealtimeInputDict")
    assert hasattr(types, "LiveClientSetupDict")


def test_live_client_message_fields():
    """Verify that LiveClientMessage has expected fields."""
    # Get the field details
    fields = types.LiveClientMessage.model_fields

    # Check for expected fields
    assert "setup" in fields
    assert "client_content" in fields
    assert "realtime_input" in fields
    assert "tool_response" in fields


def test_list_pydantic_in_generate_content_response():
    """Verify that GenerateContentResponse can handle list[pydantic.BaseModel]."""

    class Recipe(BaseModel):
        recipe_name: str
        ingredients: List[str]

    # Create a test response
    response = types.GenerateContentResponse()

    # Assign a list of pydantic models
    recipes = [
        Recipe(
            recipe_name="Chocolate Chip Cookies",
            ingredients=["Flour", "Sugar", "Chocolate"],
        ),
        Recipe(
            recipe_name="Oatmeal Cookies", ingredients=["Oats", "Flour", "Brown Sugar"]
        ),
    ]

    # This assignment would fail with mypy if the type annotation is incorrect
    response.parsed = recipes

    # Verify assignment worked properly
    assert response.parsed is not None
    assert isinstance(response.parsed, list)
    assert len(response.parsed) == 2
    assert all(isinstance(item, Recipe) for item in response.parsed)


def test_combined_functionality():
    """Test that combines verification of both LiveClient classes and list[pydantic.BaseModel] support."""
    # Verify LiveClient classes exist
    assert hasattr(types, "LiveClientMessage")
    assert inspect.isclass(types.LiveClientMessage)

    # Test that GenerateContentResponse.parsed accepts list[pydantic.BaseModel]
    class Recipe(BaseModel):
        recipe_name: str
        ingredients: List[str]
        instructions: Optional[List[str]] = None

    response = types.GenerateContentResponse()
    recipes = [
        Recipe(recipe_name="Chocolate Chip Cookies", ingredients=["Flour", "Sugar"]),
        Recipe(recipe_name="Oatmeal Cookies", ingredients=["Oats", "Flour"]),
    ]
    response.parsed = recipes

    assert isinstance(response.parsed, list)
    assert len(response.parsed) == 2
    assert all(isinstance(item, Recipe) for item in response.parsed)


def test_live_connect_config_exists():
    """Verify that LiveConnectConfig exists and has expected attributes."""
    # Check that LiveConnectConfig exists
    assert hasattr(types, "LiveConnectConfig")
    assert inspect.isclass(types.LiveConnectConfig)

    # Check that LiveConnectConfigDict exists
    assert hasattr(types, "LiveConnectConfigDict")

    # Get the field details if it's a pydantic model
    if hasattr(types.LiveConnectConfig, "model_fields"):
        fields = types.LiveConnectConfig.model_fields

        # Check for expected fields (these might vary based on actual implementation)
        assert "generation_config" in fields


def test_live_client_tool_response():
    """Verify that LiveClientToolResponse exists and has expected attributes."""
    # Check that LiveClientToolResponse exists
    assert hasattr(types, "LiveClientToolResponse")
    assert inspect.isclass(types.LiveClientToolResponse)

    # Check that LiveClientToolResponseDict exists
    assert hasattr(types, "LiveClientToolResponseDict")

    # Get the field details
    fields = types.LiveClientToolResponse.model_fields

    # Check for expected fields
    assert "function_responses" in fields
