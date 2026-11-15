"""
Centralized AI Service Abstraction for MASTERY.
Ensures:
1. No OpenAI calls at application initialization.
2. Safe failure when OPENAI_API_KEY is not configured.
3. Structured JSON generation with Pydantic validation.
4. Clean separation from domain business logic.
"""
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()
T = TypeVar("T", bound=BaseModel)


class AIService:
    """
    Central AI orchestration gateway.
    All modules (Syllabus extraction, Question generation, Recommendation generation)
    interact with LLMs through this service.
    """

    def __init__(self):
        self.model_name = settings.OPENAI_MODEL
        self._api_key = settings.OPENAI_API_KEY

    @property
    def is_available(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        """
        Executes a prompt against the configured LLM and enforces Pydantic response modeling.
        Raises RuntimeError if OpenAI is unconfigured, or ValidationError if response is invalid.
        """
        if not self.is_available:
            raise RuntimeError(
                "AI Service is unavailable: OPENAI_API_KEY is not configured in environment."
            )

        logger.info(
            "Invoking AI structured generation for schema: %s using model %s",
            response_model.__name__,
            self.model_name,
        )

        # In Phase 02+ this calls OpenAI client with response_format=response_model
        raise NotImplementedError("AI Service implementation will be wired in Phase 02/03.")


# Singleton service provider
ai_service = AIService()
