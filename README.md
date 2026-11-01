# Convolución de imágenes en CPU y CUDA C

Práctica 01 · Computación Paralela · Universidad Politécnica Salesiana

Aplica filtros de convolución (media, nitidez y laplaciano) a imágenes en escala de grises de
2000×2000, 4000×4000 y 6000×6000 píxeles, en una versión secuencial en C y otra en CUDA C, y
compara sus tiempos.

## Integrantes y división del trabajo

| Bloque | Integrante | Qué hace | Estado |
|---|---|---|---|
| 1 | Michael Lata | Imágenes PGM, máscaras, convolución en CPU, prueba manual, preparación de datos | Terminado |
| 2 | Jordi Romero | Kernel CUDA, transferencias CPU–GPU, validación CPU vs GPU | Pendiente |
| 3 | Andrés Morocho | Experimentos, CSV, gráficas, informe y presentación | Pendiente |

Cada archivo indica en su primera línea a qué bloque pertenece y quién lo hizo.

**Pendiente Bloque 2** (`convolucion_gpu.cu`, `probar_gpu` en `pruebas.cu`)
- [ ] Kernel con bloques e hilos en X: un hilo por píxel, control de límites, ceros fuera.
- [ ] Medir con eventos CUDA: CPU→GPU, kernel, GPU→CPU y total.
- [ ] Error absoluto máximo y medio contra la CPU, con imagen 1001×777 y 256 hilos.

**Pendiente Bloque 3** (`experimentos.cu`, `graficas.py`)
- [ ] Calentamiento y 5 repeticiones por configuración, guardadas en `resultados/mediciones.csv`.
- [ ] Experimentos: filtro (3×3, 4000), resolución (media 9×9), máscara (3, 9, 21), hilos (128, 256, 512).
- [ ] Mediana, variabilidad, aceleraciones y gráficas; informe y diapositivas.

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
scripts/
  preparar_imagenes.py    recorte y redimensionado a 2000/4000/6000   B1
  info_equipo.sh          CPU, RAM, GPU y versiones                   B1
  graficas.py             gráficas a partir del CSV                   B3
datos/                    foto original y ejemplos (los .pgm se generan, no se suben)
resultados/               CSV y datos del equipo
```

## Uso

Requiere CUDA Toolkit 12 o posterior, CMake 3.24 o posterior y Python 3 con `pillow` y `matplotlib`.

```bash
cmake -S . -B build && cmake --build build -j         # compila build/convolucion
./build/convolucion probar                            # prueba manual y validación GPU
python3 scripts/preparar_imagenes.py datos/original.jpg   # genera datos/imagen_{2000,4000,6000}.pgm
./build/convolucion filtrar datos/imagen_4000.pgm resultados/media.pgm media 9 cpu
./build/convolucion filtrar datos/imagen_4000.pgm resultados/media.pgm media 9 gpu 256
./build/convolucion medir                               # experimentos
bash scripts/info_equipo.sh                           # datos del equipo
```

## Imágenes

Las tres resoluciones salen de la misma foto, `datos/original.jpg` (6200×8272): recorte cuadrado
centrado de 6200×6200 y reducción con LANCZOS a 6000, 4000 y 2000. No hay ampliación.
`ejemplo_bosque.jpg` y `ejemplo_perro.jpg` solo se usan para mostrar el efecto de los filtros en el informe.

Fotos de Unsplash (licencia Unsplash): Davide Manzini (`original.jpg`), Filip Kvasnák (`ejemplo_bosque.jpg`)
y Alvan Nee (`ejemplo_perro.jpg`).

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
