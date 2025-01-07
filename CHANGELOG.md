# Changelog

## [0.4.0](https://github.com/googleapis/python-genai/compare/v0.3.0...v0.4.0) (2025-01-07)


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

* Fix typo in code document ([f9243e8](https://github.com/googleapis/python-genai/commit/f9243e890aa42ae13b6f83dd885824b629a17cd3))
* Fix typo in CONTRIBUTING.md ([3e42644](https://github.com/googleapis/python-genai/commit/3e42644784304d45d0b0bfdc8279958109650576))

## [0.3.0](https://github.com/googleapis/python-genai/compare/v0.2.2...v0.3.0) (2024-12-17)


### BREAKING CHANGES
* contents must be passed to CreateCachedContentConfig instead as a parameter to create_cached_content.

### Features

* Add support for Pydantic default value in Automatic Function Calling.
* Add support for thought.
* Add support for streaming chat.
