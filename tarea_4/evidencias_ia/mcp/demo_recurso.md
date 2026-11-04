# Demostración: Claude Code con el MCP del BCRP

- **Fecha:** 2026-11-04 08:25
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas que ve el modelo:** ListMcpResourcesTool, ReadMcpResourceTool, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie (solo puede usar las de --allowedTools)
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --mcp-config .mcp.json --tools ListMcpResourcesTool,ReadMcpResourceTool --allowedTools ListMcpResourcesTool,ReadMcpResourceTool`
- **Turnos:** 2 · **segundos:** 26.8 · **costo:** US$ 0.008

## Pregunta

> Lee el recurso bcrp://serie/PN01273PM del servidor MCP bcrp y, solo con lo que dice esa ficha, responde: ¿qué área del BCRP publica la serie, en qué grupo de publicación, cuál es su fuente original, desde cuándo hay datos y cómo se cita?

## Llamadas a herramientas

### 1. `ReadMcpResourceTool`

```json
{
 "server": "bcrp",
 "uri": "bcrp://serie/PN01273PM"
}
```

<details><summary>Resultado</summary>

```json
{"contents":[{"uri":"bcrp://serie/PN01273PM","mimeType":"application/json","text":"{\"codigo\": \"PN01273PM\", \"nombre\": \"\\u00cdndice de precios Lima Metropolitana (var% 12 meses) - IPC\", \"categoria\": \"Inflaci\\u00f3n\", \"grupo_de_serie\": \"\\u00cdndice de precios Lima Metropolitana (var% 12 meses)\", \"nombre_de_serie\": \"IPC\", \"descripcion\": null, \"metodologia\": null, \"frecuencia\": \"Mensual\", \"datos_desde\": \"Ene-1950\", \"actualizada\": \"2026-10-08\", \"fuente_original\": \"INEI\", \"grupo_de_publicacion\": \"\\u00cdndice de precios al consumidor y tipo de cambio real\", \"area_que_publica\": \"Departamento de Estad\\u00edsticas de Precios\", \"tabla_web\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01273PM/html\", \"api\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/{desde}/{hasta}\", \"como_citar\": \"Banco Central de Reserva del Per\\u00fa, serie PN01273PM \\u00ab\\u00cdndice de precios Lima Metropolitana (var% 12 meses) - IPC\\u00bb (fuente original: INEI). https://estadisticas.bcrp.gob.pe\"}"}]}
```

</details>

## Respuesta final

Según la ficha de la serie **PN01273PM** («Índice de precios Lima Metropolitana (var% 12 meses) - IPC»):

- **Área que la publica:** Departamento de Estadísticas de Precios.
- **Grupo de publicación:** Índice de precios al consumidor y tipo de cambio real.
- **Fuente original:** INEI.
- **Datos desde:** enero de 1950. La serie es mensual y se actualizó el 2026-10-08.
- **Cómo se cita:** Banco Central de Reserva del Perú, serie PN01273PM «Índice de precios Lima Metropolitana (var% 12 meses) - IPC» (fuente original: INEI). https://estadisticas.bcrp.gob.pe

La ficha no trae descripción ni metodología (ambos campos están en `null`).
