#!/usr/bin/env python3
"""Procesa mediciones.csv y genera las gráficas del informe. Bloque 3 - Andrés Morocho

Uso:
    python3 scripts/graficas.py [ruta_csv]

Salida (en resultados/):
    grafica_exp1_filtros.png    — Exp 1: CPU vs GPU por tipo de filtro
    grafica_exp2_resolucion.png — Exp 2: CPU vs GPU por resolución
    grafica_exp3_mascara.png    — Exp 3: CPU vs GPU por tamaño de máscara
    grafica_exp4_hilos.png      — Exp 4: tiempos GPU internos por hilos/bloque
    grafica_speedup.png         — Aceleración GPU / CPU en todos los experimentos
    grafica_gpu_desglose.png    — Desglose h2d + kernel + d2h por experimento
"""

import csv
import sys
import os
import statistics
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")          # sin pantalla (servidor / headless)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Configuración visual ──────────────────────────────────────────────────────

COLOR_CPU    = "#4C72B0"   # azul UPS
COLOR_GPU    = "#DD8452"   # naranja GPU total
COLOR_H2D    = "#55A868"   # verde: copia Host→Device
COLOR_KERNEL = "#C44E52"   # rojo: cómputo puro
COLOR_D2H    = "#8172B2"   # morado: copia Device→Host
DIRECTORIO_SALIDA = "resultados"

plt.rcParams.update({
    "figure.dpi":      150,
    "font.size":       10,
    "axes.titlesize":  11,
    "axes.labelsize":  10,
    "legend.fontsize": 9,
})

# ── Carga y agrupación del CSV ────────────────────────────────────────────────

def cargar_csv(ruta):
    """Lee el CSV y devuelve lista de dicts con tipos correctos."""
    filas = []
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            filas.append({
                "implementacion":    fila["implementacion"],
                "filtro":            fila["filtro"],
                "resolucion":        fila["resolucion"],
                "mascara":           fila["mascara"],
                "hilos_por_bloque":  int(fila["hilos_por_bloque"]),
                "bloques":           int(fila["bloques"]),
                "repeticion":        int(fila["repeticion"]),
                "h2d_ms":            float(fila["h2d_ms"]),
                "kernel_ms":         float(fila["kernel_ms"]),
                "d2h_ms":            float(fila["d2h_ms"]),
                "total_ms":          float(fila["total_ms"]),
                "cpu_ms":            float(fila["cpu_ms"]),
            })
    print(f"Filas leídas: {len(filas)}")
    return filas


def agrupar(filas, *claves):
    """Agrupa filas por las claves dadas. Devuelve dict {tuple_clave: [filas]}."""
    grupos = defaultdict(list)
    for f in filas:
        k = tuple(f[c] for c in claves)
        grupos[k].append(f)
    return grupos


def mediana_campo(grupo, campo):
    """Mediana de un campo numérico en un grupo de filas."""
    valores = [f[campo] for f in grupo]
    return statistics.median(valores)


def stdev_campo(grupo, campo):
    """Desviación estándar de un campo (0 si hay menos de 2 muestras)."""
    valores = [f[campo] for f in grupo]
    return statistics.stdev(valores) if len(valores) >= 2 else 0.0


# ── Utilidad de guardado ──────────────────────────────────────────────────────

def guardar(fig, nombre):
    os.makedirs(DIRECTORIO_SALIDA, exist_ok=True)
    ruta = os.path.join(DIRECTORIO_SALIDA, nombre)
    fig.savefig(ruta, bbox_inches="tight")
    plt.close(fig)
    print(f"  Guardada: {ruta}")


# ── Gráfica base: barras agrupadas CPU vs GPU ─────────────────────────────────

