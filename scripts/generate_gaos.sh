#!/bin/bash
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

set -euo pipefail

# Paths for the two layouts this script runs in. Each default must exist in the
# detected layout; there is no cross-layout fallback.
#   github:  repo root, with .speakeasy/ and google/genai/_gaos/
#   google3: third_party/py/google/genai, with _gaos/ and the spec and Speakeasy
#            config under labs/language/genai/interactions/openapi/genai-next/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

die() {
  echo "Error: $*" >&2
  exit 1
}

if [[ "${REPO_ROOT}" == */third_party/py/google/genai ]]; then
  LAYOUT="google3"
  GOOGLE3_ROOT="${REPO_ROOT%/third_party/py/google/genai}"
  GENAI_NEXT_DIR="${GOOGLE3_ROOT}/labs/language/genai/interactions/openapi/genai-next"
  DEFAULT_SPEC_FILE="${GENAI_NEXT_DIR}/specs/genai/openapi.with-overlays.gaos.json"
  DEFAULT_SPEAKEASY_CONFIG_DIR="${GENAI_NEXT_DIR}/dist/sp_python/.speakeasy"
  DEFAULT_TARGET_GAOS_DIR="${REPO_ROOT}/_gaos"
elif [[ -d "${REPO_ROOT}/google/genai" ]]; then
  LAYOUT="github"
  DEFAULT_SPEC_FILE="${REPO_ROOT}/.speakeasy/openapi.json"
  DEFAULT_SPEAKEASY_CONFIG_DIR="${REPO_ROOT}/.speakeasy"
  DEFAULT_TARGET_GAOS_DIR="${REPO_ROOT}/google/genai/_gaos"
else
  die "unrecognized repo layout at ${REPO_ROOT} (expected a GitHub checkout" \
    "with google/genai/, or google3 third_party/py/google/genai)."
fi

# Parse optional CLI flags
SPEC_FILE=""
SPEAKEASY_CONFIG_DIR=""
TARGET_GAOS_DIR=""
GENERATOR_BIN_CLI=""
SYNC_GAOS_OUTPUT_BIN_CLI=""
SKIP_COMPILE=true

# Fails if option "$1" was not given a value ("$2").
require_value() {
  if [[ $# -lt 2 || -z "$2" || "$2" == -* ]]; then
    die "option '$1' requires a value."
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --spec|-s)
      require_value "$1" "${2:-}"
      SPEC_FILE="$2"
      shift 2
      ;;
    --speakeasy-config)
      require_value "$1" "${2:-}"
      SPEAKEASY_CONFIG_DIR="$2"
      shift 2
      ;;
    --output-dir|-o)
      require_value "$1" "${2:-}"
      TARGET_GAOS_DIR="$2"
      shift 2
      ;;
    --generator-bin)
      require_value "$1" "${2:-}"
      GENERATOR_BIN_CLI="$2"
      shift 2
      ;;
    --sync-bin)
      require_value "$1" "${2:-}"
      SYNC_GAOS_OUTPUT_BIN_CLI="$2"
      shift 2
      ;;
    --no-skip-compile)
      SKIP_COMPILE=false
      shift 1
      ;;
    --skip-compile)
      SKIP_COMPILE=true
      shift 1
      ;;
    *)
      die "unknown option '$1'."
      ;;
  esac
done

SPEC_FILE="${SPEC_FILE:-${DEFAULT_SPEC_FILE}}"
SPEAKEASY_CONFIG_DIR="${SPEAKEASY_CONFIG_DIR:-${DEFAULT_SPEAKEASY_CONFIG_DIR}}"
TARGET_GAOS_DIR="${TARGET_GAOS_DIR:-${DEFAULT_TARGET_GAOS_DIR}}"

[[ -f "${SPEC_FILE}" ]] || die "OpenAPI spec not found: ${SPEC_FILE}"
[[ -f "${SPEAKEASY_CONFIG_DIR}/gen.yaml" ]] \
  || die "Speakeasy config has no gen.yaml: ${SPEAKEASY_CONFIG_DIR}"

# Generator binary: --generator-bin > SPEAKEASY_GENERATOR_BIN > layout default.
# google3 only uses the Blaze-built generator, never one from PATH.
GENERATOR_BIN="${GENERATOR_BIN_CLI:-${SPEAKEASY_GENERATOR_BIN:-}}"
if [[ -z "${GENERATOR_BIN}" ]]; then
  if [[ "${LAYOUT}" == "google3" ]]; then
    GENERATOR_TARGET="//third_party/golang/github_com/speakeasy_api/openapi_generation/v/v2/cmd/generate"
    GENERATOR_BIN="${GOOGLE3_ROOT}/blaze-bin/${GENERATOR_TARGET#//}/generate"
    [[ -x "${GENERATOR_BIN}" ]] \
      || die "Speakeasy generator not built. Run: blaze build ${GENERATOR_TARGET}"
  elif command -v generate >/dev/null 2>&1; then
    GENERATOR_BIN="generate"
  else
    GENERATOR_BIN="${GOBIN:-${GOPATH:-${HOME}/go}/bin}/generate"
    [[ -x "${GENERATOR_BIN}" ]] || die "Speakeasy generator 'generate' not found." \
      "Run: git clone --depth 1 --branch \${SPEAKEASY_VERSION}" \
      "https://github.com/speakeasy-api/openapi-generation.git /tmp/openapi-generation" \
      "&& (cd /tmp/openapi-generation && go install ./cmd/generate)"
  fi
