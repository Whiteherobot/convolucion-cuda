// Experimentos de rendimiento CPU vs GPU. Bloque 3 - Andrés Morocho
//
// Protocolo:
//   - 1 ejecución de calentamiento (no se mide) por cada configuración.
//   - 5 repeticiones medidas y guardadas en el CSV.
//
// Los cuatro experimentos son:
//   1. Tipo de filtro  : media/nitidez/laplaciano  (k=3,    imagen 4000, hilos=256)
//   2. Resolución      : media 9x9                 (2000/4000/6000,      hilos=256)
//   3. Tamaño de másc. : media k=3/9/21            (imagen 4000,         hilos=256)
//   4. Hilos por bloque: media 9x9                 (imagen 4000,    128/256/512)
//
// Alcance de la medición (igual en todas las configuraciones):
//   - CPU: solo convolucion_cpu, con std::chrono.
//   - GPU: eventos CUDA dentro de convolucion_gpu (Bloque 2). H2D incluye imagen y
//     máscara; total = H2D + kernel + D2H. cudaMalloc/cudaFree quedan FUERA.
//   - Fuera de todo: lectura de PGM, creación de máscaras y escritura del CSV.
// Cada fila lleva el número de experimento, así una configuración que se repite
// entre experimentos (p.ej. media 9x9, 4000, 256 hilos) no mezcla sus muestras.

#include "experimentos.h"
#include "imagen.h"
#include "mascara.h"
#include "convolucion_cpu.h"
#include "convolucion_gpu.h"
#include "csv.h"
#include "consola.h"
#include "pruebas.h"     // TOLERANCIA

#include <chrono>
#include <cstdio>
#include <cstring>
#include <cmath>

// ── Constantes ────────────────────────────────────────────────────────────────

#define REPETICIONES     5
#define RUTA_CSV         "resultados/mediciones.csv"

// Rutas de las imágenes generadas por preparar_imagenes.py
static const char *RUTA_2000 = "datos/imagen_2000.pgm";
static const char *RUTA_4000 = "datos/imagen_4000.pgm";
static const char *RUTA_6000 = "datos/imagen_6000.pgm";

// ── Ayudantes internos ────────────────────────────────────────────────────────

// Devuelve un string con el tamaño de la imagen "ANxALT", p.ej. "4000x4000".
static void resolucion_str(const Imagen *img, char *buf, int tam)
{
    snprintf(buf, tam, "%dx%d", img->ancho, img->alto);
}

// Devuelve un string con el tamaño de la máscara, p.ej. "3x3".
static void mascara_str(const Mascara *m, char *buf, int tam)
{
    snprintf(buf, tam, "%dx%d", m->k, m->k);
}

// ── Medición de una sola configuración ───────────────────────────────────────
//
// Ejecuta 1 calentamiento + REPETICIONES ejecuciones medidas de CPU y GPU para
// la combinación (imagen, máscara, hilos). Escribe todas las filas en el CSV.
// Antes de medir compara la salida CPU y GPU del calentamiento (error absoluto).
//
static void medir_configuracion(FILE *csv, int experimento,
                                const Imagen  *entrada,
                                const Mascara *mascara,
                                int            hilos_por_bloque)
{
    char res_str[32], mask_str[32];
    resolucion_str(entrada, res_str, sizeof(res_str));
    mascara_str(mascara, mask_str, sizeof(mask_str));

    int n_pixeles  = entrada->ancho * entrada->alto;
    int n_bloques  = (n_pixeles + hilos_por_bloque - 1) / hilos_por_bloque;

    Imagen salida_cpu = crear_imagen(entrada->ancho, entrada->alto);
    Imagen salida_gpu = crear_imagen(entrada->ancho, entrada->alto);
    TiemposGPU tiempos;

    // ── Calentamiento (no se guarda en CSV) ──────────────────────────────────
    convolucion_cpu(entrada, &salida_cpu, mascara);
    convolucion_gpu(entrada, &salida_gpu, mascara, hilos_por_bloque, &tiempos);

    // ── Validación numérica CPU vs GPU sobre la imagen real (antes de redondear) ─
    float err_max = 0.0f;
    double err_suma = 0.0;
    for (int i = 0; i < n_pixeles; i++) {
        float e = fabsf(salida_cpu.datos[i] - salida_gpu.datos[i]);
        if (e > err_max) err_max = e;
        err_suma += e;
    }
    printf("    %s %s %s, %d hilos x %d bloques: error max %.2e, medio %.2e %s\n",
           mascara->nombre, mask_str, res_str, hilos_por_bloque, n_bloques,
           err_max, err_suma / n_pixeles, err_max < TOLERANCIA ? "OK" : "FUERA DE TOLERANCIA");

    // ── 5 repeticiones medidas ────────────────────────────────────────────────
    for (int rep = 1; rep <= REPETICIONES; rep++) {

        // CPU: medición con std::chrono (igual que en main.cu)
        auto t0 = std::chrono::steady_clock::now();
        convolucion_cpu(entrada, &salida_cpu, mascara);
        auto t1 = std::chrono::steady_clock::now();
        double cpu_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

        // GPU: los tiempos los devuelve la función de Jordi (Bloque 2)
        convolucion_gpu(entrada, &salida_gpu, mascara, hilos_por_bloque, &tiempos);

        // Fila CPU
        escribir_fila_csv(csv, experimento,
            "cpu", mascara->nombre, res_str, mask_str,
            0, 0, rep,
            0.0f, 0.0f, 0.0f, 0.0f, cpu_ms, "ms");

        // Fila GPU
        escribir_fila_csv(csv, experimento,
            "gpu", mascara->nombre, res_str, mask_str,
            hilos_por_bloque, n_bloques, rep,
            tiempos.h2d_ms, tiempos.kernel_ms,
            tiempos.d2h_ms, tiempos.total_ms,
            0.0, "ms");
    }

    liberar_imagen(&salida_cpu);
    liberar_imagen(&salida_gpu);
}

