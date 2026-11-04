# Convolución de imágenes en CPU y CUDA C

Práctica 01 · Computación Paralela · Universidad Politécnica Salesiana

Aplica filtros de convolución (media, nitidez y laplaciano) a imágenes en escala de grises de
2000×2000, 4000×4000 y 6000×6000 píxeles, en una versión secuencial en C y otra en CUDA C, y
compara sus tiempos.

## Integrantes y división del trabajo

| Bloque | Integrante | Qué hace | Estado |
|---|---|---|---|
| 1 | Michael Lata | Imágenes PGM, máscaras, convolución en CPU, prueba manual, preparación de datos | Terminado |
| 2 | Jordi Romero | Kernel CUDA, transferencias CPU–GPU, validación CPU vs GPU | Terminado |
| 3 | Andrés Morocho | Experimentos, CSV, gráficas, informe y presentación | Pendiente |

Cada archivo indica en su primera línea a qué bloque pertenece y quién lo hizo.

**Bloque 2 (terminado)** (`convolucion_gpu.cu`, `probar_gpu` en `pruebas.cu`)
- [x] Kernel con bloques e hilos en X: un hilo por píxel, control de límites, ceros fuera.
- [x] Medir con eventos CUDA: CPU→GPU, kernel, GPU→CPU y total.
- [x] Error absoluto máximo y medio contra la CPU, con imagen 1001×777 y 256 hilos.

**Bloque 3** (`experimentos.cu`, `medicion.cu`, `csv.cpp`, `graficas.py`)
- [x] Por configuración: CPU (1 calentamiento + 5 medidas), calentamiento GPU de 2 s y 5 medidas GPU seguidas, guardadas en `resultados/mediciones.csv`.
- [x] Experimentos: filtro (3×3, 4000), resolución (media 9×9), máscara (3, 9, 21), hilos (128, 256, 512).
- [x] Validación CPU vs GPU (error máximo y medio) sobre cada imagen real antes de medir.
- [x] Mediana, variabilidad (desv. estándar, mín, máx), aceleraciones y gráficas (`resultados/resumen.csv`).
- [x] Corrida 1 en el equipo con GPU (`mediciones_corrida1.csv`): tiempos de GPU con dos niveles de rendimiento.
- [x] Corrida 2 con registro del estado de la GPU (`mediciones_corrida2.csv`, `gpu_estado_corrida2.csv`): la GPU cambia de estado entre repeticiones.
- [ ] Corrida 3 con el nuevo orden de medición (calentamiento GPU de 2 s, CPU y GPU en bloques).
- [x] Figuras de filtros y rangos (`scripts/figuras_filtros.py`).
- [ ] Informe (`informe/informe.tex`, faltan las partes que dependen de la corrida 3) y diapositivas.

### Mediciones

| Experimento | Varía | Fijo |
|---|---|---|
| 1 | media, nitidez, laplaciano | 4000×4000, 3×3, 256 hilos |
| 2 | 2000, 4000, 6000 | media 9×9, 256 hilos |
| 3 | k = 3, 9, 21 | media, 4000×4000, 256 hilos |
| 4 | 128, 256, 512 hilos | media 9×9, 4000×4000 |

- CPU: solo `convolucion_cpu`, medido con `std::chrono::steady_clock`.
- GPU: eventos CUDA. CPU→GPU incluye imagen y máscara; total = CPU→GPU + kernel + GPU→CPU.
  La reserva (`cudaMalloc`/`cudaFree`) **no** está incluida.
- No se mide lectura/escritura de archivos ni preparación de imágenes.
- Los bloques se ajustan para cubrir la imagen: `bloques = (ancho·alto + hilos − 1) / hilos`.
- Cada fila del CSV lleva su número de experimento: la configuración media 9×9, 4000, 256 hilos
  aparece en los experimentos 2, 3 y 4 y cada uno conserva sus propias 5 repeticiones.
- `graficas.py [csv] [sufijo]`: con sufijo los archivos no se pisan entre corridas, p.ej.
  `python3 scripts/graficas.py resultados/mediciones_corrida1.csv _corrida1`.
- El % de transferencias se calcula en cada repetición y luego se toma la mediana.
- Aceleración de cómputo = mediana CPU / mediana kernel. Aceleración con transferencias =
  mediana CPU / mediana total GPU.

