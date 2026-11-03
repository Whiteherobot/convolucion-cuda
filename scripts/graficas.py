#!/usr/bin/env python3
"""Procesa mediciones.csv y genera tablas y gráficas del informe. Bloque 3 - Andrés Morocho

Uso:
    python3 scripts/graficas.py [ruta_csv]        (por defecto resultados/mediciones.csv)

Salida (en resultados/):
    resumen.csv                 una fila por configuración: medianas, variabilidad,
                                aceleraciones y % de transferencias
    grafica_exp1_filtros.png    Exp 1: CPU, kernel y GPU total por tipo de filtro
    grafica_exp2_resolucion.png Exp 2: idem por resolución
    grafica_exp3_mascara.png    Exp 3: idem por tamaño de máscara
    grafica_exp4_hilos.png      Exp 4: distribución del kernel y desglose por hilos/bloque
    grafica_speedup.png         aceleración de cómputo y con transferencias
    grafica_gpu_desglose.png    % del tiempo GPU en H2D, kernel y D2H

Definiciones:
    mediana de las 5 repeticiones; variabilidad = desviación estándar y rango (máx - mín)
    aceleración de cómputo         = mediana CPU / mediana kernel
    aceleración con transferencias = mediana CPU / mediana total GPU (H2D + kernel + D2H)
"""

import csv
import os
import statistics
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SALIDA = "resultados"
COLOR = {"cpu": "#4C72B0", "kernel": "#C44E52", "total": "#DD8452",
         "h2d": "#55A868", "d2h": "#8172B2"}
plt.rcParams.update({"figure.dpi": 150, "font.size": 10, "axes.titlesize": 11,
                     "legend.fontsize": 9})

# Orden y eje variable de cada experimento: (título, clave variable, valores en orden)
EXPERIMENTOS = {
    1: ("Exp 1: tipo de filtro (4000×4000, 3×3, 256 hilos)", "filtro",
        ["media", "nitidez", "laplaciano"]),
    2: ("Exp 2: resolución (media 9×9, 256 hilos)", "resolucion",
        ["2000x2000", "4000x4000", "6000x6000"]),
    3: ("Exp 3: tamaño de máscara (media, 4000×4000, 256 hilos)", "mascara",
        ["3x3", "9x9", "21x21"]),
    4: ("Exp 4: hilos por bloque (media 9×9, 4000×4000)", "hilos_por_bloque",
        [128, 256, 512]),
}
CAMPOS_GPU = ["h2d_ms", "kernel_ms", "d2h_ms", "total_ms"]


# ── Carga ─────────────────────────────────────────────────────────────────────

