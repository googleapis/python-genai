import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

model1 = genai.GenerativeModel("gemini-1.5-flash")
model2 = genai.GenerativeModel("gemini-1.5-pro")

response1 = model1.generate_content("Hello")
response2 = model2.generate_content("World")
