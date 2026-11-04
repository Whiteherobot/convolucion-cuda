// Medición de una configuración: bloque CPU, calentamiento GPU, bloque GPU y validación. Bloque 3 - Andrés Morocho
//
// Orden y motivo (corridas 1 y 2, ver resultados/):
//   1. CPU: 1 calentamiento + REPETICIONES medidas, seguidas.
//   2. GPU: calentamiento de al menos CALENTAMIENTO_GPU_MS de trabajo continuo.
//   3. GPU: REPETICIONES medidas, seguidas, sin escribir nada entre ellas.
//   4. Validación de la última salida GPU medida contra la CPU, y escritura del CSV.
//
// Antes CPU y GPU se alternaban en cada repetición con un solo calentamiento de pocos ms.
// Mientras la CPU calculaba (hasta 6,7 s con 21x21) la GPU quedaba sin trabajo y bajaba
// de reloj y de enlace PCIe, así que cada repetición GPU caía en un estado distinto: la
// misma media 3x3 en 4000 dio un kernel de 5,45 ms en el exp 1 y de 0,67 ms en el exp 3.
// La CPU no tiene ese problema (variación < 3 %), por eso medirla en bloque no cambia
// sus resultados y deja a la GPU trabajar sin pausas.

#include "medicion.h"
#include "convolucion_cpu.h"
#include "convolucion_gpu.h"
#include "csv.h"
#include "pruebas.h"     // TOLERANCIA

#include <chrono>
#include <cmath>
#include <ctime>

typedef std::chrono::steady_clock Reloj;

// Lo que se repite en cada fila del CSV de una configuración.
struct Configuracion {
    int experimento;
    const Imagen  *entrada;
    const Mascara *mascara;
    int  hilos;
    int  bloques;
    char resolucion[32];   // "4000x4000"
    char tam_mascara[16];  // "9x9"
};

static double ms_desde(Reloj::time_point inicio)
{
    return std::chrono::duration<double, std::milli>(Reloj::now() - inicio).count();
}

// Hora local con milisegundos, para ubicar cada bloque GPU en gpu_estado.csv
// (nvidia-smi registra la hora; el CSV de mediciones no).
static void hora_actual(char *buf, int tam)
{
    auto ahora = std::chrono::system_clock::now();
    std::time_t seg = std::chrono::system_clock::to_time_t(ahora);
    int ms = (int)(std::chrono::duration_cast<std::chrono::milliseconds>(
                       ahora.time_since_epoch()).count() % 1000);
    char hms[16];
    std::strftime(hms, sizeof(hms), "%H:%M:%S", std::localtime(&seg));
    snprintf(buf, tam, "%s.%03d", hms, ms);
}

// ── 1. CPU ───────────────────────────────────────────────────────────────────
// Solo convolucion_cpu queda dentro del cronómetro.
static void medir_cpu(const Configuracion *c, Imagen *salida, double cpu_ms[REPETICIONES])
{
    convolucion_cpu(c->entrada, salida, c->mascara);   // calentamiento: cachés y páginas
    for (int rep = 0; rep < REPETICIONES; rep++) {
        Reloj::time_point t0 = Reloj::now();
        convolucion_cpu(c->entrada, salida, c->mascara);
        cpu_ms[rep] = ms_desde(t0);
    }
}

// ── 2. Calentamiento GPU ─────────────────────────────────────────────────────
// Por tiempo y no por número de llamadas: una llamada tarda de ~12 ms (3x3) a ~240 ms
// (21x21), así que un número fijo daría calentamientos muy distintos. Se imprime el
// kernel de la primera y la última llamada para ver en la consola si la GPU subió.
static void calentar_gpu(const Configuracion *c, Imagen *salida)
{
    TiemposGPU t;
    Reloj::time_point inicio = Reloj::now();
    convolucion_gpu(c->entrada, salida, c->mascara, c->hilos, &t);
    float primer_kernel = t.kernel_ms;
    int llamadas = 1;
    while (ms_desde(inicio) < CALENTAMIENTO_GPU_MS) {
        convolucion_gpu(c->entrada, salida, c->mascara, c->hilos, &t);
        llamadas++;
    }
    printf("      calentamiento GPU: %d llamadas en %.0f ms, kernel %.3f -> %.3f ms\n",
           llamadas, ms_desde(inicio), primer_kernel, t.kernel_ms);
}

