import re
import uuid
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.enums import CompetencyCategory, BloomTaxonomyLevel
from app.models.syllabus import (
    AcademicSubject,
    SyllabusUnit,
    SyllabusTopic,
    LearningOutcome,
    Competency,
    SubjectCompetencyMapping,
)
from app.schemas.syllabus import AISyllabusStructuringOutput

PROGRAMMING_KEYWORDS = {
    "python", "java", "c++", "c programming", "rust", "golang", "javascript", "typescript",
    "sql", "syntax", "oop", "recursion", "pointer", "polymorphism", "inheritance", "function",
    "class", "code", "coding", "algorithm", "implementation", "scripting",
}

TOOLS_KEYWORDS = {
    "git", "docker", "kubernetes", "linux", "bash", "postman", "react", "fastapi", "django",
    "spring", "postgresql", "mysql", "mongodb", "redis", "kafka", "aws", "gcp", "azure",
    "ci/cd", "jenkins", "graphql", "rest", "ide", "vscode", "pytorch", "tensorflow",
}

ANALYTICAL_KEYWORDS = {
    "complexity", "big o", "time complexity", "space complexity", "optimization",
    "trade-off", "tradeoff", "analysis", "scheduling", "deadlock", "performance",
    "evaluation", "metrics", "benchmark", "fault tolerance", "concurrency",
}

PRACTICAL_KEYWORDS = {
    "lab", "experiment", "project", "hands-on", "build", "debug", "debugging",
    "configuration", "simulation", "profiling", "deployment", "integration",
}


def classify_competency_category(title: str, text: str) -> Tuple[CompetencyCategory, int]:
    combined = f"{title} {text}".lower()
    
    # Check Tools & Technologies
    for tool in TOOLS_KEYWORDS:
        if tool in combined:
            return CompetencyCategory.TOOLS_TECHNOLOGIES, 3

    # Check Programming
    for prog in PROGRAMMING_KEYWORDS:
        if prog in combined:
            return CompetencyCategory.PROGRAMMING, 4

    # Check Analytical
    for ana in ANALYTICAL_KEYWORDS:
        if ana in combined:
            return CompetencyCategory.ANALYTICAL, 4

    # Check Practical
    for prac in PRACTICAL_KEYWORDS:
        if prac in combined:
            return CompetencyCategory.PRACTICAL, 3

    # Default to Theoretical
    return CompetencyCategory.THEORETICAL, 3


class CompetencyService:
    def extract_competencies_from_structure(
        self,
        db: Session,
        subject: AcademicSubject,
        structured_data: AISyllabusStructuringOutput,
        institution_id: uuid.UUID,
    ) -> List[Competency]:
        created_competencies = []

        # Process each unit and topic
        for unit_schema in structured_data.units:
            # Look up or match unit in DB if persisted
            for topic_schema in unit_schema.topics:
                title = topic_schema.topic_name.strip()
                if not title or len(title) < 3:
                    continue

                category, depth = classify_competency_category(
                    title,
                    " ".join(topic_schema.subtopics) if topic_schema.subtopics else unit_schema.description or "",
                )

                evidence = f"Topic from Unit {unit_schema.unit_number} ({unit_schema.title}): {title}"
                if topic_schema.subtopics:
                    evidence += f" [Subtopics: {', '.join(topic_schema.subtopics[:4])}]"

                bloom_level = BloomTaxonomyLevel.UNDERSTAND
                if category in [CompetencyCategory.PROGRAMMING, CompetencyCategory.PRACTICAL]:
                    bloom_level = BloomTaxonomyLevel.APPLY
                elif category == CompetencyCategory.ANALYTICAL:
                    bloom_level = BloomTaxonomyLevel.ANALYZE

                competency = Competency(
                    id=uuid.uuid4(),
                    institution_id=institution_id,
                    title=f"{subject.name}: {title}",
                    description=f"Demonstrated competency in {title} covering {', '.join(topic_schema.subtopics) if topic_schema.subtopics else 'foundational concepts'}.",
                    category=category.value,
                    bloom_level=bloom_level.value,
                    depth_level=depth,
                    syllabus_evidence=evidence,
                    is_verified=False,
                )
                db.add(competency)
                created_competencies.append(competency)

        db.flush()
        return created_competencies


competency_service = CompetencyService()
