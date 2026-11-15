import re
from typing import List, Optional
from app.core.config import get_settings
from app.core.logging import logger
from app.models.enums import BloomTaxonomyLevel
from app.schemas.syllabus import (
    AISyllabusStructuringOutput,
    SyllabusUnitSchema,
    TopicSchema,
    LearningOutcomeSchema,
    CompetencyBase,
    CompetencyCategory,
)

settings = get_settings()

BLOOM_VERB_MAP = {
    BloomTaxonomyLevel.REMEMBER: [
        "define", "list", "recall", "state", "identify", "name", "recognize", "reproduce"
    ],
    BloomTaxonomyLevel.UNDERSTAND: [
        "explain", "describe", "discuss", "summarize", "interpret", "classify", "contrast", "illustrate"
    ],
    BloomTaxonomyLevel.APPLY: [
        "apply", "implement", "execute", "solve", "construct", "demonstrate", "use", "program", "code"
    ],
    BloomTaxonomyLevel.ANALYZE: [
        "analyze", "differentiate", "compare", "examine", "distinguish", "investigate", "deconstruct"
    ],
    BloomTaxonomyLevel.EVALUATE: [
        "evaluate", "assess", "judge", "critique", "verify", "measure", "validate", "rate"
    ],
    BloomTaxonomyLevel.CREATE: [
        "design", "architect", "formulate", "develop", "synthesize", "invent", "compose", "optimize"
    ],
}


def classify_bloom_verb(text: str) -> BloomTaxonomyLevel:
    lower_text = text.lower()
    first_words = lower_text.split()[:4]
    
    # Priority check: CREATE, EVALUATE, ANALYZE, APPLY, UNDERSTAND, REMEMBER
    for level in [
        BloomTaxonomyLevel.CREATE,
        BloomTaxonomyLevel.EVALUATE,
        BloomTaxonomyLevel.ANALYZE,
        BloomTaxonomyLevel.APPLY,
        BloomTaxonomyLevel.UNDERSTAND,
        BloomTaxonomyLevel.REMEMBER,
    ]:
        for verb in BLOOM_VERB_MAP[level]:
            for word in first_words:
                if word.startswith(verb):
                    return level
            if f" {verb} " in f" {lower_text} ":
                return level
    return BloomTaxonomyLevel.UNDERSTAND


