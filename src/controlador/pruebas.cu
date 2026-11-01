// Pruebas de corrección. probar_manual: Bloque 1 - Michael Lata. probar_gpu: Bloque 2 - Jordi Romero
#include "pruebas.h"
#include "convolucion_cpu.h"
#include "convolucion_gpu.h"
#include "consola.h"
#include <cmath>
#include <cstdio>

// Compara un valor obtenido con el esperado e imprime OK o FALLA.
static int revisar(const char *caso, float obtenido, float esperado)
{
    int ok = fabsf(obtenido - esperado) < TOLERANCIA;
    printf("%-6s %s: obtenido %.1f, esperado %.1f\n", ok ? "OK" : "FALLA", caso, obtenido, esperado);
    return ok ? 0 : 1;
}

// Matriz y máscara de la figura 1 del enunciado. Los valores esperados se calcularon a mano.
int probar_manual(void)
{
    float valores[25] = {35, 40, 41, 45, 50,
                         40, 40, 42, 46, 52,
                         42, 46, 50, 55, 55,
                         48, 52, 56, 58, 60,
                         56, 60, 65, 70, 75};
    float coeficientes[9] = {-2, -1, 0, -1, 1, 1, 0, 1, 2};
    Mascara figura = {3, coeficientes, "figura1"};
    Imagen entrada = crear_imagen(5, 5);
    Imagen salida = crear_imagen(5, 5);
    int i, fallas = 0;

    for (i = 0; i < 25; i++)
        entrada.datos[i] = valores[i];
    convolucion_cpu(&entrada, &salida, &figura);
    imprimir_matriz(&salida);

    // 35(-2)+40(-1)+41(0)+40(-1)+40(1)+42(1)+42(0)+46(1)+50(2) = 78
    fallas += revisar("pixel (1,1)", salida.datos[1 * 5 + 1], 78);
    fallas += revisar("pixel (1,2)", salida.datos[1 * 5 + 2], 87);
    // esquina: solo 4 vecinos dentro, 35(1)+40(1)+40(1)+40(2) = 195
    fallas += revisar("esquina (0,0) con ceros", salida.datos[0], 195);

    liberar_imagen(&entrada);
    liberar_imagen(&salida);
    return fallas;
}

// Compara CPU contra GPU.
int probar_gpu(void)
{
    // TODO: figura 1 en GPU, debe dar 78 y 87
    // TODO: imagen 1001x777 (no múltiplo de 256 hilos): error absoluto máximo y medio CPU vs GPU
    // TODO: aceptar si el error máximo es menor que TOLERANCIA
    printf("probar_gpu: pendiente (Bloque 2)\n");
    return 0;
}
