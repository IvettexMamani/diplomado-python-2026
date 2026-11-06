"""Pruebas de las Skills de la ENAHO. Van aparte de las 10 del MCP, que `uv run pytest` sigue corriendo solas:

    uv run pytest pruebas

Las que usan microdatos se saltan si no están los zip en datos/enaho/.
"""
import io
import subprocess
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point

RAIZ = Path(__file__).parent.parent
SKILLS = RAIZ / ".claude" / "skills"
sys.path[:0] = [str(SKILLS / "limpiando-enaho" / "scripts"), str(SKILLS / "mapeando-enaho" / "scripts")]

import estimar  # noqa: E402
import limpiar  # noqa: E402
import mapear  # noqa: E402

Z34, Z02 = limpiar.DATOS / "966-Modulo34.zip", limpiar.DATOS / "966-Modulo02.zip"
hay_microdatos = pytest.mark.skipif(not (Z34.exists() and Z02.exists()), reason="faltan los zip de la ENAHO")


# Muestra de juguete para calcular a mano: 2 estratos, 2 UPM en cada uno, 2 hogares por UPM y peso 1.
# La razón es 4/8 = 0.5. Variable linealizada: (y - 0.5) / 8. Totales por UPM: 0.125, -0.125, 0 y 0.
# Estrato A: 2/(2-1) × (0.125² + 0.125²) = 0.0625. Estrato B: 0. Error estándar: √0.0625 = 0.25.
JUGUETE = pd.DataFrame({"estrato_diseno": ["A"] * 4 + ["B"] * 4, "conglome": list("11223344"),
                        "pobre": [1, 1, 0, 0, 1, 0, 1, 0], "peso": 1.0})


def test_el_estimador_coincide_con_el_calculo_a_mano():
    f = estimar.fila(JUGUETE, "pobre", pd.Series(True, index=JUGUETE.index))
    assert f["pct"] == pytest.approx(50)
    assert f["ee"] == pytest.approx(25)
    assert (f["ic95_inf"], f["ic95_sup"]) == (pytest.approx(1), pytest.approx(99))
    assert f["n_muestra"] == 8 and f["upm"] == 4 and f["poblacion"] == 8


