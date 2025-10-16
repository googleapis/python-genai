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
"""Private chats for google.genai."""
# Imports all the public chats but change the
# public types to private types.

from .. import chats as public_chats
from ..chats import *  # pylint: disable=wildcard-import
from . import _transformers as private_transformers
from . import types as private_types
from . import models as private_models

public_chats.types = private_types
public_chats.t = private_transformers

public_chats.Content = private_types.Content
public_chats.ContentOrDict = private_types.ContentOrDict
public_chats.GenerateContentConfigOrDict = (
    private_types.GenerateContentConfigOrDict
)
public_chats.GenerateContentResponse = private_types.GenerateContentResponse
public_chats.Part = private_types.Part
public_chats.PartUnionDict = private_types.PartUnionDict

public_chats.AsyncModels = private_models.AsyncModels
public_chats.Models = private_models.Models
