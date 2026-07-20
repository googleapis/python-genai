"""Legacy -> new transformation mappings for google-generativeai -> google-genai migration.

Each dict represents one legacy -> new transformation with keys:
- name: short identifier for the transformation
- legacy_pattern: legacy code snippet (string snippet, not regex)
- new_pattern: new code snippet (string snippet, not regex)
- notes: additional notes about the transformation
"""

MAPPINGS = [
    {
        "name": "import",
        "legacy_pattern": "import google.generativeai as genai",
        "new_pattern": "from google import genai",
        "notes": "Change import style from module import to from google import genai",
    },
    {
        "name": "configure",
        "legacy_pattern": "genai.configure(api_key=...)",
        "new_pattern": "client = genai.Client(api_key=...)",
        "notes": "Replace configure() with Client instantiation",
    },
    {
        "name": "model",
        "legacy_pattern": "genai.GenerativeModel('gemini-X')",
        "new_pattern": "client.models.generate_content(model='gemini-X', ...)",
        "notes": "Replace GenerativeModel instantiation with client.models.generate_content",
    },
    {
        "name": "generate_content",
        "legacy_pattern": "model.generate_content(text)",
        "new_pattern": "client.models.generate_content(model=..., contents=text)",
        "notes": "Replace model.generate_content with client.models.generate_content",
    },
    {
        "name": "start_chat",
        "legacy_pattern": "model.start_chat(history=...)",
        "new_pattern": "client.chats.create(model=..., config=...)",
        "notes": "Replace model.start_chat with client.chats.create",
    },
    {
        "name": "count_tokens",
        "legacy_pattern": "model.count_tokens(text)",
        "new_pattern": "client.models.count_tokens(model=..., contents=text)",
        "notes": "Replace model.count_tokens with client.models.count_tokens",
    },
]
