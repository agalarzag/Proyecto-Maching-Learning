"""
SIAGD-YAU: API RESTful de Interoperabilidad Municipal + Motor Real de Archivos PDF (FastAPI)
Incluye endpoints para subir y analizar archivos PDF reales (Trámites TUPA y Currículos CAS).
"""

import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.data_pipeline import hash_pii
from src.ml_engine import predict_single_tramite, evaluate_candidate_cv
from src.alerts_feedback import (
    dispatch_citizen_alert,
    register_feedback,
    get_recent_alerts,
    get_feedback_records
)
from src.pdf_processor import (
    analyze_pdf_as_tramite,
    analyze_pdf_as_cv,
    generate_sample_pdfs
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")
WEB_DIR = os.path.join(BASE_DIR, "web")
os.makedirs(WEB_DIR, exist_ok=True)
generate_sample_pdfs()

app = FastAPI(
    title="SIAGD-YAU 3D Spatial AI Platform - Municipalidad Provincial de Yau",
    description=(
        "Plataforma 3D de Gestión Documental Automatizada, Análisis de Archivos PDF, "
        "Alertas Ciudadanas en Tiempo Real y Selección de Currículos CAS mediante Machine Learning."
    ),
    version="3.5.0"
)


class TramiteInput(BaseModel):
    dni_ciudadano: str = Field(default="45892103")
    codigo_tupa: str = Field(default="TUPA-01")
    canal_ingreso: str = Field(default="Mesa de Partes Virtual")
    grupo_vulnerable: str = Field(default="Adulto Mayor (+65)")
    asunto_texto: str = Field(
        default="Solicitud urgente de licencia de edificación y demolición por riesgo de colapso estructural frente a colegio."
    )
    num_folios: int = Field(default=32, ge=1)
    num_requisitos_exigidos: int = Field(default=8, ge=1)
    requisitos_faltantes: int = Field(default=0, ge=0)
    firma_digital_valida: int = Field(default=1, ge=0, le=1)
    calidad_escaneo_ocr: float = Field(default=0.92, ge=0.0, le=1.0)
    carga_area_actual: int = Field(default=42, ge=1)
    impacto_social: int = Field(default=1, ge=0, le=1)
    sla_legal_dias: int = Field(default=15, ge=1)
    canal_notificacion: str = Field(default="WhatsApp + SMS + Casilla Electrónica")


class CurriculoInput(BaseModel):
    dni_postulante: str = Field(default="71239845")
    codigo_convocatoria: str = Field(default="CAS-YAU-002")
    grado_nivel_num: int = Field(default=4, ge=1, le=5)
    experiencia_total_anios: float = Field(default=4.5, ge=0)
    experiencia_sector_publico_anios: float = Field(default=2.5, ge=0)
    ratio_skills_clave: float = Field(default=0.85, ge=0.0, le=1.0)
    certificacion_siga_siaf_servir: int = Field(default=1, ge=0, le=1)
    colegiatura_habilitada: int = Field(default=1, ge=0, le=1)
    registro_sanciones_rnssc: int = Field(default=0, ge=0, le=1)
    texto_cv: str = Field(
        default="Ingeniero de Sistemas y Científico de Datos titulado y colegiado. Especialista en Python, Machine Learning, SQL, FastAPI, interoperabilidad PIDE."
    )


class FeedbackInput(BaseModel):
    expediente_id: str = Field(default="EXP-YAU-2026-00001")
    origen_actor: str = Field(default="Personal Municipal (Ventanilla Única)")
    prediccion_original: str = Field(default="MEDIA")
    correccion_humana: str = Field(default="ALTA")
    calificacion_csat: int = Field(default=5, ge=1, le=5)
    comentario: str = Field(default="El trámite involucra adulto mayor en zona rural; se elevó prioridad a ALTA.")


@app.get("/")
def serve_immersive_3d_app():
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "SIAGD-YAU API Activa"}


@app.get("/health")
def health_check():
    return {
        "status": "OPERATIVO",
        "entidad": "Municipalidad Provincial de Yau",
        "sistema": "SIAGD-YAU v3.5 Spatial PDF Edition",
        "cumplimiento_legal": [
            "Ley N° 29733 (Protección de Datos)",
            "Ley N° 27806 (Transparencia)",
            "D.L. N° 1412 (Gobierno Digital)"
        ]
    }


