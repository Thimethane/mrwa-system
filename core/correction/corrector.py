# ============================================================================
# core/correction/corrector.py - Complete Corrector
# ============================================================================

import asyncio
from typing import Dict, Any, Optional
import logging

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from core.config import settings

logger = logging.getLogger(__name__)


class Corrector:
    """Self-correction engine for failed executions"""
    
    def __init__(self):
        self.gemini_available = GEMINI_AVAILABLE and settings.GEMINI_API_KEY
        
        if self.gemini_available:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info("Corrector: Gemini integration enabled")
        else:
            self.model = None
            logger.info("Corrector: Running in demo mode")
    
    async def analyze_failure(
        self,
        step_name: str,
        error: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze execution failure and generate correction strategy
        
        Returns:
            dict: {
                "root_cause": str,
                "strategy": str,
                "action": str,
                "confidence": float,
                "adjusted_parameters": dict
            }
        """
        
        logger.info(f"Analyzing failure for: {step_name}")
        
        if self.model:
            try:
                return await self._analyze_with_gemini(step_name, error, context)
            except Exception as e:
                logger.error(f"Gemini analysis failed: {e}")
                return self._get_default_correction(error)
        else:
            return self._get_default_correction(error)
    
    async def _analyze_with_gemini(
        self,
        step_name: str,
        error: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze failure using Gemini AI"""
        
        prompt = f"""
        You are an expert at analyzing execution failures and generating corrections.
        
        Failed Step: {step_name}
        Error: {error}
        Context: {context}
        
        Provide:
        1. Root cause analysis (1-2 sentences)
        2. Specific correction strategy (actionable approach)
        3. Concrete correction action (what to change)
        4. Confidence level (0-1)
        
        Format your response as:
        ROOT CAUSE: [analysis]
        STRATEGY: [strategy]
        ACTION: [action]
        CONFIDENCE: [0-1]
        """
        
        response = await asyncio.to_thread(
            self.model.generate_content,
            prompt
        )
        
        # Parse response
        text = response.text.strip()
        lines = text.split('\n')
        
        result = {
            "root_cause": "Unknown",
            "strategy": "Retry with adjustments",
            "action": "Reformatting and retrying",
            "confidence": 0.7,
            "adjusted_parameters": {}
        }
        
        for line in lines:
            if line.startswith("ROOT CAUSE:"):
                result["root_cause"] = line.split(":", 1)[1].strip()
            elif line.startswith("STRATEGY:"):
                result["strategy"] = line.split(":", 1)[1].strip()
            elif line.startswith("ACTION:"):
                result["action"] = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    conf = float(line.split(":", 1)[1].strip())
                    result["confidence"] = max(0.0, min(1.0, conf))
                except:
                    pass
        
        logger.info(f"Gemini correction analysis: {result['strategy']}")
        return result
    
    def _get_default_correction(self, error: str) -> Dict[str, Any]:
        """Fallback correction for demo mode"""
        
        # Simple error pattern matching
        if "format" in error.lower():
            strategy = "Adjust output format and retry"
            action = "Relaxing format constraints and reformatting output"
        elif "incomplete" in error.lower():
            strategy = "Increase processing depth"
            action = "Processing with more detail and thoroughness"
        elif "timeout" in error.lower():
            strategy = "Optimize for speed"
            action = "Reducing scope and optimizing execution path"
        else:
            strategy = "Retry with adjusted parameters"
            action = "Reformatting output structure and relaxing constraints"
        
        return {
            "root_cause": "Likely validation criteria mismatch or data quality issue",
            "strategy": strategy,
            "action": action,
            "confidence": 0.75,
            "adjusted_parameters": {
                "tolerance": "increased",
                "retry_delay_ms": 500
            }
        }
    
    async def apply_correction(
        self,
        step,
        correction: Dict[str, Any]
    ) -> bool:
        """Apply correction to execution step"""
        
        logger.info(f"Applying correction: {correction['action']}")
        
        # Simulate correction application
        await asyncio.sleep(0.5)
        
        # Update step parameters based on correction
        if "adjusted_parameters" in correction:
            logger.debug(f"Adjusted parameters: {correction['adjusted_parameters']}")
        
        return True

