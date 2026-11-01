// Convolución en GPU con CUDA. Bloque 2 - Jordi Romero (pendiente)
#include <cstdio>
#include "book.h"
#include "convolucion_gpu.h"

// Un hilo calcula un píxel de salida; bloques e hilos solo en X.
__global__ void kernel_convolucion(const float *entrada, float *salida, int ancho, int alto,
                                   const float *mascara, int k) {
    // TODO: int tid = blockIdx.x * blockDim.x + threadIdx.x;
    // TODO: if (tid < ancho * alto) { fila = tid / ancho; columna = tid % ancho; ... }
    // TODO: misma suma que convolucion_cpu, con ceros fuera de la imagen
}

void convolucion_gpu(const Imagen *ent, Imagen *sal, const Mascara *m, int hilos, TiemposGPU *t) {
    // TODO: HANDLE_ERROR(cudaMalloc(...)) para dev_entrada, dev_salida y dev_mascara
    // TODO: cudaMemcpy CPU -> GPU, medido con cudaEvent (t->h2d_ms)
    // TODO: bloques = (n + hilos - 1) / hilos; kernel<<<bloques, hilos>>>; CHECK_KERNEL(); (t->kernel_ms)
    // TODO: cudaMemcpy GPU -> CPU (t->d2h_ms), t->total_ms y cudaFree
    t->h2d_ms = t->kernel_ms = t->d2h_ms = t->total_ms = 0;
    std::printf("convolucion_gpu: pendiente (Bloque 2)\n");
}
