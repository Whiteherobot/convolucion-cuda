// Escritura de filas para experimentos. Bloque 3 - Andrés Morocho
#include "csv.h"

// Una fila por repetición e implementación. En las filas "cpu" las columnas de GPU
// quedan en 0 y en las filas "gpu" cpu_ms queda en 0. Todos los tiempos en ms.
FILE *abrir_csv(const char *ruta)
{
    FILE *archivo = fopen(ruta, "w");
    if (archivo != NULL)
        fprintf(archivo, "experimento,implementacion,filtro,resolucion,mascara,hilos_por_bloque,bloques,repeticion,h2d_ms,kernel_ms,d2h_ms,total_ms,cpu_ms,unidad\n");
    return archivo;
}

void escribir_fila_csv(FILE *archivo, int experimento, const char *implementacion,
                       const char *filtro, const char *resolucion,
                       const char *mascara, int hilos_por_bloque, int bloques,
                       int repeticion, float h2d_ms, float kernel_ms,
                       float d2h_ms, float total_ms, double cpu_ms,
                       const char *unidad)
{
    fprintf(archivo, "%d,%s,%s,%s,%s,%d,%d,%d,%.4f,%.4f,%.4f,%.4f,%.4f,%s\n",
            experimento, implementacion, filtro, resolucion, mascara, hilos_por_bloque,
            bloques, repeticion, h2d_ms, kernel_ms, d2h_ms, total_ms, cpu_ms,
            unidad);
    fflush(archivo);  // si se corta la ejecución, lo medido ya queda en disco
}