def test_el_peso_cambia_la_estimacion():
    d = JUGUETE.assign(peso=[3.0, 3.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    assert estimar.fila(d, "pobre", pd.Series(True, index=d.index))["pct"] == pytest.approx(8 / 12 * 100)


def test_un_dominio_conserva_las_upm_de_fuera_para_el_error():
    """Calcular sobre el estrato A filtrado daría 0.5 con otro error: la fila se marca, no se borra."""
    dentro = JUGUETE["conglome"].isin(["1", "3"])
    f = estimar.fila(JUGUETE, "pobre", dentro)
    assert f["pct"] == pytest.approx(75)
    assert f["ee"] > 0 and f["upm"] == 2


def test_la_diferencia_de_un_grupo_consigo_mismo_es_cero():
    todos = pd.Series(True, index=JUGUETE.index)
    d = estimar.diferencia(JUGUETE, "pobre", todos, todos)
    assert d["dif"] == 0 and d["ee"] == 0 and d["distinguible"] is False


def test_sin_base_procesada_se_pide_limpiar_primero(tmp_path):
    with pytest.raises(SystemExit, match="limpiando-enaho"):
        estimar.cargar("hogares", tmp_path)


def test_otro_anio_se_rechaza_con_un_mensaje_claro():
    r = subprocess.run([sys.executable, str(SKILLS / "limpiando-enaho" / "scripts" / "limpiar.py"), "--anio", "2023"],
                       capture_output=True, text=True, encoding="utf-8", env={"PYTHONUTF8": "1", "SYSTEMROOT": "C:\\Windows"})
    assert r.returncode != 0 and "2023" in r.stderr


@pytest.fixture(scope="module")
def modulos():
    return limpiar.leer(Z34, limpiar.SUMARIA), limpiar.leer(Z02, limpiar.MIEMBROS)


def validar(sumaria, miembros):
    h, p = limpiar.construir(sumaria, miembros)
    return limpiar.validar(sumaria, miembros, h, p), h, p


def fallas(v):
    return [x for x in v.lineas if x.startswith("[FALLA]")]


@hay_microdatos
def test_los_datos_reales_aprueban_y_reproducen_las_cifras(modulos):
    v, h, p = validar(*modulos)
    assert v.fallas == 0 and v.avisos == 0
    assert len(p) == 108_664 and h["departamento"].nunique() == 25
    assert estimar.fila(h, "pobre", pd.Series(True, index=h.index))["pct"] == pytest.approx(27.579, abs=0.001)
    assert estimar.fila(p, "pobre", pd.Series(True, index=p.index))["pct"] == pytest.approx(27.529, abs=0.001)


def _sin_ceros(s, m):
    s = s.assign(conglome=pd.to_numeric(s["conglome"]))
    return s, m.assign(conglome=pd.to_numeric(m["conglome"]))


def _factor_a_la_mitad(s, m):
    return s.assign(factor07=s["factor07"] / 2), m


def _sin_factor(s, m):
    return s, m.assign(facpob07=1.0)


def _pobreza_alterada(s, m):
    return s.assign(pobreza=s["pobreza"].where(s.index > 2000, 3)), m


def _persona_repetida(s, m):
    return s, pd.concat([m, m.iloc[[0]]], ignore_index=True)


def _sin_callao(s, m):
    return s[s["ubigeo"].str[:2] != "07"], m[m["ubigeo"].str[:2] != "07"]


def _filtro_equivocado(s, m):
    return s, m.assign(p205=m["p205"].where(m["p205"] != 1, 2))


@hay_microdatos
@pytest.mark.parametrize("dano, esperado", [
    (_sin_ceros, "ancho fijo"), (_factor_a_la_mitad, "Población expandida"), (_sin_factor, "facpob07"),
    (_pobreza_alterada, "gasto mensual"), (_persona_repetida, "personas repetidas"), (_sin_callao, "Códigos territoriales"),
    (_filtro_equivocado, "Residentes habituales"),
])
def test_cada_dano_hace_fallar_su_validacion(modulos, dano, esperado):
    v, _, _ = validar(*dano(*modulos))
    assert any(esperado in x for x in fallas(v)), fallas(v)


@hay_microdatos
def test_un_hogar_repetido_rompe_la_union(modulos):
    s, m = modulos
    with pytest.raises(pd.errors.MergeError):
        limpiar.construir(pd.concat([s, s.iloc[[0]]], ignore_index=True), m)


@hay_microdatos
def test_una_validacion_fallida_detiene_el_proceso_y_no_deja_bases(modulos, tmp_path):
    """De punta a punta: con un módulo dañado, el script termina con error y salidas/ no conserva parquet."""
    s, _ = modulos
    datos, salidas = tmp_path / "datos", tmp_path / "salidas"
    datos.mkdir()
    salidas.mkdir()
    (salidas / "personas_2024.parquet").write_text("una base anterior")
    (datos / Z02.name).write_bytes(Z02.read_bytes())
    buffer = io.BytesIO()
    s[limpiar.COLUMNAS_HOGAR].iloc[:-500].to_stata(buffer, write_index=False, version=118)
    with zipfile.ZipFile(datos / Z34.name, "w") as z:
        z.writestr("966-Modulo34/sumaria-2024.dta", buffer.getvalue())
    r = subprocess.run(["uv", "run", "--quiet", str(SKILLS / "limpiando-enaho" / "scripts" / "limpiar.py"),
                        "--datos", str(datos), "--salidas", str(salidas)], cwd=RAIZ, capture_output=True, text=True,
                       encoding="utf-8")
    assert r.returncode != 0 and "No se guardó ninguna base" in r.stderr
    assert "RESULTADO: RECHAZADA" in (salidas / "validacion.txt").read_text(encoding="utf-8")
    assert not list(salidas.glob("*.parquet"))


def cifras(codigos):
    return pd.DataFrame({"codigo": codigos, "categoria": codigos, "pct": 10.0, "cv_pct": 5.0})


def geo(codigos):
    return gpd.GeoDataFrame({mapear.LLAVE: codigos}, geometry=[Point(i, 0).buffer(0.4) for i, _ in enumerate(codigos)],
                            crs="EPSG:4326")


CODIGOS = [f"{i:02d}" for i in range(1, 26)]


def test_el_mapa_une_las_25_unidades_por_codigo():
    u, problemas = mapear.unir(geo(CODIGOS), cifras(CODIGOS))
    assert not problemas and len(u) == 25 and u["pct"].notna().all()


def test_el_mapa_rechaza_una_llave_sin_el_cero_inicial():
    sin_cero = [c.lstrip("0") for c in CODIGOS]
    _, problemas = mapear.unir(geo(sin_cero), cifras(CODIGOS))
    assert any("dos dígitos" in x for x in problemas) and any("Unión incompleta" in x for x in problemas)


def test_el_mapa_rechaza_que_falte_callao():
    sin_callao = [c for c in CODIGOS if c != "07"]
    _, problemas = mapear.unir(geo(sin_callao), cifras(CODIGOS))
    assert any("se esperan 25" in x for x in problemas) and any("Lima (15) y Callao (07)" in x for x in problemas)


@hay_microdatos
def test_el_mapa_coincide_con_la_referencia_de_la_sesion_16(modulos):
    _, h, _ = validar(*modulos)
    u, problemas = mapear.unir(mapear.geometrias(), estimar.tabla(h, "departamento"))
    c = mapear.comparar(u)
    assert not problemas and len(c) == 25
    assert c["diferencia"].abs().max() <= mapear.TOLERANCIA
