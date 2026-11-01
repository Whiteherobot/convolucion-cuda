/* Prueba manual de la figura 1, bordes y máscara media. */
#include "conv_cpu.h"
#include <math.h>
#include <stdio.h>

static int cerca(float a, float b)
{
    return fabsf(a - b) < 1e-4f;
}

static void imprimir_imagen(const Imagen *img)
{
    int i, j;
    for (i = 0; i < img->alto; ++i) {
        for (j = 0; j < img->ancho; ++j)
            printf("%8.3f ", img->datos[i * img->ancho + j]);
        putchar('\n');
    }
}

int main(void)
{
    static const float valores[] = {
        35,40,41,45,50, 40,40,42,46,52, 42,46,50,55,55,
        48,52,56,58,60, 56,60,65,70,75
    };
    static const float coeficientes[] = {-2,-1,0, -1,1,1, 0,1,2};
    Imagen entrada = crear_imagen(5, 5);
    Imagen salida = crear_imagen(5, 5);
    Mascara figura = {3, NULL, "figura1"};
    Mascara media;
    Imagen salida_media;
    int fallo = 0, i;
    figura.coef = (float *)coeficientes;
    for (i = 0; i < 25; ++i)
        entrada.datos[i] = valores[i];
    convolucion_cpu(&entrada, &salida, &figura);
    printf("Salida figura 1:\n");
    imprimir_imagen(&salida);
    /* 35*(-2)+40*(-1)+41*0+40*(-1)+40*1+42*1+42*0+46*1+50*2=78 */
    if (!cerca(salida.datos[1 * 5 + 1], 78.0f) ||
        !cerca(salida.datos[1 * 5 + 2], 87.0f)) {
        printf("FALLA: valores centrales\n");
        fallo = 1;
    } else {
        printf("OK: valores centrales\n");
    }
    /* En (0,0), la extensión de ceros deja 35+40+40+2*40=195. */
    if (!cerca(salida.datos[0], 195.0f)) {
        printf("FALLA: esquina (0,0), esperado 195, obtenido %.3f\n", salida.datos[0]);
        fallo = 1;
    } else {
        printf("OK: esquina con ceros\n");
    }
    media = mascara_media(3);
    salida_media = crear_imagen(5, 5);
    convolucion_cpu(&entrada, &salida_media, &media);
    if (!cerca(salida_media.datos[2 * 5 + 2], 445.0f / 9.0f)) {
        printf("FALLA: media central\n");
        fallo = 1;
    } else {
        printf("OK: media central\n");
    }
    liberar_imagen(&salida_media);
    liberar_mascara(&media);
    liberar_imagen(&salida);
    liberar_imagen(&entrada);
    return fallo ? 1 : 0;
}
