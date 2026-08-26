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

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
import shutil
import tempfile
import time
from typing import Any, Optional, Union

from pydantic import Field

from . import _common
from . import types

logger = logging.getLogger(__name__)

_DEFAULT_FILE_MODE = 0o644
_METADATA_FILENAME = "metadata.json"


class FileArtifactVersion(_common.BaseModel):
  """Metadata describing a saved artifact version."""

  version: int = 0
  canonical_uri: str = ""
  custom_metadata: dict[str, Any] = Field(default_factory=dict)
  create_time: float = Field(default_factory=time.time)
  mime_type: Optional[str] = None
  file_name: Optional[str] = None
  display_name: Optional[str] = None


def _list_versions_on_disk(artifact_dir: Path) -> list[int]:
  versions_dir = artifact_dir / "versions"
  if not versions_dir.exists():
    return []
  versions: list[int] = []
  for entry in versions_dir.iterdir():
    if entry.is_dir() and entry.name.isdigit():
      versions.append(int(entry.name))
  return sorted(versions)


def _write_metadata(
    path: Path,
    *,
    filename: str,
    mime_type: Optional[str],
    version: int,
    canonical_uri: str,
    custom_metadata: Optional[dict[str, Any]] = None,
    display_name: Optional[str] = None,
) -> None:
  """Persists metadata describing an artifact version atomically."""
  metadata = FileArtifactVersion(
      version=version,
      canonical_uri=canonical_uri,
      custom_metadata=dict(custom_metadata or {}),
      create_time=time.time(),
      mime_type=mime_type,
      file_name=filename,
      display_name=display_name,
  )
  serialized = metadata.model_dump_json(by_alias=True, exclude_none=True)

  path.parent.mkdir(parents=True, exist_ok=True)
  fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
  tmp_path = Path(tmp_name)
  try:
    with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
      tmp_file.write(serialized)
    os.chmod(tmp_path, _DEFAULT_FILE_MODE)
    os.replace(tmp_path, path)
  except BaseException:
    tmp_path.unlink(missing_ok=True)
    raise


def _read_metadata(path: Path) -> Optional[FileArtifactVersion]:
  try:
    raw = path.read_text(encoding="utf-8")
    return FileArtifactVersion.model_validate_json(raw)
  except Exception as exc:
    logger.warning("Unreadable or invalid metadata at %s: %s", path, exc)
    return None


