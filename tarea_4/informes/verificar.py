"""Comprueba cifras del informe final por un camino distinto al del agente y escribe informes/verificacion.md.

    uv run informes/verificar.py

No importa nada del proyecto. Las cifras del BCRP se recalculan con otras series (las mensuales, no las anuales que usó
el agente) y las de la ENAHO, con los .dta originales del INEI y una media ponderada escrita aquí. La columna «En el
informe» se copia a mano de informes/informe_final.md: es lo que se quiere poner a prueba.
"""
import io
import ssl
import statistics
import zipfile
from datetime import date
from pathlib import Path

import httpx
import pandas as pd
import truststore

RAIZ = Path(__file__).parent.parent
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
WEB = "https://estadisticas.bcrp.gob.pe/estadisticas/series"
TLS = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# Series mensuales: no son las que usó el agente
NO_TRADICIONALES, TRADICIONALES = "PN38744BM", "PN38740BM"
LA_LIBERTAD = ("RD38347BM", "RD38343BM")
CINCO_PRIMEROS = ["13", "15", "11", "20", "14"]  # La Libertad, Lima, Ica, Piura y Lambayeque
CINCO_SIN_LIMA = ["13", "11", "20", "14", "06"]  # sin Lima ni Callao entra Cajamarca


def meses(codigo, desde, hasta):
    r = httpx.get(f"{API}/{codigo}/json/{desde}/{hasta}", timeout=60, verify=TLS, follow_redirects=True).json()
    return [float(p["values"][0]) for p in r["periods"] if p["values"][0] != "n.d."]


def bcrp():
    no_t, tr = {}, {}
    for anio in (2020, 2024):
        no_t[anio] = meses(NO_TRADICIONALES, f"{anio}-1", f"{anio}-12")
        tr[anio] = meses(TRADICIONALES, f"{anio}-1", f"{anio}-12")
        assert len(no_t[anio]) == len(tr[anio]) == 12
    total = {a: sum(no_t[a]) + sum(tr[a]) for a in (2020, 2024)}
    libertad = [meses(c, "2022-1", "2022-12") for c in LA_LIBERTAD]
    assert all(len(x) == 12 for x in libertad)
    return total, sum(map(sum, libertad))


def enaho():
    ruta = RAIZ / "datos" / "enaho" / "966-Modulo34.zip"
    with zipfile.ZipFile(ruta) as z:
        s = pd.read_stata(io.BytesIO(z.read("966-Modulo34/sumaria-2024.dta")), convert_categoricals=False,
                          columns=["ubigeo", "pobreza", "factor07", "mieperho"])
    s["dep"] = s["ubigeo"].str[:2]
    s["peso"] = s["factor07"].astype(float) * s["mieperho"].astype(float)
    s["pobre_peso"] = (s["pobreza"] <= 2) * s["peso"]

    def tasa(d):
        return d["pobre_peso"].sum() / d["peso"].sum() * 100

    por_dep = s.groupby("dep")[["pobre_peso", "peso"]].sum()
    por_dep = por_dep["pobre_peso"] / por_dep["peso"] * 100
    fuera = ["15", "07"]
    return {"nacional": tasa(s), "cajamarca": por_dep["06"], "ica": por_dep["11"],
            "cinco": tasa(s[s["dep"].isin(CINCO_PRIMEROS)]), "resto": tasa(s[~s["dep"].isin(CINCO_PRIMEROS)]),
            "cinco_sl": tasa(s[s["dep"].isin(CINCO_SIN_LIMA)]),
            "resto_sl": tasa(s[~s["dep"].isin(CINCO_SIN_LIMA + fuera)]), "por_dep": por_dep}


def rangos(por_dep):
    """Spearman con la biblioteca estándar. El departamento se toma de la posición del código, no del nombre."""
    d = pd.read_csv(RAIZ / "salidas" / "bcrp" / "agro_departamental.csv")
    d = d[(d["periodo"].astype(str) == "2022")]
    numero = d["codigo"].str[2:7].astype(int)
    d = d[numero <= 41372]  # las dos últimas son «sin ubigeo»
    d = d.assign(dep=[f"{(int(c[2:7]) - (40960 if (int(c[2:7]) - 40960) % 17 == 0 else 40964)) // 17 + 1:02d}" for c in d["codigo"]])
    valor = d.groupby("dep")["valor"].sum()
    assert len(valor) == 25
    return statistics.correlation(valor.sort_index().tolist(), por_dep.sort_index().tolist(), method="ranked"), valor


