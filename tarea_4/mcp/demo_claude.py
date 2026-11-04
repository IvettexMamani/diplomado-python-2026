"""Demostración de la integración: Claude Code responde una pregunta con el MCP del BCRP como única herramienta.

    uv run mcp/demo_claude.py                                  # la pregunta de abajo, con Sonnet
    uv run mcp/demo_claude.py "otra pregunta" --modelo haiku --nombre otra_demo
    uv run mcp/demo_claude.py "/mcp__bcrp__informe inflación 2025-01" --nombre demo_prompt_informe   # el prompt MCP
    uv run mcp/demo_claude.py "Lee el recurso bcrp://serie/PN01273PM ..." --recursos --nombre demo_recurso

En Git Bash, antepongan MSYS_NO_PATHCONV=1 al comando del prompt: si no, Git Bash convierte /mcp__bcrp__informe en
una ruta de Windows y Claude nunca recibe el prompt. Con --recursos, Claude no tiene las herramientas del BCRP: solo
puede leer recursos MCP (ListMcpResourcesTool y ReadMcpResourceTool).

Corre `claude -p` sin terminal ni archivos (--tools ""), con solo el servidor bcrp de .mcp.json, así que cada cifra
tiene que salir de una herramienta. Guarda la transcripción completa (stream-json) y un resumen legible con cada
llamada, sus argumentos, lo que devolvió y la respuesta final, en evidencias_ia/mcp/.
"""
import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).parent.parent
SALIDA = RAIZ / "evidencias_ia" / "mcp"
PREGUNTA = ("¿Cómo evolucionó la inflación interanual de Lima Metropolitana entre diciembre de 2024 y el último dato "
            "disponible? Dame el valor inicial y el final, el cambio en puntos porcentuales y el máximo del periodo, y "
            "dime si en ese periodo se movió junto con el tipo de cambio interbancario venta. Para cada cifra indica "
            "el código de la serie, el periodo y la fuente.")


def correr(pregunta, modelo, recursos=False):
    herramientas = ["--tools", "ListMcpResourcesTool,ReadMcpResourceTool",
                    "--allowedTools", "ListMcpResourcesTool,ReadMcpResourceTool"] if recursos else                    ["--tools", "", "--allowedTools", "mcp__bcrp"]
    cmd = ["claude", "-p", pregunta, "--model", modelo, "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--strict-mcp-config", "--mcp-config", ".mcp.json", *herramientas]
    t = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=900, cwd=RAIZ)
    eventos = [json.loads(linea) for linea in proc.stdout.splitlines() if linea.strip().startswith("{")]
    if not eventos:
        raise SystemExit(f"claude -p no devolvió eventos:\n{proc.stderr[-2000:]}")
    return cmd, _limpiar(eventos), round(time.time() - t, 1)


def _limpiar(eventos):
    """Quita lo que no hace falta para revisar la demostración y que describe la cuenta o el equipo: rutas de memoria,
    plugins, sockets, límites de uso. Del evento inicial quedan el modelo, la versión, las herramientas y los MCP."""
    conservar = {"type", "subtype", "model", "claude_code_version", "tools", "mcp_servers", "permissionMode"}
    limpios = []
    for e in eventos:
        if e.get("type") == "rate_limit_event":
            continue
        if e.get("type") == "system" and e.get("subtype") == "init":
            e = {k: v for k, v in e.items() if k in conservar}
        limpios.append(e)
    return limpios


def _texto(contenido):
    if isinstance(contenido, str):
        return contenido
    return "\n".join(c.get("text", "") for c in contenido or [] if isinstance(c, dict))


def legible(pregunta, modelo, cmd, eventos, segundos):
    init = next((e for e in eventos if e.get("type") == "system" and e.get("subtype") == "init"), {})
    final = next((e for e in reversed(eventos) if e.get("type") == "result"), {})
    comando = " ".join(f'"{c}"' if (" " in c or not c) else c for c in cmd[:2] + ["«pregunta»"] + cmd[3:])
    servidores = ", ".join(f"{s['name']} ({s['status']})" for s in init.get("mcp_servers", []))
    lineas = [
        "# Demostración: Claude Code con el MCP del BCRP", "",
        f"- **Fecha:** {datetime.now():%Y-%m-%d %H:%M}",
        f"- **Modelo:** {init.get('model', modelo)}",
        f"- **Servidores MCP:** {servidores}",
        f"- **Herramientas que ve el modelo:** {', '.join(init.get('tools', []))} (solo puede usar las de --allowedTools)",
        f"- **Comando:** `{comando}`",
        f"- **Turnos:** {final.get('num_turns')} · **segundos:** {segundos} · **costo:** US$ {round(final.get('total_cost_usd') or 0, 4)}",
        "", "## Pregunta", "", f"> {pregunta}", "", "## Llamadas a herramientas", "",
    ]
    resultados = {}
    for e in eventos:
        if e.get("type") == "user":
            for c in e.get("message", {}).get("content", []):
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    resultados[c["tool_use_id"]] = _texto(c.get("content"))
    n = 0
    for e in eventos:
        if e.get("type") != "assistant":
            continue
        for c in e.get("message", {}).get("content", []):
            if c.get("type") == "tool_use":
                n += 1
                res = resultados.get(c["id"], "")
                res = res if len(res) <= 1500 else res[:1500] + f"\n... ({len(res)} caracteres en total)"
                lineas += [f"### {n}. `{c['name']}`", "", "```json", json.dumps(c["input"], ensure_ascii=False, indent=1),
                           "```", "", "<details><summary>Resultado</summary>", "", "```json", res, "```", "",
                           "</details>", ""]
    lineas += ["## Respuesta final", "", final.get("result", "(sin respuesta)"), ""]
    return "\n".join(lineas)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("pregunta", nargs="?", default=PREGUNTA)
    p.add_argument("--modelo", default="sonnet")
    p.add_argument("--nombre", default="demo_claude_code")
    p.add_argument("--recursos", action="store_true", help="solo puede leer recursos MCP, sin las herramientas")
    a = p.parse_args()
    cmd, eventos, segundos = correr(a.pregunta, a.modelo, a.recursos)
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / f"{a.nombre}.jsonl").write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in eventos),
                                             encoding="utf-8")
    (SALIDA / f"{a.nombre}.md").write_text(legible(a.pregunta, a.modelo, cmd, eventos, segundos), encoding="utf-8")
    print(f"Listo en {segundos} s: {SALIDA / a.nombre}.md")
