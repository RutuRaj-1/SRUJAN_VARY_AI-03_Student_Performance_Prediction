from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    users,
    institutions,
    syllabus,
    academic_data,
    assessments,
    mastery,
    risk,
)

api_router = APIRouter()

# Core diagnostic and health probes
api_router.include_router(health.router)

# Authentication & Identity (Phase 02)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(institutions.router)

# Module 02: AI Syllabus & Competency Intelligence Engine (Phase 03)
api_router.include_router(syllabus.router, prefix="/syllabus", tags=["Module 02: Syllabus & Competencies"])

# Module 01/03: Academic Data Intelligence Hub (Phase 04)
api_router.include_router(academic_data.router, prefix="/academic-data", tags=["Module 03: Academic Data Intelligence"])
api_router.include_router(academic_data.router, prefix="/academic", tags=["Module 03: Academic Data Intelligence (Alias)"])

# Module 04: Intelligent Assessment & Attentiveness Engine (Phase 05)
api_router.include_router(assessments.router, prefix="/assessments", tags=["Module 04: Assessment & Attentiveness Engine"])

# Module 05: Learning Mastery & Performance Analytics (Phase 06)
api_router.include_router(mastery.router, prefix="/mastery", tags=["Module 05: Learning Mastery & Performance Analytics"])

# Module 06: Academic Risk Prediction (Phase 07)
api_router.include_router(risk.router, prefix="/risk", tags=["Module 06: Academic Risk Prediction"])

# Domain router hooks (Phase 03 - Phase 08 will register endpoints here)
# - Module 01: Academic Data Intelligence Hub (/academic)
# - Module 02: AI Syllabus & Competency Intelligence (/syllabus)
# - Module 03: Continuous Learning & Assessment Engine (/assessments)
# - Module 04: Evidence Calibration & Student Mastery Analytics (/mastery)
# - Module 05: Explainable Academic Risk Prediction (/risk)
# - Module 06: Personalized Intervention & Student Growth (/interventions)
# - Module 07: Industry & Placement Readiness Intelligence (/career)
