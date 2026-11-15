from datetime import datetime
from typing import List, Dict, Any, Tuple
from app.core.logging import logger


class TemporalLeakageException(Exception):
    """Raised when data leakage or temporal causality violations are detected."""
    pass


class TemporalLeakageValidator:
    """
    Validates temporal causality and prevents data leakage across feature engineering and modeling.
    """

    @staticmethod
    def assert_record_precedes_cutoff(record_timestamp: datetime, cutoff_date: datetime, record_id: str):
        """
        Ensures a record was recorded/verified strictly on or before the observation cutoff.
        """
        if record_timestamp > cutoff_date:
            raise TemporalLeakageException(
                f"Temporal Leakage Violation: Record {record_id} has timestamp {record_timestamp} "
                f"which occurs after observation cutoff {cutoff_date}."
            )

    @staticmethod
    def validate_feature_vector(feature_vector: Dict[str, Any], prohibited_targets: List[str]):
        """
        Ensures target labels or final outcomes are not included in the feature inputs.
        """
        for prohibited in prohibited_targets:
            if prohibited in feature_vector:
                raise TemporalLeakageException(
                    f"Target Leakage Violation: Prohibited target field '{prohibited}' detected in feature vector."
                )

    @staticmethod
    def validate_temporal_split(
        train_timestamps: List[datetime],
        val_timestamps: List[datetime],
    ) -> bool:
        """
        Ensures all training records strictly precede validation records in temporal evaluation.
        """
        if not train_timestamps or not val_timestamps:
            return True
        max_train = max(train_timestamps)
        min_val = min(val_timestamps)
        if max_train > min_val:
            logger.warning(
                f"Temporal split overlap detected: Max train time ({max_train}) > Min val time ({min_val})."
            )
            return False
        return True

    @staticmethod
    def validate_student_grouped_split(
        train_student_ids: List[str],
        val_student_ids: List[str],
    ) -> bool:
        """
        Ensures student instances do not appear in both train and validation splits when testing generalization.
        """
        overlap = set(train_student_ids).intersection(set(val_student_ids))
        if overlap:
            logger.warning(
                f"Student leakage detected: {len(overlap)} students appear in both train and validation splits."
            )
            return False
        return True


leakage_validator = TemporalLeakageValidator()
