from google import genai

client = genai.Client(api_key="YOUR_API_KEY")
tokens = client.models.count_tokens(model = 'gemini-1.5-flash', contents = "Hello")
