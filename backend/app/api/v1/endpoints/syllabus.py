import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.core.security import get_current_active_user, CurrentUser, require_roles
from app.models.enums import UserRole, DocumentStatus
from app.models.syllabus import (
    AcademicProgram,
    AcademicSubject,
    SyllabusDocument,
    SyllabusUnit,
    SyllabusTopic,
    LearningOutcome,
    Competency,
    SubjectCompetencyMapping,
    IndustryRoleProfile,
    IndustryCompetencyRequirement,
)
from app.schemas.syllabus import (
    AcademicProgramCreate,
    AcademicProgramResponse,
    AcademicSubjectCreate,
    AcademicSubjectResponse,
    SyllabusDocumentResponse,
    SyllabusDocumentDetailResponse,
    SyllabusUnitResponse,
    CompetencyResponse,
    SubjectCompetencyMappingResponse,
    IndustryRoleProfileResponse,
    CurriculumGapAnalysisResponse,
    GapAnalysisSummaryResponse,
    SyllabusReviewRequest,
    SyllabusReviewHistoryResponse,
    UnitUpdateRequest,
    TopicUpdateRequest,
)
from app.services.syllabus.document_service import document_service
from app.services.syllabus.ai_structuring_service import ai_structuring_service
from app.services.syllabus.competency_service import competency_service
from app.services.syllabus.industry_mapping_service import industry_mapping_service
from app.services.syllabus.gap_analysis_service import gap_analysis_service
from app.services.syllabus.review_service import review_service

router = APIRouter()


# --- Programs & Subjects Endpoints ---

