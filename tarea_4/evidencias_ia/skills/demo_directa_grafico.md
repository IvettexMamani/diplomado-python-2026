# Demostración en Claude Code

- **Fecha:** 2026-11-06 15:02
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas que ve el modelo:** Bash, Read, Skill, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie (solo puede usar las de --allowedTools)
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --mcp-config .mcp.json --tools Skill,Read,Bash --allowedTools "Skill,Read,Bash(uv run *)"`
- **Skills activadas, en orden:** graficando-enaho (invocada con /)
- **Scripts ejecutados, en orden:** graficar.py
- **Herramientas usadas:** Bash ×1, Read ×1
- **Turnos:** 3 · **segundos:** 29.7 · **costo:** US$ 0.0599

## Pregunta

> /graficando-enaho pobreza por sexo en Puno

## Llamadas a herramientas

### 1. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && ls salidas/*.parquet && uv run \".claude/skills/graficando-enaho/scripts/graficar.py\" --por sexo --solo departamento=Puno",
 "description": "Verificar bases y graficar pobreza por sexo en Puno"
}
```

<details><summary>Resultado</summary>

```json
salidas/hogares_2024.parquet
salidas/personas_2024.parquet
Guardado: figuras/pobreza_sexo_departamento-puno.png

Título: La pobreza afecta más a las mujeres (42,9 %) que a los hombres (37,8 %), por 5,1 puntos

categoria   pct  ic95_inf  ic95_sup  cv_pct  n_muestra

    Mujer 42.92     38.40     47.43    5.37       1627

   Hombre 37.81     32.84     42.79    6.72       1485

Total del dominio: 40.42 %

Diferencia: 5.10 pp, IC 95 % de 1.88 a 8.33; distinguible del error de muestreo
```

</details>

### 2. `Read`

```json
{
 "file_path": "C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/figuras/pobreza_sexo_departamento-puno.png"
}
```

<details><summary>Resultado</summary>

```json

```

</details>

## Respuesta final

Gráfico guardado en `figuras/pobreza_sexo_departamento-puno.png`. Lo abrí y se lee bien: las barras parten de cero, la línea punteada marca el total de Puno y el título lleva el hallazgo.

**Pobreza monetaria en Puno, ENAHO 2024 (% de personas, ponderado)**

| Sexo | % | IC 95 % | n muestral |
|---|---|---|---|
| Mujer | 42,9 | 38,4 – 47,4 | 1 627 |
| Hombre | 37,8 | 32,8 – 42,8 | 1 485 |
| Total Puno | 40,4 | | |

- **Diferencia:** las mujeres superan a los hombres por 5,1 puntos porcentuales (IC 95 %: 1,9 a 8,3). El script la clasifica como distinguible del error de muestreo, así que la brecha es real en esta muestra.
- **Precisión:** los dos intervalos individuales se solapan bastante (38,4–42,8). La brecha es significativa porque el script calcula el intervalo de la diferencia, no porque los intervalos se separen.
- **Cifras referenciales (†):** ninguna lleva †. Los coeficientes de variación son 5,4 % y 6,7 %.
- **Interpretación:** esto describe una asociación entre sexo y pobreza monetaria. No indica por qué ocurre.
