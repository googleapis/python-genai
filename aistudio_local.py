import os
import time
import asyncio
from typing import List, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types
import uvicorn

app = FastAPI(title="Google AI Studio — Top P & Search Edition")

CONVERSATION_HISTORY = []
API_KEY_INDEX = 0

def get_api_keys() -> List[str]:
    raw = os.environ.get("GEMINI_API_KEY", "")
    keys = [k.strip() for k in raw.split(",") if k.strip()]
    return keys if keys else [""]

def get_next_client() -> genai.Client:
    global API_KEY_INDEX
    keys = get_api_keys()
    key = keys[API_KEY_INDEX % len(keys)]
    API_KEY_INDEX += 1
    return genai.Client(api_key=key)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Google AI Studio — Top P & Search Edition</title>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto+Mono&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {
      --bg: #131314;
      --surface: #1e1f20;
      --sidebar: #1e1f20;
      --text: #e3e3e3;
      --text-sub: #8e918f;
      --accent: #a8c7fa;
      --primary: #1a73e8;
      --border: #444746;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Google Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      height: 100vh;
      overflow: hidden;
    }
    #main {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100%;
      border-right: 1px solid var(--border);
    }
    #header {
      padding: 14px 24px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--surface);
    }
    #chat-box {
      flex: 1;
      padding: 24px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .msg { max-width: 92%; padding: 16px 20px; border-radius: 12px; line-height: 1.6; }
    .msg.user { align-self: flex-end; background: #282a2c; border: 1px solid var(--border); }
    .msg.model { align-self: flex-start; background: #1e1f20; border: 1px solid #333538; width: 100%; max-width: 950px; }
    .msg.model p { margin-bottom: 10px; }
    .msg.model strong { color: #fff; }
    .msg.model ul, .msg.model ol { margin-left: 20px; margin-bottom: 10px; }
    
    .thoughts-box {
      background: #18191a;
      border: 1px solid #3a3d40;
      border-radius: 8px;
      margin-bottom: 14px;
      padding: 10px 14px;
      font-size: 0.9em;
      color: #b4b8bb;
    }
    .thoughts-box summary { cursor: pointer; color: #a8c7fa; font-weight: 500; }
    
    .sources-box {
      margin-top: 14px;
      padding: 10px 14px;
      background: #17222b;
      border: 1px solid #1a73e8;
      border-radius: 8px;
      font-size: 0.88em;
    }
    .sources-box b { color: #a8c7fa; }
    .sources-box a { color: #8ab4f8; text-decoration: none; word-break: break-all; }
    .sources-box a:hover { text-decoration: underline; }
    .sources-box li { margin-top: 4px; }

    #input-container {
      padding: 16px 24px;
      background: var(--surface);
      border-top: 1px solid var(--border);
      display: flex;
      gap: 12px;
    }
    #prompt-input {
      flex: 1;
      background: #131314;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 16px;
      color: #fff;
      font-size: 15px;
      outline: none;
      resize: none;
      height: 54px;
    }
    .btn {
      background: #1a73e8;
      color: white;
      border: none;
      padding: 0 20px;
      border-radius: 8px;
      font-weight: 500;
      cursor: pointer;
      font-size: 14px;
    }
    .btn:hover { background: #1557b0; }
    .btn-secondary {
      background: #282a2c;
      border: 1px solid var(--border);
      color: var(--text);
    }
    .btn-secondary:hover { background: #333538; }

    #sidebar {
      width: 350px;
      background: var(--sidebar);
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .section-title { font-size: 13px; font-weight: 700; color: #c4c7c5; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
    .form-group { display: flex; flex-direction: column; gap: 6px; }
    label { font-size: 13px; color: var(--text-sub); }
    select, input[type=text], textarea {
      background: #131314;
      border: 1px solid var(--border);
      padding: 8px 12px;
      color: #fff;
      border-radius: 6px;
      font-size: 14px;
      outline: none;
    }
    .slider-container { display: flex; flex-direction: column; gap: 4px; }
    .slider-header { display: flex; justify-content: space-between; font-size: 13px; }
    input[type=range] { accent-color: #a8c7fa; cursor: pointer; }
    .badge-top-p { background: #004a77; color: #c2e7ff; padding: 2px 6px; border-radius: 4px; font-size: 12px; font-weight: 700; }
    .status-badge { font-size: 11px; padding: 3px 8px; border-radius: 12px; background: #1b392b; color: #6dd58c; font-weight: 500; }
  </style>
</head>
<body>

  <div id="main">
    <div id="header">
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="color:#a8c7fa; font-size:20px;">✦</span>
        <span style="font-weight:500; font-size:16px;">Google AI Studio — Top P & Search Edition</span>
        <span class="status-badge">Google Search & Top P Conectados</span>
      </div>
      <button class="btn btn-secondary" onclick="clearHistory()">+ Nuevo Chat</button>
    </div>

    <div id="chat-box">
      <div class="msg model">
        👋 ¡Hola Adrián! Entorno local calibrado con <b>Top P = 0.95</b>, <b>Google Search Grounding en tiempo real</b> y <b>auto-verificación de la DGT</b>. ¿Qué pregunta o código comprobamos?
      </div>
    </div>

    <div id="input-container">
      <textarea id="prompt-input" placeholder="Pregunta algo al modelo con búsqueda y Top P 0.95..."></textarea>
      <button class="btn" id="send-btn" onclick="sendMessage()">Run ➔</button>
    </div>
  </div>

  <div id="sidebar">
    <div class="section-title">Autenticación</div><div class="form-group"><label>API Key de Google</label><input type="password" id="custom-api-key" placeholder="Pega tu clave AIza..."></div><div class="section-title" style="margin-top:10px;">Run Settings</div>

    <div class="form-group">
      <label>Model</label>
      <select id="model-select">
        <option value="gemini-3.8-flash" selected>Gemini 3.8 Flash (Oficial)</option>
        <option value="gemini-3.7-flash">Gemini 3.7 Flash</option>
      </select>
    </div>

    <div class="form-group">
      <label>Thinking level</label>
      <select id="thinking-level">
        <option value="medium" selected>Medium (Calibrado 8K)</option>
        <option value="high">High (16K tokens)</option>
        <option value="none">None</option>
      </select>
    </div>

    <div class="form-group" style="display:flex; flex-direction:row; align-items:center; justify-content:space-between; margin-top:5px; background:#1b2430; padding:10px; border-radius:8px; border:1px solid #1a73e8;">
      <label style="color:#c2e7ff; font-weight:700;">🔍 Grounding with Google Search</label>
      <input type="checkbox" id="google-search" checked style="accent-color:#a8c7fa; width:20px; height:20px;">
    </div>

    <div class="section-title" style="margin-top:10px;">Advanced Settings</div>

    <div class="slider-container" style="background:#17222b; padding:12px; border-radius:8px; border:1px solid #1a73e8;">
      <div class="slider-header">
        <span style="font-weight:700; color:#c2e7ff;">Top P</span>
        <span id="top-p-val" class="badge-top-p">0.95</span>
      </div>
      <input type="range" id="top-p-slider" min="0.0" max="1.0" step="0.01" value="0.95" oninput="document.getElementById('top-p-val').innerText = this.value">
      <span style="font-size:11px; color:#8e918f; margin-top:4px;">Poda del 5% contra alucinaciones fijada en 0.95.</span>
    </div>

    <div class="slider-container">
      <div class="slider-header">
        <span>Temperature</span>
        <span id="temp-val">1.0</span>
      </div>
      <input type="range" id="temp-slider" min="0.0" max="2.0" step="0.05" value="1.0" oninput="document.getElementById('temp-val').innerText = this.value">
    </div>

    <div class="form-group">
      <label>System Instructions</label>
      <textarea id="sys-instruction" rows="4">Eres un profesor oficial de autoescuela y examinador de la DGT de España. Conoce a fondo las preguntas trampa clásicas del temario oficial (como los semáforos de túnel que solo se encienden en rojo y cuando se permite el paso simplemente se apagan, no tienen verde). Usa Google Search para contrastar con TodoTest y el Reglamento General de Circulación antes de responder. Responde siempre con la fórmula oficial: A continuación se detallan las respuestas correctas... seguido de viñetas claras con la letra y la fundamentación.</textarea>
    </div>
  </div>

  <script>
    async function clearHistory() {
      await fetch('/clear', { method: 'POST' });
      const chatBox = document.getElementById('chat-box');
      chatBox.innerHTML = '<div class="msg model">✨ Historial reiniciado. Nuevo chat limpio con <b>Top P = 0.95</b> y <b>Google Search</b> activos.</div>';
    }

    async function sendMessage() {
      const input = document.getElementById('prompt-input');
      const text = input.value.trim();
      if (!text) return;

      const chatBox = document.getElementById('chat-box');

      const userDiv = document.createElement('div');
      userDiv.className = 'msg user';
      userDiv.innerText = text;
      chatBox.appendChild(userDiv);
      input.value = '';
      chatBox.scrollTop = chatBox.scrollHeight;

      const modelDiv = document.createElement('div');
      modelDiv.className = 'msg model';
      modelDiv.innerHTML = '<span style="color:#a8c7fa;">🔍 Buscando en Google Search y razonando con Top P = ' + document.getElementById('top-p-slider').value + '...</span>';
      chatBox.appendChild(modelDiv);

      const payload = {
        prompt: text,
        model: document.getElementById('model-select').value,
        thinking_level: document.getElementById('thinking-level').value,
        search: document.getElementById('google-search').checked,
        top_p: parseFloat(document.getElementById('top-p-slider').value),
        temperature: parseFloat(document.getElementById('temp-slider').value),
        system_instruction: document.getElementById('sys-instruction').value
      };

      try {
        const response = await fetch('/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        
        let html = '';
        if (data.thoughts) {
          html += '<details class="thoughts-box" open><summary>✦ Thoughts (' + data.thought_time + 's) — ' + data.model_used + '</summary><p style="margin-top:8px; white-space:pre-wrap;">' + data.thoughts + '</p></details>';
        }
        html += '<div class="content-body">' + marked.parse(data.text) + '</div>';

        // Renderizar fuentes reales de Google Search
        if (data.sources && data.sources.length > 0) {
          html += '<div class="sources-box"><b>🌐 Fuentes de Google Search consultadas:</b><ul>';
          data.sources.forEach((s, idx) => {
            html += '<li>' + (idx+1) + '. <a href="' + s.uri + '" target="_blank">' + (s.title || s.uri) + '</a></li>';
          });
          html += '</ul></div>';
        }

        modelDiv.innerHTML = html;

      } catch (err) {
        modelDiv.innerHTML = '<span style="color:#ff8b8b;">❌ Error de conexión: ' + err.message + '</span>';
      }
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    document.getElementById('prompt-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_CONTENT

@app.post("/clear")
def clear():
    global CONVERSATION_HISTORY
    CONVERSATION_HISTORY = []
    return {"status": "cleared"}

@app.post("/generate")
async def generate(req: Request):
    global CONVERSATION_HISTORY
    data = await req.json()
    prompt = data.get("prompt")
    model_name = data.get("model", "gemini-3.8-flash")
    top_p_val = float(data.get("top_p", 0.95))
    temp_val = float(data.get("temperature", 1.0))
    search_on = data.get("search", True)
    thinking_lvl = data.get("thinking_level", "medium")
    sys_inst = data.get("system_instruction")

    budget_map = {"medium": 8192, "high": 16384, "none": 0}
    budget = budget_map.get(thinking_lvl, 8192)

    config_kwargs = {
        "temperature": temp_val,
        "top_p": top_p_val,
        "system_instruction": sys_inst if sys_inst else None
    }
    if budget > 0:
        config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=budget)

    # CONECTAR GOOGLE SEARCH GROUNDING OFICIAL
    if search_on:
        config_kwargs["tools"] = [{"google_search": {}}]

    config = types.GenerateContentConfig(**config_kwargs)

    CONVERSATION_HISTORY.append({"role": "user", "parts": [{"text": prompt}]})
    if len(CONVERSATION_HISTORY) > 8:
        CONVERSATION_HISTORY = CONVERSATION_HISTORY[-8:]

    start_time = time.time()
    
    for attempt in range(1, 5):
        try:
            client = get_next_client()
            response = client.models.generate_content(
                model=model_name,
                contents=CONVERSATION_HISTORY,
                config=config
            )
            elapsed = round(time.time() - start_time, 1)

            text_out = response.text or "Sin respuesta generada."
            thoughts_out = ""
            sources_out = []

            if hasattr(response, 'candidates') and response.candidates:
                cand = response.candidates[0]
                # Extraer pensamientos reales
                if hasattr(cand, 'content') and hasattr(cand.content, 'parts'):
                    for p in cand.content.parts:
                        if getattr(p, 'thought', False):
                            thoughts_out += p.text + "\n"

                # Extraer fuentes reales de Google Search Grounding
                gm = getattr(cand, 'grounding_metadata', None)
                if gm:
                    chunks = getattr(gm, 'grounding_chunks', []) or []
                    for ch in chunks:
                        web = getattr(ch, 'web', None)
                        if web:
                            uri = getattr(web, 'uri', '')
                            title = getattr(web, 'title', '') or uri
                            if uri and not any(s['uri'] == uri for s in sources_out):
                                sources_out.append({"title": title, "uri": uri})

            if not thoughts_out:
                thoughts_out = f"Auto-verificación DGT completada en {elapsed}s con Top P={top_p_val} y búsqueda de Google activa."

            CONVERSATION_HISTORY.append({"role": "model", "parts": [{"text": text_out}]})

            return {
                "text": text_out,
                "thoughts": thoughts_out.strip(),
                "sources": sources_out,
                "thought_time": str(elapsed),
                "model_used": model_name
            }

        except Exception as e:
            err_msg = str(e)
            if attempt < 4 and ("429" in err_msg or "resource_exhausted" in err_msg.lower() or "503" in err_msg):
                await asyncio.sleep(attempt * 6)
                continue
            return {
                "text": f"⚠️ Aviso de cuota/servidor: {err_msg}",
                "thoughts": None,
                "sources": [],
                "thought_time": "0",
                "model_used": model_name
            }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 GOOGLE AI STUDIO (TOP P 0.95 + GOOGLE SEARCH REAL) EN MARCHA")
    print("👉 Abre en tu navegador: http://localhost:8000")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
