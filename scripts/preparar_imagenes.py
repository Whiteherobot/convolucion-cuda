#!/usr/bin/env python3
"""Prepara imágenes cuadradas PGM para los experimentos."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def imagen_sintetica():
    lado = 6000
    imagen = Image.new("L", (lado, lado))
    pixeles = imagen.load()
    for y in range(lado):
        for x in range(lado):
            pixeles[x, y] = (x * 255 // (lado - 1) + y * 255 // (lado - 1)) // 2
    dibujo = ImageDraw.Draw(imagen)
    dibujo.ellipse((1000, 1000, 3000, 3000), fill=220)
    dibujo.ellipse((3300, 2500, 5500, 5200), fill=40)
    return imagen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("entrada", nargs="?", help="imagen de entrada")
    parser.add_argument("-o", "--salida", default="datos", help="carpeta de salida")
    parser.add_argument("--sintetica", action="store_true")
    args = parser.parse_args()
    if args.sintetica:
        imagen = imagen_sintetica()
        print("Imagen sintética original: 6000x6000")
    elif args.entrada:
        imagen = Image.open(args.entrada).convert("L")
        print("Tamaño original:", imagen.size)
    else:
        parser.error("indique una entrada o use --sintetica")
    lado = min(imagen.size)
    izquierda = (imagen.width - lado) // 2
    arriba = (imagen.height - lado) // 2
    imagen = imagen.crop((izquierda, arriba, izquierda + lado, arriba + lado))
    print("Recorte cuadrado:", imagen.size)
    if lado < 6000:
        print("Aviso: se hará ampliación para alcanzar 6000x6000.")
    carpeta = Path(args.salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    for tamano in (2000, 4000, 6000):
        salida = carpeta / f"imagen_{tamano}.pgm"
        imagen.resize((tamano, tamano), Image.Resampling.LANCZOS).save(salida)
        print("Salida:", salida)


if __name__ == "__main__":
    main()
