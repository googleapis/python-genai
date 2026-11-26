import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[{"role": "user", "parts": "Hello"}])
