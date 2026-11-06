"""Calcula las respuestas esperadas de la evaluación y escribe evaluacion/preguntas.csv.

    uv run evaluacion/construir_preguntas.py

No importa nada del proyecto ni usa ninguna respuesta del agente. Las cifras del BCRP salen de su API y las de la ENAHO,
de los .dta originales del INEI, con medias ponderadas escritas aquí. Este archivo se publicó antes de la primera
corrida: el historial de git demuestra que las respuestas esperadas no cambiaron después de ver los resultados.
"""
import io
import json
import re
import ssl
import statistics
import time
import zipfile
from pathlib import Path

import httpx
import pandas as pd
import truststore

RAIZ = Path(__file__).parent.parent
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
TLS = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
MESES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10,
         "Nov": 11, "Dic": 12}
CAUSAL = ("Debe decir que esos datos no prueban una relación causal y dar al menos un motivo: años distintos, una sola "
          "observación, asociación o correlación, o factores no considerados.")


def bcrp(codigo, desde, hasta):
    """El BCRP a veces responde con una página HTML cuando recibe muchas consultas seguidas: se reintenta con espera."""
    for espera in (2, 4, 8, 16, 0):
        try:
            r = httpx.get(f"{API}/{codigo}/json/{desde}/{hasta}", timeout=90, verify=TLS, follow_redirects=True).json()
            return [(p["name"], float(p["values"][0])) for p in r["periods"] if p["values"][0] != "n.d."]
        except (ValueError, httpx.TransportError):
            time.sleep(espera)
    raise SystemExit(f"El BCRP no respondió con datos para {codigo}.")


def suma(codigo, anio):
    datos = bcrp(codigo, f"{anio}-1", f"{anio}-12")
    assert len(datos) == 12, (codigo, anio, len(datos))
    return sum(v for _, v in datos)


def promedio_mensual_tc(desde, hasta):
    """Promedio por mes del tipo de cambio diario. Los días llegan como 02Ene23."""
    meses = {}
    for nombre, valor in bcrp("PD04638PD", desde, hasta):
        m = re.fullmatch(r"\d{2}\.?([A-Za-z]{3})\.?(\d{2})", nombre)
        meses.setdefault((2000 + int(m[2]), MESES[m[1]]), []).append(valor)
    return {k: statistics.fmean(v) for k, v in sorted(meses.items())}


def enaho():
    with zipfile.ZipFile(RAIZ / "datos" / "enaho" / "966-Modulo34.zip") as z:
        s = pd.read_stata(io.BytesIO(z.read("966-Modulo34/sumaria-2024.dta")), convert_categoricals=False,
                          columns=["conglome", "vivienda", "hogar", "ubigeo", "pobreza", "factor07", "mieperho"])
    with zipfile.ZipFile(RAIZ / "datos" / "enaho" / "966-Modulo02.zip") as z:
        m = pd.read_stata(io.BytesIO(z.read("966-Modulo02/enaho01-2024-200.dta")), convert_categoricals=False,
                          columns=["conglome", "vivienda", "hogar", "p204", "p205", "p206", "p207", "p208a", "facpob07"])
    s["dep"] = s["ubigeo"].str[:2]
    s["peso"] = s["factor07"].astype(float) * s["mieperho"].astype(float)
    s["p"] = (s["pobreza"] <= 2).astype(float)
    r = m[((m["p204"] == 1) & (m["p205"] == 2)) | ((m["p204"] == 2) & (m["p206"] == 1))]
    r = r.merge(s[["conglome", "vivienda", "hogar", "dep", "p"]], on=["conglome", "vivienda", "hogar"], validate="m:1")
    assert len(r) == 108_664

    def tasa(d, peso):
        return float((d["p"] * d[peso].astype(float)).sum() / d[peso].astype(float).sum() * 100)

    por_dep = {c: tasa(g, "peso") for c, g in s.groupby("dep")}
    puno = r[r["dep"] == "21"]
    return {"nacional": tasa(s, "peso"), "por_dep": por_dep, "ninos": tasa(r[r["p208a"] < 15], "facpob07"),
            "puno_mujer": tasa(puno[puno["p207"] == 2], "facpob07"), "puno_hombre": tasa(puno[puno["p207"] == 1], "facpob07")}


