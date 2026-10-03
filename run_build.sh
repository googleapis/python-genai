#!/bin/bash
set -e

# 1. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar herramientas de compilación
pip install --upgrade pip
pip install build wheel

# 3. Buscar y parchear automáticamente types.py dondequiera que esté
TYPES_FILE=$(find . -name "types.py" | head -n 1)
echo "💉 Parcheando archivo encontrado en: $TYPES_FILE"

sed -i 's/top_p: Optional\[float\] = None/top_p: Optional[float] = 0.95/g' "$TYPES_FILE"
sed -i 's/thinking_budget: Optional\[int\] = None/thinking_budget: Optional[int] = 16384/g' "$TYPES_FILE"

# 4. Compilar el paquete .whl
python3 -m build

# 5. Instalar la rueda compilada
pip install --force-reinstall dist/*.whl

echo "🎉 ¡PAQUETE .WHL COMPILADO E INSTALADO CON ÉXITO EN DEBIAN 12!"