def grafica_cpu_vs_gpu(etiquetas, tiempos_cpu, tiempos_gpu,
                       err_cpu, err_gpu,
                       titulo, xlabel, nombre_archivo):
    """
    Barras agrupadas (CPU | GPU total) con barras de error (desv. estándar).
    Los valores sobre cada barra muestran el tiempo en ms.
    """
    x    = np.arange(len(etiquetas))
    ancho = 0.35

    fig, ax = plt.subplots(figsize=(7, 4.5))
    barras_cpu = ax.bar(x - ancho/2, tiempos_cpu, ancho,
                        yerr=err_cpu, capsize=4,
                        color=COLOR_CPU, label="CPU")
    barras_gpu = ax.bar(x + ancho/2, tiempos_gpu, ancho,
                        yerr=err_gpu, capsize=4,
                        color=COLOR_GPU, label="GPU (total)")

    # Valores encima de cada barra
    for barra in list(barras_cpu) + list(barras_gpu):
        h = barra.get_height()
        ax.text(barra.get_x() + barra.get_width() / 2, h + max(tiempos_cpu + tiempos_gpu) * 0.01,
                f"{h:.1f}", ha="center", va="bottom", fontsize=8)

    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Tiempo (ms) — mediana de 5 repeticiones")
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    guardar(fig, nombre_archivo)


# ── Experimento 1: Tipo de filtro ─────────────────────────────────────────────

def graficar_exp1(filas):
    """
    Fija: imagen 4000x4000, k=3x3, 256 hilos.
    Varía: media, nitidez, laplaciano.
    """
    print("\n[Exp 1] Tipo de filtro")
    filtros_orden = ["media", "nitidez", "laplaciano"]

    cpu_med, cpu_err = [], []
    gpu_med, gpu_err = [], []

    for filtro in filtros_orden:
        grupo_cpu = [f for f in filas
                     if f["implementacion"] == "cpu"
                     and f["filtro"] == filtro
                     and f["resolucion"] == "4000x4000"
                     and f["mascara"] == "3x3"]
        grupo_gpu = [f for f in filas
                     if f["implementacion"] == "gpu"
                     and f["filtro"] == filtro
                     and f["resolucion"] == "4000x4000"
                     and f["mascara"] == "3x3"
                     and f["hilos_por_bloque"] == 256]

        if not grupo_cpu or not grupo_gpu:
            print(f"  [AVISO] Sin datos para filtro='{filtro}'")
            continue

        cpu_med.append(mediana_campo(grupo_cpu, "cpu_ms"))
        cpu_err.append(stdev_campo(grupo_cpu, "cpu_ms"))
        gpu_med.append(mediana_campo(grupo_gpu, "total_ms"))
        gpu_err.append(stdev_campo(grupo_gpu, "total_ms"))

    if not cpu_med:
        print("  Sin datos suficientes, omitiendo.")
        return

    grafica_cpu_vs_gpu(
        filtros_orden, cpu_med, gpu_med, cpu_err, gpu_err,
        "Exp 1: Tiempo por tipo de filtro\n(imagen 4000×4000, máscara 3×3, 256 hilos)",
        "Tipo de filtro",
        "grafica_exp1_filtros.png"
    )


# ── Experimento 2: Resolución ─────────────────────────────────────────────────

def graficar_exp2(filas):
    """
    Fija: media, k=9x9, 256 hilos.
    Varía: 2000x2000, 4000x4000, 6000x6000.
    """
    print("\n[Exp 2] Resolución")
    resoluciones = ["2000x2000", "4000x4000", "6000x6000"]

    cpu_med, cpu_err = [], []
    gpu_med, gpu_err = [], []

    for res in resoluciones:
        grupo_cpu = [f for f in filas
                     if f["implementacion"] == "cpu"
                     and f["filtro"] == "media"
                     and f["resolucion"] == res
                     and f["mascara"] == "9x9"]
        grupo_gpu = [f for f in filas
                     if f["implementacion"] == "gpu"
                     and f["filtro"] == "media"
                     and f["resolucion"] == res
                     and f["mascara"] == "9x9"
                     and f["hilos_por_bloque"] == 256]

        if not grupo_cpu or not grupo_gpu:
            print(f"  [AVISO] Sin datos para resolución='{res}'")
            continue

        cpu_med.append(mediana_campo(grupo_cpu, "cpu_ms"))
        cpu_err.append(stdev_campo(grupo_cpu, "cpu_ms"))
        gpu_med.append(mediana_campo(grupo_gpu, "total_ms"))
        gpu_err.append(stdev_campo(grupo_gpu, "total_ms"))

    if not cpu_med:
        print("  Sin datos suficientes, omitiendo.")
        return

    grafica_cpu_vs_gpu(
        resoluciones, cpu_med, gpu_med, cpu_err, gpu_err,
        "Exp 2: Tiempo por resolución de imagen\n(filtro media, máscara 9×9, 256 hilos)",
        "Resolución (píxeles)",
        "grafica_exp2_resolucion.png"
    )


