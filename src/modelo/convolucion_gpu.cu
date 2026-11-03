// Convolución en GPU con CUDA. Bloque 2 - Jordi Romero
#include <cstdio>
#include "book.h"
#include "convolucion_gpu.h"

// Un hilo calcula un píxel de salida; bloques e hilos solo en X.
__global__ void kernel_convolucion(const float *entrada, float *salida, int ancho, int alto,
                                   const float *mascara, int k) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int fila, columna, i, j;
    int radio = k / 2;

    // El último bloque puede tener hilos de más: esos no hacen nada.
    if (tid < ancho * alto) {
        fila = tid / ancho;
        columna = tid % ancho;
        float suma = 0.0f;
        for (i = 0; i < k; i++) {
            for (j = 0; j < k; j++) {
                int y = fila + i - radio;
                int x = columna + j - radio;
                if (y >= 0 && y < alto && x >= 0 && x < ancho)
                    suma += entrada[y * ancho + x] * mascara[i * k + j];
            }
        }
        salida[tid] = suma;
    }
}

// Reserva, copia, ejecuta y devuelve. La reserva queda fuera de los tiempos.
void convolucion_gpu(const Imagen *ent, Imagen *sal, const Mascara *m, int hilos, TiemposGPU *t) {
    int n = ent->ancho * ent->alto;
    size_t bytes_imagen = (size_t)n * sizeof(float);
    size_t bytes_mascara = (size_t)m->k * m->k * sizeof(float);
    int bloques = (n + hilos - 1) / hilos;
    float *dev_entrada, *dev_salida, *dev_mascara;
    cudaEvent_t inicio, tras_copia_ida, tras_kernel, fin;

    HANDLE_ERROR(cudaEventCreate(&inicio));
    HANDLE_ERROR(cudaEventCreate(&tras_copia_ida));
    HANDLE_ERROR(cudaEventCreate(&tras_kernel));
    HANDLE_ERROR(cudaEventCreate(&fin));

    HANDLE_ERROR(cudaMalloc((void **)&dev_entrada, bytes_imagen));
    HANDLE_ERROR(cudaMalloc((void **)&dev_salida, bytes_imagen));
    HANDLE_ERROR(cudaMalloc((void **)&dev_mascara, bytes_mascara));

    HANDLE_ERROR(cudaEventRecord(inicio, 0));
    HANDLE_ERROR(cudaMemcpy(dev_entrada, ent->datos, bytes_imagen, cudaMemcpyHostToDevice));
    HANDLE_ERROR(cudaMemcpy(dev_mascara, m->coef, bytes_mascara, cudaMemcpyHostToDevice));
    HANDLE_ERROR(cudaEventRecord(tras_copia_ida, 0));

    kernel_convolucion<<<bloques, hilos>>>(dev_entrada, dev_salida, ent->ancho, ent->alto,
                                           dev_mascara, m->k);
    CHECK_KERNEL();
    HANDLE_ERROR(cudaEventRecord(tras_kernel, 0));

    HANDLE_ERROR(cudaMemcpy(sal->datos, dev_salida, bytes_imagen, cudaMemcpyDeviceToHost));
    HANDLE_ERROR(cudaEventRecord(fin, 0));
    HANDLE_ERROR(cudaEventSynchronize(fin));

    HANDLE_ERROR(cudaEventElapsedTime(&t->h2d_ms, inicio, tras_copia_ida));
    HANDLE_ERROR(cudaEventElapsedTime(&t->kernel_ms, tras_copia_ida, tras_kernel));
    HANDLE_ERROR(cudaEventElapsedTime(&t->d2h_ms, tras_kernel, fin));
    HANDLE_ERROR(cudaEventElapsedTime(&t->total_ms, inicio, fin));

    HANDLE_ERROR(cudaFree(dev_entrada));
    HANDLE_ERROR(cudaFree(dev_salida));
    HANDLE_ERROR(cudaFree(dev_mascara));
    HANDLE_ERROR(cudaEventDestroy(inicio));
    HANDLE_ERROR(cudaEventDestroy(tras_copia_ida));
    HANDLE_ERROR(cudaEventDestroy(tras_kernel));
    HANDLE_ERROR(cudaEventDestroy(fin));
}
