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

"""Table tests for chats.send_message()."""

from ... import pytest_helper
from pydantic import BaseModel


class _SendMessageParameters(BaseModel):
  model: str
  message: str


def send_message(client, parameters):
  chat = client.chats.create(model=parameters.model)
  chat.send_message(parameters.message)

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_send_message",
        parameters=_SendMessageParameters(
            model="gemini-2.5-flash",
            message="Hello",
        ),
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="send_message",
    test_table=test_table,
)

pytest_plugins = ("pytest_asyncio",)
