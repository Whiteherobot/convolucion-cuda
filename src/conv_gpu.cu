/* Esqueleto CUDA del Bloque 2; la implementación queda pendiente. */
#include "conv_gpu.h"
#include <stdio.h>

__global__ void kernel_convolucion(const float *entrada, float *salida,
                                   int ancho, int alto, const float *mascara, int k)
{
    /* TODO: calcular idx global = blockIdx.x*blockDim.x+threadIdx.x. */
    /* TODO: salir si idx >= ancho*alto; obtener fila=idx/ancho y col=idx%ancho. */
    /* TODO: recorrer la máscara y usar cero cuando el vecino esté fuera. */
    (void)entrada; (void)salida; (void)ancho; (void)alto; (void)mascara; (void)k;
}

void convolucion_gpu(const Imagen *entrada, Imagen *salida, const Mascara *m,
                     int hilos_por_bloque, TiemposGPU *t)
{
    /* TODO Bloque 2: cudaMalloc, eventos, cudaMemcpy H2D, lanzamiento con
     * bloques=(n+hilos-1)/hilos, cudaGetLastError, D2H, sincronización,
     * medición de TiemposGPU y cudaFree. */
    size_t n = 0;
    (void)m;
    (void)hilos_por_bloque;
    if (entrada != NULL && entrada->ancho > 0 && entrada->alto > 0)
        n = (size_t)entrada->ancho * (size_t)entrada->alto;
    if (salida != NULL && salida->datos != NULL)
        for (size_t i = 0; i < n; ++i)
            salida->datos[i] = 0.0f;
    if (t != NULL) {
        t->h2d_ms = 0.0f;
        t->kernel_ms = 0.0f;
        t->d2h_ms = 0.0f;
        t->total_ms = 0.0f;
    }
    printf("convolucion_gpu: pendiente (Bloque 2)\n");
}
