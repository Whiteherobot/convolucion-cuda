// Medición de una configuración CPU vs GPU. Bloque 3 - Andrés Morocho
#ifndef MEDICION_H
#define MEDICION_H
#include "imagen.h"
#include "mascara.h"
#include <cstdio>

#define REPETICIONES          5       // repeticiones medidas por implementación
#define CALENTAMIENTO_GPU_MS  2000.0  // trabajo continuo en GPU antes de medir

// Mide CPU y GPU para (imagen, máscara, hilos por bloque), escribe 2*REPETICIONES filas
// en el CSV y compara la salida GPU con la CPU. Devuelve 1 si está dentro de TOLERANCIA.
int medir_configuracion(FILE *csv, int experimento, const Imagen *entrada,
                        const Mascara *mascara, int hilos_por_bloque);
#endif
