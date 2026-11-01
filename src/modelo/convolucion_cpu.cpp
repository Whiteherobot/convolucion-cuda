// Convolución secuencial en CPU, usada como referencia. Bloque 1 - Michael Lata
#include "convolucion_cpu.h"

// Recorre cada píxel de salida y suma la vecindad k x k multiplicada por la máscara.
// Entrada y salida son arreglos separados.
void convolucion_cpu(const Imagen *ent, Imagen *sal, const Mascara *m)
{
    int fila, columna, i, j;
    int radio = m->k / 2;

    for (fila = 0; fila < ent->alto; fila++) {
        for (columna = 0; columna < ent->ancho; columna++) {
            float suma = 0.0f;
            for (i = 0; i < m->k; i++) {
                for (j = 0; j < m->k; j++) {
                    int y = fila + i - radio;
                    int x = columna + j - radio;
                    // fuera de la imagen se toma cero: simplemente no se suma
                    if (y >= 0 && y < ent->alto && x >= 0 && x < ent->ancho)
                        suma += ent->datos[y * ent->ancho + x] * m->coef[i * m->k + j];
                }
            }
            sal->datos[fila * sal->ancho + columna] = suma;
        }
    }
}
