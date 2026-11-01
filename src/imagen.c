/* Implementación de memoria y lectura/escritura de imágenes PGM P5. */
#include "imagen.h"
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

Imagen crear_imagen(int ancho, int alto)
{
    Imagen img;
    img.ancho = ancho;
    img.alto = alto;
    img.datos = NULL;
    if (ancho > 0 && alto > 0)
        img.datos = (float *)calloc((size_t)ancho * (size_t)alto, sizeof(float));
    return img;
}

void liberar_imagen(Imagen *img)
{
    if (img == NULL)
        return;
    free(img->datos);
    img->datos = NULL;
    img->ancho = 0;
    img->alto = 0;
}

/* Lee un token de la cabecera y descarta espacios y comentarios. */
static int leer_token(FILE *f, char *token, size_t capacidad)
{
    int c;
    size_t i = 0;
    do {
        c = fgetc(f);
        if (c == '#') {
            do c = fgetc(f); while (c != '\n' && c != EOF);
        }
    } while (c != EOF && isspace((unsigned char)c));
    if (c == EOF)
        return -1;
    do {
        if (i + 1 < capacidad)
            token[i++] = (char)c;
        c = fgetc(f);
    } while (c != EOF && !isspace((unsigned char)c) && c != '#');
    if (c == '#') {
        do c = fgetc(f); while (c != '\n' && c != EOF);
    }
    token[i] = '\0';
    return i == 0 ? -1 : 0;
}

int leer_pgm(const char *ruta, Imagen *img)
{
    FILE *f;
    char token[64];
    long cantidad;
    unsigned char *pixeles;
    Imagen temporal;
    int i, ancho, alto, maximo;

    if (ruta == NULL || img == NULL)
        return -1;
    f = fopen(ruta, "rb");
    if (f == NULL)
        return -1;
    if (leer_token(f, token, sizeof(token)) != 0 || strcmp(token, "P5") != 0 ||
        leer_token(f, token, sizeof(token)) != 0) {
        fclose(f);
        return -1;
    }
    ancho = atoi(token);
    if (leer_token(f, token, sizeof(token)) != 0) {
        fclose(f);
        return -1;
    }
    alto = atoi(token);
    if (leer_token(f, token, sizeof(token)) != 0) {
        fclose(f);
        return -1;
    }
    maximo = atoi(token);
    if (ancho <= 0 || alto <= 0 || maximo != 255) {
        fclose(f);
        return -1;
    }
    cantidad = (long)ancho * (long)alto;
    pixeles = (unsigned char *)malloc((size_t)cantidad);
    if (pixeles == NULL || fread(pixeles, 1, (size_t)cantidad, f) != (size_t)cantidad) {
        free(pixeles);
        fclose(f);
        return -1;
    }
    fclose(f);
    temporal = crear_imagen(ancho, alto);
    if (temporal.datos == NULL) {
        free(pixeles);
        return -1;
    }
    for (i = 0; i < cantidad; ++i)
        temporal.datos[i] = (float)pixeles[i];
    free(pixeles);
    liberar_imagen(img);
    *img = temporal;
    return 0;
}

unsigned char a_rango_visual(float v)
{
    float redondeado;
    if (isnan(v) || v <= 0.0f)
        return 0;
    if (v >= 255.0f)
        return 255;
    redondeado = floorf(v + 0.5f);
    return (unsigned char)redondeado;
}

int guardar_pgm(const char *ruta, const Imagen *img)
{
    FILE *f;
    size_t cantidad, i;
    unsigned char *pixeles;
    if (ruta == NULL || img == NULL || img->datos == NULL ||
        img->ancho <= 0 || img->alto <= 0)
        return -1;
    cantidad = (size_t)img->ancho * (size_t)img->alto;
    pixeles = (unsigned char *)malloc(cantidad);
    if (pixeles == NULL)
        return -1;
    for (i = 0; i < cantidad; ++i)
        pixeles[i] = a_rango_visual(img->datos[i]);
    f = fopen(ruta, "wb");
    if (f == NULL || fprintf(f, "P5\n%d %d\n255\n", img->ancho, img->alto) < 0 ||
        fwrite(pixeles, 1, cantidad, f) != cantidad) {
        free(pixeles);
        if (f != NULL) fclose(f);
        return -1;
    }
    free(pixeles);
    return fclose(f) == 0 ? 0 : -1;
}
