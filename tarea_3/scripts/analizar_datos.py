"""Calcula los indicadores del subempleo por ingresos y escribe los datos del dashboard.

Entradas:
  - datos/procesados/pea_2019_2025.parquet (de procesar_datos.py, ENAHO 2019-2025)
  - datos/originales/inei_epe_lima/series_empleo_lima_metropolitana.xlsx (INEI, EPE Lima)

Salidas:
  - datos/procesados/serie_nacional.csv, tasas_departamento.csv, cambio_departamento_2024_2025.csv,
    tasas_grupos.csv, serie_lima_epe.csv, hallazgos.txt
  - web/data/datos.json (todo lo que usa el dashboard)

Toda cifra de la ENAHO va ponderada con fac500a. Los errores estándar tratan al conglomerado
como unidad primaria de muestreo (sin estratos, por eso son algo conservadores); un cambio es
«significativo» si |z| >= 1,96.

Uso:
    python scripts/analizar_datos.py            # desde tarea_3/
"""
from __future__ import annotations

import json
import shutil
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROCESADOS = RAIZ / "datos" / "procesados"
EPE = RAIZ / "datos" / "originales" / "inei_epe_lima" / "series_empleo_lima_metropolitana.xlsx"
WEB_DATA = RAIZ / "web" / "data"
GEOJSON = RAIZ / "datos" / "originales" / "peru_departamental_simple.geojson"

ANIO_BASE, ANIO_FIN = 2024, 2025
INDICADORES = {"sub_ingresos": "si", "sub_horas": "sh", "adecuado": "ad"}


def tasa_y_error(d: pd.DataFrame, col: str) -> tuple[float, float]:
    """Proporción ponderada (en %) y su error estándar por conglomerados."""
    w = d.fac500a.to_numpy()
    y = d[col].to_numpy(dtype=float)
    total = w.sum()
    p = (w * y).sum() / total
    z = pd.Series(w * (y - p)).groupby(d.conglome.to_numpy()).sum()
    n = len(z)
    se = np.sqrt(n / (n - 1) * (z ** 2).sum()) / total if n > 1 else np.nan
    return p * 100, se * 100


def mediana_ponderada(x: pd.Series, w: pd.Series) -> float:
    orden = np.argsort(x.to_numpy())
    xs, ws = x.to_numpy()[orden], w.to_numpy()[orden]
    acum = np.cumsum(ws) / ws.sum()
    return float(xs[np.searchsorted(acum, 0.5)])


