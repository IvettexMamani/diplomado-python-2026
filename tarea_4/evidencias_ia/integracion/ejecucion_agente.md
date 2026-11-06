# Demostración en Claude Code

- **Fecha:** 2026-11-06 16:05
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas que ve el modelo:** Bash, ListMcpResourcesTool, Read, ReadMcpResourceTool, Skill, Write, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__guardar_series, mcp__bcrp__resumen, mcp__bcrp__serie (solo puede usar las de --allowedTools)
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --mcp-config .mcp.json --tools Skill,Read,Write,Bash,ListMcpResourcesTool,ReadMcpResourceTool --allowedTools "mcp__bcrp,Write,ListMcpResourcesTool,ReadMcpResourceTool,Skill,Read,Bash(uv run *)"`
- **Skills activadas, en orden:** investigando-peru (invocada con /) → limpiando-enaho → graficando-enaho → mapeando-enaho
- **Scripts ejecutados, en orden:** limpiar.py → graficar.py → mapear.py → graficar_bcrp.py → cruzar.py
- **Herramientas usadas:** Bash ×10, mcp__bcrp__buscar_series ×4, ReadMcpResourceTool ×3, mcp__bcrp__guardar_series ×3, Write ×2, Skill ×3, Read ×4, mcp__bcrp__resumen ×2
- **Turnos:** 37 · **segundos:** 213.0 · **costo:** US$ 0.6139

## Pregunta

> /investigando-peru ¿Cómo evolucionaron las agroexportaciones peruanas entre 2020 y 2024, y los departamentos que más agroexportaban en 2022 tenían menos pobreza monetaria en 2024? Entiende agroexportaciones como la suma de los productos tradicionales agrícolas y los no tradicionales agropecuarios.

## Llamadas a herramientas

### 1. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && ls; ls salidas salidas/bcrp figuras mapas informes 2>&1 | head -60"
}
```

<details><summary>Resultado</summary>

```json
_avast_
datos
evidencias_ia
figuras
informes
mapas
mcp
pruebas
pyproject.toml
README.md
salidas
uv.lock
ls: cannot access 'salidas/bcrp': No such file or directory
figuras:
pobreza_area.png
pobreza_departamento.png
pobreza_dominio.png
pobreza_grupo_edad.png
pobreza_sexo.png
pobreza_sexo_departamento-puno.png

informes:

mapas:
pobreza_departamento.png
pobreza_extrema_departamento.png

salidas:
comparacion_mapa.csv
indicadores.csv
validacion_mapa.txt
validacion_mapa_extrema.txt
```

</details>

### 2. `mcp__bcrp__buscar_series`

```json
{
 "texto": "exportaciones productos tradicionales agricolas",
 "frecuencia": "Anual",
 "limite": 30
}
```

<details><summary>Resultado</summary>

```json
{"result":[{"codigo":"PM40076BA","nombre":"Exportaciones de Productos Tradicionales (valores FOB millones US$) - Agrícolas","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat"},{"codigo":"PM40083BA","nombre":"Exportaciones de Productos Tradicionales (valores FOB millones US$) - Agrícolas - Café","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat"},{"codigo":"PM40080BA","nombre":"Exportaciones de Productos Tradicionales (valores FOB millones US$) - Agrícolas - Azúcar","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat"},{"codigo":"PM40077BA","nombre":"Exportaciones de Productos Tradicionales (valores FOB millones US$) - Agrícolas - Algodón","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat"},{"codigo":"PM40086BA","nombre":"Exportaciones de Productos Tradicionales (valores FOB millones US$) - Agrícolas - Resto de Agrícolas","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat"},{"codigo":"PM40046BA","nombre":"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agrícolas","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","
... (8261 caracteres en total)
```

</details>

### 3. `mcp__bcrp__buscar_series`

```json
{
 "texto": "exportaciones productos no tradicionales agropecuarios",
 "frecuencia": "Anual",
 "limite": 30
}
```

<details><summary>Resultado</summary>

```json
{"result":[{"codigo":"PM40121BA","nombre":"Exportaciones de productos no tradicionales - valores FOB (millones US$) - Agropecuarios","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat"},{"codigo":"PM40127BA","nombre":"Exportaciones de productos no tradicionales - valores FOB (millones US$) - Agropecuarios - Resto","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat"},{"codigo":"PM40123BA","nombre":"Exportaciones de productos no tradicionales - valores FOB (millones US$) - Agropecuarios - Frutas","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat"},{"codigo":"PM40122BA","nombre":"Exportaciones de productos no tradicionales - valores FOB (millones US$) - Agropecuarios - Legumbres","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat"},{"codigo":"PM40050BA","nombre":"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos No Tradicionales - Agropecuarios","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat, empresas"},{"codigo":"PM40126BA","nombre":"Exportaciones de productos no tradicionales - valores FOB (millones US$) - Agropecuarios - Té Café Cacao y Esencias","categoria":"Balanza comer
... (8477 caracteres en total)
```

</details>

### 4. `mcp__bcrp__buscar_series`

```json
{
 "texto": "exportaciones por grupo de productos de Valores FOB Productos tradicionales Agrícolas",
 "frecuencia": "Anual",
 "limite": 60
}
```

<details><summary>Resultado</summary>

```json
{"result":[{"codigo":"PM40046BA","nombre":"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agrícolas","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat, empresas"},{"codigo":"RD41130BA","nombre":"Exportaciones por grupo de productos de Ica (Valores FOB en millones US$) - Productos tradicionales - Agrícolas","categoria":"Exportaciones e importaciones","frecuencia":"Anual","inicio":"2005","actualizada":"2024-12-20","fuente_original":""},{"codigo":"RD41198BA","nombre":"Exportaciones por grupo de productos de Lima (Valores FOB en millones US$) - Productos tradicionales - Agrícolas","categoria":"Exportaciones e importaciones","frecuencia":"Anual","inicio":"2005","actualizada":"2024-12-20","fuente_original":""},{"codigo":"RD41300BA","nombre":"Exportaciones por grupo de productos de Puno (Valores FOB en millones US$) - Productos tradicionales - Agrícolas","categoria":"Exportaciones e importaciones","frecuencia":"Anual","inicio":"2005","actualizada":"2024-12-20","fuente_original":""},{"codigo":"RD41079BA","nombre":"Exportaciones por grupo de productos de Cusco (Valores FOB en millones US$) - Productos tradicionales - Agrícolas","categoria":"Exportaciones e importaciones","frecuencia":"Anual","inicio":"2005","actualizada":"2024-12-20","fuente_original":""},{"codigo":"RD41147BA","nombre":"Exportaciones por grupo de productos de Junín (Valores FOB en millones US$) - P
... (7544 caracteres en total)
```

</details>

### 5. `mcp__bcrp__buscar_series`

```json
{
 "texto": "exportaciones por grupo de productos de Valores FOB Productos no tradicionales Agropecuarios",
 "frecuencia": "Anual",
 "limite": 60
}
```

<details><summary>Resultado</summary>

