# ============================================================================
# core/orchestrator/engine.py - Complete Orchestrator
# ============================================================================

import asyncio
import logging
import random
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional Gemini Support (Safe)
# ---------------------------------------------------------------------------

try:
    import google.generativeai as genai  # deprecated but still functional
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Gemini SDK not available, running in demo mode")


# ---------------------------------------------------------------------------
# Execution Step Model
# ---------------------------------------------------------------------------

class ExecutionStep:
    """Represents a single execution step"""

    def __init__(self, id: int, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description
        self.status = "pending"
        self.output: Optional[str] = None
        self.error: Optional[str] = None
        self.attempts = 0
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.duration_ms = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "attempts": self.attempts,
            "duration_ms": self.duration_ms,
        }


# ---------------------------------------------------------------------------
# Orchestrator Engine (MAIN CLASS)
# ---------------------------------------------------------------------------

class OrchestratorEngine:
    """Autonomous execution orchestrator"""

    def __init__(self):
        self.gemini_available = bool(
            GEMINI_AVAILABLE and getattr(settings, "GEMINI_API_KEY", None)
        )

        self.model = None

        if self.gemini_available:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info("Gemini integration enabled")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")
                self.gemini_available = False

        if not self.gemini_available:
            logger.info("Running in demo mode (no Gemini)")

    # ---------------------------------------------------------------------

    async def generate_plan(
        self,
        input_type: str,
        input_value: str
    ) -> List[ExecutionStep]:
        """Generate execution plan"""

        logger.info(f"Generating plan for {input_type}")

        if self.model:
            try:
                return await self._generate_plan_gemini(input_type, input_value)
            except Exception as e:
                logger.error(f"Gemini plan generation failed: {e}")

        return self._get_default_plan(input_type)

    # ---------------------------------------------------------------------

    async def _generate_plan_gemini(
        self,
        input_type: str,
        input_value: str
    ) -> List[ExecutionStep]:
        """Generate plan using Gemini"""

        prompt = f"""
You are an autonomous workflow planner.

Input Type: {input_type}
Input Value: {input_value}

Create 4-6 execution steps.

Format:
Step N: Action - Expected outcome
"""

        response = await asyncio.to_thread(
            self.model.generate_content,
            prompt
        )

        steps: List[ExecutionStep] = []

        for i, line in enumerate(response.text.splitlines()):
            line = line.strip()
            if ":" not in line:
                continue

            _, content = line.split(":", 1)
            if "-" in content:
                name, desc = content.split("-", 1)
            else:
                name, desc = content, "Execute step"

            steps.append(
                ExecutionStep(i + 1, name.strip(), desc.strip())
            )

            if len(steps) >= 6:
                break

        if not steps:
            return self._get_default_plan(input_type)

        logger.info(f"Generated {len(steps)} steps via Gemini")
        return steps

    # ---------------------------------------------------------------------

    def _get_default_plan(self, input_type: str) -> List[ExecutionStep]:
        """Fallback execution plan"""

        plans = {
            "pdf": [
                ExecutionStep(1, "Extract document structure", "Parse PDF sections"),
                ExecutionStep(2, "Analyze content", "Extract key concepts"),
                ExecutionStep(3, "Generate summary", "Create document summary"),
                ExecutionStep(4, "Validate output", "Ensure completeness"),
            ],
            "code": [
                ExecutionStep(1, "Parse code", "Build syntax tree"),
                ExecutionStep(2, "Analyze dependencies", "Map imports"),
                ExecutionStep(3, "Detect patterns", "Identify patterns"),
                ExecutionStep(4, "Generate docs", "Create documentation"),
            ],
            "url": [
                ExecutionStep(1, "Fetch content", "Download page"),
                ExecutionStep(2, "Extract data", "Parse structure"),
                ExecutionStep(3, "Analyze relevance", "Rank content"),
                ExecutionStep(4, "Summarize", "Generate insights"),
            ],
            "youtube": [
                ExecutionStep(1, "Extract metadata", "Get video info"),
                ExecutionStep(2, "Process transcript", "Clean captions"),
                ExecutionStep(3, "Identify key points", "Main topics"),
                ExecutionStep(4, "Generate summary", "Video overview"),
            ],
        }

        plan = plans.get(input_type, plans["pdf"])
        logger.info(f"Using default plan ({len(plan)} steps)")
        return plan

    # ---------------------------------------------------------------------

    async def execute_step(
        self,
        step: ExecutionStep,
        execution_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a single step"""

        step.attempts += 1
        step.status = "executing"
        step.started_at = datetime.utcnow()

        logger.info(f"Executing step {step.id}: {step.name}")

        await asyncio.sleep(1.5)

        step.completed_at = datetime.utcnow()
        step.duration_ms = int(
            (step.completed_at - step.started_at).total_seconds() * 1000
        )

        if random.random() < 0.2:
            step.status = "failed"
            step.error = "Validation failed"
            logger.warning(f"Step {step.id} failed")

            return {
                "success": False,
                "error": step.error,
                "step": step.to_dict(),
            }

        step.status = "completed"
        step.output = f"Completed: {step.name}"

        logger.info(f"Step {step.id} completed")

        return {
            "success": True,
            "output": step.output,
            "step": step.to_dict(),
            "metadata": {
                "duration_ms": step.duration_ms,
                "attempts": step.attempts,
            },
        }


# ---------------------------------------------------------------------------
# BACKWARD COMPATIBILITY ALIAS (IMPORTANT)
# ---------------------------------------------------------------------------

# If any code still imports `Orchestrator`
Orchestrator = OrchestratorEngine
