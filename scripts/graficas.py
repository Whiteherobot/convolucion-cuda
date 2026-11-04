#!/usr/bin/env python3
"""Procesa mediciones.csv y genera tablas y gráficas del informe. Bloque 3 - Andrés Morocho

Uso:
    python3 scripts/graficas.py [ruta_csv] [sufijo]
    (por defecto resultados/mediciones.csv y sin sufijo; con sufijo "_corrida1" cada archivo
    de salida se llama p.ej. resumen_corrida1.csv, así no se pisan los de otra corrida)

Salida (en resultados/):
    resumen.csv                 una fila por configuración: medianas, variabilidad,
                                aceleraciones y % de transferencias
    tabla_resumen.tex           la misma tabla en LaTeX (la incluye informe/informe.tex)
    grafica_exp1_filtros.png    Exp 1: CPU, kernel y GPU total por tipo de filtro
    grafica_exp2_resolucion.png Exp 2: idem por resolución
    grafica_exp3_mascara.png    Exp 3: idem por tamaño de máscara
    grafica_exp4_hilos.png      Exp 4: distribución del kernel y desglose por hilos/bloque
    grafica_speedup.png         aceleración de cómputo y con transferencias
    grafica_gpu_desglose.png    % del tiempo GPU en H2D, kernel y D2H
    grafica_repeticiones.png    cada repetición GPU en orden de ejecución (estabilidad)

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
SUFIJO = ""   # se fija en main() con el segundo argumento
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
            # Porcentajes por repetición y después la mediana: combinar medianas de
            # componentes que vienen de repeticiones distintas puede dar un % que no ocurrió.
            pct = {campo: [100 * f[campo] / f["total_ms"] for f in gpu]
                   for campo in ("h2d_ms", "kernel_ms", "d2h_ms")}
            transf = [a + b for a, b in zip(pct["h2d_ms"], pct["d2h_ms"])]
            c["pct_transf"] = statistics.median(transf)
            c["pct_transf_min"], c["pct_transf_max"] = min(transf), max(transf)
            c["pct_partes"] = {campo[:-3]: statistics.median(v) for campo, v in pct.items()}
            c["muestras_kernel"] = [f["kernel_ms"] for f in gpu]
            resumen[exp].append(c)
    return resumen


def con_sufijo(nombre):
    base, ext = os.path.splitext(nombre)
    return os.path.join(SALIDA, base + SUFIJO + ext)


def guardar_tabla_latex(resumen):
    """Tabla para el informe: medianas (ms), desviación, aceleraciones y % de transferencias."""
    ruta = con_sufijo("tabla_resumen.tex")
    nombres = {1: "Filtro", 2: "Resolución", 3: "Máscara", 4: "Hilos/bloque"}
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("% Generado por scripts/graficas.py; no editar a mano.\n")
        f.write("\\begin{tabular}{llrrrrrrrr}\n\\toprule\n")
        f.write("Exp. & Valor & CPU & $\\sigma_{CPU}$ & CPU$\\to$GPU & Kernel & $\\sigma_{K}$"
                " & Total GPU & Acel. & \\% transf. \\\\\n")
        f.write(" & & (ms) & (ms) & (ms) & (ms) & (ms) & (ms) & cómp./total & \\\\\n\\midrule\n")
        for exp, confs in resumen.items():
            for i, c in enumerate(confs):
                etiqueta_exp = f"{exp} ({nombres[exp]})" if i == 0 else ""
                f.write(f"{etiqueta_exp} & {c['variable'].replace('x', '$\\times$')} & "
                        f"{c['cpu']['mediana']:.1f} & {c['cpu']['desv']:.1f} & "
                        f"{c['h2d']['mediana']:.2f} & {c['kernel']['mediana']:.2f} & "
                        f"{c['kernel']['desv']:.2f} & {c['total']['mediana']:.2f} & "
                        f"{c['acel_computo']:.1f} / {c['acel_total']:.1f} & "
                        f"{c['pct_transf']:.1f} \\\\\n")
            if confs and exp != 4:
                f.write("\\midrule\n")
        f.write("\\bottomrule\n\\end{tabular}\n")
    print(f"  Guardado: {ruta}")


def guardar_resumen(resumen):
    ruta = con_sufijo("resumen.csv")
    cols = ["experimento", "variable", "filtro", "resolucion", "mascara", "hilos", "bloques"]
    tiempos = ["cpu", "h2d", "kernel", "d2h", "total"]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        cab = cols[:]
        for t in tiempos:
            cab += [f"{t}_mediana_ms", f"{t}_desv_ms", f"{t}_min_ms", f"{t}_max_ms"]
        cab += ["n_repeticiones", "aceleracion_computo", "aceleracion_con_transferencias",
                "porcentaje_transferencias", "porcentaje_transferencias_min",
                "porcentaje_transferencias_max"]
        w.writerow(cab)
        for exp in resumen.values():
            for c in exp:
                fila = [c[k] for k in cols]
                for t in tiempos:
                    fila += [f"{c[t][s]:.4f}" for s in ("mediana", "desv", "min", "max")]
                fila += [c["total"]["n"], f"{c['acel_computo']:.2f}",
                         f"{c['acel_total']:.2f}", f"{c['pct_transf']:.1f}",
                         f"{c['pct_transf_min']:.1f}", f"{c['pct_transf_max']:.1f}"]
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
    ruta = con_sufijo(nombre)
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
    # Mediana del % de cada parte por repetición, reescalada para que la barra sume 100.
    partes = np.array([[c["pct_partes"][p] for p in ("h2d", "kernel", "d2h")] for _, c in pares])
    partes = 100 * partes / partes.sum(axis=1, keepdims=True)
    h2d, ker, d2h = partes[:, 0], partes[:, 1], partes[:, 2]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(x, h2d, 0.6, color=COLOR["h2d"], label="CPU→GPU")
    ax.bar(x, ker, 0.6, bottom=h2d, color=COLOR["kernel"], label="Kernel")
    ax.bar(x, d2h, 0.6, bottom=h2d + ker, color=COLOR["d2h"], label="GPU→CPU")
    for xi, (_, c) in zip(x, pares):
        ax.text(xi, 101, f"{c['pct_transf']:.0f}%", ha="center", fontsize=7)
    ax.set_ylim(0, 110)
    ax.set_xticks(x)
    ax.set_xticklabels([f"E{e}: {etiqueta(e, c)}" for e, c in pares], rotation=30,
                       ha="right", fontsize=8)
    ax.set_ylabel("% del tiempo GPU total")
    ax.set_title("Proporción del tiempo GPU (mediana por repetición; número = % en transferencias)")
    ax.legend(loc="lower right")
    guardar(fig, "grafica_gpu_desglose.png")


def grafica_repeticiones(filas):
    """Cada repetición GPU en orden de ejecución (orden del CSV). Arriba: ancho de banda
    de la copia CPU→GPU. Abajo: kernel dividido por el mínimo de su configuración.
    Sirve para ver si los tiempos cambian de nivel durante la corrida."""
    gpu = [f for f in filas if f["implementacion"] == "gpu"]
    if not gpu:
        return
    def clave(f):
        return (f["experimento"], f["filtro"], f["resolucion"], f["mascara"], f["hilos_por_bloque"])
    minimo = {}
    for f in gpu:
        minimo[clave(f)] = min(minimo.get(clave(f), f["kernel_ms"]), f["kernel_ms"])
    x = np.arange(1, len(gpu) + 1)
    lado = [int(f["resolucion"].split("x")[0]) for f in gpu]
    gbs = [l * l * 4 / 1e6 / f["h2d_ms"] for l, f in zip(lado, gpu)]
    rel = [f["kernel_ms"] / minimo[clave(f)] for f in gpu]
    colores = [plt.cm.tab10(f["experimento"] - 1) for f in gpu]

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
    a1.scatter(x, gbs, c=colores, s=18)
    a1.set_ylabel("CPU→GPU (GB/s)")
    a1.set_ylim(0, max(gbs) * 1.2)
    a1.set_title("Cada repetición GPU en orden de ejecución (color = experimento)")
    a2.scatter(x, rel, c=colores, s=18)
    a2.set_ylabel("Kernel / mínimo de su config.")
    a2.set_xlabel("Repetición GPU en orden de ejecución")
    a2.set_ylim(0, max(rel) * 1.15)
    for a in (a1, a2):
        a.grid(linestyle="--", alpha=0.5)
    # Separadores entre configuraciones
    for i in range(1, len(gpu)):
        if clave(gpu[i]) != clave(gpu[i - 1]):
            for a in (a1, a2):
                a.axvline(i + 0.5, color="gray", linewidth=0.5, alpha=0.5)
    a1.legend(handles=[plt.Line2D([], [], marker="o", linestyle="", color=plt.cm.tab10(e - 1),
                                  label=f"Exp {e}") for e in EXPERIMENTOS], ncol=4, loc="lower right")
    guardar(fig, "grafica_repeticiones.png")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    global SUFIJO
    SUFIJO = sys.argv[2] if len(sys.argv) > 2 else ""
    ruta_csv = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SALIDA, "mediciones.csv")
    if not os.path.exists(ruta_csv):
        print(f"[ERROR] No se encontró: {ruta_csv}. Ejecuta primero: ./build/convolucion medir")
        sys.exit(1)
    os.makedirs(SALIDA, exist_ok=True)

    filas = cargar_csv(ruta_csv)
    resumen = resumir(filas)
    grafica_repeticiones(filas)
    guardar_resumen(resumen)
    guardar_tabla_latex(resumen)
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
