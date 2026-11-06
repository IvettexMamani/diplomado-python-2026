"""Demostración de la integración: Claude Code responde un pedido solo con las herramientas del modo elegido.

    uv run mcp/demo_claude.py                                  # la pregunta de abajo, con Sonnet
    uv run mcp/demo_claude.py "otra pregunta" --modelo haiku --nombre otra_demo
    uv run mcp/demo_claude.py "/mcp__bcrp__informe inflación 2025-01" --nombre demo_prompt_informe   # el prompt MCP
    uv run mcp/demo_claude.py "Lee el recurso bcrp://serie/PN01273PM ..." --modo recursos --nombre demo_recurso
    uv run mcp/demo_claude.py "Haz un mapa de la pobreza..." --modo skills --carpeta skills --nombre demo_mapa

En Git Bash, antepongan MSYS_NO_PATHCONV=1 al comando de un pedido que empiece con /: si no, Git Bash convierte
/mcp__bcrp__informe en una ruta de Windows y Claude nunca lo recibe.

Modos:
- mcp: sin terminal ni archivos (--tools ""), con solo el servidor bcrp de .mcp.json. Cada cifra sale de una herramienta.
- recursos: sin las herramientas del BCRP; solo puede leer recursos MCP.
- skills: las Skills del proyecto, Read y Bash limitado a `uv run`. El MCP queda fuera.
- completo: el MCP, sus recursos y las Skills a la vez, y Write para escribir el informe. Es el agente de la Parte 3.

Guarda la transcripción completa (stream-json) y un resumen legible con cada llamada, sus argumentos, lo que devolvió y
la respuesta final, en evidencias_ia/<carpeta>/.
"""
import argparse
import json
import re
import subprocess
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).parent.parent
EVIDENCIAS = RAIZ / "evidencias_ia"
RECURSOS = "ListMcpResourcesTool,ReadMcpResourceTool"
SKILLS = "Skill,Read,Bash(uv run *)"
MODOS = {"mcp": ["--tools", "", "--allowedTools", "mcp__bcrp"],
         "recursos": ["--tools", RECURSOS, "--allowedTools", RECURSOS],
         "skills": ["--tools", "Skill,Read,Bash", "--allowedTools", SKILLS],
         "completo": ["--tools", f"Skill,Read,Write,Bash,{RECURSOS}", "--allowedTools", f"mcp__bcrp,Write,{RECURSOS},{SKILLS}"]}
PREGUNTA = ("¿Cómo evolucionó la inflación interanual de Lima Metropolitana entre diciembre de 2024 y el último dato "
            "disponible? Dame el valor inicial y el final, el cambio en puntos porcentuales y el máximo del periodo, y "
            "dime si en ese periodo se movió junto con el tipo de cambio interbancario venta. Para cada cifra indica "
            "el código de la serie, el periodo y la fuente.")


def correr(pregunta, modelo, modo="mcp"):
    cmd = ["claude", "-p", pregunta, "--model", modelo, "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--strict-mcp-config", "--mcp-config", ".mcp.json", *MODOS[modo]]
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
    llamadas = [c for e in eventos if e.get("type") == "assistant" for c in e.get("message", {}).get("content", [])
                if c.get("type") == "tool_use"]
    skills = [c["input"].get("skill", "") for c in llamadas if c["name"] == "Skill"]
    if pregunta.startswith("/") and not pregunta.startswith("/mcp__"):  # /nombre carga la skill sin llamar a la herramienta
        skills.insert(0, f"{pregunta.split()[0][1:]} (invocada con /)")
    scripts = [a or b for c in llamadas if c["name"] == "Bash"  # solo lo que se ejecutó, no lo que se leyó con head o cat
               for a, b in re.findall(r'uv run\s+(?:"[^"]*?([\w-]+\.py)"|\S*?([\w-]+\.py))', c["input"].get("command", ""))]
    usadas =", ".join(f"{nombre} ×{n}" for nombre, n in Counter(c["name"] for c in llamadas).items())
    lineas = [
        "# Demostración en Claude Code", "",
        f"- **Fecha:** {datetime.now():%Y-%m-%d %H:%M}",
        f"- **Modelo:** {init.get('model', modelo)}",
        f"- **Servidores MCP:** {servidores}",
        f"- **Herramientas que ve el modelo:** {', '.join(init.get('tools', []))} (solo puede usar las de --allowedTools)",
        f"- **Comando:** `{comando}`",
        f"- **Skills activadas, en orden:** {' → '.join(skills) or 'ninguna'}",
        f"- **Scripts ejecutados, en orden:** {' → '.join(scripts) or 'ninguno'}",
        f"- **Herramientas usadas:** {usadas or 'ninguna'}",
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
    p.add_argument("--modo", default="mcp", choices=list(MODOS))
    p.add_argument("--carpeta", default="mcp", help="subcarpeta de evidencias_ia/")
    a = p.parse_args()
    cmd, eventos, segundos = correr(a.pregunta, a.modelo, a.modo)
    salida = EVIDENCIAS / a.carpeta
    salida.mkdir(parents=True, exist_ok=True)
    (salida / f"{a.nombre}.jsonl").write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in eventos),
                                             encoding="utf-8")
    (salida / f"{a.nombre}.md").write_text(legible(a.pregunta, a.modelo, cmd, eventos, segundos), encoding="utf-8")
    print(f"Listo en {segundos} s: {salida / a.nombre}.md")
