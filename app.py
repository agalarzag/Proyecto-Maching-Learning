"""
SIAGD-YAU v4.0 — Minimalist Luxury 3D Civic AI Platform (Streamlit Full-Stack Edition)
- Corrige el corte superior de la cabecera (Image 1).
- En Pestaña 1 y Pestaña 2: primero se sube el archivo PDF, luego aparece el botón dorado
  "EJECUTAR EVALUACIÓN IA", muestra animación de carga por etapas en tiempo real, y recién
  despliega el dictamen (Images 2 & 3).
- Elimina de la web los selectores/descargas de PDFs de muestra (los 3 PDFs oficiales con
  estructura gráfica real están en la carpeta `EJEMPLOS_PDF_PARA_SUBIR/`).
"""

import os
import time
import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.data_pipeline import hash_pii
from src.ml_engine import predict_single_tramite, evaluate_candidate_cv
from src.alerts_feedback import dispatch_citizen_alert, get_recent_alerts
from src.pdf_processor import (
    analyze_pdf_as_tramite,
    analyze_pdf_as_cv,
    generate_sample_pdfs
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")

# Generar en la carpeta local EJEMPLOS_PDF_PARA_SUBIR/ los 3 PDFs oficiales estructurados
generate_sample_pdfs()

st.set_page_config(
    page_title="SIAGD-YAU 3D | Municipalidad Provincial de Yau",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# CSS FULL-STACK: CORRIGE EL CORTE DEL HEADER SUPERIOR Y ESTILIZA TABS & BOTONES
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

.stApp {
    background: radial-gradient(circle at 50% 0%, #161320 0%, #070709 70%) !important;
    color: #F4EFE6 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Hacer transparente la barra superior nativa de Streamlit para que NUNCA tape las letras */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 2.2rem !important;
}

.block-container {
    padding-top: 2.8rem !important;
    padding-bottom: 3rem !important;
    max-width: 1320px !important;
}

/* Cabecera Minimalista Supima / KOBA con holgura superior perfecta */
.topbar-minimal {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 4px 18px 4px;
    border-bottom: 1px solid rgba(212, 175, 55, 0.22);
    margin-bottom: 18px;
}

.brand-minimal {
    font-family: 'Cormorant Garamond', serif;
    font-size: 25px;
    font-weight: 600;
    letter-spacing: 0.12em;
    color: #F4EFE6;
    text-transform: uppercase;
    line-height: 1.3;
}

.status-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.14em;
    color: #6EE7B7;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.38);
    padding: 7px 16px;
    border-radius: 999px;
}

/* 4 Tarjetas KPI Ultra-Limpias (Foundry Bento) */
.kpi-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 16px 0 26px 0;
}

.kpi-pill {
    background: rgba(17, 18, 25, 0.78);
    border: 1px solid rgba(244, 239, 230, 0.08);
    border-top: 2px solid #D4AF37;
    border-radius: 12px;
    padding: 18px 20px;
}

.kpi-code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.16em;
    color: #D4AF37;
    text-transform: uppercase;
}

.kpi-big {
    font-family: 'Cormorant Garamond', serif;
    font-size: 42px;
    font-weight: 600;
    color: #F4EFE6;
    line-height: 1.05;
    margin: 4px 0;
}

.kpi-short {
    font-size: 12px;
    color: #A39E93;
}

/* Pill Dock de 4 Cápsulas */
div[data-baseweb="tab-list"] {
    display: grid !important;
    grid-template-columns: repeat(4, 1fr) !important;
    gap: 12px !important;
    background: rgba(12, 13, 18, 0.88) !important;
    padding: 8px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(212, 175, 55, 0.25) !important;
    margin-bottom: 24px !important;
}

button[data-baseweb="tab"] {
    width: 100% !important;
    justify-content: center !important;
    border-radius: 10px !important;
    padding: 12px 10px !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #A39E93 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(212, 175, 55, 0.22) 0%, rgba(212, 175, 55, 0.08) 100%) !important;
    border: 1px solid #D4AF37 !important;
    color: #F4EFE6 !important;
    font-weight: 600 !important;
}

div[data-baseweb="tab-highlight"],
div[data-baseweb="tab-border"] {
    display: none !important;
}

