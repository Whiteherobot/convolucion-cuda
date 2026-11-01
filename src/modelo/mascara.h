// Máscaras de convolución. Bloque 1 - Michael Lata
#ifndef MASCARA_H
#define MASCARA_H
struct Mascara {
    int k;          // tamaño k x k (impar)
    float *coef;    // coeficientes fila por fila
    char nombre[16];
};
Mascara crear_mascara(const char *nombre, int k);
Mascara mascara_media(int k);
Mascara mascara_nitidez(void);
Mascara mascara_laplaciano(void);
void liberar_mascara(Mascara *m);
#endif
