#!/bin/bash
set -e

echo "🔍 [1/4] Buscando archivos de configuración y tipos..."
TYPES_FILE="google/genai/types.py"
CONFIG_FILE="google/genai/generationconfig.py"

# Parche inteligente en Python para evitar duplicados de sintaxis
python3 -c '
import re

def patch_file(filepath):
    try:
        with open(filepath, "r") as f:
            content = f.read()
        
        # 1. Asegurar default=0.95 en Field de Pydantic
        content = re.sub(
            r"top_p:\s*Optional\[float\]\s*=\s*Field\(\s*default=None,",
            "top_p: Optional[float] = Field(\n      default=0.95,",
            content
        )
        
        # 2. Asegurar top_p=0.95 en TypedDicts o dataclasses
        content = re.sub(
            r"top_p:\s*Optional\[float\]\s*=\s*None",
            "top_p: Optional[float] = 0.95",
            content
        )

        with open(filepath, "w") as f:
            f.write(content)
        print(f"✅ Parche aplicado con éxito en: {filepath}")
    except FileNotFoundError:
        pass

patch_file("google/genai/types.py")
patch_file("google/genai/generationconfig.py")
'

echo "🧪 [2/4] Verificando sintaxis e importación..."
source venv/bin/activate || true
python3 -c "
import google.genai
from google.genai import types
config = types.GenerateContentConfig()
print(f'🎯 top_p activo por defecto = {config.top_p}')
assert config.top_p == 0.95, 'Error: top_p no es 0.95'
"

echo "📦 [3/4] Recompilando paquete .whl..."
python3 -m build --wheel

echo "🎉 [4/4] ¡AUTOMATIZACIÓN COMPLETADA CON ÉXITO!"
