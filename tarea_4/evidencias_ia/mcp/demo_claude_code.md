# Demostración: Claude Code con el MCP del BCRP

- **Fecha:** 2026-11-04 08:21
- **Modelo:** claude-sonnet-5-5
- **Servidores MCP:** bcrp (connected)
- **Herramientas disponibles:** mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie
- **Comando:** `claude -p «pregunta» --model sonnet --output-format stream-json --verbose --no-session-persistence --tools "" --strict-mcp-config --mcp-config .mcp.json --allowedTools mcp__bcrp`
- **Turnos:** 5 · **segundos:** 29.4 · **costo:** US$ 0.0320752

## Pregunta

> ¿Cómo evolucionó la inflación interanual de Lima Metropolitana entre diciembre de 2024 y el último dato disponible? Dame el valor inicial y el final, el cambio en puntos porcentuales y el máximo del periodo, y dime si en ese periodo se movió junto con el tipo de cambio interbancario venta. Para cada cifra indica el código de la serie, el periodo y la fuente.

## Llamadas a herramientas

### 1. `mcp__bcrp__buscar_series`

```json
{
 "texto": "ipc lima metropolitana 12 meses",
 "frecuencia": "Mensual"
}
```

<details><summary>Resultado</summary>

```json
{"result":[{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1950","actualizada":"2026-10-08","fuente_original":"INEI"},{"codigo":"PN09821PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Importado","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08","fuente_original":"INEI"},{"codigo":"PN01279PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Subyacente","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08","fuente_original":"INEI"},{"codigo":"PN01281PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Transables","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08","fuente_original":"INEI"},{"codigo":"PN01283PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC No Transables","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08","fuente_original":"INEI"},{"codigo":"PN09820PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC No Subyacente","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08","fuente_original":"INEI"},{"codigo":"PN09819PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual
... (2280 caracteres en total)
```

</details>

### 2. `mcp__bcrp__buscar_series`

```json
{
 "texto": "tipo de cambio interbancario venta"
}
```

<details><summary>Resultado</summary>

```json
{"result":[{"codigo":"PD04638PD","nombre":"Tipo de cambio - TC Interbancario (S/ por US$) - Venta","categoria":"Tipo de cambio nominal","frecuencia":"Diaria","inicio":"1997-01-02","actualizada":"2026-10-23","fuente_original":"SBS, Reuters, Datatec, BCRP"},{"codigo":"PN01215PM","nombre":"Tipo de cambio - fin de periodo (S/ por US$) - Interbancario - Venta","categoria":"Tipo de cambio nominal","frecuencia":"Mensual","inicio":"Ene-1995","actualizada":"2026-10-08","fuente_original":"BCRP, SBS, Reuters, Datatec"},{"codigo":"PN01206PM","nombre":"Tipo de cambio - promedio del periodo (S/ por US$) - Interbancario - Venta","categoria":"Tipo de cambio nominal","frecuencia":"Mensual","inicio":"Ene-1995","actualizada":"2026-10-08","fuente_original":"BCRP, SBS, Reuters, Datatec"}]}
```

</details>

### 3. `mcp__bcrp__resumen`

```json
{
 "codigo": "PN01273PM",
 "desde": "2024-12"
}
```

<details><summary>Resultado</summary>

```json
{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","frecuencia":"Mensual","periodo":{"desde":"2024-12","hasta":"2026-09"},"n":22,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2024-12/2026-9","fuente_web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01273PM/html/2024-12/2026-9/","fuente_original":"INEI","primero":{"periodo":"2024-12","valor":1.966303},"ultimo":{"periodo":"2026-09","valor":4.548655},"cambio":2.5824,"variacion_pct":131.3303,"promedio":2.3948,"desviacion_estandar":1.2322,"maximo":{"periodo":"2026-09","valor":4.548655},"minimo":{"periodo":"2025-08","valor":1.106331},"nota":"La serie ya es una tasa o variación en %: «cambio» está en puntos porcentuales y «variacion_pct» es el cambio relativo de esa tasa, que casi nunca es lo que se quiere reportar."}
```

</details>

### 4. `mcp__bcrp__correlacion`

```json
{
 "codigo_a": "PN01273PM",
 "codigo_b": "PD04638PD",
 "desde": "2024-12"
}
```