// ── 3. GPU ───────────────────────────────────────────────────────────────────
// Los tiempos se guardan en memoria y se escriben al final: así no hay escritura de
// archivo (fflush) entre repeticiones que deje a la GPU sin trabajo.
static void medir_gpu(const Configuracion *c, Imagen *salida, TiemposGPU t[REPETICIONES])
{
    char inicio[16], fin[16];
    hora_actual(inicio, sizeof(inicio));
    for (int rep = 0; rep < REPETICIONES; rep++)
        convolucion_gpu(c->entrada, salida, c->mascara, c->hilos, &t[rep]);
    hora_actual(fin, sizeof(fin));
    printf("      GPU medida de %s a %s\n", inicio, fin);
}

// ── 4. Validación ────────────────────────────────────────────────────────────
// Se compara la salida de la última repetición medida (no la del calentamiento), en
// float y antes de pasar a 0-255. Devuelve 1 si el error máximo está bajo TOLERANCIA.
static int validar(const Configuracion *c, const Imagen *cpu, const Imagen *gpu)
{
    int n = cpu->ancho * cpu->alto;
    float err_max = 0.0f;
    double err_suma = 0.0;
    for (int i = 0; i < n; i++) {
        float e = fabsf(cpu->datos[i] - gpu->datos[i]);
        if (e > err_max) err_max = e;
        err_suma += e;
    }
    int ok = err_max < TOLERANCIA;
    printf("    %s %s %s, %d hilos x %d bloques: error max %.2e, medio %.2e %s\n",
           c->mascara->nombre, c->tam_mascara, c->resolucion, c->hilos, c->bloques,
           err_max, err_suma / n, ok ? "OK" : "FUERA DE TOLERANCIA");
    return ok;
}

static void escribir_filas(FILE *csv, const Configuracion *c,
                           const double cpu_ms[REPETICIONES], const TiemposGPU gpu[REPETICIONES])
{
    for (int rep = 0; rep < REPETICIONES; rep++)
        escribir_fila_csv(csv, c->experimento, "cpu", c->mascara->nombre, c->resolucion,
                          c->tam_mascara, 0, 0, rep + 1,
                          0.0f, 0.0f, 0.0f, 0.0f, cpu_ms[rep], "ms");
    for (int rep = 0; rep < REPETICIONES; rep++)
        escribir_fila_csv(csv, c->experimento, "gpu", c->mascara->nombre, c->resolucion,
                          c->tam_mascara, c->hilos, c->bloques, rep + 1,
                          gpu[rep].h2d_ms, gpu[rep].kernel_ms, gpu[rep].d2h_ms,
                          gpu[rep].total_ms, 0.0, "ms");
}

int medir_configuracion(FILE *csv, int experimento, const Imagen *entrada,
                        const Mascara *mascara, int hilos_por_bloque)
{
    Configuracion c;
    c.experimento = experimento;
    c.entrada     = entrada;
    c.mascara     = mascara;
    c.hilos       = hilos_por_bloque;
    c.bloques     = (entrada->ancho * entrada->alto + hilos_por_bloque - 1) / hilos_por_bloque;
    snprintf(c.resolucion, sizeof(c.resolucion), "%dx%d", entrada->ancho, entrada->alto);
    snprintf(c.tam_mascara, sizeof(c.tam_mascara), "%dx%d", mascara->k, mascara->k);

    Imagen salida_cpu = crear_imagen(entrada->ancho, entrada->alto);
    Imagen salida_gpu = crear_imagen(entrada->ancho, entrada->alto);
    double     cpu_ms[REPETICIONES];
    TiemposGPU gpu[REPETICIONES];

    medir_cpu(&c, &salida_cpu, cpu_ms);
    calentar_gpu(&c, &salida_gpu);
    medir_gpu(&c, &salida_gpu, gpu);
    int ok = validar(&c, &salida_cpu, &salida_gpu);
    escribir_filas(csv, &c, cpu_ms, gpu);

    liberar_imagen(&salida_cpu);
    liberar_imagen(&salida_gpu);
    return ok;
}