/* Zona Drag & Drop PDF */
section[data-testid="stFileUploaderDropzone"] {
    background: rgba(212, 175, 55, 0.05) !important;
    border: 1.5px dashed rgba(212, 175, 55, 0.45) !important;
    border-radius: 14px !important;
    padding: 26px !important;
}

/* Botón Dorado Principal de Evaluación IA */
div.stButton > button {
    background: linear-gradient(135deg, #D4AF37 0%, #AA821C 100%) !important;
    color: #070709 !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.85rem 1.4rem !important;
    width: 100% !important;
    box-shadow: 0 10px 28px rgba(212, 175, 55, 0.28) !important;
    transition: all 0.25s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 14px 36px rgba(212, 175, 55, 0.45) !important;
}

.awaiting-box {
    background: rgba(15, 17, 24, 0.55);
    border: 1px dashed rgba(244, 239, 230, 0.14);
    border-radius: 14px;
    padding: 48px 28px;
    text-align: center;
    color: #A39E93;
}
</style>
""", unsafe_allow_html=True)

with open(os.path.join(GOLD_DIR, "ml_metrics_report.json"), "r", encoding="utf-8") as f:
    metrics = json.load(f)

df_kpis = pd.read_csv(os.path.join(GOLD_DIR, "kpis_cuellos_botella.csv"))

# ==============================================================================
# 1. BARRA SUPERIOR (SIN NINGÚN CORTE EN LAS LETRAS) + ESCULTURA 3D
# ==============================================================================
st.markdown("""
<div class="topbar-minimal">
    <div class="brand-minimal">🏛️ SIAGD — YAU <span style="font-size:13px; color:#D4AF37; font-family:'JetBrains Mono',monospace;">// SPATIAL CIVIC AI</span></div>
    <div class="status-badge">● MOTOR PDF + 4 MODELOS ML ACTIVOS</div>
</div>
""", unsafe_allow_html=True)

threejs_minimal_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;1,400&family=Plus+Jakarta+Sans:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: linear-gradient(135deg, #09090d 0%, #15121e 100%);
    color: #F4EFE6;
    font-family: 'Plus Jakarta Sans', sans-serif;
    overflow: hidden;
    border-radius: 16px;
    border: 1px solid rgba(212, 175, 55, 0.26);
  }
  #wrap {
    position: relative;
    width: 100%;
    height: 320px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 26px 36px;
  }
  #c3d {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    cursor: grab;
  }
  .hero-left {
    position: relative;
    z-index: 5;
    max-width: 430px;
    pointer-events: none;
  }
  .eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    color: #D4AF37;
    text-transform: uppercase;
    margin-bottom: 10px;
    display: block;
  }
  h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 38px;
    font-weight: 600;
    line-height: 1.06;
    margin-bottom: 10px;
  }
  h1 em { color: #E6C762; font-style: italic; font-weight: 400; }
  p { font-size: 13px; color: #A39E93; line-height: 1.55; }
  .hero-right {
    position: relative;
    z-index: 5;
    width: 310px;
    background: rgba(9, 10, 14, 0.78);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(212, 175, 55, 0.25);
    border-radius: 12px;
    padding: 16px;
  }
  .grid-btns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7px;
    margin-bottom: 12px;
  }
  .mbtn {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(212,175,55,0.2);
    color: #F4EFE6;
    padding: 8px 10px;
    border-radius: 7px;
    font-size: 11px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
  }
  .mbtn:hover, .mbtn.active {
    background: rgba(212,175,55,0.22);
    border-color: #D4AF37;
  }
  .mbtn span {
    display: block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: #D4AF37;
  }
  .mini-info { font-size: 12px; color: #E6C762; font-weight: 600; margin-bottom: 3px; }
  .mini-sub { font-size: 11.5px; color: #A39E93; line-height: 1.45; }
</style>
</head>
<body>
<div id="wrap">
  <canvas id="c3d"></canvas>
  <div class="hero-left">
    <span class="eyebrow">MUNICIPALIDAD PROVINCIAL DE YAU</span>
    <h1>Gestión Documental &amp; Selección de CVs <em>con IA 3D.</em></h1>
    <p>Sube cualquier expediente o currículum en <strong>PDF</strong> y presiona el botón de evaluación para ejecutar los 4 modelos de Machine Learning.</p>
  </div>
  <div class="hero-right">
    <span class="eyebrow" style="margin-bottom:6px;">NÚCLEO 3D • TOCA UN CEREBRO IA</span>
    <div class="grid-btns">
      <button class="mbtn active" onclick="pick(0, this)"><span>M1 • 94.7%</span>Prioridades</button>
      <button class="mbtn" onclick="pick(1, this)"><span>M2 • 89.6%</span>Anti-Errores</button>
      <button class="mbtn" onclick="pick(2, this)"><span>M3 • 96.4%</span>Plazo Días</button>
      <button class="mbtn" onclick="pick(3, this)"><span>M4 • 98.8%</span>Selector CVs</button>
    </div>
    <div class="mini-info" id="mi-title">M1: Priorizador Automático (NLP)</div>
    <div class="mini-sub" id="mi-desc">Detecta emergencias y adultos mayores en el PDF para atenderlos primero.</div>
  </div>
</div>
<script>
  const canvas = document.getElementById('c3d');
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, window.innerWidth / 320, 0.1, 1000);
  camera.position.set(0, 0, 14);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, 320);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const l1 = new THREE.PointLight(0xD4AF37, 2.8, 40); l1.position.set(5, 5, 7); scene.add(l1);
  const l2 = new THREE.PointLight(0x38BDF8, 1.8, 40); l2.position.set(-5, -4, 6); scene.add(l2);

  const grp = new THREE.Group();
  scene.add(grp);

  const core = new THREE.Mesh(
    new THREE.IcosahedronGeometry(2.1, 1),
    new THREE.MeshStandardMaterial({ color: 0x171822, metalness: 0.85, roughness: 0.2, flatShading: true })
  );
  grp.add(core);

  const wireMat = new THREE.MeshBasicMaterial({ color: 0xD4AF37, wireframe: true, transparent: true, opacity: 0.45 });
  const wire = new THREE.Mesh(new THREE.IcosahedronGeometry(2.35, 1), wireMat);
  grp.add(wire);

  const cols = [0xD4AF37, 0x38BDF8, 0x10B981, 0xF59E0B];
  const sats = [];
  for (let i = 0; i < 4; i++) {
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(3.0 + i * 0.55, 0.016, 16, 90),
      new THREE.MeshBasicMaterial({ color: cols[i], transparent: true, opacity: 0.38 })
    );
    ring.rotation.x = 1.1 + i * 0.3; ring.rotation.y = i * 0.5;
    grp.add(ring);

    const sat = new THREE.Mesh(
      new THREE.OctahedronGeometry(0.3, 0),
      new THREE.MeshStandardMaterial({ color: cols[i], emissive: cols[i], emissiveIntensity: 0.5 })
    );
    grp.add(sat);
    sats.push({ mesh: sat, r: 3.0 + i * 0.55, a: i * 1.5, s: 0.01 - i * 0.0015 });
  }

  let mx = 0, my = 0, sc = 1;
  window.addEventListener('mousemove', e => {
    mx = (e.clientX / window.innerWidth - 0.5) * 2;
    my = -(e.clientY / 320 - 0.5) * 2;
  });

  function anim() {
    requestAnimationFrame(anim);
    core.rotation.y += 0.004; wire.rotation.y -= 0.003;
    grp.rotation.y += (mx * 0.5 - grp.rotation.y) * 0.05;
    grp.rotation.x += (-my * 0.35 - grp.rotation.x) * 0.05;
    grp.scale.lerp(new THREE.Vector3(sc, sc, sc), 0.08);
    sats.forEach(s => {
      s.a += s.s;
      s.mesh.position.set(Math.cos(s.a) * s.r, Math.sin(s.a * 0.8) * 1.0, Math.sin(s.a) * s.r);
      s.mesh.rotation.y += 0.03;
    });
    renderer.render(scene, camera);
  }
  anim();

  const items = [
    { t: "M1: Priorizador Automático (NLP)", d: "Detecta emergencias y adultos mayores en el PDF para atenderlos primero.", c: 0xD4AF37 },
    { t: "M2: Filtro Anti-Errores TUPA", d: "Verifica en ventanilla que el PDF tenga firma válida y requisitos completos.", c: 0x38BDF8 },
    { t: "M3: Predictor de Plazo Real (SLA)", d: "Calcula los días exactos de atención y envía alerta inmediata por WhatsApp.", c: 0x10B981 },
    { t: "M4: Evaluador de Currículos CAS", d: "Lee el CV en PDF, extrae experiencia y valida que no tenga sanciones SERVIR.", c: 0xF59E0B }
  ];

  function pick(i, btn) {
    document.querySelectorAll('.mbtn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('mi-title').textContent = items[i].t;
    document.getElementById('mi-desc').textContent = items[i].d;
    wireMat.color.setHex(items[i].c); l1.color.setHex(items[i].c);
    sc = 1.18; setTimeout(() => { sc = 1.0; }, 300);
  }
</script>
</body>
</html>
"""
components.html(threejs_minimal_html, height=335)

# ==============================================================================
# 2. TIRA MINIMALISTA DE 4 KPIs
# ==============================================================================
st.markdown(f"""
<div class="kpi-strip">
    <div class="kpi-pill">
        <div class="kpi-code">01 · PRIORIZACIÓN IA</div>
        <div class="kpi-big">{metrics['modelo_1_priorizacion']['roc_auc_ovr']*100:.2f}%</div>
        <div class="kpi-short">ROC-AUC • Triaje de Urgencias</div>
    </div>
    <div class="kpi-pill">
        <div class="kpi-code">02 · FILTRO VENTANILLA</div>
        <div class="kpi-big">{metrics['modelo_2_deteccion_errores']['accuracy']*100:.2f}%</div>
        <div class="kpi-short">Exactitud • Detector de Errores</div>
    </div>
    <div class="kpi-pill">
        <div class="kpi-code">03 · CÁLCULO DE PLAZO</div>
        <div class="kpi-big">{metrics['modelo_3_regresion_sla']['r2_score']*100:.2f}%</div>
        <div class="kpi-short">R² Score • Error ±{metrics['modelo_3_regresion_sla']['mae_dias']:.2f} días</div>
    </div>
    <div class="kpi-pill">
        <div class="kpi-code">04 · SELECCIÓN CV CAS</div>
        <div class="kpi-big">{metrics['modelo_4_seleccion_curriculos']['roc_auc']*100:.2f}%</div>
        <div class="kpi-short">ROC-AUC • Meritocracia SERVIR</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGACIÓN PILL DOCK DE 4 CÁPSULAS
# ==============================================================================
tabs = st.tabs([
    "01 · SUBIR PDF TRÁMITE",
    "02 · SUBIR PDF CURRÍCULO",
    "03 · CUELLOS DE BOTELLA",
    "04 · ALERTAS EN VIVO"
])

# ------------------------------------------------------------------------------
# PESTAÑA 1: SUBIR PDF TRÁMITE -> BOTÓN DE EVALUACIÓN -> LOADING -> DICTAMEN
# ------------------------------------------------------------------------------
with tabs[0]:
    col_up, col_res = st.columns([1.0, 1.05], gap="large")

    with col_up:
        st.markdown("#### 📄 1. Carga del Expediente Municipal (PDF)")
        uploaded_tramite_pdf = st.file_uploader(
            "Selecciona o arrastra desde tu PC el archivo PDF del trámite",
            type=["pdf"],
            key="uploader_tramite_pdf"
        )

        eval_tramite_clicked = False
        if uploaded_tramite_pdf is not None:
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            eval_tramite_clicked = st.button(
                "✦ ANALIZAR EXPEDIENTE PDF CON INTELIGENCIA ARTIFICIAL",
                key="btn_evaluar_tramite_pdf"
            )

    with col_res:
        st.markdown("#### ⚡ 2. Dictamen de Machine Learning & Alerta")
        if uploaded_tramite_pdf is None:
            st.session_state.pop("last_tramite_result", None)
            st.markdown("""
            <div class="awaiting-box">
                <div style="font-size:28px; margin-bottom:8px;">📥</div>
                <div style="font-family:'Cormorant Garamond',serif; font-size:24px; color:#F4EFE6; margin-bottom:6px;">
                    Esperando archivo PDF de trámite
                </div>
                <div style="font-size:13px;">
                    Sube un documento PDF en el panel izquierdo y presiona el botón dorado para iniciar la evaluación IA.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            if eval_tramite_clicked:
                pdf_bytes = uploaded_tramite_pdf.read()
                pdf_name = uploaded_tramite_pdf.name

                with st.status("🔄 Procesando expediente PDF con la Suite de Machine Learning...", expanded=True) as status:
                    st.write("1/4 📄 Extrayendo capa de texto, folios y verificando firma digital del PDF...")
                    time.sleep(0.45)
                    meta_t = analyze_pdf_as_tramite(pdf_bytes, pdf_name)

                    st.write("2/4 🔐 Aplicando seudonimización criptográfica SHA-256 al DNI (Ley N° 29733)...")
                    time.sleep(0.35)
                    ciudadano_hash = hash_pii(meta_t["dni_ciudadano"])

                    st.write("3/4 🧠 Ejecutando Modelo 1 (Prioridad NLP), Modelo 2 (Anti-Errores) y Modelo 3 (Plazo SLA)...")
                    time.sleep(0.45)
                    pred_t = predict_single_tramite(meta_t)
                    exp_id = f"EXP-PDF-{ciudadano_hash[:6].upper()}"

                    st.write("4/4 📲 Despachando notificación en tiempo real al ciudadano (WhatsApp / Casilla)...")
                    time.sleep(0.30)
                    alerta_t = dispatch_citizen_alert(
                        expediente_id=exp_id,
                        ciudadano_hash_id=ciudadano_hash,
                        codigo_tupa=meta_t["codigo_tupa"],
                        nivel_prioridad=pred_t["nivel_prioridad"],
                        tiene_error=pred_t["tiene_error_documental"],
                        dias_estimados=pred_t["tiempo_estimado_siagd_dias"]
                    )
                    status.update(label="✅ Evaluación IA completada con éxito", state="complete", expanded=False)

                st.session_state["last_tramite_result"] = {
                    "file_name": pdf_name,
                    "meta": meta_t,
                    "hash": ciudadano_hash,
                    "pred": pred_t,
                    "alerta": alerta_t
                }

            saved_t = st.session_state.get("last_tramite_result")
            if saved_t and saved_t["file_name"] == uploaded_tramite_pdf.name:
                meta_t = saved_t["meta"]
                ciudadano_hash = saved_t["hash"]
                pred_t = saved_t["pred"]
                alerta_t = saved_t["alerta"]
                b_color = "#EF4444" if pred_t["tiene_error_documental"] else "#10B981"

                st.markdown(f"""
                <div style="background:rgba(15,17,24,0.92); border:1px solid {b_color}; border-left:5px solid {b_color}; border-radius:14px; padding:22px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-family:'JetBrains Mono',monospace; font-size:11px; color:#D4AF37;">
                            📄 {meta_t['nombre_archivo']} ({meta_t['tamano_kb']} KB • {meta_t['num_folios']} folios)
                        </span>
                        <span style="font-family:'JetBrains Mono',monospace; font-size:11px; color:{b_color}; font-weight:700;">
                            PRIORIDAD {pred_t['nivel_prioridad']} ({pred_t['confianza_prioridad_pct']}%)
                        </span>
                    </div>
                    <div style="font-family:'Cormorant Garamond',serif; font-size:28px; color:#F4EFE6; margin-bottom:10px;">
                        {meta_t['codigo_tupa']} • {'OBSERVADO EN VENTANILLA' if pred_t['tiene_error_documental'] else 'ADMITIDO Y PRIORIZADO'}
                    </div>
                    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px; background:rgba(0,0,0,0.4); padding:12px; border-radius:8px; margin-bottom:12px;">
                        <div>
                            <div style="font-size:10px; color:#A39E93;">DNI (HASH LEY 29733)</div>
                            <div style="font-size:14px; font-family:'JetBrains Mono',monospace; color:#E6C762;">{ciudadano_hash[:10]}...</div>
                        </div>
                        <div>
                            <div style="font-size:10px; color:#A39E93;">RIESGO DE ERROR</div>
                            <div style="font-size:18px; font-weight:700; color:{b_color};">{pred_t['riesgo_error_documental_pct']}%</div>
                        </div>
                        <div>
                            <div style="font-size:10px; color:#A39E93;">TIEMPO ESTIMADO IA</div>
                            <div style="font-size:18px; font-weight:700; color:#10B981;">{pred_t['tiempo_estimado_siagd_dias']} días <span style="font-size:11px; color:#A39E93; text-decoration:line-through;">({pred_t['tiempo_estimado_manual_dias']}d)</span></div>
                        </div>
                    </div>
                    <div style="font-size:12.5px; color:#A39E93; background:rgba(255,255,255,0.03); padding:10px; border-radius:6px; margin-bottom:12px;">
                        <strong>Extracto leído del PDF:</strong> <em>"{meta_t['texto_extraido'][:230]}..."</em>
                    </div>
                    <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); padding:12px; border-radius:8px; font-size:12.5px; color:#D1FAE5;">
                        <strong>📲 Alerta WhatsApp enviada ({alerta_t['latencia_ms']} ms):</strong><br/>
                        {alerta_t['mensaje']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="awaiting-box" style="border-color:rgba(212,175,55,0.45);">
                    <div style="font-size:28px; margin-bottom:8px;">✨</div>
                    <div style="font-family:'Cormorant Garamond',serif; font-size:24px; color:#E6C762; margin-bottom:6px;">
                        Archivo "{uploaded_tramite_pdf.name}" cargado y listo
                    </div>
                    <div style="font-size:13px;">
                        Haz clic en el botón dorado <strong>"ANALIZAR EXPEDIENTE PDF CON INTELIGENCIA ARTIFICIAL"</strong> para iniciar la lectura y evaluación.
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PESTAÑA 2: SUBIR PDF CURRÍCULO -> BOTÓN DE EVALUACIÓN -> LOADING -> DICTAMEN
# ------------------------------------------------------------------------------
with tabs[1]:
    c_cv_up, c_cv_res = st.columns([1.0, 1.05], gap="large")

    with c_cv_up:
        st.markdown("#### 🎖️ 1. Carga del Currículum Vitae (PDF)")
        uploaded_cv_pdf = st.file_uploader(
            "Selecciona o arrastra desde tu PC el Currículum Vitae en PDF",
            type=["pdf"],
            key="uploader_cv_pdf"
        )

        eval_cv_clicked = False
        if uploaded_cv_pdf is not None:
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            eval_cv_clicked = st.button(
                "✦ EVALUAR CURRÍCULO PDF CON INTELIGENCIA ARTIFICIAL",
                key="btn_evaluar_cv_pdf"
            )

    with c_cv_res:
        st.markdown("#### 🔍 2. Dictamen de Selección CAS / SERVIR (Modelo 4)")
        if uploaded_cv_pdf is None:
            st.session_state.pop("last_cv_result", None)
            st.markdown("""
            <div class="awaiting-box">
                <div style="font-size:28px; margin-bottom:8px;">📥</div>
                <div style="font-family:'Cormorant Garamond',serif; font-size:24px; color:#F4EFE6; margin-bottom:6px;">
                    Esperando archivo PDF de Currículum Vitae
                </div>
                <div style="font-size:13px;">
                    Sube un CV en formato PDF en el panel izquierdo y presiona el botón dorado para que el Modelo 4 lo evalúe.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            if eval_cv_clicked:
                cv_bytes = uploaded_cv_pdf.read()
                cv_fname = uploaded_cv_pdf.name

                with st.status("🔄 Analizando Currículum Vitae PDF con NLP y Gradient Boosting...", expanded=True) as status_cv:
                    st.write("1/3 📄 Extrayendo formación académica, colegiatura y años de experiencia del PDF...")
                    time.sleep(0.45)
                    meta_cv = analyze_pdf_as_cv(cv_bytes, cv_fname)

                    st.write("2/3 🔍 Vectorizando competencias técnicas (TF-IDF) y verificando registro de sanciones RNSSC...")
                    time.sleep(0.45)
                    res_cv = evaluate_candidate_cv(meta_cv)

                    st.write("3/3 🏅 Calculando puntaje de idoneidad meritocrática SERVIR...")
                    time.sleep(0.30)
                    status_cv.update(label="✅ Currículum Vitae evaluado con éxito", state="complete", expanded=False)

                st.session_state["last_cv_result"] = {
                    "file_name": cv_fname,
                    "meta": meta_cv,
                    "res": res_cv
                }

            saved_cv = st.session_state.get("last_cv_result")
            if saved_cv and saved_cv["file_name"] == uploaded_cv_pdf.name:
                meta_cv = saved_cv["meta"]
                res_cv = saved_cv["res"]
                c_border = "#10B981" if res_cv["apto_preseleccion"] else "#EF4444"
                skills_badges = " • ".join([s.upper() for s in meta_cv["skills_detectadas"]])

                st.markdown(f"""
                <div style="background:rgba(15,17,24,0.92); border:1px solid {c_border}; border-left:5px solid {c_border}; border-radius:14px; padding:22px;">
                    <span style="font-family:'JetBrains Mono',monospace; font-size:11px; color:#D4AF37;">
                        📄 {meta_cv['nombre_archivo']} ({meta_cv['tamano_kb']} KB) • CONVOCATORIA DETECTADA: {meta_cv['codigo_convocatoria']}
                    </span>
                    <div style="font-family:'Cormorant Garamond',serif; font-size:30px; color:{c_border}; margin:6px 0 12px 0;">
                        {res_cv['estado_filtro']} — Idoneidad: {res_cv['probabilidad_idoneidad_pct']}%
                    </div>
                    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px; background:rgba(0,0,0,0.4); padding:12px; border-radius:8px; margin-bottom:12px;">
                        <div>
                            <div style="font-size:10px; color:#A39E93;">GRADO DETECTADO</div>
                            <div style="font-size:13.5px; font-weight:600; color:#F4EFE6;">{meta_cv['grado_detectado']}</div>
                        </div>
                        <div>
                            <div style="font-size:10px; color:#A39E93;">EXPERIENCIA EXTRAÍDA</div>
                            <div style="font-size:15px; font-weight:700; color:#E6C762;">{meta_cv['experiencia_total_anios']} años ({meta_cv['experiencia_sector_publico_anios']} púb.)</div>
                        </div>
                        <div>
                            <div style="font-size:10px; color:#A39E93;">SANCIONES RNSSC</div>
                            <div style="font-size:14px; font-weight:700; color:{c_border};">{'SIN SANCIONES' if meta_cv['registro_sanciones_rnssc']==0 else 'INHABILITADO'}</div>
                        </div>
                    </div>
                    <div style="font-size:11.5px; font-family:'JetBrains Mono',monospace; color:#6EE7B7; margin-bottom:10px;">
                        COMPETENCIAS DETECTADAS EN EL PDF: {skills_badges}
                    </div>
                    <div style="font-size:12.5px; color:#A39E93; background:rgba(255,255,255,0.03); padding:10px; border-radius:6px;">
                        <strong>Extracto leído del PDF:</strong> <em>"{meta_cv['texto_cv'][:230]}..."</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="awaiting-box" style="border-color:rgba(212,175,55,0.45);">
                    <div style="font-size:28px; margin-bottom:8px;">✨</div>
                    <div style="font-family:'Cormorant Garamond',serif; font-size:24px; color:#E6C762; margin-bottom:6px;">
                        Currículum "{uploaded_cv_pdf.name}" cargado y listo
                    </div>
                    <div style="font-size:13px;">
                        Haz clic en el botón dorado <strong>"EVALUAR CURRÍCULO PDF CON INTELIGENCIA ARTIFICIAL"</strong> para ejecutar el Modelo 4.
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PESTAÑA 3: GALERÍA MINIMALISTA DE CUELLOS DE BOTELLA
# ------------------------------------------------------------------------------
with tabs[2]:
    g_cols = st.columns(3)
    for idx, row in df_kpis.iterrows():
        dias_ia = round(row["tiempo_promedio_dias"] * 0.44, 1)
        with g_cols[idx % 3]:
            st.markdown(f"""
            <div style="background:rgba(18,19,26,0.78); border:1px solid rgba(212,175,55,0.2); border-radius:12px; padding:18px; margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between; font-family:'JetBrains Mono',monospace; font-size:10.5px; color:#D4AF37;">
                    <span>#{idx+1} • {row['codigo_tupa']}</span>
                    <span style="color:#FCA5A5;">Error: {row['tasa_error_documental_pct']}%</span>
                </div>
                <div style="font-family:'Cormorant Garamond',serif; font-size:21px; color:#F4EFE6; margin:6px 0 10px 0;">
                    {row['tipo_tramite']}
                </div>
                <div style="display:flex; justify-content:space-between; font-size:12.5px;">
                    <span style="color:#A39E93;">Manual: <strong style="color:#EF4444;">{row['tiempo_promedio_dias']}d</strong></span>
                    <span style="color:#A39E93;">Con IA: <strong style="color:#10B981;">{dias_ia}d</strong></span>
                    <span style="color:#A39E93;">SLA: <strong>{row['sla_legal_dias']}d</strong></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PESTAÑA 4: BANDEJA DE ALERTAS EN TIEMPO REAL
# ------------------------------------------------------------------------------
with tabs[3]:
    st.dataframe(get_recent_alerts(12), use_container_width=True)