def main():
    e = enaho()
    no_t = {a: suma("PN38744BM", a) for a in (2020, 2022, 2023, 2024)}
    tr = {a: suma("PN38740BM", a) for a in (2020, 2024)}
    agro = (no_t[2024] + tr[2024]) / (no_t[2020] + tr[2020])
    ipc = bcrp("PN01273PM", "2023-1", "2024-12")
    tc = promedio_mensual_tc("2023-01-01", "2024-12-31")
    assert len(ipc) == len(tc) == 24
    correlacion = statistics.correlation([v for _, v in ipc], list(tc.values()))
    diarios = bcrp("PD04638PD", "2024-01-01", "2024-12-31")
    ipc_dic = bcrp("PN01273PM", "2024-12", "2024-12")[0][1]

    d = pd.read_csv(RAIZ / "salidas" / "bcrp" / "agro_departamental.csv")
    d = d[d["periodo"].astype(str) == "2022"]
    d = d.assign(dep=d["nombre"].str.extract(r"productos de (.+?) \(")[0]).dropna(subset="dep")
    primero = d.groupby("dep")["valor"].sum().idxmax()
    assert primero == "La Libertad" and len(d["dep"].unique()) == 25
    mayor = max(e["por_dep"], key=e["por_dep"].get)
    assert mayor == "06"  # Cajamarca
    catalogo = pd.read_csv(RAIZ / "datos" / "bcrp" / "catalogo_bcrp.csv", sep=";", encoding="utf-8", dtype=str)
    fila = catalogo[catalogo["Grupo de serie"].str.contains("productos de Cajamarca", na=False)
                    & (catalogo["Nombre de serie"].str.strip() == "Total Exportaciones")
                    & (catalogo["Frecuencia"] == "Mensual")]
    assert len(fila) == 1
    cajamarca = suma(fila["Código de serie"].iloc[0], 2022)

    filas = [
        dict(id="P01", tipo="BCRP", pregunta="¿Cuál fue la inflación interanual (variación del IPC en 12 meses) de Lima "
             "Metropolitana en diciembre de 2024, en %?", valores=[round(ipc_dic, 4)], tolerancias=[0.02],
             texto="", verificacion="API del BCRP, serie PN01273PM, 2024-12"),
        dict(id="P02", tipo="BCRP", pregunta="¿Cuál fue el promedio de 2024 del tipo de cambio interbancario venta, en soles "
             "por dólar, calculado con los datos diarios del BCRP?", valores=[round(statistics.fmean(v for _, v in diarios), 4)],
             tolerancias=[0.002], texto="", verificacion=f"Promedio de {len(diarios)} datos diarios de PD04638PD, API del BCRP"),
        dict(id="P03", tipo="BCRP", pregunta="¿Cuál fue el valor de las exportaciones no tradicionales agropecuarias del Perú "
             "en 2023, en millones de US$ FOB, según el BCRP?", valores=[round(no_t[2023], 2)], tolerancias=[5], texto="",
             verificacion="Suma de los 12 meses de PN38744BM, API del BCRP"),
        dict(id="P04", tipo="BCRP", pregunta="Con los 24 meses de enero de 2023 a diciembre de 2024, ¿cuál fue la correlación "
             "de Pearson entre la inflación interanual de Lima Metropolitana y el promedio mensual del tipo de cambio "
             "interbancario venta?", valores=[round(correlacion, 4)], tolerancias=[0.02], texto="",
             verificacion="statistics.correlation sobre PN01273PM y el promedio mensual de PD04638PD"),
        dict(id="P05", tipo="ENAHO", pregunta="Según la ENAHO 2024, ¿qué porcentaje de la población del Perú estaba en pobreza "
             "monetaria?", valores=[round(e["nacional"], 2)], tolerancias=[0.1], texto="",
             verificacion="sumaria-2024.dta, media ponderada con factor07 × mieperho; INEI publicó 27,6 %"),
        dict(id="P06", tipo="ENAHO", pregunta="Según la ENAHO 2024, ¿qué porcentaje de la población del departamento de Cusco "
             "estaba en pobreza monetaria?", valores=[round(e["por_dep"]["08"], 2)], tolerancias=[0.1], texto="",
             verificacion="sumaria-2024.dta, media ponderada; referencia de la Sesión 16: 18,5 %"),
        dict(id="P07", tipo="ENAHO", pregunta="Con los microdatos de la ENAHO 2024, ¿qué porcentaje de los residentes habituales "
             "de 0 a 14 años estaba en pobreza monetaria, ponderado con el factor de expansión de personas?",
             valores=[round(e["ninos"], 2)], tolerancias=[0.1], texto="",
             verificacion="Módulos 34 y 02 originales, residentes con p208a < 15 ponderados con facpob07"),
        dict(id="P08", tipo="ENAHO", pregunta="Con los microdatos de la ENAHO 2024, en el departamento de Puno, ¿qué porcentaje "
             "de las mujeres y qué porcentaje de los hombres residentes habituales estaba en pobreza monetaria, ponderado con "
             "el factor de expansión de personas? Da primero mujeres y luego hombres.",
             valores=[round(e["puno_mujer"], 2), round(e["puno_hombre"], 2)], tolerancias=[0.1, 0.1], texto="",
             verificacion="Módulos 34 y 02 originales, residentes con ubigeo 21 por p207, ponderados con facpob07"),
        dict(id="P09", tipo="Combinada", pregunta="¿En qué porcentaje crecieron entre 2020 y 2024 las agroexportaciones peruanas "
             "(productos tradicionales agrícolas más no tradicionales agropecuarios, valor FOB, BCRP), qué departamento agroexportó "
             "más en 2022, y qué porcentaje de pobreza monetaria tuvo ese departamento en 2024 según la ENAHO? ¿Estos datos prueban "
             "que la agroexportación aumenta la pobreza?", valores=[round((agro - 1) * 100, 2), round(e["por_dep"]["13"], 2)],
             tolerancias=[0.1, 0.1], texto="La Libertad", criterio=CAUSAL,
             verificacion="PN38744BM + PN38740BM por 12 meses de cada año; series regionales anuales de 2022; sumaria-2024.dta"),
        dict(id="P10", tipo="Combinada", pregunta="¿Qué departamento tuvo la mayor pobreza monetaria en 2024 según la ENAHO, qué "
             "porcentaje tuvo, y cuánto exportó en total en 2022 según el BCRP, en millones de US$ FOB? ¿Se puede concluir de "
             "esos datos que exportar mucho no reduce la pobreza?", valores=[round(e["por_dep"]["06"], 2), round(cajamarca, 2)],
             tolerancias=[0.1, 5], texto="Cajamarca", criterio=CAUSAL,
             verificacion=f"sumaria-2024.dta; suma de los 12 meses de {fila['Código de serie'].iloc[0]}, API del BCRP"),
    ]
    t = pd.DataFrame(filas)
    t["criterio"] = t["criterio"].fillna("")
    t["respuesta_esperada"] = [", ".join(filter(None, [x.texto, *[str(v) for v in x.valores]])) for x in t.itertuples()]
    t["valores"] = t["valores"].map(json.dumps)
    t["tolerancias"] = t["tolerancias"].map(json.dumps)
    columnas = ["id", "tipo", "pregunta", "respuesta_esperada", "valores", "tolerancias", "texto", "criterio", "verificacion"]
    t[columnas].to_csv(Path(__file__).parent / "preguntas.csv", index=False, encoding="utf-8")
    print(t[["id", "tipo", "respuesta_esperada", "tolerancias"]].to_string(index=False))


if __name__ == "__main__":
    main()
