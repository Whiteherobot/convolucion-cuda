// Convolución en GPU con CUDA. Bloque 2 - Jordi Romero
#ifndef CONVOLUCION_GPU_H
#define CONVOLUCION_GPU_H
#include "imagen.h"
#include "mascara.h"

// Tiempos de cada parte, en milisegundos.
struct TiemposGPU {
    float h2d_ms;     // copia CPU -> GPU
    float kernel_ms;  // ejecución del kernel
    float d2h_ms;     // copia GPU -> CPU
    float total_ms;   // todo junto
};

void convolucion_gpu(const Imagen *ent, Imagen *sal, const Mascara *m, int hilos, TiemposGPU *t);
#endif
