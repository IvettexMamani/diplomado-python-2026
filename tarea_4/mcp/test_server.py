"""El contrato del servidor: si estas pruebas pasan, Claude Code y evaluar.py pueden usarlo.

    uv run pytest -q

Llaman al servidor en memoria, igual que lo haría Claude Code, y piden datos reales al BCRP.
"""
import asyncio

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from server import mcp


async def _con_cliente(f):
    async with Client(mcp) as c:
        return await f(c)


def llamar(herramienta, **args):
    return asyncio.run(_con_cliente(lambda c: c.call_tool(herramienta, args))).data


def test_buscar_encuentra_el_ipc():
    r = llamar("buscar_series", texto="ipc 12 meses", limite=5)
    assert "PN01273PM" in [x["codigo"] for x in r]
    assert {"codigo", "nombre", "frecuencia"} <= r[0].keys()


def test_cuatro_herramientas_como_minimo():
    nombres = {t.name for t in asyncio.run(_con_cliente(lambda c: c.list_tools()))}
    assert {"buscar_series", "serie", "resumen"} <= nombres
    assert len(nombres) >= 4, "falta su herramienta propia"


def test_serie_mensual():
    r = llamar("serie", codigo="PN01271PM", desde="2025-01", hasta="2025-12")
    assert len(r["datos"]) == 12
    assert r["datos"][0]["periodo"] == "2025-01"
    assert r["datos"][2]["valor"] == pytest.approx(0.81, abs=0.01)   # IPC de Lima, marzo de 2025
    assert r["fuente"].startswith("https://estadisticas.bcrp.gob.pe")


def test_serie_diaria():
    r = llamar("serie", codigo="PD04638PD", desde="2026-10-01", hasta="2026-10-15")
    assert r["datos"][0]["periodo"] == "2026-10-01"
    assert r["datos"][-1] == {"periodo": "2026-10-15", "valor": pytest.approx(3.428, abs=0.001)}


def test_resumen_sin_cuentas_a_mano():
    r = llamar("resumen", codigo="PN01273PM", desde="2025-12", hasta="2026-09")
    assert r["primero"]["valor"] == pytest.approx(1.51, abs=0.01)
    assert r["ultimo"]["valor"] == pytest.approx(4.55, abs=0.01)
    assert r["maximo"]["periodo"] == "2026-09"
    assert {"cambio", "variacion_pct", "promedio", "minimo"} <= r.keys()


def test_codigo_inexistente_da_un_error_claro():
    with pytest.raises(ToolError, match="XX999"):
        llamar("serie", codigo="XX999", desde="2025-01", hasta="2025-02")


def test_un_recurso():
    async def contar(c):
        return len(await c.list_resources()) + len(await c.list_resource_templates())
    assert asyncio.run(_con_cliente(contar)) >= 1


def test_un_prompt():
    assert len(asyncio.run(_con_cliente(lambda c: c.list_prompts()))) >= 1


# ---------------------------------------------------------------------------------------------------------------
# Pruebas propias (Tarea 4): la herramienta correlacion. Las 8 de arriba son las originales de la Sesión 04, sin
# cambios. Estas calculan la verdad por su cuenta, con statistics de la biblioteca estándar sobre los datos que
# devuelve serie, para no repetir el código de pandas del servidor.
from statistics import correlation, fmean


def test_correlacion_alinea_frecuencias_y_coincide_con_un_calculo_independiente():
    # Inflación a 12 meses (mensual) contra tipo de cambio interbancario venta (diario), 2024-2025
    r = llamar("correlacion", codigo_a="PN01273PM", codigo_b="PD04638PD", desde="2024-01", hasta="2025-12")
    assert r["frecuencia_comun"] == "Mensual"
    assert r["n"] == 24 and r["periodo"] == {"desde": "2024-01", "hasta": "2025-12"}
    assert r["serie_a"]["fuente"].startswith("https://estadisticas.bcrp.gob.pe")
    assert r["serie_b"]["fuente"].startswith("https://estadisticas.bcrp.gob.pe")

    # El mismo cálculo a mano: promedio de los días de cada mes y Pearson de la biblioteca estándar
    ipc = {d["periodo"]: d["valor"] for d in llamar("serie", codigo="PN01273PM", desde="2024-01", hasta="2025-12")["datos"]}
    dias = llamar("serie", codigo="PD04638PD", desde="2024-01-01", hasta="2025-12-31")["datos"]
    tc = {mes: fmean(d["valor"] for d in dias if d["periodo"].startswith(mes)) for mes in ipc}
    assert r["datos"][0] == {"periodo": "2024-01", "a": pytest.approx(ipc["2024-01"]), "b": pytest.approx(tc["2024-01"])}
    assert r["pearson"] == pytest.approx(correlation(list(ipc.values()), [tc[m] for m in ipc]), abs=1e-4)

    # Es simétrica y el intervalo de confianza contiene a la estimación
    r2 = llamar("correlacion", codigo_a="PD04638PD", codigo_b="PN01273PM", desde="2024-01", hasta="2025-12")
    assert r2["pearson"] == pytest.approx(r["pearson"])
    assert r["intervalo_95"][0] <= r["pearson"] <= r["intervalo_95"][1]


def test_correlacion_trata_faltantes_y_rezago():
    # El tipo de cambio diario empieza el 2 de enero de 1997: los 6 meses de 1996 no tienen par y se descartan
    r = llamar("correlacion", codigo_a="PN01273PM", codigo_b="PD04638PD", desde="1996-07", hasta="1997-12")
    assert r["n"] == 12 and r["periodo"]["desde"] == "1997-01"
    assert r["descartados"] == {"sin_dato_en_a": 0, "sin_dato_en_b": 6}

    # rezago=1 sobre la misma serie es la autocorrelación de orden 1: compara cada mes con el anterior,
    # y baja diciembre de 2024 para que enero de 2025 también tenga par
    r = llamar("correlacion", codigo_a="PN01271PM", codigo_b="PN01271PM", desde="2025-01", hasta="2025-12", rezago=1)
    x = [d["valor"] for d in llamar("serie", codigo="PN01271PM", desde="2024-12", hasta="2025-12")["datos"]]
    assert r["n"] == 12
    assert r["datos"][0] == {"periodo": "2025-01", "a": pytest.approx(x[1]), "b": pytest.approx(x[0])}
    assert r["pearson"] == pytest.approx(correlation(x[1:], x[:-1]), abs=1e-4)

    # Con menos de 4 pares no inventa un número: da un error que explica qué falta
    with pytest.raises(ToolError, match="al menos 4"):
        llamar("correlacion", codigo_a="PN01273PM", codigo_b="PM04923AA", desde="2024", hasta="2025")