fi
command -v "${GENERATOR_BIN}" >/dev/null 2>&1 \
  || die "generator binary not found or not executable: ${GENERATOR_BIN}"

# Sync command: --sync-bin > SYNC_GAOS_OUTPUT_BIN > python3 sync_gaos_output.py.
SYNC_BIN="${SYNC_GAOS_OUTPUT_BIN_CLI:-${SYNC_GAOS_OUTPUT_BIN:-}}"
if [[ -n "${SYNC_BIN}" ]]; then
  [[ -x "${SYNC_BIN}" ]] || die "sync binary not found or not executable: ${SYNC_BIN}"
  SYNC_CMD=("${SYNC_BIN}")
else
  command -v python3 >/dev/null 2>&1 || die "python3 not found."
  SYNC_CMD=(python3 "${SCRIPT_DIR}/sync_gaos_output.py")
fi

STAGING_DIR="$(mktemp -d -t gaos_gen.XXXXXX)"
cleanup() {
  rm -rf "${STAGING_DIR}"
}
trap cleanup EXIT

# Stage .speakeasy config in staging dir
mkdir -p "${STAGING_DIR}/.speakeasy"
cp -r "${SPEAKEASY_CONFIG_DIR}/." "${STAGING_DIR}/.speakeasy/"

GEN_OPTS=("-skip-versioning")
if [[ "${SKIP_COMPILE}" == "true" ]]; then
  GEN_OPTS+=("-skip-compile")
fi

# The generator wants SPEAKEASY_LICENSE_TOKEN to be a signed license JWT. Those
# expire after 30 days, so CI stores a Speakeasy API key instead. If the value
# is not a JWT (header.payload.signature), exchange it for one using the same
# endpoint as the generator's own `./zero` bootstrap
# (internal/licensebootstrap/fetch.go: GET /v1/auth/validate -> license_jwt).
TOKEN_CANDIDATE="${SPEAKEASY_LICENSE_TOKEN:-${SPEAKEASY_API_KEY:-}}"
if [[ -n "${TOKEN_CANDIDATE}" && "${TOKEN_CANDIDATE}" != *.*.* ]]; then
  echo "Exchanging Speakeasy API key for a signed license token..."
  # The key is passed through the environment (not the command line or the
  # script source) so it doesn't show up in the process list or break quoting.
  # -I keeps the current directory off sys.path (e.g. genai/types.py would
  # shadow the stdlib `types` module).
  if ! FETCHED_TOKEN="$(SPEAKEASY_KEY_TO_EXCHANGE="${TOKEN_CANDIDATE}" python3 -I - <<'PY'
import json
import os
import sys
import urllib.error
import urllib.request

url = "https://app.speakeasy.com/v1/auth/validate"
req = urllib.request.Request(
    url,
    headers={
        "x-api-key": os.environ["SPEAKEASY_KEY_TO_EXCHANGE"],
        "Accept": "application/json",
    },
)
try:
  with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.load(resp)
except urllib.error.HTTPError as e:
  sys.exit(f"Speakeasy license exchange failed: HTTP {e.code} from {url}")
except (urllib.error.URLError, OSError, ValueError) as e:
  sys.exit(f"Speakeasy license exchange failed: {e}")

token = data.get("license_jwt")
if not token:
  sys.exit(
      "Speakeasy license exchange failed: no license_jwt in the response"
      " (is the API key for a workspace with a commercial license?)"
  )
print(token)
PY
  )"; then
    echo "Error: could not get a Speakeasy license token (see above)." >&2
    exit 1
  fi
  export SPEAKEASY_LICENSE_TOKEN="${FETCHED_TOKEN}"
fi

echo "Generating Python GAOS SDK using ${GENERATOR_BIN}..."
"${GENERATOR_BIN}" \
  -s "${SPEC_FILE}" \
  -o "${STAGING_DIR}" \
  -l python \
  "${GEN_OPTS[@]}"

# Locate generated source inside staging dir
SRC_GEN=""
for candidate in "${STAGING_DIR}/src/google/genai" "${STAGING_DIR}/google/genai"; do
  if [[ -d "${candidate}" ]]; then
    SRC_GEN="${candidate}"
    break
  fi
done

if [[ -z "${SRC_GEN}" ]]; then
  echo "Error: Generator did not produce expected output under ${STAGING_DIR}" >&2
  exit 1
fi

SYNC_ARGS=(--input-dir="${SRC_GEN}" --output-dir="${TARGET_GAOS_DIR}")
# GitHub defaults to httpx2 (see common.bara.sky).
if [[ "${LAYOUT}" == "github" ]]; then
  SYNC_ARGS+=(--httpx2-fallback)
fi

echo "Syncing and rewriting imports to ${TARGET_GAOS_DIR}..."
"${SYNC_CMD[@]}" "${SYNC_ARGS[@]}"

echo "GAOS SDK generation finished successfully!"
