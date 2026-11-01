"""Esqueleto de análisis de las mediciones del Bloque 3."""
import csv
import statistics


def main():
    # TODO: calcular medianas, desviaciones y aceleraciones.
    # TODO: generar las gráficas con matplotlib.
    with open("resultados/mediciones.csv", newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    print("graficas: pendiente (Bloque 3), filas:", len(filas))


if __name__ == "__main__":
    main()
