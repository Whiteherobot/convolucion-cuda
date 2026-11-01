# Plan de trabajo por bloques

Práctica 01 · PA 69 — Convolución de imágenes de alta resolución mediante CUDA C.
Asignatura: Computación Paralela. Equipo de 3 integrantes.

Cada bloque tiene un responsable, archivos propios y una interfaz fija (los `.h` de
`include/`). Mientras se respeten esas firmas, cada uno puede trabajar en su rama sin
pisar el código de los demás.

| Bloque | Responsable | Rama | Estado |
|---|---|---|---|
| 1. Datos, máscaras, CPU secuencial y prueba manual | Integrante 1 (Michi) | `main` | Terminado |
| 2. Kernel CUDA, transferencias y validación CPU–GPU | Integrante 2 | `bloque-2-cuda` | Pendiente |
| 3. Experimentos, CSV, gráficas, informe y presentación | Integrante 3 | `bloque-3-experimentos` | Pendiente |

---

## Bloque 1 — Datos, máscaras y versión secuencial (Integrante 1 (Michi))

- [x] Estructura del repositorio, `Makefile` y `README.md`.
- [x] Lectura y escritura de imágenes PGM en escala de grises (`src/imagen.c`).
- [x] Máscaras de referencia: media k×k, nitidez 3×3 y laplaciano 3×3 (`src/mascaras.c`).
- [x] Convolución secuencial en C con extensión de ceros (`src/conv_cpu.c`).
- [x] Conversión al rango de visualización 0–255 documentada (`src/imagen.c`).
- [x] Prueba manual con la matriz 5×5 de la figura 1 (`tests/test_manual.c`).
- [x] Script de preparación de imágenes 2000, 4000 y 6000 px (`scripts/preparar_imagenes.py`).
- [x] Script para registrar el equipo (`scripts/info_equipo.sh`).
- [x] Programa `filtrar_cpu` para aplicar un filtro a una imagen.

**Entrega a los demás:** `include/imagen.h`, `include/mascaras.h` e `include/conv_cpu.h`.
La salida de `convolucion_cpu` es la referencia de corrección y de aceleración.

## Bloque 2 — Versión CUDA C (Integrante 2)

Archivos: `src/conv_gpu.cu`, `include/conv_gpu.h`, `tests/test_gpu.cu`, `src/filtrar_gpu.cu`.

- [ ] Kernel `kernel_convolucion`: bloques e hilos **solo en X**, un hilo por píxel de salida,
      lectura desde memoria global, arreglos separados de entrada y salida.
- [ ] Transformar el índice global en fila y columna (`fila = idx / ancho`, `col = idx % ancho`)
      y controlar el límite `idx < ancho * alto`.
- [ ] Extensión con ceros fuera de la imagen (igual que la CPU).
- [ ] Función `convolucion_gpu` que mida por separado con eventos CUDA:
      CPU→GPU, kernel, GPU→CPU y tiempo conjunto. Llenar `TiemposGPU`.
- [ ] Verificar errores con `CUDA_CHECK` y `cudaGetLastError()` después del kernel.
- [ ] `tests/test_gpu.cu`: comparar CPU vs GPU (error absoluto máximo y medio), usar la
      tolerancia de `TOLERANCIA` y justificarla; probar una imagen de dimensiones **no
      múltiplo** del número de hilos por bloque (por ejemplo 1001×777 con 256 hilos).
- [ ] Repetir la prueba manual de la figura 1 sobre la GPU (debe dar 78 y 87).

## Bloque 3 — Experimentos y entrega (Integrante 3)

Archivos: `experimentos/benchmark.cu`, `experimentos/graficas.py`, `resultados/*.csv`, `informe/`.

- [ ] `benchmark`: calentamiento previo + al menos **5 repeticiones medidas** por configuración.
- [ ] Guardar cada repetición en CSV: implementación, filtro, resolución, máscara,
      hilos/bloques, repetición, tiempos y unidades (ver encabezado en `experimentos/README.md`).
- [ ] Experimentos (modificar un factor a la vez):
  - Filtro: media, nitidez y laplaciano 3×3; 4000×4000.
  - Resolución: media 9×9; 2000, 4000 y 6000.
  - Máscara: media 3×3, 9×9 y 21×21; 4000×4000.
  - Hilos por bloque: media 9×9; 4000×4000; 128, 256 y 512.
- [ ] `graficas.py`: mediana y variabilidad, aceleración de cómputo
      (secuencial / kernel) y con transferencias (secuencial / conjunto).
- [ ] Responder las 4 preguntas de análisis.
- [ ] Informe PDF (con enlace al repo y hash del commit de entrega) y diapositivas.

---

## Integración

1. Cada integrante trabaja en su rama y abre un Pull Request hacia `main`.
2. Antes de abrir el PR: `make` y `make test` deben pasar.
3. No cambiar las firmas de `include/` sin avisar al grupo.
4. El commit de entrega se etiqueta como `entrega` y su hash va en el informe.

## Contribuciones (para el informe)

| Integrante | Bloque | Aporte |
|---|---|---|
| Integrante 1 (Michi) | 1 | Datos, E/S de imágenes, máscaras, versión secuencial, prueba manual |
| Integrante 2 | 2 | _(completar)_ |
| Integrante 3 | 3 | _(completar)_ |