## Estructura

```text
common/book.h             HANDLE_ERROR y CHECK_KERNEL (CUDA by Example)
src/
  modelo/                 datos y cálculo
    imagen.cpp            leer y guardar PGM                          B1
    mascara.cpp           máscaras media, nitidez y laplaciano        B1
    convolucion_cpu.cpp   convolución secuencial (referencia)         B1
    convolucion_gpu.cu    convolución en CUDA                         B2
  vista/                  lo que se muestra o se guarda
    consola.cpp           imprimir matrices, máscaras y tiempos       B1
    csv.cpp               escribir las mediciones                     B3
  controlador/            decide qué se ejecuta
    main.cu               lee los argumentos (filtrar, probar, medir) B1
    pruebas.cu            prueba manual (B1) y validación GPU (B2)
    experimentos.cu       los cuatro experimentos                     B3
    medicion.cu           medición de una configuración (CPU, GPU)    B3
scripts/
  preparar_imagenes.py    recorte y redimensionado a 2000/4000/6000   B1
  info_equipo.sh          CPU, RAM, GPU y versiones                   B1
  graficas.py             gráficas a partir del CSV                   B3
  figuras_filtros.py      imágenes de los filtros para el informe     B3
informe/                  informe en LaTeX (lee figuras y tablas de resultados/) B3
datos/                    foto original y ejemplos (los .pgm se generan, no se suben)
resultados/               CSV y datos del equipo
```

## Uso

Requiere CUDA Toolkit 12 o posterior, CMake 3.24 o posterior y Python 3 con `pillow`, `matplotlib` y `numpy`.

```bash
cmake -S . -B build && cmake --build build -j         # compila build/convolucion
./build/convolucion probar                            # prueba manual y validación GPU
python3 scripts/preparar_imagenes.py datos/original.jpg   # genera datos/imagen_{2000,4000,6000}.pgm
./build/convolucion filtrar datos/imagen_4000.pgm resultados/media.pgm media 9 cpu
./build/convolucion filtrar datos/imagen_4000.pgm resultados/media.pgm media 9 gpu 256
./build/convolucion medir                             # experimentos -> resultados/mediciones.csv
python3 scripts/graficas.py                           # resumen.csv y gráficas en resultados/
python3 scripts/figuras_filtros.py                    # imágenes de los filtros y rangos antes de 0–255
cd informe && latexmk -pdf informe.tex                # informe PDF (o: tectonic informe.tex)
bash scripts/info_equipo.sh                           # datos del equipo
```

## Imágenes

Las tres resoluciones salen de la misma foto, `datos/original.jpg` (6200×8272): recorte cuadrado
centrado de 6200×6200 y reducción con LANCZOS a 6000, 4000 y 2000. No hay ampliación.
`ejemplo_perro.jpg` solo se usa para mostrar el efecto de los filtros en el informe.

Fotos de Unsplash (licencia Unsplash): Davide Manzini (`original.jpg`) y Alvan Nee
(`ejemplo_perro.jpg`).

## Filtros

| Filtro | Máscara | Efecto |
|---|---|---|
| Media | k×k, todos 1/(k·k) | Suaviza la imagen |
| Nitidez | [0,−1,0; −1,5,−1; 0,−1,0] | Realza bordes y detalles |
| Laplaciano | [0,1,0; 1,−4,1; 0,1,0] | Resalta cambios de intensidad |

## Decisiones

- Mismo estilo que los ejemplos de *CUDA by Example*: `HANDLE_ERROR` en cada llamada a CUDA,
  `tid = blockIdx.x * blockDim.x + threadIdx.x`, eventos CUDA para el kernel y `std::chrono` para la CPU.
- Fuera de la imagen se toman ceros.
- Se calcula como correlación (sin invertir la máscara); como las tres máscaras son simétricas,
  el resultado es igual al de la convolución.
- Los cálculos se hacen en `float` y se validan así. Solo al guardar se redondea y se recorta
  a 0–255.
- La prueba manual usa la matriz de la figura 1 del enunciado: debe dar 78 en (1,1), 87 en
  (1,2) y 195 en la esquina (0,0).
