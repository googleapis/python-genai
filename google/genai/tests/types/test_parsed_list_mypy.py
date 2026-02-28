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

"""Tests to verify that mypy correctly handles list[pydantic.BaseModel] in response.parsed."""

from typing import List, cast
import logging

from pydantic import BaseModel

from google.genai import types

# Configure logging
logger = logging.getLogger(__name__)


def test_mypy_with_list_pydantic():
    """
    This test doesn't actually run, but it's meant to be analyzed by mypy.

    The code patterns here would have caused mypy errors before the fix,
    but now should pass type checking with our enhanced types.
    """

    # Define a Pydantic model for structured output
    class Recipe(BaseModel):
        recipe_name: str
        ingredients: List[str]

    # Create a mock response (simulating what we'd get from the API)
    response = types.GenerateContentResponse()

    # Before the fix[issue #886], this next line would cause a mypy error:
    # Incompatible types in assignment (expression has type "List[Recipe]",
    # variable has type "Optional[Union[BaseModel, Dict[Any, Any], Enum]]")
    #
    # With the fix adding list[pydantic.BaseModel] to the Union, this is now valid:
    response.parsed = [
        Recipe(
            recipe_name="Chocolate Chip Cookies",
            ingredients=["Flour", "Sugar", "Chocolate"],
        ),
        Recipe(
            recipe_name="Oatmeal Cookies", ingredients=["Oats", "Flour", "Brown Sugar"]
        ),
    ]

    # This pattern would require a type cast before the fix
    if response.parsed is not None:
        # Before the fix, accessing response.parsed as a list would cause a mypy error
        # and require a cast:
        # parsed_items = cast(list[Recipe], response.parsed)

        # With the fix, we can directly use it as a list without casting:
        recipes = response.parsed

        # Now iteration over the list without casting is possible
        for recipe in recipes:
            logger.info(f"Recipe: {recipe.recipe_name}")
            for ingredient in recipe.ingredients:
                logger.info(f" - {ingredient}")

        # Also accessing elements by index without casting is possible
        first_recipe = recipes[0]
        logger.info(f"First recipe: {first_recipe.recipe_name}")


def test_with_pydantic_inheritance():
    """Test with inheritance to ensure the type annotation works with subclasses."""

    class FoodItem(BaseModel):
        name: str

    class Recipe(FoodItem):
        ingredients: List[str]

    response = types.GenerateContentResponse()

    # Before the fix, this would require a cast with mypy
    # Now it works directly with the enhanced type annotation
    response.parsed = [
        Recipe(
            name="Chocolate Chip Cookies",
            ingredients=["Flour", "Sugar", "Chocolate"],
        ),
        Recipe(
            name="Oatmeal Cookies",
            ingredients=["Oats", "Flour", "Brown Sugar"],
        ),
    ]

    if response.parsed is not None:
        # Previously would need: cast(list[Recipe], response.parsed)
        recipes = response.parsed

        # Access fields from parent class
        for recipe in recipes:
            logger.info(f"Recipe name: {recipe.name}")


def test_with_nested_list_models():
    """Test with nested list models to ensure complex structures work."""

    class Ingredient(BaseModel):
        name: str
        amount: str

    class Recipe(BaseModel):
        recipe_name: str
        ingredients: List[Ingredient]

    response = types.GenerateContentResponse()

    # With the fix, mypy correctly handles this complex structure
    response.parsed = [
        Recipe(
            recipe_name="Chocolate Chip Cookies",
            ingredients=[
                Ingredient(name="Flour", amount="2 cups"),
                Ingredient(name="Sugar", amount="1 cup"),
            ],
        ),
        Recipe(
            recipe_name="Oatmeal Cookies",
            ingredients=[
                Ingredient(name="Oats", amount="1 cup"),
                Ingredient(name="Flour", amount="1.5 cups"),
            ],
        ),
    ]

    if response.parsed is not None:
        recipes = response.parsed

        # Access nested structures without casting
        for recipe in recipes:
            logger.info(f"Recipe: {recipe.recipe_name}")
            for ingredient in recipe.ingredients:
                logger.info(f" - {ingredient.name}: {ingredient.amount}")


# Example of how you would previously need to cast the results
def old_approach_with_cast():
    """
    This demonstrates the old approach that required explicit casting,
    which was less type-safe and more error-prone.
    """

    class Recipe(BaseModel):
        recipe_name: str
        ingredients: List[str]

    response = types.GenerateContentResponse()

    # Simulate API response
    response.parsed = [
        Recipe(
            recipe_name="Chocolate Chip Cookies",
            ingredients=["Flour", "Sugar", "Chocolate"],
        ),
        Recipe(
            recipe_name="Oatmeal Cookies", ingredients=["Oats", "Flour", "Brown Sugar"]
        ),
    ]

    if response.parsed is not None:
        # Before the fix, you'd need this cast for mypy to work successfully
        recipes = cast(List[Recipe], response.parsed)

        # Using the cast list
        for recipe in recipes:
            logger.info(f"Recipe: {recipe.recipe_name}")
