# 🗞️ Tarea 1 – Noticias peruanas: del titular al clasificador

**Estudiante:** Ivette Carolina Mamani Flores ([@IvettexMamani](https://github.com/IvettexMamani)) · Diplomado Python 2026 · Trabajo individual

## 1. Pregunta del proyecto

> **¿Pueden convertir titulares peruanos en un clasificador de noticias?**

Sí. Con 374 titulares de El Comercio, un DistilBERT multilingüe ajustado en CPU clasifica titulares nuevos en `politica`, `economia`, `deportes` o `ciencia_tecnologia` con **F1 macro 0.80** en un conjunto de test reservado. La línea base zero-shot obtuvo F1 0.58.

| Enfoque (evaluado en el mismo test, n = 57) | Accuracy | F1 macro | Latencia en CPU |
| :--- | :---: | :---: | :---: |
| Zero-shot `Recognai/bert-base-spanish-wwm-cased-xnli` | 0.72 | 0.71 | 298 ms |
| LLM `Qwen2.5-1.5B-Instruct` (GGUF 4 bits; lee titular + bajada) | 0.88 | 0.88 | 2 695 ms |
| DistilBERT fine-tuned con las etiquetas del LLM | 0.81 | 0.80 | 33 ms |
| **DistilBERT fine-tuned con la etiqueta de sección (modelo del dashboard)** | **0.81** | **0.805** | **33 ms** |

- **Zero-shot (paso 1, 40 titulares):** F1 macro 0.58.
- **Acuerdo LLM vs. auditoría humana (20 casos a ciegas):** 17/20 (85 %).

**Decisión:** el dashboard usa DistilBERT, porque responde ~80 veces más rápido que el LLM y es barato de servir en CPU. El LLM queda como etiquetador offline para ampliar el dataset (detalle en la sección 6 de `02_clasificacion.ipynb`).

## 2. Medio y fechas de extracción

| | |
| :--- | :--- |
| Opción | **B – El Comercio** (`https://elcomercio.pe`) |
| Fecha de descarga | **18 de octubre de 2026** |
| Fechas de publicación | del 6 al 18 de octubre de 2026 (política y economía: 12–18 oct; deportes: 16–18 oct; ciencia y tecnología: 6–18 oct) |
| Fuente | Sitemaps oficiales por sección declarados en `robots.txt` (`/sitemap/web/{seccion}/?outputType=xml`) + HTML de cada nota (`requests` + `BeautifulSoup`) |
| Volumen | 400 URLs → 26 descartes (15 columnas de opinión, 10 secciones fuera de las 4 categorías, 1 duplicado) → **374 noticias** (90–98 por categoría) |
| Buenas prácticas | `robots.txt` verificado, `User-Agent` descriptivo, 1.5 s entre solicitudes, máximo 1 reintento, respaldo crudo en `datos/raw/` |

Se usaron sitemaps y no la portada de cada sección porque las portadas cargan los listados con JavaScript y los RSS antiguos del diario redirigen o devuelven 404.

## 3. Hallazgos analíticos

1. **Las etiquetas de un LLM pequeño y local bastan para entrenar el clasificador.**
   - Qwen2.5-1.5B coincide con la sección del diario en el 87 % de las 374 noticias (F1 0.87) y con la auditoría humana en 17 de 20 casos.
   - Cuando su confianza es ≥ 0.90 (78 % de las noticias), acierta el 93.5 %; por debajo de ese umbral baja a 65 %. La confianza sirve para decidir qué revisar a mano.
   - Un DistilBERT entrenado **solo** con las etiquetas del LLM logra en test casi el mismo F1 que el entrenado con la sección (0.80 vs. 0.805). La supervisión débil permite crecer el dataset sin etiquetar a mano.

2. **Economía es la categoría más difícil, y las cifras confunden al clasificador.**
   - Es la peor clase en test (F1 0.67), mientras que política es la mejor (0.89).
   - Sus titulares comparten vocabulario con política (*"Gobierno designa… Fonafe"*, *Ley MAPE*) y con tecnología (*fintech*, *Premio Nobel de Economía*). El propio LLM etiquetó 19 de las 90 notas de economía como `ciencia_tecnologia`.
   - DistilBERT clasificó como *deportes* titulares como *"El dólar abre en S/3,44"*: viendo solo el titular, asocia las cifras a marcadores de partido.
   - Política, en cambio, tiene un vocabulario muy propio (Congreso, Senado, ministro) y los titulares más largos (mediana de 109 caracteres frente a ~90 del resto).

## 4. Limitaciones técnicas

1. **Hardware modesto (solo CPU, 7.3 GB de RAM) que condicionó los modelos.**
   - Qwen2.5-1.5B en `transformers` no era viable: en `float32` necesita ~6 GB y en `bfloat16` tardaba 10–14 s por titular. Se usó su versión GGUF de 4 bits con `llama.cpp`.
   - DistilBERT se ajustó con la matriz de embeddings congelada (44 M de 135 M parámetros entrenables). Quedaron fuera modelos mayores, como `xlm-roberta-large-xnli`.
   - Los pesos del modelo (541 MB) superan el límite de GitHub, así que no están en el repo: hay que regenerarlos con el notebook 2 para usar el probador en vivo. Por eso el dashboard se comprobó en local y no se desplegó en Streamlit Community Cloud.

2. **Datos acotados y una "verdad" imperfecta.**
   - Hay un solo medio y una ventana corta (6–18 de octubre de 2026; deportes cubre solo 3 días, centrados en la fecha 12 del Torneo Clausura), así que el modelo puede no generalizar a otros periodos o diarios.
   - La etiqueta de referencia es la sección del diario, que no siempre coincide con el tema: la *Ley MAPE* figura en política aunque trata de regulación minera, y los despidos en Netflix aparecen en tecnología.
   - El test tiene solo 57 titulares, así que cada error mueve el F1 unos 2 puntos.

## 5. Cómo ejecutarlo en local

Requisitos: Python 3.12 y unos 3 GB libres en disco para los modelos. No hace falta GPU.

```powershell
# 1) Clonar el repositorio y entrar a la carpeta de la tarea
git clone https://github.com/IvettexMamani/diplomado-python-2026.git
cd diplomado-python-2026/tarea_1

# 2) Crear el entorno e instalar las dependencias exactas
python -m venv .venv
.venv\Scripts\activate            # en macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 3) Regenerar el modelo (los pesos .safetensors no se suben a GitHub por pesar > 100 MB)
jupyter nbconvert --to notebook --execute --inplace 02_clasificacion.ipynb

# 4) Abrir el dashboard
streamlit run app.py
```

Notas:

- `01_recoleccion.ipynb` puede reejecutarse sin volver a descargar las noticias, porque lee los respaldos de `datos/raw/`. Para una recolección nueva, borra `datos/raw/articulos.jsonl` y `datos/raw/sitemaps/`.
- `02_clasificacion.ipynb` reutiliza las respuestas del LLM guardadas en `datos/raw/llm_respuestas.jsonl`. Si borras ese archivo, el etiquetado con Qwen tarda unos 20 minutos en CPU.

## 6. Estructura

```text
tarea_1/
├── 01_recoleccion.ipynb      # Scraping, limpieza, mapeo de secciones, EDA (ejecutado)
├── 02_clasificacion.ipynb    # Zero-shot, LLM + auditoría, split 70/15/15, fine-tuning, test (ejecutado)
├── app.py                    # Dashboard Streamlit con probador en vivo
├── requirements.txt          # Dependencias exactas
├── datos/
│   ├── noticias.csv          # 374 noticias x 7 columnas
│   ├── etiquetas_llm.csv     # Etiquetas de Qwen2.5-1.5B (titular, etiqueta_llm, confianza, modelo_llm, fecha, url)
│   ├── auditoria_humana.csv  # 20 casos etiquetados a mano, a ciegas
│   ├── particion.csv         # Asignación train/val/test de cada URL
│   └── raw/                  # Respaldos crudos: sitemaps, HTML parseado, respuestas del LLM
└── modelo/                   # config, tokenizer y metricas.json (los pesos se generan con el notebook 2)
```

## 7. Uso de IA

Siguiendo lo permitido en el enunciado, el código de scraping, los notebooks y el dashboard se desarrollaron con asistencia de **Claude Code** (Anthropic). La elección del medio y del LLM, la auditoría humana de las 20 predicciones y la revisión de los resultados fueron hechas por la estudiante.
