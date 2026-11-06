"""Cruza series del BCRP por departamento con la pobreza monetaria de la ENAHO 2024.

    uv run .claude/skills/investigando-peru/scripts/cruzar.py --datos salidas/bcrp/agroexportaciones_departamento.csv \
        --nacional salidas/agroexportaciones_anual.csv --anio 2022 --tema agroexportaciones --unidad "millones de US$"

Entra el CSV de la herramienta MCP guardar_series, ya con una o más series por departamento. Sale
salidas/cruce_<tema>.csv, salidas/cruce_<tema>.json y figuras/cruce_<tema>.png.

Las series regionales del BCRP no traen ubigeo: su departamento solo aparece en el nombre. Por eso aquí se compara el
nombre sin tildes contra el código del INEI, y se exige que las 25 unidades queden identificadas una por una. Las series
que no son de un departamento, como «sin ubigeo», se apartan y se informan.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patheffects import withStroke  # noqa: E402

sys.path.insert(0, str(Path(__file__).parents[2] / "limpiando-enaho" / "scripts"))
from estimar import ANIO, RAIZ, SALIDAS, cargar, diferencia, fila, tabla  # noqa: E402
from limpiar import DEPARTAMENTOS  # noqa: E402

SUPERFICIE, TEXTO, TEXTO_2, REJILLA, COLOR = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e0", "#2a78d6"
DATOS_POR_ANIO = {"Anual": 1, "Trimestral": 4, "Mensual": 12}
TOLERANCIA_TOTAL = 0.5  # %, frente al total nacional
PERMUTACIONES = 20_000
SEMILLA = 2024


# Puntos en casi el mismo lugar: desplazamiento de la etiqueta en puntos y alineación
ETIQUETAS = {"Pasco": (-6, 3, "right"), "Huánuco": (6, -10, "left"), "San Martín": (-6, 3, "right"),
             "Ucayali": (6, 7, "left"), "Tumbes": (6, -11, "left"), "Lima": (6, -11, "left")}


def coma(x, d=1):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def _normal(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c))


NOMBRES = {_normal(n): c for c, n in DEPARTAMENTOS.items()}


def departamento_de(nombre_serie):
    """Código del departamento que nombra la serie, o None si no nombra exactamente uno."""
    texto = _normal(nombre_serie)
    hallados = [c for n, c in NOMBRES.items() if re.search(rf"\b{re.escape(n)}\b", texto)]
    return hallados[0] if len(hallados) == 1 else None


def leer_bcrp(d, anio):
    """Suma por departamento un año completo. Devuelve (Series por código, dinero fuera de los departamentos)."""
    d = d.assign(anio=d["periodo"].astype(str).str[:4].astype(int), departamento=d["nombre"].map(departamento_de))
    d = d[d["anio"] == anio]
    if d.empty:
        raise SystemExit(f"El archivo no tiene datos de {anio}.")
    conteo = d.groupby("codigo").size()
    esperado = d.groupby("codigo")["frecuencia"].first().map(DATOS_POR_ANIO)
    if (conteo != esperado).any():
        raise SystemExit(f"Hay series con {anio} incompleto: {conteo[conteo != esperado].to_dict()}")
    fuera = float(d.loc[d["departamento"].isna(), "valor"].sum())
    valor = d.dropna(subset="departamento").groupby("departamento")["valor"].sum()
    faltan = sorted(set(DEPARTAMENTOS) - set(valor.index))
    if faltan:
        raise SystemExit(f"Faltan {len(faltan)} departamentos en el archivo: {[DEPARTAMENTOS[c] for c in faltan]}")
    return valor, fuera


def spearman(x, y, n=PERMUTACIONES, semilla=SEMILLA):
    """Correlación de rangos y su p-valor por permutaciones: no supone ninguna distribución y sirve con 25 unidades."""
    rx, ry = pd.Series(x).rank().to_numpy(), pd.Series(y).rank().to_numpy()
    rho = float(np.corrcoef(rx, ry)[0, 1])
    azar = np.random.default_rng(semilla)
    extremos = sum(abs(np.corrcoef(rx, azar.permutation(ry))[0, 1]) >= abs(rho) - 1e-12 for _ in range(n))
    return {"rho": rho, "p_valor": (extremos + 1) / (n + 1), "n": len(x)}


def comparar_grupo(h, codigos):
    """Pobreza del grupo de departamentos y del resto, con el intervalo de su diferencia según el diseño de la muestra."""
    a = h["departamento"].isin(codigos)
    return {"grupo": fila(h, "pobre", a), "resto": fila(h, "pobre", ~a), "diferencia": diferencia(h, "pobre", a, ~a)}


def cruzar(valor, h, escala, top):
    t = tabla(h, "departamento").rename(columns={"codigo": "departamento", "categoria": "nombre", "pct": "pobreza_pct"})
    t = t.merge(valor.rename("valor").rename_axis("departamento").reset_index(), on="departamento", how="outer",
                validate="1:1")
    if t[["valor", "pobreza_pct"]].isna().any().any():
        raise SystemExit("La unión por código no dio 25 departamentos con las dos cifras.")
    t["por_habitante"] = t["valor"] * escala / t["poblacion"]
    t["participacion_pct"] = t["valor"] / t["valor"].sum() * 100
    t = t.sort_values("valor", ascending=False, ignore_index=True)
    t["puesto"] = t.index + 1
    primeros = t["departamento"].head(top).tolist()
    sin_lima = t[~t["departamento"].isin(["15", "07"])]
    primeros_sin_lima = sin_lima["departamento"].head(top).tolist()
    resumen = {
        "departamentos": len(t),
        "primeros": t["nombre"].head(top).tolist(),
        "participacion_primeros_pct": float(t["participacion_pct"].head(top).sum()),
        "spearman_valor": spearman(t["valor"], t["pobreza_pct"]),
        "spearman_por_habitante": spearman(t["por_habitante"], t["pobreza_pct"]),
        "spearman_valor_sin_lima_callao": spearman(sin_lima["valor"], sin_lima["pobreza_pct"]),
        "comparacion_primeros": comparar_grupo(h, primeros),
        "primeros_sin_lima_callao": sin_lima["nombre"].head(top).tolist(),
        "comparacion_sin_lima_callao": comparar_grupo(h[~h["departamento"].isin(["15", "07"])], primeros_sin_lima),
    }
    return t, resumen


def sensibilidad(d, anio, h, escala, top):
    """Repite el cruce con cada grupo de productos por separado: muestra si el resultado depende de la definición."""
    productos = d["nombre"].str.rsplit(") - ", n=1).str[-1]
    if productos.nunique() < 2:
        return {}
    salida = {}
    for producto, parte in d.groupby(productos):
        valor, _ = leer_bcrp(parte, anio)
        _, r = cruzar(valor, h, escala, top)
        salida[producto] = {k: r[k] for k in ("primeros", "spearman_valor", "primeros_sin_lima_callao")} | {
            "diferencia_primeros": r["comparacion_primeros"]["diferencia"],
            "diferencia_sin_lima_callao": r["comparacion_sin_lima_callao"]["diferencia"]}
    return salida


def dibujar(t, r, tema, unidad, anio, top, nacional, ruta):
    fig, ax = plt.subplots(figsize=(9, 6.6), facecolor=SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)
    ax.set_xscale("log")
    primeros = t["puesto"] <= top
    ax.vlines(t["valor"], t["ic95_inf"], t["ic95_sup"], color=REJILLA, linewidth=1.4, zorder=1)
    ax.axhline(nacional, color=TEXTO_2, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
    ax.scatter(t.loc[~primeros, "valor"], t.loc[~primeros, "pobreza_pct"], s=44, color="#9ec5f4", edgecolor=SUPERFICIE,
               linewidth=1.2, zorder=3, label="Resto de departamentos")
    ax.scatter(t.loc[primeros, "valor"], t.loc[primeros, "pobreza_pct"], s=62, color=COLOR, edgecolor=SUPERFICIE,
               linewidth=1.2, zorder=4, label=f"Los {top} que más exportan")
    halo = [withStroke(linewidth=2.5, foreground=SUPERFICIE)]
    for f in t.itertuples():
        dx, dy, alineacion = ETIQUETAS.get(f.nombre, (6, 4, "left"))
        ax.annotate(f.nombre, (f.valor, f.pobreza_pct), xytext=(dx, dy), textcoords="offset points", fontsize=7.5,
                    ha=alineacion, color=TEXTO if f.puesto <= top else TEXTO_2, path_effects=halo, zorder=5)
    ax.text(t["valor"].min() * 0.8, nacional + 0.6, f"Perú: {coma(nacional)} %", fontsize=8.5, color=TEXTO_2, path_effects=halo)
    ax.set_xlabel(f"{tema.capitalize()} en {anio} ({unidad}, escala logarítmica)", fontsize=9.5, color=TEXTO_2)
    ax.set_ylabel(f"Pobreza monetaria en {ANIO} (% de personas)", fontsize=9.5, color=TEXTO_2)
    ax.set_ylim(0, max(t["ic95_sup"].max() * 1.05, 10))
    ax.set_xlim(t["valor"].min() * 0.7, t["valor"].max() * 2.2)
    ax.xaxis.set_major_formatter(lambda v, _: coma(v, 0))
    ax.tick_params(colors=TEXTO_2, labelsize=9, length=0)
    ax.grid(color=REJILLA, linewidth=0.6, zorder=0)
    for lado in ("top", "right", "left", "bottom"):
        ax.spines[lado].set_visible(False)
    ax.legend(frameon=False, loc="lower left", fontsize=9, labelcolor=TEXTO)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.82, bottom=0.14)
    c, sl, s = r["comparacion_primeros"], r["comparacion_sin_lima_callao"], r["spearman_valor"]
    sin_lima = "distinguible" if sl["diferencia"]["distinguible"] else "no distinguible"
    fig.text(0.02, 0.975, f"Los {top} departamentos que más {tema_verbo(tema)} tienen {coma(c['grupo']['pct'])} % de pobreza; "
                          f"el resto, {coma(c['resto']['pct'])} %", fontsize=12.5, fontweight="bold", color=TEXTO, va="top")
    fig.text(0.02, 0.925, f"Diferencia con 95 % de confianza: de {coma(c['diferencia']['ic95_inf'])} a "
                          f"{coma(c['diferencia']['ic95_sup'])} puntos. Sin Lima y Callao: {coma(sl['grupo']['pct'])} % "
                          f"frente a {coma(sl['resto']['pct'])} %, diferencia {sin_lima}.\n"
                          f"Correlación de rangos: {coma(s['rho'], 2)} (p = {coma(s['p_valor'], 2)}, n = {s['n']}). Es una "
                          "asociación entre años distintos, no una relación causal.", fontsize=8.8, color=TEXTO_2, va="top",
             linespacing=1.4)
    fig.text(0.02, 0.02, f"Fuente: BCRP (series regionales, {anio}) e INEI, ENAHO {ANIO} (módulo 34), ponderado con "
                         "factor07 × mieperho. Línea gris: intervalo de 95 %. Elaboración propia.", fontsize=7.5,
             color=TEXTO_2, va="bottom")
    ruta.parent.mkdir(exist_ok=True)
    fig.savefig(ruta, dpi=200, facecolor=SUPERFICIE)
    plt.close(fig)


def tema_verbo(tema):
    return "agroexportan" if tema == "agroexportaciones" else f"registran en {tema}"


def contrastar(valor, nacional, anio):
    """La suma de los departamentos frente al total nacional del mismo año, calculado de otra serie."""
    if nacional is None:
        return None
    n = pd.read_csv(nacional).set_index("anio")
    if anio not in n.index:
        raise SystemExit(f"{nacional} no tiene el año {anio}.")
    total, suma = float(n.loc[anio, "total"]), float(valor.sum())
    dif = (suma / total - 1) * 100
    return {"suma_departamentos": suma, "total_nacional": total, "diferencia_pct": dif,
            "coincide": bool(abs(dif) <= TOLERANCIA_TOTAL)}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datos", type=Path, required=True, help="CSV de guardar_series con las series por departamento")
    p.add_argument("--nacional", type=Path, help="tabla anual de graficar_bcrp.py, para contrastar el total")
    p.add_argument("--anio", type=int, required=True, help="año de la serie del BCRP")
    p.add_argument("--tema", required=True, help="una palabra para los títulos y los archivos")
    p.add_argument("--unidad", required=True)
    p.add_argument("--escala", type=float, default=1e6, help="para pasar el valor a unidades por habitante")
    p.add_argument("--top", type=int, default=5)
    a = p.parse_args()
    if not a.datos.exists():
        raise SystemExit(f"No existe {a.datos}. Guarda antes las series con la herramienta MCP guardar_series.")
    datos = pd.read_csv(a.datos)
    valor, fuera = leer_bcrp(datos, a.anio)
    contraste = contrastar(valor, a.nacional, a.anio)
    if contraste and not contraste["coincide"]:
        raise SystemExit(f"La suma de los departamentos no cuadra con el total nacional: {contraste}")
    h = cargar("hogares")
    t, r = cruzar(valor, h, a.escala, a.top)
    r |= {"anio_bcrp": a.anio, "anio_enaho": ANIO, "unidad": a.unidad, "fuera_de_departamentos": fuera,
          "contraste_con_total_nacional": contraste, "pobreza_nacional_pct": fila(h, "pobre", pd.Series(True, index=h.index))["pct"],
          "sensibilidad_por_producto": sensibilidad(datos, a.anio, h, a.escala, a.top)}
    columnas = ["puesto", "departamento", "nombre", "valor", "participacion_pct", "por_habitante", "poblacion",
                "pobreza_pct", "ic95_inf", "ic95_sup", "cv_pct"]
    t[columnas].round(2).to_csv(SALIDAS / f"cruce_{a.tema}.csv", index=False, encoding="utf-8")
    (SALIDAS / f"cruce_{a.tema}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    ruta = RAIZ / "figuras" / f"cruce_{a.tema}.png"
    dibujar(t, r, a.tema, a.unidad, a.anio, a.top, r["pobreza_nacional_pct"], ruta)
    print(f"Guardado: {ruta.relative_to(RAIZ).as_posix()}, salidas/cruce_{a.tema}.csv y salidas/cruce_{a.tema}.json")
    print(t[columnas[:8]].round(2).to_string(index=False))
    print(json.dumps(r, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
