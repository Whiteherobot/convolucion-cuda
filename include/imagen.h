#ifndef IMAGEN_H
#define IMAGEN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Tipos y operaciones de entrada/salida para imágenes PGM en escala de grises. */
typedef struct {
    int ancho;
    int alto;
    float *datos;
} Imagen;

Imagen crear_imagen(int ancho, int alto);
void liberar_imagen(Imagen *img);
int leer_pgm(const char *ruta, Imagen *img);
int guardar_pgm(const char *ruta, const Imagen *img);

/* Redondea al entero más cercano y recorta el resultado al intervalo [0, 255].
 * Para el laplaciano también podría usarse el valor absoluto, pero se aplica
 * clamp a todos los filtros para mantener condiciones comunes. La validación
 * numérica se hace sobre los float antes de esta conversión. */
unsigned char a_rango_visual(float v);

#ifdef __cplusplus
}
#endif

#endif
