# Tarea 4 · Agente de investigación socioeconómica del Perú

**Pregunta guía:** ¿puede un agente de IA investigar la realidad socioeconómica peruana con datos oficiales del INEI
(ENAHO 2024) y del BCRP, combinando servidores MCP, Skills de Claude Code y análisis reproducible?

| Parte | Componente | Estado |
|---|---|---|
| 1 | Servidor MCP del BCRP (`mcp/`) | ✅ Terminada: 10 de 10 pruebas aprobadas |
| 2 | Skills para limpiar, graficar y mapear la ENAHO (`.claude/skills/`) | Pendiente |
| 3 | Integración y agente de investigación (`informes/`) | Pendiente |
| 4 | Evaluación, documentación y reproducibilidad (`evaluacion/`) | Pendiente |

## Instalación

Se necesitan [uv](https://docs.astral.sh/uv/), [Claude Code](https://claude.com/claude-code) con la sesión iniciada e
internet. No se usa ninguna clave de API.

```bash
cd tarea_4
uv sync                 # crea .venv con FastMCP 4, pandas, httpx y truststore (fijados en uv.lock)
uv run pytest -q        # 10 passed
```

Si hay un antivirus o proxy que inspecciona HTTPS (por ejemplo, Avast), usen `uv sync --system-certs`. El servidor ya
usa los certificados del sistema mediante `truststore`, así que no necesita nada más.

La primera vez, el servidor baja el catálogo oficial del BCRP (17 167 series, unos 7 MB) a `datos/bcrp/`. Git ignora
esa carpeta, y basta con borrarla para volver a bajar el catálogo.

## Estructura

```
tarea_4/
├── README.md
├── pyproject.toml · uv.lock      # entorno reproducible con uv
├── .mcp.json                     # conecta el servidor bcrp a Claude Code
├── .gitignore                    # ignora .venv/ y datos/
├── mcp/
│   ├── server.py                 # servidor MCP del BCRP (FastMCP)
│   ├── test_server.py            # 8 pruebas originales de la Sesión 04 + 2 propias
│   └── demo_claude.py            # demostración reproducible con claude -p
└── evidencias_ia/
    └── mcp/                      # transcripciones de las demostraciones en Claude Code
```

---

## Parte 1 · Servidor MCP del BCRP

`mcp/server.py` parte del proyecto de la
[Sesión 04](https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/04-mcp-claude-code/proyecto). Ahí,
`buscar_series` ya venía hecha y se mantiene igual. Lo demás se agregó en esta tarea. Todas las cuentas las hace
Python con pandas, y el modelo solo lee los resultados. Así cada cifra sale de una llamada que se puede repetir.

### Arquitectura

```
Claude Code ──stdio──► mcp/server.py (FastMCP "bcrp")
                          │
                          ├─ catálogo: estadisticas.bcrp.gob.pe/estadisticas/series/metadata  → datos/bcrp/ (caché en disco)
                          └─ datos:    estadisticas.bcrp.gob.pe/estadisticas/series/api/{código}/json/{desde}/{hasta}
                                       (caché en memoria; reintenta con 2, 4, 8 y 16 s si el BCRP devuelve HTML)
```

### Herramientas

| Herramienta | Qué hace | Ejemplo de argumentos |
|---|---|---|
| `buscar_series` | Busca por palabras en la categoría, el grupo y el nombre de las 17 167 series. Devuelve primero las vigentes. También acepta un código | `texto="ipc 12 meses"` |
| `serie` | Descarga los datos de un periodo, sin los `n.d.`. Devuelve los periodos como `2025-01`, `2026-10-01`, `2025-T1` o `2025` | `codigo="PN01271PM", desde="2025-01", hasta="2025-12"` |
| `resumen` | Calcula el primer y último dato, el cambio, la variación %, el promedio, la desviación estándar, el máximo y el mínimo (cada extremo con su periodo). Si la serie ya es una tasa, avisa que el cambio está en puntos porcentuales | `codigo="PN01273PM", desde="2025-12", hasta="2026-09"` |
| **`correlacion`** (propia) | Calcula la correlación entre dos series, con periodos alineados, faltantes tratados y rezago opcional | `codigo_a="PN01273PM", codigo_b="PD04638PD", desde="2024-01", hasta="2025-12"` |

Todas las herramientas devuelven tres datos de procedencia:

- `fuente`: la URL de la API.
- `fuente_web`: la tabla del BCRP donde una persona puede comprobar la cifra.
- `fuente_original`: quién produce el dato, por ejemplo INEI o SBS.

Las URL citan el rango de los datos devueltos y no el pedido, así que al abrirlas después muestran las mismas cifras.

Las fechas se aceptan como `2025`, `2025-T1`, `2025-03` o `2025-03-15`, y se adaptan a la frecuencia de cada serie.
Por ejemplo, `desde="2025"` en una serie diaria empieza el 1 de enero. Las fechas imposibles, como `2025-13` o
`2025-02-30`, dan un error claro; pandas, en cambio, convertía `2025-13` en enero de 2026 sin avisar.

Otros errores también son claros:

- Un código inexistente da un `ToolError` que nombra el código.
- Un periodo sin datos dice desde cuándo hay datos.
- Una consulta de más de 3 000 datos sugiere usar `resumen` o `correlacion`, para no llenar el contexto del modelo.

### Herramienta propia: `correlacion`

**Para qué sirve.** Responde preguntas que las otras tres herramientas no resuelven, como *«¿se mueven juntos el tipo
de cambio y la inflación?»* o *«¿las expectativas de inflación se anticipan a la inflación?»*. Hacerlo a mano exige
varios pasos donde un modelo de lenguaje suele equivocarse: alinear frecuencias distintas, emparejar periodos y descartar
faltantes. La herramienta hace estos pasos, en orden:

1. **Alinea frecuencias.** Si una serie es diaria y la otra mensual, lleva la más fina a la más gruesa con el promedio de
   cada periodo, y avisa cuántos datos promedió.
2. **Trata los faltantes.** Empareja periodo con periodo sobre un calendario completo. Descarta los periodos que no
   tienen dato en alguna de las dos series y dice cuántos descartó de cada una.
3. **Aplica el rezago.** `rezago=k` compara A en *t* con B en *t − k* y baja B desde *k* periodos antes, para no perder
   pares.
4. **Calcula.** Devuelve Pearson con su intervalo de confianza al 95 % y su p-valor aproximados con la transformación de
   Fisher. También devuelve Spearman y la **correlación de las variaciones** periodo a periodo. Si los niveles están muy
   correlacionados pero las variaciones no, la herramienta advierte una posible correlación espuria por tendencia común.
5. **Recuerda los límites.** Siempre agrega que una correlación no prueba causalidad y que, en series de tiempo, el
   p-valor suele ser optimista.

Con 120 pares o menos, devuelve también los datos emparejados para que se puedan revisar.

**Cómo se validó.** Las dos pruebas propias calculan la verdad por su cuenta, con `statistics.correlation` de la
biblioteca estándar sobre los datos de `serie`, sin reutilizar el código de pandas del servidor:

| Prueba | Qué comprueba |
|---|---|
| `test_correlacion_alinea_frecuencias_y_coincide_con_un_calculo_independiente` | Toma la inflación a 12 meses (mensual) y el tipo de cambio venta (diario) de 2024-2025. Comprueba que la frecuencia común es la mensual, que hay 24 pares, que el promedio mensual de los días coincide, que Pearson coincide con el cálculo independiente (±0,0001), que el resultado es simétrico y que el intervalo contiene la estimación |
| `test_correlacion_trata_faltantes_y_rezago` | El tipo de cambio diario empieza el 2 de enero de 1997, así que entre 1996-07 y 1997-12 descarta exactamente 6 meses. Con `rezago=1` sobre la misma serie da la autocorrelación de orden 1. Con menos de 4 pares, la herramienta da un error en vez de un número |

Además, se comprobó que las pruebas detectan errores reales. Se introdujeron tres fallas a propósito en una copia del
servidor, y cada una hizo fallar una prueba:

- usar el último dato del mes en vez del promedio;
- invertir el signo del rezago;
- no ampliar el rango de B cuando hay rezago.

### Recurso y prompt

| Tipo | Nombre | Qué da |
|---|---|---|
| Recurso (plantilla) | `bcrp://serie/{codigo}` | Ficha de la serie: nombre, categoría, grupo de serie, grupo de publicación, área del BCRP que la publica, fuente original, frecuencia, inicio de los datos, fecha de actualización, enlaces a la tabla web y a la API, y cómo citarla |
| Prompt | `informe(tema, desde="2024-01", hasta="")` | Guía para un informe breve: de 2 a 4 series, `resumen` para cada una, `correlacion` si el tema relaciona dos indicadores, nada de cuentas a mano, una tabla con código, periodo, cifra y unidad, tres hallazgos, limitaciones y fuentes |

### Conexión con Claude Code

`.mcp.json` registra el servidor con alcance de proyecto. Es equivalente a
`claude mcp add --scope project bcrp -- uv run --quiet mcp/server.py`:

```json
{ "mcpServers": { "bcrp": { "type": "stdio", "command": "uv", "args": ["run", "--quiet", "mcp/server.py"], "env": {} } } }
```

Abran `claude` **dentro de `tarea_4/`** y aprueben el servidor `bcrp` cuando se lo pida. Luego prueben:

1. `/mcp`: muestra `bcrp` conectado, con sus 4 herramientas.
2. Una pregunta: *«¿Cuál fue la inflación de Lima a 12 meses en setiembre de 2026?»*. Claude debería llamar a
   `buscar_series` y luego a `resumen` o `serie`, en vez de calcular.
3. El recurso: `@bcrp:bcrp://serie/PN01273PM ¿qué área del BCRP publica esta serie?`
4. El prompt: `/mcp__bcrp__informe inflación 2025-01`

### Demostración reproducible

`mcp/demo_claude.py` corre `claude -p` sin terminal ni archivos (`--tools ""`) y con `bcrp` como único servidor MCP.
Así, cada cifra de la respuesta tiene que salir de una herramienta. El script guarda la transcripción completa (`.jsonl`)
y un resumen legible (`.md`) con cada llamada, sus argumentos, lo que devolvió y la respuesta final.

```bash
uv run mcp/demo_claude.py                                                            # pregunta de la tabla
MSYS_NO_PATHCONV=1 uv run mcp/demo_claude.py "/mcp__bcrp__informe inflación 2025-01" --nombre demo_prompt_informe
uv run mcp/demo_claude.py "Lee el recurso bcrp://serie/PN01273PM ..." --recursos --nombre demo_recurso
```

`MSYS_NO_PATHCONV=1` solo hace falta en Git Bash, que si no convierte `/mcp__...` en una ruta de Windows. En PowerShell
no se necesita.

Resultados del 4 de noviembre de 2026 con Sonnet:

| Demostración | Qué pide | Llamadas de Claude | Resultado |
|---|---|---|---|
| [`demo_claude_code`](evidencias_ia/mcp/demo_claude_code.md) | Evolución de la inflación interanual de Lima desde dic-2024 y si se movió con el tipo de cambio | `buscar_series` ×2 → `resumen` → `correlacion` | Inflación de 1,97 % (2024-12) a 4,55 % (2026-09), +2,58 p. p., máximo en 2026-09 (PN01273PM). Con el tipo de cambio diario PD04638PD promediado por mes, Pearson −0,47 en niveles y +0,65 en variaciones: Claude lo reporta como señales contradictorias y sin causalidad |
| [`demo_prompt_informe`](evidencias_ia/mcp/demo_prompt_informe.md) | El prompt `/mcp__bcrp__informe inflación 2025-01` | `buscar_series` ×3 → `resumen` ×4 → `correlacion` | Informe con tabla de códigos y periodos, 3 hallazgos (el alza viene del IPC no subyacente: de 0,43 % a 8,20 %), limitaciones y fuentes |
| [`demo_recurso`](evidencias_ia/mcp/demo_recurso.md) | Leer la ficha `bcrp://serie/PN01273PM` sin acceso a las herramientas | `ReadMcpResourceTool` | Área: Departamento de Estadísticas de Precios; fuente original: INEI; datos desde ene-1950; texto para citarla |

Las transcripciones se limpiaron: del evento inicial de Claude Code solo quedan el modelo, la versión, las
herramientas y los servidores MCP.

### Pruebas

```text
$ uv run pytest -v
mcp/test_server.py::test_buscar_encuentra_el_ipc PASSED
mcp/test_server.py::test_cuatro_herramientas_como_minimo PASSED
mcp/test_server.py::test_serie_mensual PASSED
mcp/test_server.py::test_serie_diaria PASSED
mcp/test_server.py::test_resumen_sin_cuentas_a_mano PASSED
mcp/test_server.py::test_codigo_inexistente_da_un_error_claro PASSED
mcp/test_server.py::test_un_recurso PASSED
mcp/test_server.py::test_un_prompt PASSED
mcp/test_server.py::test_correlacion_alinea_frecuencias_y_coincide_con_un_calculo_independiente PASSED
mcp/test_server.py::test_correlacion_trata_faltantes_y_rezago PASSED
10 passed
```

Las 8 pruebas originales son **idénticas byte a byte** a las de la Sesión 04: los primeros 2 455 bytes de
`mcp/test_server.py` coinciden con el archivo original (`cmp`). Las 2 propias van después, separadas por un
comentario. Ni siquiera el import cambió: `from server import mcp` funciona porque pytest agrega `mcp/` al `sys.path`
(`testpaths = ["mcp"]` en `pyproject.toml`). Las pruebas piden datos reales al BCRP, así que necesitan internet.

## Uso de IA

El servidor, las pruebas y esta documentación se desarrollaron con Claude Code (Claude Opus 5.5). La conversación
completa se exporta a `evidencias_ia/mcp/`.
