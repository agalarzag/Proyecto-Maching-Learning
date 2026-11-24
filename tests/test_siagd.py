"""
Suite de Pruebas Automatizadas End-to-End para SIAGD-YAU v3.5 (Municipalidad Provincial de Yau).
Incluye verificación real de subida y análisis de archivos PDF (/api/v1/pdf/analizar-tramite y /api/v1/pdf/analizar-cv).
"""

import os
import json
from fastapi.testclient import TestClient

from src.data_pipeline import hash_pii, DB_PATH, GOLD_DIR
from src.pdf_processor import generate_sample_pdfs, TRAMITES_PDF_DIR, CVS_PDF_DIR
from src.api import app

client = TestClient(app)


def run_all_tests():
    print("Ejecutando verificaciones Full-Stack (Datos, ML, API y Subida Real de los 6 PDFs Oficiales)...")

    # 1. Prueba de Anonimización Ley N° 29733
    h1 = hash_pii("45678912")
    assert len(h1) == 16 and "45678912" not in h1
    print(" [OK] Prueba 1: Seudonimización SHA-256 conforme a Ley N° 29733.")

    # 2. Prueba de Modelos ML
    metrics_path = os.path.join(GOLD_DIR, "ml_metrics_report.json")
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    assert metrics["modelo_1_priorizacion"]["roc_auc_ovr"] >= 0.94
    assert metrics["modelo_2_deteccion_errores"]["f1_score"] >= 0.85
    assert metrics["modelo_3_regresion_sla"]["r2_score"] >= 0.90
    assert metrics["modelo_4_seleccion_curriculos"]["roc_auc"] >= 0.95
    print(" [OK] Prueba 2: Los 4 modelos de Machine Learning superan el umbral de calidad.")

    # 3. Prueba de los 3 PDFs de Trámites Municipales
    generate_sample_pdfs()
    for fname in sorted(os.listdir(TRAMITES_PDF_DIR)):
        fpath = os.path.join(TRAMITES_PDF_DIR, fname)
        with open(fpath, "rb") as f:
            r_pdf_t = client.post(
                "/api/v1/pdf/analizar-tramite",
                files={"archivo": (fname, f, "application/pdf")}
            )
        assert r_pdf_t.status_code == 200
        bt = r_pdf_t.json()
        print(
            f" [OK] Trámite PDF ({fname}) -> TUPA: {bt['metadatos_pdf']['codigo_tupa']} | "
            f"Prioridad: {bt['evaluacion_ml']['nivel_prioridad']} | "
            f"Error Documental: {bt['evaluacion_ml']['tiene_error_documental']} ({bt['evaluacion_ml']['riesgo_error_documental_pct']}%)"
        )

    # 4. Prueba de los 3 PDFs de Currículos CAS
    for fname in sorted(os.listdir(CVS_PDF_DIR)):
        fpath = os.path.join(CVS_PDF_DIR, fname)
        with open(fpath, "rb") as f:
            r_pdf_cv = client.post(
                "/api/v1/pdf/analizar-cv",
                files={"archivo": (fname, f, "application/pdf")}
            )
        assert r_pdf_cv.status_code == 200
        bcv = r_pdf_cv.json()
        print(
            f" [OK] Currículo PDF ({fname}) -> {bcv['metadatos_pdf_cv']['codigo_convocatoria']} | "
            f"Estado: {bcv['resultado_ml']['estado_filtro']} (Idoneidad: {bcv['resultado_ml']['probabilidad_idoneidad_pct']}%)"
        )

    print("\nTODAS LAS PRUEBAS FULL-STACK Y DE ARCHIVOS PDF PASARON EXITOSAMENTE.")


if __name__ == "__main__":
    run_all_tests()
