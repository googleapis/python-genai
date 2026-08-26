# Copyright 2026 Google LLC
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

import json
from pathlib import Path

import pytest

from ... import types
from ...file_artifact_service import FileArtifactService


@pytest.fixture
def temp_service(tmp_path):
  return FileArtifactService(base_dir=tmp_path)


@pytest.mark.asyncio
async def test_save_artifact_creates_version_and_atomic_metadata(temp_service):
  data = b"raw_pcm_audio_content_test"
  part = types.Part(inline_data=types.Blob(data=data, mime_type="audio/pcm"))

  version = await temp_service.save_artifact(
      app_name="sample_app",
      user_id="user_1",
      session_id="session_abc",
      filename="test_audio.pcm",
      artifact=part,
      custom_metadata={"key": "val"},
  )
  assert version == 0

  # Check on-disk structure
  artifact_dir = (
      temp_service.base_dir
      / "users"
      / "user_1"
      / "sessions"
      / "session_abc"
      / "artifacts"
      / "test_audio.pcm"
  )
  payload_path = artifact_dir / "versions" / "0" / "test_audio.pcm"
  metadata_path = artifact_dir / "versions" / "0" / "metadata.json"

  assert payload_path.exists()
  assert payload_path.read_bytes() == data

  assert metadata_path.exists()
  meta = json.loads(metadata_path.read_text())
  assert (
      meta.get("fileName") == "test_audio.pcm"
      or meta.get("file_name") == "test_audio.pcm"
  )
  assert meta["version"] == 0
  assert (
      meta.get("mimeType") == "audio/pcm"
      or meta.get("mime_type") == "audio/pcm"
  )
  assert meta.get("customMetadata") == {"key": "val"} or meta.get(
      "custom_metadata"
  ) == {"key": "val"}
  assert "createTime" in meta or "create_time" in meta
  canonical_uri = meta.get("canonicalUri") or meta.get("canonical_uri")
  assert canonical_uri.startswith("file://")
  assert "test_audio.pcm" in canonical_uri


@pytest.mark.asyncio
async def test_multiple_versions(temp_service):
  part1 = types.Part(
      inline_data=types.Blob(data=b"v1_data", mime_type="audio/pcm")
  )
  part2 = types.Part(
      inline_data=types.Blob(data=b"v2_data", mime_type="audio/pcm")
  )

  v1 = await temp_service.save_artifact(
      app_name="app",
      user_id="u",
      session_id="s",
      filename="doc.pcm",
      artifact=part1,
  )
  v2 = await temp_service.save_artifact(
      app_name="app",
      user_id="u",
      session_id="s",
      filename="doc.pcm",
      artifact=part2,
  )
  assert v1 == 0
  assert v2 == 1

  versions = await temp_service.list_versions(
      app_name="app", user_id="u", session_id="s", filename="doc.pcm"
  )
  assert versions == [0, 1]

  # Test load
  loaded_v1 = await temp_service.load_artifact(
      app_name="app", user_id="u", session_id="s", filename="doc.pcm", version=0
  )
  assert loaded_v1.inline_data.data == b"v1_data"

  loaded_v2 = await temp_service.load_artifact(
      app_name="app", user_id="u", session_id="s", filename="doc.pcm", version=1
  )
  assert loaded_v2.inline_data.data == b"v2_data"

  # Load latest default
  loaded_latest = await temp_service.load_artifact(
      app_name="app", user_id="u", session_id="s", filename="doc.pcm"
  )
  assert loaded_latest.inline_data.data == b"v2_data"


@pytest.mark.asyncio
async def test_delete_artifact(temp_service):
  part = types.Part(inline_data=types.Blob(data=b"data", mime_type="audio/pcm"))
  await temp_service.save_artifact(
      app_name="app",
      user_id="u",
      session_id="s",
      filename="del.pcm",
      artifact=part,
  )
  await temp_service.delete_artifact(
      app_name="app", user_id="u", session_id="s", filename="del.pcm"
  )

  versions = await temp_service.list_versions(
      app_name="app", user_id="u", session_id="s", filename="del.pcm"
  )
  assert versions == []
