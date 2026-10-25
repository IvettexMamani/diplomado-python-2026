"""App de la Tarea 2: documentos (OCR) y audios (ASR) con extracción por LLM.

Solo muestra resultados ya calculados en 01_extraccion.ipynb y 02_evaluacion.ipynb: no ejecuta modelos.
Todos los textos que muestra están seudonimizados. Las imágenes y los audios salen de datos/ejemplos/,
que solo tiene los archivos cuya licencia permite publicarlos.

Ejecutar desde la carpeta tarea_2/:  streamlit run app.py
"""
import html
import json
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

RAIZ = Path(__file__).parent
DATOS = RAIZ / "datos"
EJEMPLOS = DATOS / "ejemplos"

st.set_page_config(page_title="Tarea 2 – OCR, ASR y LLM", page_icon="📄", layout="wide")

# Paleta de los notebooks, en orden fijo: el color sigue al modelo en todos los gráficos
AZUL, NARANJA, AQUA, AMARILLO = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
COLOR = {"PaddleOCR": AZUL, "EasyOCR": NARANJA,
         "faster-whisper small": AZUL, "Parakeet TDT 0.6B v3": NARANJA, "faster-whisper large-v3-turbo": AQUA}
TIPOS = {"impreso": "Impreso", "foto": "Foto de celular", "manuscrito": "Manuscrito"}
coma = lambda x, d=1: f"{x:.{d}f}".replace(".", ",")   # decimales con coma
pct = lambda x: coma(100 * x) + " %"


@st.cache_data
def cargar():
    leer = lambda nombre: pd.read_csv(DATOS / nombre, keep_default_na=False)
    docs, audios, fuentes = leer("documentos.csv"), leer("transcripciones.csv"), leer("fuentes.csv")
    llm, auditoria = leer("extraccion_llm.csv"), leer("auditoria_llm.csv")
    evaluacion = pd.read_csv(DATOS / "evaluacion_modelos.csv")   # numérico: rtf queda vacío en el OCR
    evaluacion["texto_salida"] = evaluacion["texto_salida"].fillna("")
    fuentes = fuentes.set_index("id")
    for d in (docs, audios):
        d["licencia"] = d["id"].map(fuentes["licencia"])
    llm["campos"] = llm["campos_json"].map(json.loads)
    return docs, audios, fuentes, llm.set_index("id"), evaluacion, auditoria


docs, audios, fuentes, llm, evaluacion, auditoria = cargar()
audios["minutos"] = audios["duracion_seg"] / 60


def tasa(g):
    "CER o WER agregado: errores totales entre el tamaño total de la referencia."
    return g["errores"].sum() / g["n_ref"].sum()


def resaltar(texto, termino):
    "Texto escapado para HTML, con saltos de línea, las marcas de hablante en negrita y el término buscado resaltado."
    salida = html.escape(texto)
    if termino:
        salida = re.sub(f"({re.escape(html.escape(termino))})", r"<mark>\1</mark>", salida, flags=re.I)
    salida = re.sub(r"\s*(\[HABLANTE_\d+\])\s*", r"<br><b>\1</b> ", salida).removeprefix("<br>")
    return salida.replace("\n", "<br>")


def mostrar_texto(texto, termino, alto=360):
    st.markdown(f'<div style="max-height:{alto}px; overflow-y:auto; padding:0.6rem 0.8rem; border:1px solid rgba(128,128,128,.35);'
                f' border-radius:6px; font-size:0.92rem; line-height:1.5">{resaltar(texto, termino) or "<i>(vacío)</i>"}</div>',
                unsafe_allow_html=True)


def ficha_licencia(ident):
    "Fuente y licencia de un archivo; el enlace solo se muestra si es una URL."
    f = fuentes.loc[ident]
    url = f["fuente_url"] if str(f["fuente_url"]).startswith("http") else ""
    st.caption(f"**Fuente:** {f'[{url}]({url})' if url else f['fuente_url']}  \n**Licencia:** {f['licencia']}  \n"
               f"**Acceso:** {f['acceso']} ({f['fecha_acceso']})")


# ── Encabezado ────────────────────────────────────────────────────────────────
st.title("¿Pueden convertirse documentos escaneados y entrevistas en audio en un archivo de texto estructurado y buscable?")
st.markdown(
    f"**{len(docs)} documentos peruanos** (impresos, fotos de celular y manuscritos) pasaron por OCR y "
    f"**{len(audios)} clips de audio** ({coma(audios['minutos'].sum())} min) por reconocimiento de voz. "
    "Los textos se limpiaron y seudonimizaron, y un LLM local extrajo campos en JSON. "
    "La calidad se midió con CER y WER sobre una muestra de 10 documentos y 10 clips transcritos a mano, "
    "y la extracción del LLM se auditó a mano en 20 casos.")
