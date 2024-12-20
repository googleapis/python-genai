# Google Gen AI SDK

[![PyPI version](https://img.shields.io/pypi/v/google-genai.svg)](https://pypi.org/project/google-genai/)

--------
**Documentation:** https://googleapis.github.io/python-genai/

-----

## Installation

``` cmd
pip install google-genai
```

## Imports

``` python
from google import genai
from google.genai import types
```

## Create a client

Please run one of the following code blocks to create a client for
different services (Google AI or Vertex). Feel free to switch the client
and run all the examples to see how it behaves under different APIs.

``` python
# Only run this block for Google AI API
client = genai.Client(api_key='YOUR_API_KEY')
```

``` python
# Only run this block for Vertex AI API
client = genai.Client(
    vertexai=True, project='your-project-id', location='us-central1'
)
```

## Types

Parameter types can be specified as either dictionaries(TypedDict) or
pydantic Models. Pydantic model types are available in the `types`
module.

## Models

The `client.models` modules exposes model inferencing and model getters.

### Generate Content

``` python
response = client.models.generate_content(
    model='gemini-2.0-flash-exp', contents='What is your name?'
)
print(response.text)
```

### System Instructions and Other Configs

``` python
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='high',
    config=types.GenerateContentConfig(
        system_instruction='I say high, you say low',
        temperature= 0.3,
    ),
)
print(response.text)
```

### Typed Config

All API methods support pydantic types for parameters as well as
dictionaries. You can get the type from `google.genai.types`.

``` python
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents=types.Part.from_text('Why is sky blue?'),
    config=types.GenerateContentConfig(
        temperature=0,
        top_p=0.95,
        top_k=20,
        candidate_count=1,
        seed=5,
        max_output_tokens=100,
        stop_sequences=["STOP!"],
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
)

response
```

### Safety Settings

``` python
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='Say something bad.',
    config=types.GenerateContentConfig(
        safety_settings= [types.SafetySetting(
            category='HARM_CATEGORY_HATE_SPEECH',
            threshold='BLOCK_ONLY_HIGH',
        )]
    ),
)
print(response.text)
```

### Function Calling

#### Automatic Python function Support

You can pass a python function directly and it will be automatically
called and responded.

``` python
def get_current_weather(location: str) -> str:
  """Returns the current weather.

  Args:
    location: The city and state, e.g. San Francisco, CA
  """
  return 'sunny'

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents="What is the weather like in Boston?",
    config=types.GenerateContentConfig(tools=[get_current_weather],)
)

response.text
```

#### Manually declare and invoke a function for function calling

If you don't want to use the automatic function support, you can manually
declare the function and invoke it.

The following example shows how to declare a function and pass it as a tool.
Then you will receive a function call part in the response.

``` python
function = dict(
    name="get_current_weather",
    description="Get the current weather in a given location",
    parameters={
      "type": "OBJECT",
      "properties": {
          "location": {
              "type": "STRING",
              "description": "The city and state, e.g. San Francisco, CA",
          },
      },
      "required": ["location"],
    }
)

tool = types.Tool(function_declarations=[function])


response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents="What is the weather like in Boston?",
    config=types.GenerateContentConfig(tools=[tool],)
)

response.candidates[0].content.parts[0].function_call
```

After you receive the function call part from model, you can invoke the function
and get the function response. And then you can pass the function response to
the model.
The following example shows how to do it for a simple function invocation.

``` python
function_call_part = response.candidates[0].content.parts[0]

try:
  function_result = get_current_weather(**function_call_part.function_call.args)
  function_response = {'result': function_result}
except Exception as e:  # instead of raising the exception, you can let the model handle it
  function_response = {'error': str(e)}


function_response_part = types.Part.from_function_response(
    name=function_call_part.function_call.name,
    response=function_response,
)

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents=[
        types.Part.from_text("What is the weather like in Boston?"),
        function_call_part,
        function_response_part,
    ])

response
```

### JSON Response Schema

#### Pydantic Model Schema support

Schemas can be provided as Pydantic Models.

``` python
from pydantic import BaseModel

class CountryInfo(BaseModel):
  name: str
  population: int
  capital: str
  continent: str
  gdp: int
  official_language: str
  total_area_sq_mi: int


response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='Give me information of the United States.',
    config=types.GenerateContentConfig(
        response_mime_type= 'application/json',
        response_schema= CountryInfo,
    ),
)
print(response.text)
```

``` python
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='Give me information of the United States.',
    config={
        'response_mime_type': 'application/json',
        'response_schema': {
            'required': [
                'name',
                'population',
                'capital',
                'continent',
                'gdp',
                'official_language',
                'total_area_sq_mi',
            ],
            'properties': {
                'name': {'type': 'STRING'},
                'population': {'type': 'INTEGER'},
                'capital': {'type': 'STRING'},
                'continent': {'type': 'STRING'},
                'gdp': {'type': 'INTEGER'},
                'official_language': {'type': 'STRING'},
                'total_area_sq_mi': {'type': 'INTEGER'},
            },
            'type': 'OBJECT',
        },
    },
)
print(response.text)
```

### Streaming

#### Streaming for text content

``` python
for chunk in client.models.generate_content_stream(
    model='gemini-2.0-flash-exp', contents='Tell me a story in 300 words.'
):
  print(chunk.text)
```

#### Streaming for image content

If your image is stored in Google Cloud Storage, you can use the `from_uri`
class method to create a Part object.

``` python
for chunk in client.models.generate_content_stream(
    model='gemini-1.5-flash',
    contents=[
      'What is this image about?',
      types.Part.from_uri(
        file_uri='gs://generativeai-downloads/images/scones.jpg',
        mime_type='image/jpeg'
      )
    ],
):
  print(chunk.text)
```

If your image is stored in your local file system, you can read it in as bytes
data and use the `from_bytes` class method to create a Part object.

``` python
YOUR_IMAGE_PATH = 'your_image_path'
YOUR_IMAGE_MIME_TYPE = 'your_image_mime_type'
with open(YOUR_IMAGE_PATH, 'rb') as f:
  image_bytes = f.read()

for chunk in client.models.generate_content_stream(
    model='gemini-1.5-flash',
    contents=[
      'What is this image about?',
      types.Part.from_bytes(
        data=image_bytes,
        mime_type=YOUR_IMAGE_MIME_TYPE
      )
    ],
):
  print(chunk.text)
```

### Async

`client.aio` exposes all the analogous `async` methods that are
available on `client`

For example, `client.aio.models.generate_content` is the async version
of `client.models.generate_content`

``` python
request = await client.aio.models.generate_content(
    model='gemini-2.0-flash-exp', contents='Tell me a story in 300 words.'
)

print(response.text)
```

### Streaming

``` python
async for response in client.aio.models.generate_content_stream(
    model='gemini-2.0-flash-exp', contents='Tell me a story in 300 words.'
):
  print(response.text)
```

### Count Tokens and Compute Tokens

``` python
response = client.models.count_tokens(
    model='gemini-2.0-flash-exp',
    contents='What is your name?',
)
print(response)
```

#### Compute Tokens

Compute tokens is not supported by Google AI.

``` python
response = client.models.compute_tokens(
    model='gemini-2.0-flash-exp',
    contents='What is your name?',
)
print(response)
```

##### Async

``` python
response = await client.aio.models.count_tokens(
    model='gemini-2.0-flash-exp',
    contents='What is your name?',
)
print(response)
```

### Embed Content

``` python
response = client.models.embed_content(
    model='text-embedding-004',
    contents='What is your name?',
)
response
```

``` python
# multiple contents with config
response = client.models.embed_content(
    model='text-embedding-004',
    contents=['What is your name?', 'What is your age?'],
    config=types.EmbedContentConfig(output_dimensionality= 10)
)

response
```

### Imagen

#### Generate Image

Support for generate image in Google AI is behind an allowlist

``` python
# Generate Image
response1 = client.models.generate_image(
    model='imagen-3.0-generate-001',
    prompt='An umbrella in the foreground, and a rainy night sky in the background',
    config=types.GenerateImageConfig(
        negative_prompt= "human",
        number_of_images= 1,
        include_rai_reason= True,
        output_mime_type= "image/jpeg"
    )
)
response1.generated_images[0].image.show()
```

#### Upscale Image

Upscale image is not supported in Google AI.

``` python
# Upscale the generated image from above
response2 = client.models.upscale_image(
    model='imagen-3.0-generate-001',
    image=response1.generated_images[0].image,
    config=types.UpscaleImageConfig(upscale_factor="x2")
)
response2.generated_images[0].image.show()
```

#### Edit Image

Edit image uses a separate model from generate and upscale.

Edit image is not supported in Google AI.

``` python
# Edit the generated image from above
from google.genai.types import RawReferenceImage, MaskReferenceImage
raw_ref_image = RawReferenceImage(
    reference_id=1,
    reference_image=response1.generated_images[0].image,
)

# Model computes a mask of the background
mask_ref_image = MaskReferenceImage(
    reference_id=2,
    config=types.MaskReferenceConfig(
        mask_mode='MASK_MODE_BACKGROUND',
        mask_dilation=0,
    ),
)

response3 = client.models.edit_image(
    model='imagen-3.0-capability-001',
    prompt='Sunlight and clear sky',
    reference_images=[raw_ref_image, mask_ref_image],
    config=types.EditImageConfig(
        edit_mode= 'EDIT_MODE_INPAINT_INSERTION',
        number_of_images= 1,
        negative_prompt= 'human',
        include_rai_reason= True,
        output_mime_type= 'image/jpeg',
    ),
)
response3.generated_images[0].image.show()
```

## Files (Only Google AI)

``` python
!gsutil cp gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf .
!gsutil cp gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf .
```

### Upload

``` python
file1 = client.files.upload(path='2312.11805v3.pdf')
file2 = client.files.upload(path='2403.05530.pdf')

print(file1)
print(file2)
```

### Delete

``` python
file3 = client.files.upload(path='2312.11805v3.pdf')

client.files.delete(name=file3.name)
```

## Caches

`client.caches` contains the control plane APIs for cached content

### Create

``` python
if client.vertexai:
  file_uris = [
      'gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf',
      'gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf'
  ]
else:
  file_uris = [file1.uri, file2.uri]

cached_content = client.caches.create(
      model='gemini-1.5-pro-002',
      contents=[
          types.Content(
              role='user',
              parts=[
                types.Part.from_uri(
                    file_uri=file_uris[0],
                    mime_type='application/pdf'),
                types.Part.from_uri(
                    file_uri=file_uris[1],
                    mime_type='application/pdf',)])
      ],
      system_instruction='What is the sum of the two pdfs?',
      config=types.CreateCachedContentConfig(
          display_name='test cache',
          ttl='3600s',
      ),
  )
```

### Get

``` python
client.caches.get(name=cached_content.name)
```

### Generate Content

``` python
client.models.generate_content(
    model='gemini-1.5-pro-002',
    contents='Summarize the pdfs',
    config=types.GenerateContentConfig(
        cached_content=cached_content.name,
    )
)
```

## Tunings

`client.tunings` contains tuning job APIs and supports supervised fine
tuning through `tune` and distillation through `distill`

### Tune

-   Vertex supports tuning from GCS source
-   Google AI supports tuning from inline examples

``` python
if client.vertexai:
  model = 'gemini-1.5-pro-002'
  training_dataset=types.TuningDataset(
        gcs_uri='gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl',
  )
else:
  model = 'models/gemini-1.0-pro-001'
  training_dataset=types.TuningDataset(
        examples=[
            types.TuningExample(
                text_input=f"Input text {i}",
                output=f"Output text {i}",
            )
            for i in range(5)
        ],
    )
```

``` python
tuning_job = client.tunings.tune(
    base_model=model,
    training_dataset=training_dataset,
    config=types.CreateTuningJobConfig(
        epoch_count= 1,
        tuned_model_display_name="test_dataset_examples model"
    )
)
tuning_job
```

### Get Tuning Job

``` python
tuning_job = client.tunings.get(name=tuning_job.name)
tuning_job
```

``` python
import time

running_states = set([
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
])

while tuning_job.state in running_states:
    print(tuning_job.state)
    tuning_job = client.tunings.get(name=tuning_job.name)
    time.sleep(10)
```

#### Use Tuned Model

``` python
response = client.models.generate_content(
    model=tuning_job.tuned_model.endpoint,
    contents='What is your name?',
)

response.text
```

### Get Tuned Model

``` python
tuned_model = client.models.get(model=tuning_job.tuned_model.model)
tuned_model
```

### List Tuned Models

``` python
for model in client.models.list(config={'page_size': 10}):
  print(model)
```

``` python
pager = client.models.list(config={'page_size': 10})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

#### Async

``` python
async for job in await client.aio.models.list(config={'page_size': 10}):
  print(job)
```

``` python
async_pager = await client.aio.models.list(config={'page_size': 10})
print(async_pager.page_size)
print(async_pager[0])
await async_pager.next_page()
print(async_pager[0])
```

### Update Tuned Model

``` python
model = pager[0]

model = client.models.update(
    model=model.name,
    config=types.UpdateModelConfig(
        display_name='my tuned model',
        description='my tuned model description'))

model
```

### Distillation

Only supported on Vertex. Requires allowlist.

``` python
distillation_job = client.tunings.distill(
    student_model="gemma-2b-1.1-it",
    teacher_model="gemini-1.5-pro-002",
    training_dataset=genai.types.DistillationDataset(
        gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl",
    ),
    config=genai.types.CreateDistillationJobConfig(
        epoch_count=1,
        pipeline_root_directory=(
            "gs://my-bucket"
        ),
    ),
)
distillation_job
```

``` python
tcompleted_states = set([
    "JOB_STATE_SUCCEEDED",
    "JOB_STATE_FAILED",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_PAUSED"
])

while distillation_job.state not in completed_states:
    print(distillation_job.state)
    distillation_job = client.tunings.get(name=distillation_job.name)
    time.sleep(10)
```

``` python
distillation_job
```

### List Tuning Jobs

``` python
for job in client.tunings.list(config={'page_size': 10}):
  print(job)
```

``` python
pager = client.tunings.list(config={'page_size': 10})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

#### Async

``` python
async for job in await client.aio.tunings.list(config={'page_size': 10}):
  print(job)
```

``` python
async_pager = await client.aio.tunings.list(config={'page_size': 10})
print(async_pager.page_size)
print(async_pager[0])
await async_pager.next_page()
print(async_pager[0])
```

## Batch Prediction

Only supported in Vertex AI.

### Create

``` python
# Specify model and source file only, destination and job display name will be auto-populated
job = client.batches.create(
    model='gemini-1.5-flash-002',
    src='bq://my-project.my-dataset.my-table',
)

job
```

``` python
# Get a job by name
job = client.batches.get(name=job.name)

job.state
```

``` python
completed_states = set([
    "JOB_STATE_SUCCEEDED",
    "JOB_STATE_FAILED",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_PAUSED"
])

while job.state not in completed_states:
    print(job.state)
    job = client.batches.get(name=job.name)
    time.sleep(30)

job
```

### List

``` python
for job in client.batches.list(config={'page_size': 10}):
  print(job)
```

``` python
pager = client.batches.list(config={'page_size': 10})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

#### Async

``` python
async for job in await client.aio.batches.list(config={'page_size': 10}):
  print(job)
```

``` python
async_pager = await client.aio.batches.list(config={'page_size': 10})
print(async_pager.page_size)
print(async_pager[0])
await async_pager.next_page()
print(async_pager[0])
```

### Delete

``` python
# Delete the job resource
delete_job = client.batches.delete(name=job.name)

delete_job
```
