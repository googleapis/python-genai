# Changelog

## [0.6.0](https://github.com/googleapis/python-genai/compare/v0.5.0...v0.6.0) (2025-01-21)


### Features

* Add support for audio_timestamp to types.GenerateContentConfig (fixes [#132](https://github.com/googleapis/python-genai/issues/132)) ([116395b](https://github.com/googleapis/python-genai/commit/116395b23d2415407c01efb30cb6c1863a4a3032))
* Add support for case insensitive enum types. (fixes [#11](https://github.com/googleapis/python-genai/issues/11)) ([252f302](https://github.com/googleapis/python-genai/commit/252f302d3bb02271ba3e8953aeb4fb8fa7023fa6))
* Add support for class methods in the Tools for the GenerateContent Function ([5afa6bb](https://github.com/googleapis/python-genai/commit/5afa6bb9ac9445491bea6af28655535c78976a49))
* Add ThinkingConfig to generate content config. ([c23c42c](https://github.com/googleapis/python-genai/commit/c23c42c1bf012b36717dd21e86fdb7859b43b759))
* Implement client.files.download ([a034b77](https://github.com/googleapis/python-genai/commit/a034b77dc6c0806d791942d2a6ced4cf5973d2c3))
* Support BytesIO when uploading files ([4b490dc](https://github.com/googleapis/python-genai/commit/4b490dce9ead29fe28411b20801fc95a8617143c))
* Support lists in response_schema ([8ed933d](https://github.com/googleapis/python-genai/commit/8ed933dd4068add6983fc084df1cb434b444ba2a))
* Usability change to simplify generate content with uploaded files ([5c372ae](https://github.com/googleapis/python-genai/commit/5c372ae61914c75a5700297a8f2301f76379e926))


### Bug Fixes

* Fix count_tokens system_instruction and tools config ([056eaba](https://github.com/googleapis/python-genai/commit/056eabad0cd863d5729f423416a4961c5113c1a5))
* Fix models.list() with empty tuned models ([75409f1](https://github.com/googleapis/python-genai/commit/75409f12d9f531f126c427b3bd9a0b8d3bacabf7))
* Fixed the `bytes` type handling (the `base64.urlsafe_bencode` error) ([1bc161d](https://github.com/googleapis/python-genai/commit/1bc161d81c78afa35f21a24ee1840b5ed03f3a96))
* Project and location are required when using client in Vertex AI mode. ([d5859fa](https://github.com/googleapis/python-genai/commit/d5859fa8d89bb26b3c31ee3dab0deaf9c159e615))

### Documentation

* Add project description to README. ([384f413](https://github.com/googleapis/python-genai/commit/384f413666e8d2430a943163dd109814ee9b6137))
* Update formatting in README.md ([d33fb37](https://github.com/googleapis/python-genai/commit/d33fb37a082e04f512063d88bbe500a9acdbfb2c))
* Update models.list doc and code examples to include list base models ([f2e0c43](https://github.com/googleapis/python-genai/commit/f2e0c43417f4b6a7ca8b1b0e5bef97f68a8ff84b))
* Tool use example in docs ([87fe5b0](https://github.com/googleapis/python-genai/commit/87fe5b0cdfbf34c295398217185d857ca1413c02))
* Tool use example in README.md ([87fe5b0](https://github.com/googleapis/python-genai/commit/87fe5b0cdfbf34c295398217185d857ca1413c02))


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
