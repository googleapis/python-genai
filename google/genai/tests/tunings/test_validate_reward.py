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


"""Tests for tunings.validate_reward()."""

from ... import types as genai_types
from .. import pytest_helper

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_validate_reward_single_autorater",
        parameters=genai_types._ValidateRewardParameters(
            parent="projects/801452371447/locations/us-central1",
            sample_response=genai_types.Content(
                parts=[genai_types.Part(text="The answer is 42.")]
            ),
            example=genai_types.ReinforcementTuningExample(
                contents=[
                    genai_types.Content(
                        parts=[
                            genai_types.Part(text="What is the answer to life?")
                        ]
                    )
                ],
            ),
            single_reward_config=genai_types.SingleReinforcementTuningRewardConfig(
                autorater_scorer=genai_types.ReinforcementTuningAutoraterScorer(
                    autorater_config=genai_types.AutoraterConfig(
                        autorater_model="test-model"
                    )
                )
            ),
        ),
        exception_if_mldev=(
            "only supported in Gemini Enterprise Agent Platform mode"
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_validate_reward_code_execution",
        parameters=genai_types._ValidateRewardParameters(
            parent="projects/801452371447/locations/us-central1",
            sample_response=genai_types.Content(
                parts=[genai_types.Part(text="print('hello')")]
            ),
            example=genai_types.ReinforcementTuningExample(
                contents=[
                    genai_types.Content(
                        parts=[
                            genai_types.Part(
                                text="Write a hello world program."
                            )
                        ]
                    )
                ],
                references={"reference": "hello"},
            ),
            single_reward_config=genai_types.SingleReinforcementTuningRewardConfig(
                reward_name="codeExecReward",
                parse_response_config=genai_types.ReinforcementTuningParseResponseConfig(
                    parse_type="IDENTITY",
                ),
                code_execution_reward_scorer=genai_types.ReinforcementTuningCodeExecutionRewardScorer(
                    python_code_snippet=(
                        "reward = 1.0 if response == references['reference']"
                        " else 0.0"
                    ),
                ),
            ),
        ),
        exception_if_mldev=(
            "only supported in Gemini Enterprise Agent Platform mode"
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_validate_reward_string_match",
        parameters=genai_types._ValidateRewardParameters(
            parent="projects/801452371447/locations/us-central1",
            sample_response=genai_types.Content(
                parts=[genai_types.Part(text="42")]
            ),
            example=genai_types.ReinforcementTuningExample(
                contents=[
                    genai_types.Content(
                        parts=[genai_types.Part(text="What is 6 times 7?")]
                    )
                ],
                references={"answer": "42"},
                system_instruction=genai_types.Content(
                    parts=[genai_types.Part(text="You are a math tutor.")]
                ),
            ),
            single_reward_config=genai_types.SingleReinforcementTuningRewardConfig(
                reward_name="stringMatchReward",
                parse_response_config=genai_types.ReinforcementTuningParseResponseConfig(
                    parse_type="REGEX_EXTRACT",
                    regex_extract_expression=r"(\d+)",
                ),
                string_match_reward_scorer=genai_types.ReinforcementTuningStringMatchRewardScorer(
                    correct_answer_reward=1.0,
                    wrong_answer_reward=-1.0,
                    string_match_expression=genai_types.ReinforcementTuningStringMatchRewardScorerStringMatchExpression(
                        match_operation="EXACT_MATCH",
                        expression="{{references.answer}}",
                    ),
                ),
            ),
        ),
        exception_if_mldev=(
            "only supported in Gemini Enterprise Agent Platform mode"
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_validate_reward_composite",
        parameters=genai_types._ValidateRewardParameters(
            parent="projects/801452371447/locations/us-central1",
            sample_response=genai_types.Content(
                parts=[genai_types.Part(text="The answer is 42.")]
            ),
            example=genai_types.ReinforcementTuningExample(
                contents=[
                    genai_types.Content(
                        parts=[
                            genai_types.Part(text="What is the answer to life?")
                        ]
                    )
                ],
            ),
            composite_reward_config=genai_types.CompositeReinforcementTuningRewardConfig(
                weighted_reward_configs=[
                    genai_types.CompositeReinforcementTuningRewardConfigWeightedRewardConfig(
                        weight=0.7,
                        reward_config=genai_types.SingleReinforcementTuningRewardConfig(
                            reward_name="autoraterReward",
                            autorater_scorer=genai_types.ReinforcementTuningAutoraterScorer(
                                autorater_config=genai_types.AutoraterConfig(
                                    autorater_model="test-model"
                                ),
                                autorater_prompt=(
                                    "Rate the response: {{response}}"
                                ),
                                exact_match_scorer=genai_types.ReinforcementTuningAutoraterScorerExactMatchScorer(
                                    correct_answer_reward=1.0,
                                    wrong_answer_reward=0.0,
                                    expression="good",
                                ),
                            ),
                        ),
                    ),
                    genai_types.CompositeReinforcementTuningRewardConfigWeightedRewardConfig(
                        weight=0.3,
                        reward_config=genai_types.SingleReinforcementTuningRewardConfig(
                            reward_name="codeReward",
                            code_execution_reward_scorer=genai_types.ReinforcementTuningCodeExecutionRewardScorer(
                                python_code_snippet="reward = 1.0",
                            ),
                        ),
                    ),
                ]
            ),
        ),
        exception_if_mldev=(
            "only supported in Gemini Enterprise Agent Platform mode"
        ),
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="tunings.validate_reward",
    test_table=test_table,
)

pytest_plugins = ("pytest_asyncio",)
