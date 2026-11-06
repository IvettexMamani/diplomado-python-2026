# Demostración en Claude Code

- **Fecha:** 2026-11-06 15:08
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas que ve el modelo:** Bash, Read, Skill, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie (solo puede usar las de --allowedTools)
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --mcp-config .mcp.json --tools Skill,Read,Bash --allowedTools "Skill,Read,Bash(uv run *)"`
- **Skills activadas, en orden:** limpiando-enaho (invocada con /)
- **Scripts ejecutados, en orden:** limpiar.py → estimar.py
- **Herramientas usadas:** Bash ×3
- **Turnos:** 4 · **segundos:** 40.1 · **costo:** US$ 0.0756

## Pregunta

> /limpiando-enaho 2024

## Llamadas a herramientas

### 1. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && ls -la salidas/ && cat salidas/validacion.txt 2>/dev/null"
}
```

<details><summary>Resultado</summary>

```json
Exit code 1
total 26
drwxr-xr-x 1 USUARIO 197121    0 nov.  6 15:08 .
drwxr-xr-x 1 USUARIO 197121    0 nov.  6 15:08 ..
-rw-r--r-- 1 USUARIO 197121 1333 nov.  6 15:06 comparacion_mapa.csv
-rw-r--r-- 1 USUARIO 197121 9395 nov.  6 15:06 indicadores.csv
-rw-r--r-- 1 USUARIO 197121  278 nov.  6 15:06 validacion_mapa.txt
-rw-r--r-- 1 USUARIO 197121  275 nov.  6 15:04 validacion_mapa_extrema.txt
```

</details>

### 2. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && uv run \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/.claude/skills/limpiando-enaho/scripts/limpiar.py\" 2>&1 | tail -40; echo ---; cat salidas/validacion.txt",
 "timeout": 600000
}
```

<details><summary>Resultado</summary>

```json
[OK   ] Filas del módulo 02: 117,721 (esperado 117,721)
[OK   ] Llaves y ubigeo como texto de ancho fijo, con sus ceros iniciales (sumaria)
[OK   ] Llaves y ubigeo como texto de ancho fijo, con sus ceros iniciales (módulo 02)
[OK   ] Sin hogares repetidos en la sumaria
[OK   ] Sin personas repetidas en el módulo 02

Residentes habituales y unión
[OK   ] Residentes habituales: 108,664 de 117,721 filas (esperado 108,664)
[OK   ] Unión validate='m:1': 0 residentes sin hogar
[OK   ] La unión no pierde ni duplica personas: 108,664 antes y 108,664 después
[OK   ] Ubigeo y estrato coinciden entre módulos en 100.0% de los residentes
[OK   ] Hogares con al menos un residente: 33,691 de 33,691

Territorio
[OK   ] Códigos territoriales: 25 en hogares y 25 en personas, del 01 al 25, con Lima (15) y Callao (07) separados
[OK   ] Conglomerados: 5,359 (Ficha Técnica: 5,359)

Factores de expansión
[OK   ] Pesos faltantes o no positivos: 0
[OK   ] Población expandida: 34,482,699 con factor07 × mieperho y 34,147,766 con facpob07
[OK   ] facpob07 es el factor del hogar en 100.0% de los residentes

Pobreza
[OK   ] pobreza solo toma los valores 1, 2 y 3, sin faltantes
[OK   ] La variable pobreza se reproduce con gasto mensual por persona < línea en 100.00% de los hogares
[OK   ] Pobreza nacional (sumaria, factor07 × mieperho): 27.58 % (referencia 27.6 %, tolerancia ±0.1 pp)
[OK   ] Pobreza nacional (residentes, facpob07): 27.53 % (referencia 27.6 %, tolerancia ±0.1 pp)

... (4696 caracteres en total)
```

</details>

### 3. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && uv run \".claude/skills/limpiando-enaho/scripts/estimar.py\" --por area 2>&1 | tail -20"
}
```

<details><summary>Resultado</summary>

```json
Pobreza monetaria, % de personas, ENAHO 2024. Base: sumaria, hogares ponderados con factor07 × mieperho.
codigo categoria   pct   ee  ic95_inf  ic95_sup  cv_pct  n_muestra  upm   poblacion
 Rural     Rural 39.30 0.77     37.80     40.81    1.96      11660 1544  6595187.91
Urbana    Urbana 24.81 0.60     23.62     25.99    2.43      22031 3815 27887511.40
```

</details>

## Respuesta final

La base de la ENAHO 2024 quedó limpia y validada. `salidas/validacion.txt` dice `RESULTADO: APROBADA`, con 25 comprobaciones aprobadas, 0 fallidas y 0 avisos. Se generaron `personas_2024.parquet` (108,664 personas), `hogares_2024.parquet` (33,691 hogares) e `indicadores.csv`.

**Pobreza monetaria 2024**

Estas cifras usan la base de hogares con `factor07 × mieperho`, que es el método del INEI. Se contrastaron con las cifras oficiales y coinciden dentro de la tolerancia.

| Corte | % de personas pobres | IC 95 % |
|---|---|---|
| Nacional | 27.6 % | no calculé este intervalo |
| Urbana | 24.8 % | 23.6 – 26.0 |
| Rural | 39.3 % | 37.8 – 40.8 |
| Pobreza extrema (nacional) | 5.5 % | no calculé este intervalo |
| Lima Metropolitana | 28.2 % | no calculé este intervalo |

- **Intervalos que faltan:** la skill pide dar el intervalo con cada cifra. Solo corrí el corte por área, así que los de las filas nacional, extrema y Lima Metropolitana no están. Puedo calcularlos con `estimar.py`.
- **Diferencia urbana y rural:** los intervalos de ambas áreas no se cruzan. Eso apunta a una brecha, pero no la prueba. Para eso hace falta el intervalo de la diferencia, que calcula la skill `graficando-enaho`.
- **Variabilidad:** los coeficientes de variación son 2.4 % (urbana) y 2.0 % (rural), muy por debajo del 15 %. Las cifras no son solo referenciales.
- **Base de personas:** con `facpob07` la nacional da 27.53 % en vez de 27.58 %. La diferencia viene de que `mieperho` cuenta 109,842 miembros del hogar y los residentes habituales son 108,664. La explicación está en `salidas/validacion.txt`.
- **Alcance:** esta skill solo cubre la ENAHO 2024.

Fuente: INEI, ENAHO 2024.

Si quieres otro corte (departamento, sexo, grupo de edad), dime cuál.
