#!/bin/sh
# Guarda información del equipo. Bloque 1 - Michael Lata
salida="resultados/equipo.txt"
mkdir -p resultados
{
    echo "CPU"
    lscpu | grep -E 'Model name|^CPU\(s\):|Thread|Core'
    echo "RAM"
    free -h
    echo "GPU"
    if command -v nvidia-smi >/dev/null 2>&1; then
        nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    else
        echo "nvidia-smi no disponible"
    fi
    echo "Versiones"
    gcc --version | head -1
    nvcc --version 2>/dev/null | tail -1 || echo "nvcc no disponible"
    python3 --version
    uname -a
} | tee "$salida"
