/* Programa principal CUDA reservado para el Bloque 2. */
#include "conv_gpu.h"
#include "imagen.h"
#include "mascaras.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    Imagen entrada = {0, 0, NULL}, salida;
    Mascara mascara;
    TiemposGPU tiempos;
    int hilos;
    if (argc < 5 || argc > 6) {
        fprintf(stderr, "Uso: %s <entrada.pgm> <salida.pgm> <filtro> <hilos_por_bloque> [k]\n", argv[0]);
        return 1;
    }
    hilos = atoi(argv[4]);
    if (leer_pgm(argv[1], &entrada) != 0) {
        fprintf(stderr, "Error al leer %s\n", argv[1]);
        return 1;
    }
    mascara = mascara_por_nombre(argv[3], argc == 6 ? atoi(argv[5]) : 3);
    salida = crear_imagen(entrada.ancho, entrada.alto);
    if (mascara.coef == NULL || salida.datos == NULL) {
        liberar_mascara(&mascara);
        liberar_imagen(&entrada);
        return 1;
    }
    convolucion_gpu(&entrada, &salida, &mascara, hilos, &tiempos);
    if (guardar_pgm(argv[2], &salida) != 0)
        fprintf(stderr, "Error al guardar %s\n", argv[2]);
    liberar_imagen(&salida);
    liberar_mascara(&mascara);
    liberar_imagen(&entrada);
    return 0;
}