@router.post("/programs", response_model=AcademicProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    program_in: AcademicProgramCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    if current_user.role != UserRole.SUPER_ADMIN and str(program_in.institution_id) != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create program for another institution.")

    program = AcademicProgram(
        id=uuid.uuid4(),
        institution_id=program_in.institution_id,
        name=program_in.name,
        code=program_in.code,
        degree_type=program_in.degree_type,
        duration_years=program_in.duration_years,
        is_active=program_in.is_active,
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@router.get("/programs", response_model=List[AcademicProgramResponse])
def list_programs(
    institution_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    target_inst_id = institution_id
    if current_user.role != UserRole.SUPER_ADMIN:
        if not current_user.institution_id:
            return []
        target_inst_id = uuid.UUID(current_user.institution_id)

    stmt = select(AcademicProgram)
    if target_inst_id:
        stmt = stmt.where(AcademicProgram.institution_id == target_inst_id)
    return db.execute(stmt).scalars().all()


@router.post("/subjects", response_model=AcademicSubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_in: AcademicSubjectCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    if current_user.role != UserRole.SUPER_ADMIN and str(subject_in.institution_id) != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create subject for another institution.")

    subject = AcademicSubject(
        id=uuid.uuid4(),
        institution_id=subject_in.institution_id,
        program_id=subject_in.program_id,
        name=subject_in.name,
        code=subject_in.code,
        semester=subject_in.semester,
        academic_year=subject_in.academic_year,
        regulation_version=subject_in.regulation_version,
        credits=subject_in.credits,
        total_hours=subject_in.total_hours,
        description=subject_in.description,
        prerequisites=subject_in.prerequisites or [],
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.get("/subjects", response_model=List[AcademicSubjectResponse])
def list_subjects(
    institution_id: Optional[uuid.UUID] = None,
    program_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    target_inst_id = institution_id
    if current_user.role != UserRole.SUPER_ADMIN:
        if not current_user.institution_id:
            return []
        target_inst_id = uuid.UUID(current_user.institution_id)

    stmt = select(AcademicSubject)
    if target_inst_id:
        stmt = stmt.where(AcademicSubject.institution_id == target_inst_id)
    if program_id:
        stmt = stmt.where(AcademicSubject.program_id == program_id)
    return db.execute(stmt).scalars().all()


@router.get("/subjects/{subject_id}", response_model=AcademicSubjectResponse)
def get_subject_detail(
    subject_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    subject = db.get(AcademicSubject, subject_id)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")
    return subject


# --- Document Upload & Processing Endpoints ---

@router.post("/upload", response_model=SyllabusDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_syllabus_document(
    file: UploadFile = File(...),
    subject_id: Optional[uuid.UUID] = Form(None),
    institution_id: Optional[uuid.UUID] = Form(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    # Verify institution access
    target_inst = institution_id
    if current_user.role != UserRole.SUPER_ADMIN:
        if not current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not assigned to an institution.")
        target_inst = uuid.UUID(current_user.institution_id)
    elif not target_inst:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="institution_id is required for Super Admin uploads.")

    # Save physical file to private storage
    storage_path, file_size = await document_service.save_file(file, target_inst)

    # Persist document record
    doc = SyllabusDocument(
        id=uuid.uuid4(),
        institution_id=target_inst,
        subject_id=subject_id,
        uploaded_by=uuid.UUID(current_user.user_id) if current_user.user_id else None,
        file_name=file.filename or "unknown_syllabus",
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/octet-stream",
        storage_path=storage_path,
        status=DocumentStatus.UPLOADED.value,
        extraction_metadata={"file_size": file_size, "filename": file.filename},
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.post("/documents/{document_id}/process", response_model=SyllabusDocumentDetailResponse)
async def process_syllabus_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    doc = db.get(SyllabusDocument, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    if current_user.role != UserRole.SUPER_ADMIN and str(doc.institution_id) != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot process document for another institution.")

    doc.status = DocumentStatus.PROCESSING.value
    db.commit()

    try:
        # Step 1: Text extraction
        raw_text, meta = document_service.extract_text(doc.storage_path)
        doc.raw_text = raw_text
        doc.extraction_metadata = meta

        # Find or create subject if needed
        subject = db.get(AcademicSubject, doc.subject_id) if doc.subject_id else None
        subject_name = subject.name if subject else doc.file_name

        # Step 2: AI Structuring
        structured = await ai_structuring_service.structure_syllabus(raw_text, subject_name)

        # Clear existing units for this document
        db.query(SyllabusUnit).filter(SyllabusUnit.document_id == doc.id).delete()

        # Step 3: Persist Units, Topics, Outcomes
        for unit_schema in structured.units:
            unit = SyllabusUnit(
                id=uuid.uuid4(),
                document_id=doc.id,
                subject_id=doc.subject_id or uuid.uuid4(),
                unit_number=unit_schema.unit_number,
                title=unit_schema.title,
                estimated_hours=unit_schema.estimated_hours,
                description=unit_schema.description,
            )
            db.add(unit)
            db.flush()

            for top_schema in unit_schema.topics:
                topic = SyllabusTopic(
                    id=uuid.uuid4(),
                    unit_id=unit.id,
                    topic_name=top_schema.topic_name,
                    subtopics=top_schema.subtopics,
                    order_index=top_schema.order_index,
                )
                db.add(topic)

        # Persist Course Learning Outcomes if subject exists
        if subject:
            db.query(LearningOutcome).filter(LearningOutcome.subject_id == subject.id).delete()
            for co_schema in structured.course_learning_outcomes:
                co = LearningOutcome(
                    id=uuid.uuid4(),
                    subject_id=subject.id,
                    outcome_code=co_schema.outcome_code,
                    description=co_schema.description,
                    bloom_level=co_schema.bloom_level.value,
                )
                db.add(co)

            # Step 4: Extract and persist competencies
            competencies = competency_service.extract_competencies_from_structure(
                db=db,
                subject=subject,
                structured_data=structured,
                institution_id=doc.institution_id,
            )

            # Step 5: Industry Alignment & Gap Analysis
            industry_mapping_service.map_subject_to_roles(
                db=db,
                subject=subject,
                competencies=competencies,
            )

        doc.status = DocumentStatus.REVIEW_REQUIRED.value
        db.commit()
        db.refresh(doc)
        return doc
    except Exception as exc:
        db.rollback()
        doc.status = DocumentStatus.FAILED.value
        doc.extraction_metadata = {"error": str(exc)}
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Syllabus extraction and structuring failed: {str(exc)}",
        )


@router.get("/documents", response_model=List[SyllabusDocumentResponse])
def list_documents(
    subject_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    stmt = select(SyllabusDocument)
    if current_user.role != UserRole.SUPER_ADMIN:
        if not current_user.institution_id:
            return []
        stmt = stmt.where(SyllabusDocument.institution_id == uuid.UUID(current_user.institution_id))
    if subject_id:
        stmt = stmt.where(SyllabusDocument.subject_id == subject_id)
    return db.execute(stmt.order_by(SyllabusDocument.created_at.desc())).scalars().all()


@router.get("/documents/{document_id}", response_model=SyllabusDocumentDetailResponse)
def get_document_detail(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    doc = db.get(SyllabusDocument, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    if current_user.role != UserRole.SUPER_ADMIN and str(doc.institution_id) != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to other institution document denied.")
    return doc


# --- Syllabus Structure & Competencies Exploration ---

@router.get("/subjects/{subject_id}/structure", response_model=List[SyllabusUnitResponse])
def get_subject_structure(
    subject_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    stmt = (
        select(SyllabusUnit)
        .where(SyllabusUnit.subject_id == subject_id)
        .order_by(SyllabusUnit.unit_number.asc())
    )
    return db.execute(stmt).scalars().all()


@router.get("/subjects/{subject_id}/competencies", response_model=List[CompetencyResponse])
def get_subject_competencies(
    subject_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    subject = db.get(AcademicSubject, subject_id)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")

    stmt = (
        select(Competency)
        .where(
            (Competency.institution_id == subject.institution_id) | (Competency.institution_id == None)
        )
        .order_by(Competency.created_at.asc())
    )
    return db.execute(stmt).scalars().all()


# --- Industry Alignment & Gap Analysis ---

@router.get("/industry-roles", response_model=List[IndustryRoleProfileResponse])
def list_industry_roles(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    stmt = select(IndustryRoleProfile).order_by(IndustryRoleProfile.role_family, IndustryRoleProfile.role_title)
    return db.execute(stmt).scalars().all()


@router.get("/subjects/{subject_id}/gap-analysis", response_model=List[GapAnalysisSummaryResponse])
def get_subject_gap_analysis(
    subject_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    subject = db.get(AcademicSubject, subject_id)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")

    return gap_analysis_service.get_gap_summaries_for_subject(db, subject_id)


# --- Faculty Review & Modification Workspace ---

@router.post("/documents/{document_id}/review", response_model=SyllabusDocumentResponse)
def review_syllabus_document(
    document_id: uuid.UUID,
    review_in: SyllabusReviewRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    return review_service.review_document(
        db=db,
        document_id=document_id,
        reviewer_id=uuid.UUID(current_user.user_id),
        action=review_in.action,
        comments=review_in.comments,
    )


@router.get("/documents/{document_id}/history", response_model=List[SyllabusReviewHistoryResponse])
def get_document_review_history(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    return review_service.get_review_history(db, document_id)


@router.patch("/units/{unit_id}")
def update_syllabus_unit(
    unit_id: uuid.UUID,
    update_data: UnitUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    return review_service.update_unit(
        db=db,
        unit_id=unit_id,
        reviewer_id=uuid.UUID(current_user.user_id),
        update_data=update_data,
        comments="Faculty manual unit update",
    )


@router.patch("/topics/{topic_id}")
def update_syllabus_topic(
    topic_id: uuid.UUID,
    update_data: TopicUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    return review_service.update_topic(
        db=db,
        topic_id=topic_id,
        reviewer_id=uuid.UUID(current_user.user_id),
        update_data=update_data,
        comments="Faculty manual topic update",
    )
