from google import genai

client = genai.Client(api_key="YOUR_API_KEY")
chat = client.chats.create(model = "gemini-1.5-flash", config = types.GenerateContentConfig())
