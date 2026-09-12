from google import genai

client = genai.Client(api_key="YOUR_API_KEY")
response = client.models.generate_content(model = 'gemini-1.5-flash', contents = "Hello", generation_config={"temperature": 0.5},
    safety_settings=[
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    ],
)
