"""
SIAGD-YAU: Sistema Inteligente Automatizado de Gestión Documental y Selección de Currículos
Municipalidad Provincial de Yau - Pipeline de Ingeniería de Datos (Arquitectura Medallion)
Cumplimiento con Ley N° 29733 (Ley de Protección de Datos Personales) y Ley N° 27806 (Transparencia).
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
BRONZE_DIR = os.path.join(DATA_DIR, "bronze")
SILVER_DIR = os.path.join(DATA_DIR, "silver")
GOLD_DIR = os.path.join(DATA_DIR, "gold")
DB_PATH = os.path.join(DATA_DIR, "siagd_yau.db")

for d in [BRONZE_DIR, SILVER_DIR, GOLD_DIR]:
    os.makedirs(d, exist_ok=True)


def hash_pii(value: str, salt: str = "MUNIYAU_2026_LPDP29733") -> str:
    """Seudonimización criptográfica SHA-256 conforme a la Ley N° 29733."""
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()[:16]


def generate_tramites_bronze(n_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Genera datos históricos crudos (Capa Bronze) simulando el TUPA de la Municipalidad Provincial de Yau.
    Refleja los cuellos de botella reales identificados en las Preguntas Guía.
    """
    rng = np.random.default_rng(seed)

    catalogo_tramites = [
        {
            "codigo_tupa": "TUPA-01",
            "tipo_tramite": "Licencia de Edificación y Habilitación Urbana",
            "area_destino": "Gerencia de Desarrollo Urbano y Rural",
            "sla_dias": 15,
            "media_dias_manual": 28.5,
            "complejidad_base": 4.6,
            "prob_error_base": 0.34,
            "peso_frecuencia": 0.18,
            "plantillas_asunto": [
                "Solicito licencia de construcción para vivienda multifamiliar de 4 pisos en zona urbana, adjunto planos estructurales y memoria descriptiva.",
                "Expediente técnico para habilitación urbana de lote rústico en sector periférico de Yau con revisión de parámetros urbanísticos.",
                "Regularización de ampliación de edificación comercial sin licencia previa, adjunto certificado de estabilidad estructural.",
                "Solicitud urgente de demolición parcial por riesgo de colapso estructural en pared colindante a vía pública y colegio."
            ]
        },
        {
            "codigo_tupa": "TUPA-02",
            "tipo_tramite": "Licencia de Funcionamiento e Inspección ITSE",
            "area_destino": "Subgerencia de Desarrollo Económico y Defensa Civil",
            "sla_dias": 7,
            "media_dias_manual": 16.2,
            "complejidad_base": 3.8,
            "prob_error_base": 0.29,
            "peso_frecuencia": 0.20,
            "plantillas_asunto": [
                "Solicitud de licencia de funcionamiento para restaurante y cevichería con inspección ITSE de riesgo medio.",
                "Certificado ITSE de seguridad en edificaciones para local comercial de venta de abarrotes y almacén mayorista.",
                "Renovación urgente de certificado de defensa civil ITSE para centro médico y farmacia con atención al público.",
                "Apertura de taller mecánico automotriz y soldadura, adjunto plano de señalización, extintores y rutas de evacuación."
            ]
        },
        {
            "codigo_tupa": "TUPA-03",
            "tipo_tramite": "Saneamiento Físico-Legal y Visación de Planos",
            "area_destino": "Subgerencia de Catastro y Acondicionamiento Territorial",
            "sla_dias": 12,
            "media_dias_manual": 24.8,
            "complejidad_base": 4.4,
            "prob_error_base": 0.36,
            "peso_frecuencia": 0.14,
            "plantillas_asunto": [
                "Visación de planos y memoria descriptiva para prescripción adquisitiva de dominio y saneamiento catastral.",
                "Subdivisión de lote urbano e independización de predio matriz ubicado en el centro histórico de Yau.",
                "Certificado de posesión y actualización de linderos catastrales con coordenadas UTM WGS84 para titulación.",
                "Rectificación de área y medidas perimétricas por superposición gráfica en registro catastral municipal."
            ]
        },
        {
            "codigo_tupa": "TUPA-04",
            "tipo_tramite": "Reclamación Tributaria y Fraccionamiento Coactivo",
            "area_destino": "Gerencia de Administración Tributaria (SAT Yau)",
            "sla_dias": 10,
            "media_dias_manual": 18.0,
            "complejidad_base": 3.5,
            "prob_error_base": 0.25,
            "peso_frecuencia": 0.16,
            "plantillas_asunto": [
                "Recurso de reclamación contra resolución de determinación de impuesto predial y arbitrios municipales 2024-2026.",
                "Solicitud urgente de suspensión de cobranza coactiva y embargo por prescripción de deuda tributaria municipal.",
                "Deducción de 50 UIT de la base imponible del Impuesto Predial para pensionista y adulto mayor vulnerable.",
                "Solicitud de fraccionamiento tributario en 24 cuotas para regularización de arbitrios de limpieza pública y serenazgo."
            ]
        },
        {
            "codigo_tupa": "TUPA-05",
            "tipo_tramite": "Acceso a la Información Pública y Transparencia",
            "area_destino": "Secretaría General y Unidad de Transparencia",
            "sla_dias": 7,
            "media_dias_manual": 9.8,
            "complejidad_base": 2.4,
            "prob_error_base": 0.14,
            "peso_frecuencia": 0.10,
            "plantillas_asunto": [
                "Solicitud al amparo de la Ley N° 27806 de copias fedateadas de órdenes de servicio y contratos de obras públicas.",
                "Requerimiento urgente de información presupuestal y expediente de contratación de mantenimiento vial en Yau.",
                "Acceso a actas de sesión de concejo municipal y resoluciones de alcaldía emitidas en el último trimestre."
            ]
        },
        {
            "codigo_tupa": "TUPA-06",
            "tipo_tramite": "Denuncia Ambiental, Ruido y Salud Pública",
            "area_destino": "Gerencia de Servicios Públicos y Gestión Ambiental",
            "sla_dias": 3,
            "media_dias_manual": 7.5,
            "complejidad_base": 3.2,
            "prob_error_base": 0.18,
            "peso_frecuencia": 0.10,
            "plantillas_asunto": [
                "Denuncia urgente por arrojo clandestino de residuos sólidos peligrosos y colapso de desagüe frente a mercado municipal.",
                "Emergencia sanitaria por contaminación de canal de regadío y proliferación de focos infecciosos cerca de posta médica.",
                "Queja vecinal por contaminación sonora excesiva de local nocturno sin aislamiento acústico en zona residencial."
            ]
        },
        {
            "codigo_tupa": "TUPA-07",
            "tipo_tramite": "Registro Civil y Actas Certificadas",
            "area_destino": "Oficina de Registro del Estado Civil",
            "sla_dias": 2,
            "media_dias_manual": 3.8,
            "complejidad_base": 1.6,
            "prob_error_base": 0.12,
            "peso_frecuencia": 0.12,
            "plantillas_asunto": [
                "Expedición de copia certificada de acta de nacimiento y matrimonio para trámite de pensión y seguro de salud.",
                "Rectificación administrativa de error material en partida de defunción y apellido materno.",
                "Solicitud de constancia de soltería y programación de matrimonio civil comunitario."
            ]
        }
    ]

    pesos = [t["peso_frecuencia"] for t in catalogo_tramites]
    indices = rng.choice(len(catalogo_tramites), size=n_samples, p=pesos)

    canales = ["Ventanilla Presencial", "Mesa de Partes Virtual", "Módulo Descentralizado"]
    pesos_canales = [0.64, 0.26, 0.10]

    grupos_vulnerables = ["Ninguno", "Adulto Mayor (+65)", "Persona con Discapacidad (CONADIS)", "Madre Gestante / Lactante"]
    pesos_vulnerables = [0.72, 0.16, 0.07, 0.05]

    zonas = ["Yau Centro Urbano", "Sector Norte Industrial", "Valle Agrícola Sur", "Anexo Alto Andino", "Barrio Periférico Este"]

    base_date = datetime(2025, 1, 1, 8, 0, 0)
    registros = []

    for i, idx in enumerate(indices):
        meta = catalogo_tramites[idx]
        canal = rng.choice(canales, p=pesos_canales)
        grupo_vuln = rng.choice(grupos_vulnerables, p=pesos_vulnerables)
        zona = rng.choice(zonas)

        # Simular fecha y hora de ingreso
        dias_offset = int(rng.integers(0, 420))
        hora_offset = int(rng.integers(8, 17))
        minuto_offset = int(rng.integers(0, 60))
        fecha_ingreso = base_date + timedelta(days=dias_offset, hours=hora_offset - 8, minutes=minuto_offset)

        # Folios y documentos adjuntos
        num_folios = int(max(1, rng.normal(loc=meta["complejidad_base"] * 8, scale=6)))
        num_requisitos_exigidos = int(max(2, round(meta["complejidad_base"] * 2)))

        # En ventanilla manual ocurren más omisiones documentales que en digital con validación previa
        factor_canal_error = 1.20 if canal == "Ventanilla Presencial" else 0.75
        prob_error_doc = min(0.88, max(0.03, meta["prob_error_base"] * factor_canal_error + rng.normal(0, 0.06)))
        requisitos_faltantes = int(rng.binomial(2, prob_error_doc * 0.55))
        firma_digital_valida = int(rng.random() > (0.28 if canal == "Ventanilla Presencial" else 0.06))
        calidad_escaneo_ocr = float(np.clip(rng.normal(0.84 if canal != "Ventanilla Presencial" else 0.72, 0.12), 0.35, 0.99))

        # Selección de asunto + posible indicador de urgencia
        asunto_base = rng.choice(meta["plantillas_asunto"])
        impacto_social = int(
            ("urgente" in asunto_base.lower())
            or ("emergencia" in asunto_base.lower())
            or ("riesgo" in asunto_base.lower())
            or (grupo_vuln != "Ninguno")
        )
        carga_area_actual = int(np.clip(rng.normal(loc=48 if meta["complejidad_base"] > 3.5 else 25, scale=14), 5, 110))
        reincidencia_subsanacion = int(rng.binomial(2, prob_error_doc * 0.45))

        # Determinación de si el expediente tiene error/observación (Target 2: Detección de Errores)
        score_error_latente = (
            1.65 * (requisitos_faltantes > 0)
            + 1.15 * (1 - firma_digital_valida)
            + 1.25 * (calidad_escaneo_ocr < 0.68)
            + 0.70 * (reincidencia_subsanacion > 0)
            + 0.35 * (num_folios > 45)
            + rng.normal(0, 0.35)
        )
        tiene_error_documental = int(score_error_latente >= 1.35)

        # Tiempo real de resolución en días (Target 3: Regresión de SLA y Cuellos de Botella)
        tiempo_resolucion_dias = max(
            1.0,
            meta["media_dias_manual"]
            * (0.82 + 0.006 * carga_area_actual)
            * (1.35 if tiene_error_documental else 0.92)
            + rng.normal(0, 2.2)
        )
        excede_sla = int(tiempo_resolucion_dias > meta["sla_dias"])

        # Nivel de Prioridad / Criticidad (Target 1: Clasificación Multiclase)
        # 0: Baja, 1: Media, 2: Alta, 3: Crítica
        riesgo_sla_ratio = tiempo_resolucion_dias / max(1, meta["sla_dias"])
        score_criticidad = (
            2.1 * impacto_social
            + 1.6 * (grupo_vuln != "Ninguno")
            + 1.3 * (meta["codigo_tupa"] in ["TUPA-06", "TUPA-01", "TUPA-02"])
            + 1.2 * min(2.5, riesgo_sla_ratio)
            + 0.015 * carga_area_actual
            + rng.normal(0, 0.25)
        )

        if score_criticidad >= 4.9:
            prioridad_label = "CRITICA"
            prioridad_id = 3
        elif score_criticidad >= 3.4:
            prioridad_label = "ALTA"
            prioridad_id = 2
        elif score_criticidad >= 2.1:
            prioridad_label = "MEDIA"
            prioridad_id = 1
        else:
            prioridad_label = "BAJA"
            prioridad_id = 0

        dni_raw = f"{rng.integers(10000000, 89999999)}"
        csat_ciudadano = int(np.clip(
            round(5.0 - 1.3 * excede_sla - 1.1 * tiene_error_documental - 0.04 * tiempo_resolucion_dias + rng.normal(0, 0.45)),
            1, 5
        ))

        registros.append({
            "expediente_id": f"EXP-YAU-2026-{i+1:05d}",
            "fecha_ingreso": fecha_ingreso.strftime("%Y-%m-%d %H:%M:%S"),
            "dni_ciudadano_raw": dni_raw,
            "codigo_tupa": meta["codigo_tupa"],
            "tipo_tramite": meta["tipo_tramite"],
            "area_destino": meta["area_destino"],
            "canal_ingreso": canal,
            "zona_procedencia": zona,
            "grupo_vulnerable": grupo_vuln,
            "asunto_texto": asunto_base,
            "num_folios": num_folios,
            "num_requisitos_exigidos": num_requisitos_exigidos,
            "requisitos_faltantes": requisitos_faltantes,
            "firma_digital_valida": firma_digital_valida,
            "calidad_escaneo_ocr": round(calidad_escaneo_ocr, 4),
            "carga_area_actual": carga_area_actual,
            "reincidencia_subsanacion": reincidencia_subsanacion,
            "impacto_social": impacto_social,
            "sla_legal_dias": meta["sla_dias"],
            "tiempo_resolucion_dias": round(tiempo_resolucion_dias, 2),
            "excede_sla": excede_sla,
            "tiene_error_documental": tiene_error_documental,
            "nivel_prioridad": prioridad_label,
            "prioridad_id": prioridad_id,
            "satisfaccion_csat": csat_ciudadano
        })

    return pd.DataFrame(registros)