with st.expander("Metodología y privacidad"):
    st.markdown("""
- **OCR:** PaddleOCR 3.7 (PP-OCRv6 medium) en CPU; alternativo evaluado: EasyOCR 1.7.
- **ASR:** faster-whisper large-v3-turbo en CPU, con VAD Silero y diarización por huellas de voz (WeSpeaker); evaluados también faster-whisper `small` y Parakeet TDT 0.6B v3.
- **Métricas:** CER y WER con `jiwer`, tras una normalización única (minúsculas, sin puntuación ni marcas de hablante). El valor de un grupo es la suma de errores entre la suma de la referencia.
- **LLM:** Qwen2.5-1.5B-Instruct local (GGUF, `llama-cpp-python`), con salida JSON obligada por un esquema.
- **Privacidad:** los entrevistados son niños de un jardín. Sus audios no se publican y sus textos aparecen seudonimizados (`[PERSONA_NN]`). Solo se muestran imágenes y audios cuya licencia lo permite.
- Esta app no ejecuta modelos: lee los CSV que producen los notebooks `01_extraccion.ipynb` y `02_evaluacion.ipynb`.
""")

# ── Filtros ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filtros")
    termino = st.text_input("Buscar en los textos OCR y ASR", placeholder="p. ej., contrato, jardín, sectores").strip()
    tipos = st.multiselect("Tipo de documento", list(TIPOS), default=list(TIPOS), format_func=TIPOS.get)
    fuentes_audio = st.multiselect("Fuente del audio", sorted(audios["fuente"].unique()), default=sorted(audios["fuente"].unique()))
    dur_max = float(audios["duracion_seg"].max())
    duracion = st.slider("Duración del clip (s)", 0.0, dur_max, (0.0, dur_max), step=5.0)
    modelos_ocr = st.multiselect("Modelos OCR", ["PaddleOCR", "EasyOCR"], default=["PaddleOCR", "EasyOCR"])
    modelos_asr = st.multiselect("Modelos ASR", ["faster-whisper large-v3-turbo", "faster-whisper small", "Parakeet TDT 0.6B v3"],
                                 default=["faster-whisper large-v3-turbo", "faster-whisper small", "Parakeet TDT 0.6B v3"])
    st.caption("Los filtros se aplican a las tablas, los gráficos y los indicadores de las tres pestañas.")

coincide = lambda serie: serie.str.contains(re.escape(termino), case=False) if termino else pd.Series(True, index=serie.index)
docs_f = docs[docs["tipo"].isin(tipos) & coincide(docs["texto_ocr"])].copy()
audios_f = audios[audios["fuente"].isin(fuentes_audio) & audios["duracion_seg"].between(*duracion) & coincide(audios["texto_asr"])].copy()
if termino:
    docs_f["coincidencias"] = docs_f["texto_ocr"].str.count(re.escape(termino), flags=re.I)
    audios_f["coincidencias"] = audios_f["texto_asr"].str.count(re.escape(termino), flags=re.I)
ev_ocr = evaluacion[(evaluacion["metrica"] == "CER") & evaluacion["modelo"].isin(modelos_ocr) & evaluacion["grupo"].isin(tipos)]
ids_audio = set(audios[audios["fuente"].isin(fuentes_audio) & audios["duracion_seg"].between(*duracion)]["id"])
ev_asr = evaluacion[(evaluacion["metrica"] == "WER") & evaluacion["modelo"].isin(modelos_asr) & evaluacion["id"].isin(ids_audio)]

resultados, pestana_docs, pestana_audios = st.tabs(["📊 Resultados", "📄 Documentos", "🎙️ Audios"])

