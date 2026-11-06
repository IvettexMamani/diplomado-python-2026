# Demostración en Claude Code

- **Fecha:** 2026-11-06 15:07
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas que ve el modelo:** Bash, Read, Skill, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie (solo puede usar las de --allowedTools)
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --mcp-config .mcp.json --tools Skill,Read,Bash --allowedTools "Skill,Read,Bash(uv run *)"`
- **Skills activadas, en orden:** limpiando-enaho
- **Scripts ejecutados, en orden:** estimar.py → estimar.py
- **Herramientas usadas:** Skill ×1, Bash ×2
- **Turnos:** 5 · **segundos:** 35.1 · **costo:** US$ 0.029

## Pregunta

> ¿Cuál fue la pobreza en Cusco en 2024?

## Llamadas a herramientas

### 1. `Skill`

```json
{
 "skill": "limpiando-enaho",
 "args": "pobreza monetaria en Cusco 2024"
}
```

<details><summary>Resultado</summary>

```json
Launching skill: limpiando-enaho
```

</details>

### 2. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && ls salidas && cat salidas/validacion.txt | tail -15"
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
[OK   ] La variable pobreza se reproduce con gasto mensual por persona < línea en 100.00% de los hogares
[OK   ] Pobreza nacional (sumaria, factor07 × mieperho): 27.58 % (referencia 27.6 %, tolerancia ±0.1 pp)
[OK   ] Pobreza nacional (residentes, facpob07): 27.53 % (referencia 27.6 %, tolerancia ±0.1 pp)
[OK   ] Pobreza urbana: 24.81 % (referencia 24.8 %)
[OK   ] Pobreza rural: 39.30 % (referencia 39.3 %)
[OK   ] Pobreza extrema: 5.50 % (referencia 5.5 %)
[OK   ] Lima Metropolitana: 28.21 % (referencia 28.2 %)

Por qué importa ponderar (solo para comparar)
        Promedio simple de hogares: 20.22 %. De personas: 25.61 %. Hogares con factor07, sin mieperho: 21.85 %.
[OK   ] Las cifras ponderadas difieren de los promedios simples
        27.58 frente a 27.53: mieperho cuenta a los 109,842 miembros del hogar (p204 = 1) y los residentes habituales son 108,664: son dos poblaciones distintas.

Aprobadas: 25. Fallidas: 0. Avisos: 0.
RESULTADO: APROBADA
```

</details>

### 3. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && uv run \".claude/skills/limpiando-enaho/scripts/estimar.py\" --solo departamento=Cusco; uv run \".claude/skills/limpiando-enaho/scripts/estimar.py\" --solo departamento=Cusco --indicador pobre_extremo"
}
```

<details><summary>Resultado</summary>

```json
Pobreza monetaria, % de personas, ENAHO 2024. Base: sumaria, hogares ponderados con factor07 × mieperho.
Dominio: departamento=Cusco
codigo categoria   pct   ee  ic95_inf  ic95_sup  cv_pct  n_muestra  upm  poblacion
            Perú 18.54 1.95     14.72     22.36   10.52       1230  189 1409467.16
Pobreza monetaria extrema, % de personas, ENAHO 2024. Base: sumaria, hogares ponderados con factor07 × mieperho.
Dominio: departamento=Cusco
codigo categoria  pct  ee  ic95_inf  ic95_sup  cv_pct  n_muestra  upm  poblacion
            Perú  2.1 0.6      0.93      3.28   28.52       1230  189 1409467.16
Coeficiente de variación mayor a 15 %, cifra solo referencial: Perú
```

</details>

## Respuesta final

En 2024, la pobreza monetaria en Cusco fue de **18,5 %** de la población. El intervalo de confianza al 95 % va de 14,7 % a 22,4 %.

- **Fuente y método:** INEI, ENAHO 2024. Usé la base de hogares, ponderada con `factor07 × mieperho`, que es el método del INEI. La validación de la base salió aprobada: 25 comprobaciones pasaron y ninguna falló.
- **Muestra:** 1 230 hogares en 189 conglomerados, que representan a unos 1,41 millones de personas.
- **Pobreza extrema:** fue de 2,1 % (IC 95 %: 0,9 % a 3,3 %). Su coeficiente de variación es 28,5 %, así que esta cifra es solo referencial. La de pobreza total tiene un coeficiente de 10,5 %, por debajo del umbral de 15 %.
- **Comparaciones:** si quieres comparar Cusco con otros departamentos, no basta con ver si los intervalos se cruzan. Para eso hay que calcular el intervalo de la diferencia, y la skill `graficando-enaho` lo hace.

En la tabla de resultados la etiqueta del territorio sale como «Perú», aunque el filtro fue `departamento=Cusco`. Las cifras corresponden a Cusco, pero conviene tenerlo presente si las copias a un informe.
