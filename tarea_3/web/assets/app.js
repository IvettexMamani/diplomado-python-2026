/* Dashboard del subempleo por ingresos. Datos: window.DATOS (data/datos.js) y window.GEO. */
(function () {
  "use strict";
  const D = window.DATOS;
  const GEO = window.GEO;
  const DEP = D.meta.departamentos;
  const ANIOS = [...new Set(D.nacional.map(r => r.anio))].sort();
  const IND = {
    si: { nombre: "Subempleo por ingresos", corto: "subempleo por ingresos" },
    sh: { nombre: "Subempleo por horas", corto: "subempleo por horas" },
    ad: { nombre: "Empleo adecuado", corto: "empleo adecuado" },
    de: { nombre: "Desempleo", corto: "desempleo" },
  };
  const SEXO = { T: "Todos", M: "Mujeres", H: "Hombres" };
  const AREA = { T: "todas las áreas", U: "área urbana", R: "área rural" };
  const ORDEN = {
    sexo: ["Mujer", "Hombre"], area: ["Rural", "Urbana"],
    grupo_edad: ["14-24", "25-44", "45-64", "65+"],
    educacion: ["Primaria o menos", "Secundaria", "Superior no universitaria", "Universitaria"],
  };
  const ETIQ_GRUPO = { "14-24": "14 a 24 años", "25-44": "25 a 44 años", "45-64": "45 a 64 años", "65+": "65 años a más" };

  const estado = { anio: ANIOS[ANIOS.length - 1], dep: "00", sexo: "T", area: "T", ind: "si",
                   mapa: "nivel", lima: "var", grupo: "sexo", buscar: "", orden: { col: "si", desc: true } };

  // ---------- utilidades ----------
  const cubo = new Map(D.cubo.map(r => [`${r.a}|${r.d}|${r.s}|${r.z}`, r]));
  const celda = (a, d, s = estado.sexo, z = estado.area) => cubo.get(`${a}|${d}|${s}|${z}`);
  const nombreDep = d => (d === "00" ? "Perú" : DEP[d]);
  const NBSP = " ";
  function num(x, dec = 1) {
    if (x === null || x === undefined || Number.isNaN(x)) return "—";
    const [ent, frac] = Math.abs(x).toFixed(dec).split(".");
    const miles = ent.replace(/\B(?=(\d{3})+(?!\d))/g, NBSP);
    return (x < 0 ? "−" : "") + miles + (frac ? "," + frac : "");
  }
  const pct = (x, dec = 1) => num(x, dec) + NBSP + "%";
  const pp = (x, dec = 1) => (x > 0 ? "+" : "") + num(x, dec) + NBSP + "pp";
  const signo = (x, dec = 1) => (x > 0 ? "+" : "") + num(x, dec);
  const personas = miles => (miles >= 1000 ? num(miles / 1000, 2) + " millones" : num(miles, 1) + " mil");
  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const z = (a, b) => (b.si - a.si) / Math.hypot(a.se, b.se);
  const el = id => document.getElementById(id);

  function baseLayout(extra = {}) {
    return Object.assign({
      paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
      font: { family: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif', size: 12, color: css("--text-secondary") },
      separators: ", ",
      margin: { l: 48, r: 16, t: 10, b: 40 },
      hoverlabel: { bgcolor: css("--surface-1"), bordercolor: css("--axis"), font: { color: css("--text-primary"), size: 13 } },
      xaxis: { gridcolor: css("--grid"), linecolor: css("--axis"), zerolinecolor: css("--axis"), tickfont: { color: css("--text-muted") } },
      yaxis: { gridcolor: css("--grid"), linecolor: css("--axis"), zerolinecolor: css("--axis"), tickfont: { color: css("--text-muted") } },
      showlegend: false,
    }, extra);
  }
  // topojsonURL: el mapa base de Plotly se sirve desde data/ (sin depender de cdn.plot.ly)
  const CONFIG = { responsive: true, displayModeBar: false, locale: "es", topojsonURL: "data/" };

  // ---------- controles ----------
  function llenarControles() {
    el("f-anio").innerHTML = ANIOS.slice().reverse().map(a => `<option value="${a}">${a}</option>`).join("");
    el("f-anio").value = estado.anio;
    const deps = Object.entries(DEP).sort((a, b) => a[1].localeCompare(b[1], "es"));
    el("f-dep").innerHTML = `<option value="00">Perú (nacional)</option>` +
      deps.map(([c, n]) => `<option value="${c}">${n}</option>`).join("");
    el("f-anio").addEventListener("change", e => { estado.anio = +e.target.value; render(); });
    el("f-dep").addEventListener("change", e => { estado.dep = e.target.value; render(); });
    el("f-ind").addEventListener("change", e => { estado.ind = e.target.value; render(); });
    el("f-grupo").addEventListener("change", e => { estado.grupo = e.target.value; renderBrecha(); });
    el("f-buscar").addEventListener("input", e => { estado.buscar = e.target.value; renderTabla(); });
    el("descargar").addEventListener("click", descargarCSV);
    segmentado("f-sexo", v => { estado.sexo = v; render(); });
    segmentado("f-area", v => { estado.area = v; render(); });
    segmentado("f-mapa", v => { estado.mapa = v; renderMapa(); renderRanking(); });
    segmentado("f-lima", v => { estado.lima = v; renderLima(); });
    segmentado("f-tema", v => {
      if (v === "auto") delete document.documentElement.dataset.theme;
      else document.documentElement.dataset.theme = v;
      try { localStorage.setItem("tema", v); } catch (e) { /* sin almacenamiento */ }
      render();
    });
    let guardado = "auto";
    try { guardado = localStorage.getItem("tema") || "auto"; } catch (e) { /* sin almacenamiento */ }
    if (guardado !== "auto") {
      document.documentElement.dataset.theme = guardado;
      el("f-tema").querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === guardado));
    }
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
  }
  function segmentado(id, alCambiar) {
    const grupo = el(id);
    grupo.addEventListener("click", e => {
      const b = e.target.closest("button");
      if (!b) return;
      grupo.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === b));
      alCambiar(b.dataset.v);
    });
  }

  // ---------- textos ----------
  function renderTextos() {
    const nac = Object.fromEntries(D.nacional.map(r => [r.anio, r]));
    const a0 = D.meta.anio_base, a1 = D.meta.anio_fin;
    const L = D.lima[D.lima.length - 1];
    const racha = (() => { let n = 0; for (let i = D.lima.length - 1; i >= 0 && D.lima[i].var_interanual_pct > 0; i--) n++; return n; })();
    document.querySelectorAll(".corte").forEach(x => (x.textContent = L.trimestre.toLowerCase()));
    el("respuesta").innerHTML =
      `<b>Respuesta corta: en Lima, sí; en el país, todavía no se puede afirmar.</b> En Lima Metropolitana el subempleo por ingresos ` +
      `subió <b>${signo(L.var_interanual_pct)}${NBSP}%</b> en el último año (${L.trimestre.toLowerCase()}): ` +
      `${personas(L.sub_ingresos_miles)} de personas, ${num(L.var_interanual_miles, 1)} mil más. A nivel nacional, el último dato anual ` +
      `(ENAHO ${a1}) muestra lo contrario: bajó de ${pct(nac[a0].tasa_sub_ingresos)} a ${pct(nac[a1].tasa_sub_ingresos)} de la PEA.`;

    const cambio = D.cambio;
    const suben = cambio.filter(r => r.cambio_pp > 0);
    const subenSig = cambio.filter(r => r.cambio_pp > 0 && r.significativo);
    const top = cambio.slice().sort((a, b) => b[`tasa_${a1}`] - a[`tasa_${a1}`]);
    const g = (v, gr) => D.grupos.find(r => r.variable === v && r.grupo === gr && r.anio === a1).tasa;
    const H = [
      ["En Lima, el subempleo por ingresos lleva " + racha + " trimestres móviles seguidos al alza",
       `Según la EPE del INEI, en ${L.trimestre.toLowerCase()} hubo ${num(L.sub_ingresos_miles, 1)} mil subempleados por ingresos en Lima Metropolitana ` +
       `(${pct(L.tasa_sub_ingresos)} de la PEA): ${num(L.var_interanual_miles, 1)} mil más que un año antes (${signo(L.var_interanual_pct)}${NBSP}%). ` +
       `Durante 2025 la serie caía; el giro empezó a fines de 2025.`],
      [`El país venía mejorando: ${pct(nac[a0].tasa_sub_ingresos)} en ${a0} y ${pct(nac[a1].tasa_sub_ingresos)} en ${a1}`,
       `Con la ENAHO, la tasa nacional bajó ${num(nac[a0].tasa_sub_ingresos - nac[a1].tasa_sub_ingresos)} puntos en ${a1} ` +
       `(de ${personas(nac[a0].sub_ingresos_miles)} a ${personas(nac[a1].sub_ingresos_miles)}) y volvió al nivel de 2019 (${pct(nac[2019].tasa_sub_ingresos)}), ` +
       `tras el pico de la pandemia (${pct(nac[2020].tasa_sub_ingresos)} en 2020). El repunte de 2026 aún no aparece en los datos anuales.`],
      [`Tumbes fue la excepción en ${a1}`,
       `${cambio.length - suben.length} de 25 departamentos bajaron. Solo ${subenSig.map(r => r.nombre).join(", ")} subió de forma significativa ` +
       `(${subenSig.map(r => `${pct(r[`tasa_${a0}`])} → ${pct(r[`tasa_${a1}`])}`).join("; ")}). ` +
       `La tasa más alta está en ${top[0].nombre} (${pct(top[0][`tasa_${a1}`])}) y la más baja en ${top[top.length - 1].nombre} (${pct(top[top.length - 1][`tasa_${a1}`])}).`],
      ["Las mujeres y el campo cargan el problema",
       `En ${a1}, ${pct(g("sexo", "Mujer"))} de las mujeres de la PEA estaba subempleada por ingresos, frente a ${pct(g("sexo", "Hombre"))} de los hombres. ` +
       `En el área rural la tasa fue ${pct(g("area", "Rural"))}, frente a ${pct(g("area", "Urbana"))} en la urbana. ` +
       `Con estudios universitarios baja a ${pct(g("educacion", "Universitaria"))}.`],
    ];
    el("hallazgos").innerHTML = H.map(([t, p]) => `<article class="hallazgo"><h3>${t}</h3><p>${p}</p></article>`).join("");
  }

  // ---------- KPIs ----------
  function renderKPIs() {
    const { anio, dep, sexo, area } = estado;
    const c = celda(anio, dep);
    const prev = celda(anio - 1, dep);
    const L = D.lima[D.lima.length - 1];
    el("kpi-sub").textContent = `${nombreDep(dep)} · ${SEXO[sexo]} · ${AREA[area]} · ${anio}. El recuadro naranja es Lima Metropolitana con el dato más reciente (EPE).`;
    const tarjetas = [];
    if (c) {
      let det = "Primer año de la serie";
      if (prev) {
        const dz = z(prev, c), dif = c.si - prev.si;
        const cls = dif > 0 ? "sube" : "baja";
        det = `<span class="${cls}">${dif > 0 ? "▲" : "▼"} ${pp(dif)}</span> vs. ${anio - 1} · ${Math.abs(dz) >= 1.96 ? "cambio significativo" : "cambio no significativo"}`;
      }
      tarjetas.push(["Subempleo por ingresos", pct(c.si), det + `<br>% de la PEA · IC 95 %: ${num(c.si - 1.96 * c.se)}-${num(c.si + 1.96 * c.se)}`]);
      let detP = `de ${personas(c.pea)} en la PEA`;
      if (prev) detP += ` · ${signo(c.mi - prev.mi, 0)} mil vs. ${anio - 1}`;
      tarjetas.push(["Personas subempleadas por ingresos", personas(c.mi), detP]);
    } else {
      tarjetas.push(["Subempleo por ingresos", "—", "Muy pocos encuestados para esta combinación"]);
      tarjetas.push(["Personas subempleadas por ingresos", "—", ""]);
    }
    tarjetas.push(["Lima Metropolitana, último año", signo(L.var_interanual_pct) + NBSP + "%",
      `${personas(L.sub_ingresos_miles)} en ${L.trimestre.toLowerCase()} · ${signo(L.var_interanual_miles, 1)} mil frente al mismo trimestre de 2025`, true]);
    const m = celda(anio, dep, "M"), h = celda(anio, dep, "H");
    if (m && h) {
      tarjetas.push(["Brecha mujeres − hombres", pp(m.si - h.si), `Mujeres ${pct(m.si)} · Hombres ${pct(h.si)} (${nombreDep(dep)}, ${AREA[area]})`]);
    } else {
      tarjetas.push(["Brecha mujeres − hombres", "—", "Muy pocos encuestados"]);
    }
    const filas = Object.keys(DEP).map(d => celda(anio, d)).filter(Boolean).sort((a, b) => b[estado.ind] - a[estado.ind]);
    if (filas.length) {
      const hi = filas[0], lo = filas[filas.length - 1];
      tarjetas.push([`Mayor ${IND[estado.ind].corto}`, DEP[hi.d], `${pct(hi[estado.ind])} · la menor: ${DEP[lo.d]} (${pct(lo[estado.ind])})`]);
    }
    el("kpis").innerHTML = tarjetas.map(([l, v, d, dest]) =>
      `<div class="kpi${dest ? " destacado" : ""}"><div class="lbl">${l}</div><div class="val">${v}</div><div class="det">${d}</div></div>`).join("");
  }

  // ---------- Lima (EPE) ----------
  function renderLima() {
    const vista = estado.lima;
    // La variación interanual de 2020-2022 está dominada por la caída y el rebote de la
    // pandemia (hasta +130 %): esa vista empieza en 2023 para que se lea el último año.
    const desde = vista === "var" ? "2023-01" : "2019-01";
    const datos = D.lima.filter(r => r.mes_final >= desde);
    const x = datos.map(r => r.mes_final + "-01");
    const ult = datos[datos.length - 1];
    let trazas, yaxis, titulo, anot;
    const hover = datos.map(r => `<b>${r.trimestre}</b><br>Subempleados por ingresos: ${num(r.sub_ingresos_miles, 1)} mil<br>` +
      `% de la PEA: ${pct(r.tasa_sub_ingresos)}<br>Variación interanual: ${signo(r.var_interanual_pct)}${NBSP}% (${signo(r.var_interanual_miles, 1)} mil)`);
    if (vista === "var") {
      titulo = "Variación interanual de los subempleados por ingresos en Lima Metropolitana (%)";
      trazas = [{ type: "bar", x, y: datos.map(r => r.var_interanual_pct),
        marker: { color: datos.map(r => (r.var_interanual_pct > 0 ? css("--up") : css("--down"))), line: { width: 0 } },
        hovertext: hover, hoverinfo: "text" }];
      yaxis = { ticksuffix: " %", zeroline: true };
      anot = { x: ult.mes_final + "-01", y: ult.var_interanual_pct, text: `<b>${signo(ult.var_interanual_pct)} %</b>`, yshift: 12, showarrow: false };
    } else {
      const campo = vista === "miles" ? "sub_ingresos_miles" : "tasa_sub_ingresos";
      titulo = vista === "miles" ? "Subempleados por ingresos en Lima Metropolitana (miles de personas)" : "Subempleados por ingresos en Lima Metropolitana (% de la PEA)";
      trazas = [{ type: "scatter", mode: "lines", x, y: datos.map(r => r[campo]), line: { color: css("--series-1"), width: 2 },
        hovertext: hover, hoverinfo: "text" },
        { type: "scatter", mode: "markers", x: [x[x.length - 1]], y: [ult[campo]], marker: { color: css("--series-1"), size: 9, line: { color: css("--surface-1"), width: 2 } }, hoverinfo: "skip" }];
      yaxis = vista === "miles" ? { rangemode: "tozero" } : { ticksuffix: " %", rangemode: "tozero" };
      anot = { x: x[x.length - 1], y: ult[campo], text: `<b>${vista === "miles" ? num(ult[campo], 1) + " mil" : pct(ult[campo])}</b>`, yshift: 16, showarrow: false };
    }
    el("lima-titulo").textContent = titulo;
    const L = baseLayout({ yaxis: Object.assign(baseLayout().yaxis, yaxis), bargap: 0.25,
      annotations: [Object.assign({ font: { color: css("--text-primary"), size: 13 } }, anot)].concat(vista === "var" ? [] :
        [{ x: "2020-09-01", y: 1, yref: "paper", text: "Pandemia", showarrow: false, font: { color: css("--text-muted"), size: 11 } }]),
      shapes: vista === "var" ? [] : [{ type: "rect", xref: "x", yref: "paper", x0: "2020-03-01", x1: "2021-03-01", y0: 0, y1: 1, fillcolor: css("--surface-2"), line: { width: 0 }, layer: "below" }],
      hovermode: "closest" });
    Plotly.react("g-lima", trazas, L, CONFIG);
  }

  // ---------- mapa ----------
  function valoresDep() {
    const { anio, ind } = estado;
    return Object.keys(DEP).map(d => {
      const c = celda(anio, d), p = celda(anio - 1, d);
      if (!c) return null;
      const dif = p ? c[ind] - p[ind] : null;
      const sig = p && ind === "si" ? Math.abs(z(p, c)) >= 1.96 : null;
      return { d, nombre: DEP[d], v: c[ind], dif, sig, n: c.n, se: c.se };
    }).filter(Boolean);
  }
  function renderMapa() {
    const { anio, ind, mapa, dep } = estado;
    const vals = valoresDep();
    const cambio = mapa === "cambio" && anio > ANIOS[0];
    const zv = vals.map(r => (cambio ? r.dif : r.v));
    el("mapa-titulo").textContent = cambio ? `Cambio del ${IND[ind].corto}, ${anio - 1}-${anio}` : `${IND[ind].nombre}, ${anio}`;
    el("mapa-nota").textContent = (cambio ? "Puntos porcentuales · rojo = subió, azul = bajó" : "% de la PEA") +
      ` · ${SEXO[estado.sexo]}, ${AREA[estado.area]}` + (mapa === "cambio" && !cambio ? " · 2019 no tiene año anterior" : "");
    const hover = vals.map(r => `<b>${r.nombre}</b><br>${IND[ind].nombre} ${anio}: ${pct(r.v)}` +
      (r.dif !== null ? `<br>Cambio vs. ${anio - 1}: ${pp(r.dif)}${r.sig === null ? "" : r.sig ? " (significativo)" : " (no significativo)"}` : "") +
      `<br>Encuestados: ${num(r.n, 0)}`);
    let escala, zmin, zmax;
    if (cambio) {
      const m = Math.max(...zv.map(Math.abs));
      escala = [[0, css("--down")], [0.5, css("--mid")], [1, css("--up")]];
      zmin = -m; zmax = m;
    } else {
      escala = [[0, css("--seq-0")], [0.25, css("--seq-1")], [0.5, css("--seq-2")], [0.75, css("--seq-3")], [1, css("--seq-4")]];
      zmin = 0; zmax = Math.max(...zv);
    }
    const trazas = [{
      type: "choropleth", geojson: GEO, featureidkey: "properties.FIRST_IDDP",
      locations: vals.map(r => r.d), z: zv, zmin, zmax, colorscale: escala,
      marker: { line: { color: css("--surface-1"), width: 0.8 } },
      hovertext: hover, hoverinfo: "text",
      colorbar: { thickness: 10, len: 0.6, x: 0.98, ticksuffix: cambio ? " pp" : " %", tickfont: { color: css("--text-muted") }, outlinewidth: 0 },
    }];
    if (dep !== "00") {
      trazas.push({ type: "choropleth", geojson: GEO, featureidkey: "properties.FIRST_IDDP", locations: [dep], z: [1],
        colorscale: [[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale: false,
        marker: { line: { color: css("--text-primary"), width: 2.5 } }, hoverinfo: "skip" });
    }
    const L = baseLayout({ margin: { l: 0, r: 0, t: 0, b: 0 },
      geo: { fitbounds: "locations", visible: false, bgcolor: "rgba(0,0,0,0)", projection: { type: "mercator" } } });
    Plotly.react("g-mapa", trazas, L, CONFIG).then(gd => {
      if (!gd._clicEnlazado) {
        gd.on("plotly_click", ev => {
          const loc = ev.points && ev.points[0] && ev.points[0].location;
          if (loc) { estado.dep = estado.dep === loc ? "00" : loc; el("f-dep").value = estado.dep; render(); }
        });
        gd._clicEnlazado = true;
      }
    });
  }

  // ---------- ranking ----------
  function renderRanking() {
    const { anio, ind, mapa, dep } = estado;
    const cambio = mapa === "cambio" && anio > ANIOS[0];
    const vals = valoresDep().filter(r => !cambio || r.dif !== null)
      .sort((a, b) => (cambio ? a.dif - b.dif : a.v - b.v));
    const y = vals.map(r => r.nombre + (cambio && r.sig ? " *" : ""));
    const xv = vals.map(r => (cambio ? r.dif : r.v));
    const colores = vals.map(r => {
      if (cambio) return r.dif > 0 ? css("--up") : css("--down");
      return dep === "00" || r.d === dep ? css("--series-1") : css("--neutral");
    });
    const opac = vals.map(r => (cambio && ind === "si" && !r.sig ? 0.45 : 1));
    el("rank-titulo").textContent = cambio ? `Cambio ${anio - 1}-${anio} por departamento (pp)` : `${IND[ind].nombre} por departamento, ${anio}`;
    const nac = celda(anio, "00");
    const nacPrev = celda(anio - 1, "00");
    const ref = cambio ? (nac && nacPrev ? nac[ind] - nacPrev[ind] : null) : (nac ? nac[ind] : null);
    const L = baseLayout({ margin: { l: 112, r: 48, t: 4, b: 34 }, bargap: 0.28,
      xaxis: Object.assign(baseLayout().xaxis, { ticksuffix: cambio ? " pp" : " %", zeroline: true,
        // margen para que las etiquetas de los extremos no choquen con el eje
        range: [Math.min(0, ...xv) * 1.22 - (cambio ? 0.6 : 0), Math.max(0, ...xv) * 1.15 + (cambio ? 0.6 : 0)] }),
      yaxis: Object.assign(baseLayout().yaxis, { automargin: true, tickfont: { color: css("--text-secondary"), size: 12 } }),
      shapes: ref === null ? [] : [{ type: "line", x0: ref, x1: ref, y0: -0.5, y1: vals.length - 0.5, line: { color: css("--text-muted"), width: 1.5 } }],
      annotations: ref === null ? [] : [{ x: ref, y: vals.length - 0.5, yanchor: "bottom", text: `Perú ${cambio ? pp(ref) : pct(ref)}`, showarrow: false, font: { size: 11, color: css("--text-muted") } }] });
    Plotly.react("g-rank", [{
      type: "bar", orientation: "h", y, x: xv, marker: { color: colores, opacity: opac },
      text: xv.map(v => (cambio ? signo(v) : num(v))), textposition: "outside", cliponaxis: false,
      textfont: { color: css("--text-secondary"), size: 11 },
      hovertext: vals.map(r => `<b>${r.nombre}</b><br>${IND[ind].nombre}: ${pct(r.v)}` + (r.dif !== null ? `<br>Cambio: ${pp(r.dif)}` : "") +
        (r.sig === null ? "" : r.sig ? "<br>Cambio significativo" : "<br>Cambio no significativo")),
      hoverinfo: "text",
    }], L, CONFIG);
    if (cambio && ind === "si") el("rank-titulo").textContent += " · * = significativo";
  }

  // ---------- tendencia ----------
  function renderTendencia() {
    const { dep, ind } = estado;
    const serie = d => ANIOS.map(a => celda(a, d)).map((c, i) => ({ a: ANIOS[i], c }));
    const sel = serie(dep).filter(r => r.c);
    el("tend-titulo").textContent = `${IND[ind].nombre}: ${nombreDep(dep)}${dep !== "00" ? " frente a Perú" : ""}`;
    const trazas = [];
    if (ind === "si") {
      const sup = sel.map(r => r.c.si + 1.96 * r.c.se), inf = sel.map(r => r.c.si - 1.96 * r.c.se);
      trazas.push({ type: "scatter", mode: "lines", x: sel.map(r => r.a), y: sup, line: { width: 0 }, hoverinfo: "skip", showlegend: false });
      trazas.push({ type: "scatter", mode: "lines", x: sel.map(r => r.a), y: inf, line: { width: 0 }, fill: "tonexty",
        fillcolor: css("--series-1") + "26", hoverinfo: "skip", showlegend: false });
    }
    if (dep !== "00") {
      const p = serie("00").filter(r => r.c);
      trazas.push({ type: "scatter", mode: "lines+markers", name: "Perú", x: p.map(r => r.a), y: p.map(r => r.c[ind]),
        line: { color: css("--neutral"), width: 2 }, marker: { size: 7 },
        hovertemplate: `Perú: %{y:.1f} %<extra></extra>` });
    }
    trazas.push({ type: "scatter", mode: "lines+markers", name: nombreDep(dep), x: sel.map(r => r.a), y: sel.map(r => r.c[ind]),
      line: { color: css("--series-1"), width: 2.5 }, marker: { size: 9, line: { color: css("--surface-1"), width: 2 } },
      hovertemplate: `${nombreDep(dep)}: %{y:.1f} %<extra></extra>` });
    const ult = sel[sel.length - 1];
    const L = baseLayout({ hovermode: "x unified", showlegend: dep !== "00",
      legend: { orientation: "h", y: 1.1, x: 0, font: { color: css("--text-secondary") } },
      xaxis: Object.assign(baseLayout().xaxis, { dtick: 1 }),
      yaxis: Object.assign(baseLayout().yaxis, { ticksuffix: " %", rangemode: "tozero" }),
      annotations: ult ? [{ x: ult.a, y: ult.c[ind], text: `<b>${pct(ult.c[ind])}</b>`, xanchor: "left", xshift: 8, showarrow: false, font: { color: css("--text-primary") } }] : [],
      shapes: [{ type: "rect", x0: 2019.5, x1: 2020.5, y0: 0, y1: 1, yref: "paper", fillcolor: css("--surface-2"), line: { width: 0 }, layer: "below" }] });
    L.margin.r = 56;
    Plotly.react("g-tend", trazas, L, CONFIG);
  }

  // ---------- brechas ----------
  function renderBrecha() {
    const v = estado.grupo, a1 = estado.anio, a0 = a1 - 1;
    const filas = D.grupos.filter(r => r.variable === v);
    let grupos = ORDEN[v] || [...new Set(filas.filter(r => r.anio === a1).sort((a, b) => a.tasa - b.tasa).map(r => r.grupo))];
    if (ORDEN[v]) grupos = grupos.slice().reverse();
    const val = (g, a) => (filas.find(r => r.grupo === g && r.anio === a) || {}).tasa;
    const etiqueta = g => ETIQ_GRUPO[g] || g;
    el("brecha-nota").textContent = `Perú · % de ${v === "sector" ? "los ocupados de cada sector" : "la PEA de cada grupo"} · ${ANIOS.includes(a0) ? a0 + " y " : ""}${a1}`;
    const trazas = [];
    if (ANIOS.includes(a0)) {
      trazas.push({ type: "bar", orientation: "h", name: String(a0), y: grupos.map(etiqueta), x: grupos.map(g => val(g, a0)),
        marker: { color: css("--seq-1") }, hovertemplate: `${a0}: %{x:.1f} %<extra></extra>` });
    }
    trazas.push({ type: "bar", orientation: "h", name: String(a1), y: grupos.map(etiqueta), x: grupos.map(g => val(g, a1)),
      marker: { color: css("--series-1") }, text: grupos.map(g => num(val(g, a1))), textposition: "outside", cliponaxis: false,
      textfont: { color: css("--text-secondary"), size: 11 }, hovertemplate: `${a1}: %{x:.1f} %<extra></extra>` });
    const L = baseLayout({ barmode: "group", bargap: 0.3, bargroupgap: 0.08, showlegend: true, hovermode: "y unified",
      legend: { orientation: "h", y: 1.12, x: 0, traceorder: "normal", font: { color: css("--text-secondary") } },
      margin: { l: 150, r: 40, t: 10, b: 34 },
      xaxis: Object.assign(baseLayout().xaxis, { ticksuffix: " %", rangemode: "tozero" }),
      yaxis: Object.assign(baseLayout().yaxis, { automargin: true, tickfont: { color: css("--text-secondary"), size: 12 } }) });
    Plotly.react("g-brecha", trazas, L, CONFIG);
  }

  // ---------- tabla ----------
  const COLS = [
    ["nombre", "Departamento", r => r.nombre],
    ["si", "Subempleo por ingresos (%)", r => num(r.si)],
    ["ic", "IC 95 %", r => `${num(r.si - 1.96 * r.se)}-${num(r.si + 1.96 * r.se)}`],
    ["dif", "Cambio vs. año anterior (pp)", r => (r.dif === null ? "—" : signo(r.dif) + (r.sig ? " *" : ""))],
    ["sh", "Subempleo por horas (%)", r => num(r.sh)],
    ["ad", "Empleo adecuado (%)", r => num(r.ad)],
    ["de", "Desempleo (%)", r => num(r.de)],
    ["mi", "Subempleados por ingresos (miles)", r => num(r.mi)],
    ["n", "Encuestados", r => num(r.n, 0)],
  ];
  function filasTabla() {
    const { anio } = estado;
    const q = estado.buscar.trim().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
    const filas = Object.keys(DEP).map(d => {
      const c = celda(anio, d), p = celda(anio - 1, d);
      if (!c) return null;
      return Object.assign({}, c, { nombre: DEP[d], dif: p ? c.si - p.si : null, sig: p ? Math.abs(z(p, c)) >= 1.96 : false, ic: c.si });
    }).filter(Boolean).filter(r => r.nombre.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").includes(q));
    const { col, desc } = estado.orden;
    filas.sort((a, b) => {
      const x = a[col], y = b[col];
      if (typeof x === "string") return desc ? y.localeCompare(x, "es") : x.localeCompare(y, "es");
      return desc ? (y ?? -1e9) - (x ?? -1e9) : (x ?? 1e9) - (y ?? 1e9);
    });
    return filas;
  }
  function renderTabla() {
    const filas = filasTabla();
    const flecha = k => (estado.orden.col === k ? (estado.orden.desc ? " ↓" : " ↑") : "");
    el("tabla").innerHTML = `<thead><tr>${COLS.map(([k, t]) => `<th data-k="${k}" scope="col">${t}${flecha(k)}</th>`).join("")}</tr></thead>` +
      `<tbody>${filas.map(r => `<tr class="${r.d === estado.dep ? "sel" : ""}">${COLS.map(([, , f]) => `<td>${f(r)}</td>`).join("")}</tr>`).join("")}</tbody>`;
    el("tabla").querySelectorAll("th").forEach(th => th.addEventListener("click", () => {
      const k = th.dataset.k;
      estado.orden = { col: k, desc: estado.orden.col === k ? !estado.orden.desc : k !== "nombre" };
      renderTabla();
    }));
  }
  function descargarCSV() {
    const filas = filasTabla();
    const enc = ["departamento", "anio", "sexo", "area", "tasa_sub_ingresos", "ic95_inferior", "ic95_superior",
      "cambio_pp_vs_anio_anterior", "cambio_significativo", "tasa_sub_horas", "tasa_empleo_adecuado", "tasa_desempleo",
      "sub_ingresos_miles", "pea_miles", "encuestados"];
    const lineas = [enc.join(",")].concat(filas.map(r => [
      `"${r.nombre}"`, estado.anio, SEXO[estado.sexo], AREA[estado.area].replace("área ", ""), r.si,
      (r.si - 1.96 * r.se).toFixed(2), (r.si + 1.96 * r.se).toFixed(2), r.dif === null ? "" : r.dif.toFixed(2),
      r.dif === null ? "" : r.sig, r.sh, r.ad, r.de, r.mi, r.pea, r.n].join(",")));
    const blob = new Blob(["﻿" + lineas.join("\n")], { type: "text/csv;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `subempleo_departamentos_${estado.anio}_${estado.sexo}_${estado.area}.csv`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  function render() {
    renderKPIs(); renderLima(); renderMapa(); renderRanking(); renderTendencia(); renderBrecha(); renderTabla();
  }

  if (!window.Plotly) {
    document.querySelectorAll(".chart").forEach(c => (c.textContent = "No se pudo cargar la librería de gráficos (Plotly). Revisa tu conexión."));
  }
  llenarControles();
  renderTextos();
  if (window.Plotly) render(); else { renderKPIs(); renderTabla(); }
})();
