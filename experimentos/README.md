# Experimentos

El benchmark del Bloque 3 medirá, con calentamiento y al menos cinco repeticiones:

1. Filtro media, nitidez y laplaciano 3x3 a 4000x4000.
2. Resoluciones 2000x2000, 4000x4000 y 6000x6000 con media 9x9.
3. Máscaras media 3x3, 9x9 y 21x21 a 4000x4000.
4. 128, 256 y 512 hilos por bloque con media 9x9 a 4000x4000.

`resultados/mediciones.csv` usa el encabezado:

```text
implementacion,filtro,resolucion,mascara,hilos_por_bloque,bloques,repeticion,h2d_ms,kernel_ms,d2h_ms,total_ms,cpu_ms,unidad
```

Los tiempos están en milisegundos y cada fila representa una repetición.
