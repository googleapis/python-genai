from google import genai

client = genai.Client(api_key="YOUR_API_KEY")
response = client.models.generate_content_stream(model = 'gemini-1.5-flash', contents = "Hello")