@app.get("/api/v1/metricas")
def obtener_metricas_ml():
    metrics_file = os.path.join(GOLD_DIR, "ml_metrics_report.json")
    if os.path.exists(metrics_file):
        with open(metrics_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Métricas aún no generadas"}


@app.get("/api/v1/cuellos-botella")
def obtener_cuellos_botella():
    kpis_file = os.path.join(GOLD_DIR, "kpis_cuellos_botella.csv")
    if os.path.exists(kpis_file):
        import pandas as pd
        df = pd.read_csv(kpis_file)
        return df.to_dict(orient="records")
    return []


@app.post("/api/v1/tramites/evaluar-y-notificar")
def evaluar_y_notificar_tramite(tramite: TramiteInput):
    ciudadano_hash = hash_pii(tramite.dni_ciudadano)
    payload = tramite.model_dump()
    pred = predict_single_tramite(payload)
    expediente_id = f"EXP-YAU-LIVE-{ciudadano_hash[:6].upper()}"

    alerta = dispatch_citizen_alert(
        expediente_id=expediente_id,
        ciudadano_hash_id=ciudadano_hash,
        codigo_tupa=tramite.codigo_tupa,
        nivel_prioridad=pred["nivel_prioridad"],
        tiene_error=pred["tiene_error_documental"],
        dias_estimados=pred["tiempo_estimado_siagd_dias"],
        canal_preferido=tramite.canal_notificacion
    )

    return {
        "expediente_id": expediente_id,
        "ciudadano_hash_ley29733": ciudadano_hash,
        "evaluacion_ml": pred,
        "alerta_tiempo_real": alerta
    }


def _extract_pdf_bytes_from_request(raw_body: bytes) -> bytes:
    """Extrae los bytes exactos del PDF desde un cuerpo raw o multipart/form-data sin depender de python-multipart."""
    start_idx = raw_body.find(b"%PDF-")
    end_idx = raw_body.rfind(b"%%EOF")
    if start_idx != -1 and end_idx != -1:
        return raw_body[start_idx:end_idx + 5]
    return raw_body


@app.post("/api/v1/pdf/analizar-tramite")
async def analizar_pdf_tramite_endpoint(request: Request, filename: str = "expediente.pdf"):
    """Recibe un archivo PDF real (raw o multipart), extrae su contenido y ejecuta los Modelos 1, 2 y 3 + Alerta."""
    raw_body = await request.body()
    pdf_bytes = _extract_pdf_bytes_from_request(raw_body)
    extracted = analyze_pdf_as_tramite(pdf_bytes, filename)
    ciudadano_hash = hash_pii(extracted["dni_ciudadano"])
    pred = predict_single_tramite(extracted)
    expediente_id = f"EXP-PDF-{ciudadano_hash[:6].upper()}"

    alerta = dispatch_citizen_alert(
        expediente_id=expediente_id,
        ciudadano_hash_id=ciudadano_hash,
        codigo_tupa=extracted["codigo_tupa"],
        nivel_prioridad=pred["nivel_prioridad"],
        tiene_error=pred["tiene_error_documental"],
        dias_estimados=pred["tiempo_estimado_siagd_dias"]
    )
    return {
        "expediente_id": expediente_id,
        "ciudadano_hash_ley29733": ciudadano_hash,
        "metadatos_pdf": extracted,
        "evaluacion_ml": pred,
        "alerta_tiempo_real": alerta
    }


@app.post("/api/v1/pdf/analizar-cv")
async def analizar_pdf_cv_endpoint(request: Request, filename: str = "cv_postulante.pdf"):
    """Recibe un Currículum Vitae en PDF real, extrae sus datos y ejecuta el Modelo 4 de Selección CAS."""
    raw_body = await request.body()
    pdf_bytes = _extract_pdf_bytes_from_request(raw_body)
    extracted = analyze_pdf_as_cv(pdf_bytes, filename)
    postulante_hash = hash_pii(extracted["dni_postulante"])
    resultado = evaluate_candidate_cv(extracted)
    return {
        "postulante_hash_ley29733": postulante_hash,
        "metadatos_pdf_cv": extracted,
        "resultado_ml": resultado
    }


@app.post("/api/v1/rrhh/evaluar-curriculo")
def evaluar_curriculo_cas(cv: CurriculoInput):
    postulante_hash = hash_pii(cv.dni_postulante)
    resultado = evaluate_candidate_cv(cv.model_dump())
    return {
        "postulante_hash_ley29733": postulante_hash,
        "codigo_convocatoria": cv.codigo_convocatoria,
        "resultado_ml": resultado
    }


@app.post("/api/v1/feedback/registrar")
def registrar_feedback_sistema(fb: FeedbackInput):
    return register_feedback(
        expediente_id=fb.expediente_id,
        origen_actor=fb.origen_actor,
        prediccion_original=fb.prediccion_original,
        correccion_humana=fb.correccion_humana,
        calificacion_csat=fb.calificacion_csat,
        comentario=fb.comentario
    )
