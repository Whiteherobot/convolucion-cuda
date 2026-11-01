/* Esqueleto de benchmark del Bloque 3. */
#include <stdio.h>

static void escribir_encabezado_csv(FILE *f)
{
    fprintf(f, "implementacion,filtro,resolucion,mascara,hilos_por_bloque,bloques,repeticion,h2d_ms,kernel_ms,d2h_ms,total_ms,cpu_ms,unidad\n");
}

static void escribir_fila_csv(FILE *f, const char *implementacion, const char *filtro,
                              const char *resolucion, int mascara, int hilos,
                              int bloques, int repeticion, float h2d, float kernel,
                              float d2h, float total, float cpu, const char *unidad)
{
    fprintf(f, "%s,%s,%s,%d,%d,%d,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%s\n",
            implementacion, filtro, resolucion, mascara, hilos, bloques,
            repeticion, h2d, kernel, d2h, total, cpu, unidad);
}

int main(void)
{
    /* TODO: calentamiento y al menos cinco repeticiones por configuración. */
    /* TODO: recorrer filtro, resolución, máscara y hilos según PLAN.md. */
    /* TODO: abrir resultados/mediciones.csv y registrar las mediciones. */
    (void)escribir_encabezado_csv;
    (void)escribir_fila_csv;
    printf("benchmark: pendiente (Bloque 3)\n");
    return 0;
}