def generate_curriculos_bronze(n_candidates: int = 800, seed: int = 101) -> pd.DataFrame:
    """
    Genera datos históricos de postulantes y currículos para convocatorias CAS / Servicio Civil
    de la Municipalidad Provincial de Yau (Tema 1 del PDF: Selección de Currículos mediante ML).
    """
    rng = np.random.default_rng(seed)

    puestos_municipales = [
        {
            "codigo_convocatoria": "CAS-YAU-001",
            "puesto": "Especialista en Ingeniería Civil y Licencias de Edificación",
            "area": "Gerencia de Desarrollo Urbano y Rural",
            "exp_min_anios": 4,
            "exp_publica_min": 2,
            "skills_clave": [
                "autocad", "civil 3d", "reglamento nacional de edificaciones", "habilitaciones urbanas",
                "expedientes tecnicos", "catastro", "supervision de obras", "invierte.pe", "s10", "bim"
            ],
            "grado_min": "Titulado Colegiado"
        },
        {
            "codigo_convocatoria": "CAS-YAU-002",
            "puesto": "Analista de Sistemas, Ciencia de Datos y Gobierno Digital",
            "area": "Oficina de Tecnologías de la Información y Gobierno Digital",
            "exp_min_anios": 3,
            "exp_publica_min": 1,
            "skills_clave": [
                "python", "machine learning", "sql", "fastapi", "transformacion digital",
                "interoperabilidad pide", "seguridad de la informacion", "iso 27001", "nlp", "docker"
            ],
            "grado_min": "Bachiller / Titulado"
        },
        {
            "codigo_convocatoria": "CAS-YAU-003",
            "puesto": "Inspector Técnico de Seguridad en Edificaciones (ITSE) y Defensa Civil",
            "area": "Subgerencia de Desarrollo Económico y Defensa Civil",
            "exp_min_anios": 3,
            "exp_publica_min": 2,
            "skills_clave": [
                "inspeccion itse", "gestion de riesgos de desastres", "cenepred", "indeci",
                "seguridad electrica", "plan de contingencia", "defensa civil", "normas NFPA", "aforo"
            ],
            "grado_min": "Titulado Colegiado"
        },
        {
            "codigo_convocatoria": "CAS-YAU-004",
            "puesto": "Especialista en Gestión Pública, Trámite Documentario y Archivo",
            "area": "Secretaría General y Unidad de Transparencia",
            "exp_min_anios": 2,
            "exp_publica_min": 2,
            "skills_clave": [
                "sistema de gestion documental", "tupa", "ley 27444", "procedimiento administrativo general",
                "transparencia publica", "archivo central", "atencion al ciudadano", "firma digital", "siga", "siaf"
            ],
            "grado_min": "Bachiller / Titulado"
        },
        {
            "codigo_convocatoria": "CAS-YAU-005",
            "puesto": "Especialista Legal en Tributación Municipal y Ejecución Coactiva",
            "area": "Gerencia de Administración Tributaria (SAT Yau)",
            "exp_min_anios": 4,
            "exp_publica_min": 2,
            "skills_clave": [
                "derecho tributario municipal", "codigo tributario", "cobranza coactiva", "impuesto predial",
                "arbitrios municipales", "procedimiento contencioso", "resoluciones de determinacion", "sunat"
            ],
            "grado_min": "Titulado Colegiado"
        }
    ]

    grados = ["Técnico", "Egresado", "Bachiller", "Titulado Colegiado", "Maestría en Gestión Pública"]
    grado_puntos = {
        "Técnico": 1,
        "Egresado": 2,
        "Bachiller": 3,
        "Titulado Colegiado": 4,
        "Maestría en Gestión Pública": 5
    }

    distractores_skills = [
        "liderazgo", "trabajo en equipo", "ofimatica basica", "redaccion de informes",
        "atencion telefonica", "logistica comercial", "ventas minoristas", "contabilidad privada"
    ]

    registros_cv = []
    for i in range(n_candidates):
        puesto_meta = puestos_municipales[i % len(puestos_municipales)]
        grado = rng.choice(grados, p=[0.10, 0.12, 0.28, 0.36, 0.14])
        exp_total = round(float(max(0.5, rng.normal(loc=puesto_meta["exp_min_anios"] + 0.8, scale=2.1))), 1)
        exp_publica = round(float(min(exp_total, max(0.0, rng.normal(loc=puesto_meta["exp_publica_min"] + 0.3, scale=1.5)))), 1)

        # Seleccionar qué porcentaje de skills clave domina el candidato
        n_clave = int(rng.integers(1, len(puesto_meta["skills_clave"]) + 1))
        skills_candidato = list(rng.choice(puesto_meta["skills_clave"], size=n_clave, replace=False))
        skills_extra = list(rng.choice(distractores_skills, size=int(rng.integers(1, 4)), replace=False))
        todas_skills = skills_candidato + skills_extra

        cert_servir_siga_siaf = int(rng.random() < (0.68 if exp_publica >= 1.5 else 0.25))
        colegiatura_habilitada = int(grado in ["Titulado Colegiado", "Maestría en Gestión Pública"] and rng.random() < 0.88)
        sanciones_redam_rnssc = int(rng.random() < 0.04)  # Registro Nacional de Sanciones contra Servidores Civiles

        ratio_skills = n_clave / len(puesto_meta["skills_clave"])
        cumple_exp = int(exp_total >= puesto_meta["exp_min_anios"] and exp_publica >= puesto_meta["exp_publica_min"])
        cumple_grado = int(grado_puntos[grado] >= (4 if "Colegiado" in puesto_meta["grado_min"] else 3))

        # Puntaje técnico objetivo (0 a 100)
        puntaje_idoneidad = np.clip(
            38.0 * ratio_skills
            + 22.0 * min(1.3, exp_total / max(1, puesto_meta["exp_min_anios"]))
            + 18.0 * min(1.3, (exp_publica + 0.2) / max(1, puesto_meta["exp_publica_min"]))
            + 12.0 * (grado_puntos[grado] / 5.0)
            + 6.0 * cert_servir_siga_siaf
            + 4.0 * colegiatura_habilitada
            - 50.0 * sanciones_redam_rnssc
            + rng.normal(0, 2.5),
            5.0, 100.0
        )

        apto_convocatoria = int(
            puntaje_idoneidad >= 72.0
            and cumple_exp == 1
            and cumple_grado == 1
            and sanciones_redam_rnssc == 0
        )

        resumen_cv = (
            f"Profesional con grado de {grado}, {exp_total} años de experiencia general y {exp_publica} años en el sector público municipal. "
            f"Especialista en {', '.join(todas_skills)}. "
            f"{'Cuenta con certificaciones SIAF/SIGA y Gestión Pública SERVIR.' if cert_servir_siga_siaf else ''} "
            f"{'Colegiatura profesional activa y habilitada.' if colegiatura_habilitada else ''}"
        )

        dni_postulante = f"{rng.integers(10000000, 89999999)}"

        registros_cv.append({
            "postulante_id": f"CV-YAU-2026-{i+1:04d}",
            "dni_raw": dni_postulante,
            "codigo_convocatoria": puesto_meta["codigo_convocatoria"],
            "puesto_postulado": puesto_meta["puesto"],
            "area_solicitante": puesto_meta["area"],
            "grado_academico": grado,
            "grado_nivel_num": grado_puntos[grado],
            "experiencia_total_anios": exp_total,
            "experiencia_sector_publico_anios": exp_publica,
            "num_skills_clave_match": n_clave,
            "ratio_skills_clave": round(ratio_skills, 4),
            "certificacion_siga_siaf_servir": cert_servir_siga_siaf,
            "colegiatura_habilitada": colegiatura_habilitada,
            "registro_sanciones_rnssc": sanciones_redam_rnssc,
            "cumple_requisitos_minimos": int(cumple_exp and cumple_grado and not sanciones_redam_rnssc),
            "texto_cv": resumen_cv.strip(),
            "puntaje_idoneidad": round(float(puntaje_idoneidad), 2),
            "apto_preseleccion": apto_convocatoria
        })

    return pd.DataFrame(registros_cv)


