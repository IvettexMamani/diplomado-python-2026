# Verificación de cifras del informe final

Generado por `informes/verificar.py` el 2026-11-06. El script no importa nada del proyecto: recalcula con las series
mensuales del BCRP, no con las anuales que usó el agente, y con los `.dta` originales de la ENAHO.

13 de 13 afirmaciones coinciden.

| Afirmación del informe | Fuente | En el informe | Calculado | Diferencia | ¿Coincide? | Procedimiento |
|---|---|---:|---:|---:|---|---|
| Agroexportaciones de 2024, millones de US$ | BCRP | 12,325.60 | 12,325.557 | -0.043 | Sí | Suma de los 12 meses de PN38744BM y PN38740BM, API del BCRP |
| Agroexportaciones de 2020, millones de US$ | BCRP | 7,466.50 | 7,466.521 | +0.021 | Sí | Suma de los 12 meses de PN38744BM y PN38740BM, API del BCRP |
| Crecimiento 2020-2024, % | BCRP | 65.08 | 65.078 | -0.002 | Sí | Calculado con las dos sumas anteriores |
| La Libertad en 2022, millones de US$ | BCRP | 1,924.30 | 1,924.330 | +0.030 | Sí | Suma de los 12 meses de RD38347BM y RD38343BM |
| Suma de los 25 departamentos en 2022, millones de US$ | BCRP | 9,721.88 | 9,721.879 | -0.001 | Sí | Suma directa de las series anuales guardadas, con el departamento tomado del código |
| Pobreza nacional 2024, % | ENAHO | 27.58 | 27.579 | -0.001 | Sí | Media ponderada desde sumaria-2024.dta |
| Pobreza de Cajamarca, % | ENAHO | 45.00 | 45.007 | +0.007 | Sí | Media ponderada desde sumaria-2024.dta; coincide con la cifra publicada por el INEI |
| Pobreza de Ica, % | ENAHO | 6.00 | 6.014 | +0.014 | Sí | Media ponderada desde sumaria-2024.dta |
| Pobreza de los 5 primeros, % | Ambas | 26.00 | 25.955 | -0.045 | Sí | Media ponderada desde sumaria-2024.dta |
| Pobreza del resto, % | Ambas | 29.30 | 29.263 | -0.037 | Sí | Media ponderada desde sumaria-2024.dta |
| Sin Lima y Callao: 5 primeros, % | Ambas | 28.10 | 28.134 | +0.034 | Sí | Media ponderada desde sumaria-2024.dta |
| Sin Lima y Callao: resto, % | Ambas | 27.20 | 27.175 | -0.025 | Sí | Media ponderada desde sumaria-2024.dta |
| Correlación de rangos, 25 departamentos | Ambas | -0.17 | -0.173 | -0.003 | Sí | statistics.correlation(method="ranked") |

Las tolerancias son de redondeo: la mitad del último decimal publicado en el informe, o algo menos para las cifras con más
decimales.

## Comprobación manual

La estudiante abrió estas fuentes y confirmó cada cifra el 2026-11-06. El agente no puede hacer este paso: consiste en mirar las
fuentes oficiales con los propios ojos.

- [x] **BCRP, 2024.** Abrir [la tabla de no tradicionales agropecuarias](https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/PM40050BA/html/2020/2024/)
  y [la de tradicionales agrícolas](https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/PM40046BA/html/2020/2024/). Las tablas redondean al entero:
  sumar con calculadora 11 096 + 1 229 da 12 325, frente a 12 325,6 millones de US$ del informe.
- [x] **BCRP, por departamento.** Abrir [la serie de Ica, pedida de 2020 a 2024](https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/RD41134BA/html/2020/2024/)
  y comprobar que 2022 muestra 1 568 millones de US$, redondeo de 1 567,8, y que la tabla termina ahí: no hay 2023 ni 2024.
- [x] **ENAHO e INEI.** Abrir [la nota del INEI](https://www.gob.pe/institucion/inei/noticias/1164173-pobreza-monetaria-afecto-al-27-6-de-la-poblacion-del-pais-en-el-ano-2024)
  y comprobar que la pobreza nacional de 2024 es 27,6 %. Luego abrir `salidas/comparacion_mapa.csv` y ver que Cajamarca
  tiene 45,01 % y que la referencia de la Sesión 16 dice 45,0 %.

## Correcciones hechas al informe

El agente generó el informe. La revisión encontró tres frases sin respaldo y se corrigieron a mano. Ninguna cifra cambió:

| Sección | Decía | Dice ahora | Motivo |
|---|---|---|---|
| 6, Alcance | «las agroexportaciones se registran por departamento de origen asignado por el BCRP» | «las agroexportaciones se atribuyen a cada departamento con un criterio que las fichas no explican» | Contradecía la propia incógnita metodológica de la misma sección |
| 6, Definición | «quedan fuera productos agroindustriales clasificados en otros grupos» | «queda fuera cualquier producto de origen agrario clasificado en otro grupo» | No se comprobó que existan esos productos |
| 5, Interpretación | «Piura y La Libertad combinan alta agroexportación y pobreza por encima del promedio nacional» | Añade que La Libertad no se distingue del promedio con 95 % de confianza | El gráfico por departamento lo muestra así |

## Qué cambió entre las dos corridas del agente

La [primera corrida](../evidencias_ia/integracion/primera_corrida.md) y su
[informe](../evidencias_ia/integracion/primera_corrida_informe.md) se conservan como evidencia. Tenía cuatro fallas, y
la revisión humana las detectó:

| Falla | Corrección |
|---|---|
| Corrió los scripts de las Skills de la ENAHO sin invocarlas: la ejecución no dejaba constancia de ninguna | `investigando-peru` exige la herramienta `Skill`. En la segunda corrida se activaron las tres |
| Definió agroexportaciones solo como no tradicionales, sin café ni azúcar, y sin Lima y Callao concluía −5,7 puntos | La pregunta fija la definición completa, y `cruzar.py` repite el cruce por producto. Con la definición completa, esa diferencia desaparece |
| Afirmó que el valor se registra «en el departamento de origen declarado», sin fuente | La Skill obliga a declarar esas incógnitas |
| Dijo que las series regionales cubren «de 2020 a 2022», que era el rango pedido | `guardar_series` devuelve `inicio_catalogo`, y el informe dice de 2005 a 2022 |

También se declara esta desviación: la Skill pide escribir el plan antes de consultar datos, y en la corrida final
`informes/plan.md` se escribió después de buscar y guardar las series del BCRP, antes de procesar la ENAHO.
