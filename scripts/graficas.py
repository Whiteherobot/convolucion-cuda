#!/usr/bin/env python3
"""Lee mediciones y prepara gráficas. Bloque 3 - Andrés Morocho"""
import csv


def main():
    with open("resultados/mediciones.csv", newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    # TODO: calcular medianas y variabilidad por experimento.
    # TODO: calcular aceleraciones y crear gráficas con matplotlib.
    print(f"Filas leídas: {len(filas)}")


if __name__ == "__main__":
    main()
