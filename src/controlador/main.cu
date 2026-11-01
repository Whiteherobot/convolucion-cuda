// Controlador: lee los argumentos y llama al modelo y a la vista. Bloque 1 - Michael Lata
#include "convolucion_cpu.h"
#include "convolucion_gpu.h"
#include "consola.h"
#include "experimentos.h"
#include "pruebas.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <chrono>

Mascara elegir_mascara(const char *nombre, int k)
{
    if (strcmp(nombre, "media") == 0)
        return mascara_media(k);
    if (strcmp(nombre, "nitidez") == 0)
        return mascara_nitidez();
    return mascara_laplaciano();
}

// filtrar <entrada> <salida> <filtro> [k] [cpu|gpu] [hilos]
int filtrar(int argc, char **argv)
{
    int k = argc > 5 ? atoi(argv[5]) : 3;
    const char *modo = argc > 6 ? argv[6] : "cpu";
    int hilos = argc > 7 ? atoi(argv[7]) : 256;
    Imagen entrada, salida;
    Mascara mascara;
    TiemposGPU tiempos;

    if (leer_pgm(argv[2], &entrada) != 0) {
        printf("No se pudo leer %s\n", argv[2]);
        return 1;
    }
    mascara = elegir_mascara(argv[4], k);
    salida = crear_imagen(entrada.ancho, entrada.alto);
    printf("Imagen %dx%d\n", entrada.ancho, entrada.alto);
    imprimir_mascara(&mascara);

    if (strcmp(modo, "gpu") == 0) {
        convolucion_gpu(&entrada, &salida, &mascara, hilos, &tiempos);
        imprimir_tiempo("GPU kernel", tiempos.kernel_ms);
        imprimir_tiempo("GPU total", tiempos.total_ms);
    } else {
        auto t0 = std::chrono::steady_clock::now();
        convolucion_cpu(&entrada, &salida, &mascara);
        auto t1 = std::chrono::steady_clock::now();
        imprimir_tiempo("CPU", std::chrono::duration<double, std::milli>(t1 - t0).count());
    }

    guardar_pgm(argv[3], &salida);
    liberar_mascara(&mascara);
    liberar_imagen(&entrada);
    liberar_imagen(&salida);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc >= 5 && strcmp(argv[1], "filtrar") == 0)
        return filtrar(argc, argv);
    if (argc >= 2 && strcmp(argv[1], "probar") == 0)
        return probar_manual() + probar_gpu();
    if (argc >= 2 && strcmp(argv[1], "medir") == 0) {
        ejecutar_experimentos();
        return 0;
    }
    printf("Uso:\n");
    printf("  ./build/convolucion filtrar <entrada.pgm> <salida.pgm> <media|nitidez|laplaciano> [k] [cpu|gpu] [hilos]\n");
    printf("  ./build/convolucion probar\n");
    printf("  ./build/convolucion medir\n");
    return 1;
}