# ── Resultados ────────────────────────────────────────────────────────────────
with resultados:
    c = st.columns(6)
    c[0].metric("Documentos con OCR", len(docs_f), help="Documentos que cumplen los filtros (de 25)")
    c[1].metric("Minutos de audio transcritos", coma(audios_f["minutos"].sum()),
                help="Clips que cumplen los filtros")
    for col, ev, nombre in [(c[2], ev_ocr, "CER"), (c[3], ev_asr, "WER")]:
        if ev.empty:
            col.metric(f"Mejor {nombre}", "—")
        else:
            por_modelo = ev.groupby("modelo").apply(tasa)
            col.metric(f"Mejor {nombre}", pct(por_modelo.min()), help=f"{por_modelo.idxmin()}, en la muestra evaluada con los filtros actuales")
    aud = auditoria.assign(ok=auditoria["correcto"] == "sí")
    completas = aud.groupby("id")["ok"].all()
    c[4].metric("Concordancia LLM vs. auditoría", pct(aud["ok"].mean()), help="Campos que la auditoría humana juzgó correctos")
    c[5].metric("Extracciones sin errores", f"{completas.sum()}/{len(completas)}", help="Extracciones con todos los campos correctos")

    izq, der = st.columns(2)
    with izq:
        if ev_ocr.empty:
            st.info("Elige al menos un modelo OCR y un tipo de documento.")
        else:
            g = ev_ocr.groupby(["grupo", "modelo"]).apply(tasa).rename("CER").reset_index()
            g["tipo"] = g["grupo"].map(TIPOS)
            fig = px.bar(g, x="tipo", y="CER", color="modelo", barmode="group", color_discrete_map=COLOR,
                         category_orders={"tipo": [TIPOS[t] for t in tipos]}, labels={"tipo": "", "modelo": "Modelo"},
                         title="CER por tipo de documento (menos es mejor)", hover_data={"CER": ":.1%"})
            fig.update_yaxes(tickformat=".0%", rangemode="tozero")
            fig.update_layout(barcornerradius=4, legend=dict(orientation="h", y=-0.15))
            st.plotly_chart(fig)
    with der:
        if ev_asr.empty:
            st.info("Ningún clip de la muestra evaluada cumple los filtros.")
        else:
            g = ev_asr.groupby(["modelo", "grupo"]).apply(tasa).rename("WER").reset_index()
            g["condición"] = g["grupo"].str.split(" ").str[0].str.capitalize()
            fig = px.bar(g, x="condición", y="WER", color="modelo", barmode="group", color_discrete_map=COLOR,
                         labels={"condición": "", "modelo": "Modelo"}, category_orders={"modelo": modelos_asr},
                         title="WER por tipo de audio (menos es mejor)", hover_data={"WER": ":.1%", "grupo": True})
            fig.update_yaxes(tickformat=".0%", rangemode="tozero")
            fig.update_layout(barcornerradius=4, legend=dict(orientation="h", y=-0.15))
            st.plotly_chart(fig)

    if not ev_asr.empty:
        g = ev_asr.groupby("modelo").agg(segundos=("segundos", "sum"), WER=("errores", "sum"), n=("n_ref", "sum")).reset_index()
        dur = audios.set_index("id")["duracion_seg"]
        g["RTF"] = g["segundos"] / [dur[ev_asr.loc[ev_asr["modelo"] == m, "id"]].sum() for m in g["modelo"]]
        g["WER"] = g["WER"] / g["n"]
        fig = px.scatter(g, x="RTF", y="WER", color="modelo", text="modelo", color_discrete_map=COLOR,
                         title="Precisión frente a velocidad del ASR en CPU (abajo a la izquierda es mejor)",
                         labels={"RTF": "Factor de tiempo real (segundos de cómputo por segundo de audio)"},
                         hover_data={"WER": ":.1%", "RTF": ":.2f"})
        fig.update_traces(marker=dict(size=16, line=dict(color="white", width=2)), textposition="top center", showlegend=False)
        fig.update_xaxes(rangemode="tozero")
        fig.update_yaxes(tickformat=".0%", rangemode="tozero")
        st.plotly_chart(fig)

    st.subheader("Métricas por archivo de la muestra evaluada")
    tabla_ev = pd.concat([ev_ocr, ev_asr])[["id", "modalidad", "grupo", "modelo", "rol", "metrica", "valor", "errores", "n_ref", "segundos", "rtf"]]
    st.dataframe(tabla_ev, hide_index=True,
                 column_config={"valor": st.column_config.NumberColumn("CER/WER", format="percent")})
    st.download_button("Descargar métricas (CSV)", tabla_ev.to_csv(index=False).encode("utf-8"), "metricas_filtradas.csv", "text/csv")

    with st.expander("Auditoría humana del LLM por campo"):
        st.dataframe(aud.groupby(["modalidad", "campo"], sort=False)["ok"].agg(correctos="sum", revisados="size", acierto="mean").reset_index(),
                     hide_index=True, column_config={"acierto": st.column_config.NumberColumn(format="percent")})

