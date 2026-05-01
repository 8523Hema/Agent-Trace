"""
analyzer.py -- Core logic for AI-powered root cause analysis using Gemini Flash.
Uses the new google-genai SDK (google.genai).
"""

import json
import os
import uuid
from datetime import datetime

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import AnalysisCache, Run
from .prompts import build_prompt

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_CATEGORIES = {"wrong_tool", "bad_input", "llm_confusion", "api_error", "logic_error"}
GEMINI_MODEL = "gemini-2.0-flash"


# ---------------------------------------------------------------------------
# Pydantic output model
# ---------------------------------------------------------------------------

class AnalysisResult(BaseModel):
    """Structured result returned to the API caller."""

    run_id: uuid.UUID
    root_cause: str
    fix_suggestion: str
    fix_code_hint: str | None = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    failure_category: str
    analyzed_at: datetime
    gemini_model: str
    cached: bool = False


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def analyze_run(run_id: uuid.UUID, db: AsyncSession) -> AnalysisResult:
    """
    Perform or retrieve an AI root cause analysis for a failed run.

    Steps:
    1. Fetch run + steps from DB (raise LookupError if missing).
    2. If run is not 'failed', raise ValueError.
    3. Return cached result if one exists in analysis_cache.
    4. Build prompt -> call Gemini -> parse / validate JSON.
    5. Persist result to analysis_cache.
    6. Return AnalysisResult.
    """

    # 1. Load run with steps and any existing analysis
    query = (
        select(Run)
        .options(selectinload(Run.steps), selectinload(Run.analysis))
        .where(Run.id == run_id)
    )
    result = await db.execute(query)
    run = result.scalar_one_or_none()

    if run is None:
        raise LookupError(f"Run {run_id} not found")

    # 2. Must be a failed run
    if run.status != "failed":
        raise ValueError(f"Run {run_id} has status '{run.status}', not 'failed'")

    # 3. Return cached analysis if present
    if run.analysis is not None:
        cached = run.analysis
        return AnalysisResult(
            run_id=run.id,
            root_cause=cached.root_cause,
            fix_suggestion=cached.fix_suggestion,
            fix_code_hint=cached.fix_code_hint,
            confidence=cached.confidence,
            failure_category=cached.failure_category,
            analyzed_at=cached.analyzed_at,
            gemini_model=cached.gemini_model,
            cached=True,
        )

    # 4. Build prompt
    steps_sorted = sorted(run.steps, key=lambda s: s.step_index)
    steps_data = [
        {
            "step_type": s.step_type,
            "name": s.name,
            "input": s.input,
            "output": s.output,
            "error": s.error,
            "status": s.status,
        }
        for s in steps_sorted
    ]

    # Determine user_input: prefer run.input["input"] -> run.input (as JSON string)
    raw_input = run.input
    if isinstance(raw_input, dict):
        user_input_str = raw_input.get("input") or json.dumps(raw_input)
    else:
        user_input_str = str(raw_input)

    prompt = build_prompt(
        agent_name=run.agent_name,
        user_input=user_input_str,
        steps=steps_data,
        top_level_error=run.error or "",
    )

    # 5. Call Gemini Flash via new google-genai SDK
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in environment")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )

    raw_text = response.text.strip()

    # Strip markdown fences if Gemini adds them despite the mime type hint
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    parsed: dict = json.loads(raw_text)

    # Validate required fields
    required_keys = {"root_cause", "fix_suggestion", "confidence", "failure_category"}
    missing = required_keys - parsed.keys()
    if missing:
        raise ValueError(f"Gemini response missing required fields: {missing}")

    if parsed["failure_category"] not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid failure_category '{parsed['failure_category']}'. "
            f"Must be one of {VALID_CATEGORIES}"
        )

    confidence = float(parsed["confidence"])
    if not (0.0 <= confidence <= 1.0):
        raise ValueError(f"confidence must be between 0 and 1, got {confidence}")

    # 6. Persist to analysis_cache
    now = datetime.utcnow()
    cache_entry = AnalysisCache(
        id=uuid.uuid4(),
        run_id=run.id,
        root_cause=parsed["root_cause"],
        fix_suggestion=parsed["fix_suggestion"],
        fix_code_hint=parsed.get("fix_code_hint"),
        confidence=confidence,
        failure_category=parsed["failure_category"],
        analyzed_at=now,
        gemini_model=GEMINI_MODEL,
    )
    db.add(cache_entry)
    await db.commit()

    # 7. Return result
    return AnalysisResult(
        run_id=run.id,
        root_cause=parsed["root_cause"],
        fix_suggestion=parsed["fix_suggestion"],
        fix_code_hint=parsed.get("fix_code_hint"),
        confidence=confidence,
        failure_category=parsed["failure_category"],
        analyzed_at=now,
        gemini_model=GEMINI_MODEL,
        cached=False,
    )