class FileArtifactService:
  """Executes physical disk operations to synchronously write and structure raw blobs."""

  def __init__(self, base_dir: Optional[Union[str, Path]] = None) -> None:
    if base_dir is None:
      self.base_dir = Path("./artifacts").resolve()
    else:
      self.base_dir = Path(base_dir).resolve()

  def _artifact_dir(
      self,
      app_name: str,
      user_id: str,
      session_id: Optional[str],
      filename: str,
  ) -> Path:
    if session_id:
      return (
          self.base_dir
          / "users"
          / user_id
          / "sessions"
          / session_id
          / "artifacts"
          / filename
      )
    return self.base_dir / "users" / user_id / "artifacts" / filename

  async def save_artifact(
      self,
      *,
      app_name: str,
      user_id: str,
      session_id: Optional[str] = None,
      filename: str,
      artifact: Union[types.Part, types.Blob, bytes],
      custom_metadata: Optional[dict[str, Any]] = None,
      display_name: Optional[str] = None,
  ) -> int:
    """Saves an artifact and its metadata to disk, returning the version ID."""
    return await asyncio.to_thread(
        self._save_artifact_sync,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=filename,
        artifact=artifact,
        custom_metadata=custom_metadata,
        display_name=display_name,
    )

  def _save_artifact_sync(
      self,
      *,
      app_name: str,
      user_id: str,
      session_id: Optional[str],
      filename: str,
      artifact: Union[types.Part, types.Blob, bytes],
      custom_metadata: Optional[dict[str, Any]] = None,
      display_name: Optional[str] = None,
  ) -> int:
    artifact_dir = self._artifact_dir(app_name, user_id, session_id, filename)
    versions_dir = artifact_dir / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)

    existing_versions = _list_versions_on_disk(artifact_dir)
    next_version = 0 if not existing_versions else max(existing_versions) + 1
    version_dir = versions_dir / str(next_version)
    version_dir.mkdir(parents=True, exist_ok=True)

    if hasattr(artifact, "inline_data") and artifact.inline_data:
      data = artifact.inline_data.data
      mime_type = artifact.inline_data.mime_type
    elif hasattr(artifact, "data") and hasattr(artifact, "mime_type"):
      data = artifact.data
      mime_type = artifact.mime_type
    elif isinstance(artifact, bytes):
      data = artifact
      mime_type = "application/octet-stream"
    else:
      raise ValueError(f"Unsupported artifact type: {type(artifact)}")

    if not isinstance(data, bytes):
      raise ValueError("Artifact data must be bytes.")

    payload_path = version_dir / filename
    payload_path.write_bytes(data)
    os.chmod(payload_path, _DEFAULT_FILE_MODE)

    canonical_uri = payload_path.resolve().as_uri()

    metadata_path = version_dir / _METADATA_FILENAME
    _write_metadata(
        metadata_path,
        filename=filename,
        mime_type=mime_type,
        version=next_version,
        canonical_uri=canonical_uri,
        custom_metadata=custom_metadata,
        display_name=display_name,
    )

    logger.debug(
        "Saved artifact %s version %d to %s",
        filename,
        next_version,
        version_dir,
    )
    return next_version

  async def load_artifact(
      self,
      *,
      app_name: str,
      user_id: str,
      filename: str,
      session_id: Optional[str] = None,
      version: Optional[int] = None,
  ) -> Optional[types.Part]:
    return await asyncio.to_thread(
        self._load_artifact_sync,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=filename,
        version=version,
    )

  def _load_artifact_sync(
      self,
      *,
      app_name: str,
      user_id: str,
      session_id: Optional[str],
      filename: str,
      version: Optional[int],
  ) -> Optional[types.Part]:
    artifact_dir = self._artifact_dir(app_name, user_id, session_id, filename)
    versions = _list_versions_on_disk(artifact_dir)
    if not versions:
      return None
    target_version = version if version is not None else versions[-1]
    if target_version not in versions:
      return None

    version_dir = artifact_dir / "versions" / str(target_version)
    payload_path = version_dir / filename
    metadata_path = version_dir / _METADATA_FILENAME

    if not payload_path.exists():
      return None

    data = payload_path.read_bytes()
    metadata = _read_metadata(metadata_path)
    mime_type = metadata.mime_type if metadata else "application/octet-stream"

    return types.Part(inline_data=types.Blob(data=data, mime_type=mime_type))

  async def list_versions(
      self,
      *,
      app_name: str,
      user_id: str,
      filename: str,
      session_id: Optional[str] = None,
  ) -> list[int]:
    return await asyncio.to_thread(
        self._list_versions_sync,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=filename,
    )

  def _list_versions_sync(
      self,
      *,
      app_name: str,
      user_id: str,
      session_id: Optional[str],
      filename: str,
  ) -> list[int]:
    artifact_dir = self._artifact_dir(app_name, user_id, session_id, filename)
    return _list_versions_on_disk(artifact_dir)

  async def delete_artifact(
      self,
      *,
      app_name: str,
      user_id: str,
      filename: str,
      session_id: Optional[str] = None,
  ) -> None:
    await asyncio.to_thread(
        self._delete_artifact_sync,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=filename,
    )

  def _delete_artifact_sync(
      self,
      *,
      app_name: str,
      user_id: str,
      session_id: Optional[str],
      filename: str,
  ) -> None:
    artifact_dir = self._artifact_dir(app_name, user_id, session_id, filename)
    if artifact_dir.exists():
      shutil.rmtree(artifact_dir)
      logger.debug("Deleted artifact directory %s", artifact_dir)
