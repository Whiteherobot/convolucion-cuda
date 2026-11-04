# Convolución de imágenes en CPU y CUDA C

Práctica 01 · Computación Paralela · Universidad Politécnica Salesiana

Aplicamos filtros de convolución (media, nitidez y laplaciano) a imágenes en escala de grises, con
una versión secuencial y otra en CUDA C, y comparamos sus tiempos.

**Integrantes:** Michael Lata, Jordi Romero y Andrés Morocho.

El informe está en `informe/informe.tex` y las diapositivas en `presentacion/`.

## Requisitos

- CUDA Toolkit 12 o posterior y una GPU NVIDIA
- CMake 3.24 o posterior
- Python 3 con `pillow`, `matplotlib` y `numpy`
- LaTeX, solo para compilar el informe

## Cómo ejecutarlo

```bash
# Compilar
cmake -S . -B build && cmake --build build -j

# Prueba manual y validación CPU contra GPU
./build/convolucion probar

# Generar las imágenes de 2000, 4000 y 6000 píxeles
python3 scripts/preparar_imagenes.py datos/original.jpg

# Aplicar un filtro en CPU o en GPU
./build/convolucion filtrar datos/imagen_4000.pgm resultados/media.pgm media 9 cpu
./build/convolucion filtrar datos/imagen_4000.pgm resultados/media.pgm media 9 gpu 256

# Medir los experimentos y generar la tabla y las gráficas
./build/convolucion medir
python3 scripts/graficas.py

# Figuras de los filtros y compilación del informe
python3 scripts/figuras_filtros.py
cd informe && latexmk -pdf informe.tex
```

## Filtros

| Filtro | Máscara | Efecto |
|---|---|---|
| Media | k×k, todos 1/(k·k) | Suaviza la imagen |
| Nitidez | [0,−1,0; −1,5,−1; 0,−1,0] | Realza bordes y detalles |
| Laplaciano | [0,1,0; 1,−4,1; 0,1,0] | Resalta cambios de intensidad |

Fuera de la imagen se toman ceros. Se calcula como correlación; como las tres máscaras son
simétricas, el resultado es igual al de la convolución. Los cálculos se hacen en `float` y solo al
guardar se redondea y se recorta a 0–255.

## Experimentos

| Experimento | Varía | Fijo |
|---|---|---|
| Filtro | media, nitidez, laplaciano | 4000×4000, 3×3, 256 hilos |
| Resolución | 2000, 4000, 6000 | media 9×9, 256 hilos |
| Máscara | k = 3, 9, 21 | media, 4000×4000, 256 hilos |
| Hilos por bloque | 128, 256, 512 | media 9×9, 4000×4000 |

Para cada configuración se mide la CPU (1 calentamiento y 5 repeticiones), se calienta la GPU al
menos 2 s y se toman 5 repeticiones en GPU. La CPU se mide con `std::chrono` y la GPU con eventos
CUDA. No se mide la lectura o escritura de archivos ni la reserva de memoria.

## Resultados

Medianas de 5 repeticiones con la media en 4000×4000 y 256 hilos, en un i7-13650HX y una RTX 4060
Laptop:

| Máscara | CPU (ms) | Kernel (ms) | Total GPU (ms) | Aceleración de cómputo | Aceleración con copias | Copias |
|---|---:|---:|---:|---:|---:|---:|
| 3×3 | 159.2 | 0.64 | 11.00 | 250× | 14× | 94 % |
| 9×9 | 1084.4 | 2.77 | 13.07 | 392× | 83× | 79 % |
| 21×21 | 6675.3 | 14.82 | 25.79 | 450× | 259× | 43 % |

El error máximo entre CPU y GPU fue de 1.22×10⁻⁴, por debajo de la tolerancia de 10⁻³. Los
hilos por bloque casi no cambian el tiempo. La tabla completa y el análisis están en el informe.

## Estructura

```text
common/book.h       HANDLE_ERROR y CHECK_KERNEL (CUDA by Example)
src/modelo/         imágenes PGM, máscaras y convolución en CPU y GPU
src/vista/          salida por consola y CSV
src/controlador/    argumentos, pruebas, experimentos y medición
scripts/            preparar imágenes, gráficas, figuras y datos del equipo
datos/              foto original y ejemplo (los .pgm se generan, no se suben)
resultados/         mediciones, tablas, gráficas y datos del equipo
informe/            informe en LaTeX
presentacion/       diapositivas en PDF
```

Los archivos `resultados/*_corrida1*` y `*_corrida2*` son mediciones previas que no se usan en el
análisis.

## Imágenes

Las tres resoluciones salen de la misma foto, `datos/original.jpg` (6200×8272): recorte cuadrado
centrado de 6200×6200 y reducción con LANCZOS a 6000, 4000 y 2000. No se amplía ninguna.

Fotos de Unsplash (licencia Unsplash): Davide Manzini (`original.jpg`) y Alvan Nee
(`ejemplo_perro.jpg`).
