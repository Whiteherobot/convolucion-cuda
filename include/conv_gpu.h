#ifndef CONV_GPU_H
#define CONV_GPU_H

#include "imagen.h"
#include "mascaras.h"
#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

typedef struct {
    float h2d_ms;
    float kernel_ms;
    float d2h_ms;
    float total_ms;
} TiemposGPU;

#define CUDA_CHECK(llamada) do { \
    cudaError_t error_cuda = (llamada); \
    if (error_cuda != cudaSuccess) { \
        fprintf(stderr, "CUDA error en %s:%d: %s\n", __FILE__, __LINE__, \
                cudaGetErrorString(error_cuda)); \
        exit(1); \
    } \
} while (0)

void convolucion_gpu(const Imagen *entrada, Imagen *salida, const Mascara *m,
                     int hilos_por_bloque, TiemposGPU *t);

#endif
