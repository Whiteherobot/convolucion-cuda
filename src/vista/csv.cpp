// Escritura de filas para experimentos. Bloque 3 - Andrés Morocho
#include "csv.h"

FILE *abrir_csv(const char *ruta)
{
    FILE *archivo = fopen(ruta, "w");
    if (archivo != NULL)
        fprintf(archivo, "implementacion,filtro,resolucion,mascara,hilos_por_bloque,bloques,repeticion,h2d_ms,kernel_ms,d2h_ms,total_ms,cpu_ms,unidad\n");
    return archivo;
}

void escribir_fila_csv(FILE *archivo, const char *implementacion,
                       const char *filtro, const char *resolucion,
                       const char *mascara, int hilos_por_bloque, int bloques,
                       int repeticion, float h2d_ms, float kernel_ms,
                       float d2h_ms, float total_ms, double cpu_ms,
                       const char *unidad)
{
    fprintf(archivo, "%s,%s,%s,%s,%d,%d,%d,%.3f,%.3f,%.3f,%.3f,%.3f,%s\n",
            implementacion, filtro, resolucion, mascara, hilos_por_bloque,
            bloques, repeticion, h2d_ms, kernel_ms, d2h_ms, total_ms, cpu_ms,
            unidad);
}
