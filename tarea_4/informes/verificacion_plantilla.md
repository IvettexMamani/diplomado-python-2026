# Verificación de cifras del informe final

Generado por `informes/verificar.py` el {{FECHA}}. El script no importa nada del proyecto: recalcula con las series
mensuales del BCRP, no con las anuales que usó el agente, y con los `.dta` originales de la ENAHO.

{{RESUMEN}}

{{TABLA}}

Las tolerancias son de redondeo: la mitad del último decimal publicado en el informe, o algo menos para las cifras con más
decimales.

## Comprobación manual

Estos pasos no los puede hacer el agente: son para abrir las fuentes y mirar la cifra con los propios ojos. Marcar cada
casilla después de hacerlo.

- [ ] **BCRP, 2024.** Abrir [la tabla de no tradicionales agropecuarias]({{WEB}}/anuales/resultados/PM40050BA/html/2020/2024/)
  y [la de tradicionales agrícolas]({{WEB}}/anuales/resultados/PM40046BA/html/2020/2024/). Las tablas redondean al entero:
  sumar con calculadora 11 096 + 1 229 da 12 325, frente a 12 325,6 millones de US$ del informe.
- [ ] **BCRP, por departamento.** Abrir [la serie de Ica]({{WEB}}/anuales/resultados/RD41134BA/html/2020/2022/) y comprobar
  que 2022 muestra 1 568 millones de US$, redondeo de 1 567,8. El rango se puede ampliar en la página para ver que la
  serie no llega a 2023.
- [ ] **ENAHO e INEI.** Abrir [la nota del INEI](https://cdna.www.gob.pe/en/institucion/inei/noticias/1164173-pobreza-monetaria-afecto-al-27-6-de-la-poblacion-del-pais-en-el-ano-2024)
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