class AIStructuringService:
    """
    Transforms raw unformatted syllabus text into structured units, topics, and learning outcomes.
    Uses AI LLM when configured, or reliable deterministic curriculum parsing with NLP rules.
    """

    async def structure_syllabus(self, raw_text: str, subject_name: str = "") -> AISyllabusStructuringOutput:
        if settings.is_ai_configured:
            try:
                from app.services.ai.service import ai_service
                prompt = (
                    f"Analyze and structure the following university syllabus for subject '{subject_name}'.\n"
                    f"Extract units/modules (unit_number, title, estimated_hours, description), "
                    f"topics and subtopics for each unit, and Course Learning Outcomes (outcome_code, description, bloom_level).\n\n"
                    f"Syllabus Text:\n{raw_text[:8000]}"
                )
                return await ai_service.generate_structured(
                    prompt=prompt,
                    response_model=AISyllabusStructuringOutput,
                    system_prompt="You are an expert academic curriculum engineer and accreditation specialist.",
                )
            except Exception as e:
                logger.warning("AI structuring failed or unconfigured, falling back to deterministic parser: %s", e)

        return self._deterministic_parse(raw_text, subject_name)

    def _deterministic_parse(self, raw_text: str, subject_name: str) -> AISyllabusStructuringOutput:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        
        units: List[SyllabusUnitSchema] = []
        current_unit: Optional[SyllabusUnitSchema] = None
        current_topics: List[TopicSchema] = []
        course_outcomes: List[LearningOutcomeSchema] = []

        unit_pattern = re.compile(
            r"^(?:UNIT|MODULE|CHAPTER)\s*[-:]?\s*([0-9IVXLCDM]+)[\s:.\-]*(.*)",
            re.IGNORECASE,
        )
        hours_pattern = re.compile(r"\(?\b(\d+)\s*(?:hours|hrs|hr|periods)\b\)?", re.IGNORECASE)
        co_pattern = re.compile(r"^(?:CO|CLO|LO)\s*([0-9]+)[\s:.\-]*(.*)", re.IGNORECASE)

        unit_counter = 0

        for line in lines:
            # Check for Course Learning Outcomes
            co_match = co_pattern.match(line)
            if co_match:
                co_num = co_match.group(1)
                co_desc = co_match.group(2).strip() or line
                bloom = classify_bloom_verb(co_desc)
                course_outcomes.append(
                    LearningOutcomeSchema(
                        outcome_code=f"CO{co_num}",
                        description=co_desc,
                        bloom_level=bloom,
                    )
                )
                continue

            # Check for Unit/Module headers
            unit_match = unit_pattern.match(line)
            if unit_match:
                unit_counter += 1
                unit_title = unit_match.group(2).strip() or f"Unit {unit_counter}"
                
                # Extract hours if specified in line
                hours_match = hours_pattern.search(line)
                est_hours = int(hours_match.group(1)) if hours_match else 9

                if current_unit:
                    current_unit.topics = current_topics
                    units.append(current_unit)
                    current_topics = []

                current_unit = SyllabusUnitSchema(
                    unit_number=unit_counter,
                    title=unit_title,
                    estimated_hours=est_hours,
                    description=f"Curriculum study covering {unit_title}",
                    topics=[],
                    learning_outcomes=[],
                )
                continue

            # Process content within a unit
            if current_unit:
                # Split comma or semicolon separated topic items
                parts = [p.strip() for p in re.split(r"[;•\n\t]", line) if len(p.strip()) > 3]
                for part in parts:
                    if ":" in part:
                        main_topic, sub_part = part.split(":", 1)
                        subs = [s.strip() for s in sub_part.split(",") if s.strip()]
                        current_topics.append(
                            TopicSchema(
                                topic_name=main_topic.strip(),
                                subtopics=subs,
                                order_index=len(current_topics) + 1,
                            )
                        )
                    else:
                        current_topics.append(
                            TopicSchema(
                                topic_name=part.strip(),
                                subtopics=[],
                                order_index=len(current_topics) + 1,
                            )
                        )

        # Flush final unit
        if current_unit:
            current_unit.topics = current_topics
            units.append(current_unit)

        # If document had no explicit "UNIT" headers, synthesize standard modular structure
        if not units:
            units = self._synthesize_fallback_units(raw_text, subject_name)

        # Ensure default learning outcomes if none parsed
        if not course_outcomes:
            course_outcomes = [
                LearningOutcomeSchema(
                    outcome_code=f"CO{i+1}",
                    description=f"Understand and apply core theoretical foundations and practical principles of {u.title}",
                    bloom_level=BloomTaxonomyLevel.APPLY,
                )
                for i, u in enumerate(units[:5])
            ]

        return AISyllabusStructuringOutput(
            subject_name=subject_name,
            units=units,
            course_learning_outcomes=course_outcomes,
            competencies=[],
        )

    def _synthesize_fallback_units(self, raw_text: str, subject_name: str) -> List[SyllabusUnitSchema]:
        paragraphs = [p.strip() for p in raw_text.split("\n\n") if len(p.strip()) > 20]
        if not paragraphs:
            paragraphs = [raw_text[:200]] if raw_text else ["Foundational Principles"]

        units = []
        for i, para in enumerate(paragraphs[:5]):
            first_line = para.splitlines()[0][:80]
            topics = [
                TopicSchema(
                    topic_name=line.strip()[:100],
                    subtopics=[],
                    order_index=idx + 1,
                )
                for idx, line in enumerate(para.splitlines()[:5])
                if len(line.strip()) > 4
            ]
            units.append(
                SyllabusUnitSchema(
                    unit_number=i + 1,
                    title=f"Module {i+1}: {first_line}",
                    estimated_hours=9,
                    description=para[:250],
                    topics=topics or [TopicSchema(topic_name=first_line, subtopics=[], order_index=1)],
                    learning_outcomes=[],
                )
            )
        return units


ai_structuring_service = AIStructuringService()
