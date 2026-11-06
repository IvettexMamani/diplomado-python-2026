---
name: investigando-peru
description: Investiga preguntas socioeconómicas del Perú que combinan series oficiales del BCRP con microdatos de la ENAHO 2024 y escribe un informe reproducible en informes/informe_final.md. Úsala cuando pidan un informe, una investigación o un análisis que una indicadores macroeconómicos, como exportaciones, inflación o actividad económica, con pobreza o brechas territoriales.
argument-hint: "[pregunta de investigación]"
allowed-tools: Bash(uv run *), PowerShell(uv run *), Read, Write, ReadMcpResourceTool, mcp__bcrp
---

# Investigar con el BCRP y la ENAHO

Pregunta: $ARGUMENTS

Regla central: tú planificas, eliges e interpretas; los números salen de las herramientas. No calcules a mano ni copies
cifras a un script. Cada cifra del informe debe aparecer en una salida de una herramienta o en un archivo de `salidas/`.

## 1. Planificar

Antes de consultar datos, escribe `informes/plan.md` con la pregunta, el objetivo, la delimitación, cada indicador con
su fuente, los pasos y los riesgos previsibles. Si la pregunta no usa las dos fuentes, dilo y detente.

Define cada indicador por escrito. Si un concepto tiene varios componentes, inclúyelos todos y nombra lo que quede fuera.

## 2. Consultar el BCRP con el servidor MCP

1. Encuentra las series con `buscar_series`, una búsqueda por cada componente del indicador. Para series por departamento
   usa `frecuencia="Anual"` y `limite=30`, con las palabras del grupo y del producto, por ejemplo
   `exportaciones grupo productos tradicionales agricolas` y `exportaciones grupo productos no tradicionales agropecuarios`.
2. Lee el recurso `bcrp://serie/{codigo}` de una serie principal para saber quién la publica y cómo citarla.
3. Usa `resumen` para la evolución de las series nacionales.
4. Usa `guardar_series` para todo dato que un script vaya a procesar. Revisa `sin_datos` y el periodo real de cada serie.
5. Comprueba si cada serie llega al año de la ENAHO. Si una herramienta devuelve un error o no hay datos, no lo rodees ni
   interpoles: anótalo para la sección de limitaciones.

## 3. Procesar la ENAHO con las Skills

Invoca cada Skill con la herramienta `Skill`, por su nombre, y sigue sus instrucciones. No leas su `SKILL.md` ni corras sus
scripts desde aquí: cada una trae sus reglas de validación, y la ejecución debe dejar constancia de que se activó.

1. Invoca `limpiando-enaho` si faltan las bases de `salidas/` y confirma `RESULTADO: APROBADA`.
2. Invoca `graficando-enaho` para al menos un gráfico pertinente a la pregunta.
3. Invoca `mapeando-enaho` para el mapa departamental.

Si una validación falla, detente y explícalo: el informe no se escribe sobre una base rechazada.

## 4. Cruzar las dos fuentes

Primero, el gráfico del BCRP. Suma por año lo guardado con `guardar_series`:

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/graficar_bcrp.py" --datos salidas/bcrp/<archivo_nacional>.csv --desde 2020 --hasta 2024 --tema <tema> --unidad "millones de US$" --etiqueta <CODIGO>="<texto>" --etiqueta <CODIGO>="<texto>"
```

Después, el cruce con la pobreza por departamento:

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/cruzar.py" --datos salidas/bcrp/<archivo_departamental>.csv --nacional salidas/<tema>_anual.csv --anio <año> --tema <tema> --unidad "millones de US$"
```

`cruzar.py` escribe `salidas/cruce_<tema>.csv`, `salidas/cruce_<tema>.json` y `figuras/cruce_<tema>.png`. Los dos scripts
imprimen sus resultados. Si terminan con un error, informa cuál fue.

El JSON trae dos pruebas de sensibilidad: `comparacion_sin_lima_callao` quita esos dos departamentos, y
`sensibilidad_por_producto` repite el cruce con cada grupo de productos por separado. Léelas antes de concluir.

## 5. Contrastar con las fuentes oficiales

Revisa y anota:

- `salidas/validacion.txt`: pobreza frente a las cifras del INEI.
- `salidas/validacion_mapa.txt` y `salidas/comparacion_mapa.csv`: el mapa frente a la referencia de la Sesión 16.
- `contraste_con_total_nacional` en `salidas/cruce_<tema>.json`: la suma de los departamentos frente al total nacional.

## 6. Escribir el informe

Escribe `informes/informe_final.md` con estas siete secciones, en este orden:

1. **Pregunta de investigación:** tema, objetivo y delimitación.
2. **Fuentes y metodología:** datos, procesamiento e indicadores. Nombra los códigos de las series.
3. **Resultados:** al menos 3 hallazgos, cada uno con su cifra, periodo y origen.
4. **Visualizaciones:** un gráfico del BCRP, uno de la ENAHO, el mapa y el gráfico del cruce. Enlázalos como
   `![texto](../figuras/archivo.png)` y `![texto](../mapas/archivo.png)`.
5. **Interpretación:** los patrones principales.
6. **Limitaciones:** cobertura temporal, calidad de los datos y alcance. Incluye lo que no se pudo obtener.
7. **Reproducibilidad:** scripts, archivos, series y comandos. Termina con una tabla «Origen de las cifras» con tres
   columnas: afirmación, cifra y archivo o serie de donde sale.

Reglas del informe:

- Escribe en tercera persona, con coma decimal, y di siempre la unidad, el periodo y si la cifra es de hogares o personas.
- Antes de afirmar algo sobre el cruce, lee los resultados completos de `cruzar.py`. Si una prueba de sensibilidad
  contradice el resultado principal, esa contradicción es un hallazgo y va en primer plano: no presentes como firme un
  resultado que cambia al quitar un departamento o al cambiar la definición.
- Di si una diferencia se distingue del error de muestreo. Señala las cifras con coeficiente de variación mayor a 15 %.
- Describe la cobertura de una serie con su inicio y su fin reales (`inicio_catalogo` y `hasta`), no con el rango pedido.
- Las exportaciones están en dólares corrientes: no hables de volumen si no lo mediste.
- Presenta asociaciones, no causas. Datos de años o niveles distintos no prueban que una variable afecte a la otra.
- No afirmes nada que ninguna salida respalde. Si las fuentes consultadas no dicen cómo se construye un dato, por ejemplo
  cómo asigna el BCRP cada exportación a un departamento, decláralo como una incógnita en las limitaciones.
- No inventes referencias: cita solo lo que consultaste.

## 7. Cerrar

Responde con la conclusión en dos o tres frases, los archivos creados, las herramientas MCP y Skills que usaste y las
limitaciones principales.
