# Changelog

## [1.28.0](https://github.com/googleapis/python-genai/compare/v1.27.0...v1.28.0) (2025-07-30)


### Features

* Add images quick accessor to GenerateImagesResponse ([2e43d91](https://github.com/googleapis/python-genai/commit/2e43d91e3c8b33df1c621a09fdc782f53824fb51))
* Allow methods in models to return headers in sdk_http_response by default. ([fa6675a](https://github.com/googleapis/python-genai/commit/fa6675a9ca4d2042d61ad7f47c65add65e7b4987))
* Allow methods in tuning to return headers in sdk_http_response by default ([dd19971](https://github.com/googleapis/python-genai/commit/dd199715304dcad188e4711d1c8997c812ef3227))
* Define StringDict type alias for better readability ([0f4613f](https://github.com/googleapis/python-genai/commit/0f4613f35fb0b0be8cf31b6dfdf08b4c65903df3))
* Increase buffer size to read response body from HTTP client ([ae2d790](https://github.com/googleapis/python-genai/commit/ae2d79051995f753fa997a9c636cd2dd8fd04a59))
* Support retry configuration at request level ([417e655](https://github.com/googleapis/python-genai/commit/417e655d1fb00633b2a700942fe7f0b895bc25aa))


### Bug Fixes

* Allow empty proj/location and api key when overriding base_url ([79f7bfc](https://github.com/googleapis/python-genai/commit/79f7bfcd1cada39a2fe4902d55a7b0ffaa499cbe))
* Retry async when seeing aiohttp ClientConnectorError, ClientOSError, ServerDisconnectedError ([b0d18de](https://github.com/googleapis/python-genai/commit/b0d18decb49d17840f9e5d27bc6603a6827e400b))

## [1.27.0](https://github.com/googleapis/python-genai/compare/v1.26.0...v1.27.0) (2025-07-22)


### Features

* Add image_size field for Vertex Imagen 4 generation ([df52660](https://github.com/googleapis/python-genai/commit/df526605bbca6befb645418f4b3f267aeb83e99a))
* Return headers for list method in all modules. ([dd3df9b](https://github.com/googleapis/python-genai/commit/dd3df9b19e7cce249773794139f86d0c87ca64f7))


### Documentation

* Copy improvements and minor changes to instructions. ([235ee99](https://github.com/googleapis/python-genai/commit/235ee9935e589144dbd42aea2e0721142b33db1b))
* Update batches and tunings doc ([97a3494](https://github.com/googleapis/python-genai/commit/97a34945bad64cd2b3c88e2b14142397551a0947))
* Update extra_body docstring ([633eca3](https://github.com/googleapis/python-genai/commit/633eca3c96739d2bb8a32ceb22654ca7cab7a829))

## [1.26.0](https://github.com/googleapis/python-genai/compare/v1.25.0...v1.26.0) (2025-07-16)


### Features

* Add `addWatermark` parameter to the edit image configuration. ([a5b1545](https://github.com/googleapis/python-genai/commit/a5b1545ece2df77c4a99449e2066ac98bc5201b5))
* Adding codegen instructions to guide LLMs to generate code with the Google GenAI SDK ([d82634b](https://github.com/googleapis/python-genai/commit/d82634bdc0aa053bdad0da158ee06845ec890d6d))


### Bug Fixes

* **live:** Enhance security by moving api key from query parameters to header ([d78add3](https://github.com/googleapis/python-genai/commit/d78add3d1429b9d9aad0e0e3ea09b06d2293616a))


### Documentation

* Update generated video resolution config docstring ([d06254c](https://github.com/googleapis/python-genai/commit/d06254ccd94d6d90a20769bb003f8eb5dfb62553))

## [1.25.0](https://github.com/googleapis/python-genai/compare/v1.24.0...v1.25.0) (2025-07-09)


### Features

* Add new languages for Imagen 4 prompt language ([cbd643e](https://github.com/googleapis/python-genai/commit/cbd643ebc64a64dd51f3d96844107010d88083c5))
* Make t_schema in Gemini API reusable from Genai Procesors. ([922eaf5](https://github.com/googleapis/python-genai/commit/922eaf5020737bd1a3cf66df5ddd29f156311228))


### Bug Fixes

* Improve code dependency to make `types` more self-contained ([7d0a7d8](https://github.com/googleapis/python-genai/commit/7d0a7d8de13caee8e80f7136bb841c9e97d7e1e0))
* **python:** Fix response.parse when response_json_schema is provided. ([babb01f](https://github.com/googleapis/python-genai/commit/babb01fc4e4e60c0442f35ad1c6bd9e55a9646da))


### Documentation

* Add extra_body example to README.md ([0b077bf](https://github.com/googleapis/python-genai/commit/0b077bfc0d7a0bafc97402fe8b58efe255aabe1d))
* Mention both API-key environment variables. ([50fff0c](https://github.com/googleapis/python-genai/commit/50fff0c54844e8fa70d7d4a60f5c9f5ec6e69ea3))
* Regenerate docs for 1.24.0 ([fe7ed6d](https://github.com/googleapis/python-genai/commit/fe7ed6d07f13dd42bf1908d0e308143d58541129))

## [1.24.0](https://github.com/googleapis/python-genai/compare/v1.23.0...v1.24.0) (2025-07-01)


### Features

* Support Batches delete ([5d0a4e6](https://github.com/googleapis/python-genai/commit/5d0a4e6887c396c3b464a33943b8421ad47d11c5))
* Support different media input in Vertex Live API ([8b0a703](https://github.com/googleapis/python-genai/commit/8b0a7032c8ebed662fd2096d7ff2dc0cde4db75a))


### Bug Fixes

* Force httpx if the client was instantiated with an httpx.AsyncBaseTransport ([4851590](https://github.com/googleapis/python-genai/commit/48515900b9550e5e68a820385af004da9e93c72e))
* Retry on exception instead of a status code ([fc78107](https://github.com/googleapis/python-genai/commit/fc781074d76fcdbeb1351344210775d5a1e9de17))


### Documentation

* Add I2V and V2V generate_videos examples in Python README file ([858f738](https://github.com/googleapis/python-genai/commit/858f73893599f647254886637fdb5315d9c9f081))
* Regenerate docs for 1.23.0 ([4273da2](https://github.com/googleapis/python-genai/commit/4273da23ffcc6ef16b1f979735cf0dd7b7c9c691))

## [1.23.0](https://github.com/googleapis/python-genai/compare/v1.22.0...v1.23.0) (2025-06-27)


### Features

* Enable Vertex Multimodal Dataset as input to supervised fine-tuning. ([15cf810](https://github.com/googleapis/python-genai/commit/15cf810ccf7249d44896024a5a29be49d31396fd))


### Bug Fixes

* Broken async stream when using aiohttp ([231b4c1](https://github.com/googleapis/python-genai/commit/231b4c10772dd04097d6afc8fc4a4ef18a13a91e))


### Documentation

* Add hint for base64 string ([70eb9c1](https://github.com/googleapis/python-genai/commit/70eb9c1172f48f6c052f5f18758c53957e34d494))
* Add mcp example in README ([81d3831](https://github.com/googleapis/python-genai/commit/81d38319c04c31905d0c2684e7c23f4db68ba307))
* Regenerate docs for 1.22.0 ([6f7f223](https://github.com/googleapis/python-genai/commit/6f7f2236f0f6f3e64556683eae7c1c336a70214c))

## [1.22.0](https://github.com/googleapis/python-genai/compare/v1.21.1...v1.22.0) (2025-06-25)


### Features

* Add compressionQuality enum for generate_videos ([b132387](https://github.com/googleapis/python-genai/commit/b132387be80c74b003acfa362be34c8477728ce5))
* Add enhance_input_image and image_preservation_factor fields for upscale_image ([cdcd4f5](https://github.com/googleapis/python-genai/commit/cdcd4f5282fdc7d526dd93c929786f110afe6f28))
* Allow users to access headers for generateContent method and generateContentStream ([80c8964](https://github.com/googleapis/python-genai/commit/80c8964f29fe64e44fc2b09ec135914d5ef0f0d6))
* Expose the responseJsonSchema in GenerateContentConfig ([714452f](https://github.com/googleapis/python-genai/commit/714452fb6d8167e55a3d72c20bcf9f6d54a5def4))
* Improve __repr__ for pydantic objects. ([80ab054](https://github.com/googleapis/python-genai/commit/80ab054f2a2ea6e6475ae4ff971861fd86f8dbb1))
* Support Batches create/get/list/cancel in Gemini Developer API ([5ab8a56](https://github.com/googleapis/python-genai/commit/5ab8a5641a18f68ae52bf7c9bf6694842348cef3))
* Support IntEnums when processing JSON schemas ([6cc2bdb](https://github.com/googleapis/python-genai/commit/6cc2bdb9e36005fe91e873b09861cc3ca9b81bda))


### Bug Fixes

* Keep chunk content history when thought summaries are enabled in the stream response ([91e7246](https://github.com/googleapis/python-genai/commit/91e7246dd1894d2dd75dadb05385f6e994914c66))
* The send_client_content function with Blob input. ([8491e4c](https://github.com/googleapis/python-genai/commit/8491e4cd5176912b262b69cb43b38fecf8ffb9e5))


### Documentation

* Improve generate images documentation ([15b2144](https://github.com/googleapis/python-genai/commit/15b21443d060819f4b87297ed3a76766ea5d630f))
* Update description of thinking_budget. ([7c2ae32](https://github.com/googleapis/python-genai/commit/7c2ae3256faffda752ff3e0d16aac5c1bb97e45a))

## [1.21.1](https://github.com/googleapis/python-genai/compare/v1.21.0...v1.21.1) (2025-06-19)


### Bug Fixes

* Re-raise exception during retries ([d6a223c](https://github.com/googleapis/python-genai/commit/d6a223cbb1d85c339bd907e0770665c6c2d0e42f))


### Documentation

* Regenerate docs for 1.21.0 ([feaf5fe](https://github.com/googleapis/python-genai/commit/feaf5fe900d9bcf371bf935db346edfd61143b44))

## [1.21.0](https://github.com/googleapis/python-genai/compare/v1.20.0...v1.21.0) (2025-06-18)


### Features

* Add retries to http client ([aed2f48](https://github.com/googleapis/python-genai/commit/aed2f48705db0b9a7d320055e6111247f7b88d76))
* Enable json schema for controlled output and function declaration. ([624c8e7](https://github.com/googleapis/python-genai/commit/624c8e75fd1e3048bed3ab9a9a333387bc570f01))
* Support extra_body in HttpOptions ([273c9b8](https://github.com/googleapis/python-genai/commit/273c9b870aa363321a56147945c271e9698c8251))


### Bug Fixes

* Update aiohttp client's SSL handling and configure trust_env by default to match httpx ([462dd3e](https://github.com/googleapis/python-genai/commit/462dd3e33b8334198508aefc3090242e3bcd2727))


### Documentation

* Add instructions to use the aiohttp options for faster async performance and client_args/async_client_args in HttpOptions ([0820ed6](https://github.com/googleapis/python-genai/commit/0820ed645e2b3258152909119bb8eb39925dbcfd))
* Add proxy instruction ([f90af49](https://github.com/googleapis/python-genai/commit/f90af49ffaab6ee468d6b973bd3d72287c163db0))
* Regenerate docs for 1.20.0 ([66f198a](https://github.com/googleapis/python-genai/commit/66f198a34668bd597ae5c721dcf08c6807d0fa19))

## [1.20.0](https://github.com/googleapis/python-genai/compare/v1.19.0...v1.20.0) (2025-06-11)


### Features

* Add datastore_spec field for VertexAISearch ([a26d998](https://github.com/googleapis/python-genai/commit/a26d99815fc471d73f9aa1a628a65ba6c67d94b6))
* Add support for Veo frame interpolation and video extension ([1648dda](https://github.com/googleapis/python-genai/commit/1648dda65ef8ce0056f61312f3a508ef81fa99a1))
* Add Video.from_file() support in Python SDK ([7eb5b07](https://github.com/googleapis/python-genai/commit/7eb5b07bf1ffb16761825d96b4c1a536bc395701))
* RAG - Introducing context storing for Gemini Live API. ([c00c4a9](https://github.com/googleapis/python-genai/commit/c00c4a9bf534bf742950294973e1fcd0979230d0))
* Use aiohttp in async APIs to lower latency if aiohttp is installed, otherwise use default httpx in async APIs ([2f448bc](https://github.com/googleapis/python-genai/commit/2f448bc2b8d2b09b6abc0ddba829610c227cf979))


### Bug Fixes

* **chats:** Relax the constraint on chat turns ([046fa87](https://github.com/googleapis/python-genai/commit/046fa87d5d048cf619e3c40320b592990edeebfb))
* Make function calls asynchronous in subsequent AFC calls ([3e429a0](https://github.com/googleapis/python-genai/commit/3e429a0fd66387b17f30584cc780f8781c3cd53d))


### Documentation

* Generate docs for 1.19.0 ([4df9230](https://github.com/googleapis/python-genai/commit/4df9230944e21474b9c31d771f3d109b195aef71))

## [1.19.0](https://github.com/googleapis/python-genai/compare/v1.18.0...v1.19.0) (2025-06-04)


### Features

* Add enhance_prompt field for Gemini Developer API generate_videos ([92ca562](https://github.com/googleapis/python-genai/commit/92ca562e21216bd1dcd29ea113fc302b9982536f))
* Add FunctionResponse.from_mcp_response() convenience function for parsing MCP responses to send to subsequent model calls. ([e1b980d](https://github.com/googleapis/python-genai/commit/e1b980d63e19396be1d9128cb7bab200eb5269c5))
* Enable url_context for Vertex ([99551c9](https://github.com/googleapis/python-genai/commit/99551c9bc009998bbc277f5ac919e3bab039a97e))
* **python:** Support `GEMINI_API_KEY` as environment variable for setting API key. ([ae2392c](https://github.com/googleapis/python-genai/commit/ae2392c4c0afc87c86b3abd11d89e6441a854470))


### Bug Fixes

* Enable FunctionDeclaration parser when future is imported ([589b520](https://github.com/googleapis/python-genai/commit/589b5205e89a030bc5565b290fe175c599b99195))

## [1.18.0](https://github.com/googleapis/python-genai/compare/v1.17.0...v1.18.0) (2025-05-30)


### Features

* Adding `thought_signature` field to the `Part` to store the signature for thoughts. ([303f906](https://github.com/googleapis/python-genai/commit/303f9069f508e544fe2f9c680a700624057b6341))
* Include UNEXPECTED_TOOL_CALL enum value to FinishReason for Vertex AI APIs. ([ccbc66e](https://github.com/googleapis/python-genai/commit/ccbc66e199b23cecf3a4bd0680c6a52b1260cedb))
* Support ephemeral auth tokens as API keys for live connections in Python. ([db1d7ee](https://github.com/googleapis/python-genai/commit/db1d7eec869525d41ffc7b1570bd597b12fab323))

### Bug Fixes

* Ignore struct types when performing forward compatibility field filtering ([7024011](https://github.com/googleapis/python-genai/commit/702401102a34e21e94201c9cc48aa7fe2db68958))

### ⚠ BREAKING CHANGES TO EXPERIMENTAL FEATURES

* Removed `live_ephemeral_connect`, ephemeral auth tokens can now be used as API keys ([db1d7ee](https://github.com/googleapis/python-genai/commit/db1d7eec869525d41ffc7b1570bd597b12fab323))
* Rename LiveEphemeralParameters to LiveConnectConstraints. ([6719faf](https://github.com/googleapis/python-genai/commit/6719faf6be905b192397cfc361283f2bb9cad8de))



## [1.17.0](https://github.com/googleapis/python-genai/compare/v1.16.1...v1.17.0) (2025-05-28)


### ⚠ BREAKING CHANGES TO EXPERIMENTAL FEATURES

* Remove unsupported Lyria enum for music generation mode

### Features

* Add generate_audio field for private testing of video generation ([c2bccf3](https://github.com/googleapis/python-genai/commit/c2bccf373806be03c4e69973df8157dba6a2d0dc))
* Send automatic function calling None responses as NULL to the model ([8446e3d](https://github.com/googleapis/python-genai/commit/8446e3deb514fd0bbc929d8dc8bcf79264bc0b45))
* Support API keys for live in VertexAI mode ([5b5a750](https://github.com/googleapis/python-genai/commit/5b5a750fb25a2cdece16ca4027364ff0c9a591ef))
* Support new fields in FileData, GenerationConfig, GroundingChunkRetrievedContext, RetrievalConfig, Schema, TuningJob, VertexAISearch, ([b07c549](https://github.com/googleapis/python-genai/commit/b07c549fa0d380629e5e25956291cb0693b23c94))


### Documentation

* Fix comment typo for Modality.AUDIO ([d16cf1e](https://github.com/googleapis/python-genai/commit/d16cf1e9b1c2d210b911d3b3f7da5da891148c39)), closes [#620](https://github.com/googleapis/python-genai/issues/620)
* Fix README typo. ([59ae8e0](https://github.com/googleapis/python-genai/commit/59ae8e0d18449b4eba109cfc5697d62b149eda6d))


### Miscellaneous Chores

* Remove unsupported Lyria enum for music generation mode ([98ff507](https://github.com/googleapis/python-genai/commit/98ff507d368d48066c701256c60718b620b098e2))

## [1.16.1](https://github.com/googleapis/python-genai/compare/v1.16.0...v1.16.1) (2025-05-20)


### Bug Fixes

* Fix broken tool use in generate content. ([bad81ad](https://github.com/googleapis/python-genai/commit/bad81adddb8783927c4aafef77e3c40e2553dd14))

## [1.16.0](https://github.com/googleapis/python-genai/compare/v1.15.0...v1.16.0) (2025-05-19)


### Features

* Add `time range filter` to Google Search Tool ([b79c414](https://github.com/googleapis/python-genai/commit/b79c414f759b64f356d5510a3eb8bbc5af076db0))
* Add basic support for async function calling. ([6258dad](https://github.com/googleapis/python-genai/commit/6258dad0f9634b5e40e6562353e1911fe3c2d1a6))
* Add Files module with Files.upload, .get and .delete ([f4dd629](https://github.com/googleapis/python-genai/commit/f4dd6297a54089d572e1cfb67135bc4d78c68c19))
* Add live proactivity_audio and enable_affective_dialog ([778d6a2](https://github.com/googleapis/python-genai/commit/778d6a20c924ea524a882af39bd66b13d9163598))
* Add Lyria Realtime music generation support for Python ([e746417](https://github.com/googleapis/python-genai/commit/e746417efdf4f992bd57a1e0c6ec30f56c3305e6))
* Add Lyria Realtime Music Types ([18d2407](https://github.com/googleapis/python-genai/commit/18d2407d59879468ce56780ae8d14f3a023b7cd7))
* Add MCP telemetry usage to Python SDK. ([0bc6ab5](https://github.com/googleapis/python-genai/commit/0bc6ab51704da57fb2fdb9800ce5e781305b9a6a))
* Add multi-speaker voice config ([1d73827](https://github.com/googleapis/python-genai/commit/1d73827df37f4350716837f5fc8ef0dfafcd1c4f))
* Add support for lat/long in search. ([50ddf98](https://github.com/googleapis/python-genai/commit/50ddf98bb9f063c85668ea099f1fdd175f6350a4))
* Add support for MCP in Python SDK. ([dcd7819](https://github.com/googleapis/python-genai/commit/dcd78192f920cce524c76c655c1e1c9327228d20))
* Add support for MCP in Python SDK. ([3f531c3](https://github.com/googleapis/python-genai/commit/3f531c3fab24e3c5358001e08e62979870da33ae))
* Add telemetry headers for synchronous calls with MCP ([638c7f4](https://github.com/googleapis/python-genai/commit/638c7f4b29365216e7c611d934af80d0ef0e6176))
* Add Video FPS, and enable start/end_offset for MLDev ([bfaa1df](https://github.com/googleapis/python-genai/commit/bfaa1dfa56c76080805fab97079fe0ea5cab27c9))
* Raises an error when there are duplicate tool names. ([301c699](https://github.com/googleapis/python-genai/commit/301c69940aea5ad41737b4331fe292af449a794a))
* Support customer-managed encryption key in cached content ([e951337](https://github.com/googleapis/python-genai/commit/e951337b09b5ea26f13389a0e03e710ceabc6c42))
* Support ephemeral token creation in Python ([141d540](https://github.com/googleapis/python-genai/commit/141d540aaad0fa423b4c932449e51a9bff658b43))
* Support models.get/delete/update in Java ([aeaadf8](https://github.com/googleapis/python-genai/commit/aeaadf8f31dc30bfc61f36c431fc827481356f85))
* Support Url Context Retrieval tool ([cbd1ea6](https://github.com/googleapis/python-genai/commit/cbd1ea6954823671241bfb897ceb6ee8d60ed08b))
* Support using ephemeral token in Live session connection in Python ([141d540](https://github.com/googleapis/python-genai/commit/141d540aaad0fa423b4c932449e51a9bff658b43))


### Bug Fixes

* Clone config when parsing for MCP tools ([5feeb60](https://github.com/googleapis/python-genai/commit/5feeb60ab779e33dc062965d6962458dffb69615))
* Fix imports if mcp is not installed ([e46eb05](https://github.com/googleapis/python-genai/commit/e46eb0533f01e34059c4ee1c7f384ba13f98e5ab))
* Live tools ([032d1fe](https://github.com/googleapis/python-genai/commit/032d1fe7a3e16d68fd56b28e03267ceec1d0a991))
* Prevent MCP label from being appended multiple times if they already exist ([974ba07](https://github.com/googleapis/python-genai/commit/974ba076a7ae5ba447a4d1b5d749f0fec70f5580))
* Typo in error message. ([9a45bfd](https://github.com/googleapis/python-genai/commit/9a45bfd3842d0f44f917d89e1d71c04b5fe837d7))
* Update parse_config_for_mcp_tools to remove the deep copy of the config and filter tools ([d4dd2bb](https://github.com/googleapis/python-genai/commit/d4dd2bb2b4126ca48c551684181336c10319fc3a))
* Use inspect.cleandoc on function docstrings in generate_function_declaration. ([bc664d9](https://github.com/googleapis/python-genai/commit/bc664d9b1ee6bc1ff236daadcb0c771ef9931e92))


### Documentation

* Add docs for enum fields ([2634e01](https://github.com/googleapis/python-genai/commit/2634e016377272dfc512dd281f0e18bb91b527b4))
* Regenerate docs for 1.15.0 ([a3fc532](https://github.com/googleapis/python-genai/commit/a3fc532594eff8f01749f6275c506f7516e8ab73))


### Miscellaneous Chores

* Fix Lyria method name for JS, update parameters type ([0a5d68d](https://github.com/googleapis/python-genai/commit/0a5d68da4c983ffa73624746786d6fd66d7fa290))
* Release 1.16.0 ([181d5b7](https://github.com/googleapis/python-genai/commit/181d5b7eaa152241b30f7f5fa4e7544528f5bbde))

## [1.15.0](https://github.com/googleapis/python-genai/compare/v1.14.0...v1.15.0) (2025-05-13)


### Features

* Support display_name for Blob class when calling Vertex AI ([266da4a](https://github.com/googleapis/python-genai/commit/266da4aafa693866f5df9c8bbf53ffd2a5755c9f))
* Support tuning checkpoints ([26a87ea](https://github.com/googleapis/python-genai/commit/26a87ea5cdb68cb6933a7432de5595ac6cda5f48))
* Typo fixes in a few files. ([b9c9e32](https://github.com/googleapis/python-genai/commit/b9c9e32efaefdab54414a2bc1285b1014e7385fd))


### Bug Fixes

* Improve thread safety for sync requests (fixes [#775](https://github.com/googleapis/python-genai/issues/775)) ([d88b8d4](https://github.com/googleapis/python-genai/commit/d88b8d42785749c0bc2f846af6cbf2f3614c7e2c))


### Documentation

* Improve docs for response_mime_type and response_schema. Relate to [#297](https://github.com/googleapis/python-genai/issues/297) ([832b715](https://github.com/googleapis/python-genai/commit/832b71531dc29c3b13259e691a29a7d51327346d))
* Regenerate docs for 1.14.0 ([32808f3](https://github.com/googleapis/python-genai/commit/32808f3d77c84cb25ee6fe1181bceb53b57adfcf))

## [1.14.0](https://github.com/googleapis/python-genai/compare/v1.13.0...v1.14.0) (2025-05-07)


### Features

* Add `Tool.enterprise_web_search` field ([731c5a3](https://github.com/googleapis/python-genai/commit/731c5a35ad4d48c324160e0686a6603d335ccd59))
* Add support for Grounding with Google Maps ([1efc057](https://github.com/googleapis/python-genai/commit/1efc057b1daebbebab8c5601d6917341fba9c7c4))
* Enable input transcription for Gemini API. ([157b16b](https://github.com/googleapis/python-genai/commit/157b16b8df40095b81e7206c7a16d03188744c37))


### Bug Fixes

* Add retry logic for missing x-goog-upload-status header for python ([5bb70fc](https://github.com/googleapis/python-genai/commit/5bb70fc6c16cdd5c1057033583e6f52beb53282e))
* Fix resource warning raised by unclosed httpx client ([a3a6d34](https://github.com/googleapis/python-genai/commit/a3a6d34ae4d8fe614764c8368cbb71cdd9087506))
* Raise ValueError when 'x-goog-upload-status' header is not present in file upload response ([dfdea36](https://github.com/googleapis/python-genai/commit/dfdea36b6f98d7cb59905a29f35f6bdee4aca359))


### Documentation

* Regenerate docs for 1.13.0 ([5269212](https://github.com/googleapis/python-genai/commit/5269212aa956955c4c85b4f46bbdcf1efcb07060))

## [1.13.0](https://github.com/googleapis/python-genai/compare/v1.12.1...v1.13.0) (2025-04-30)


### Features

* Add models.delete and models.update to manage tuned models ([53a3282](https://github.com/googleapis/python-genai/commit/53a32824fcb8e8e516e2aaac1da4cc7c363020a3))
* Add support for live grounding metadata ([b904cba](https://github.com/googleapis/python-genai/commit/b904cba686750906a020e17599d91aae9ee44f97))
* Make min_property, max_property, min_length, max_length, example, patter fields available for Schema class when calling Gemini API ([52919cb](https://github.com/googleapis/python-genai/commit/52919cb1a22a580c9428a5d128e098324871fed4))
* Support setting the default base URL in clients via set_default_base_urls() ([2b82d72](https://github.com/googleapis/python-genai/commit/2b82d729b0628812c048e87e79363419b6682fdf))
* Support using the passed credentials in AsyncLive::connect ([#738](https://github.com/googleapis/python-genai/issues/738)) ([568cfd2](https://github.com/googleapis/python-genai/commit/568cfd25479202ee816e6ebe0c350c3f8c9fd9a3))


### Bug Fixes

* Do not raise error for `default` field in Schema for Gemini API calls ([1d3d1c9](https://github.com/googleapis/python-genai/commit/1d3d1c9c01ffd9ae0d7f3c52b85470960aab23f5))
* Set `propertyOrdering` when schema is specified as `dict` or `types.Schema`. ([48eebe0](https://github.com/googleapis/python-genai/commit/48eebe0dbe16a438074012da89d3b44ec5f05c5d))


### Documentation

* Add a link for where to find the Google Cloud project id, API key and location ([916bd6e](https://github.com/googleapis/python-genai/commit/916bd6e538950481832d263a3c979aa0f20acd49))

## [1.12.0](https://github.com/googleapis/python-genai/compare/v1.11.0...v1.12.0) (2025-04-23)


### Features

* Add additional realtime input fields ([bef6385](https://github.com/googleapis/python-genai/commit/bef638546d820911172581f0666ae0f1270085f5))
* Add py.typed so MyPy interprets this as a typed library ([b137b4d](https://github.com/googleapis/python-genai/commit/b137b4dae363045ac1980d10cdda4712a309ef3c))
* Automatically determine mime_type for Part.from_uri ([b9d3be1](https://github.com/googleapis/python-genai/commit/b9d3be1e87a3e4260c16a3c36e0c728b330f831a))
* Generate _live_converters.py ([d526a08](https://github.com/googleapis/python-genai/commit/d526a08c6ed5dfee26d1332829cac114f0132d54))
* Introduce from_json_schema classmethod to Schema class to allow conversion from JSONSchema class object to Schema class object ([899fa1a](https://github.com/googleapis/python-genai/commit/899fa1ae9a9ec7a5cf7d2dfe72267780fcc4fdc8))
* Support `default` field in Schema when users call Gemini API ([1e56add](https://github.com/googleapis/python-genai/commit/1e56add36c9a1ebcb3499d9f3ea2a9af37edf3cd))


### Documentation

* Regenerate docs for 1.11.0 ([473bf4b](https://github.com/googleapis/python-genai/commit/473bf4b6b5a69e5324a5d4bac0fe852351338c43))

## [1.11.0](https://github.com/googleapis/python-genai/compare/v1.10.0...v1.11.0) (2025-04-16)


### Features

* Add support for model_selection_config to GenerateContentConfig ([fdb0662](https://github.com/googleapis/python-genai/commit/fdb066288228ca101042ed9b11f783ed0d5f2799))
* Introduce json_schema quick accessor in Schema class to convert Google's Schema class into JSONSchema class. ([6e55222](https://github.com/googleapis/python-genai/commit/6e55222895a6639d41e54202e3d9a963609a391f))
* Support audio transcription in Vertex Live API ([9678aba](https://github.com/googleapis/python-genai/commit/9678ababb31282130e3cb9669e3670b627f91d86))
* Support configuring the underlying httpx client by allowing the caller to pass client arguments via HttpOptions. ([5130e0a](https://github.com/googleapis/python-genai/commit/5130e0a622210400d8d09399a06df55aa4af6a0e))
* Support RealtimeInputConfig, and language_code in SpeechConfig in python ([807f098](https://github.com/googleapis/python-genai/commit/807f098dedd0f885147fb10db7f79af9230999e0))
* Support user passing in async function to async generate_content and async generate_content_stream for automatic function calling ([33d190a](https://github.com/googleapis/python-genai/commit/33d190a77a198acfc857eff9677c88ed65e99758))
* Update VertexRagStore ([c4558e5](https://github.com/googleapis/python-genai/commit/c4558e5f65555d5a5352e4276c714392d594a3fa))


### Bug Fixes

* Get SSL_CERT_FILE or SSL_CERT_DIR environment variables for proper SSL handshake in API client. They are not automatically retrieved in httpx ([5782a5f](https://github.com/googleapis/python-genai/commit/5782a5f8a0bd1b3c741ea13b917d7d0091e9e12f))
* Update tests to use the pro 2.5 model gemini-2.5-pro-preview-03-25 ([fde4a8a](https://github.com/googleapis/python-genai/commit/fde4a8a484a5ab8cd0abadaaf108c552927f1976))

## [1.10.0](https://github.com/googleapis/python-genai/compare/v1.9.0...v1.10.0) (2025-04-09)


### ⚠ BREAKING CHANGES

* remove Part.from_video_metadata

### Features

* Add adapter size 2 for Gemini 2.0 Tuning ([959df89](https://github.com/googleapis/python-genai/commit/959df89e322efd4ed74f1c186a293b6f8fb7ee6e))
* Add domain to Web GroundingChunk ([9a75d48](https://github.com/googleapis/python-genai/commit/9a75d4885056771625f1af9ae735d61db9e7dc3c))
* Add session resumption. ([6e80ae7](https://github.com/googleapis/python-genai/commit/6e80ae77eba78607b91429168da20d618af9d3f0))
* Add thinking_budget to ThinkingConfig for Gemini Thinking Models ([71863e0](https://github.com/googleapis/python-genai/commit/71863e00c187c4eb9a379780f0a871235768a555))
* Add traffic type to GenerateContentResponseUsageMetadata ([925f983](https://github.com/googleapis/python-genai/commit/925f9836e1a6baf65adb5de5154870c1ec2621db))
* Add transcription support for MLDev ([c0a1b5c](https://github.com/googleapis/python-genai/commit/c0a1b5cdc169bfed61c69ffd8a08c0bffaaa80ce))
* Add types for configurable speech detection ([ae4ecee](https://github.com/googleapis/python-genai/commit/ae4ecee9562b71a292b61c63d33853568ab37f14))
* Add types to support continuous sessions with a sliding window ([7099e1e](https://github.com/googleapis/python-genai/commit/7099e1e99ce9e80a3b1080dcd1141a51e1990fea))
* Add UsageMetadata to LiveServerMessage ([018846a](https://github.com/googleapis/python-genai/commit/018846ae3e1f73d91522b8606e611152b7f63002))
* Added support for Context Window Compression ([e5c646c](https://github.com/googleapis/python-genai/commit/e5c646c106407a6c424a5d7fc6d022a395bac430))
* Populate X-Server-Timeout header when a request timeout is set. ([2af7b67](https://github.com/googleapis/python-genai/commit/2af7b67e811ae2b2e920c090006b2054193b404b))
* Remove experimental warnings for generate_videos and operations ([fa6007a](https://github.com/googleapis/python-genai/commit/fa6007ae9fb755e7cafb518985c96d54dd572a43))
* Remove experimental warnings from live api. ([007d1b1](https://github.com/googleapis/python-genai/commit/007d1b15e31000366352449c39679848dd7f622a))
* Support media resolution ([ef64f8a](https://github.com/googleapis/python-genai/commit/ef64f8a49171f2e05765ed7141d8ee51409a1ac7))


### Bug Fixes

* Remove Part.from_video_metadata ([c0947ab](https://github.com/googleapis/python-genai/commit/c0947ab20f75ed1c67985f7a2fdea04a5959de68))
* Upload file should support timeout (in milliseconds) configuration from http_options per request or from client ([5f3e895](https://github.com/googleapis/python-genai/commit/5f3e895276c94536ed797bcdca7fb913f95ddb01))


### Miscellaneous Chores

* Release 1.10.0 ([c136e41](https://github.com/googleapis/python-genai/commit/c136e4164d0c26530871c56653e21fc30caee511))

## [1.9.0](https://github.com/googleapis/python-genai/compare/v1.8.0...v1.9.0) (2025-04-01)


### Features

* Add specialized `send` methods to the live api ([9c4e4dc](https://github.com/googleapis/python-genai/commit/9c4e4dcdff508230f635c5d174486b08b87f86c9))
* Expose generation_complete, input/output_transcription & input/output_audio_transcription to SDK for Vertex Live API ([e5685ad](https://github.com/googleapis/python-genai/commit/e5685adc7a064b511ddb490ef0aaf27f3070775f))
* Merge GenerationConfig into LiveConnectConfig ([d22535e](https://github.com/googleapis/python-genai/commit/d22535e700178f27e458a02868cd2c06d5470e34))


### Bug Fixes

* Make response arg in APIError class constructor optional. [#572](https://github.com/googleapis/python-genai/issues/572) ([7b3f4a4](https://github.com/googleapis/python-genai/commit/7b3f4a4c50646c29293c0196b471b7bf3a29f102))


### Documentation

* Docstring improvements ([77f5356](https://github.com/googleapis/python-genai/commit/77f53566bbff3a715d2c7e5e83ada61ffd80ac96))

## [1.8.0](https://github.com/googleapis/python-genai/compare/v1.7.0...v1.8.0) (2025-03-26)


### Features

* Add engine to VertexAISearch ([21f0394](https://github.com/googleapis/python-genai/commit/21f03941e23173d5c4bfce8551e9f64410a4cd95))
* Add IMAGE_SAFTY enum value to FinishReason ([3a65fb0](https://github.com/googleapis/python-genai/commit/3a65fb0e841b183d42023aef37e22207cdc9829f))
* Add MediaModalities for ModalityTokenCount ([fb2509c](https://github.com/googleapis/python-genai/commit/fb2509c471a42a3144d7b25e63be54d32608851c))
* Add Veo 2 generate_videos support in Go SDK ([55b2923](https://github.com/googleapis/python-genai/commit/55b2923de0b925ad5487d1584331cb093773a325))
* Allow title property to be sent to Gemini API. Gemini API now supports the title property, so it's ok to pass this onto both Vertex and Gemini API. ([f2f92a7](https://github.com/googleapis/python-genai/commit/f2f92a739a764f1eae20e932fdea6a3305305f77))
* **chats:** Allow user to create chat session with list of ContentDict ([43c5379](https://github.com/googleapis/python-genai/commit/43c5379aa0a6da1f742ab0eada72cbff0b2bed40)), closes [#467](https://github.com/googleapis/python-genai/issues/467)
* Move set event loop into try except logic when setting auth lock ([d04b6a6](https://github.com/googleapis/python-genai/commit/d04b6a65129960d6e70acec2879afbd8f7c5b0e0))
* Save prompt safety attributes in dedicated field for generate_images ([e5bbb0e](https://github.com/googleapis/python-genai/commit/e5bbb0e6b77f12e7e6877ae0e976fda3f8beb604))
* Support new UsageMetadata fields ([122cdc8](https://github.com/googleapis/python-genai/commit/122cdc86f1c7381f04f6c8ab3ea86409fcb85661))


### Bug Fixes

* Improve logging for response.parsed (fixes [#455](https://github.com/googleapis/python-genai/issues/455)) ([64012dd](https://github.com/googleapis/python-genai/commit/64012dd6a6c1877114100f52c10a45a7f7ff885e))
* Schema transformer logic fix. ([f64bcba](https://github.com/googleapis/python-genai/commit/f64bcba552156c1f344f8c03932a24c0a4f9c222))
* Set event loop before asyncio.Lock() to ensure threading safety ([be2d9c6](https://github.com/googleapis/python-genai/commit/be2d9c61176f8330166e7912e233fb07fa82e4a8))
* Surface complete error details from backend ([38f5beb](https://github.com/googleapis/python-genai/commit/38f5bebba79182f78c4aa921861151626c79a84d))
* **chats:** Raise error when `types.Content` is passed to `send_message()` to correctly adhere to type annotation. To migrate code previously passing `content = types.Content(...)` to `send_message()`, pass `content.parts` instead.

### Documentation

* Log warning to users that Part.from_video_metadata will be deprecated. ([2d12f54](https://github.com/googleapis/python-genai/commit/2d12f544bc3f8d1e2720855f0fe3519881baaeb0))

## [1.7.0](https://github.com/googleapis/python-genai/compare/v1.6.0...v1.7.0) (2025-03-18)


### Features

* Bump up the websockets version for proxy support ([b996c4b](https://github.com/googleapis/python-genai/commit/b996c4b62be8c4d108dbe572372a2c31661e9bcc))
* Leverage httpx connection pooling and avoid instantiation of httpx.Client or httpx.AsyncClient for each call ([2ac5129](https://github.com/googleapis/python-genai/commit/2ac5129d4005d797f29df0a213e2455d7d730b43))


### Bug Fixes

* **chats:** Fix duplicate history when appending AFC history ([e4b1d8a](https://github.com/googleapis/python-genai/commit/e4b1d8af03be5579ff6cb0ba42dd0d3d65126892))
* **chats:** Raise error when `types.Content` is passed to `send_message()` to correctly adhere to type annotation. To migrate code previously passing `content = types.Content(...)` to `send_message()`, pass `content.parts` instead.
* Fix incorrect casing of upload status and url headers in Files API. httpx.Response returns 'x-goog-upload-status', but we were checking for 'X-Goog-Upload-Status'. Also clean up upload_file and download_file requests. ([2ac5129](https://github.com/googleapis/python-genai/commit/2ac5129d4005d797f29df0a213e2455d7d730b43))


### Documentation

* Use consistent terminology for Gemini Developer API and Vertex AI ([7f1cc22](https://github.com/googleapis/python-genai/commit/7f1cc22e6220d4550726bd75c0dff922698d674e))

## [1.5.0](https://github.com/googleapis/python-genai/compare/v1.4.0...v1.5.0) (2025-03-07)


### Features

* Determine mime_type from local images ([5e84ddc](https://github.com/googleapis/python-genai/commit/5e84ddc8d4265069e6a03c9a99ff6891cc641297))
* Enable generate_videos for Gemini Developer API ([4a242f6](https://github.com/googleapis/python-genai/commit/4a242f6f759a5e3fd1435b548d8dda38091b9cee))
* Enable image to video for generate_videos ([787354b](https://github.com/googleapis/python-genai/commit/787354bf96d7a4fc479d9e8bd432e76ab54ab54c))
* Expand files.download to work on Video and GeneratedVideo objects ([8d4d6fd](https://github.com/googleapis/python-genai/commit/8d4d6fd6271b3f74d3efae676fc08418b9bb5cda))
* Support asynchronously upload and download files using httpx ([498c01d](https://github.com/googleapis/python-genai/commit/498c01da1d2820b97b2218022b7e42840453e739))


### Bug Fixes

* Fix incorrect unit for `timeout_in_seconds` in HttpOptions. ([a9be9a2](https://github.com/googleapis/python-genai/commit/a9be9a20691249bacf162d97ef6664883102edc7))
* Fix Video.show() when uri and video_bytes are provided ([3477c40](https://github.com/googleapis/python-genai/commit/3477c40cf89eb8006b6a0877710ec77cdb1edeff))

## [1.4.0](https://github.com/googleapis/python-genai/compare/v1.3.0...v1.4.0) (2025-03-05)


### Features

* Add response_id and create_time to GenerateContentResponse ([b46ed36](https://github.com/googleapis/python-genai/commit/b46ed361d9c0845880a1447ee42dd3c0f6f7a886))
* Allow non-content types in generate_content ([cbaaf4a](https://github.com/googleapis/python-genai/commit/cbaaf4ae19e17f4fafb48e8671c10786095e2936))
* Enable Live API initial connect to accept functions directly, in addition to just FunctionDeclaration ([91b1d3e](https://github.com/googleapis/python-genai/commit/91b1d3ee85fd32e9243e3a2da4d10a763e4d0005))
* Enable minItem, maxItem, nullable for Schema type when calling Gemini API. ([867ce70](https://github.com/googleapis/python-genai/commit/867ce70cf4a7ebd52554af3d494f73fd3cd4f6b6))
* Implement get history to return comprehensive or curated chat history ([92deda1](https://github.com/googleapis/python-genai/commit/92deda1b86c27c4f93691d4f4056ed64ba84d6a8))
* Support aspect ratio for edit_image ([5423a58](https://github.com/googleapis/python-genai/commit/5423a58f3abea2b468973c0c071ced6547f6cef1))


### Bug Fixes

* Allow user do batch generate content when passing a list of strings ([cbaaf4a](https://github.com/googleapis/python-genai/commit/cbaaf4ae19e17f4fafb48e8671c10786095e2936))
* Fix chats.send_message_stream curated history ([bcf2be0](https://github.com/googleapis/python-genai/commit/bcf2be03ae6d51957052cacfb8ed905045cc6f77))
* Log warn instead of raise error for GenerateContentResponse.text quick accessor when there are mixed part types ([55a0638](https://github.com/googleapis/python-genai/commit/55a0638075d89b873aea581e2012a0951cbcf7fb))
* Remove the keyword parameter requirement for UserContent and ModelContent ([0cc292f](https://github.com/googleapis/python-genai/commit/0cc292f5b61dcc2756c2110038c93c0c23b29c1d))

## [1.3.0](https://github.com/googleapis/python-genai/compare/v1.2.0...v1.3.0) (2025-02-24)


### Features

* Add generate_videos (Veo 2) support for Python ([e9e2be7](https://github.com/googleapis/python-genai/commit/e9e2be73d5a2f6a03d6a2a665cf35e96f2ed97cd))
* Add sdk logger instance (fixes [#278](https://github.com/googleapis/python-genai/issues/278)) ([cf281b5](https://github.com/googleapis/python-genai/commit/cf281b58195be1dd374e4754e432603ac215202f))
* Introduce response.executable_code and response.code_execution_result quick accessors for GenerateContentResponse class ([3725ddf](https://github.com/googleapis/python-genai/commit/3725ddf44a0df04f6fac0bd5295f45ed20b4a8fe))
* Introduce UserContent and ModelContent to facilitate easier content creation ([c8cfef8](https://github.com/googleapis/python-genai/commit/c8cfef85ca1f7901e802800f580915a14340cae7))
* Native async client support using httpx ([c38da8d](https://github.com/googleapis/python-genai/commit/c38da8d4425a92bd6ba483abccc3dbeafbf8daa4))
* Provide a public property for determining the module backend. ([8e561de](https://github.com/googleapis/python-genai/commit/8e561de04965bb8766db87ad8eea7c57c1040442))


### Bug Fixes

* Enable sending empty input to Live API as turn complete ([99a5510](https://github.com/googleapis/python-genai/commit/99a55100e1c4e91f53b22881fbff67e62f6fb99d))
* Fix automatic function calling warning message logic. ([b99da95](https://github.com/googleapis/python-genai/commit/b99da95ae0b986d77853c917931bdfa94c6b7714))
* Fix duplicate get_function_response_parts in (async) generate_content_stream and ensure chunk isn't empty before get_function_response_parts ([d4193e6](https://github.com/googleapis/python-genai/commit/d4193e6eb22d62c61b2727600171eb06780bfa18))
* Properly handle empty json response with headers for list models ([859ebc3](https://github.com/googleapis/python-genai/commit/859ebc3dc51aab9834b9034b5a1a205bcc72d25d))


### Documentation

* Add docs for error handling ([#317](https://github.com/googleapis/python-genai/issues/317)) ([6e1cb82](https://github.com/googleapis/python-genai/commit/6e1cb82704f6cb05b67191a319190c5ce0f67d9c))
* Add instruction on how to disable automatic function calling. ([f8b12d5](https://github.com/googleapis/python-genai/commit/f8b12d53567585094f7e7b1d015b89c993f480de))
* Regenerate docs for 1.2.0 ([30a3493](https://github.com/googleapis/python-genai/commit/30a34931d200feb12da54e978ea1f4a4a3d1e82e))
* Remove negative_prompt from image samples (fixes [#339](https://github.com/googleapis/python-genai/issues/339)) ([81e18f0](https://github.com/googleapis/python-genai/commit/81e18f053048ff4b3d2c5dde0726234d51cc8290))
* Update docs for models modules ([d96bba2](https://github.com/googleapis/python-genai/commit/d96bba29326113dba46ff16932deeb50618b8d8c))

## [1.2.0](https://github.com/googleapis/python-genai/compare/v1.1.0...v1.2.0) (2025-02-12)


### Features

* Enable Media resolution for Gemini API. ([6cdf61d](https://github.com/googleapis/python-genai/commit/6cdf61d09f0dec0b27f2be6a0487ec5f4792d62f))
* Support property_ordering in response_schema (fixes [#236](https://github.com/googleapis/python-genai/issues/236)) ([01b15e3](https://github.com/googleapis/python-genai/commit/01b15e32d3823a58d25534bb6eea93f30bf82219))


### Bug Fixes

* Default to list base models for async models list ([d3226b7](https://github.com/googleapis/python-genai/commit/d3226b7ce9fde115e503da7f9108d735fc89325c))
* Remove Type import from types.py that get's shadowed by API Type type. (fixes [#310](https://github.com/googleapis/python-genai/issues/310)) ([78f58c3](https://github.com/googleapis/python-genai/commit/78f58c3f63ec1d9fb916e81f9b962d5b65b13ec2))
* Use typing_extensions.TypedDict for TypedDict types (fixes [#189](https://github.com/googleapis/python-genai/issues/189)) ([996562a](https://github.com/googleapis/python-genai/commit/996562afed6d19b20bef343262e4c8820559c2d6))


### Documentation

* Client initialization using environmental variables. ([e4c2ffc](https://github.com/googleapis/python-genai/commit/e4c2ffcdb5ddd68ded5f3e2b98c0b44afe91ca1b))
* Fix File.expiration_time description (fixes [#318](https://github.com/googleapis/python-genai/issues/318)) ([729f619](https://github.com/googleapis/python-genai/commit/729f619bdc88f0d775fda3b9f1a75a527ddf90ac))
* Fix files.upload docs to use 'file' instead of 'path' (fixes [#306](https://github.com/googleapis/python-genai/issues/306)) ([2b35d0c](https://github.com/googleapis/python-genai/commit/2b35d0ca4e74b67f98e64da88286148370be9b6f))

## [1.1.0](https://github.com/googleapis/python-genai/compare/v1.0.0...v1.1.0) (2025-02-10)


### Features

* Add support for typing.Literal in response_schema (fixes [#264](https://github.com/googleapis/python-genai/issues/264)) ([384c4eb](https://github.com/googleapis/python-genai/commit/384c4eb7bac7ac867db8f19777c33e01daff89ef))
* Allow converting a function into FunctionDeclaration with api option ([408e28f](https://github.com/googleapis/python-genai/commit/408e28fc9892996eb1cb617de3cf7ce658deed16))
* Support generate content config for each chat turn ([ca19100](https://github.com/googleapis/python-genai/commit/ca1910026d7e425c1f9adb13779ec43bc2b9d99e))
* Tuning - `Tuning.tune` for Gemini API no longer blocks until the tuning operation is resolved ([fcf8888](https://github.com/googleapis/python-genai/commit/fcf88881698eabfa7d808df0f1353aa6bcc54cb8))


### Bug Fixes

* Remove duplicate function invocations and ensure automatic function calling can be disabled in generate_content_stream ([0958fbe](https://github.com/googleapis/python-genai/commit/0958fbe4ce68c09a6b665fcacb2e3a16dfd822d2))
* Response_schema generation for pydantic fields with type Optional[list] and Optional[MyBaseModel] now work correctly (fixes [#246](https://github.com/googleapis/python-genai/issues/246)) ([8330561](https://github.com/googleapis/python-genai/commit/833056195bb7fe7c7e45095df2eea748f48de49c))
* Support dict response_schema with 'any_of' key ([75f5056](https://github.com/googleapis/python-genai/commit/75f505637c89df50120e3ea25c6379fa49b54abf))
* Common - Do not fail when server returns unknown enum values on Python &lt;3.11 ([843d86d](https://github.com/googleapis/python-genai/commit/843d86d38699be5f6acc58e5e5a915acab8018be))


### Documentation

* Add docs on how to structure `contents` (fixes [#274](https://github.com/googleapis/python-genai/issues/274)) ([da356cb](https://github.com/googleapis/python-genai/commit/da356cb12d9b68fe9ccae0fec1c059399e7f9685))
* Regenerate docs for 1.0 ([fbee816](https://github.com/googleapis/python-genai/commit/fbee81625178fe9d39c7856bcae01ebf570b154c))
* Update model names in README, fix function calling example ([11c0274](https://github.com/googleapis/python-genai/commit/11c0274fbac5c82e39dac4e99ac7237cd9705e0b))

## [1.0.0](https://github.com/googleapis/python-genai/compare/v0.8.0...v1.0.0) (2025-02-05)


### ⚠ BREAKING CHANGES

* Remove deprecated field: `deprecated_response_payload`

### Features

* Add labels for GenerateContent requests ([3e3b82d](https://github.com/googleapis/python-genai/commit/3e3b82dcdc8d50852a9fdd452c8e0957bb4493de))
* Add Union support to response_schema ([eedf4f1](https://github.com/googleapis/python-genai/commit/eedf4f12aea9f5a0d4056d6f14a91b14db1903cf))
* Support automatic function calling in models.generate_content_stream and send_message_stream, sync and async mode ([7c9f8b5](https://github.com/googleapis/python-genai/commit/7c9f8b5833e393e5879fd267abf3a34d122a5d1d))


### Bug Fixes

* Avoid false test failure by skipping incompatible test case for python 3.13 ([7f10e55](https://github.com/googleapis/python-genai/commit/7f10e550db4767ab172f5f5b00eda484cb0141d6))
* Default to list base models (instead of tuned models) ([ef48f0d](https://github.com/googleapis/python-genai/commit/ef48f0dfcae1811ddc3160e368a5ef25a535ee25))
* Handle pydantic model type recognition gracefully for python 3.9 and 3.10 ([4a38fdf](https://github.com/googleapis/python-genai/commit/4a38fdf53fd689fdab611dbcaebc9570c7d46bd5))
* Raise error when Gemini API response_schema has 'default' or 'anyof' fields ([c50bca0](https://github.com/googleapis/python-genai/commit/c50bca00c814b39a98fc6aacba0c4c429fed0570))
* Remove redundant contents in Automatic Function Calling history ([5510595](https://github.com/googleapis/python-genai/commit/5510595eb18ad0a0af34ce63df1685b49e03ce10))
* Remove unsupported parameter from Gemini API ([f8addb5](https://github.com/googleapis/python-genai/commit/f8addb544e545100ae7342621910a2338072ddc6))


### Documentation

* Remove experimental classification from description. ([b14ac57](https://github.com/googleapis/python-genai/commit/b14ac57b07d4e7794d83f2b2123a4df80890f772))
* Remove thoughts examples and update tests ([af3b339](https://github.com/googleapis/python-genai/commit/af3b339a9d58e25cb3baa6fd3d0b1d078c620f9d))
* Update documentation on how to set api version using genai client ([6fd4425](https://github.com/googleapis/python-genai/commit/6fd442520d1b59003fd5fcd24d395b9790caec6f))
* Update instruction on function calling experience in `ANY` mode. ([451cf98](https://github.com/googleapis/python-genai/commit/451cf989e2a917884475cf66fce1d809a7495b53))


### Code Refactoring

* Remove deprecated field: `deprecated_response_payload` ([197fa46](https://github.com/googleapis/python-genai/commit/197fa46c9639799b8d71ddf92ab372140dc5b65b))

## [0.8.0](https://github.com/googleapis/python-genai/compare/v0.7.0...v0.8.0) (2025-01-30)


### ⚠ BREAKING CHANGES

* Rename files.upload argument to "file" instead of "path".

### Features

* Add enhanced_prompt to GeneratedImage class ([76c810b](https://github.com/googleapis/python-genai/commit/76c810b6bb82bde4cc4fe9754e0bbcc85e10a4c4))
* Added Operation and PredictOperation (internal module) ([309dd26](https://github.com/googleapis/python-genai/commit/309dd26cb3aa761bfae7070ffa5eab23b2a5a75c))
* Support global endpoint natively in Vertex ([f4530b0](https://github.com/googleapis/python-genai/commit/f4530b0af972d0b5e376e7463af235b8378e0694))
* Support unknown enum values ([da448b3](https://github.com/googleapis/python-genai/commit/da448b3cb2bf5d6cba6fdefa8d15365253fe0384))


### Bug Fixes

* Streaming in Vertex AI Express ([ff78b7b](https://github.com/googleapis/python-genai/commit/ff78b7b0277800e2b4b9e9958a87688383422d29))


### Documentation

* Correct generate content with uploaded file example ([8cea052](https://github.com/googleapis/python-genai/commit/8cea052ac148890a343f14b7185e394646802b41))


### Miscellaneous Chores

* Rename files.upload argument to "file" instead of "path". ([f68aa1f](https://github.com/googleapis/python-genai/commit/f68aa1f63f04629f9eb8629c5b1359f500f89a47))

## [0.7.0](https://github.com/googleapis/python-genai/compare/v0.6.0...v0.7.0) (2025-01-28)


### ⚠ BREAKING CHANGES

* Remove skip_project_and_location_in_path from async models.list
* remove "tuning.distill"
* Change asynchronous streaming output to an awaitable async iterator for client.aio.models.generate_content_stream and client.aio.chat.send_message_stream
* Remove pillow as a required dependency
* rename batches.list method signature.
* make Part, FunctionDeclaration, Image, and GenerateContentResponse classmethods argument keyword only
* Remove skip_project_and_location_in_path from HttpOption
* Renamed FunctionDeclaration class functions to reflect the fact that they work off of the `Callable` type not just functions.
* Moved the HttpOptions class into types.py, by making it autogenerated. This causes the following breaking change:
* rename generate_image() to generate_images(), rename GenerateImageConfig to GenerateImagesConfig, rename GenerateImageResponse to GenerateImagesResponse, rename GenerateImageParameters to GenerateImagesParameters

### Features

* [genai-modules][models] Add HttpOptions to all method configs for models. ([76fdde7](https://github.com/googleapis/python-genai/commit/76fdde7138b7bc3bd1e761bca753610fbb83a1af))
* Add support for enhance_prompt to model.generate_image ([d09e14e](https://github.com/googleapis/python-genai/commit/d09e14ea77de455c545c07ef0e4d0735c21521af))
* Added support for the new HttpOptions class in the per request options overrides. ([ad57025](https://github.com/googleapis/python-genai/commit/ad5702512ee78ad7bcda6233a7d1eafaaaf50e1f))
* Change asynchronous streaming output to an awaitable async iterator for client.aio.models.generate_content_stream and client.aio.chat.send_message_stream ([0c124eb](https://github.com/googleapis/python-genai/commit/0c124eba8909e77336a7c22681d57080d6f1a6ad))
* Enable enum support in the GenerateContentConfig.response_schema ([fe82e10](https://github.com/googleapis/python-genai/commit/fe82e1065095eabfe97cd197ebcea5b73efb01cd))
* Handle a wider variety of response_schemas - primitives and nested lists. ([24fffea](https://github.com/googleapis/python-genai/commit/24fffea93a6c127826a16a4183ff38a4376a4d5f))
* Images - Added Image.mime_type ([71a8f1d](https://github.com/googleapis/python-genai/commit/71a8f1da1904a34c9f8c720d2356e50db7b279b3))
* Make Part, FunctionDeclaration, Image, and GenerateContentResponse classmethods argument keyword only ([b58f4e0](https://github.com/googleapis/python-genai/commit/b58f4e03050fce29a6c47091cf25ef6f440c2e7e))
* Remove skip_project_and_location_in_path from async models.list ([d788626](https://github.com/googleapis/python-genai/commit/d788626a8de8bd8540739b673ae34530b494d83e))
* Remove skip_project_and_location_in_path from HttpOption ([a1c0435](https://github.com/googleapis/python-genai/commit/a1c043521558aca80a3bf55ff3eb96c95ec12e72))
* Support GenerateContentResponse.parsed to return Enum ([e214211](https://github.com/googleapis/python-genai/commit/e2142118ae7796c52503f327ca8d949a80be0e16))
* Validate enum value for different backend endpoint. ([97bb958](https://github.com/googleapis/python-genai/commit/97bb9580511c3517134d867500c8d155c231e04c))


### Bug Fixes

* Add required key to nested fields in function declaration schemas ([c7dba47](https://github.com/googleapis/python-genai/commit/c7dba473610547f153f13f82b8d8977a60b11308))
* Fix pydantic list support in Python 3.9 and 3.10 (fixes [#52](https://github.com/googleapis/python-genai/issues/52)) ([81150b3](https://github.com/googleapis/python-genai/commit/81150b3e0b21eded0cbdb2d0e3308b7866de619a))
* Handle nullable types in pydantic classes (fixes [#62](https://github.com/googleapis/python-genai/issues/62)) ([773e1c0](https://github.com/googleapis/python-genai/commit/773e1c0e28ff6dbfc799275c24b280c79375f9d5))
* Support parameterized generics Union type in automatic function calling parameters (fixes [#22](https://github.com/googleapis/python-genai/issues/22)) ([04475ab](https://github.com/googleapis/python-genai/commit/04475ab9d75e38f33ed07e7c6ad03bde36634105))


### Documentation

* Add examples & tests for thinking model ([59e2763](https://github.com/googleapis/python-genai/commit/59e27633de46f3521916a6d7819eae6ffc387405))
* Correct usage ([0c546de](https://github.com/googleapis/python-genai/commit/0c546deee62b5bbfbf3e05938f7b46a89861250e))
* Document experimental state of the live module. ([115ac47](https://github.com/googleapis/python-genai/commit/115ac4769088c43ef9eafe5eff588abc340b8213))
* Fix Blob type docstring. ([7f38e55](https://github.com/googleapis/python-genai/commit/7f38e55207d0c049a530e1f5eb605a251c133382))
* Remove repeated docstring for interrupted in docs ([230cfbc](https://github.com/googleapis/python-genai/commit/230cfbc73e45c0ea9a1a360890a68831a0dc3b60))
* Remove the word "class" in docstring and sync Live types docstring up-to-date ([7fa3ef3](https://github.com/googleapis/python-genai/commit/7fa3ef335e08cc752fa1eb41bf7d130ffccf7898))
* Update supported model parameter format for generate_content ([a5c3a1c](https://github.com/googleapis/python-genai/commit/a5c3a1ce6b0cffe3a91ffcb3756b3176ecf7b213))


### Code Refactoring

* Moved the HttpOptions class into types.py, by making it autogenerated. This causes the following breaking change: ([ad57025](https://github.com/googleapis/python-genai/commit/ad5702512ee78ad7bcda6233a7d1eafaaaf50e1f))
* Remove "tuning.distill" ([ca8cd5e](https://github.com/googleapis/python-genai/commit/ca8cd5e389263a261d1d9e05e47d6f108803efff))
* Remove pillow as a required dependency ([8ccdf2e](https://github.com/googleapis/python-genai/commit/8ccdf2e99246ba948b97f786596ae418f85749b0))
* Rename batches.list method signature. ([aa7c071](https://github.com/googleapis/python-genai/commit/aa7c071cb5922510f189da7875e1a3f6e1836733))
* Rename generate_image() to generate_images(), rename GenerateImageConfig to GenerateImagesConfig, rename GenerateImageResponse to GenerateImagesResponse, rename GenerateImageParameters to GenerateImagesParameters ([65d7bf5](https://github.com/googleapis/python-genai/commit/65d7bf5f519570c7af72d434a22e302fbafe0735))
* Renamed FunctionDeclaration class functions to reflect the fact that they work off of the `Callable` type not just functions. ([0e4a003](https://github.com/googleapis/python-genai/commit/0e4a0030295323177b38d052f7b7d695c07555b2))

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
