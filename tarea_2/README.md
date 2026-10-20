# Tarea 2 – OCR, transcripción y extracción con LLM

## Datos

| | |
| :--- | :--- |
| Documentos (OCR) | `datos/documentos.csv`: _pendiente_ (meta: 25+ documentos) |
| Audios (ASR) | `datos/transcripciones.csv`: _pendiente_ (meta: 30+ min de audio) |
| Extracción LLM | `datos/extraccion_llm.csv`: _pendiente_ |
| Fuentes y licencias | `datos/fuentes.csv`: fuente, licencia y acceso de cada archivo |
| Fecha de extracción | _pendiente_ |


## Estructura

```
tarea_2/
├── 01_extraccion.ipynb        # OCR, transcripción, limpieza y EDA
├── 02_evaluacion.ipynb        # CER/WER, LLM y comparativa de modelos
├── app.py                     # Aplicación interactiva Streamlit
├── requirements.txt           # Dependencias exactas
├── README.md                  # Reporte y guía de ejecución
├── .gitignore                 # Exclusión de archivos pesados
├── evidencias_ia/             # Capturas completas de la conversación con IA
├── datos/
│   ├── documentos.csv         # Corpus OCR (25+ documentos)
│   ├── transcripciones.csv    # Corpus ASR (30+ min de audio)
│   ├── extraccion_llm.csv     # Campos extraídos por el LLM
│   ├── fuentes.csv            # Fuente, licencia y acceso a cada archivo
│   └── ejemplos/              # Muestra ligera, publicable (si aplica)
└── modelos/                   # Configuraciones o artefactos ligeros del modelo
```

## Ejecución en local

Requisitos: Python 3.12.

**Windows (PowerShell):**

```powershell
cd tarea_2
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

**Linux / macOS:**

```bash
cd tarea_2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

La app se abre en `http://localhost:8501`.
