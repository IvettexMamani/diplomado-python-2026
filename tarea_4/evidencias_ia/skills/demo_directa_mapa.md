# Demostración en Claude Code

- **Fecha:** 2026-11-06 15:10
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas que ve el modelo:** Bash, Read, Skill, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie (solo puede usar las de --allowedTools)
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --mcp-config .mcp.json --tools Skill,Read,Bash --allowedTools "Skill,Read,Bash(uv run *)"`
- **Skills activadas, en orden:** mapeando-enaho (invocada con /)
- **Scripts ejecutados, en orden:** mapear.py → mapear.py → mapear.py
- **Herramientas usadas:** Bash ×5, Read ×1
- **Turnos:** 8 · **segundos:** 43.1 · **costo:** US$ 0.0891

## Pregunta

> /mapeando-enaho pobreza extrema

## Llamadas a herramientas

### 1. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && ls salidas/ && uv run \".claude/skills/mapeando-enaho/scripts/mapear.py\" --indicador pobre_extremo; echo EXIT $?; cat salidas/validacion_mapa_extrema.txt"
}
```

<details><summary>Resultado</summary>

```json
A variable in this command can't be checked before it runs
```

</details>

### 2. `Bash`

```json
{
 "command": "ls salidas/"
}
```

<details><summary>Resultado</summary>

```json
comparacion_mapa.csv
hogares_2024.parquet
indicadores.csv
personas_2024.parquet
validacion.txt
validacion_mapa.txt
validacion_mapa_extrema.txt
```

</details>

### 3. `Bash`

```json
{
 "command": "uv run \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/.claude/skills/mapeando-enaho/scripts/mapear.py\" --indicador pobre_extremo; echo EXIT $?"
}
```

<details><summary>Resultado</summary>

```json
A variable in this command can't be checked before it runs
```

</details>

### 4. `Bash`

```json
{
 "command": "cat salidas/validacion_mapa_extrema.txt"
}
```

<details><summary>Resultado</summary>

```json
Validación del mapa, ENAHO 2024: Pobreza monetaria extrema

[OK   ] Unión por código FIRST_IDDP = ubigeo[:2]: 25 de 25 unidades con geometría y dato
[AVISO] Sin comparación: la referencia de la Sesión 16 solo cubre la pobreza monetaria total

RESULTADO: APROBADO
```

</details>

### 5. `Bash`

```json
{
 "command": "uv run \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/.claude/skills/mapeando-enaho/scripts/mapear.py\" --indicador pobre_extremo"
}
```

<details><summary>Resultado</summary>

```json
Validación del mapa, ENAHO 2024: Pobreza monetaria extrema

[OK   ] Unión por código FIRST_IDDP = ubigeo[:2]: 25 de 25 unidades con geometría y dato
[AVISO] Sin comparación: la referencia de la Sesión 16 solo cubre la pobreza monetaria total

RESULTADO: APROBADO

Guardado: mapas/pobreza_extrema_departamento.png
codigo     categoria   pct  ic95_inf  ic95_sup  cv_pct
    06     Cajamarca 19.72     16.31     23.12    8.81
    16        Loreto 14.98     11.72     18.25   11.13
    21          Puno 12.49      9.67     15.31   11.52
    10       Huánuco 12.20      8.80     15.60   14.20
    09  Huancavelica 11.16      8.15     14.17   13.77
    05      Ayacucho  9.09      6.43     11.75   14.93
    19         Pasco  8.33      5.17     11.50   19.39
    13   La Libertad  6.56      4.85      8.27   13.30
    01      Amazonas  6.01      3.50      8.52   21.30
    02        Áncash  5.80      4.15      7.45   14.50
    03      Apurímac  5.24      2.80      7.67   23.70
    07        Callao  5.04      2.88      7.19   21.82
    20         Piura  4.41      2.84      5.97   18.10
    22    San Martín  4.39      2.65      6.13   20.18
    12         Junín  3.82      2.27      5.37   20.71
    25       Ucayali  3.26      1.65      4.88   25.18
    15          Lima  3.12      2.15      4.08   15.76
    23         Tacna  2.65      1.37      3.93   24.58
    18      Moquegua  2.38      1.25      3.52   24.29
    08         Cusco  2.10      0.93      3.28   28.52
   
... (1775 caracteres en total)
```

</details>

### 6. `Read`

```json
{
 "file_path": "C:\\Users\\USUARIO\\Documents\\CIENCIA DE DATOS\\CLASES PYTHON\\PHYTON INTERMEDIO\\diplomado-python-2026\\tarea_4\\mapas\\pobreza_extrema_departamento.png"
}
```

<details><summary>Resultado</summary>

```json

```

</details>

## Respuesta final

**Mapa:** `mapas/pobreza_extrema_departamento.png`

**Validación:** `RESULTADO: APROBADO`. La unión por código (`FIRST_IDDP` con `ubigeo[:2]`) dio 25 de 25 unidades con geometría y dato. No hay comparación con la Sesión 16, porque esa referencia solo cubre la pobreza total. Por eso `comparacion_mapa.csv` no corresponde a este indicador. Revisé la imagen: están los 25 departamentos, sin zonas en blanco, y Lima y Callao aparecen separados en el recuadro.

**Más pobreza extrema (% de personas):**
- Cajamarca, 19,7 % (IC 95 %: 16,3–23,1)
- Loreto, 15,0 % (11,7–18,3)
- Puno, 12,5 % (9,7–15,3)
- Huánuco, 12,2 % (8,8–15,6)
- Huancavelica, 11,2 % (8,2–14,2)

**Menos pobreza extrema:**
- Ica, 0,1 %
- Lambayeque, 0,5 %
- Tumbes, 1,1 %
- Madre de Dios, 1,5 %
- Arequipa, 1,6 %

**Advertencias:**
- Las cifras son muestrales. Los intervalos de Cajamarca y Loreto se cruzan entre 16,3 y 18,3. Lo mismo pasa entre Loreto, Puno, Huánuco y Huancavelica, así que el orden entre ellos no es seguro. Cajamarca sí queda por encima de Puno, Huánuco y Huancavelica.
- Llevan † (coeficiente de variación mayor a 15 %, solo referenciales) 16 departamentos, entre ellos Pasco, Amazonas, Lima y Callao. Las cifras de Ica (CV 99,99 %), Tumbes (49 %) y Madre de Dios (48 %) son especialmente inestables. Ordenar los departamentos de la parte baja no es confiable.

**Patrón territorial:** la pobreza extrema se concentra en la sierra norte (Cajamarca), el sur andino (Puno, Huancavelica, Ayacucho) y Loreto, en la Amazonía. Los departamentos de la costa y los de Cusco, Arequipa y Madre de Dios quedan en el tramo más bajo, de 0 a 5 %. Esto describe dónde se ubica el fenómeno y no explica sus causas.
