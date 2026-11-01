/* Programa principal del Bloque 1 para aplicar un filtro en CPU. */
#include "comun.h"
#include "conv_cpu.h"
#include "imagen.h"
#include "mascaras.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    Imagen entrada = {0, 0, NULL}, salida;
    Mascara mascara;
    int k = 3;
    double inicio, fin;
    if (argc < 4 || argc > 5) {
        fprintf(stderr, "Uso: %s <entrada.pgm> <salida.pgm> <media|nitidez|laplaciano> [k]\n", argv[0]);
        return 1;
    }
    if (argc == 5)
        k = atoi(argv[4]);
    if (leer_pgm(argv[1], &entrada) != 0) {
        fprintf(stderr, "Error al leer %s\n", argv[1]);
        return 1;
    }
    mascara = mascara_por_nombre(argv[3], k);
    if (mascara.coef == NULL) {
        fprintf(stderr, "Mascara invalida o k no impar\n");
        liberar_imagen(&entrada);
        return 1;
    }
    salida = crear_imagen(entrada.ancho, entrada.alto);
    if (salida.datos == NULL) {
        liberar_mascara(&mascara);
        liberar_imagen(&entrada);
        return 1;
    }
    inicio = tiempo_ms();
    convolucion_cpu(&entrada, &salida, &mascara);
    fin = tiempo_ms();
    printf("Tamano: %dx%d\n", entrada.ancho, entrada.alto);
    imprimir_mascara(&mascara);
    printf("Tiempo de convolucion CPU: %.3f ms\n", fin - inicio);
    if (guardar_pgm(argv[2], &salida) != 0) {
        fprintf(stderr, "Error al guardar %s\n", argv[2]);
        liberar_imagen(&salida);
        liberar_mascara(&mascara);
        liberar_imagen(&entrada);
        return 1;
    }
    liberar_imagen(&salida);
    liberar_mascara(&mascara);
    liberar_imagen(&entrada);
    return 0;
}