```json
{"result":[{"codigo":"PM40050BA","nombre":"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos No Tradicionales - Agropecuarios","categoria":"Balanza comercial","frecuencia":"Anual","inicio":"2012","actualizada":"2026-05-19","fuente_original":"BCRP, Sunat, empresas"},{"codigo":"RD41134BA","nombre":"Exportaciones por grupo de productos de Ica (Valores FOB en millones US$) - Productos no tradicionales - Agropecuarios","categoria":"Exportaciones e importaciones","frecuencia":"Anual","inicio":"2005","actualizada":"2024-12-20","fuente_original":""},{"codigo":"RD41202BA","nombre":"Exportaciones por grupo de productos de Lima (Valores FOB en millones US$) - Productos no tradicionales - Agropecuarios","categoria":"Exportaciones e importaciones","frecuencia":"Anual","inicio":"2005","actualizada":"2024-12-20","fuente_original":""},{"codigo":"RD41304BA","nombre":"Exportaciones por grupo de productos de Puno (Valores FOB en millones US$) - Productos no tradicionales - Agropecuarios","categoria":"Exportaciones e importaciones","frecuencia":"Anual","inicio":"2005","actualizada":"2024-12-20","fuente_original":""},{"codigo":"RD41083BA","nombre":"Exportaciones por grupo de productos de Cusco (Valores FOB en millones US$) - Productos no tradicionales - Agropecuarios","categoria":"Exportaciones e importaciones","frecuencia":"Anual","inicio":"2005","actualizada":"2024-12-20","fuente_original":""},{"codigo":"RD41151BA","nombre":"Exportaciones por grupo de productos de Juní
... (7733 caracteres en total)
```

</details>

### 6. `ReadMcpResourceTool`

```json
{
 "server": "bcrp",
 "uri": "bcrp://serie/RD41134BA"
}
```

<details><summary>Resultado</summary>

```json
{"contents":[{"uri":"bcrp://serie/RD41134BA","mimeType":"application/json","text":"{\"codigo\": \"RD41134BA\", \"nombre\": \"Exportaciones por grupo de productos de Ica (Valores FOB en millones US$) - Productos no tradicionales - Agropecuarios\", \"categoria\": \"Exportaciones e importaciones\", \"grupo_de_serie\": \"Exportaciones por grupo de productos de Ica (Valores FOB en millones US$)\", \"nombre_de_serie\": \"Productos no tradicionales - Agropecuarios\", \"descripcion\": \"Informaci\\u00f3n estad\\u00edstica regional / Exportaciones e importaciones / Exportaciones por grupo de productos de Ica (Valores FOB en millones US$) / Productos no tradicionales - Agropecuarios\", \"metodologia\": null, \"frecuencia\": \"Anual\", \"datos_desde\": \"2005\", \"actualizada\": \"2024-12-20\", \"fuente_original\": \"BCRP\", \"grupo_de_publicacion\": \"\", \"area_que_publica\": \"Departamento de Estad\\u00edsticas de Balanza de Pagos\", \"tabla_web\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/RD41134BA/html\", \"api\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/RD41134BA/json/{desde}/{hasta}\", \"como_citar\": \"Banco Central de Reserva del Per\\u00fa, serie RD41134BA \\u00abExportaciones por grupo de productos de Ica (Valores FOB en millones US$) - Productos no tradicionales - Agropecuarios\\u00bb (fuente original: BCRP). https://estadisticas.bcrp.gob.pe\"}"}]}
```

</details>

### 7. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/.claude/skills/investigando-peru\" && ls -R . | head; wc -l scripts/*.py; sed -n 1,80p scripts/cruzar.py"
}
```

<details><summary>Resultado</summary>

```json
.:
scripts
SKILL.md

./scripts:
__pycache__
cruzar.py
graficar_bcrp.py

./scripts/__pycache__:
  234 scripts/cruzar.py
  108 scripts/graficar_bcrp.py
  342 total
