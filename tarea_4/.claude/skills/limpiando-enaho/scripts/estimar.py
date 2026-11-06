"""Estimaciones de pobreza de la ENAHO con factor de expansión y error de muestreo. Es la única fuente de cifras de las
tres Skills: limpiar.py arma con ella indicadores.csv, y graficar.py y mapear.py la importan.

    uv run .claude/skills/limpiando-enaho/scripts/estimar.py --por departamento
    uv run .claude/skills/limpiando-enaho/scripts/estimar.py --por sexo --solo departamento=Puno
    uv run .claude/skills/limpiando-enaho/scripts/estimar.py --por area --indicador pobre_extremo

Dos bases, según la unidad de análisis:
- hogares_2024.parquet: una fila por hogar, peso factor07 × mieperho. Es el método del INEI y da las cifras publicadas.
- personas_2024.parquet: residentes habituales, peso facpob07. Es la única con el sexo y la edad de cada persona.

El error estándar sigue el diseño de la muestra: la UPM es el conglomerado y los estratos son departamento × estrato,
porque la muestra es «estratificada, bietápica e independiente en cada departamento» (Ficha Técnica). Es la
linealización de Taylor de una razón, con reemplazo en la primera etapa: lo mismo que hace `svy` en Stata.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).parents[4]
SALIDAS = RAIZ / "salidas"
ANIO = 2024
Z95 = 1.96
INDICADORES = {"pobre": "Pobreza monetaria", "pobre_extremo": "Pobreza monetaria extrema"}
SOLO_PERSONAS = {"sexo", "grupo_edad", "edad"}
ORDEN_FIJO = {"sexo": ["Mujer", "Hombre"], "grupo_edad": ["0-14", "15-29", "30-44", "45-59", "60 y más"]}
ETIQUETA = {"departamento": "nombre_departamento", "dominio": "nombre_dominio"}
SIN_BASE = (f"Falta la base procesada en {SALIDAS}. Usa primero la skill limpiando-enaho "
            "(uv run .claude/skills/limpiando-enaho/scripts/limpiar.py).")


def cargar(unidad, salidas=SALIDAS):
    """unidad es 'hogares' o 'personas'. Termina con un mensaje explícito si la base no existe."""
    ruta = Path(salidas) / f"{unidad}_{ANIO}.parquet"
    if not ruta.exists():
        raise SystemExit(SIN_BASE)
    return pd.read_parquet(ruta)


def base_para(por, filtros, salidas=SALIDAS):
    """Elige la base por la unidad de análisis: hogares (método del INEI), salvo que el corte exija datos de personas."""
    unidad = "personas" if ({por} | set(filtros)) & SOLO_PERSONAS else "hogares"
    return cargar(unidad, salidas), unidad


def filtrar(df, filtros):
    """Marca el dominio de estudio sin borrar filas: el error estándar necesita todas las UPM de la muestra."""
    dentro = pd.Series(True, index=df.index)
    for columna, valor in filtros.items():
        if columna not in df:
            raise SystemExit(f"La base no tiene la columna {columna!r}. Disponibles: {', '.join(df.columns)}")
        coincide = df[columna].astype(str).str.casefold() == str(valor).casefold()
        if not coincide.any() and columna in ETIQUETA:  # departamento=Puno además de departamento=21
            coincide = df[ETIQUETA[columna]].astype(str).str.casefold() == str(valor).casefold()
        if not coincide.any():
            raise SystemExit(f"Ninguna fila cumple {columna}={valor}. Valores: {sorted(df[columna].astype(str).unique())}")
        dentro &= coincide
    return dentro


def _lineal(df, y, dentro):
    """Variable linealizada de la razón Σwy/Σw sobre un dominio: vale 0 fuera de él."""
    w = df["peso"].to_numpy(float)
    d = dentro.to_numpy(bool)
    v = df[y].to_numpy(float)
    total = w[d].sum()
    razon = (w[d] * v[d]).sum() / total
    return razon, np.where(d, w * (v - razon) / total, 0.0)


def _error_estandar(df, z):
    """Suma por UPM y compara dentro de cada estrato. Un estrato con una sola UPM no aporta varianza."""
    t = pd.DataFrame({"estrato": df["estrato_diseno"].to_numpy(), "upm": df["conglome"].to_numpy(), "z": z})
    t = t.groupby(["estrato", "upm"], observed=True)["z"].sum().reset_index()
    g = t.groupby("estrato", observed=True)["z"]
    n = g.transform("size")
    aporte = (t["z"] - g.transform("mean")) ** 2 * n / (n - 1)
    return float(np.sqrt(aporte[n > 1].sum()))


def fila(df, y, dentro):
    """Una estimación en %: valor, error estándar, IC 95 %, coeficiente de variación y tamaños."""
    razon, z = _lineal(df, y, dentro)
    ee = _error_estandar(df, z)
    return {"pct": razon * 100, "ee": ee * 100, "ic95_inf": max(razon - Z95 * ee, 0) * 100,
            "ic95_sup": min(razon + Z95 * ee, 1) * 100, "cv_pct": ee / razon * 100 if razon else np.nan,
            "n_muestra": int(dentro.sum()), "upm": int(df.loc[dentro, "conglome"].nunique()),
            "poblacion": float(df.loc[dentro, "peso"].sum())}


def tabla(df, por=None, y="pobre", dentro=None):
    """Estimaciones de y por cada categoría de `por` (o del conjunto, si por es None) dentro del dominio."""
    dentro = pd.Series(True, index=df.index) if dentro is None else dentro
    if por is None:
        return pd.DataFrame([{"codigo": "", "categoria": "Perú"} | fila(df, y, dentro)])
    etiqueta = ETIQUETA.get(por, por)
    claves = df.loc[dentro, [por, etiqueta]].drop_duplicates().itertuples(index=False)
    t = pd.DataFrame([{"codigo": str(c), "categoria": str(e)} | fila(df, y, dentro & (df[por] == c)) for c, e in claves])
    if por in ORDEN_FIJO:
        return t.set_index("categoria").reindex(ORDEN_FIJO[por]).dropna(subset="pct").reset_index()[t.columns]
    return t.sort_values("pct", ascending=False, ignore_index=True)


def diferencia(df, y, a, b):
    """Diferencia a − b en puntos porcentuales con su IC 95 %. Tiene en cuenta que a y b comparten hogares y
    conglomerados, así que no equivale a mirar si se cruzan los dos intervalos por separado."""
    ra, za = _lineal(df, y, a)
    rb, zb = _lineal(df, y, b)
    ee = _error_estandar(df, za - zb)
    d = ra - rb
    return {"dif": d * 100, "ee": ee * 100, "ic95_inf": (d - Z95 * ee) * 100, "ic95_sup": (d + Z95 * ee) * 100,
            "distinguible": bool(abs(d) > Z95 * ee)}


def separar_filtros(pares):
    filtros = {}
    for par in pares or []:
        if "=" not in par:
            raise SystemExit(f"--solo espera columna=valor y recibió {par!r}")
        columna, valor = par.split("=", 1)
        filtros[columna.strip()] = valor.strip()
    return filtros


def nota_metodo(unidad):
    return ("sumaria, hogares ponderados con factor07 × mieperho" if unidad == "hogares"
            else "residentes habituales ponderados con facpob07")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--por", choices=["area", "dominio", "departamento", "sexo", "grupo_edad"], help="sin esto, el total")
    p.add_argument("--indicador", default="pobre", choices=list(INDICADORES))
    p.add_argument("--solo", action="append", metavar="COLUMNA=VALOR", help="restringe el dominio; se puede repetir")
    a = p.parse_args()
    filtros = separar_filtros(a.solo)
    df, unidad = base_para(a.por, filtros)
    t = tabla(df, a.por, a.indicador, filtrar(df, filtros)).round(2)
    print(f"{INDICADORES[a.indicador]}, % de personas, ENAHO {ANIO}. Base: {nota_metodo(unidad)}.")
    if filtros:
        print("Dominio:", ", ".join(f"{k}={v}" for k, v in filtros.items()))
    print(t.to_string(index=False))
    referenciales = t.loc[t["cv_pct"] > 15, "categoria"].tolist()
    if referenciales:
        print("Coeficiente de variación mayor a 15 %, cifra solo referencial:", ", ".join(referenciales))


if __name__ == "__main__":
    main()
