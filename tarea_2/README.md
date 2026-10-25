# Tarea 2 – OCR, transcripción y extracción con LLM

**Pregunta guía:** ¿pueden convertirse documentos escaneados y entrevistas en audio en un archivo de texto estructurado y buscable?

**App:** _ENLACE_APP_ (Streamlit Community Cloud)

Este trabajo convierte 25 documentos peruanos y 49 minutos de audio en texto con OCR y ASR. Luego mide cuánto se equivocan esos modelos y extrae con un LLM local campos estructurados en JSON. El dashboard permite buscar en los textos y comparar modelos, y no ejecuta modelos en vivo.

## Corpus, fuentes y licencias

| Corpus | Archivos | Fuente | Licencia | Fecha de acceso |
| :--- | :--- | :--- | :--- | :--- |
| Impresos | 8 páginas (`impreso1`–`8`) | Bases integradas de la AS N° 013-2024-INDECOPI-1, [buscador público del SEACE](https://prod2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml) | Texto oficial sin derecho de autor (D. Leg. 822, art. 9 b) | 2026-10-22 |
| Fotos de celular | 8 (`foto1`–`8`) | Directiva Ejecutiva Regional N° 002-2024-GR/GOB.REG.TACNA, fotografiada por la estudiante | Texto oficial sin derecho de autor; fotos propias | 2026-10-22 |
| Manuscritos | 9 (`manuscrito1`–`9`) | Wikimedia Commons, Biblioteca Nacional del Perú y otros (textos de 1580 a 1917: cartas, poemas, un tratado y una muestra caligráfica) | 4 en dominio público o CC0; 5 con fotografía con derechos reservados (uso académico local) | 2026-10-22 |
| Podcasts | 2 clips (27,9 min) | Fragmentos de dos videos de YouTube | Licencia estándar de YouTube: el audio no se publica | 2026-10-23 |
| Entrevistas | 9 clips (19,1 min) | Entrevistas de la estudiante a niños de un jardín, con consentimiento de sus padres | Grabación propia: el audio no se publica y el texto solo se publica seudonimizado | 2026-10-23 |
| Frases leídas | 12 clips (1,8 min) | [OpenSLR 73](https://www.openslr.org/73/), español peruano (Google) | CC BY-SA 4.0; Guevara-Rukoz et al. (2020), LREC | 2026-10-23 |

El detalle por archivo está en [`datos/fuentes.csv`](datos/fuentes.csv). La extracción se hizo el 2026-10-23 y la evaluación el 2026-10-25.

## Método

1. **Extracción** ([`01_extraccion.ipynb`](01_extraccion.ipynb)):
   - OCR con PaddleOCR 3.7 (PP-OCRv6 medium).
   - ASR con faster-whisper large-v3-turbo, VAD Silero y diarización por huellas de voz.
   - Limpieza y seudonimización de nombres de personas vivas: spaCy, con revisión manual y reemplazo difuso.
2. **Evaluación** ([`02_evaluacion.ipynb`](02_evaluacion.ipynb)):
   - Muestra de 10 documentos y 10 clips, transcritos a mano por la estudiante.
   - CER y WER con `jiwer`, con un único criterio de normalización.
   - Comparación con EasyOCR, faster-whisper `small` y Parakeet TDT 0.6B v3.
   - Extracción en JSON con Qwen2.5-1.5B-Instruct en local y auditoría humana de 20 extracciones.
3. **Dashboard** ([`app.py`](app.py)): lee los CSV ya calculados.

## Resultados

| Modelo | Tarea | Métrica global | Impreso / foto / manuscrito · Entrevista / lectura | Velocidad en CPU |
| :--- | :--- | ---: | :--- | :--- |
| **PaddleOCR** (elegido) | OCR | CER 9,6 % | 3,3 % / 0,7 % / 55,8 % | ~22 s por página, 2,3 GB de RAM |
| EasyOCR | OCR | CER 16,3 % | 5,7 % / 8,5 % / 72,0 % | ~15 s por página, 3,5 GB de RAM |
| **Whisper large-v3-turbo** (elegido) | ASR | WER 4,5 % | 4,8 % / 1,0 % | RTF 0,98, 2,1 GB de RAM |
| Whisper `small` (línea base) | ASR | WER 17,2 % | 18,9 % / 1,0 % | RTF 0,33, 0,9 GB de RAM |
| Parakeet TDT 0.6B v3 | ASR | WER 26,8 % | 29,0 % / 6,2 % | RTF 0,28, 2,2 GB de RAM |
| Qwen2.5-1.5B-Instruct | Extracción JSON | 79 % de campos correctos | 11/20 extracciones sin errores: audios 10/10, documentos 1/10 | ~16 s por archivo, 1,2 GB de RAM |

**Hallazgos:**

1. **Imprenta sí, manuscritos no.** PaddleOCR lee páginas impresas y fotos de celular con menos del 4 % de errores de carácter: sirve para buscar texto. En los manuscritos de los siglos XVI a XX el error sube al 56 %. Ahí falla tanto el orden de lectura (columnas, notas al margen) como el reconocimiento de letras antiguas. Los dos modelos probados fallan, y EasyOCR encuentra menos del 10 % de las palabras.
2. **El habla de los niños es el caso difícil del audio, y el modelo decide.** En frases leídas por adultos, los tres ASR casi no fallan: Whisper tiene un WER del 1 %, y el 6,2 % de Parakeet viene solo de escribir los números en letras. En las entrevistas a niños de 5 años, grabadas con celular en el aula, Whisper turbo se queda en el 4,8 %, `small` sube al 18,9 % y Parakeet al 29,0 %. Parakeet además pierde las tildes que distinguen palabras («tú», «qué»). Turbo cuesta 3 veces más tiempo de cómputo, pero comete 4 veces menos errores.

3. **El LLM local resume bien, pero inventa datos exactos.** En la auditoría humana de 20 extracciones, los 10 audios salieron sin errores y solo 1 de los 10 documentos. El modelo pone una fecha aunque el texto no la tenga, como «2024-01-01», y confunde al emisor con un cargo o un lugar. Sirve para el tema y el resumen. Las fechas, los emisores y los montos necesitan reglas, o comprobar que el valor aparece en el texto.

**Limitaciones:**

1. **Muestra pequeña y una sola transcriptora.** Las métricas salen de 10 documentos y 10 clips, transcritos por una sola persona. Las referencias tienen algunas erratas, y el WER depende de convenciones como escribir los números en cifras o en letras. Diferencias de 1 o 2 puntos entre modelos no son concluyentes.
2. **Solo CPU y 7 GB de RAM.** Las imágenes se procesaron con límites de tamaño por memoria (3000 px en PaddleOCR y 1600 px para la detección de EasyOCR). Los tiempos se midieron en una laptop compartida con otros programas. El LLM tiene 1500 millones de parámetros, y un modelo más grande extraería mejor los campos. Además, los audios de las entrevistas no se publican, así que esa parte de la evaluación no la puede repetir un tercero.

## Privacidad

Los entrevistados son menores de edad:

- Sus audios no se suben al repositorio.
- Sus nombres y los de sus compañeros y profesoras se reemplazan por `[PERSONA_NN]` en todos los textos publicados.
- Los textos crudos, las referencias manuales y la tabla de seudónimos quedan en `datos/raw/`, que no se versiona.

En el dashboard solo se muestran las imágenes y los audios cuya licencia lo permite. Están en [`datos/ejemplos/`](datos/ejemplos/): 17 imágenes y las 12 frases de OpenSLR. Las fotos 1, 5 y 7 no se muestran porque en ellas se transparentan nombres del reverso de la hoja.

## Datos

| Archivo | Contenido |
| :--- | :--- |
| `datos/documentos.csv` | 25 documentos: texto OCR seudonimizado y referencia manual de la muestra |
| `datos/transcripciones.csv` | 23 clips (48,9 min): transcripción con marcas de hablante y referencia manual de la muestra |
| `datos/extraccion_llm.csv` | 48 extracciones JSON del LLM (`id`, `modalidad`, `campos_json`, `modelo_llm`, `fecha`) |
| `datos/auditoria_llm.csv` | Auditoría humana de 20 extracciones, por campo |
| `datos/evaluacion_modelos.csv` | CER/WER, errores, tiempos y salida seudonimizada de cada modelo en la muestra |
| `datos/fuentes.csv` | Fuente, licencia, acceso y fecha de cada archivo |
| `datos/ejemplos/` | Imágenes y audios publicables |
| `modelos/configuracion_evaluacion.json` | Configuración de todos los modelos de la evaluación |

## Ejecución en local

Requisitos: Python 3.12.

**App (Windows, PowerShell):**

```powershell
cd tarea_2
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

**App (Linux / macOS):**

```bash
cd tarea_2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

La app se abre en `http://localhost:8501`.

**Notebooks.** Necesitan los archivos originales de `datos/raw/`, que no están en el repositorio. Sus dependencias exactas están en [`requirements-notebooks.txt`](requirements-notebooks.txt):

```bash
pip install -r requirements-notebooks.txt
jupyter nbconvert --to notebook --execute --inplace 01_extraccion.ipynb
jupyter nbconvert --to notebook --execute --inplace 02_evaluacion.ipynb
```

## Estructura

```
tarea_2/
├── 01_extraccion.ipynb        # OCR, transcripción, limpieza, seudonimización y EDA
├── 02_evaluacion.ipynb        # CER/WER, modelos alternativos, LLM y comparativa
├── app.py                     # Dashboard en Streamlit
├── requirements.txt           # Dependencias mínimas de la app
├── requirements-notebooks.txt # Dependencias exactas de los notebooks
├── evidencias_ia/             # Capturas de la conversación con IA
├── datos/                     # CSV publicables y muestra en ejemplos/
└── modelos/                   # Configuración de los modelos evaluados
```

## Uso de IA

El trabajo se hizo con ayuda de Claude Code (Anthropic). Las capturas de la conversación están en [`evidencias_ia/`](evidencias_ia/), y las decisiones y los problemas de cada parte, en los comentarios de los issues #8, #9 y #10. La revisión de la seudonimización, las transcripciones de referencia y la auditoría del LLM las hizo la estudiante.
