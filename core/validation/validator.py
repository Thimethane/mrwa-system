# ============================================================================
# core/validation/validator.py - Complete Validator
# ============================================================================

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class Validator:
    """Validates execution step outputs"""
    
    def validate_output(
        self,
        step_name: str,
        output: Any,
        expected_type: str = "any"
    ) -> Dict[str, Any]:
        """
        Validate step output against criteria
        
        Returns:
            dict: {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str],
                "score": float (0-1)
            }
        """
        
        errors = []
        warnings = []
        score = 1.0
        
        # Basic null check
        if output is None:
            errors.append("Output is None")
            score = 0.0
        
        # Type validation
        elif expected_type != "any":
            if expected_type == "string" and not isinstance(output, str):
                errors.append(f"Expected string, got {type(output).__name__}")
                score -= 0.3
            elif expected_type == "dict" and not isinstance(output, dict):
                errors.append(f"Expected dict, got {type(output).__name__}")
                score -= 0.3
            elif expected_type == "list" and not isinstance(output, list):
                errors.append(f"Expected list, got {type(output).__name__}")
                score -= 0.3
        
        # Content validation
        if isinstance(output, str):
            if len(output) < 10:
                warnings.append("Output seems too short")
                score -= 0.1
            elif len(output) > 100000:
                warnings.append("Output is very large")
                score -= 0.05
        
        elif isinstance(output, dict):
            if not output:
                errors.append("Output dictionary is empty")
                score -= 0.5
        
        elif isinstance(output, list):
            if not output:
                warnings.append("Output list is empty")
                score -= 0.2
        
        # Quality checks
        if isinstance(output, str):
            if output.count(' ') < 5:
                warnings.append("Output may lack detail")
                score -= 0.1
        
        valid = len(errors) == 0
        score = max(0.0, min(1.0, score))
        
        result = {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "score": score
        }
        
        if not valid:
            logger.warning(f"Validation failed for {step_name}: {errors}")
        
        return result

