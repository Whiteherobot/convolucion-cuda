// Datos y operaciones de imágenes PGM. Bloque 1 - Michael Lata
#ifndef IMAGEN_H
#define IMAGEN_H
struct Imagen {
    int ancho;
    int alto;
    float *datos;  // píxeles fila por fila
};
Imagen crear_imagen(int ancho, int alto);
void liberar_imagen(Imagen *img);
int leer_pgm(const char *ruta, Imagen *img);
int guardar_pgm(const char *ruta, const Imagen *img);
unsigned char a_rango_visual(float valor);
#endif
