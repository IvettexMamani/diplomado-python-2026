"""Pruebas de la integración: la herramienta guardar_series, que pasa datos del MCP a los scripts, y el cruce.

    uv run pytest pruebas

Las de guardar_series piden datos reales al BCRP, así que necesitan internet.
"""
import asyncio
import sys
from pathlib import Path

import pandas as pd
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

RAIZ = Path(__file__).parent.parent
SKILLS = RAIZ / ".claude" / "skills"
sys.path[:0] = [str(RAIZ / "mcp"), str(SKILLS / "limpiando-enaho" / "scripts"), str(SKILLS / "investigando-peru" / "scripts")]

import cruzar  # noqa: E402
import estimar  # noqa: E402
import graficar_bcrp  # noqa: E402
import server  # noqa: E402
from limpiar import DEPARTAMENTOS  # noqa: E402


def llamar(herramienta, **argumentos):
    async def ir():
        async with Client(server.mcp) as cliente:
            return (await cliente.call_tool(herramienta, argumentos)).data
    return asyncio.run(ir())


@pytest.fixture
def carpeta(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "SALIDAS_BCRP", tmp_path)
    return tmp_path


def test_guardar_series_escribe_las_mismas_cifras_que_devuelve_serie(carpeta):
    r = llamar("guardar_series", codigos=["PN38744BM", "pn38740bm"], desde="2024-01", hasta="2024-12", nombre="agro")
    assert r["archivo"] == "salidas/bcrp/agro.csv" and r["filas"] == 24 and r["sin_datos"] == []
    d = pd.read_csv(carpeta / "agro.csv")
    assert set(d["codigo"]) == {"PN38744BM", "PN38740BM"}
    assert list(d.columns) == ["codigo", "nombre", "frecuencia", "periodo", "valor", "fuente_web"]
    directo = llamar("serie", codigo="PN38744BM", desde="2024-01", hasta="2024-12")["datos"]
    assert d[d["codigo"] == "PN38744BM"]["valor"].tolist() == [x["valor"] for x in directo]


def test_guardar_series_informa_las_series_sin_datos_sin_detenerse(carpeta):
    r = llamar("guardar_series", codigos=["RD38313BM", "PN38744BM"], desde="2024-01", hasta="2024-12", nombre="parcial")
    assert r["filas"] == 12
    assert r["sin_datos"][0]["codigo"] == "RD38313BM" and "no tiene datos" in r["sin_datos"][0]["motivo"]
    with pytest.raises(ToolError, match="Ninguna serie"):
        llamar("guardar_series", codigos=["RD38313BM"], desde="2024-01", hasta="2024-12", nombre="vacio")
    assert not (carpeta / "vacio.csv").exists()


def test_guardar_series_no_acepta_rutas_ni_demasiados_codigos(carpeta):
    with pytest.raises(ToolError, match="no sirve"):
        llamar("guardar_series", codigos=["PN38744BM"], desde="2024", nombre="../fuera")
    with pytest.raises(ToolError, match="máximo"):
        llamar("guardar_series", codigos=[f"PN{i:05d}BM" for i in range(61)], desde="2024", nombre="muchos")


SIN_TILDE = {"02": "Ancash", "03": "Apurimac", "10": "Huanuco"}  # así los escribe el BCRP


def serie_de(codigo, departamento, valor, anio=2022, frecuencia="Anual"):
    return {"codigo": codigo, "nombre": f"Exportaciones por grupo de productos de {departamento} (Valores FOB) - Agropecuarios",
            "frecuencia": frecuencia, "periodo": str(anio), "valor": valor}


def panel(omitir=()):
    filas = [serie_de(f"A{c}", SIN_TILDE.get(c, n), float(c)) for c, n in DEPARTAMENTOS.items() if c not in omitir]
    return pd.DataFrame(filas + [serie_de("B13", "La Libertad", 5.0), serie_de("X", "sin ubigeo", 7.0)])


def test_cada_departamento_se_identifica_por_su_codigo():
    for codigo, nombre in DEPARTAMENTOS.items():
        assert cruzar.departamento_de(serie_de("A", SIN_TILDE.get(codigo, nombre), 1)["nombre"]) == codigo
    assert cruzar.departamento_de("Exportaciones por grupo de productos sin ubigeo (Valores FOB)") is None


def test_leer_bcrp_suma_por_departamento_y_aparta_lo_que_no_es_de_uno():
    valor, fuera = cruzar.leer_bcrp(panel(), 2022)
    assert len(valor) == 25 and valor["13"] == 18 and valor["06"] == 6
    assert fuera == 7


