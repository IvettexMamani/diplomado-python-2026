# Plan de investigación

## Pregunta
¿Cómo evolucionaron las agroexportaciones peruanas entre 2020 y 2024, y los departamentos que más agroexportaban en 2022 tenían menos pobreza monetaria en 2024?

## Objetivo
1. Describir la evolución anual 2020-2024 de las agroexportaciones nacionales (millones de US$ FOB, corrientes).
2. Medir la asociación entre las agroexportaciones departamentales de 2022 y la pobreza monetaria departamental de 2024 (ENAHO 2024).

## Delimitación
- Agroexportaciones = productos tradicionales agrícolas + productos no tradicionales agropecuarios. Quedan fuera las exportaciones pesqueras, mineras, textiles y otras no tradicionales. Los productos agroindustriales clasificados fuera de «agropecuarios» tampoco entran.
- Valores FOB en dólares corrientes: no se mide volumen ni precio.
- Pobreza monetaria: personas en hogares pobres, ENAHO 2024, ponderada con factor de expansión, 25 unidades (Lima y Callao separados).
- Los años difieren (exportaciones 2022, pobreza 2024): es una asociación entre niveles de años distintos.

## Indicadores y fuentes
| Indicador | Fuente | Series |
|---|---|---|
| Agroexportaciones nacionales | BCRP, Balanza comercial (anual) | PM40046BA (tradicionales agrícolas) + PM40050BA (no tradicionales agropecuarios) |
| Agroexportaciones departamentales | BCRP, información regional (anual) | 25 series RD… de tradicionales agrícolas + 25 de no tradicionales agropecuarios, más «sin ubigeo» |
| Pobreza monetaria 2024 | INEI, ENAHO 2024, módulos 34 y 02 | salidas/ (Skills limpiando-enaho, graficando-enaho, mapeando-enaho) |

## Pasos
1. Buscar y guardar las series con el MCP del BCRP (`guardar_series`) y revisar `sin_datos` y el periodo real.
2. Procesar la ENAHO con las Skills `limpiando-enaho` (validación), `graficando-enaho` y `mapeando-enaho`.
3. Graficar la evolución nacional con `graficar_bcrp.py` y cruzar con `cruzar.py` (año 2022).
4. Contrastar con `validacion.txt`, `validacion_mapa.txt` y el total nacional.
5. Escribir `informes/informe_final.md`.

## Riesgos previsibles
- Las series departamentales llegan solo hasta 2022 (verificado en `guardar_series`): no hay desglose departamental 2023-2024.
- Lima y Callao pueden concentrar exportaciones por razones de domicilio fiscal o puerto; el criterio de asignación del BCRP no está en la ficha consultada.
- Parte de las exportaciones queda «sin ubigeo» y no puede asignarse a un departamento.
- Con 25 unidades y años distintos, la correlación es frágil y sensible a valores extremos.
- Si la validación de la ENAHO falla, no se escribe el informe.
