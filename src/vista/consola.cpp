// Impresión de resultados sencillos. Bloque 1 - Michael Lata
#include "consola.h"
#include <cstdio>

void imprimir_matriz(const Imagen *img)
{
    int i, j;
    for (i = 0; i < img->alto; ++i) {
        for (j = 0; j < img->ancho; ++j)
            printf("%8.3f ", img->datos[i * img->ancho + j]);
        putchar('\n');
    }
}

void imprimir_mascara(const Mascara *m)
{
    int i, j;
    printf("Mascara %s:\n", m->nombre);
    for (i = 0; i < m->k; ++i) {
        for (j = 0; j < m->k; ++j)
            printf("%8.3f ", m->coef[i * m->k + j]);
        putchar('\n');
    }
}

void imprimir_tiempo(const char *etiqueta, double ms)
{
    printf("%s: %.3f ms\n", etiqueta, ms);
}
