#ifndef CONV_CPU_H
#define CONV_CPU_H

#include "imagen.h"
#include "mascaras.h"

#ifdef __cplusplus
extern "C" {
#endif

void convolucion_cpu(const Imagen *entrada, Imagen *salida, const Mascara *m);

#ifdef __cplusplus
}
#endif

#endif
