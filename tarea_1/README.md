# Tarea 1 – Clasificador de titulares peruanos

**Pregunta del proyecto:** ¿se pueden convertir titulares de un diario peruano en un clasificador de noticias?

**Respuesta corta:** sí. Un DistilBERT multilingüe ajustado con solo 263 titulares clasifica titulares nuevos en 4 categorías con **F1 macro 0.89 en test**, iguala a un LLM local y responde en milisegundos en CPU.

## Datos

| | |
| :--- | :--- |
| Medio | **El Comercio** (`elcomercio.pe`), opción B |
| Fuente | Sitemaps oficiales de 4 secciones declarados en `robots.txt` (`/sitemap/web/{seccion}/`) + HTML de cada nota (`requests` + `BeautifulSoup`) |
| Fecha de extracción | **18/10/2026**, de 20:18 a 20:34 (hora de Lima), con pausas de 1.5 s y máximo 1 reintento |
| Fechas de publicación | Del 06/10/2026 al 18/10/2026 |
| Dataset final | `datos/noticias.csv`: 376 noticias × 7 columnas (titular, bajada, medio, seccion_original, url, fecha, etiqueta) |
| Categorías | politica 92 · economia 90 · deportes 98 · ciencia_tecnologia 96 |
| Descartes | 24 de 400 URLs (opinión, ECData, BBC News Mundo, autos, 1 repetida), con su motivo en `datos/raw/descartes.csv` |

## Resultados en test (57 titulares reservados)

| Enfoque | Accuracy | F1 macro | Latencia en CPU |
| :--- | :---: | :---: | :---: |
| Zero-shot `Recognai/bert-base-spanish-wwm-cased-xnli` | 0.72 | 0.70 | ~0.35 s |
| LLM `Qwen2.5-1.5B-Instruct` (GGUF 4 bits, titular + bajada) | 0.88 | 0.88 | ~2.8 s |
| DistilBERT entrenado con las etiquetas del LLM | 0.82 | 0.81 | 30–50 ms |
| **DistilBERT entrenado con la sección (modelo del dashboard)** | **0.89** | **0.89** | **30–50 ms** |

Otros resultados:

- Línea base zero-shot en 40 titulares: F1 macro 0.63.
- Acuerdo LLM–auditoría humana a ciegas: **18/20 (90 %)**.

## Hallazgos

1. **Un modelo pequeño y ajustado gana en la relación precisión/costo.** Con 263 titulares de entrenamiento, DistilBERT supera al zero-shot por 0.19 de F1 y empata con el LLM (0.89 frente a 0.88, una diferencia de 1 titular en test). El LLM, además, tiene la ventaja de leer también la bajada. DistilBERT es más de 50 veces más rápido que el LLM y ocupa la mitad de espacio, por eso es el modelo que usa el dashboard.
2. **El LLM sirve como etiquetador, pero sus dudas se notan y sus errores se heredan.** Su acuerdo con la auditoría humana (90 %) es igual al de la persona con la sección del diario, y su confianza es informativa: con confianza ≥ 0.90 acierta el 94 % frente al 65 % por debajo. Aun así, el DistilBERT entrenado solo con etiquetas del LLM baja a F1 0.81. La frontera política–economía (nombramientos del Gobierno en Fonafe o Indecopi, acuerdos comerciales) confunde por igual al LLM, al modelo y a la persona que auditó.

## Limitaciones

1. **Cobertura temporal corta, desigual y de un solo medio.** El sitemap trae las 100 notas más recientes de cada sección, así que deportes cubre 3 días y ciencia y tecnología, 13. El modelo puede estar aprendiendo los temas de esos días (la Ley MAPE, Caminos del Inca) más que la categoría. Probablemente por eso deportes tiene F1 1.00, y no se sabe cómo generaliza a otros meses o a otros diarios.
2. **Evaluación pequeña y modelos limitados por el hardware.** Con 57 titulares de test, cada error mueve el F1 de una categoría entre 3 y 7 puntos. La laptop (CPU, 7.3 GB de RAM) obligó a varias concesiones: congelar los embeddings de DistilBERT, usar un LLM de 1.5B cuantizado a 4 bits y el modelo zero-shot base en lugar de `xlm-roberta-large-xnli`. Además, los pesos del modelo (541 MB) no caben en GitHub y hay que regenerarlos localmente (ver abajo).

## Estructura

```
tarea_1/
├── 01_recoleccion.ipynb     # Scraping, limpieza y EDA (ejecutado)
├── 02_clasificacion.ipynb   # Zero-shot, LLM, fine-tuning y evaluación (ejecutado)
├── app.py                   # Dashboard Streamlit
├── requirements.txt         # Dependencias exactas
├── datos/
│   ├── noticias.csv         # 376 noticias, 7 columnas
│   ├── etiquetas_llm.csv    # Etiquetas y confianza del LLM
│   ├── auditoria_humana.csv # 20 casos revisados a ciegas
│   ├── particion.csv        # train / val / test
│   └── raw/                 # Respaldo crudo: robots.txt, sitemaps, HTML extraído, respuestas del LLM
└── modelo/                  # config, tokenizer y metricas.json (los pesos .safetensors se excluyen)
```

## Ejecución en local

Requisitos: Python 3.12. Probado en Windows con solo CPU, en un entorno virtual nuevo creado únicamente con `requirements.txt`.

**Windows (PowerShell):**

```powershell
cd tarea_1
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

**Linux / macOS:**

```bash
cd tarea_1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

La app se abre en `http://localhost:8501`.

**Pesos del modelo:** la exploración y las métricas funcionan apenas se clona el repositorio. El probador en vivo, en cambio, necesita `modelo/model.safetensors` (541 MB), que no se sube a GitHub. Para generarlo, abre `02_clasificacion.ipynb` en VS Code con el kernel de `.venv` y ejecuta todo (*Run All*). Toma unos 5 minutos en CPU más la descarga de ~2 GB de modelos de Hugging Face. Las etiquetas del LLM se leen del respaldo `datos/raw/llm_respuestas.jsonl`, así que no se vuelven a calcular.

**Notebooks:** `01_recoleccion.ipynb` se puede reejecutar sin volver a pedir nada al diario, porque usa los respaldos de `datos/raw/`. Si borras esa carpeta, descarga todo de nuevo con las mismas pausas.

> En Windows con antivirus que inspecciona HTTPS (por ejemplo Avast), los notebooks usan `truststore` para validar los certificados con el almacén del sistema.
