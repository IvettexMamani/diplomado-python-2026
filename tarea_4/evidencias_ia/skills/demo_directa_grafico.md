# Demostración en Claude Code

- **Fecha:** 2026-11-06 15:09
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas que ve el modelo:** Bash, Read, Skill, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie (solo puede usar las de --allowedTools)
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --mcp-config .mcp.json --tools Skill,Read,Bash --allowedTools "Skill,Read,Bash(uv run *)"`
- **Skills activadas, en orden:** graficando-enaho (invocada con /)
- **Scripts ejecutados, en orden:** graficar.py
- **Herramientas usadas:** Bash ×2, Read ×1
- **Turnos:** 4 · **segundos:** 34.4 · **costo:** US$ 0.0638

## Pregunta

> /graficando-enaho pobreza por sexo en Puno

## Llamadas a herramientas

### 1. `Bash`

```json
{
 "command": "ls salidas/personas_2024.parquet salidas/hogares_2024.parquet",
 "description": "Check base files exist"
}
```

<details><summary>Resultado</summary>

```json
salidas/hogares_2024.parquet
salidas/personas_2024.parquet
```

</details>

### 2. `Bash`

```json
{
 "command": "uv run \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/.claude/skills/graficando-enaho/scripts/graficar.py\" --por sexo --solo departamento=Puno",
 "description": "Generate poverty by sex chart for Puno"
}
```

<details><summary>Resultado</summary>

```json
Guardado: figuras/pobreza_sexo_departamento-puno.png
Título: La pobreza afecta más a las mujeres (42,9 %) que a los hombres (37,8 %), por 5,1 puntos
categoria   pct  ic95_inf  ic95_sup  cv_pct  n_muestra
    Mujer 42.92     38.40     47.43    5.37       1627
   Hombre 37.81     32.84     42.79    6.72       1485
Total del dominio: 40.42 %
Diferencia: 5.10 pp, IC 95 % de 1.88 a 8.33; distinguible del error de muestreo
```

</details>

### 3. `Read`

```json
{
 "file_path": "C:\\Users\\USUARIO\\Documents\\CIENCIA DE DATOS\\CLASES PYTHON\\PHYTON INTERMEDIO\\diplomado-python-2026\\tarea_4\\figuras\\pobreza_sexo_departamento-puno.png"
}
```

<details><summary>Resultado</summary>

```json

```

</details>

## Respuesta final

Generé el gráfico de pobreza monetaria por sexo en Puno, ENAHO 2024: `figuras/pobreza_sexo_departamento-puno.png`. Lo abrí y se lee bien: barras desde cero, una sola base y el total de Puno como línea punteada.

| Sexo | Pobreza (%) | IC 95 % | CV (%) | Muestra |
|---|---|---|---|---|
| Mujer | 42,9 | 38,4 – 47,4 | 5,4 | 1 627 |
| Hombre | 37,8 | 32,8 – 42,8 | 6,7 | 1 485 |

El total de Puno es 40,4 %.

- **Diferencia:** las mujeres superan a los hombres por 5,1 puntos porcentuales (IC 95 % de 1,9 a 8,3). El script indica que es distinguible del error de muestreo.
- **Intervalos que se traslapan:** los intervalos de cada sexo se traslapan entre sí. Aun así, el intervalo de la diferencia no incluye el cero, y ese es el que decide.
- **Referencial (†):** ninguna cifra lleva †, así que todas son confiables como estimaciones.
- **Alcance:** esto describe una asociación entre sexo y pobreza monetaria en Puno. No dice qué la causa.
