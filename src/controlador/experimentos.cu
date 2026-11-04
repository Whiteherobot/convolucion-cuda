// Experimentos de rendimiento CPU vs GPU. Bloque 3 - Andrés Morocho
//
// Qué se mide aquí: los cuatro experimentos y sus configuraciones. Cómo se mide cada
// configuración (orden CPU/GPU, calentamiento, validación, CSV) está en medicion.cu.
//
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
#include "medicion.h"
#include "imagen.h"
#include "mascara.h"
#include "csv.h"

#include <cstdio>

#define RUTA_CSV "resultados/mediciones.csv"

static const char *RUTA_2000 = "datos/imagen_2000.pgm";
static const char *RUTA_4000 = "datos/imagen_4000.pgm";
static const char *RUTA_6000 = "datos/imagen_6000.pgm";

// Configuraciones fuera de tolerancia, para el resumen final.
static int fallas = 0;

static void medir(FILE *csv, int experimento, const Imagen *img, const Mascara *m, int hilos)
{
    if (!medir_configuracion(csv, experimento, img, m, hilos))
        fallas++;
}

// Una imagen que falta no detiene la corrida: el CSV simplemente no tendrá esas filas.
static int cargar_imagen(const char *ruta, Imagen *img)
{
    if (leer_pgm(ruta, img) != 0) {
        printf("[AVISO] No se pudo leer: %s  (omitiendo)\n", ruta);
        return 0;
    }
    printf("  Imagen cargada: %s  (%dx%d)\n", ruta, img->ancho, img->alto);
    return 1;
}

static void exp1_tipo_filtro(FILE *csv)
{
    printf("\n[Exp 1] Tipo de filtro (imagen 4000, k=3, 256 hilos)\n");
    Imagen img;
    if (!cargar_imagen(RUTA_4000, &img)) return;

    Mascara filtros[3] = {mascara_media(3), mascara_nitidez(), mascara_laplaciano()};
    for (int f = 0; f < 3; f++) {
        medir(csv, 1, &img, &filtros[f], 256);
        liberar_mascara(&filtros[f]);
    }
    liberar_imagen(&img);
}

static void exp2_resolucion(FILE *csv)
{
    printf("\n[Exp 2] Resolución (media 9x9, 256 hilos)\n");
    const char *rutas[3] = {RUTA_2000, RUTA_4000, RUTA_6000};
    Mascara m = mascara_media(9);

    for (int r = 0; r < 3; r++) {
        Imagen img;
        if (!cargar_imagen(rutas[r], &img)) continue;
        medir(csv, 2, &img, &m, 256);
        liberar_imagen(&img);
    }
    liberar_mascara(&m);
}

static void exp3_tamano_mascara(FILE *csv)
{
    printf("\n[Exp 3] Tamaño de máscara (imagen 4000, media, 256 hilos)\n");
    Imagen img;
    if (!cargar_imagen(RUTA_4000, &img)) return;

    int ks[3] = {3, 9, 21};
    for (int i = 0; i < 3; i++) {
        Mascara m = mascara_media(ks[i]);
        medir(csv, 3, &img, &m, 256);
        liberar_mascara(&m);
    }
    liberar_imagen(&img);
}

static void exp4_hilos_por_bloque(FILE *csv)
{
    printf("\n[Exp 4] Hilos por bloque (imagen 4000, media 9x9)\n");
    Imagen img;
    if (!cargar_imagen(RUTA_4000, &img)) return;

    Mascara m = mascara_media(9);
    int hilos[3] = {128, 256, 512};
    for (int i = 0; i < 3; i++)
        medir(csv, 4, &img, &m, hilos[i]);

    liberar_mascara(&m);
    liberar_imagen(&img);
}

void ejecutar_experimentos(void)
{
    printf("=== Experimentos: %d repeticiones, calentamiento GPU de %.0f ms ===\n",
           REPETICIONES, CALENTAMIENTO_GPU_MS);
    printf("CSV de salida: %s\n", RUTA_CSV);

    FILE *csv = abrir_csv(RUTA_CSV);
    if (csv == NULL) {
        printf("[ERROR] No se pudo crear %s\n", RUTA_CSV);
        return;
    }

    fallas = 0;
    exp1_tipo_filtro(csv);
    exp2_resolucion(csv);
    exp3_tamano_mascara(csv);
    exp4_hilos_por_bloque(csv);
    fclose(csv);

    printf("\n=== Experimentos completados: %d configuraciones fuera de tolerancia. "
           "Resultados en %s ===\n", fallas, RUTA_CSV);
}
