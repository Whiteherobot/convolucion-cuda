// Pruebas de corrección. probar_manual: Bloque 1 - Michael Lata. probar_gpu: Bloque 2 - Jordi Romero
#include "pruebas.h"
#include "convolucion_cpu.h"
#include "convolucion_gpu.h"
#include "consola.h"
#include <cmath>
#include <cstdio>
#include <cstdlib>

#define HILOS_PRUEBA 256
#define ANCHO_PRUEBA 1001
#define ALTO_PRUEBA 777
#define SEMILLA 2026

// Matriz y máscara de la figura 1 del enunciado. Los valores esperados se calcularon a mano.
static float figura1_valores[25] = {35, 40, 41, 45, 50,
                                    40, 40, 42, 46, 52,
                                    42, 46, 50, 55, 55,
                                    48, 52, 56, 58, 60,
                                    56, 60, 65, 70, 75};
static float figura1_coef[9] = {-2, -1, 0, -1, 1, 1, 0, 1, 2};

static Imagen imagen_figura1(void)
{
    Imagen img = crear_imagen(5, 5);
    int i;
    for (i = 0; i < 25; i++)
        img.datos[i] = figura1_valores[i];
    return img;
}

// Compara un valor obtenido con el esperado e imprime OK o FALLA.
static int revisar(const char *caso, float obtenido, float esperado)
{
    int ok = fabsf(obtenido - esperado) < TOLERANCIA;
    printf("%-6s %s: obtenido %.1f, esperado %.1f\n", ok ? "OK" : "FALLA", caso, obtenido, esperado);
    return ok ? 0 : 1;
}

int probar_manual(void)
{
    Mascara figura = {3, figura1_coef, "figura1"};
    Imagen entrada = imagen_figura1();
    Imagen salida = crear_imagen(5, 5);
    int fallas = 0;

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

// Valores 0..255 pseudoaleatorios; la semilla fija hace que la prueba sea repetible.
static Imagen imagen_aleatoria(int ancho, int alto)
{
    Imagen img = crear_imagen(ancho, alto);
    int i;
    srand(SEMILLA);
    for (i = 0; i < ancho * alto; i++)
        img.datos[i] = (float)(rand() % 256);
    return img;
}

// Aplica la misma máscara en CPU y GPU y mide el error absoluto píxel a píxel.
static int comparar_cpu_gpu(const Imagen *entrada, const Mascara *m)
{
    int n = entrada->ancho * entrada->alto;
    Imagen cpu = crear_imagen(entrada->ancho, entrada->alto);
    Imagen gpu = crear_imagen(entrada->ancho, entrada->alto);
    TiemposGPU tiempos;
    float error, maximo = 0.0f;
    double suma = 0.0;
    int i, ok;

    convolucion_cpu(entrada, &cpu, m);
    convolucion_gpu(entrada, &gpu, m, HILOS_PRUEBA, &tiempos);
    for (i = 0; i < n; i++) {
        error = fabsf(cpu.datos[i] - gpu.datos[i]);
        if (error > maximo)
            maximo = error;
        suma += error;
    }

    ok = maximo < TOLERANCIA;
    printf("%-6s %s %dx%d en %dx%d: error maximo %.2e, medio %.2e\n", ok ? "OK" : "FALLA",
           m->nombre, m->k, m->k, entrada->ancho, entrada->alto, maximo, suma / n);
    liberar_imagen(&cpu);
    liberar_imagen(&gpu);
    return ok ? 0 : 1;
}

int probar_gpu(void)
{
    Mascara figura = {3, figura1_coef, "figura1"};
    Imagen entrada = imagen_figura1();
    Imagen salida = crear_imagen(5, 5);
    Imagen grande = imagen_aleatoria(ANCHO_PRUEBA, ALTO_PRUEBA);
    Mascara mascaras[4] = {mascara_media(3), mascara_media(9), mascara_nitidez(), mascara_laplaciano()};
    TiemposGPU tiempos;
    int i, fallas = 0;

    convolucion_gpu(&entrada, &salida, &figura, HILOS_PRUEBA, &tiempos);
    fallas += revisar("GPU pixel (1,1)", salida.datos[1 * 5 + 1], 78);
    fallas += revisar("GPU pixel (1,2)", salida.datos[1 * 5 + 2], 87);
    fallas += revisar("GPU esquina (0,0) con ceros", salida.datos[0], 195);

    for (i = 0; i < 4; i++) {
        fallas += comparar_cpu_gpu(&grande, &mascaras[i]);
        liberar_mascara(&mascaras[i]);
    }

    liberar_imagen(&entrada);
    liberar_imagen(&salida);
    liberar_imagen(&grande);
    return fallas;
}