# ── Experimento 3: Tamaño de máscara ─────────────────────────────────────────

def graficar_exp3(filas):
    """
    Fija: imagen 4000x4000, media, 256 hilos.
    Varía: k=3x3, 9x9, 21x21.
    """
    print("\n[Exp 3] Tamaño de máscara")
    mascaras = ["3x3", "9x9", "21x21"]

    cpu_med, cpu_err = [], []
    gpu_med, gpu_err = [], []

    for mask in mascaras:
        grupo_cpu = [f for f in filas
                     if f["implementacion"] == "cpu"
                     and f["filtro"] == "media"
                     and f["resolucion"] == "4000x4000"
                     and f["mascara"] == mask]
        grupo_gpu = [f for f in filas
                     if f["implementacion"] == "gpu"
                     and f["filtro"] == "media"
                     and f["resolucion"] == "4000x4000"
                     and f["mascara"] == mask
                     and f["hilos_por_bloque"] == 256]

        if not grupo_cpu or not grupo_gpu:
            print(f"  [AVISO] Sin datos para máscara='{mask}'")
            continue

        cpu_med.append(mediana_campo(grupo_cpu, "cpu_ms"))
        cpu_err.append(stdev_campo(grupo_cpu, "cpu_ms"))
        gpu_med.append(mediana_campo(grupo_gpu, "total_ms"))
        gpu_err.append(stdev_campo(grupo_gpu, "total_ms"))

    if not cpu_med:
        print("  Sin datos suficientes, omitiendo.")
        return

    grafica_cpu_vs_gpu(
        mascaras, cpu_med, gpu_med, cpu_err, gpu_err,
        "Exp 3: Tiempo por tamaño de máscara\n(imagen 4000×4000, filtro media, 256 hilos)",
        "Tamaño de máscara (k×k)",
        "grafica_exp3_mascara.png"
    )


# ── Experimento 4: Hilos por bloque ──────────────────────────────────────────

