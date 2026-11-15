import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import (
    DocumentStatus,
    BloomTaxonomyLevel,
    CompetencyCategory,
    IndustryMappingStatus,
    IndustryImportance,
    ReviewStatus,
)


# --- Program & Subject Schemas ---

class AcademicProgramBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "B.Tech Computer Science & Engineering"})
    code: str = Field(..., json_schema_extra={"example": "BTECH-CSE"})
    degree_type: str = Field(default="Bachelor of Technology", json_schema_extra={"example": "Bachelor of Technology"})
    duration_years: int = Field(default=4, ge=1, le=6)
    is_active: bool = True


class AcademicProgramCreate(AcademicProgramBase):
    institution_id: uuid.UUID


class AcademicProgramResponse(AcademicProgramBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AcademicSubjectBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Operating Systems"})
    code: str = Field(..., json_schema_extra={"example": "CS301"})
    semester: int = Field(..., ge=1, le=12, json_schema_extra={"example": 4})
    academic_year: str = Field(default="2024-2025", json_schema_extra={"example": "2024-2025"})
    regulation_version: str = Field(default="R22", json_schema_extra={"example": "R22"})
    credits: int = Field(default=4, ge=1, le=10)
    total_hours: int = Field(default=45, ge=10, le=200)
    description: Optional[str] = None
    prerequisites: Optional[List[str]] = Field(default_factory=list)


class AcademicSubjectCreate(AcademicSubjectBase):
    institution_id: uuid.UUID
    program_id: uuid.UUID


class AcademicSubjectResponse(AcademicSubjectBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    program_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Topic & Unit Schemas ---

class TopicSchema(BaseModel):
    topic_name: str
    subtopics: List[str] = Field(default_factory=list)
    order_index: int = 1


class SyllabusTopicResponse(TopicSchema):
    id: uuid.UUID
    unit_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearningOutcomeSchema(BaseModel):
    outcome_code: str
    description: str
    bloom_level: BloomTaxonomyLevel = BloomTaxonomyLevel.APPLY


class LearningOutcomeResponse(LearningOutcomeSchema):
    id: uuid.UUID
    subject_id: uuid.UUID
    unit_id: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyllabusUnitSchema(BaseModel):
    unit_number: int
    title: str
    estimated_hours: int = 9
    description: Optional[str] = None
    topics: List[TopicSchema] = Field(default_factory=list)
    learning_outcomes: List[LearningOutcomeSchema] = Field(default_factory=list)


class SyllabusUnitResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    subject_id: uuid.UUID
    unit_number: int
    title: str
    estimated_hours: int
    description: Optional[str] = None
    topics: List[SyllabusTopicResponse] = Field(default_factory=list)
    learning_outcomes: List[LearningOutcomeResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Document Schemas ---

class SyllabusDocumentResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    subject_id: Optional[uuid.UUID] = None
    uploaded_by: Optional[uuid.UUID] = None
    file_name: str
    file_size_bytes: int
    mime_type: str
    storage_path: str
    status: DocumentStatus
    extraction_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyllabusDocumentDetailResponse(SyllabusDocumentResponse):
    raw_text: Optional[str] = None
    units: List[SyllabusUnitResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Competency Schemas ---

class CompetencyBase(BaseModel):
    title: str
    description: str
    category: CompetencyCategory
    bloom_level: BloomTaxonomyLevel
    depth_level: int = Field(default=3, ge=1, le=5)
    syllabus_evidence: Optional[str] = None


class CompetencyCreate(CompetencyBase):
    institution_id: Optional[uuid.UUID] = None


class CompetencyResponse(CompetencyBase):
    id: uuid.UUID
    institution_id: Optional[uuid.UUID] = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubjectCompetencyMappingResponse(BaseModel):
    id: uuid.UUID
    subject_id: uuid.UUID
    unit_id: Optional[uuid.UUID] = None
    topic_id: Optional[uuid.UUID] = None
    outcome_id: Optional[uuid.UUID] = None
    competency: CompetencyResponse
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Industry Alignment & Gap Analysis Schemas ---

class IndustryCompetencyRequirementResponse(BaseModel):
    id: uuid.UUID
    role_id: uuid.UUID
    competency_name: str
    category: CompetencyCategory
    required_depth: int
    importance: IndustryImportance
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IndustryRoleProfileResponse(BaseModel):
    id: uuid.UUID
    role_title: str
    role_family: str
    description: str
    experience_tier: str
    requirements: List[IndustryCompetencyRequirementResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CurriculumGapAnalysisResponse(BaseModel):
    id: uuid.UUID
    subject_id: uuid.UUID
    role_id: uuid.UUID
    role_title: Optional[str] = None
    industry_competency_id: uuid.UUID
    industry_competency_name: Optional[str] = None
    category: Optional[CompetencyCategory] = None
    required_depth: Optional[int] = None
    importance: Optional[IndustryImportance] = None
    academic_competency_id: Optional[uuid.UUID] = None
    academic_competency_name: Optional[str] = None
    status: IndustryMappingStatus
    rationale: str
    evidence: Optional[str] = None
    recommendation: Optional[str] = None
    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GapAnalysisSummaryResponse(BaseModel):
    subject_id: uuid.UUID
    role_id: uuid.UUID
    role_title: str
    total_industry_requirements: int
    direct_match_count: int
    partial_match_count: int
    missing_count: int
    outdated_count: int
    coverage_percentage: float
    gaps: List[CurriculumGapAnalysisResponse]


# --- Review & Audit Schemas ---

class SyllabusReviewRequest(BaseModel):
    action: str = Field(..., json_schema_extra={"example": "APPROVED"})
    comments: Optional[str] = None


class SyllabusReviewHistoryResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    reviewed_by: Optional[uuid.UUID] = None
    reviewer_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: uuid.UUID
    previous_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    comments: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UnitUpdateRequest(BaseModel):
    title: Optional[str] = None
    estimated_hours: Optional[int] = None
    description: Optional[str] = None


class TopicUpdateRequest(BaseModel):
    topic_name: Optional[str] = None
    subtopics: Optional[List[str]] = None


# --- AI Structured Output Contracts ---

class AISyllabusStructuringOutput(BaseModel):
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    credits: Optional[int] = None
    total_hours: Optional[int] = None
    prerequisites: List[str] = Field(default_factory=list)
    units: List[SyllabusUnitSchema] = Field(default_factory=list)
    course_learning_outcomes: List[LearningOutcomeSchema] = Field(default_factory=list)
    competencies: List[CompetencyBase] = Field(default_factory=list)
