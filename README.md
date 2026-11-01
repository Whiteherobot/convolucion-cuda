# Práctica 01: convolución de imágenes en CPU y CUDA

Esta práctica implementa convolución de imágenes en escala de grises. El Bloque 1
contiene la versión secuencial en C99, lectura y escritura PGM, máscaras y prueba
manual. Los Bloques 2 y 3 incluyen interfaces y esqueletos compilables.

## Estructura

`include/` contiene interfaces, `src/` programas e implementaciones, `tests/`
pruebas, `scripts/` preparación de datos e información del equipo,
`experimentos/` benchmark y gráficas, `datos/` entradas, `resultados/` salidas
medidas e `informe/` documentación de entrega.

## Dependencias

Se necesitan GCC, CUDA Toolkit (para los objetivos CUDA), Python 3, Pillow,
NumPy y matplotlib. La ruta CPU no requiere CUDA.

```bash
make
make cpu
make test
python3 scripts/preparar_imagenes.py --sintetica
./bin/filtrar_cpu datos/imagen_2000.pgm resultados/salida.pgm media 9
./scripts/info_equipo.sh
```

## Máscaras

| Máscara | Efecto |
|---|---|
| `media` | Suaviza y reduce variaciones locales. |
| `nitidez` | Realza bordes y detalles. |
| `laplaciano` | Detecta cambios de intensidad y bordes. |

La convolución usa extensión con ceros: cualquier vecino fuera de la imagen
aporta cero. La salida conserva valores `float`; al escribir PGM se redondean y
recortan al rango `[0,255]`. La validación numérica se realiza antes de esta
conversión, sobre los valores float.

La división del trabajo y las interfaces fijas están en [PLAN.md](PLAN.md).
