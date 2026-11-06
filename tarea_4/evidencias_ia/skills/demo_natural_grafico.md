# Demostración en Claude Code

- **Fecha:** 2026-11-06 15:08
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas que ve el modelo:** Bash, Read, Skill, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie (solo puede usar las de --allowedTools)
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --mcp-config .mcp.json --tools Skill,Read,Bash --allowedTools "Skill,Read,Bash(uv run *)"`
- **Skills activadas, en orden:** graficando-enaho
- **Scripts ejecutados, en orden:** graficar.py
- **Herramientas usadas:** Skill ×1, Bash ×1, Read ×1
- **Turnos:** 5 · **segundos:** 34.3 · **costo:** US$ 0.0286

## Pregunta

> Grafica la pobreza urbana y rural.

## Llamadas a herramientas

### 1. `Skill`

```json
{
 "skill": "graficando-enaho",
 "args": "pobreza urbana y rural"
}
```

<details><summary>Resultado</summary>

```json
Launching skill: graficando-enaho
```

</details>

### 2. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && ls salidas/*.parquet && uv run \".claude/skills/graficando-enaho/scripts/graficar.py\" --por area"
}
```

<details><summary>Resultado</summary>

```json
salidas/hogares_2024.parquet
salidas/personas_2024.parquet
Guardado: figuras/pobreza_area.png
Título: La pobreza rural (39,3 %) supera a la urbana (24,8 %) en 14,5 puntos porcentuales
categoria   pct  ic95_inf  ic95_sup  cv_pct  n_muestra
    Rural 39.30     37.80     40.81    1.96      11660
   Urbana 24.81     23.62     25.99    2.43      22031
Total del dominio: 27.58 %
Diferencia: 14.50 pp, IC 95 % de 12.58 a 16.41; distinguible del error de muestreo
```

</details>

### 3. `Read`

```json
{
 "file_path": "C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/figuras/pobreza_area.png"
}
```

<details><summary>Resultado</summary>

```json

```

</details>

## Respuesta final

Gráfico guardado en `figuras/pobreza_area.png`.

**Pobreza monetaria por área, Perú 2024 (ENAHO, % de personas)**

| Área | % | IC 95 % | n muestra |
|---|---|---|---|
| Rural | 39,3 | 37,8 – 40,8 | 11 660 |
| Urbana | 24,8 | 23,6 – 26,0 | 22 031 |
| Total nacional | 27,6 | | |

- La diferencia es de 14,5 puntos porcentuales (IC 95 %: 12,6 a 16,4). Es distinguible del error de muestreo: los intervalos de ambas áreas no se solapan.
- Ninguna cifra lleva † (los coeficientes de variación son de 2,0 % y 2,4 %), así que ambas son confiables.
- Esto describe una asociación entre el área de residencia y la pobreza, no una causa.
- Como el pedido no decía qué indicador usar, grafiqué la pobreza monetaria total. Si quieres la pobreza extrema, puedo agregar `--indicador pobre_extremo`.
- La imagen se ve bien: las barras parten de cero, están ordenadas de mayor a menor y tienen la línea del total nacional.
