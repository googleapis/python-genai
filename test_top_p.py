import os
import sys
import time
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: Falta GEMINI_API_KEY")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# CONFIGURACIÓN COMPLETA: Top P + Pensamiento Profundo (Thinking)
config = types.GenerateContentConfig(
    temperature=1.0,
    top_p=0.95,
    thinking_config=types.ThinkingConfig(
        thinking_budget=4096
    )
)

prompt = (
    "Pregunta oficial de examen DGT: ¿Qué debemos hacer al encontrar un semáforo rojo "
    "fijo en la entrada de un túnel? "
    "Opciones típicas de examen: "
    "a) Pasar con precaución. "
    "b) Esperar a que cambie a verde. "
    "c) Esperar a que se apague la luz roja. "
    "Analiza detalladamente las características de los semáforos de túnel según el RGC y da la opción correcta."
)

print("=" * 65)
print(f"🎯 ACTUALIZADO: Top P = {config.top_p} | Thinking Budget = {config.thinking_config.thinking_budget}")
print("=" * 65)

print("\n🧠 Pensando y razonando la normativa con Gemini 3.8 Flash...")

for attempt in range(1, 4):
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=config
        )
        print("\n--- 📄 RESPUESTA RAZONADA (CON THINKING Y TOP P 0.95) ---")
        print(response.text)
        print("---------------------------------------------------------")
        sys.exit(0)
    except Exception as e:
        if "503" in str(e):
            print(f"⚠️ Servidor ocupado. Reintentando ({attempt}/3)...")
            time.sleep(3)
        else:
            print(f"❌ Error: {e}")
            break
