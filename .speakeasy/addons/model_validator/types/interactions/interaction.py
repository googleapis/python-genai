# pylint: skip-file
from typing import Any, List
import pydantic


@classmethod
def _maybe_coerce_outputs(cls, data: Any) -> Any:
  legacy_lyria_models = ("lyria-3-pro-preview", "lyria-3-clip-preview")
  if not isinstance(data, dict):
    return data
  if (
      not isinstance(data.get("model"), str)
      or data["model"] not in legacy_lyria_models
  ):
    return data
  if "steps" in data:
    return data
  if "outputs" not in data:
    return {**data, "steps": []}
  outputs = data["outputs"]
  if not isinstance(outputs, list):
    return {**data, "steps": []}

  coerced = {**data}
  coerced.pop("outputs")
  coerced["steps"] = [{"type": "model_output", "content": outputs}]
  return coerced


@pydantic.model_validator(mode="before")
@classmethod
def _coerce_outputs_to_steps(cls, data: Any) -> Any:
  return cls._maybe_coerce_outputs(data)


# Applied to `Interaction(BaseModel)`: use `super().model_construct(...)`
# rather than `pydantic.BaseModel.model_construct(...)` so `cls` stays bound to
# `Interaction` through its MRO.
@classmethod
def model_construct(cls, _fields_set=None, **values):
  # Coerce legacy lyria `outputs` -> `steps` here as well: validators
  # do not run on model_construct (used by deferred SSE parsing).
  return super().model_construct(
      _fields_set, **cls._maybe_coerce_outputs(values)
  )


@pydantic.model_validator(mode="after")
def _populate_output_helpers(self):
  steps = self.steps if isinstance(self.steps, list) else []

  text_parts: List[str] = []
  collecting = False
  for step in reversed(steps):
    step_type = getattr(step, "type", None)
    if step_type == "user_input":
      break
    if step_type == "thought":
      continue
    if step_type != "model_output":
      if collecting:
        break
      continue
    content = getattr(step, "content", None)
    if not isinstance(content, list):
      continue
    should_stop = False
    for item in reversed(content):
      if getattr(item, "type", None) == "text":
        collecting = True
        text = getattr(item, "text", None)
        text_parts.append(text if isinstance(text, str) else "")
      elif collecting:
        should_stop = True
        break
    if should_stop:
      break
  # Always derived from the trailing model-output text; a str, "" when none.
  self.output_text = "".join(reversed(text_parts))

  output_image = None
  output_audio = None
  output_video = None
  for step in reversed(steps):
    step_type = getattr(step, "type", None)
    if step_type == "user_input":
      break
    if step_type != "model_output":
      continue
    content = getattr(step, "content", None)
    if not isinstance(content, list):
      continue
    for item in reversed(content):
      content_type = getattr(item, "type", None)
      if content_type == "image" and output_image is None:
        output_image = item
      if content_type == "audio" and output_audio is None:
        output_audio = item
      if content_type == "video" and output_video is None:
        output_video = item
  if output_image is not None and self.output_image is None:
    self.output_image = output_image
  if output_audio is not None and self.output_audio is None:
    self.output_audio = output_audio
  if output_video is not None and self.output_video is None:
    self.output_video = output_video
  return self