<details><summary>Resultado</summary>

```json
{"serie_a":{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","frecuencia":"Mensual","observaciones":22,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2024-12/2026-9","fuente_web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01273PM/html/2024-12/2026-9/","fuente_original":"INEI"},"serie_b":{"codigo":"PD04638PD","nombre":"Tipo de cambio - TC Interbancario (S/ por US$) - Venta","frecuencia":"Diaria","observaciones":473,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04638PD/json/2024-12-02/2026-11-02","fuente_web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/diarias/resultados/PD04638PD/html/2024-12-02/2026-11-02/","fuente_original":"SBS, Reuters, Datatec, BCRP","rezago":0},"frecuencia_comun":"Mensual","periodo":{"desde":"2024-12","hasta":"2026-09"},"n":22,"descartados":{"sin_dato_en_a":2,"sin_dato_en_b":0},"pearson":-0.4671,"intervalo_95":[-0.7425,-0.0567],"p_valor_aprox":0.027293,"spearman":-0.3337,"fuerza":"moderada negativa","pearson_variaciones":0.65,"n_variaciones":21,"advertencias":["La serie PD04638PD es diaria: se usó el promedio de cada periodo mensual (473 datos en 24 periodos).","Se descartaron 2 periodos sin dato en una de las series.","Correlación no implica causalidad; el p-valor supone datos independientes y en series de tiempo suele ser optimista."],"datos":[{"periodo":"2024-12","a":1.966303,"b":3.736079},{"periodo":"2025-01"
... (2482 caracteres en total)
```

</details>

## Respuesta final

**Resumen:** la inflación interanual de Lima Metropolitana pasó de 1,97 % en diciembre de 2024 a 4,55 % en septiembre de 2026. En ese periodo no se movió junto con el tipo de cambio.

**Inflación interanual de Lima Metropolitana** (serie `PN01273PM`, IPC var. % 12 meses, mensual, fuente original INEI, vía BCRP)
- **Valor inicial (dic 2024):** 1,97 %.
- **Valor final (sep 2026, último dato disponible):** 4,55 %.
- **Cambio:** +2,58 puntos porcentuales.
- **Máximo del periodo:** 4,55 % en sep 2026, es decir, el último dato.
- **Mínimo, como referencia:** 1,11 % en ago 2025.
- **Fuente:** https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01273PM/html/2024-12/2026-9/

**Trayectoria:** la inflación bajó hasta 1,11 % en agosto de 2025 y se mantuvo en 1,3–1,7 % hasta enero de 2026. Desde febrero de 2026 subió con fuerza: 2,21 % en febrero y 3,80 % en marzo. Desde entonces siguió subiendo hasta 4,55 % en septiembre.

**Relación con el tipo de cambio** (serie `PD04638PD`, TC interbancario venta, S/ por US$, diaria, fuente original SBS, Reuters, Datatec y BCRP)
- La serie diaria se promedió por mes para compararla con la inflación. El periodo común es dic 2024–sep 2026, con 22 meses.
- **Niveles:** la correlación de Pearson es −0,47, con intervalo de confianza al 95 % de −0,74 a −0,06. La de Spearman es −0,33. Es una asociación moderada y negativa.
- **Variaciones mensuales:** la correlación es +0,65 con 21 observaciones.
- El tipo de cambio cayó de unos 3,74 a unos 3,38 soles por dólar, mientras la inflación subía de 1,97 % a 4,55 %. Esto explica el signo negativo en niveles.
- **Fuente:** https://estadisticas.bcrp.gob.pe/estadisticas/series/diarias/resultados/PD04638PD/html/2024-12-02/2026-11-02/

**Cautelas**
- **Señales contradictorias:** las dos correlaciones tienen signos opuestos, así que no se puede decir que ambas variables se hayan movido juntas de forma clara.
- **Sin causalidad:** una correlación no prueba que una variable cause la otra.
- **Pocos datos:** con 22 meses y series con tendencia, el p-valor (0,027) probablemente es optimista.
- **Meses sin dato:** el tipo de cambio llega hasta el 2 de noviembre de 2026, pero la inflación solo hasta septiembre. Octubre y noviembre quedaron fuera del cálculo.
