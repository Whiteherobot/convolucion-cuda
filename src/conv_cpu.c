/*
 * conv_cpu.c
 * Convolución secuencial en CPU. Es la versión de referencia: contra ella se
 * valida la salida de la GPU y se calcula la aceleración.
 */
#include "conv_cpu.h"
#include <stddef.h>

/*
 * Aplica la máscara m a cada píxel de la entrada y guarda el resultado en
 * salida (arreglos separados, así ningún píxel ya calculado afecta a otro).
 *
 * Se recorren cuatro bucles:
 *   fila, col -> píxel de salida que se calcula
 *   i, j      -> posición dentro de la máscara k x k
 *
 * Extensión con ceros: si el vecino (y, x) cae fuera de la imagen no se suma
 * nada, que es lo mismo que suponer que afuera hay ceros.
 *
 * Se calcula como correlación (no se invierte la máscara). Para las máscaras
 * de la práctica (media, nitidez y laplaciano), que son simétricas, la
 * convolución y la correlación dan exactamente el mismo resultado.
 */
void convolucion_cpu(const Imagen *entrada, Imagen *salida, const Mascara *m)
{
    int fila, col, i, j, r;
    if (entrada == NULL || salida == NULL || m == NULL || m->coef == NULL ||
        entrada->datos == NULL || salida->datos == NULL || m->k <= 0)
        return;

    /* Radio de la máscara: para k = 3 es 1, para k = 9 es 4, para k = 21 es 10. */
    r = m->k / 2;

    for (fila = 0; fila < entrada->alto; ++fila) {
        for (col = 0; col < entrada->ancho; ++col) {
            float acumulador = 0.0f;

            /* Recorre la vecindad k x k centrada en (fila, col). */
            for (i = 0; i < m->k; ++i) {
                for (j = 0; j < m->k; ++j) {
                    int y = fila + i - r;   /* fila del vecino    */
                    int x = col + j - r;    /* columna del vecino */

                    /* Solo se suman los vecinos que están dentro de la imagen. */
                    if (y >= 0 && y < entrada->alto && x >= 0 && x < entrada->ancho)
                        acumulador += entrada->datos[y * entrada->ancho + x] *
                                      m->coef[i * m->k + j];
                }
            }

            /* Se guarda el valor en float, sin recortar; la conversión a
             * 0-255 se hace solo al guardar la imagen (ver a_rango_visual). */
            salida->datos[fila * salida->ancho + col] = acumulador;
        }
    }
}