def cargar_csv(ruta):
    filas = []
    with open(ruta, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for c in ("experimento", "hilos_por_bloque", "bloques", "repeticion"):
                r[c] = int(r[c])
            for c in CAMPOS_GPU + ["cpu_ms"]:
                r[c] = float(r[c])
            filas.append(r)
    print(f"Filas leídas: {len(filas)}")
    return filas


def estadisticos(valores):
    return {"mediana": statistics.median(valores),
            "desv": statistics.stdev(valores) if len(valores) > 1 else 0.0,
            "min": min(valores), "max": max(valores), "n": len(valores)}


# ── Resumen por configuración ─────────────────────────────────────────────────

def resumir(filas):
    """Devuelve {experimento: [dict por configuración en el orden de EXPERIMENTOS]}."""
    resumen = {}
    for exp, (_, clave, orden) in EXPERIMENTOS.items():
        resumen[exp] = []
        for valor in orden:
            gpu = [f for f in filas if f["experimento"] == exp
                   and f["implementacion"] == "gpu" and f[clave] == valor]
            if not gpu:
                print(f"  [AVISO] Exp {exp}: sin datos para {clave}={valor}")
                continue
            ref = gpu[0]
            # CPU de la misma imagen y máscara. En exp 4 la CPU no usa hilos: las tres
            # configuraciones comparten como referencia todas las filas CPU del experimento.
            cpu = [f for f in filas if f["experimento"] == exp
                   and f["implementacion"] == "cpu"
                   and f["filtro"] == ref["filtro"] and f["resolucion"] == ref["resolucion"]
                   and f["mascara"] == ref["mascara"]]
            c = {"experimento": exp, "variable": str(valor), "filtro": ref["filtro"],
                 "resolucion": ref["resolucion"], "mascara": ref["mascara"],
                 "hilos": ref["hilos_por_bloque"], "bloques": ref["bloques"],
                 "cpu": estadisticos([f["cpu_ms"] for f in cpu])}
            for campo in CAMPOS_GPU:
                c[campo[:-3]] = estadisticos([f[campo] for f in gpu])
            c["acel_computo"] = c["cpu"]["mediana"] / c["kernel"]["mediana"]
            c["acel_total"] = c["cpu"]["mediana"] / c["total"]["mediana"]
            c["pct_transf"] = 100 * (c["h2d"]["mediana"] + c["d2h"]["mediana"]) / c["total"]["mediana"]
            c["muestras_kernel"] = [f["kernel_ms"] for f in gpu]
            resumen[exp].append(c)
    return resumen


def guardar_resumen(resumen):
    ruta = os.path.join(SALIDA, "resumen.csv")
    cols = ["experimento", "variable", "filtro", "resolucion", "mascara", "hilos", "bloques"]
    tiempos = ["cpu", "h2d", "kernel", "d2h", "total"]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        cab = cols[:]
        for t in tiempos:
            cab += [f"{t}_mediana_ms", f"{t}_desv_ms", f"{t}_min_ms", f"{t}_max_ms"]
        cab += ["n_repeticiones", "aceleracion_computo", "aceleracion_con_transferencias",
                "porcentaje_transferencias"]
        w.writerow(cab)
        for exp in resumen.values():
            for c in exp:
                fila = [c[k] for k in cols]
                for t in tiempos:
                    fila += [f"{c[t][s]:.4f}" for s in ("mediana", "desv", "min", "max")]
                fila += [c["total"]["n"], f"{c['acel_computo']:.2f}",
                         f"{c['acel_total']:.2f}", f"{c['pct_transf']:.1f}"]
                w.writerow(fila)
    print(f"  Guardado: {ruta}")


def imprimir_resumen(resumen):
    print(f"\n{'=' * 100}")
    print(f"{'Exp':<4}{'Variable':<12}{'CPU med±desv (ms)':>22}{'Kernel (ms)':>16}"
          f"{'Total GPU (ms)':>18}{'Acel. cómp.':>12}{'Acel. total':>12}{'% transf':>10}")
    print("-" * 100)
    for exp in resumen.values():
        for c in exp:
            print(f"{c['experimento']:<4}{c['variable']:<12}"
                  f"{c['cpu']['mediana']:>13.2f} ± {c['cpu']['desv']:<6.2f}"
                  f"{c['kernel']['mediana']:>16.3f}{c['total']['mediana']:>18.3f}"
                  f"{c['acel_computo']:>11.1f}×{c['acel_total']:>11.1f}×{c['pct_transf']:>9.1f}%")
    print("=" * 100)


# ── Gráficas ──────────────────────────────────────────────────────────────────

def guardar(fig, nombre):
    ruta = os.path.join(SALIDA, nombre)
    fig.tight_layout()
    fig.savefig(ruta, bbox_inches="tight")
    plt.close(fig)
    print(f"  Guardada: {ruta}")


def etiqueta(exp, c):
    return f"{c['variable']} hilos" if exp == 4 else c["variable"].replace("x", "×")


def grafica_tiempos(exp, confs, nombre, xlabel):
    """CPU, kernel y total GPU por configuración. Eje Y logarítmico porque la CPU
    suele estar órdenes de magnitud por encima del kernel."""
    x = np.arange(len(confs))
    ancho = 0.27
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for i, (clave, texto) in enumerate([("cpu", "CPU secuencial"), ("kernel", "GPU kernel"),
                                        ("total", "GPU total (con transferencias)")]):
        med = [c[clave]["mediana"] for c in confs]
        err = [c[clave]["desv"] for c in confs]
        barras = ax.bar(x + (i - 1) * ancho, med, ancho, yerr=err, capsize=3,
                        color=COLOR[clave], label=texto)
        for b, v in zip(barras, med):
            ax.text(b.get_x() + b.get_width() / 2, v * 1.08, f"{v:.1f}" if v >= 1 else f"{v:.2f}",
                    ha="center", va="bottom", fontsize=7)
    ax.set_yscale("log")
    ax.set_title(EXPERIMENTOS[exp][0])
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Tiempo (ms, escala log)")
    ax.text(0.99, 0.01, "Barra: mediana de 5 rep.; línea: desv. estándar",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7, color="gray")
    ax.set_xticks(x)
    ax.set_xticklabels([etiqueta(exp, c) for c in confs])
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5, which="both")
    guardar(fig, nombre)


