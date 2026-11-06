# Demostración en Claude Code

- **Fecha:** 2026-11-06 15:07
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas que ve el modelo:** Bash, Read, Skill, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie (solo puede usar las de --allowedTools)
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --mcp-config .mcp.json --tools Skill,Read,Bash --allowedTools "Skill,Read,Bash(uv run *)"`
- **Skills activadas, en orden:** graficando-enaho → limpiando-enaho
- **Scripts ejecutados, en orden:** graficar.py → limpiar.py → graficar.py
- **Herramientas usadas:** Skill ×2, Bash ×3, Read ×1
- **Turnos:** 9 · **segundos:** 52.0 · **costo:** US$ 0.0571

## Pregunta

> Grafica la pobreza por grupos de edad con la ENAHO 2024.

## Llamadas a herramientas

### 1. `Skill`

```json
{
 "skill": "graficando-enaho"
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
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && ls salidas/*.parquet && uv run \".claude/skills/graficando-enaho/scripts/graficar.py\" --por grupo_edad"
}
```

<details><summary>Resultado</summary>

```json
Exit code 2
ls: cannot access 'salidas/*.parquet': No such file or directory
```

</details>

### 3. `Skill`

```json
{
 "skill": "limpiando-enaho"
}
```

<details><summary>Resultado</summary>

```json
Launching skill: limpiando-enaho
```

</details>

### 4. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && uv run \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/.claude/skills/limpiando-enaho/scripts/limpiar.py\" 2>&1 | tail -40; echo ---; cat salidas/validacion.txt | tail -30",
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

... (3960 caracteres en total)
```

</details>

### 5. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && uv run \".claude/skills/graficando-enaho/scripts/graficar.py\" --por grupo_edad 2>&1 | tail -30; ls figuras"
}
```

<details><summary>Resultado</summary>

```json
Guardado: figuras/pobreza_grupo_edad.png
Título: La pobreza es más alta en el grupo de 0-14 años (37,5 %) y más baja en el grupo de 45-59 años (21,4 %)
categoria   pct  ic95_inf  ic95_sup  cv_pct  n_muestra
     0-14 37.52     36.17     38.86    1.83      26489
    15-29 25.97     24.69     27.25    2.51      23122
    30-44 27.87     26.57     29.17    2.38      20648
    45-59 21.41     20.24     22.58    2.79      19408
 60 y más 22.02     20.78     23.26    2.86      18997
Total del dominio: 27.53 %
pobreza_area.png
pobreza_departamento.png
pobreza_dominio.png
pobreza_grupo_edad.png
pobreza_sexo.png
pobreza_sexo_departamento-puno.png
```

</details>

### 6. `Read`

```json
{
 "file_path": "C:\\Users\\USUARIO\\Documents\\CIENCIA DE DATOS\\CLASES PYTHON\\PHYTON INTERMEDIO\\diplomado-python-2026\\tarea_4\\figuras\\pobreza_grupo_edad.png"
}
```

<details><summary>Resultado</summary>

```json

```

</details>

## Respuesta final

Hice el gráfico: `figuras/pobreza_grupo_edad.png`. Lo revisé y se lee bien. Antes tuve que generar la base con `limpiando-enaho`, porque no existía. Su validación salió APROBADA, con 25 comprobaciones aprobadas y ninguna fallida.

**Pobreza monetaria por grupo de edad, Perú 2024** (% de personas, ponderado con `facpob07`, IC 95 %)

| Grupo | % | IC 95 % | CV |
|---|---|---|---|
| 0-14 | 37,5 | 36,2 – 38,9 | 1,8 % |
| 15-29 | 26,0 | 24,7 – 27,3 | 2,5 % |
| 30-44 | 27,9 | 26,6 – 29,2 | 2,4 % |
| 45-59 | 21,4 | 20,2 – 22,6 | 2,8 % |
| 60 y más | 22,0 | 20,8 – 23,3 | 2,9 % |

El total nacional con esta base es 27,5 %.

- **Niñez:** el grupo de 0-14 años tiene la pobreza más alta, unos 10 puntos porcentuales sobre el promedio nacional.
- **Contra el total:** 0-14 está por encima, 15-29, 45-59 y 60 y más están por debajo, y 30-44 no se distingue del total. Esta última es la barra de color suave.
- **Brecha:** 45-59 y 60 y más, los dos grupos más bajos, tienen intervalos que se cruzan, así que no hay una diferencia clara entre ellos.
- **Fiabilidad:** ninguna cifra supera el 15 % de coeficiente de variación, así que ninguna es solo referencial.

Esto describe una asociación entre edad y pobreza, no su causa. Probablemente se deba en parte a que los hogares con niños son más numerosos, pero eso no sale de estos datos.

Fuente: INEI, ENAHO 2024 (módulos 34 y 02).
