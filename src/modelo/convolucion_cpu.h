// Interfaz de convolución secuencial. Bloque 1 - Michael Lata
#ifndef CONVOLUCION_CPU_H
#define CONVOLUCION_CPU_H
#include "imagen.h"
#include "mascara.h"
void convolucion_cpu(const Imagen *ent, Imagen *sal, const Mascara *m);
#endif
