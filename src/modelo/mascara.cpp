// Máscaras de la práctica: media, nitidez y laplaciano. Bloque 1 - Michael Lata
#include "mascara.h"
#include <cstdlib>
#include <cstring>

// Reserva una máscara k x k (k impar) con su nombre.
Mascara crear_mascara(const char *nombre, int k)
{
    Mascara m;
    m.k = k;
    m.coef = (float *)malloc(k * k * sizeof(float));
    strncpy(m.nombre, nombre, sizeof(m.nombre) - 1);
    m.nombre[sizeof(m.nombre) - 1] = '\0';
    return m;
}

// Media: todos los coeficientes valen 1/(k*k). Suaviza la imagen.
Mascara mascara_media(int k)
{
    Mascara m = crear_mascara("media", k);
    int i;
    for (i = 0; i < k * k; i++)
        m.coef[i] = 1.0f / (k * k);
    return m;
}

// Nitidez: refuerza el píxel central frente a sus vecinos. Realza detalles.
Mascara mascara_nitidez(void)
{
    const float valores[9] = {0, -1, 0, -1, 5, -1, 0, -1, 0};
    Mascara m = crear_mascara("nitidez", 3);
    memcpy(m.coef, valores, sizeof(valores));
    return m;
}

// Laplaciano: responde a los cambios bruscos de intensidad (bordes).
Mascara mascara_laplaciano(void)
{
    const float valores[9] = {0, 1, 0, 1, -4, 1, 0, 1, 0};
    Mascara m = crear_mascara("laplaciano", 3);
    memcpy(m.coef, valores, sizeof(valores));
    return m;
}

void liberar_mascara(Mascara *m)
{
    free(m->coef);
    m->coef = NULL;
}
