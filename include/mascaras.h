#ifndef MASCARAS_H
#define MASCARAS_H

#ifdef __cplusplus
extern "C" {
#endif

/* Máscara cuadrada de convolución, almacenada por filas. */
typedef struct {
    int k;
    float *coef;
    char nombre[32];
} Mascara;

Mascara mascara_media(int k);
Mascara mascara_nitidez(void);
Mascara mascara_laplaciano(void);
Mascara mascara_por_nombre(const char *nombre, int k);
void liberar_mascara(Mascara *m);
void imprimir_mascara(const Mascara *m);

#ifdef __cplusplus
}
#endif

#endif