def graficar_exp4(filas):
    """
    Fija: imagen 4000x4000, media, k=9x9.
    Varía: 128, 256, 512 hilos/bloque.
    Muestra desglose h2d + kernel + d2h como barras apiladas.
    """
    print("\n[Exp 4] Hilos por bloque")
    configs = [128, 256, 512]
    etiquetas = [f"{h} hilos" for h in configs]

    h2d_med, ker_med, d2h_med = [], [], []
    h2d_err, ker_err, d2h_err = [], [], []
    cpu_med_vals = []

    for hilos in configs:
        grupo_gpu = [f for f in filas
                     if f["implementacion"] == "gpu"
                     and f["filtro"] == "media"
                     and f["resolucion"] == "4000x4000"
                     and f["mascara"] == "9x9"
                     and f["hilos_por_bloque"] == hilos]
        grupo_cpu = [f for f in filas
                     if f["implementacion"] == "cpu"
                     and f["filtro"] == "media"
                     and f["resolucion"] == "4000x4000"
                     and f["mascara"] == "9x9"]

        if not grupo_gpu:
            print(f"  [AVISO] Sin datos GPU para {hilos} hilos")
            continue

        h2d_med.append(mediana_campo(grupo_gpu, "h2d_ms"))
        ker_med.append(mediana_campo(grupo_gpu, "kernel_ms"))
        d2h_med.append(mediana_campo(grupo_gpu, "d2h_ms"))
        h2d_err.append(stdev_campo(grupo_gpu, "h2d_ms"))
        ker_err.append(stdev_campo(grupo_gpu, "kernel_ms"))
        d2h_err.append(stdev_campo(grupo_gpu, "d2h_ms"))
        cpu_med_vals.append(mediana_campo(grupo_cpu, "cpu_ms") if grupo_cpu else None)

    if not h2d_med:
        print("  Sin datos suficientes, omitiendo.")
        return

    x     = np.arange(len(etiquetas[:len(h2d_med)]))
    ancho = 0.5

    fig, ax = plt.subplots(figsize=(7, 4.5))

    # Barras apiladas GPU
    b_h2d = ax.bar(x, h2d_med, ancho, color=COLOR_H2D,    label="H→D (copia a GPU)")
    b_ker = ax.bar(x, ker_med, ancho, bottom=h2d_med,      color=COLOR_KERNEL, label="Kernel (cómputo)")
    b_d2h = ax.bar(x, d2h_med, ancho,
                   bottom=[a + b for a, b in zip(h2d_med, ker_med)],
                   color=COLOR_D2H, label="D→H (copia a CPU)")

    # Línea horizontal del tiempo CPU (referencia)
    cpu_ref = [v for v in cpu_med_vals if v is not None]
    if cpu_ref:
        cpu_val = cpu_ref[0]
        ax.axhline(cpu_val, color=COLOR_CPU, linestyle="--", linewidth=1.5,
                   label=f"CPU ref. ({cpu_val:.1f} ms)")

    ax.set_title("Exp 4: Desglose GPU por hilos/bloque\n"
                 "(imagen 4000×4000, filtro media, máscara 9×9)")
    ax.set_xlabel("Configuración de hilos por bloque")
    ax.set_ylabel("Tiempo (ms) — mediana de 5 repeticiones")
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas[:len(h2d_med)])
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    guardar(fig, "grafica_exp4_hilos.png")


# ── Gráfica de Speedup ────────────────────────────────────────────────────────

