# Demostración en Claude Code

- **Fecha:** 2026-11-06 15:03
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas que ve el modelo:** Bash, Read, Skill, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie (solo puede usar las de --allowedTools)
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --mcp-config .mcp.json --tools Skill,Read,Bash --allowedTools "Skill,Read,Bash(uv run *)"`
- **Skills activadas, en orden:** mapeando-enaho (invocada con /)
- **Scripts ejecutados, en orden:** mapear.py
- **Herramientas usadas:** Bash ×2, Read ×1
- **Turnos:** 5 · **segundos:** 43.4 · **costo:** US$ 0.094

## Pregunta

> /mapeando-enaho pobreza extrema

## Llamadas a herramientas

### 1. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && ls -la salidas/ && uv run \".claude/skills/mapeando-enaho/scripts/mapear.py\" --indicador pobre_extremo 2>&1 | tail -30"
}
```

<details><summary>Resultado</summary>

```json
total 2025
drwxr-xr-x 1 USUARIO 197121       0 nov.  6 15:01 .
drwxr-xr-x 1 USUARIO 197121       0 nov.  6 14:55 ..
-rw-r--r-- 1 USUARIO 197121    1333 nov.  6 14:59 comparacion_mapa.csv
-rw-r--r-- 1 USUARIO 197121 1123331 nov.  6 15:01 hogares_2024.parquet
-rw-r--r-- 1 USUARIO 197121    9395 nov.  6 15:01 indicadores.csv
-rw-r--r-- 1 USUARIO 197121  915555 nov.  6 15:01 personas_2024.parquet
-rw-r--r-- 1 USUARIO 197121    2437 nov.  6 15:01 validacion.txt
-rw-r--r-- 1 USUARIO 197121     278 nov.  6 14:59 validacion_mapa.txt


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
... (2060 caracteres en total)
```

</details>

### 2. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && cat salidas/validacion_mapa.txt; echo; cat salidas/comparacion_mapa.csv | head -30; ls mapas"
}
```

<details><summary>Resultado</summary>

```json
Validación del mapa, ENAHO 2024: Pobreza monetaria extrema



[OK   ] Unión por código FIRST_IDDP = ubigeo[:2]: 25 de 25 unidades con geometría y dato



RESULTADO: APROBADO


codigo,categoria,pct,referencia,diferencia,ic95_inf,ic95_sup,cv_pct,n_muestra

01,Amazonas,25.75,25.7,0.05,20.92,30.58,9.57,1243

02,Áncash,22.77,22.8,-0.03,19.16,26.39,8.09,1393

03,Apurímac,23.96,24.0,-0.04,19.45,28.47,9.61,913

04,Arequipa,15.78,15.8,-0.02,12.73,18.84,9.87,1506

05,Ayacucho,32.76,32.8,-0.04,28.36,37.16,6.85,1160

06,Cajamarca,45.01,45.0,0.01,40.85,49.17,4.72,1469

07,Callao,33.86,33.9,-0.04,29.16,38.56,7.09,1027

08,Cusco,18.54,18.5,0.04,14.72,22.36,10.52,1230

09,Huancavelica,33.4,33.4,0.0,29.12,37.69,6.55,1042

10,Huánuco,38.96,39.0,-0.04,33.98,43.94,6.52,1244

11,Ica,6.01,6.0,0.01,4.17,7.85,15.61,1500

12,Junín,18.5,18.5,0.0,14.92,22.08,9.87,1506

13,La Libertad,30.19,30.2,-0.01,26.61,33.77,6.05,1509

14,Lambayeque,14.04,14.0,0.04,10.37,17.71,13.34,1302

15,Lima,27.07,27.1,-0.03,24.71,29.43,4.45,4544

16,Loreto,42.97,43.0,-0.03,38.81,47.13,4.94,1359

17,Madre de Dios,11.15,11.1,0.05,6.89,15.41,19.5,603

18,Moquegua,10.97,11.0,-0.03,7.48,14.46,16.23,963

