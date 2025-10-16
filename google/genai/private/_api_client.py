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
"""Private api_client for google.genai."""
# Imports all the public api_client but change the
# public types to private types.

from .. import _api_client as public_api_client
from .._api_client import *  # pylint: disable=wildcard-import
from . import errors as private_errors
from . import types as private_types


public_api_client.HttpOptions = private_types.HttpOptions
public_api_client.HttpOptionsOrDict = private_types.HttpOptionsOrDict
public_api_client.SdkHttpResponse = private_types.HttpResponse
public_api_client.HttpRetryOptions = private_types.HttpRetryOptions
public_api_client.errors = private_errors
