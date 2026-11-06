# Agroexportaciones y pobreza monetaria departamental en el Perú

## 1. Pregunta de investigación

**Tema.** Agroexportaciones peruanas (exportaciones no tradicionales agropecuarias, valores FOB) y pobreza monetaria.

**Objetivo.** (1) Describir cómo evolucionaron las agroexportaciones nacionales entre 2020 y 2024. (2) Ver si los departamentos que más agroexportaban en 2022 tenían menos pobreza monetaria en 2024.

**Delimitación.** Exportaciones en millones de US$ corrientes, no en volumen. Pobreza monetaria de **personas**, ENAHO 2024, en 25 unidades territoriales (Lima y Callao separados). El cruce une el departamento de 2022 con la pobreza de 2024: es una asociación entre años distintos, no una relación causal.

## 2. Fuentes y metodología

**Datos del BCRP** (consultados el 2026-11-06 con el servidor MCP):

- `PM40050BA`: Exportaciones por Grupo de Productos (valores FOB millones US$), Productos No Tradicionales – Agropecuarios. Anual, 2020-2024. Fuente original: BCRP, Sunat, empresas. Publica el Departamento de Estadísticas de Balanza de Pagos.
- 26 series departamentales de «Exportaciones por grupo de productos de {departamento}», Productos no tradicionales – Agropecuarios: `RD40964BA` (Amazonas), `RD40981BA` (Áncash), `RD40998BA` (Apurímac), `RD41015BA` (Arequipa), `RD41032BA` (Ayacucho), `RD41049BA` (Cajamarca), `RD41066BA` (Callao), `RD41083BA` (Cusco), `RD41100BA` (Huancavelica), `RD41117BA` (Huánuco), `RD41134BA` (Ica), `RD41151BA` (Junín), `RD41168BA` (La Libertad), `RD41185BA` (Lambayeque), `RD41202BA` (Lima), `RD41219BA` (Loreto), `RD41236BA` (Madre de Dios), `RD41253BA` (Moquegua), `RD41270BA` (Pasco), `RD41287BA` (Piura), `RD41304BA` (Puno), `RD41321BA` (San Martín), `RD41338BA` (Tacna), `RD41355BA` (Tumbes), `RD41372BA` (Ucayali) y `RD41389BA` (sin ubigeo).

**Datos de la ENAHO.** INEI, ENAHO 2024, módulos 34 (sumaria) y 02 (miembros). Pobreza monetaria ponderada con intervalos de confianza de 95 % y coeficiente de variación (CV). Las cifras por departamento usan la base de hogares (`factor07 × mieperho`), el método del INEI.

**Procesamiento.** Skills `limpiando-enaho` (validación: 25 comprobaciones aprobadas, 0 fallidas), `graficando-enaho` y `mapeando-enaho`. Los scripts `graficar_bcrp.py` y `cruzar.py` de `investigando-peru` producen el gráfico del BCRP y el cruce. El cruce calcula la pobreza de los departamentos con mayor valor exportado frente al resto, el intervalo de esa diferencia y correlaciones de Spearman.

## 3. Resultados

1. **Las agroexportaciones nacionales crecieron 64,7 % entre 2020 y 2024.** Pasaron de 6 735,4 a 11 096,2 millones de US$ corrientes (FOB), con aumento en cada año: 7 868,0 (2021), 8 367,7 (2022) y 9 169,0 (2023). El máximo fue 2024 y el mínimo 2020. Origen: `PM40050BA`, herramienta `resumen` y `salidas/agroexportaciones_anual.csv`. Es valor en dólares corrientes: no mide volumen ni distingue precio de cantidad.
2. **En 2022 la agroexportación estaba concentrada.** Cinco departamentos sumaron 85,6 % del total: La Libertad (1 857,7 millones de US$; 22,2 %), Lima (1 633,8; 19,5 %), Ica (1 567,8; 18,7 %), Piura (1 259,2; 15,1 %) y Lambayeque (844,1; 10,1 %). La suma de los 25 departamentos (8 367,7) coincide con el total nacional de `PM40050BA` (diferencia −0,0006 %). Origen: `salidas/cruce_agroexportaciones.csv` y `.json`.
3. **Los cinco mayores agroexportadores de 2022 tenían menos pobreza en 2024 que el resto, y la diferencia se distingue del error de muestreo.** Pobreza de personas, ENAHO 2024: 26,0 % en esos cinco (IC 95 %: 24,3-27,6) frente a 29,3 % en los demás (IC 95 %: 28,2-30,3). Diferencia: −3,3 puntos porcentuales (IC 95 %: −5,3 a −1,3). Si se excluyen Lima y Callao, el grupo (La Libertad, Ica, Piura, Lambayeque y Áncash) tiene 23,8 % frente a 29,4 %: −5,7 pp (IC 95 %: −7,7 a −3,7). Origen: `salidas/cruce_agroexportaciones.json`, `comparacion_primeros` y `comparacion_sin_lima_callao`.
4. **La correlación entre ambas variables, en cambio, es débil y no concluyente.** Spearman entre valor exportado 2022 y pobreza 2024, 25 departamentos: ρ = −0,26 (p = 0,22). Por habitante: ρ = −0,38 (p = 0,056). Sin Lima y Callao: ρ = −0,34 (p = 0,11). Origen: `salidas/cruce_agroexportaciones.json`. Los p-valores se calculan con permutaciones sobre 25 puntos y no prueban nada causal.
5. **La pobreza varía mucho entre departamentos.** Nacional: 27,6 % (hogares, `factor07 × mieperho`). Cajamarca tiene 45,0 % (IC 95 %: 40,9-49,2) e Ica 6,0 % (IC 95 %: 4,2-7,9). Origen: `salidas/validacion.txt` y `salidas/indicadores.csv`.