19,Pasco,38.97,39.0,-0.03,34.0,43.94,6.5,865

20,Piura,31.86,31.9,-0.04,28.62,35.1,5.19,1611

21,Puno,39.94,39.9,0.04,35.43,44.45,5.76,1123

22,San Martín,22.02,22.0,0.02,18.12,25.92,9.04,1347

23,Tacna,23.99,24.0,-0.01,18.38,29.6,11.94,1271

24,Tumbes,26.9,26.9,0.0,22.1,31.7,9.1,842

25,Ucayali,27.07,27.1,-0.03,22.76,31.38,8.12,11
... (1561 caracteres en total)
```

</details>

### 3. `Read`

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

El mapa de pobreza extrema está generado, pero la comparación con la referencia de la Sesión 16 no se pudo hacer para este indicador, y el título del mapa se corta por la derecha.

**Resultado:** `mapas/pobreza_extrema_departamento.png`. La validación dice `RESULTADO: APROBADO`: los 25 departamentos se unieron por código (`FIRST_IDDP = ubigeo[:2]`) y tienen geometría y dato. En la imagen no hay zonas en blanco. Lima (3,1 %) y Callao (5,0 %) aparecen como dos unidades en el recuadro.

**Comparación con la referencia (no aplica):** `salidas/comparacion_mapa.csv` trae las cifras de pobreza total (Cajamarca 45,0 %, Lima 27,1 %…), no las de pobreza extrema. Parece un archivo de la corrida anterior y no corresponde a este mapa. La validación de este mapa solo comprobó la unión por código. No puedo decir que las cifras de pobreza extrema coinciden con la Sesión 16. Si necesitan esa comparación, habría que revisar si el script tiene referencia para este indicador.

**Dónde hay más y menos pobreza extrema**

| | Departamento | % de personas | IC 95 % |
|---|---|---|---|
| Más | Cajamarca | 19,7 | 16,3–23,1 |
| | Loreto | 15,0 | 11,7–18,3 |
| | Puno | 12,5 | 9,7–15,3 |
| | Huánuco | 12,2 | 8,8–15,6 |
| | Huancavelica | 11,2 | 8,2–14,2 |
| Menos | Ica | 0,1 | 0,0–0,4 |
| | Lambayeque | 0,5 | 0,2–0,9 |
| | Tumbes | 1,1 | 0,0–2,1 |

**Advertencias**
- Las cifras son muestrales. Los intervalos de Cajamarca y Loreto se cruzan, así que el orden entre ellos no es seguro. Cajamarca sí queda por encima de Puno, porque su límite inferior (16,3) supera el superior de Puno (15,3). Entre Puno, Huánuco y Huancavelica los intervalos también se cruzan.
- Llevan † (coeficiente de variación mayor a 15 %, solo referencial) 17 de los 25 departamentos, entre ellos Lima y Callao. La cifra de Ica (0,1 %) es especialmente poco fiable, con un coeficiente de variación de casi 100 %. Solo las de Cajamarca, Loreto, Puno, Huánuco, Huancavelica, Ayacucho, La Libertad y Áncash son más firmes.

**Patrón territorial:** los departamentos con más pobreza extrema forman dos conjuntos. Uno está en la sierra norte y centro-sur (Cajamarca, Huánuco, Huancavelica, y Puno en el altiplano). El otro es Loreto, en la selva norte. La costa y el sur (Ica, Lambayeque, Tumbes, Arequipa, Moquegua, Tacna) tienen valores bajos. Es una descripción de dónde se ubican las cifras; el mapa no permite afirmar causas.

**Defectos visuales**
- **Título cortado:** el título se corta por la derecha ("…del P" en lugar de "…del Perú"). Hay que acortarlo o partirlo en tres líneas en `mapear.py`.
- **Leyenda:** muestra solo dos clases (0–10 y 10–20). Es correcto según la regla de clases de 10 puntos, pero casi no distingue entre los departamentos con menos del 10 %.

¿Quieren que corrija el título en el script?