// ── Carga segura de imagen ────────────────────────────────────────────────────

static int cargar_imagen(const char *ruta, Imagen *img)
{
    if (leer_pgm(ruta, img) != 0) {
        printf("[AVISO] No se pudo leer: %s  (omitiendo)\n", ruta);
        return 0; // no es error fatal: el CSV simplemente no tendrá esas filas
    }
    printf("  Imagen cargada: %s  (%dx%d)\n", ruta, img->ancho, img->alto);
    return 1;
}

// ── Experimentos ─────────────────────────────────────────────────────────────

// Experimento 1: Tipo de filtro
//   Fija: imagen 4000x4000, k=3, 256 hilos/bloque
//   Varía: media, nitidez, laplaciano
static void exp1_tipo_filtro(FILE *csv)
{
    printf("\n[Exp 1] Tipo de filtro (imagen 4000, k=3, 256 hilos)\n");

    Imagen img;
    if (!cargar_imagen(RUTA_4000, &img)) return;

    Mascara filtros[3];
    filtros[0] = mascara_media(3);
    filtros[1] = mascara_nitidez();
    filtros[2] = mascara_laplaciano();

    for (int f = 0; f < 3; f++) {
        printf("  Filtro: %s\n", filtros[f].nombre);
        medir_configuracion(csv, 1, &img, &filtros[f], 256);
        liberar_mascara(&filtros[f]);
    }

    liberar_imagen(&img);
}

// Experimento 2: Resolución
//   Fija: filtro media, k=9, 256 hilos/bloque
//   Varía: 2000x2000, 4000x4000, 6000x6000
static void exp2_resolucion(FILE *csv)
{
    printf("\n[Exp 2] Resolución (media 9x9, 256 hilos)\n");

    const char *rutas[3] = {RUTA_2000, RUTA_4000, RUTA_6000};
    Mascara m = mascara_media(9);

    for (int r = 0; r < 3; r++) {
        Imagen img;
        if (!cargar_imagen(rutas[r], &img)) continue;

        medir_configuracion(csv, 2, &img, &m, 256);
        liberar_imagen(&img);
    }

    liberar_mascara(&m);
}

// Experimento 3: Tamaño de máscara
//   Fija: imagen 4000x4000, filtro media, 256 hilos/bloque
//   Varía: k = 3, 9, 21
static void exp3_tamano_mascara(FILE *csv)
{
    printf("\n[Exp 3] Tamaño de máscara (imagen 4000, media, 256 hilos)\n");

    Imagen img;
    if (!cargar_imagen(RUTA_4000, &img)) return;

    int ks[3] = {3, 9, 21};
    for (int i = 0; i < 3; i++) {
        printf("  Máscara: media %dx%d\n", ks[i], ks[i]);
        Mascara m = mascara_media(ks[i]);
        medir_configuracion(csv, 3, &img, &m, 256);
        liberar_mascara(&m);
    }

    liberar_imagen(&img);
}

// Experimento 4: Hilos por bloque
//   Fija: imagen 4000x4000, filtro media, k=9
//   Varía: 128, 256, 512 hilos/bloque
static void exp4_hilos_por_bloque(FILE *csv)
{
    printf("\n[Exp 4] Hilos por bloque (imagen 4000, media 9x9)\n");

    Imagen img;
    if (!cargar_imagen(RUTA_4000, &img)) return;

    Mascara m = mascara_media(9);
    int configs[3] = {128, 256, 512};

    for (int i = 0; i < 3; i++) {
        printf("  Hilos/bloque: %d\n", configs[i]);
        medir_configuracion(csv, 4, &img, &m, configs[i]);
    }

    liberar_mascara(&m);
    liberar_imagen(&img);
}

// ── Punto de entrada público ──────────────────────────────────────────────────

void ejecutar_experimentos(void)
{
    printf("=== Iniciando experimentos (Bloque 3 - Andrés Morocho) ===\n");
    printf("CSV de salida: %s\n", RUTA_CSV);

    FILE *csv = abrir_csv(RUTA_CSV);
    if (csv == NULL) {
        printf("[ERROR] No se pudo crear %s\n", RUTA_CSV);
        return;
    }

    exp1_tipo_filtro(csv);
    exp2_resolucion(csv);
    exp3_tamano_mascara(csv);
    exp4_hilos_por_bloque(csv);

    fclose(csv);
    printf("\n=== Experimentos completados. Resultados en %s ===\n", RUTA_CSV);
}