def graficar_speedup(filas):
    """
    Calcula Speedup = cpu_ms / total_ms para cada configuración.
    Muestra speedup en función del experimento y variable.
    """
    print("\n[Speedup] Aceleración GPU sobre CPU")

    # Configuraciones de referencia de cada experimento
    experimentos = [
        # (etiqueta larga,       etiqueta corta,  filtro,       res,         mask,  hilos)
        ("E1: media 3×3",        "media 3×3",     "media",      "4000x4000", "3x3",   256),
        ("E1: nitidez 3×3",      "nitidez 3×3",   "nitidez",    "4000x4000", "3x3",   256),
        ("E1: laplaciano 3×3",   "laplaciano 3×3","laplaciano", "4000x4000", "3x3",   256),
        ("E2: media 9×9 2000",   "2000×2000",     "media",      "2000x2000", "9x9",   256),
        ("E2: media 9×9 4000",   "4000×4000",     "media",      "4000x4000", "9x9",   256),
        ("E2: media 9×9 6000",   "6000×6000",     "media",      "6000x6000", "9x9",   256),
        ("E3: media 3×3",        "k=3×3",         "media",      "4000x4000", "3x3",   256),
        ("E3: media 9×9",        "k=9×9",         "media",      "4000x4000", "9x9",   256),
        ("E3: media 21×21",      "k=21×21",       "media",      "4000x4000", "21x21", 256),
        ("E4: 128 hilos",        "128 hilos",     "media",      "4000x4000", "9x9",   128),
        ("E4: 256 hilos",        "256 hilos",     "media",      "4000x4000", "9x9",   256),
        ("E4: 512 hilos",        "512 hilos",     "media",      "4000x4000", "9x9",   512),
    ]

    etiquetas, speedups, colores_exp = [], [], []
    palette = {
        "E1": "#4C72B0", "E2": "#DD8452", "E3": "#55A868", "E4": "#C44E52"
    }

    for (label_largo, label_corto, filtro, res, mask, hilos) in experimentos:
        g_cpu = [f for f in filas
                 if f["implementacion"] == "cpu"
                 and f["filtro"] == filtro
                 and f["resolucion"] == res
                 and f["mascara"] == mask]
        g_gpu = [f for f in filas
                 if f["implementacion"] == "gpu"
                 and f["filtro"] == filtro
                 and f["resolucion"] == res
                 and f["mascara"] == mask
                 and f["hilos_por_bloque"] == hilos]

        if not g_cpu or not g_gpu:
            continue

        cpu_t = mediana_campo(g_cpu, "cpu_ms")
        gpu_t = mediana_campo(g_gpu, "total_ms")
        if gpu_t == 0:
            continue

        speedup = cpu_t / gpu_t
        etiquetas.append(label_corto)
        speedups.append(speedup)
        prefijo = label_largo[:2]
        colores_exp.append(palette.get(prefijo, "#888888"))

    if not speedups:
        print("  Sin datos suficientes, omitiendo.")
        return

    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = np.arange(len(etiquetas))
    barras = ax.bar(x, speedups, color=colores_exp, edgecolor="white", linewidth=0.5)

    # Línea speedup = 1 (sin ganancia)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.2, label="Speedup = 1 (igual)")

    # Valor encima de cada barra
    for barra, sp in zip(barras, speedups):
        ax.text(barra.get_x() + barra.get_width() / 2,
                barra.get_height() + max(speedups) * 0.01,
                f"{sp:.1f}×", ha="center", va="bottom", fontsize=8)

    # Leyenda de colores por experimento
    leyenda = [mpatches.Patch(color=c, label=f"Exp {n}")
               for n, c in [("1", palette["E1"]), ("2", palette["E2"]),
                             ("3", palette["E3"]), ("4", palette["E4"])]]
    ax.legend(handles=leyenda + [plt.Line2D([0], [0], color="black",
                                            linestyle="--", label="Speedup = 1")])

    ax.set_title("Aceleración GPU sobre CPU (Speedup = T_CPU / T_GPU_total)")
    ax.set_xlabel("Configuración")
    ax.set_ylabel("Speedup")
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, rotation=30, ha="right", fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    guardar(fig, "grafica_speedup.png")


# ── Gráfica de desglose GPU global ───────────────────────────────────────────