**Contradicción que conviene tener presente.** La comparación de grupos encuentra una diferencia distinguible (resultado 3), pero la correlación de rangos de los 25 departamentos no llega a la significancia convencional (resultado 4). Ambas lecturas son compatibles: la diferencia se apoya en cuatro o cinco departamentos costeros con pobreza baja (en especial Ica, 6,0 %), mientras que entre los departamentos con poca agroexportación la pobreza va de 11,0 % (Moquegua) a 45,0 % (Cajamarca). Lima y La Libertad, dos de los cinco primeros, tienen pobreza cercana al promedio nacional (27,1 % y 30,2 %). La relación no es uniforme en los 25 departamentos.

## 4. Visualizaciones

![Agroexportaciones nacionales 2020-2024, BCRP](../figuras/agroexportaciones_bcrp.png)

![Pobreza monetaria por departamento, ENAHO 2024](../figuras/pobreza_departamento.png)

![Mapa de la pobreza monetaria por departamento, ENAHO 2024](../mapas/pobreza_departamento.png)

![Agroexportaciones 2022 y pobreza 2024 por departamento](../figuras/cruce_agroexportaciones.png)

## 5. Interpretación

- El crecimiento de las agroexportaciones fue sostenido en el periodo, y a precios corrientes. No puedo separar cuánto se debe a mayores cantidades y cuánto a precios.
- El valor exportado se concentra en la costa norte y central. Esos departamentos tienden a mostrar menos pobreza monetaria que el resto, sobre todo Ica y Lambayeque, pero no es un patrón que se repita en todos: Lima, La Libertad y Piura están cerca o por encima del promedio nacional.
- La asociación es compatible con varias explicaciones: diferencias previas de desarrollo, urbanización, otros sectores económicos o la composición del empleo. Estos datos no permiten decir que la agroexportación reduzca la pobreza ni que lo contrario.
- El valor se registra en el departamento de origen declarado, que no siempre es donde vive quien trabaja en la cadena exportadora.

## 6. Limitaciones

- **Cobertura temporal.** Las series departamentales del BCRP (`RD*BA`) solo tienen datos de 2020 a 2022 (actualizadas el 2024-12-20, según el catálogo). No hay datos departamentales de 2023 ni 2024, y no se interpolaron ni se estimaron. Por eso el cruce usa 2022, como pide la pregunta, y no se puede ver la evolución departamental hasta 2024. La serie nacional sí llega a 2024.
- **Años distintos.** Las exportaciones son de 2022 y la pobreza de 2024: no se midió la pobreza de 2022 ni su cambio.
- **Calidad de la ENAHO.** Ica (CV 15,6 %), Moquegua (16,2 %) y Madre de Dios (19,5 %) superan el 15 % de CV: sus cifras de pobreza son solo referenciales. Ica es parte del grupo de mayores agroexportadores, así que el resultado 3 depende en parte de una cifra referencial. Tacna (11,9 %) y Lambayeque (13,3 %) están por debajo del umbral.
- **Alcance.** Son 25 observaciones. La ENAHO es una muestra con representatividad departamental, y se comparan cifras con error de muestreo. Las exportaciones están en dólares corrientes, no en volumen. Solo se cubre el sector agropecuario no tradicional, no el empleo ni el ingreso agrícola.
- **Atribución territorial.** La serie «sin ubigeo» (`RD41389BA`) no tiene departamento; en 2022 la suma de los 25 departamentos coincide con el total nacional, por lo que el contraste muestra `fuera_de_departamentos` = 0,0.

## 7. Reproducibilidad

