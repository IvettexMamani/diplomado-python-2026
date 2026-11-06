# Comparación: Claude Code sin y con MCP y Skills

¿Mejoran las respuestas con el servidor MCP del BCRP y las Skills de la ENAHO? **Sí, en lo que depende de los microdatos:
9 de 10 correctas frente a 6.** En las cifras ya publicadas, en cambio, la búsqueda web alcanzó
la misma exactitud. Con 10 preguntas y una sola corrida, esto es una señal y no una prueba.

Estas tablas las genera `uv run evaluacion/evaluar.py --resumir` a partir de [`resultados.csv`](resultados.csv).

## Resultados

| Modo | Correctas | Parciales | Incorrectas | Sin respuesta | Errores | Tiempo promedio | Costo total |
|---|---:|---:|---:|---:|---:|---:|---:|
| A, sin MCP ni Skills | 6 | 2 | 0 | 2 | 0 | 44.6 s | US$ 0.70 |
| B, con MCP y Skills | 9 | 1 | 0 | 0 | 0 | 26.4 s | US$ 0.65 |

| Comparación | Resultado |
|---|---|
| Preguntas que mejoraron con MCP y Skills | 3: P07, P08, P09 |
| Preguntas que empeoraron | 0: ninguna |
| Preguntas iguales | 7: P01, P02, P03, P04, P05, P06, P10 |

| Pregunta | Tipo | Esperada | Modo A | Resultado A | Modo B | Resultado B | Herramientas de B |
|---|---|---|---|---|---|---|---|
| P01 | BCRP | 1.9663 | 1.97 | correcta | 1.97 | correcta | buscar_series serie |
| P02 | BCRP | 3.7553 | 3.7553 | correcta | 3.7553 | correcta | buscar_series resumen |
| P03 | BCRP | 9168.97 | 9169 | correcta | 9168.97 | correcta | buscar_series serie |
| P04 | BCRP | 0.0379 | 0.038 | correcta | 0.038 | correcta | buscar_series correlacion |
| P05 | ENAHO | 27.58 | 27.6 | correcta | 27.6 | correcta | WebSearch |
| P06 | ENAHO | 18.54 | 18.5 | correcta | 18.5 | correcta | Bash Skill |
| P07 | ENAHO | 37.52 | sin dato | sin_respuesta | 37.52 | correcta | Bash Skill |
| P08 | ENAHO | 42.92, 37.81 | sin dato, sin dato | sin_respuesta | 42.92, 37.81 | correcta | Bash Skill |
| P09 | Combinada | La Libertad, 65.08, 30.19 | 65.1, 31.9 | parcial | 65.1, 30.2 | correcta | Bash Skill buscar_series serie |
| P10 | Combinada | Cajamarca, 45.01, 1884.97 | 45, 65835 | parcial | 45, 66339.2 | parcial | Bash Skill buscar_series serie |

## Qué se comparó

Las mismas 10 preguntas, con el mismo modelo (Sonnet) y las mismas instrucciones, una por sesión independiente de
`claude -p`, sin memoria entre sesiones.

| | Modo A: sin MCP ni Skills | Modo B: con MCP y Skills |
|---|---|---|
| Herramientas habilitadas | WebSearch y WebFetch | WebSearch y WebFetch, más el MCP `bcrp`, sus recursos, Skill, Read y Bash |
| Carpeta | Vacía, fuera del repositorio | Copia del proyecto sin `evaluacion/`, `informes/`, `evidencias_ia/` ni el README |
| Skills del proyecto | No disponibles; comandos desactivados | Las 4 |
| GitHub | Bloqueado | Bloqueado |

- **Por qué web en ambos:** el modo B es el modo A más los componentes del proyecto, y Read y Bash, sin los que no pueden
  correr. Solo cambia eso. Con un modo A sin ninguna herramienta, la comparación habría favorecido al proyecto.
- **Por qué sin archivos ni terminal en A:** así no puede llegar a las respuestas guardadas en la laptop.
- **Por qué sin GitHub:** el repositorio público contiene las respuestas.
- **Control:** cada corrida se revisa en busca de rutas o términos del proyecto (columna `contaminacion`). En ninguna de
  las 20 apareció alguno.

**Respuestas esperadas.** [`construir_preguntas.py`](construir_preguntas.py) las calcula sin usar código del proyecto: la API
del BCRP y los `.dta` originales del INEI. Se publicaron con las reglas en el commit `ee0ce5c`, antes de la primera
corrida, y no cambiaron después. Las preguntas P07, P08 y P09 coinciden con lo calculado por el proyecto por otro camino.

**Tolerancias.** Fijas por pregunta en `preguntas.csv`: 0,02 puntos en inflación, S/ 0,002 en el tipo de cambio, 0,02 en la
correlación, 0,1 puntos en pobreza y crecimiento, y US$ 5 millones en exportaciones.