"""Cruza series del BCRP por departamento con la pobreza monetaria de la ENAHO 2024.

    uv run .claude/skills/investigando-peru/scripts/cruzar.py --datos salidas/bcrp/agroexportaciones_departamento.csv \
        --nacional salidas/agroexportaciones_anual.csv --anio 2022 --tema agroexportaciones --unidad "millones de US$"

Entra el CSV de la herramienta MCP guardar_series, ya con una o más series por departamento. Sale
salidas/cruce_<tema>.csv, salidas/cruce_<tema>.json y figuras/cruce_<tema>.png.

Las series regionales del BCRP no traen ubigeo: su departamento solo aparece en el nombre. Por eso aquí se compara el
nombre sin tildes contra el código del INEI, y se exige que las 25 unidades queden identificadas una por una. Las series
que no son de un departamento, como «sin ubigeo», se apartan y se informan.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patheffects import withStroke  # noqa: E402

sys.path.insert(0, str(Path(__file__).parents[2] / "limpiando-enaho" / "scripts"))
from estimar import ANIO, RAIZ, SALIDAS, cargar, diferencia, fila, tabla  # noqa: E402
from limpiar import DEPARTAMENTOS  
... (3688 caracteres en total)
```

</details>

### 8. `mcp__bcrp__guardar_series`

```json
{
 "codigos": [
  "PM40046BA",
  "PM40050BA",
  "PM40076BA",
  "PM40121BA"
 ],
 "desde": "2020",
 "hasta": "2024",
 "nombre": "agro_nacional"
}
```

<details><summary>Resultado</summary>

```json
{"archivo":"salidas/bcrp/agro_nacional.csv","filas":20,"consultado":"2026-11-06","series":[{"codigo":"PM40046BA","nombre":"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agrícolas","frecuencia":"Anual","desde":"2020","hasta":"2024","n":5,"inicio_catalogo":"2012"},{"codigo":"PM40050BA","nombre":"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos No Tradicionales - Agropecuarios","frecuencia":"Anual","desde":"2020","hasta":"2024","n":5,"inicio_catalogo":"2012"},{"codigo":"PM40076BA","nombre":"Exportaciones de Productos Tradicionales (valores FOB millones US$) - Agrícolas","frecuencia":"Anual","desde":"2020","hasta":"2024","n":5,"inicio_catalogo":"2012"},{"codigo":"PM40121BA","nombre":"Exportaciones de productos no tradicionales - valores FOB (millones US$) - Agropecuarios","frecuencia":"Anual","desde":"2020","hasta":"2024","n":5,"inicio_catalogo":"2012"}],"sin_datos":[]}
```

</details>

### 9. `mcp__bcrp__guardar_series`

```json
{
 "codigos": [
  "RD40960BA",
  "RD40977BA",
  "RD40994BA",
  "RD41011BA",
  "RD41028BA",
  "RD41045BA",
  "RD41062BA",
  "RD41079BA",
  "RD41096BA",
  "RD41113BA",
  "RD41130BA",
  "RD41147BA",
  "RD41164BA",
  "RD41181BA",
  "RD41198BA",
  "RD41215BA",
  "RD41232BA",
  "RD41249BA",
  "RD41266BA",
  "RD41283BA",
  "RD41300BA",
  "RD41317BA",
  "RD41334BA",
  "RD41351BA",
  "RD41368BA",
  "RD41385BA",
  "RD40964BA",
  "RD40981BA",
  "RD40998BA",
  "RD41015BA",
  "RD41032BA",
  "RD41049BA",
  "RD41066BA",
  "RD41083BA",
  "RD41100BA",
  "RD41117BA",
  "RD41134BA",
  "RD41151BA",
  "RD41168BA",
  "RD41185BA",
  "RD41202BA",
  "RD41219BA",
  "RD41236BA",
  "RD41253BA",
  "RD41270BA",
  "RD41287BA",
  "RD41304BA",
  "RD41321BA",
  "RD41338BA",
  "RD41355BA",
  "RD41372BA",
  "RD41389BA"
 ],
 "desde": "2020",
 "hasta": "2024",
 "nombre": "agro_departamental"
}
```

<details><summary>Resultado</summary>

```json
{"archivo":"salidas/bcrp/agro_departamental.csv","filas":156,"consultado":"2026-11-06","series":[{"codigo":"RD40960BA","nombre":"Exportaciones por grupo de productos de Amazonas (Valores FOB en millones US$) - Productos tradicionales - Agrícolas","frecuencia":"Anual","desde":"2020","hasta":"2022","n":3,"inicio_catalogo":"2005"},{"codigo":"RD40977BA","nombre":"Exportaciones por grupo de productos de Ancash (Valores FOB en millones US$) - Productos tradicionales - Agrícolas","frecuencia":"Anual","desde":"2020","hasta":"2022","n":3,"inicio_catalogo":"2005"},{"codigo":"RD40994BA","nombre":"Exportaciones por grupo de productos de Apurimac (Valores FOB en millones US$) - Productos tradicionales - Agrícolas","frecuencia":"Anual","desde":"2020","hasta":"2022","n":3,"inicio_catalogo":"2005"},{"codigo":"RD41011BA","nombre":"Exportaciones por grupo de productos de Arequipa (Valores FOB en millones US$) - Productos tradicionales - Agrícolas","frecuencia":"Anual","desde":"2020","hasta":"2022","n":3,"inicio_catalogo":"2005"},{"codigo":"RD41028BA","nombre":"Exportaciones por grupo de productos de Ayacucho (Valores FOB en millones US$) - Productos tradicionales - Agrícolas","frecuencia":"Anual","desde":"2020","hasta":"2022","n":3,"inicio_catalogo":"2005"},{"codigo":"RD41045BA","nombre":"Exportaciones por grupo de productos de Cajamarca (Valores FOB en millones US$) - Productos tradicionales - Agrícolas","frecuencia":"Anual","desde":"2020","hasta":"2022","n":3,"inicio_catalogo":"2005"},{"codi
... (12367 caracteres en total)
```

</details>

### 10. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && ls salidas salidas/bcrp; git status --short | head -20; cat salidas/bcrp/agro_nacional.csv | cut -c1-200 | head -25"
}
```

<details><summary>Resultado</summary>

```json
This command changes directory before running a version-control command, which can pick up untrusted hooks or repository configuration from the target directory. Approve only if you trust it.
```

</details>

### 11. `Bash`

```json
{
 "command": "ls \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/salidas\" \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/salidas/bcrp\"; cut -c1-220 \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/salidas/bcrp/agro_nacional.csv\""
}
```

<details><summary>Resultado</summary>

```json
C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/salidas:
bcrp
comparacion_mapa.csv
indicadores.csv
validacion_mapa.txt
validacion_mapa_extrema.txt

C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/salidas/bcrp:
agro_departamental.csv
agro_nacional.csv
codigo,nombre,frecuencia,periodo,valor,fuente_web
PM40046BA,Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agrícolas,Anual,2020,731.1315,https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/PM40046BA/html/
PM40046BA,Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agrícolas,Anual,2021,857.011185,https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/PM40046BA/htm
PM40046BA,Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agrícolas,Anual,2022,1354.215676,https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/PM40046BA/ht
PM40046BA,Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agrícolas,Anual,2023,970.670568,https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/PM40046BA/htm
PM40046BA,Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agrícolas,Anual,2024,1229.395141,https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/result
... (4772 caracteres en total)
```

</details>

### 12. `mcp__bcrp__guardar_series`

```json
{
 "codigos": [
  "PM40046BA",
  "PM40050BA"
 ],
 "desde": "2020",
 "hasta": "2024",
 "nombre": "agro_nacional"
}
```

<details><summary>Resultado</summary>

```json
{"archivo":"salidas/bcrp/agro_nacional.csv","filas":10,"consultado":"2026-11-06","series":[{"codigo":"PM40046BA","nombre":"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agrícolas","frecuencia":"Anual","desde":"2020","hasta":"2024","n":5,"inicio_catalogo":"2012"},{"codigo":"PM40050BA","nombre":"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos No Tradicionales - Agropecuarios","frecuencia":"Anual","desde":"2020","hasta":"2024","n":5,"inicio_catalogo":"2012"}],"sin_datos":[]}
```

</details>

### 13. `Write`

```json
{
 "file_path": "C:\\Users\\USUARIO\\Documents\\CIENCIA DE DATOS\\CLASES PYTHON\\PHYTON INTERMEDIO\\diplomado-python-2026\\tarea_4\\informes\\plan.md",
 "content": "# Plan de investigación\n\n## Pregunta\n¿Cómo evolucionaron las agroexportaciones peruanas entre 2020 y 2024, y los departamentos que más agroexportaban en 2022 tenían menos pobreza monetaria en 2024?\n\n## Objetivo\n1. Describir la evolución anual 2020-2024 de las agroexportaciones nacionales (millones de US$ FOB, corrientes).\n2. Medir la asociación entre las agroexportaciones departamentales de 2022 y la pobreza monetaria departamental de 2024 (ENAHO 2024).\n\n## Delimitación\n- Agroexportaciones = productos tradicionales agrícolas + productos no tradicionales agropecuarios. Quedan fuera las exportaciones pesqueras, mineras, textiles y otras no tradicionales. Los productos agroindustriales clasificados fuera de «agropecuarios» tampoco entran.\n- Valores FOB en dólares corrientes: no se mide volumen ni precio.\n- Pobreza monetaria: personas en hogares pobres, ENAHO 2024, ponderada con factor de expansión, 25 unidades (Lima y Callao separados).\n- Los años difieren (exportaciones 2022, pobreza 2024): es una asociación entre niveles de años distintos.\n\n## Indicadores y fuentes\n| Indicador | Fuente | Series |\n|---|---|---|\n| Agroexportaciones nacionales | BCRP, Balanza comercial (anual) | PM40046BA (tradicionales agrícolas) + PM40050BA (no tradicionales agropecuarios) |\n| Agroexportaciones departamentales | BCRP, información regional (anual) | 25 series RD… de tradicionales agrícolas + 25 de no tradicionales agropecuarios, más «sin ubigeo» |\n| Pobreza monetaria 2024 | INEI, ENAHO 2024, módulos 34 y 02 | salidas/ (Skills limpiando-enaho, graficando-enaho, mapeando-enaho) |\n\n## Pasos\n1. Buscar y guardar las series con el MCP del BCRP (`guardar_series`) y revisar `sin_datos` y el periodo real.\n2. Procesar la ENAHO con las Skills `limpiando-enaho` (validación), `graficando-enaho` y `mapeando-enaho`.\n3. Graficar la evolución nacional con `graficar_bcrp.py` y cruzar con `cruzar.py` (año 2022).\n4. Contrastar con `validacion.txt`, `validacion_mapa.txt` y el total nacional.\n5. Escribir `informes/informe_final.md`.\n\n## Riesgos previsibles\n- Las series departamentales llegan solo hasta 2022 (verificado en `guardar_series`): no hay desglose departamental 2023-2024.\n- Lima y Callao pueden concentrar exportaciones por razones de domicilio fiscal o puerto; el criterio de asignación del BCRP no está en la ficha consultada.\n- Parte de las exportaciones queda «sin ubigeo» y no puede asignarse a un departamento.\n- Con 25 unidades y años distintos, la correlación es frágil y sensible a valores extremos.\n- Si la validación de la ENAHO falla, no se escribe el informe.\n"
}
```

<details><summary>Resultado</summary>

```json
File created successfully at: C:\Users\USUARIO\Documents\CIENCIA DE DATOS\CLASES PYTHON\PHYTON INTERMEDIO\diplomado-python-2026\tarea_4\informes\plan.md (file state is current in your context — no need to Read it back)
```

</details>

### 14. `Skill`

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

### 15. `Bash`

```json
{
 "command": "uv run \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/.claude/skills/limpiando-enaho/scripts/limpiar.py\" 2>&1 | tail -40; echo ---; grep -n \"RESULTADO\" \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/salidas/validacion.txt\"",
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

... (2302 caracteres en total)
```

</details>

### 16. `Skill`

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

### 17. `Bash`

```json
{
 "command": "uv run \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/.claude/skills/graficando-enaho/scripts/graficar.py\" --por departamento 2>&1 | tail -50",
 "timeout": 300000
}
```

<details><summary>Resultado</summary>

```json
Guardado: figuras/pobreza_departamento.png
Título: La pobreza es más alta en Cajamarca (45,0 %) y más baja en Ica (6,0 %)
    categoria   pct  ic95_inf  ic95_sup  cv_pct  n_muestra
    Cajamarca 45.01     40.85     49.17    4.72       1469
       Loreto 42.97     38.81     47.13    4.94       1359
         Puno 39.94     35.43     44.45    5.76       1123
        Pasco 38.97     34.00     43.94    6.50        865
      Huánuco 38.96     33.98     43.94    6.52       1244
       Callao 33.86     29.16     38.56    7.09       1027
 Huancavelica 33.40     29.12     37.69    6.55       1042
     Ayacucho 32.76     28.36     37.16    6.85       1160
        Piura 31.86     28.62     35.10    5.19       1611
  La Libertad 30.19     26.61     33.77    6.05       1509
      Ucayali 27.07     22.76     31.38    8.12       1119
         Lima 27.07     24.71     29.43    4.45       4544
       Tumbes 26.90     22.10     31.70    9.10        842
     Amazonas 25.75     20.92     30.58    9.57       1243
        Tacna 23.99     18.38     29.60   11.94       1271
     Apurímac 23.96     19.45     28.47    9.61        913
       Áncash 22.77     19.16     26.39    8.09       1393
   San Martín 22.02     18.12     25.92    9.04       1347
        Cusco 18.54     14.72     22.36   10.52       1230
        Junín 18.50     14.92     22.08    9.87       1506
     Arequipa 15.78     12.73     18.84    9.87       1506
   Lambayeque 14.04     10.37     17.71   13.34       13
... (1710 caracteres en total)
```

</details>

### 18. `Read`

```json
{
 "file_path": "C:\\Users\\USUARIO\\Documents\\CIENCIA DE DATOS\\CLASES PYTHON\\PHYTON INTERMEDIO\\diplomado-python-2026\\tarea_4\\figuras\\pobreza_departamento.png"
}
```

<details><summary>Resultado</summary>

```json

```

</details>

### 19. `Skill`

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

### 20. `Bash`

```json
{
 "command": "uv run \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/.claude/skills/mapeando-enaho/scripts/mapear.py\" 2>&1 | tail -30; cat \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4/salidas/validacion_mapa.txt\" | tail -25",
 "timeout": 300000
}
```

<details><summary>Resultado</summary>

```json
RESULTADO: APROBADO

Guardado: mapas/pobreza_departamento.png
codigo     categoria   pct  ic95_inf  ic95_sup  cv_pct
    06     Cajamarca 45.01     40.85     49.17    4.72
    16        Loreto 42.97     38.81     47.13    4.94
    21          Puno 39.94     35.43     44.45    5.76
    19         Pasco 38.97     34.00     43.94    6.50
    10       Huánuco 38.96     33.98     43.94    6.52
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
    11           Ica  6.01      4.1
... (1791 caracteres en total)
```

</details>

### 21. `Read`

```json
{
 "file_path": "C:\\Users\\USUARIO\\Documents\\CIENCIA DE DATOS\\CLASES PYTHON\\PHYTON INTERMEDIO\\diplomado-python-2026\\tarea_4\\mapas\\pobreza_departamento.png"
}
```

<details><summary>Resultado</summary>

```json

```

</details>

### 22. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && uv run \".claude/skills/investigando-peru/scripts/graficar_bcrp.py\" --datos salidas/bcrp/agro_nacional.csv --desde 2020 --hasta 2024 --tema agroexportaciones --unidad \"millones de US$\" --etiqueta PM40046BA=\"Tradicionales agrícolas\" --etiqueta PM40050BA=\"No tradicionales agropecuarios\" 2>&1 | tail -30"
}
```

<details><summary>Resultado</summary>

```json
Guardado: figuras/agroexportaciones_bcrp.png y salidas/agroexportaciones_anual.csv
codigo  PM40046BA  PM40050BA     total
anio                                  
2020       731.13    6735.39   7466.52
2021       857.01    7868.02   8725.03
2022      1354.22    8367.71   9721.92
2023       970.67    9168.97  10139.64
2024      1229.40   11096.16  12325.56
Variación del total entre 2020 y 2024: 65.08 %
```

</details>

### 23. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && uv run \".claude/skills/investigando-peru/scripts/cruzar.py\" --datos salidas/bcrp/agro_departamental.csv --nacional salidas/agroexportaciones_anual.csv --anio 2022 --tema agroexportaciones --unidad \"millones de US$\" 2>&1 | tail -60; echo ----; cat salidas/cruce_agroexportaciones.json"
}
```

<details><summary>Resultado</summary>

```json
   },
   "primeros_sin_lima_callao": [
    "La Libertad",
    "Ica",
    "Piura",
    "Lambayeque",
    "Áncash"
   ],
   "diferencia_primeros": {
    "dif": -3.307882437568699,
    "ee": 1.0093131915310118,
    "ic95_inf": -5.286136292969482,
    "ic95_sup": -1.3296285821679152,
    "distinguible": true
   },
   "diferencia_sin_lima_callao": {
    "dif": -5.680424407797549,
    "ee": 1.0136827538813118,
    "ic95_inf": -7.66724260540492,
    "ic95_sup": -3.6936062101901785,
    "distinguible": true
   }
  },
  "Productos tradicionales - Agrícolas": {
   "primeros": [
    "Cajamarca",
    "Lima",
    "Callao",
    "Junín",
    "Lambayeque"
   ],
   "spearman_valor": {
    "rho": 0.17244038981854795,
    "p_valor": 0.4096795160241988,
    "n": 25
   },
   "primeros_sin_lima_callao": [
    "Cajamarca",
    "Junín",
    "Lambayeque",
    "La Libertad",
    "Amazonas"
   ],
   "diferencia_primeros": {
    "dif": -0.3402836289388478,
    "ee": 1.0244601250860434,
    "ic95_inf": -2.3482254741074926,
    "ic95_sup": 1.6676582162297973,
    "distinguible": false
   },
   "diferencia_sin_lima_callao": {
    "dif": 0.15125042269151234,
    "ee": 1.0827587568035504,
    "ic95_inf": -1.9709567406434463,
    "ic95_sup": 2.273457586026471,
    "distinguible": false
   }
  }
 }
}
----
{
 "departamentos": 25,
 "primeros": [
  "La Libertad",
  "Lima",
  "Ica",
  "Piura",
  "Lambayeque"
 ],
 "participacion_primeros_pct": 77.
... (5416 caracteres en total)
```

</details>

### 24. `Bash`

```json
{
 "command": "cd \"C:/Users/USUARIO/Documents/CIENCIA DE DATOS/CLASES PYTHON/PHYTON INTERMEDIO/diplomado-python-2026/tarea_4\" && cat salidas/cruce_agroexportaciones.csv | cut -c1-220; ls figuras mapas salidas"
}
```

<details><summary>Resultado</summary>

```json
puesto,departamento,nombre,valor,participacion_pct,por_habitante,poblacion,pobreza_pct,ic95_inf,ic95_sup,cv_pct
1,13,La Libertad,1924.33,19.79,924.81,2080788.66,30.19,26.61,33.77,6.05
2,15,Lima,1829.53,18.82,162.19,11279908.67,27.07,24.71,29.43,4.45
3,11,Ica,1568.08,16.13,1835.72,854203.11,6.01,4.17,7.85,15.61
4,20,Piura,1280.17,13.17,643.77,1988570.01,31.86,28.62,35.1,5.19
5,14,Lambayeque,954.05,9.81,706.85,1349730.84,14.04,10.37,17.71,13.34
6,06,Cajamarca,532.95,5.48,342.82,1554585.69,45.01,40.85,49.17,4.72
7,07,Callao,396.36,4.08,346.89,1142617.94,33.86,29.16,38.56,7.09
8,02,Áncash,246.3,2.53,203.14,1212494.11,22.77,19.16,26.39,8.09
9,12,Junín,229.92,2.36,158.55,1450149.12,18.5,14.92,22.08,9.87
10,22,San Martín,185.74,1.91,196.04,947445.84,22.02,18.12,25.92,9.04
11,04,Arequipa,161.58,1.66,113.65,1421683.66,15.78,12.73,18.84,9.87
12,25,Ucayali,109.08,1.12,195.31,558484.18,27.07,22.76,31.38,8.12
13,23,Tacna,86.79,0.89,227.95,380754.69,23.99,18.38,29.6,11.94
14,01,Amazonas,66.74,0.69,150.87,442355.29,25.75,20.92,30.58,9.57
15,05,Ayacucho,46.46,0.48,59.91,775446.74,32.76,28.36,37.16,6.85
16,08,Cusco,34.59,0.36,24.54,1409467.16,18.54,14.72,22.36,10.52
17,17,Madre de Dios,17.43,0.18,105.03,165991.77,11.15,6.89,15.41,19.5
18,24,Tumbes,10.89,0.11,41.57,261959.1,26.9,22.1,31.7,9.1
19,21,Puno,8.75,0.09,5.51,1586885.77,39.94,35.43,44.45,5.76
20,10,Huánuco,8.63,0.09,9.31,926653.08,38.96,33.98,43.94,6.52
21,16,Loreto,7.24,0.07,6.42,1129070.9,42.97,38.81,47.13,4.94
... (2265 caracteres en total)
```

</details>

### 25. `Read`

```json
{
 "file_path": "C:\\Users\\USUARIO\\Documents\\CIENCIA DE DATOS\\CLASES PYTHON\\PHYTON INTERMEDIO\\diplomado-python-2026\\tarea_4\\figuras\\cruce_agroexportaciones.png"
}
```

<details><summary>Resultado</summary>

```json

```

</details>

### 26. `mcp__bcrp__resumen`

```json
{
 "codigo": "PM40046BA",
 "desde": "2020",
 "hasta": "2024"
}
```

<details><summary>Resultado</summary>

```json
{"codigo":"PM40046BA","nombre":"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agrícolas","frecuencia":"Anual","periodo":{"desde":"2020","hasta":"2024"},"n":5,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PM40046BA/json/2020/2024","fuente_web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/PM40046BA/html/2020/2024/","fuente_original":"BCRP, Sunat, empresas","primero":{"periodo":"2020","valor":731.1315},"ultimo":{"periodo":"2024","valor":1229.395141},"cambio":498.2636,"variacion_pct":68.1497,"promedio":1028.4848,"desviacion_estandar":258.665,"maximo":{"periodo":"2022","valor":1354.215676},"minimo":{"periodo":"2020","valor":731.1315}}
```

</details>

### 27. `mcp__bcrp__resumen`

```json
{
 "codigo": "PM40050BA",
 "desde": "2020",
 "hasta": "2024"
}
```

<details><summary>Resultado</summary>

```json
{"codigo":"PM40050BA","nombre":"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos No Tradicionales - Agropecuarios","frecuencia":"Anual","periodo":{"desde":"2020","hasta":"2024"},"n":5,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PM40050BA/json/2020/2024","fuente_web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/PM40050BA/html/2020/2024/","fuente_original":"BCRP, Sunat, empresas","primero":{"periodo":"2020","valor":6735.3891},"ultimo":{"periodo":"2024","valor":11096.1614},"cambio":4360.7723,"variacion_pct":64.7442,"promedio":8647.2501,"desviacion_estandar":1628.643,"maximo":{"periodo":"2024","valor":11096.1614},"minimo":{"periodo":"2020","valor":6735.3891}}
```

</details>

### 28. `ReadMcpResourceTool`

```json
{
 "server": "bcrp",
 "uri": "bcrp://serie/PM40050BA"
}
```

<details><summary>Resultado</summary>

```json
{"contents":[{"uri":"bcrp://serie/PM40050BA","mimeType":"application/json","text":"{\"codigo\": \"PM40050BA\", \"nombre\": \"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos No Tradicionales - Agropecuarios\", \"categoria\": \"Balanza comercial\", \"grupo_de_serie\": \"Exportaciones por Grupo de Productos (valores FOB millones US$)\", \"nombre_de_serie\": \"Productos No Tradicionales - Agropecuarios\", \"descripcion\": null, \"metodologia\": null, \"frecuencia\": \"Anual\", \"datos_desde\": \"2012\", \"actualizada\": \"2026-05-19\", \"fuente_original\": \"BCRP, Sunat, empresas\", \"grupo_de_publicacion\": \"Demanda y oferta global, balanza de pagos, sector p\\u00fablico y monetario\", \"area_que_publica\": \"Departamento de Estad\\u00edsticas de Balanza de Pagos\", \"tabla_web\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/PM40050BA/html\", \"api\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PM40050BA/json/{desde}/{hasta}\", \"como_citar\": \"Banco Central de Reserva del Per\\u00fa, serie PM40050BA \\u00abExportaciones por Grupo de Productos (valores FOB millones US$) - Productos No Tradicionales - Agropecuarios\\u00bb (fuente original: BCRP, Sunat, empresas). https://estadisticas.bcrp.gob.pe\"}"}]}
```

</details>

### 29. `ReadMcpResourceTool`

```json
{
 "server": "bcrp",
 "uri": "bcrp://serie/PM40046BA"
}
```

<details><summary>Resultado</summary>

```json
{"contents":[{"uri":"bcrp://serie/PM40046BA","mimeType":"application/json","text":"{\"codigo\": \"PM40046BA\", \"nombre\": \"Exportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agr\\u00edcolas\", \"categoria\": \"Balanza comercial\", \"grupo_de_serie\": \"Exportaciones por Grupo de Productos (valores FOB millones US$)\", \"nombre_de_serie\": \"Productos Tradicionales - Agr\\u00edcolas\", \"descripcion\": null, \"metodologia\": null, \"frecuencia\": \"Anual\", \"datos_desde\": \"2012\", \"actualizada\": \"2026-05-19\", \"fuente_original\": \"BCRP, Sunat, empresas\", \"grupo_de_publicacion\": \"Demanda y oferta global, balanza de pagos, sector p\\u00fablico y monetario\", \"area_que_publica\": \"Departamento de Estad\\u00edsticas de Balanza de Pagos\", \"tabla_web\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/PM40046BA/html\", \"api\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PM40046BA/json/{desde}/{hasta}\", \"como_citar\": \"Banco Central de Reserva del Per\\u00fa, serie PM40046BA \\u00abExportaciones por Grupo de Productos (valores FOB millones US$) - Productos Tradicionales - Agr\\u00edcolas\\u00bb (fuente original: BCRP, Sunat, empresas). https://estadisticas.bcrp.gob.pe\"}"}]}
```

</details>

### 30. `Write`

```json
{
 "file_path": "C:\\Users\\USUARIO\\Documents\\CIENCIA DE DATOS\\CLASES PYTHON\\PHYTON INTERMEDIO\\diplomado-python-2026\\tarea_4\\informes\\informe_final.md",
 "content": "# Agroexportaciones peruanas 2020-2024 y pobreza monetaria departamental\n\n## 1. Pregunta de investigación\n\n**Tema.** Evolución de las agroexportaciones peruanas y su relación con la pobreza monetaria departamental.\n\n**Pregunta.** ¿Cómo evolucionaron las agroexportaciones peruanas entre 2020 y 2024, y los departamentos que más agroexportaban en 2022 tenían menos pobreza monetaria en 2024?\n\n**Objetivo.** (1) Describir la evolución anual 2020-2024 de las agroexportaciones nacionales. (2) Medir si los departamentos con más agroexportaciones en 2022 tenían menor pobreza monetaria en 2024.\n\n**Delimitación.**\n- Agroexportaciones = productos tradicionales agrícolas + productos no tradicionales agropecuarios, en valores FOB, millones de US$ corrientes. Quedan fuera las exportaciones de otros grupos (pesqueras, mineras, textiles, entre otras), y no se midió volumen.\n- Pobreza monetaria: porcentaje de personas en hogares pobres, ENAHO 2024, 25 unidades territoriales con Lima y Callao separados.\n- El cruce compara el año 2022 (exportaciones) con el año 2024 (pobreza). Es una asociación entre niveles de años distintos.\n\n## 2. Fuentes y metodología\n\n**BCRP (servidor MCP, serie anual, valores FOB en millones de US$).**\n- Nacional: `PM40046BA` (productos tradicionales, agrícolas) y `PM40050BA` (productos no tradicionales, agropecuarios). Fuente original: BCRP, Sunat, empresas; publica el Departamento de Estadísticas de Balanza de Pagos. Datos desde 2012; consultados de 2020 a 2024 (5 datos por serie). Actualizadas el 19 de mayo de 2026.\n- Departamental: 25 series de tradicionales agrícolas (`RD40960BA`, `RD40977BA`, `RD40994BA`, `RD41011BA`, `RD41028BA`, `RD41045BA`, `RD41062BA`, `RD41079BA`, `RD41096BA`, `RD41113BA`, `RD41130BA`, `RD41147BA`, `RD41164BA`, `RD41181BA`, `RD41198BA`, `RD41215BA`, `RD41232BA`, `RD41249BA`, `RD41266BA`, `RD41283BA`, `RD41300BA`, `RD41317BA`, `RD41334BA`, `RD41351BA`, `RD41368BA`) y 25 de no tradicionales agropecuarios (`RD40964BA`, `RD40981BA`, `RD40998BA`, `RD41015BA`, `RD41032BA`, `RD41049BA`, `RD41066BA`, `RD41083BA`, `RD41100BA`, `RD41117BA`, `RD41134BA`, `RD41151BA`, `RD41168BA`, `RD41185BA`, `RD41202BA`, `RD41219BA`, `RD41236BA`, `RD41253BA`, `RD41270BA`, `RD41287BA`, `RD41304BA`, `RD41321BA`, `RD41338BA`, `RD41355BA`, `RD41372BA`), más las dos series «sin ubigeo» (`RD41385BA`, `RD41389BA`). Datos desde 2005, actualizadas el 20 de diciembre de 2024; **terminan en 2022**.\n\n**ENAHO 2024 (INEI), módulos 34 y 02.** La Skill `limpiando-enaho` unió sumaria y miembros, y la validación quedó **APROBADA** (25 comprobaciones aprobadas, 0 fallidas). Pobreza nacional: 27,58 % (referencia INEI 27,6 %). Las cifras departamentales usan la base de hogares ponderada (`factor07 × mieperho`), con intervalos de 95 %. Las Skills `graficando-enaho` y `mapeando-enaho` generaron el gráfico y el mapa; la validación del mapa quedó APROBADA (25 de 25 unidades; diferencia máxima de 0,05 pp frente a la referencia de la Sesión 16, en Amazonas).\n\n**Procesamiento del cruce.** `graficar_bcrp.py` suma por año las dos series nacionales. `cruzar.py` suma por departamento las dos series de 2022, ordena los departamentos, compara a los 5 primeros con el resto (diferencia con intervalo de 95 %), calcula la correlación de rangos de Spearman con prueba de permutaciones y repite el cruce sin Lima y Callao y por grupo de producto.\n\n## 3. Resultados\n\n1. **Las agroexportaciones crecieron 65,08 % entre 2020 y 2024.** La suma de ambas series pasó de 7 466,5 millones de US$ (2020) a 12 325,6 millones de US$ (2024) (`salidas/agroexportaciones_anual.csv`). Cifras de valor FOB en dólares corrientes: no equivalen a crecimiento de volumen.\n2. **Los dos componentes tuvieron trayectorias distintas.** Los no tradicionales agropecuarios (`PM40050BA`) subieron cada año, de 6 735,4 a 11 096,2 millones de US$ (+64,74 %), con máximo en 2024. Los tradicionales agrícolas (`PM40046BA`) pasaron de 731,1 a 1 229,4 millones de US$ (+68,15 %), pero con máximo en 2022 (1 354,2) y caída en 2023 (970,7).\n3. **En 2022 la agroexportación estaba muy concentrada.** Los cinco primeros departamentos (La Libertad, Lima, Ica, Piura y Lambayeque) reunieron 77,72 % del total departamental de 9 721,9 millones de US$. La Libertad (1 924,3) y Lima (1 829,5) encabezaron. La suma de los 25 departamentos coincide con el total nacional (9 721,88 frente a 9 721,92; diferencia −0,0004 %), y la serie «sin ubigeo» no aportó monto en 2022.\n4. **Resultado principal del cruce, no firme:** los 5 departamentos que más agroexportaron en 2022 tenían 26,0 % de pobreza en 2024 (IC 95 %: 24,3 a 27,6; personas) y el resto 29,3 % (IC 95 %: 28,2 a 30,3), con una diferencia de −3,3 puntos (IC 95 %: −5,3 a −1,3), que se distingue del error de muestreo.\n5. **Esa diferencia no resiste las pruebas de sensibilidad:**\n   - **Sin Lima y Callao**, el grupo de los 5 primeros cambia (entra Cajamarca, con 45,0 % de pobreza) y la pobreza es 28,1 % frente a 27,2 % en el resto: diferencia de +1,0 punto (IC 95 %: −1,1 a +3,0), **no distinguible** del error de muestreo y de signo contrario.\n   - **Correlación de rangos** entre agroexportaciones y pobreza: −0,17 (p = 0,41; n = 25); por habitante, −0,28 (p = 0,18); sin Lima y Callao, −0,26 (p = 0,24; n = 23). Ninguna es estadísticamente distinguible de cero.\n   - **Solo tradicionales agrícolas**: rho = +0,17 (p = 0,41); los 5 primeros (Cajamarca, Lima, Callao, Junín, Lambayeque) difieren del resto en −0,3 puntos (IC 95 %: −2,3 a +1,7), no distinguible. **Solo no tradicionales**: rho = −0,26 (p = 0,22); diferencia de −3,3 puntos (distinguible) y de −5,7 puntos sin Lima y Callao (distinguible).\n6. **Entre los mayores agroexportadores la pobreza es muy heterogénea.** Ica tiene 6,0 % (†) y Lambayeque 14,0 %, pero Piura 31,9 %, La Libertad 30,2 % y Lima 27,1 %. Cajamarca (45,0 %, la más alta del país) es sexta en agroexportaciones (532,9 millones de US$).\n\n† Coeficiente de variación mayor a 15 %: cifra solo referencial (Ica 15,6 %, Moquegua 16,2 %, Madre de Dios 19,5 %). Las demás cifras departamentales de pobreza citadas tienen CV de 15 % o menos.\n\n## 4. Visualizaciones\n\n![Agroexportaciones nacionales 2020-2024, BCRP](../figuras/agroexportaciones_bcrp.png)\n\n![Pobreza monetaria por departamento, ENAHO 2024](../figuras/pobreza_departamento.png)\n\n![Mapa de la pobreza monetaria por departamento, ENAHO 2024](../mapas/pobreza_departamento.png)\n\n![Cruce: agroexportaciones 2022 y pobreza 2024 por departamento](../figuras/cruce_agroexportaciones.png)\n\n## 5. Interpretación\n\n- A escala nacional, las agroexportaciones crecieron de forma sostenida en valor, impulsadas sobre todo por los no tradicionales, mientras los tradicionales fluctuaron.\n- El cruce con la pobreza **no permite afirmar** que los departamentos más agroexportadores tuvieran menos pobreza. El gráfico muestra una diferencia de 3,3 puntos entre los 5 primeros y el resto, pero desaparece (y cambia de signo) al excluir Lima y Callao, y la correlación de rangos es débil y no distinguible de cero en todas las variantes. La asociación aparece solo en los no tradicionales y depende de la definición de agroexportación.\n- Los datos muestran dos polos: Ica y Lambayeque combinan alta agroexportación y baja pobreza, mientras Piura y La Libertad combinan alta agroexportación y pobreza por encima del promedio nacional (27,6 %). Cajamarca, el más pobre, también está entre los diez mayores agroexportadores.\n- Son asociaciones entre un año (2022) y otro (2024), medidas sobre 25 unidades, y no sostienen una relación causal en ningún sentido.\n\n## 6. Limitaciones\n\n- **Cobertura temporal.** Las series departamentales cubren de 2005 a 2022 (en la consulta, 2020-2022). No existe desglose departamental para 2023 y 2024; por eso el cruce usa 2022 y no puede mostrar cómo cambió la distribución territorial después. La pobreza solo cubre 2024: no hay serie ENAHO para comparar cambios en el tiempo.\n- **Años distintos.** Exportaciones 2022 frente a pobreza 2024; la pobreza de 2022 no se consultó.\n- **Incógnita metodológica.** Las fichas de las series (`metodologia: null`) no dicen cómo asigna el BCRP cada exportación a un departamento (por ejemplo, si Lima y Callao reflejan domicilio fiscal o puerto de salida). Esto es relevante porque ambos concentran valor y la conclusión cambia al excluirlos.\n- **Dólares corrientes y valor FOB.** No se separó precio de volumen, ni se deflactó.\n- **Definición de agroexportación.** Solo incluye los dos grupos nombrados; quedan fuera productos agroindustriales clasificados en otros grupos. Los resultados cambian según el grupo usado.\n- **Calidad muestral.** Con 25 unidades y estimaciones muestrales de pobreza, los órdenes entre departamentos con intervalos cruzados no son seguros. Ica, Moquegua y Madre de Dios tienen CV mayor a 15 %; Ica pertenece al grupo de los 5 primeros.\n- **Pruebas.** El p-valor de Spearman es por permutaciones sobre 25 puntos y no corrige por autocorrelación espacial.\n- **Alcance.** La pobreza es de personas en hogares pobres; las agroexportaciones se registran por departamento de origen asignado por el BCRP, no por empleo ni por ingresos de los hogares del departamento.\n- **Búsqueda.** Dos series nacionales adicionales (`PM40076BA`, `PM40121BA`) repiten valores idénticos de `PM40046BA` y `PM40050BA`; se excluyeron para no duplicar la suma.\n\n## 7. Reproducibilidad\n\n**Herramientas y Skills.** MCP del BCRP: `buscar_series`, recurso `bcrp://serie/{codigo}`, `resumen`, `guardar_series`. Skills: `limpiando-enaho`, `graficando-enaho`, `mapeando-enaho`, `investigando-peru`.\n\n**Comandos (desde `tarea_4/`).**\n\n```bash\nuv run .claude/skills/limpiando-enaho/scripts/limpiar.py\nuv run .claude/skills/graficando-enaho/scripts/graficar.py --por departamento\nuv run .claude/skills/mapeando-enaho/scripts/mapear.py\nuv run .claude/skills/investigando-peru/scripts/graficar_bcrp.py --datos salidas/bcrp/agro_nacional.csv --desde 2020 --hasta 2024 --tema agroexportaciones --unidad \"millones de US$\" --etiqueta PM40046BA=\"Tradicionales agrícolas\" --etiqueta PM40050BA=\"No tradicionales agropecuarios\"\nuv run .claude/skills/investigando-peru/scripts/cruzar.py --datos salidas/bcrp/agro_departamental.csv --nacional salidas/agroexportaciones_anual.csv --anio 2022 --tema agroexportaciones --unidad \"millones de US$\"\n```\n\n**Archivos.** `salidas/bcrp/agro_nacional.csv` (`guardar_series`, 2 series, 2020-2024), `salidas/bcrp/agro_departamental.csv` (52 series, 2020-2022), `salidas/agroexportaciones_anual.csv`, `salidas/cruce_agroexportaciones.csv` y `.json`, `salidas/validacion.txt`, `salidas/validacion_mapa.txt`, `salidas/comparacion_mapa.csv`, `salidas/indicadores.csv`, `figuras/agroexportaciones_bcrp.png`, `figuras/pobreza_departamento.png`, `figuras/cruce_agroexportaciones.png`, `mapas/pobreza_departamento.png`, `informes/plan.md`.\n\n**Origen de las cifras**\n\n| Afirmación | Cifra | Archivo o serie |\n|---|---|---|\n| Agroexportaciones totales 2020 | 7 466,5 millones de US$ | `salidas/agroexportaciones_anual.csv` (PM40046BA + PM40050BA) |\n| Agroexportaciones totales 2024 | 12 325,6 millones de US$ | `salidas/agroexportaciones_anual.csv` |\n| Variación del total 2020-2024 | +65,08 % | salida de `graficar_bcrp.py` |\n| No tradicionales agropecuarios 2020 y 2024 | 6 735,4 y 11 096,2 millones de US$; +64,74 % | PM40050BA; `resumen` |\n| Tradicionales agrícolas 2020, 2022, 2023 y 2024 | 731,1; 1 354,2; 970,7 y 1 229,4 millones de US$; +68,15 % | PM40046BA; `resumen` |\n| Participación de los 5 primeros en 2022 | 77,72 % | `salidas/cruce_agroexportaciones.json` |\n| Agroexportaciones 2022 de La Libertad, Lima y Cajamarca | 1 924,3; 1 829,5 y 532,9 millones de US$ | `salidas/cruce_agroexportaciones.csv` |\n| Suma departamental frente a total nacional 2022 | 9 721,88 frente a 9 721,92; −0,0004 % | `cruce_agroexportaciones.json` (`contraste_con_total_nacional`) |\n| Pobreza de los 5 primeros y del resto | 26,0 % y 29,3 %; diferencia −3,3 (IC −5,3 a −1,3) | `cruce_agroexportaciones.json` (`comparacion_primeros`) |\n| Sin Lima y Callao | 28,1 % y 27,2 %; diferencia +1,0 (IC −1,1 a +3,0) | `cruce_agroexportaciones.json` (`comparacion_sin_lima_callao`) |\n| Correlaciones de rangos | −0,17 (p 0,41); −0,28 (p 0,18); −0,26 (p 0,24) | `cruce_agroexportaciones.json` |\n| Sensibilidad por producto | tradicionales +0,17 (p 0,41); no tradicionales −0,26 (p 0,22) | `cruce_agroexportaciones.json` (`sensibilidad_por_producto`) |\n| Pobreza por departamento (Ica, Lambayeque, Piura, La Libertad, Lima, Cajamarca) | 6,0; 14,0; 31,9; 30,2; 27,1 y 45,0 % | `salidas/cruce_agroexportaciones.csv`; salida de `graficar.py` |\n| CV mayor a 15 % | Ica 15,6; Moquegua 16,2; Madre de Dios 19,5 % | `salidas/cruce_agroexportaciones.csv` |\n| Pobreza nacional 2024 | 27,58 % (hogares, `factor07 × mieperho`) | `salidas/validacion.txt` |\n| Validación del mapa | 25 de 25 unidades; diferencia máxima 0,05 pp (Amazonas) | `salidas/validacion_mapa.txt` |\n"
}
```

<details><summary>Resultado</summary>

```json
File created successfully at: C:\Users\USUARIO\Documents\CIENCIA DE DATOS\CLASES PYTHON\PHYTON INTERMEDIO\diplomado-python-2026\tarea_4\informes\informe_final.md (file state is current in your context — no need to Read it back)
```

</details>

### 31. `Read`

```json
{
 "file_path": "C:\\Users\\USUARIO\\Documents\\CIENCIA DE DATOS\\CLASES PYTHON\\PHYTON INTERMEDIO\\diplomado-python-2026\\tarea_4\\figuras\\agroexportaciones_bcrp.png"
}
```

<details><summary>Resultado</summary>

```json

```

</details>

## Respuesta final

**Conclusión.** Las agroexportaciones crecieron 65,08 % entre 2020 y 2024, de 7 466,5 a 12 325,6 millones de US$ corrientes. Los no tradicionales subieron cada año y los tradicionales fluctuaron. Que los departamentos más agroexportadores en 2022 tuvieran menos pobreza en 2024 **no se puede afirmar**. Los 5 primeros tenían 26,0 % de pobreza y el resto 29,3 %, una diferencia que sí se distingue del error de muestreo. Pero sin Lima y Callao la diferencia pasa a +1,0 punto y deja de distinguirse. Además, la correlación de rangos es −0,17 (p = 0,41).

**Archivos creados.**
- `informes/plan.md` y `informes/informe_final.md`
- `salidas/bcrp/agro_nacional.csv` y `salidas/bcrp/agro_departamental.csv`
- `salidas/agroexportaciones_anual.csv` y `salidas/cruce_agroexportaciones.csv` y `.json`
- `figuras/agroexportaciones_bcrp.png`, `figuras/pobreza_departamento.png` y `figuras/cruce_agroexportaciones.png`
- `mapas/pobreza_departamento.png`
- La limpieza regeneró `salidas/personas_2024.parquet`, `salidas/hogares_2024.parquet` y `salidas/validacion.txt`, que `git status` mostraba borrado, y actualizó `salidas/indicadores.csv`.

**Herramientas usadas.**
- **MCP del BCRP:** `buscar_series`, el recurso `bcrp://serie/{codigo}`, `resumen` y `guardar_series`.
- **Skills:** `limpiando-enaho` (validación APROBADA, 25 comprobaciones), `graficando-enaho` y `mapeando-enaho` (APROBADO, diferencia máxima de 0,05 pp).
- **Scripts de `investigando-peru`:** `graficar_bcrp.py` y `cruzar.py`.

**Limitaciones principales.**
- Las series departamentales del BCRP terminan en 2022. No hay desglose por departamento para 2023-2024, y el cruce compara exportaciones de 2022 con pobreza de 2024.
- Las fichas de las series no dicen cómo asigna el BCRP cada exportación a un departamento. Eso pesa porque la conclusión cambia al excluir Lima y Callao.
- Los valores son FOB en dólares corrientes, sin separar precio de volumen.
- Ica, Moquegua y Madre de Dios tienen coeficiente de variación mayor a 15 %, así que sus cifras de pobreza son solo referenciales. Ica está entre los 5 primeros en agroexportaciones.
