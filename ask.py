import os
import sys
from google import genai
from google.genai import types

# Colores para la terminal
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print(f"{YELLOW}⚠️  Falta exportar GEMINI_API_KEY.{RESET}")
    print("👉 Ejecuta: export GEMINI_API_KEY='tu_clave_de_aistudio'")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# Configuración blindada con Top P = 0.95 y Thinking
config = types.GenerateContentConfig(
    temperature=1.0,
    top_p=0.95,
    thinking_config=types.ThinkingConfig(thinking_budget=8192),
    system_instruction=(
        "Eres un asistente de ingeniería de sistemas y normativa de tráfico (DGT) de alta precisión. "
        "Aplica auto-verificación estricta. Responde siempre con rigor técnico, formato ordenado "
        "y cita artículos oficiales o detalles de código sin alucinaciones."
    )
)

def preguntar(prompt_texto):
    print(f"\n{CYAN}🧠 Razonando con Top P = 0.95 y Thinking activo...{RESET}")
    modelos = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
    
    for modelo in modelos:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt_texto,
                config=config
            )
            print(f"\n{GREEN}{BOLD}--- 📄 RESPUESTA OFICIAL [{modelo}] ---{RESET}")
            print(response.text)
            print(f"{GREEN}{BOLD}----------------------------------------{RESET}\n")
            return
        except Exception as e:
            if "503" in str(e):
                print(f"{YELLOW}⚠️ Servidor con alta demanda en {modelo}, probando modelo de respaldo...{RESET}")
                continue
            else:
                print(f"❌ Error: {e}")
                return

# Modo 1: Si le pasas la pregunta como argumento directo
if len(sys.argv) > 1:
    pregunta = " ".join(sys.argv[1:])
    preguntar(pregunta)

# Modo 2: Modo interactivo tipo chat continuo en consola
else:
    print(f"\n{BLUE}{BOLD}===================================================={RESET}")
    print(f"{BLUE}{BOLD}   TERMINAL GEMINI CLI — TOP P 0.95 AUTO-VERIFICADO   {RESET}")
    print(f"{BLUE}{BOLD}===================================================={RESET}")
    print("Escribe tu pregunta y pulsa Enter (o escribe 'salir' para terminar):\n")
    
    while True:
        try:
            entrada = input(f"{BOLD}Pregunta > {RESET}").strip()
            if not entrada:
                continue
            if entrada.lower() in ["salir", "exit", "quit"]:
                print(f"{GREEN}¡Sesión cerrada con éxito! Hasta la vista, Adrián.{RESET}")
                break
            preguntar(entrada)
        except (KeyboardInterrupt, EOFError):
            print(f"\n{GREEN}Saliendo...{RESET}")
            break
