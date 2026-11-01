#ifndef COMUN_H
#define COMUN_H

#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 199309L
#endif
#include <time.h>

/* Diferencias por el orden de suma en float entre CPU y GPU; la diferencia
 * esperada es mucho menor a 1 nivel de gris. */
#define TOLERANCIA 1e-3f

/* Devuelve tiempo monotónico para medir exclusivamente el cálculo. */
static inline double tiempo_ms(void)
{
    struct timespec ahora;
    clock_gettime(CLOCK_MONOTONIC, &ahora);
    return (double)ahora.tv_sec * 1000.0 + (double)ahora.tv_nsec / 1000000.0;
}

#endif
