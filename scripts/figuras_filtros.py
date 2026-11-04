#!/usr/bin/env python3
"""Imágenes representativas de los filtros para el informe. Bloque 3 - Andrés Morocho

Uso (desde la raíz del repo, después de compilar y de preparar_imagenes.py):
    python3 scripts/figuras_filtros.py [binario]        (por defecto ./build/convolucion)

1. Convierte datos/ejemplo_perro.jpg a grises (lado mayor 1200 px) -> datos/ejemplo_perro.pgm
2. Aplica cada filtro con el programa del repo en CPU:
       <binario> filtrar <entrada.pgm> <salida.pgm> <filtro> <k> cpu
   La conversión a 0-255 la hace guardar_pgm (redondeo y recorte), igual que en el programa.
3. Arma los paneles en resultados/:
       figura_filtros_imagen.png  recorte central 500x500 de datos/imagen_2000.pgm
       figura_filtros_perro.png   ejemplo_perro completo
       figura_bordes.png          esquina 120x120: efecto de la extensión con ceros
4. Escribe resultados/rangos_filtros.csv: mínimo, máximo y % de píxeles fuera de 0-255
   ANTES de la conversión, calculado con una convolución independiente en numpy
   (extensión con ceros, misma máscara).
"""

import csv
import os
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

BINARIO = sys.argv[1] if len(sys.argv) > 1 else "./build/convolucion"
DIR_PGM = "resultados/filtros"
FILTROS = [("media", 3), ("media", 9), ("media", 21), ("nitidez", 3), ("laplaciano", 3)]
TITULOS = {("media", 3): "Media 3×3", ("media", 9): "Media 9×9", ("media", 21): "Media 21×21",
           ("nitidez", 3): "Nitidez 3×3", ("laplaciano", 3): "Laplaciano 3×3"}


def mascara(filtro, k):
    if filtro == "media":
        return np.full((k, k), 1.0 / (k * k), dtype=np.float32)
    if filtro == "nitidez":
        return np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    return np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)


def convolucion_numpy(img, m):
    """Correlación con extensión con ceros, sumando una copia desplazada por coeficiente."""
    k = m.shape[0]
    r = k // 2
    ext = np.pad(img.astype(np.float32), r)
    sal = np.zeros(img.shape, dtype=np.float32)
    for i in range(k):
        for j in range(k):
            if m[i, j] != 0:
                sal += m[i, j] * ext[i:i + img.shape[0], j:j + img.shape[1]]
    return sal


def filtrar(entrada, base):
    os.makedirs(DIR_PGM, exist_ok=True)
    rutas = {}
    for filtro, k in FILTROS:
        salida = os.path.join(DIR_PGM, f"{base}_{filtro}_{k}.pgm")
        subprocess.run([BINARIO, "filtrar", entrada, salida, filtro, str(k), "cpu"],
                       check=True, stdout=subprocess.DEVNULL)
        rutas[(filtro, k)] = salida
    return rutas


def panel(original, rutas, titulo, nombre, recorte=None):
    items = [("Original", original)] + [(TITULOS[f], rutas[f]) for f in FILTROS]
    fig, axs = plt.subplots(2, 3, figsize=(10, 7.2))
    for ax, (t, ruta) in zip(axs.flat, items):
        im = Image.open(ruta).convert("L")
        if recorte:
            im = im.crop(recorte)
        ax.imshow(im, cmap="gray", vmin=0, vmax=255)
        ax.set_title(t)
        ax.axis("off")
    fig.suptitle(titulo)
    fig.tight_layout()
    ruta = os.path.join("resultados", nombre)
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Guardada: {ruta}")


def rangos(entradas):
    ruta = "resultados/rangos_filtros.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["imagen", "filtro", "k", "minimo", "maximo", "pct_bajo_0", "pct_sobre_255"])
        for nombre, entrada in entradas:
            img = np.array(Image.open(entrada).convert("L"))
            for filtro, k in FILTROS:
                s = convolucion_numpy(img, mascara(filtro, k))
                w.writerow([nombre, filtro, k, f"{s.min():.1f}", f"{s.max():.1f}",
                            f"{100 * (s < 0).mean():.1f}", f"{100 * (s > 255).mean():.1f}"])
    print(f"  Guardado: {ruta}")


def main():
    if not os.path.exists("datos/imagen_2000.pgm"):
        sys.exit("Falta datos/imagen_2000.pgm: ejecuta antes scripts/preparar_imagenes.py")
    perro = Image.open("datos/ejemplo_perro.jpg").convert("L")
    perro.thumbnail((1200, 1200))
    perro.save("datos/ejemplo_perro.pgm")

    r2000 = filtrar("datos/imagen_2000.pgm", "imagen_2000")
    rperro = filtrar("datos/ejemplo_perro.pgm", "ejemplo_perro")
    panel("datos/imagen_2000.pgm", r2000,
          "Imagen 2000×2000, recorte central 500×500 (salida recortada a 0–255)",
          "figura_filtros_imagen.png", (750, 750, 1250, 1250))
    panel("datos/ejemplo_perro.pgm", rperro,
          "ejemplo_perro.jpg en grises (salida recortada a 0–255)", "figura_filtros_perro.png")
    panel("datos/imagen_2000.pgm", r2000,
          "Esquina superior izquierda 120×120: efecto de la extensión con ceros",
          "figura_bordes.png", (0, 0, 120, 120))
    rangos([("imagen_2000", "datos/imagen_2000.pgm"), ("ejemplo_perro", "datos/ejemplo_perro.pgm")])


if __name__ == "__main__":
    main()