def graficar_desglose_gpu(filas):
    """
    Muestra qué porcentaje del tiempo GPU total es:
    h2d (transferencia), kernel (cómputo), d2h (transferencia de vuelta).
    Barras apiladas al 100% para comparar overhead de transferencias.
    """
    print("\n[Desglose GPU] Porcentaje h2d / kernel / d2h")

    # Mismas configuraciones clave del speedup
    configs = [
        ("media 3×3",  "media",      "4000x4000", "3x3",   256),
        ("nitidez",    "nitidez",    "4000x4000", "3x3",   256),
        ("laplaciano", "laplaciano", "4000x4000", "3x3",   256),
        ("media 9×9\n2000", "media", "2000x2000", "9x9",   256),
        ("media 9×9\n4000", "media", "4000x4000", "9x9",   256),
        ("media 9×9\n6000", "media", "6000x6000", "9x9",   256),
        ("k=21×21",    "media",      "4000x4000", "21x21", 256),
    ]

    etiquetas, pct_h2d, pct_ker, pct_d2h = [], [], [], []

    for (label, filtro, res, mask, hilos) in configs:
        g = [f for f in filas
             if f["implementacion"] == "gpu"
             and f["filtro"] == filtro
             and f["resolucion"] == res
             and f["mascara"] == mask
             and f["hilos_por_bloque"] == hilos]
        if not g:
            continue

        h2d = mediana_campo(g, "h2d_ms")
        ker = mediana_campo(g, "kernel_ms")
        d2h = mediana_campo(g, "d2h_ms")
        total = h2d + ker + d2h
        if total == 0:
            continue

        etiquetas.append(label)
        pct_h2d.append(100 * h2d / total)
        pct_ker.append(100 * ker  / total)
        pct_d2h.append(100 * d2h / total)

    if not etiquetas:
        print("  Sin datos GPU suficientes, omitiendo.")
        return

    x     = np.arange(len(etiquetas))
    ancho = 0.6

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(x, pct_h2d, ancho, color=COLOR_H2D,    label="H→D")
    ax.bar(x, pct_ker, ancho, bottom=pct_h2d,      color=COLOR_KERNEL, label="Kernel")
    ax.bar(x, pct_d2h, ancho,
           bottom=[a + b for a, b in zip(pct_h2d, pct_ker)],
           color=COLOR_D2H, label="D→H")

    ax.set_title("Desglose del tiempo GPU: transferencias vs cómputo (%)")
    ax.set_xlabel("Configuración")
    ax.set_ylabel("% del tiempo GPU total")
    ax.set_ylim(0, 110)
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, fontsize=8)
    ax.legend(loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    guardar(fig, "grafica_gpu_desglose.png")


# ── Resumen en consola ────────────────────────────────────────────────────────

def imprimir_resumen(filas):
    """Imprime tabla de medianas por configuración principal."""
    print("\n{'='*65}")
    print(f"{'Configuración':<30} {'CPU (ms)':>10} {'GPU total (ms)':>14} {'Speedup':>8}")
    print("-" * 65)

    configs = [
        ("E1 media 3×3 4000",     "media",      "4000x4000", "3x3",   256),
        ("E1 nitidez 3×3 4000",   "nitidez",    "4000x4000", "3x3",   256),
        ("E1 laplaciano 3×3 4000","laplaciano", "4000x4000", "3x3",   256),
        ("E2 media 9×9 2000",     "media",      "2000x2000", "9x9",   256),
        ("E2 media 9×9 4000",     "media",      "4000x4000", "9x9",   256),
        ("E2 media 9×9 6000",     "media",      "6000x6000", "9x9",   256),
        ("E3 media 3×3 4000",     "media",      "4000x4000", "3x3",   256),
        ("E3 media 9×9 4000",     "media",      "4000x4000", "9x9",   256),
        ("E3 media 21×21 4000",   "media",      "4000x4000", "21x21", 256),
        ("E4 media 9×9 128h",     "media",      "4000x4000", "9x9",   128),
        ("E4 media 9×9 256h",     "media",      "4000x4000", "9x9",   256),
        ("E4 media 9×9 512h",     "media",      "4000x4000", "9x9",   512),
    ]

    for (label, filtro, res, mask, hilos) in configs:
        g_cpu = [f for f in filas
                 if f["implementacion"] == "cpu"
                 and f["filtro"] == filtro
                 and f["resolucion"] == res
                 and f["mascara"] == mask]
        g_gpu = [f for f in filas
                 if f["implementacion"] == "gpu"
                 and f["filtro"] == filtro
                 and f["resolucion"] == res
                 and f["mascara"] == mask
                 and f["hilos_por_bloque"] == hilos]

        if not g_cpu or not g_gpu:
            continue

        cpu_t = mediana_campo(g_cpu, "cpu_ms")
        gpu_t = mediana_campo(g_gpu, "total_ms")
        sp    = cpu_t / gpu_t if gpu_t > 0 else float("inf")
        print(f"{label:<30} {cpu_t:>10.1f} {gpu_t:>14.1f} {sp:>7.1f}×")

    print("=" * 65)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ruta_csv = sys.argv[1] if len(sys.argv) > 1 else "resultados/mediciones.csv"

    if not os.path.exists(ruta_csv):
        print(f"[ERROR] No se encontró: {ruta_csv}")
        print("        Ejecuta primero: ./build/convolucion medir")
        sys.exit(1)

    filas = cargar_csv(ruta_csv)

    graficar_exp1(filas)
    graficar_exp2(filas)
    graficar_exp3(filas)
    graficar_exp4(filas)
    graficar_speedup(filas)
    graficar_desglose_gpu(filas)
    imprimir_resumen(filas)

    print(f"\nTodas las gráficas guardadas en '{DIRECTORIO_SALIDA}/'")


if __name__ == "__main__":
    main()
