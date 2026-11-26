import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(
    "Hello",
    generation_config={"temperature": 0.5},
    safety_settings=[
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    ],
)
