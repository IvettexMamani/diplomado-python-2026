---
name: limpiando-enaho
description: Limpia y une los módulos 34 (sumaria) y 02 (miembros) de la ENAHO 2024 del INEI, valida la pobreza monetaria contra las cifras oficiales y da cifras ponderadas de pobreza por departamento, área urbana o rural, región, sexo o edad. Úsala cuando pidan limpiar, preparar, unir o validar la ENAHO, o cuando pregunten cuánta pobreza hubo en 2024 en el Perú, en un departamento o en un grupo de personas.
argument-hint: "[2024]"
allowed-tools: Bash(uv run *), PowerShell(uv run *), Read
---

# Limpiar la ENAHO 2024 y responder cifras de pobreza

## 1. Tener la base procesada

Si faltan `salidas/personas_2024.parquet`, `salidas/hogares_2024.parquet` o `salidas/validacion.txt`, o si piden limpiar
de nuevo, corre exactamente:

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/limpiar.py"
```

El script descarga los zip del INEI a `datos/enaho/` si faltan. Si la descarga falla, pide a la persona que los baje
desde el navegador con los enlaces que imprime; no busques otra fuente.

## 2. Revisar la validación

Lee `salidas/validacion.txt`.

- `RESULTADO: APROBADA`: sigue.
- `RESULTADO: RECHAZADA` o error del script: detente y di qué comprobación falló. No hay base procesada y no debes
  calcular nada por otro camino. Nunca ajustes datos, filtros o factores para acercarte a una cifra de referencia.

## 3. Responder la cifra

Toda cifra sale de un script, nunca de un cálculo propio ni de memoria.

- Cortes habituales: busca en `salidas/indicadores.csv`. Filtra por `indicador`, `grupo` y `base`.
- Cualquier otro corte: usa `estimar.py`, que pondera y calcula el intervalo de confianza.

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/estimar.py" --por departamento
uv run "${CLAUDE_SKILL_DIR}/scripts/estimar.py" --por sexo --solo departamento=Puno
uv run "${CLAUDE_SKILL_DIR}/scripts/estimar.py" --por area --indicador pobre_extremo
uv run "${CLAUDE_SKILL_DIR}/scripts/estimar.py" --solo departamento=Cusco
```

`--por` acepta `area`, `dominio`, `departamento`, `sexo` y `grupo_edad`. `--solo` se puede repetir.

## 4. Presentar el resultado

- Indica la cifra con un decimal, su intervalo de confianza de 95 % y la fuente: «INEI, ENAHO 2024».
- Para Perú, área, dominio y departamento usa la base `hogares` (`factor07 × mieperho`): es el método del INEI y da las
  cifras publicadas. Para sexo y edad usa `personas` (`facpob07`). Di cuál usaste: la nacional da 27.58 % en una y
  27.53 % en la otra, y la diferencia está explicada en `salidas/validacion.txt`.
- Si el coeficiente de variación pasa de 15 %, avisa que la cifra es solo referencial.
- Dos cifras cuyos intervalos se cruzan no prueban una diferencia. Para comparar grupos usa la skill `graficando-enaho`,
  que calcula el intervalo de la diferencia.
- Describe asociaciones sin afirmar causas.

## 5. Límites

- Solo cubre la ENAHO 2024. Si piden otro año, dilo: esta skill no tiene esos datos.
- Antes de usar una variable que no esté en la base, lee [reference.md](reference.md). Si tampoco está en los módulos 34
  y 02, dilo en lugar de aproximarla.
