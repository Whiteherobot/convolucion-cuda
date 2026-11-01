// Lectura, escritura y memoria de imágenes PGM en escala de grises. Bloque 1 - Michael Lata
#include "imagen.h"
#include <cstdio>
#include <cstdlib>

Imagen crear_imagen(int ancho, int alto)
{
    Imagen img;
    img.ancho = ancho;
    img.alto = alto;
    img.datos = (float *)calloc((size_t)ancho * alto, sizeof(float));
    return img;
}

void liberar_imagen(Imagen *img)
{
    free(img->datos);
    img->datos = NULL;
}

// Lee un PGM binario (P5) de 8 bits y pasa cada píxel a float.
int leer_pgm(const char *ruta, Imagen *img)
{
    FILE *archivo = fopen(ruta, "rb");
    char tipo[3];
    int ancho, alto, maximo, i;
    unsigned char *pixeles;

    if (archivo == NULL)
        return -1;
    if (fscanf(archivo, "%2s %d %d %d", tipo, &ancho, &alto, &maximo) != 4 ||
        tipo[0] != 'P' || tipo[1] != '5' || maximo != 255) {
        fclose(archivo);
        return -1;
    }
    fgetc(archivo); // salto de línea antes de los píxeles

    pixeles = (unsigned char *)malloc((size_t)ancho * alto);
    fread(pixeles, 1, (size_t)ancho * alto, archivo);
    fclose(archivo);

    *img = crear_imagen(ancho, alto);
    for (i = 0; i < ancho * alto; i++)
        img->datos[i] = pixeles[i];
    free(pixeles);
    return 0;
}

// Pasa un resultado float al rango visible: redondea y recorta a [0, 255].
unsigned char a_rango_visual(float valor)
{
    if (valor <= 0.0f)
        return 0;
    if (valor >= 255.0f)
        return 255;
    return (unsigned char)(valor + 0.5f);
}

// Guarda como PGM. La conversión a 0-255 se hace solo aquí, al final.
int guardar_pgm(const char *ruta, const Imagen *img)
{
    FILE *archivo = fopen(ruta, "wb");
    int i, n = img->ancho * img->alto;
    unsigned char *pixeles;

    if (archivo == NULL)
        return -1;
    pixeles = (unsigned char *)malloc(n);
    for (i = 0; i < n; i++)
        pixeles[i] = a_rango_visual(img->datos[i]);

    fprintf(archivo, "P5\n%d %d\n255\n", img->ancho, img->alto);
    fwrite(pixeles, 1, n, archivo);
    fclose(archivo);
    free(pixeles);
    return 0;
}
