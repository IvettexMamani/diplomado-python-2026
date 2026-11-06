---
name: graficando-enaho
description: Hace gráficos de barras de la pobreza monetaria en el Perú con la ENAHO 2024 del INEI, con estimaciones ponderadas e intervalos de confianza, por área urbana y rural, sexo, grupo de edad, región o departamento. Úsala cuando pidan graficar, visualizar o comparar en un gráfico la pobreza o la pobreza extrema, o mostrar brechas entre grupos con la ENAHO.
argument-hint: "[qué graficar, en lenguaje natural]"
allowed-tools: Bash(uv run *), PowerShell(uv run *), Read
---

# Graficar la pobreza de la ENAHO 2024

Pedido: $ARGUMENTS

## 1. Revisar que exista la base

Si no existen `salidas/personas_2024.parquet` y `salidas/hogares_2024.parquet`, usa primero la skill `limpiando-enaho` y
vuelve aquí cuando su validación diga `RESULTADO: APROBADA`. Si la validación falla, detente.

## 2. Traducir el pedido a opciones

| Si piden | Usa |
|---|---|
| Urbano y rural, brecha urbano-rural, ciudad y campo | `--por area` |
| Hombres y mujeres, sexo, género | `--por sexo` |
| Edad, niños, jóvenes, adultos mayores | `--por grupo_edad` |
| Costa, sierra y selva, regiones, dominios | `--por dominio` |
| Departamentos, regiones políticas, ranking territorial | `--por departamento` |
| Pobreza extrema | añade `--indicador pobre_extremo` |
| Solo en un lugar o grupo | añade `--solo columna=valor`: `--solo departamento=Puno`, `--solo area=Rural`, `--solo sexo=Mujer`; se puede repetir |

Si el pedido no dice qué comparar, haz el gráfico de `area`, que es la brecha más usada, y dilo.

## 3. Generar el gráfico

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/graficar.py" --por area
```

Para varios gráficos, corre el comando una vez por cada uno. No dibujes con código propio: el script pondera, calcula los
intervalos, escribe el título con las cifras y guarda el PNG a 200 dpi en `figuras/`.

## 4. Mirar y responder

1. Abre el PNG con Read y comprueba que se lea bien.
2. Responde con la ruta del archivo y las cifras que imprimió el script.
3. Interpreta si la diferencia es real: el script dice si es distinguible del error de muestreo. Si no lo es, dilo con
   esas palabras en lugar de afirmar una brecha.
4. Si una cifra lleva †, avisa que es solo referencial.
5. Describe asociaciones sin afirmar causas.

## Reglas del gráfico

Todas las aplica el script; revísalas al mirar la imagen.

- Estimaciones ponderadas y una sola base por gráfico: la línea del total sale de la misma base que las barras.
- Barras que empiezan en cero, ordenadas de mayor a menor. Sexo y edad conservan su orden natural.
- Un solo color. El tono suave marca a quien no se distingue del total.
- Título con el hallazgo; debajo, indicador, unidad, lugar y año; al pie, la fuente.

## Límites

Si piden una variable que no está en la base, por ejemplo nivel educativo o empleo, consulta
`.claude/skills/limpiando-enaho/reference.md`. Si no está en los módulos 34 y 02, dilo: no la aproximes con otra.
