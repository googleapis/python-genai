from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

response1 = client.models.generate_content(model = 'gemini-1.5-flash', contents = "Hello")
response2 = client.models.generate_content(model = 'gemini-1.5-pro', contents = "World")