# ── Documentos ────────────────────────────────────────────────────────────────
with pestana_docs:
    st.subheader(f"{len(docs_f)} documentos" + (f" que contienen «{termino}»" if termino else ""))
    columnas = ["id", "tipo", "fuente", "modelo_ocr"] + (["coincidencias"] if termino else [])
    st.dataframe(docs_f[columnas], hide_index=True)
    st.download_button("Descargar documentos filtrados (CSV, textos seudonimizados)",
                       docs_f.drop(columns=["licencia"]).to_csv(index=False).encode("utf-8"), "documentos_filtrados.csv", "text/csv")

    if not docs_f.empty:
        ident = st.selectbox("Documento", docs_f["id"], key="doc")
        d = docs_f.set_index("id").loc[ident]
        izq, der = st.columns([3, 2])
        with izq:
            st.markdown(f"**Texto OCR** ({d['modelo_ocr']})")
            mostrar_texto(d["texto_ocr"], termino)
            if d["texto_referencia"]:
                st.markdown("**Referencia manual**")
                mostrar_texto(d["texto_referencia"], termino, alto=220)
                cer = evaluacion[(evaluacion["id"] == ident)].set_index("modelo")
                st.markdown("**CER frente a la referencia:** " + " · ".join(f"{m} {pct(v)}" for m, v in cer["valor"].items()))
                with st.expander("Ver la salida de cada modelo OCR"):
                    for m, r in cer.iterrows():
                        st.markdown(f"**{m}** · CER {pct(r['valor'])}")
                        mostrar_texto(r["texto_salida"], termino, alto=200)
        with der:
            imagen = EJEMPLOS / f"{ident}.jpg"
            if imagen.exists():
                st.image(str(imagen), caption=ident, width="stretch")
            else:
                st.info("La imagen de este documento no se publica: su licencia no lo permite, o muestra datos personales "
                        "(nombres que se transparentan del reverso de la hoja).")
            ficha_licencia(ident)
            st.markdown("**Campos extraídos por el LLM**")
            st.json({k: v for k, v in llm.loc[ident, "campos"].items() if k not in ("citas_clave", "numero_hablantes")})

# ── Audios ────────────────────────────────────────────────────────────────────
with pestana_audios:
    st.subheader(f"{len(audios_f)} clips · {coma(audios_f['minutos'].sum())} min" + (f" que contienen «{termino}»" if termino else ""))
    columnas = ["id", "fuente", "duracion_seg", "n_hablantes", "modelo_asr"] + (["coincidencias"] if termino else [])
    st.dataframe(audios_f[columnas], hide_index=True)
    st.download_button("Descargar transcripciones filtradas (CSV, textos seudonimizados)",
                       audios_f.drop(columns=["licencia", "minutos"]).to_csv(index=False).encode("utf-8"),
                       "transcripciones_filtradas.csv", "text/csv")

    if not audios_f.empty:
        ident = st.selectbox("Clip", audios_f["id"], key="audio")
        a = audios_f.set_index("id").loc[ident]
        izq, der = st.columns([3, 2])
        with izq:
            st.markdown(f"**Transcripción** ({a['modelo_asr']}, {a['n_hablantes']} hablante(s) según la diarización)")
            mostrar_texto(a["texto_asr"], termino)
            wer = evaluacion[(evaluacion["id"] == ident)].set_index("modelo")
            if a["texto_referencia"]:
                st.markdown("**Referencia manual**")
                mostrar_texto(a["texto_referencia"], termino, alto=220)
                st.markdown("**WER frente a la referencia:** " +
                            " · ".join(f"{m} {pct(r['valor'])} (RTF {coma(r['rtf'], 2)})" for m, r in wer.iterrows()))
                with st.expander("Comparar la salida de los tres modelos ASR"):
                    for m, r in wer.iterrows():
                        st.markdown(f"**{m}** · WER {pct(r['valor'])}")
                        mostrar_texto(r["texto_salida"], termino, alto=200)
        with der:
            audio = EJEMPLOS / f"{ident}.wav"
            if audio.exists():
                st.audio(str(audio))
            else:
                st.info("El audio de este clip no se publica: es una entrevista a menores de edad o un video de YouTube sin licencia abierta. "
                        "Solo se muestra su transcripción seudonimizada.")
            ficha_licencia(ident)
            st.markdown("**Campos extraídos por el LLM**")
            st.json({k: v for k, v in llm.loc[ident, "campos"].items() if k not in ("emisor", "fecha", "monto")})
