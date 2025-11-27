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

import sys
from enum import Enum
from typing import List, Optional, Union

import pytest
from pydantic import BaseModel, Field

from google import genai
from google.genai import types


@pytest.fixture
def client():
    """Return a client that uses the replay_session."""
    client = genai.Client(api_key="test-api-key")
    return client


def test_basic_list_of_pydantic_schema(client):
    """Test basic list of pydantic schema support."""

    class Recipe(BaseModel):
        recipe_name: str
        ingredients: List[str]
        prep_time_minutes: int

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="List 3 simple cookie recipes.",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[Recipe],
        ),
    )

    # Verify the parsed field contains a list of Recipe objects
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert all(isinstance(item, Recipe) for item in response.parsed)

    # Access a property to verify the type annotation works correctly
    recipe = response.parsed[0]
    assert isinstance(recipe.recipe_name, str)
    assert isinstance(recipe.ingredients, list)


def test_nested_list_of_pydantic_schema(client):
    """Test nested list of pydantic schema support."""

    class RecipeStep(BaseModel):
        step_number: int
        instruction: str

    class Recipe(BaseModel):
        recipe_name: str
        steps: List[RecipeStep]

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Give me 2 recipes with detailed steps.",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[Recipe],
        ),
    )

    # Verify the parsed field contains a list of Recipe objects with nested RecipeStep objects
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert all(isinstance(item, Recipe) for item in response.parsed)

    # Access nested property to verify the type annotation works correctly
    recipe = response.parsed[0]
    assert isinstance(recipe.steps, list)
    assert all(isinstance(step, RecipeStep) for step in recipe.steps)


def test_empty_list_of_pydantic_schema(client):
    """Test empty list of pydantic schema support."""

    class Recipe(BaseModel):
        recipe_name: str
        ingredients: List[str]

    # Note: I am only testing the type annotation support, not the model's behavior

    # Create a mock response with an empty list
    response = types.GenerateContentResponse()
    # Set parsed to an empty list which should be valid with our type annotation update
    response.parsed = []

    assert isinstance(response.parsed, list)
    assert len(response.parsed) == 0


def test_list_with_optional_fields(client):
    """Test list of pydantic schema with optional fields."""

    class Recipe(BaseModel):
        recipe_name: str
        ingredients: List[str]
        prep_time_minutes: Optional[int] = None
        cook_time_minutes: Optional[int] = None
        difficulty: Optional[str] = None

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="List 2 simple recipes with varying details.",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[Recipe],
        ),
    )

    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert all(isinstance(item, Recipe) for item in response.parsed)

    # Even if the optional fields are None, the type annotation should work
    recipe = response.parsed[0]
    assert isinstance(recipe.recipe_name, str)

    assert recipe.prep_time_minutes is None or isinstance(recipe.prep_time_minutes, int)


def test_list_with_enum_fields(client):
    """Test list of pydantic schema with enum fields."""

    class DifficultyLevel(Enum):
        EASY = "easy"
        MEDIUM = "medium"
        HARD = "hard"

    class Recipe(BaseModel):
        recipe_name: str
        difficulty: DifficultyLevel

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="List 3 recipes with their difficulty levels.",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[Recipe],
        ),
    )

    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert all(isinstance(item, Recipe) for item in response.parsed)

    # Check that enum values are properly parsed
    recipe = response.parsed[0]
    assert isinstance(recipe.difficulty, DifficultyLevel)


def test_double_nested_list_of_pydantic_schema(client):
    """Test double nested list of pydantic schema support."""

    class Ingredient(BaseModel):
        name: str
        amount: str

    class Recipe(BaseModel):
        recipe_name: str
        ingredients: List[Ingredient]

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Give me a list of 2 recipes with detailed ingredients.",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[Recipe],
        ),
    )

    # Verify the parsed field contains a list of Recipe objects with nested Ingredient objects
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert all(isinstance(item, Recipe) for item in response.parsed)

    # Access doubly nested property to verify the type annotation works correctly
    recipe = response.parsed[0]
    assert isinstance(recipe.ingredients, list)
    assert all(isinstance(ingredient, Ingredient) for ingredient in recipe.ingredients)

    # Access properties of the nested objects
    if recipe.ingredients:
        ingredient = recipe.ingredients[0]
        assert isinstance(ingredient.name, str)
        assert isinstance(ingredient.amount, str)
