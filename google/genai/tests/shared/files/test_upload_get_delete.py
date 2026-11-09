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

"""Tests for files.upload(), files.get(), and files.delete()."""

from pydantic import BaseModel
from ... import pytest_helper


class _UploadGetDeleteParameters(BaseModel):
  file_path: str


def upload_get_delete(client, parameters):
  file = None
  try:
    file = client.files.upload(file=parameters.file_path)
    assert file.name
    got_file = client.files.get(name=file.name)
    assert got_file.name == file.name
  finally:
    if file and file.name:
      client.files.delete(name=file.name)

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_upload_get_delete_image",
        parameters=_UploadGetDeleteParameters(
            file_path="tests/data/google.png",
        ),
        exception_if_vertex='only supported in the Gemini Developer client',
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="upload_get_delete",
    test_table=test_table,
)

pytest_plugins = ("pytest_asyncio",)
