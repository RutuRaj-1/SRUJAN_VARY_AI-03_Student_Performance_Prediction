from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()

# Core diagnostic and health probes
api_router.include_router(health.router)

# Domain router hooks (Phase 02 - Phase 11 will register endpoints here)
# - Module 01: Academic Data Intelligence Hub (/academic)
# - Module 02: AI Syllabus & Competency Intelligence (/syllabus)
# - Module 03: Continuous Learning & Assessment Engine (/assessments)
# - Module 04: Evidence Calibration & Student Mastery Analytics (/mastery)
# - Module 05: Explainable Academic Risk Prediction (/risk)
# - Module 06: Personalized Intervention & Student Growth (/interventions)
# - Module 07: Industry & Placement Readiness Intelligence (/career)