def serie_nacional(base: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for anio, d in base.groupby("anio"):
        o = d[d.ocupado]
        si, se = tasa_y_error(d, "sub_ingresos")
        filas.append({
            "anio": anio,
            "pea_miles": d.fac500a.sum() / 1e3,
            "ocupados_miles": o.fac500a.sum() / 1e3,
            "sub_ingresos_miles": (d.sub_ingresos * d.fac500a).sum() / 1e3,
            "tasa_sub_ingresos": si, "se_sub_ingresos": se,
            "tasa_sub_horas": tasa_y_error(d, "sub_horas")[0],
            "tasa_adecuado": tasa_y_error(d, "adecuado")[0],
            "tasa_desempleo": 100 - tasa_y_error(d, "ocupado")[0],
            "tasa_sub_ingresos_solo_principal": tasa_y_error(d, "sub_ingresos_principal")[0],
            "tasa_sub_ingresos_con_especie": tasa_y_error(d, "sub_ingresos_amplio")[0],
            "imr_promedio": float(np.average(o.imr, weights=o.fac500a)),
            "imr_lima_metropolitana": float(o.loc[o.dominio == "Lima Metropolitana", "imr"].iloc[0]),
            "ingreso_mediano": mediana_ponderada(o.ingreso_mensual, o.fac500a),
            "ingreso_mediano_subempleados": mediana_ponderada(
                o.loc[o.sub_ingresos, "ingreso_mensual"], o.loc[o.sub_ingresos, "fac500a"]),
            "encuestados_pea": len(d),
        })
    return pd.DataFrame(filas)


def cubo(base: pd.DataFrame) -> list[dict]:
    """Año × departamento (00 = Perú) × sexo × área: tasas para los filtros del dashboard."""
    filas = []
    sexos = {"T": None, "H": "Hombre", "M": "Mujer"}
    areas = {"T": None, "U": "Urbana", "R": "Rural"}
    for anio, da in base.groupby("anio"):
        for dep in ["00"] + sorted(da.departamento.unique()):
            dd = da if dep == "00" else da[da.departamento == dep]
            for ks, sexo in sexos.items():
                ds = dd if sexo is None else dd[dd.sexo == sexo]
                for kz, area in areas.items():
                    d = ds if area is None else ds[ds.area == area]
                    if len(d) < 30:      # muy pocos encuestados: no se publica
                        continue
                    fila = {"a": int(anio), "d": dep, "s": ks, "z": kz, "n": len(d),
                            "pea": round(d.fac500a.sum() / 1e3, 1),
                            "mi": round((d.sub_ingresos * d.fac500a).sum() / 1e3, 1)}
                    for col, k in INDICADORES.items():
                        p, se = tasa_y_error(d, col)
                        fila[k] = round(p, 2)
                        if col == "sub_ingresos":
                            fila["se"] = round(se, 2)
                    fila["de"] = round(100 - tasa_y_error(d, "ocupado")[0], 2)
                    filas.append(fila)
    return filas


def cambio_departamental(base: pd.DataFrame, nombres: dict) -> pd.DataFrame:
    filas = []
    for dep, d in base[base.anio.isin([ANIO_BASE, ANIO_FIN])].groupby("departamento"):
        p0, s0 = tasa_y_error(d[d.anio == ANIO_BASE], "sub_ingresos")
        p1, s1 = tasa_y_error(d[d.anio == ANIO_FIN], "sub_ingresos")
        dif = p1 - p0
        z = dif / np.hypot(s0, s1)
        filas.append({"departamento": dep, "nombre": nombres[dep],
                      f"tasa_{ANIO_BASE}": round(p0, 2), f"tasa_{ANIO_FIN}": round(p1, 2),
                      "cambio_pp": round(dif, 2), "z": round(z, 2),
                      "significativo": bool(abs(z) >= 1.96),
                      "encuestados_2025": int((d.anio == ANIO_FIN).sum())})
    return pd.DataFrame(filas).sort_values("cambio_pp", ascending=False)


def tasas_grupos(base: pd.DataFrame) -> pd.DataFrame:
    """Tasa por grupo y año. Sector y categoría solo existen para ocupados: % de ocupados."""
    filas = []
    for var in ["sexo", "area", "grupo_edad", "educacion", "dominio", "sector"]:
        datos = base[base.ocupado] if var == "sector" else base
        for (anio, grupo), d in datos.groupby(["anio", var]):
            if grupo in ("Sin dato", "Desocupado") or len(d) < 30:
                continue
            p, se = tasa_y_error(d, "sub_ingresos")
            filas.append({"variable": var, "grupo": grupo, "anio": anio, "tasa": round(p, 2),
                          "se": round(se, 2), "base": "ocupados" if var == "sector" else "PEA",
                          "encuestados": len(d)})
    return pd.DataFrame(filas)


def serie_lima_epe() -> pd.DataFrame:
    """Subempleo por ingresos en Lima Metropolitana por trimestre móvil (EPE del INEI).

    Las columnas de cada hoja son trimestres móviles consecutivos; la última es
    jul-ago-set 2026. Se fecha cada columna por su mes final contando hacia atrás.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sub = pd.read_excel(EPE, sheet_name="Subempl", header=None)
        ind = pd.read_excel(EPE, sheet_name="Indicad.", header=None)

    def fila(hoja: pd.DataFrame, bloque: str, etiqueta: str) -> pd.Series:
        col0 = hoja[0].astype(str).str.strip()
        ini = col0[col0.str.startswith(bloque)].index[0]
        idx = col0[(col0.index > ini) & (col0 == etiqueta)].index[0]
        valores = hoja.loc[idx, 1:]
        ultima = hoja.loc[6, 1:].last_valid_index()
        valores = pd.to_numeric(valores.loc[:ultima], errors="coerce")
        fin = pd.Period("2026-09", "M")
        valores.index = [fin - (ultima - c) for c in valores.index]
        return valores

    # La etiqueta del último encabezado confirma la fecha asumida
    for hoja in (sub, ind):
        etiqueta = "".join(str(hoja.loc[6, hoja.loc[6].last_valid_index()]).split())
        assert etiqueta.startswith("Jul/Ago/Set"), etiqueta
    df = pd.DataFrame({
        "sub_ingresos_miles": fila(sub, "SUBEMPLEO POR INGRESOS", "Total"),
        "sub_ingresos_mujeres": fila(sub, "SUBEMPLEO POR INGRESOS", "Mujer"),
        "sub_ingresos_hombres": fila(sub, "SUBEMPLEO POR INGRESOS", "Hombre"),
        "sub_ingresos_universitarios": fila(sub, "SUBEMPLEO POR INGRESOS", "Superior Universitaria"),
        "subempleo_total_miles": fila(sub, "SUBEMPLEADOS", "Total"),
    })
    pea = fila(ind, "PEA", "Total")
    df["pea_miles"] = pea.reindex(df.index)
    df["tasa_sub_ingresos"] = df.sub_ingresos_miles / df.pea_miles * 100
    df["var_interanual_pct"] = df.sub_ingresos_miles.pct_change(12, fill_method=None) * 100
    df["var_interanual_miles"] = df.sub_ingresos_miles.diff(12)
    df = df[df.index >= pd.Period("2018-03", "M")]       # marco muestral nuevo desde 2018
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"]
    df.insert(0, "trimestre", [f"{meses[(p - 2).month - 1]}-{meses[(p - 1).month - 1]}-"
                               f"{meses[p.month - 1]} {p.year}" for p in df.index])
    df.index = df.index.astype(str)
    df.index.name = "mes_final"
    return df.round(2)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    base = pd.read_parquet(PROCESADOS / "pea_2019_2025.parquet")
    nombres = base.drop_duplicates("departamento").set_index("departamento").nombre_departamento.to_dict()

    nac = serie_nacional(base)
    dep = cambio_departamental(base, nombres)
    grupos = tasas_grupos(base)
    lima = serie_lima_epe()
    cub = cubo(base)

    nac.round(3).to_csv(PROCESADOS / "serie_nacional.csv", index=False)
    dep.to_csv(PROCESADOS / "cambio_departamento_2024_2025.csv", index=False)
    grupos.to_csv(PROCESADOS / "tasas_grupos.csv", index=False)
    lima.to_csv(PROCESADOS / "serie_lima_epe.csv")
    pd.DataFrame([c for c in cub if c["s"] == "T" and c["z"] == "T" and c["d"] != "00"]) \
        .assign(nombre=lambda t: t.d.map(nombres)) \
        .to_csv(PROCESADOS / "tasas_departamento.csv", index=False)

    n0 = nac.set_index("anio").loc[ANIO_BASE]
    n1 = nac.set_index("anio").loc[ANIO_FIN]
    z_nac = (n1.tasa_sub_ingresos - n0.tasa_sub_ingresos) / np.hypot(n0.se_sub_ingresos, n1.se_sub_ingresos)
    ult = lima.iloc[-1]
    g25 = grupos[(grupos.anio == ANIO_FIN)].set_index(["variable", "grupo"]).tasa
    hallazgos = [
        f"1. Perú {ANIO_BASE}->{ANIO_FIN}: {n0.tasa_sub_ingresos:.1f}% -> {n1.tasa_sub_ingresos:.1f}% "
        f"de la PEA ({n1.tasa_sub_ingresos - n0.tasa_sub_ingresos:+.1f} pp, z = {z_nac:.1f}); "
        f"{n0.sub_ingresos_miles / 1e3:.2f} -> {n1.sub_ingresos_miles / 1e3:.2f} millones.",
        f"   Pico 2020: {nac.set_index('anio').loc[2020].tasa_sub_ingresos:.1f}%; 2019: "
        f"{nac.set_index('anio').loc[2019].tasa_sub_ingresos:.1f}%.",
        f"   Sensibilidad: solo ocupación principal {n0.tasa_sub_ingresos_solo_principal:.1f} -> "
        f"{n1.tasa_sub_ingresos_solo_principal:.1f}; con especie {n0.tasa_sub_ingresos_con_especie:.1f} -> "
        f"{n1.tasa_sub_ingresos_con_especie:.1f}.",
        f"2. Departamentos que subieron: {', '.join(f'{r.nombre} ({r.cambio_pp:+.1f} pp, z={r.z:.1f})' for r in dep[dep.cambio_pp > 0].itertuples())}; "
        f"bajaron {int((dep.cambio_pp < 0).sum())} de 25 ({int(((dep.cambio_pp < 0) & dep.significativo).sum())} con cambio significativo).",
        f"   Mayor tasa {ANIO_FIN}: {dep.sort_values(f'tasa_{ANIO_FIN}').iloc[-1].nombre} "
        f"({dep[f'tasa_{ANIO_FIN}'].max():.1f}%); menor: {dep.sort_values(f'tasa_{ANIO_FIN}').iloc[0].nombre} "
        f"({dep[f'tasa_{ANIO_FIN}'].min():.1f}%).",
        f"3. Brecha {ANIO_FIN}: mujeres {g25['sexo', 'Mujer']:.1f}% frente a hombres {g25['sexo', 'Hombre']:.1f}%; "
        f"rural {g25['area', 'Rural']:.1f}% frente a urbano {g25['area', 'Urbana']:.1f}%; "
        f"universitaria {g25['educacion', 'Universitaria']:.1f}% frente a primaria o menos {g25['educacion', 'Primaria o menos']:.1f}%.",
        f"4. Lima Metropolitana (EPE) {ult.trimestre}: {ult.sub_ingresos_miles:,.1f} mil subempleados por ingresos "
        f"({ult.tasa_sub_ingresos:.1f}% de la PEA), {ult.var_interanual_pct:+.1f}% interanual "
        f"({ult.var_interanual_miles:+,.1f} mil).",
    ]
    (PROCESADOS / "hallazgos.txt").write_text("\n".join(hallazgos) + "\n", encoding="utf-8")
    print("\n".join(hallazgos))

    WEB_DATA.mkdir(parents=True, exist_ok=True)
    datos = {
        "meta": {
            "titulo": "Trabajar y no alcanzar: el subempleo por ingresos en el Perú",
            "anio_base": ANIO_BASE, "anio_fin": ANIO_FIN,
            "fuente_enaho": "INEI, Encuesta Nacional de Hogares (ENAHO) 2019-2025, módulos 05 y 34",
            "fuente_epe": "INEI, Encuesta Permanente de Empleo (EPE), Series de Empleo Lima Metropolitana",
            "corte_epe": ult.trimestre,
            "departamentos": nombres,
        },
        "nacional": nac.round(3).to_dict(orient="records"),
        "cubo": cub,
        "cambio": dep.to_dict(orient="records"),
        "grupos": grupos.to_dict(orient="records"),
        "lima": lima.reset_index().to_dict(orient="records"),
    }
    texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"), allow_nan=False,
                       default=lambda v: None if pd.isna(v) else v)
    (WEB_DATA / "datos.json").write_text(texto, encoding="utf-8")
    # Copias .js para que el dashboard abra también con doble clic (file://), sin servidor
    (WEB_DATA / "datos.js").write_text(f"window.DATOS = {texto};\n", encoding="utf-8")
    if GEOJSON.exists():
        shutil.copy(GEOJSON, WEB_DATA / "peru_departamentos.geojson")
        geo = GEOJSON.read_text(encoding="utf-8")
        (WEB_DATA / "peru_departamentos.js").write_text(f"window.GEO = {geo};\n", encoding="utf-8")
    print(f"Listo: web/data/datos.json ({len(texto) / 1e3:.0f} KB, {len(cub)} celdas en el cubo)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
