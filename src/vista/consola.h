// Salida de datos en consola. Bloque 1 - Michael Lata
#ifndef CONSOLA_H
#define CONSOLA_H
#include "imagen.h"
#include "mascara.h"
void imprimir_matriz(const Imagen *img);
void imprimir_mascara(const Mascara *m);
void imprimir_tiempo(const char *etiqueta, double ms);
#endif
