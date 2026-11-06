# Demostración en Claude Code

- **Fecha:** 2026-11-06 15:06
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas que ve el modelo:** Bash, Read, Skill, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie (solo puede usar las de --allowedTools)
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --mcp-config .mcp.json --tools Skill,Read,Bash --allowedTools "Skill,Read,Bash(uv run *)"`
- **Skills activadas, en orden:** mapeando-enaho → limpiando-enaho
- **Scripts ejecutados, en orden:** limpiar.py → mapear.py
- **Herramientas usadas:** Skill ×2, Bash ×3, Read ×1
- **Turnos:** 10 · **segundos:** 60.8 · **costo:** US$ 0.1117

## Pregunta

> Haz un mapa de la pobreza monetaria por departamento con ENAHO 2024.

## Llamadas a herramientas

### 1. `Skill`

```json
{
 "skill": "mapeando-enaho"
}
```

<details><summary>Resultado</summary>

```json
Launching skill: mapeando-enaho
```

</details>

### 2. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && ls salidas/ && ls mapas/"
}
```

<details><summary>Resultado</summary>

```json
comparacion_mapa.csv
indicadores.csv
validacion_mapa.txt
validacion_mapa_extrema.txt
pobreza_departamento.png
pobreza_extrema_departamento.png
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
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && uv run \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/.claude/skills/limpiando-enaho/scripts/limpiar.py\" 2>&1 | tail -40; ls salidas; cat salidas/validacion.txt | tail -15",
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


... (3394 caracteres en total)
```

</details>

### 5. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && uv run \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/.claude/skills/mapeando-enaho/scripts/mapear.py\" 2>&1 | tail -20; cat salidas/validacion_mapa.txt; cat salidas/comparacion_mapa.csv",
 "timeout": 300000
}
```

<details><summary>Resultado</summary>

```json
    07        Callao 33.86     29.16     38.56    7.09

    09  Huancavelica 33.40     29.12     37.69    6.55

    05      Ayacucho 32.76     28.36     37.16    6.85

    20         Piura 31.86     28.62     35.10    5.19

    13   La Libertad 30.19     26.61     33.77    6.05

    25       Ucayali 27.07     22.76     31.38    8.12

    15          Lima 27.07     24.71     29.43    4.45

    24        Tumbes 26.90     22.10     31.70    9.10

    01      Amazonas 25.75     20.92     30.58    9.57

    23         Tacna 23.99     18.38     29.60   11.94

    03      Apurímac 23.96     19.45     28.47    9.61

    02        Áncash 22.77     19.16     26.39    8.09

    22    San Martín 22.02     18.12     25.92    9.04

    08         Cusco 18.54     14.72     22.36   10.52

    12         Junín 18.50     14.92     22.08    9.87

    04      Arequipa 15.78     12.73     18.84    9.87

    14    Lambayeque 14.04     10.37     17.71   13.34

    17 Madre de Dios 11.15      6.89     15.41   19.50

    18      Moquegua 10.97      7.48     14.46   16.23

    11           Ica  6.01      4.17      7.85   15.61

Validación del mapa, ENAHO 2024: Pobreza monetaria



[OK   ] Unión por código FIRST_IDDP = ubigeo[:2]: 25 de 25 unidades con geometría y dato

[OK   ] Frente a la referencia de la Sesión 16: diferencia máxima 0.05 pp (Amazonas), tolerancia 0.1 pp



RESULTADO: APROBADO

codigo,categoria,pct,referencia,diferencia,ic95_inf,ic95_sup,cv_pct,n_muestra

01,Amazonas,25.75,25.7,0.05,2
... (2718 caracteres en total)
```

</details>

### 6. `Read`

```json
{
 "file_path": "C:\\Users\\USUARIO\\Documents\\CIENCIA DE DATOS\\CLASES PYTHON\\PHYTON INTERMEDIO\\diplomado-python-2026\\tarea_4\\mapas\\pobreza_departamento.png"
}
```

<details><summary>Resultado</summary>

```json

```

</details>

## Respuesta final

Generé el mapa de pobreza monetaria por departamento con la ENAHO 2024. Está en `mapas/pobreza_departamento.png`.

**Validación.** Antes del mapa tuve que correr `limpiando-enaho`, porque faltaba `hogares_2024.parquet`. Su validación salió APROBADA, con 25 pruebas aprobadas y 0 fallidas. La del mapa también salió APROBADO:
- Los 25 departamentos tienen geometría y dato, unidos por código (`ubigeo[:2]` = `FIRST_IDDP`). Lima y Callao van separados y el recuadro muestra a los dos.
- Frente a la referencia de la Sesión 16, la diferencia máxima es 0,05 pp (Amazonas), dentro de la tolerancia de 0,1 pp.
- Al abrir la imagen vi los 25 departamentos coloreados, sin zonas en blanco.

**Más pobreza** (% de personas, base de hogares con `factor07 × mieperho`):

| Departamento | % | IC 95 % |
|---|---|---|
| Cajamarca | 45,0 | 40,9–49,2 |
| Loreto | 43,0 | 38,8–47,1 |
| Puno | 39,9 | 35,4–44,5 |
| Pasco | 39,0 | 34,0–43,9 |
| Huánuco | 39,0 | 34,0–43,9 |

**Menos pobreza:**

| Departamento | % | IC 95 % |
|---|---|---|
| Ica | 6,0 † | 4,2–7,9 |
| Moquegua | 11,0 † | 7,5–14,5 |
| Madre de Dios | 11,1 † | 6,9–15,4 |
| Lambayeque | 14,0 | 10,4–17,7 |
| Arequipa | 15,8 | 12,7–18,8 |

**Advertencias.**
- Las cifras vienen de una muestra, y muchos intervalos se cruzan. Por ejemplo, Cajamarca y Loreto, o Puno, Pasco y Huánuco, no se pueden ordenar con seguridad entre sí.
- Las cifras con † (Ica, Moquegua y Madre de Dios) tienen coeficiente de variación mayor a 15 %, así que son solo referenciales.

**Patrón territorial** (descriptivo, sin afirmar causas):
- La pobreza más alta se agrupa en la sierra norte (Cajamarca), el centro (Huánuco, Pasco), Puno y la selva norte (Loreto).
- La más baja aparece en departamentos de la costa sur (Ica, Moquegua, Arequipa) y en Lambayeque. Madre de Dios, en la selva sur, también está en ese grupo.
- Lima (27,1 %) y Callao (33,9 %) quedan en un nivel intermedio. Sus intervalos no se cruzan del todo, pero tampoco los comparé formalmente.

Si quieres, genero también el mapa de pobreza extrema con `--indicador pobre_extremo`. Ese mapa solo comprueba la unión, porque la referencia de la Sesión 16 cubre únicamente la pobreza total.