def run_medallion_pipeline() -> dict:
    """Ejecuta el pipeline completo Bronze -> Silver (Anonimizado Ley 29733) -> Gold + SQLite Warehouse."""
    print("[1/3] Generando Capa BRONZE (Ingesta de datos históricos municipales y CVs CAS)...")
    df_tramites_bronze = generate_tramites_bronze(n_samples=5000, seed=42)
    df_cv_bronze = generate_curriculos_bronze(n_candidates=800, seed=101)

    bronze_tramites_path = os.path.join(BRONZE_DIR, "tramites_historicos_raw.csv")
    bronze_cv_path = os.path.join(BRONZE_DIR, "postulantes_cas_raw.csv")
    df_tramites_bronze.to_csv(bronze_tramites_path, index=False, encoding="utf-8")
    df_cv_bronze.to_csv(bronze_cv_path, index=False, encoding="utf-8")

    print("[2/3] Procesando Capa SILVER (Seudonimización SHA-256 Ley N° 29733, Limpieza y Feature Engineering)...")
    df_tramites_silver = df_tramites_bronze.copy()
    df_tramites_silver["ciudadano_hash_id"] = df_tramites_silver["dni_ciudadano_raw"].apply(hash_pii)
    df_tramites_silver.drop(columns=["dni_ciudadano_raw"], inplace=True)

    # Feature engineering temporal y operativo
    dt_col = pd.to_datetime(df_tramites_silver["fecha_ingreso"])
    df_tramites_silver["mes_ingreso"] = dt_col.dt.month
    df_tramites_silver["dia_semana"] = dt_col.dt.dayofweek
    df_tramites_silver["hora_ingreso"] = dt_col.dt.hour
    df_tramites_silver["ratio_requisitos_faltantes"] = (
        df_tramites_silver["requisitos_faltantes"] / df_tramites_silver["num_requisitos_exigidos"]
    ).round(4)
    df_tramites_silver["densidad_folios_por_requisito"] = (
        df_tramites_silver["num_folios"] / df_tramites_silver["num_requisitos_exigidos"]
    ).round(4)

    df_cv_silver = df_cv_bronze.copy()
    df_cv_silver["postulante_hash_id"] = df_cv_silver["dni_raw"].apply(hash_pii)
    df_cv_silver.drop(columns=["dni_raw"], inplace=True)

    silver_tramites_parquet = os.path.join(SILVER_DIR, "tramites_silver.parquet")
    silver_cv_parquet = os.path.join(SILVER_DIR, "curriculos_silver.parquet")
    df_tramites_silver.to_parquet(silver_tramites_parquet, index=False)
    df_cv_silver.to_parquet(silver_cv_parquet, index=False)

    print("[3/3] Construyendo Capa GOLD (Analítica de Cuellos de Botella, Features ML y SQLite Data Warehouse)...")
    resumen_cuellos = (
        df_tramites_silver.groupby(["codigo_tupa", "tipo_tramite", "area_destino"])
        .agg(
            total_expedientes=("expediente_id", "count"),
            sla_legal_dias=("sla_legal_dias", "first"),
            tiempo_promedio_dias=("tiempo_resolucion_dias", "mean"),
            tasa_incumplimiento_sla=("excede_sla", "mean"),
            tasa_error_documental=("tiene_error_documental", "mean"),
            csat_promedio=("satisfaccion_csat", "mean"),
            expedientes_criticos=("prioridad_id", lambda s: int((s == 3).sum()))
        )
        .reset_index()
        .sort_values(by="tiempo_promedio_dias", ascending=False)
    )
    resumen_cuellos["tiempo_promedio_dias"] = resumen_cuellos["tiempo_promedio_dias"].round(2)
    resumen_cuellos["tasa_incumplimiento_sla_pct"] = (resumen_cuellos["tasa_incumplimiento_sla"] * 100).round(1)
    resumen_cuellos["tasa_error_documental_pct"] = (resumen_cuellos["tasa_error_documental"] * 100).round(1)
    resumen_cuellos["csat_promedio"] = resumen_cuellos["csat_promedio"].round(2)

    gold_cuellos_path = os.path.join(GOLD_DIR, "kpis_cuellos_botella.csv")
    resumen_cuellos.to_csv(gold_cuellos_path, index=False, encoding="utf-8")

    # Persistir en SQLite para consultas transaccionales de la API, Alertas y Feedback Loop
    conn = sqlite3.connect(DB_PATH)
    df_tramites_silver.to_sql("tramites", conn, if_exists="replace", index=False)
    df_cv_silver.to_sql("postulantes_cv", conn, if_exists="replace", index=False)
    resumen_cuellos.to_sql("kpis_cuellos_botella", conn, if_exists="replace", index=False)

    # Crear tablas de Alertas en Tiempo Real y Feedback Loop (Active Learning)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas_ciudadanas (
            alerta_id TEXT PRIMARY KEY,
            expediente_id TEXT,
            ciudadano_hash_id TEXT,
            canal_notificacion TEXT,
            estado_tramite TEXT,
            nivel_prioridad TEXT,
            mensaje TEXT,
            latencia_ms INTEGER,
            fecha_envio TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback_loop (
            feedback_id TEXT PRIMARY KEY,
            expediente_id TEXT,
            origen_actor TEXT,
            prediccion_original TEXT,
            correccion_humana TEXT,
            calificacion_csat INTEGER,
            comentario TEXT,
            fecha_registro TEXT
        )
    """)

    # Poblar alertas iniciales y registros de feedback de ejemplo
    sample_alerts = []
    for idx, row in df_tramites_silver.head(25).iterrows():
        estado = "OBSERVADO - SUBSANACIÓN REQUERIDA" if row["tiene_error_documental"] else "EN EVALUACIÓN PRIORIZADA"
        msg = (
            f"[MUNI-YAU] Exp. {row['expediente_id']} ({row['codigo_tupa']}): Estado actual '{estado}'. "
            f"Prioridad ML asignada: {row['nivel_prioridad']}. Tiempo estimado: {max(1.0, round(row['tiempo_resolucion_dias']*0.45, 1))} días."
        )
        sample_alerts.append((
            f"ALT-2026-{idx+1:04d}",
            row["expediente_id"],
            row["ciudadano_hash_id"],
            "WhatsApp / SMS / Casilla Electrónica",
            estado,
            row["nivel_prioridad"],
            msg,
            int(120 + (idx * 7) % 180),
            row["fecha_ingreso"]
        ))
    cursor.executemany("""
        INSERT OR REPLACE INTO alertas_ciudadanas
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_alerts)

    conn.commit()
    conn.close()

    stats = {
        "total_tramites": len(df_tramites_silver),
        "total_curriculos": len(df_cv_silver),
        "db_path": DB_PATH,
        "cuellos_botella_top": resumen_cuellos.to_dict(orient="records")
    }
    with open(os.path.join(GOLD_DIR, "etl_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"Pipeline Medallion completado exitosamente. Base de datos creada en: {DB_PATH}")
    return stats


if __name__ == "__main__":
    run_medallion_pipeline()
