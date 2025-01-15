# Changelog

## [0.5.0](https://github.com/googleapis/python-genai/compare/v0.4.0...v0.5.0) (2025-01-13)


### Features

* Support API keys for VertexAI mode generate_content ([0e4b0e5](https://github.com/googleapis/python-genai/commit/0e4b0e5ee0ecfef34f6576d8aab24cf0554bbd85))
* Support list models to return base models ([0f713f1](https://github.com/googleapis/python-genai/commit/0f713f177e84ab7a2071c635ec7231ee4fbf4657))
* Support parsing 'interrupted' field in Live Python SDK. ([eab2c4a](https://github.com/googleapis/python-genai/commit/eab2c4a9513d4ce58270b82e10698a945c01aaca))
* Use `ser_json_byte` `val_json_bytes` in bytes type public interface ([1176e43](https://github.com/googleapis/python-genai/commit/1176e43c2f87edf5566512b8f3c433b77684f87b))


### Bug Fixes

* Update header type ([62c45f9](https://github.com/googleapis/python-genai/commit/62c45f9ecdb0e7bc539d22a967672762fa6c50a8))


### Documentation

* Correct description of path parameter that only path-like object is supported ([336498b](https://github.com/googleapis/python-genai/commit/336498baebee2e064e2f44d9c6d96903bcfd63bf))

## [0.4.0](https://github.com/googleapis/python-genai/compare/v0.3.0...v0.4.0) (2025-01-08)


### ⚠ BREAKING CHANGES

* Make Imagen upscale_factor a required argument, make upscale config optional

### Features

* ApiClient - support timeout in HttpOptions ([b22286f](https://github.com/googleapis/python-genai/commit/b22286fa3cd48a7918ffa2acaa40e53f3c8bb5d8))
* Enable response_logprobs and logprobs for Google AI ([5586f3d](https://github.com/googleapis/python-genai/commit/5586f3d650964547c3e7cafa1165f9c7d1306529))
* Support function_calls quick accessor in GenerateContentResponse class ([81b8a23](https://github.com/googleapis/python-genai/commit/81b8a236b85081aa02fc4e38e27189bc2deb5cfb))


### Bug Fixes

* Change string type to int type ([5c15243](https://github.com/googleapis/python-genai/commit/5c1524370214128752905faefcf2690592b2dc90))
* FunctionCallCancellation ids type. ([b0e46b7](https://github.com/googleapis/python-genai/commit/b0e46b72aeef938414a68efd773bdac0b25c05d2))
* Gracefully catch error if streamed json does not meet schema validation (fixes [#14](https://github.com/googleapis/python-genai/issues/14)) ([f494432](https://github.com/googleapis/python-genai/commit/f494432900d60e64cbef69424918904ddbe255b1))
* Update RealtimeClientLiveMessage realtime content parameter field. ([4340939](https://github.com/googleapis/python-genai/commit/4340939d17ee38cad0d8d64aafcde5c3ef89f78f))


### Documentation

* Add readme example for Chats module ([830f0f5](https://github.com/googleapis/python-genai/commit/830f0f56e6663c173454a47ca97867031bd89819))
* Fix typo in code document ([f9243e8](https://github.com/googleapis/python-genai/commit/f9243e890aa42ae13b6f83dd885824b629a17cd3))
* Fix typo in CONTRIBUTING.md ([3e42644](https://github.com/googleapis/python-genai/commit/3e42644784304d45d0b0bfdc8279958109650576))


### Code Refactoring

* Make Imagen upscale_factor a required argument, make upscale config optional ([b06629f](https://github.com/googleapis/python-genai/commit/b06629f879b548a209e8517e92f5923d1f25c3a8))

## [0.3.0](https://github.com/googleapis/python-genai/compare/v0.2.2...v0.3.0) (2024-12-17)


### BREAKING CHANGES
* contents must be passed to CreateCachedContentConfig instead as a parameter to create_cached_content.

### Features

* Add support for Pydantic default value in Automatic Function Calling.
* Add support for thought.
* Add support for streaming chat.
