// Utilidades comunes de los ejemplos (al estilo del book.h de "CUDA by Example").
#ifndef BOOK_H
#define BOOK_H

#include <cstdio>
#include <cstdlib>
#include <cuda_runtime.h>

// Corta el programa con el archivo, la línea y el mensaje de CUDA si una llamada falla.
static void handle_error(cudaError_t err, const char *archivo, int linea) {
    if (err != cudaSuccess) {
        std::fprintf(stderr, "%s en %s:%d\n", cudaGetErrorString(err), archivo, linea);
        std::exit(EXIT_FAILURE);
    }
}
#define HANDLE_ERROR(err) (handle_error((err), __FILE__, __LINE__))

// Los lanzamientos de kernel no devuelven error: se consulta después.
#define CHECK_KERNEL() HANDLE_ERROR(cudaGetLastError())

#endif