**Archivos.** `informes/plan.md`, `informes/informe_final.md`, `salidas/bcrp/agroexportaciones_nacional.csv`, `salidas/bcrp/agroexportaciones_departamento.csv`, `salidas/agroexportaciones_anual.csv`, `salidas/cruce_agroexportaciones.csv`, `salidas/cruce_agroexportaciones.json`, `salidas/validacion.txt`, `salidas/validacion_mapa.txt`, `salidas/comparacion_mapa.csv`, `salidas/indicadores.csv`, `figuras/agroexportaciones_bcrp.png`, `figuras/pobreza_departamento.png`, `figuras/cruce_agroexportaciones.png`, `mapas/pobreza_departamento.png`.

**Validaciones.** `salidas/validacion.txt`: RESULTADO: APROBADA (25 aprobadas, 0 fallidas; pobreza nacional 27,58 % frente a 27,6 % del INEI). `salidas/validacion_mapa.txt`: RESULTADO: APROBADO (25 de 25 unidades; diferencia máxima 0,05 pp frente a la Sesión 16).

**Comandos** (desde `tarea_4/`; `<skills>` = `.claude/skills`):

```bash
# MCP bcrp: guardar_series (PM40050BA) -> salidas/bcrp/agroexportaciones_nacional.csv, 2020-2024
# MCP bcrp: guardar_series (26 series RD*BA) -> salidas/bcrp/agroexportaciones_departamento.csv, 2020-2024
uv run <skills>/limpiando-enaho/scripts/limpiar.py
uv run <skills>/graficando-enaho/scripts/graficar.py --por departamento
uv run <skills>/mapeando-enaho/scripts/mapear.py
uv run <skills>/investigando-peru/scripts/graficar_bcrp.py --datos salidas/bcrp/agroexportaciones_nacional.csv --desde 2020 --hasta 2024 --tema agroexportaciones --unidad "millones de US$" --etiqueta PM40050BA="Agroexportaciones no tradicionales"
uv run <skills>/investigando-peru/scripts/cruzar.py --datos salidas/bcrp/agroexportaciones_departamento.csv --nacional salidas/agroexportaciones_anual.csv --anio 2022 --tema agroexportaciones --unidad "millones de US$"
```

### Origen de las cifras

| Afirmación | Cifra | Archivo o serie |
|---|---|---|
| Agroexportaciones 2020 | 6 735,4 millones de US$ FOB | `PM40050BA`, `salidas/agroexportaciones_anual.csv` |
| Agroexportaciones 2024 | 11 096,2 millones de US$ FOB | `PM40050BA`, `salidas/agroexportaciones_anual.csv` |
| Variación 2020-2024 | +64,7 % | `PM40050BA`, herramienta `resumen` |
| Agroexportaciones 2021, 2022 y 2023 | 7 868,0; 8 367,7; 9 169,0 millones de US$ | `salidas/agroexportaciones_anual.csv` |
| Participación de los cinco primeros, 2022 | 85,6 % | `salidas/cruce_agroexportaciones.json` |
| Valor de La Libertad, Lima, Ica, Piura y Lambayeque, 2022 | 1 857,7; 1 633,8; 1 567,8; 1 259,2; 844,1 millones de US$ | `salidas/cruce_agroexportaciones.csv` (`RD41168BA`, `RD41202BA`, `RD41134BA`, `RD41287BA`, `RD41185BA`) |
| Suma departamental frente al total nacional | 8 367,7 frente a 8 367,7; −0,0006 % | `contraste_con_total_nacional`, `salidas/cruce_agroexportaciones.json` |
| Pobreza de los cinco primeros frente al resto | 26,0 % frente a 29,3 %; −3,3 pp (IC 95 %: −5,3 a −1,3) | `comparacion_primeros`, `salidas/cruce_agroexportaciones.json` |
| Igual, sin Lima y Callao | 23,8 % frente a 29,4 %; −5,7 pp (IC 95 %: −7,7 a −3,7) | `comparacion_sin_lima_callao`, `salidas/cruce_agroexportaciones.json` |
| Correlaciones de Spearman | −0,26 (p = 0,22); −0,38 (p = 0,056); −0,34 (p = 0,11) | `spearman_*`, `salidas/cruce_agroexportaciones.json` |
| Pobreza nacional 2024 (hogares) | 27,6 % (27,58 %) | `salidas/validacion.txt` |
| Pobreza en Cajamarca e Ica, 2024 | 45,0 % (CV 4,7 %); 6,0 % (CV 15,6 %) | `salidas/indicadores.csv`; salida de `graficar.py --por departamento` |
| CV de Moquegua y Madre de Dios | 16,2 %; 19,5 % | `salidas/indicadores.csv`; salida de `graficar.py --por departamento` |
| Pobreza en Lima y La Libertad, 2024 | 27,1 %; 30,2 % | `salidas/cruce_agroexportaciones.csv` |
| Series departamentales solo hasta 2022 | 2020-2022, n = 3 por serie | respuesta de `guardar_series`, 26 series `RD*BA` |