def main():
    total, libertad = bcrp()
    e = enaho()
    rho, valor = rangos(e["por_dep"])
    variacion = (total[2024] / total[2020] - 1) * 100
    filas = [
        ("Agroexportaciones de 2024, millones de US$", 12325.6, total[2024], 0.1, "BCRP",
         f"Suma de los 12 meses de {NO_TRADICIONALES} y {TRADICIONALES}, API del BCRP"),
        ("Agroexportaciones de 2020, millones de US$", 7466.5, total[2020], 0.1, "BCRP",
         f"Suma de los 12 meses de {NO_TRADICIONALES} y {TRADICIONALES}, API del BCRP"),
        ("Crecimiento 2020-2024, %", 65.08, variacion, 0.01, "BCRP", "Calculado con las dos sumas anteriores"),
        ("La Libertad en 2022, millones de US$", 1924.3, libertad, 0.1, "BCRP",
         f"Suma de los 12 meses de {LA_LIBERTAD[0]} y {LA_LIBERTAD[1]}"),
        ("Suma de los 25 departamentos en 2022, millones de US$", 9721.88, float(valor.sum()), 0.01, "BCRP",
         "Suma directa de las series anuales guardadas, con el departamento tomado del código"),
        ("Pobreza nacional 2024, %", 27.58, e["nacional"], 0.01, "ENAHO", "Media ponderada desde sumaria-2024.dta"),
        ("Pobreza de Cajamarca, %", 45.0, e["cajamarca"], 0.05, "ENAHO",
         "Media ponderada desde sumaria-2024.dta; coincide con la cifra publicada por el INEI"),
        ("Pobreza de Ica, %", 6.0, e["ica"], 0.05, "ENAHO", "Media ponderada desde sumaria-2024.dta"),
        ("Pobreza de los 5 primeros, %", 26.0, e["cinco"], 0.05, "Ambas", "Media ponderada desde sumaria-2024.dta"),
        ("Pobreza del resto, %", 29.3, e["resto"], 0.05, "Ambas", "Media ponderada desde sumaria-2024.dta"),
        ("Sin Lima y Callao: 5 primeros, %", 28.1, e["cinco_sl"], 0.05, "Ambas", "Media ponderada desde sumaria-2024.dta"),
        ("Sin Lima y Callao: resto, %", 27.2, e["resto_sl"], 0.05, "Ambas", "Media ponderada desde sumaria-2024.dta"),
        ("Correlación de rangos, 25 departamentos", -0.17, rho, 0.005, "Ambas", "statistics.correlation(method=\"ranked\")"),
    ]
    tabla = ["| Afirmación del informe | Fuente | En el informe | Calculado | Diferencia | ¿Coincide? | Procedimiento |",
             "|---|---|---:|---:|---:|---|---|"]
    fallas = 0
    for texto, informe, calculado, tolerancia, fuente, como in filas:
        dif = calculado - informe
        coincide = abs(dif) <= tolerancia + 1e-9
        fallas += not coincide
        tabla.append(f"| {texto} | {fuente} | {informe:,.2f} | {calculado:,.3f} | {dif:+.3f} | "
                     f"{'Sí' if coincide else '**No**'} | {como} |")
    plantilla = (Path(__file__).parent / "verificacion_plantilla.md").read_text(encoding="utf-8")
    salida = (plantilla.replace("{{FECHA}}", date.today().isoformat()).replace("{{TABLA}}", "\n".join(tabla))
              .replace("{{RESUMEN}}", f"{len(filas) - fallas} de {len(filas)} afirmaciones coinciden.")
              .replace("{{WEB}}", WEB))
    (Path(__file__).parent / "verificacion.md").write_text(salida, encoding="utf-8")
    print("\n".join(tabla))
    print(f"{len(filas) - fallas} de {len(filas)} coinciden")


if __name__ == "__main__":
    main()
