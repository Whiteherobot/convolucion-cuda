// Escritura de mediciones CSV. Bloque 3 - Andrés Morocho
#ifndef CSV_H
#define CSV_H
#include <cstdio>
FILE *abrir_csv(const char *ruta);
void escribir_fila_csv(FILE *archivo, const char *implementacion,
                       const char *filtro, const char *resolucion,
                       const char *mascara, int hilos_por_bloque, int bloques,
                       int repeticion, float h2d_ms, float kernel_ms,
                       float d2h_ms, float total_ms, double cpu_ms,
                       const char *unidad);
#endif
