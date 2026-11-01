/* Construcción y presentación de filtros de convolución. */
#include "mascaras.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static Mascara crear_mascara(int k, const char *nombre)
{
    Mascara m;
    m.k = k;
    m.coef = NULL;
    snprintf(m.nombre, sizeof(m.nombre), "%s", nombre);
    if (k > 0 && k % 2 == 1)
        m.coef = (float *)malloc((size_t)k * (size_t)k * sizeof(float));
    return m;
}

/* La máscara media suaviza y reduce variaciones locales de intensidad. */
Mascara mascara_media(int k)
{
    Mascara m = crear_mascara(k, "media");
    int i;
    if (m.coef != NULL)
        for (i = 0; i < k * k; ++i)
            m.coef[i] = 1.0f / (float)(k * k);
    return m;
}

/* Nitidez realza bordes al enfatizar el píxel central. */
Mascara mascara_nitidez(void)
{
    Mascara m = crear_mascara(3, "nitidez");
    static const float valores[] = {0, -1, 0, -1, 5, -1, 0, -1, 0};
    if (m.coef != NULL)
        memcpy(m.coef, valores, sizeof(valores));
    return m;
}

/* El laplaciano detecta cambios de intensidad y bordes. */
Mascara mascara_laplaciano(void)
{
    Mascara m = crear_mascara(3, "laplaciano");
    static const float valores[] = {0, 1, 0, 1, -4, 1, 0, 1, 0};
    if (m.coef != NULL)
        memcpy(m.coef, valores, sizeof(valores));
    return m;
}

Mascara mascara_por_nombre(const char *nombre, int k)
{
    if (nombre == NULL)
        return crear_mascara(0, "invalida");
    if (strcmp(nombre, "media") == 0)
        return mascara_media(k);
    if (strcmp(nombre, "nitidez") == 0)
        return mascara_nitidez();
    if (strcmp(nombre, "laplaciano") == 0)
        return mascara_laplaciano();
    return crear_mascara(0, "invalida");
}

void liberar_mascara(Mascara *m)
{
    if (m == NULL)
        return;
    free(m->coef);
    m->coef = NULL;
    m->k = 0;
}

void imprimir_mascara(const Mascara *m)
{
    int i, j;
    if (m == NULL || m->coef == NULL)
        return;
    printf("Mascara %s (%dx%d):\n", m->nombre, m->k, m->k);
    for (i = 0; i < m->k; ++i) {
        for (j = 0; j < m->k; ++j)
            printf("%8.3f ", m->coef[i * m->k + j]);
        putchar('\n');
    }
}
