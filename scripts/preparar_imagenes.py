# Prepara la misma imagen en 2000x2000, 4000x4000 y 6000x6000 (PGM en escala de grises).
# Bloque 1 - Michael Lata
# Uso: python3 scripts/preparar_imagenes.py datos/original.jpg
import sys
from PIL import Image

TAMANOS = [2000, 4000, 6000]

entrada = sys.argv[1] if len(sys.argv) > 1 else "datos/original.jpg"
imagen = Image.open(entrada).convert("L")  # escala de grises
print(f"Original: {imagen.width}x{imagen.height}")

# Recorte cuadrado centrado, común para las tres resoluciones
lado = min(imagen.size)
x = (imagen.width - lado) // 2
y = (imagen.height - lado) // 2
imagen = imagen.crop((x, y, x + lado, y + lado))
print(f"Recorte cuadrado: {lado}x{lado} desde ({x}, {y})")

for tamano in TAMANOS:
    accion = "reducción" if tamano <= lado else "ampliación"
    salida = f"datos/imagen_{tamano}.pgm"
    imagen.resize((tamano, tamano), Image.Resampling.LANCZOS).save(salida)
    print(f"{salida}: {tamano}x{tamano} ({accion} con LANCZOS)")