def grafica_hilos(confs):
    """Izquierda: cada repetición del kernel (variabilidad). Derecha: desglose GPU."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.5))
    etiquetas = [etiqueta(4, c) for c in confs]
    a1.boxplot([c["muestras_kernel"] for c in confs], showmeans=False)
    for i, c in enumerate(confs, start=1):
        a1.scatter([i] * len(c["muestras_kernel"]), c["muestras_kernel"],
                   color=COLOR["kernel"], s=14, zorder=3)
    a1.set_xticks(range(1, len(confs) + 1))
    a1.set_xticklabels(etiquetas)
    a1.set_title("Tiempo del kernel por repetición")
    a1.set_ylabel("Tiempo kernel (ms)")
    a1.grid(axis="y", linestyle="--", alpha=0.5)

    x = np.arange(len(confs))
    h2d = np.array([c["h2d"]["mediana"] for c in confs])
    ker = np.array([c["kernel"]["mediana"] for c in confs])
    d2h = np.array([c["d2h"]["mediana"] for c in confs])
    a2.bar(x, h2d, 0.5, color=COLOR["h2d"], label="CPU→GPU")
    a2.bar(x, ker, 0.5, bottom=h2d, color=COLOR["kernel"], label="Kernel")
    a2.bar(x, d2h, 0.5, bottom=h2d + ker, color=COLOR["d2h"], label="GPU→CPU")
    a2.set_xticks(x)
    a2.set_xticklabels(etiquetas)
    a2.set_title("Desglose GPU (medianas)")
    a2.set_ylabel("Tiempo (ms)")
    a2.legend()
    a2.grid(axis="y", linestyle="--", alpha=0.5)
    fig.suptitle(EXPERIMENTOS[4][0])
    guardar(fig, "grafica_exp4_hilos.png")


def todas_las_configuraciones(resumen):
    return [(exp, c) for exp, confs in resumen.items() for c in confs]


def grafica_speedup(resumen):
    pares = todas_las_configuraciones(resumen)
    x = np.arange(len(pares))
    comp = [c["acel_computo"] for _, c in pares]
    total = [c["acel_total"] for _, c in pares]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(x - 0.2, comp, 0.4, color=COLOR["kernel"], label="Cómputo (CPU / kernel)")
    ax.bar(x + 0.2, total, 0.4, color=COLOR["total"], label="Con transferencias (CPU / total)")
    for xi, v in zip(x - 0.2, comp):
        ax.text(xi, v * 1.08, f"{v:.0f}×", ha="center", fontsize=7)
    for xi, v in zip(x + 0.2, total):
        ax.text(xi, v * 1.08, f"{v:.1f}×", ha="center", fontsize=7)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1, label="Aceleración = 1")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([f"E{e}: {etiqueta(e, c)}" for e, c in pares], rotation=30,
                       ha="right", fontsize=8)
    ax.set_ylabel("Aceleración (escala log)")
    ax.set_title("Aceleración respecto a la CPU secuencial (medianas)")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5, which="both")
    guardar(fig, "grafica_speedup.png")


def grafica_desglose(resumen):
    pares = todas_las_configuraciones(resumen)
    x = np.arange(len(pares))
    tot = np.array([c["h2d"]["mediana"] + c["kernel"]["mediana"] + c["d2h"]["mediana"]
                    for _, c in pares])
    h2d = 100 * np.array([c["h2d"]["mediana"] for _, c in pares]) / tot
    ker = 100 * np.array([c["kernel"]["mediana"] for _, c in pares]) / tot
    d2h = 100 * np.array([c["d2h"]["mediana"] for _, c in pares]) / tot
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(x, h2d, 0.6, color=COLOR["h2d"], label="CPU→GPU")
    ax.bar(x, ker, 0.6, bottom=h2d, color=COLOR["kernel"], label="Kernel")
    ax.bar(x, d2h, 0.6, bottom=h2d + ker, color=COLOR["d2h"], label="GPU→CPU")
    for xi, p in zip(x, h2d + d2h):
        ax.text(xi, 101, f"{p:.0f}%", ha="center", fontsize=7)
    ax.set_ylim(0, 110)
    ax.set_xticks(x)
    ax.set_xticklabels([f"E{e}: {etiqueta(e, c)}" for e, c in pares], rotation=30,
                       ha="right", fontsize=8)
    ax.set_ylabel("% del tiempo GPU total")
    ax.set_title("Proporción del tiempo GPU (número arriba = % en transferencias)")
    ax.legend(loc="lower right")
    guardar(fig, "grafica_gpu_desglose.png")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ruta_csv = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SALIDA, "mediciones.csv")
    if not os.path.exists(ruta_csv):
        print(f"[ERROR] No se encontró: {ruta_csv}. Ejecuta primero: ./build/convolucion medir")
        sys.exit(1)
    os.makedirs(SALIDA, exist_ok=True)

    resumen = resumir(cargar_csv(ruta_csv))
    guardar_resumen(resumen)
    xlabels = {1: "Tipo de filtro", 2: "Resolución (píxeles)", 3: "Tamaño de máscara (k×k)"}
    nombres = {1: "grafica_exp1_filtros.png", 2: "grafica_exp2_resolucion.png",
               3: "grafica_exp3_mascara.png"}
    for exp in (1, 2, 3):
        if resumen[exp]:
            grafica_tiempos(exp, resumen[exp], nombres[exp], xlabels[exp])
    if resumen[4]:
        grafica_hilos(resumen[4])
    if any(resumen.values()):
        grafica_speedup(resumen)
        grafica_desglose(resumen)
    imprimir_resumen(resumen)


if __name__ == "__main__":
    main()