def test_leer_bcrp_rechaza_un_departamento_faltante_y_un_anio_incompleto():
    with pytest.raises(SystemExit, match="Callao"):
        cruzar.leer_bcrp(panel(omitir=("07",)), 2022)
    with pytest.raises(SystemExit, match="no tiene datos de 2024"):
        cruzar.leer_bcrp(panel(), 2024)
    meses = pd.DataFrame([serie_de("M", "Ica", 1.0, frecuencia="Mensual")] * 11)
    with pytest.raises(SystemExit, match="incompleto"):
        cruzar.leer_bcrp(meses, 2022)


def test_la_sensibilidad_separa_cada_grupo_de_productos():
    h = pd.DataFrame({"departamento": list(DEPARTAMENTOS), "nombre_departamento": list(DEPARTAMENTOS.values()),
                      "peso": 10.0, "pobre": [i % 2 for i in range(25)], "conglome": [f"{i:06d}" for i in range(25)],
                      "estrato_diseno": ["A"] * 25})
    filas = []
    for c, n in DEPARTAMENTOS.items():
        for producto, valor in (("Tradicionales", float(c)), ("No tradicionales", 100 - float(c))):
            nombre = f"Exportaciones de {SIN_TILDE.get(c, n)} (Valores FOB) - Productos {producto}"
            filas.append({"codigo": f"{producto[:2]}{c}", "nombre": nombre, "frecuencia": "Anual", "periodo": "2022", "valor": valor})
    r = cruzar.sensibilidad(pd.DataFrame(filas), 2022, h, 1e6, 5)
    assert set(r) == {"Productos Tradicionales", "Productos No tradicionales"}
    assert r["Productos Tradicionales"]["primeros"][0] == "Ucayali"
    assert r["Productos No tradicionales"]["primeros"][0] == "Amazonas"
    assert cruzar.sensibilidad(pd.DataFrame(filas[::2]), 2022, h, 1e6, 5) == {}


def test_spearman_da_los_extremos_y_es_reproducible():
    x = list(range(25))
    assert cruzar.spearman(x, x, n=500)["rho"] == pytest.approx(1)
    assert cruzar.spearman(x, x[::-1], n=500)["rho"] == pytest.approx(-1)
    assert cruzar.spearman(x, x, n=500)["p_valor"] < 0.01
    y = [(7 * i) % 25 for i in x]
    assert cruzar.spearman(x, y, n=500) == cruzar.spearman(x, y, n=500)


def test_el_contraste_detecta_que_los_departamentos_no_suman_el_total(tmp_path):
    nacional = tmp_path / "total.csv"
    pd.DataFrame({"anio": [2022], "total": [100.0]}).to_csv(nacional, index=False)
    assert cruzar.contrastar(pd.Series([60.0, 40.0]), nacional, 2022)["coincide"]
    assert not cruzar.contrastar(pd.Series([60.0, 30.0]), nacional, 2022)["coincide"]


def meses(codigo, anio, n, valor=1.0):
    return [{"codigo": codigo, "frecuencia": "Mensual", "periodo": f"{anio}-{m:02d}", "valor": valor} for m in range(1, n + 1)]


def test_el_grafico_del_bcrp_suma_anos_completos_y_rechaza_los_incompletos():
    d = pd.DataFrame(meses("A", 2023, 12) + meses("A", 2024, 12, 2.0))
    t = graficar_bcrp.anual(d, 2023, 2024)
    assert t.loc[2023, "A"] == 12 and t.loc[2024, "A"] == 24
    with pytest.raises(SystemExit, match="incompletos"):
        graficar_bcrp.anual(pd.DataFrame(meses("A", 2023, 12) + meses("A", 2024, 8)), 2023, 2024)
    with pytest.raises(SystemExit, match="incompletos"):
        graficar_bcrp.anual(pd.DataFrame(meses("A", 2022, 12) + meses("A", 2024, 12)), 2022, 2024)


@pytest.mark.skipif(not (estimar.SALIDAS / "hogares_2024.parquet").exists(), reason="falta la base procesada")
def test_el_cruce_une_por_codigo_y_compara_con_el_diseno_de_la_muestra():
    h = estimar.cargar("hogares")
    valor = pd.Series({c: float(int(c)) for c in DEPARTAMENTOS})
    t, r = cruzar.cruzar(valor, h, 1e6, 5)
    assert len(t) == 25 and t.iloc[0]["departamento"] == "25" and r["primeros"][0] == "Ucayali"
    assert t["participacion_pct"].sum() == pytest.approx(100)
    ica = t[t["departamento"] == "11"].iloc[0]
    assert ica["pobreza_pct"] == pytest.approx(6.01, abs=0.01)
    c = r["comparacion_primeros"]
    assert c["diferencia"]["dif"] == pytest.approx(c["grupo"]["pct"] - c["resto"]["pct"])
    assert "Lima" not in r["primeros_sin_lima_callao"] and "Callao" not in r["primeros_sin_lima_callao"]