**Calificación.**

| Resultado | Preguntas simples | Preguntas combinadas |
|---|---|---|
| Correcta | Todos los valores dentro de la tolerancia | Datos correctos e interpretación coherente |
| Parcial | Algún valor correcto | Solo una de las dos cosas |
| Incorrecta | Ningún valor correcto | Ninguna |
| Sin respuesta | Dijo que no puede obtener el dato | Lo mismo, sin interpretación válida |

La interpretación es coherente si niega que los datos prueben una relación causal y da al menos un motivo. La regla
automática se revisó a mano en las 4 respuestas combinadas y coincidió, así que `revision_manual.csv` no existe: ninguna
nota se cambió.

## Principales errores

| Pregunta | Modo | Qué pasó |
|---|---|---|
| P10 | A y B | Los dos dieron el total nacional (65 835 y 66 339,2) en vez de lo que exportó Cajamarca (1 884,97). Ambos lo dijeron con claridad, pero no es lo que se pedía. Que dos sesiones independientes coincidan sugiere que la redacción era ambigua. La pregunta y la nota no se cambiaron |
| P09 | A | Dio 31,9 % de pobreza para La Libertad, tomado de una fuente secundaria, porque no pudo abrir el informe del INEI. La cifra correcta es 30,19 % |
| P07 y P08 | A | No dio cifra: dijo que necesitaba procesar microdatos. Es la conducta correcta sin esas herramientas, y no inventó nada |
| P08 | B | Las cifras son correctas, pero añadió que la diferencia entre mujeres y hombres no está probada porque los intervalos se cruzan. Esa regla no vale: el intervalo de la diferencia va de 1,9 a 8,3 puntos. La calificación no lo penaliza porque esta pregunta no pedía interpretación |
| P09 | B | Es correcta, pero eligió al mayor exportador solo con los no tradicionales, aunque la pregunta suma ambos grupos. El resultado no cambia |
| P05 | B | No activó ninguna Skill: respondió con la nota del INEI. Es correcta, pero no aprovechó el proyecto |

## Lo que muestran los resultados

1. **La diferencia está en los microdatos.** P07 y P08 no se publican: solo se obtienen procesando la ENAHO, y solo el
   modo B pudo. Esas preguntas se eligieron por eso, así que favorecen al proyecto por diseño.
2. **En datos públicos, la web bastó.** El modo A acertó las 4 preguntas del BCRP. Sabía usar la API pública del BCRP y sumó
   y calculó dentro del modelo, «a mano», incluida la correlación.
3. **Un cálculo correcto no es lo mismo que uno comprobable.** Esos cálculos de A acertaron, pero no se pueden repetir ni
   auditar. En B, la cifra sale de código: `resumen` y `correlacion` en el BCRP, `estimar.py` en la ENAHO.
4. **B fue más rápido.** Tardó 41 % menos en promedio, con un costo total similar. En A, el tiempo se va en buscar,
   y a veces no encuentra la fuente primaria, como en P09.
5. **Con fuentes secundarias aparecen los errores.** La única cifra equivocada de A que no se explica por la redacción vino
   de un documento que citaba al INEI.

## Conclusión

El MCP y las Skills mejoran las respuestas cuando hay que procesar datos que nadie publicó, y hacen cada cifra verificable.
No mejoran la exactitud en cifras que ya están en internet, salvo en velocidad y trazabilidad.

La mejora no es concluyente en términos estadísticos: 3 mejoras y 0 empeoramientos en 10 preguntas dan p = 0,25 en una
prueba de signos.

## Limitaciones

- Son 10 preguntas y una corrida por modo. Claude no es determinista: otra corrida podría cambiar alguna nota.
- Las preguntas las diseñó quien construyó el sistema, y dos se eligieron porque requieren microdatos.
- El modo B partió con las bases ya procesadas. Por eso no refleja el tiempo de limpiar la ENAHO.
- El bloqueo de GitHub cubre WebFetch. WebSearch podría mostrar fragmentos de un repositorio, aunque ninguna transcripción
  lo indica.
- P10 mide en parte la ambigüedad de su redacción, no solo la capacidad del agente.

## Reproducir

```bash
uv run evaluacion/construir_preguntas.py     # recalcula las respuestas esperadas
uv run evaluacion/evaluar.py --preparar      # crea las dos carpetas aisladas
uv run evaluacion/evaluar.py --modo A
uv run evaluacion/evaluar.py --modo B
uv run evaluacion/evaluar.py --resumir       # califica y escribe resultados.csv y este archivo
```

`evaluar.py` salta las corridas que ya existen en `evidencias_ia/evaluacion/`. Para repetirlas, hay que mover esa carpeta. Cada
corrida guarda ahí su transcripción (`.jsonl`), un resumen legible (`.md`) y sus datos (`.json`).
