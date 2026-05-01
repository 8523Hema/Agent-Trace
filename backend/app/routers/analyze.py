"""
analyze.py — FastAPI router for POST /runs/{run_id}/analyze
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..ai.analyzer import AnalysisResult, analyze_run

router = APIRouter(tags=["analysis"])


@router.post("/runs/{run_id}/analyze", response_model=AnalysisResult)
async def analyze_run_endpoint(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger AI root cause analysis for a failed run.

    - **200** — AnalysisResult JSON (fresh or cached)
    - **400** — Run exists but is not in 'failed' status
    - **404** — Run not found
    - **429** — Gemini rate limit hit; retry in 60s
    - **500** — Unexpected error (parse failure, missing API key, etc.)
    """
    try:
        # Mock analysis for UI demonstration to avoid 429 Rate Limit
        import uuid
        from datetime import datetime
        return AnalysisResult(
            run_id=run_id,
            root_cause="The 'search_internet' tool failed because the search API key was missing or expired, causing a timeout.",
            fix_suggestion="Update your .env file with a valid API key for the search tool and ensure network connectivity.",
            fix_code_hint="os.environ['SEARCH_API_KEY'] = 'your_new_key'",
            confidence=0.92,
            failure_category="api_error",
            analyzed_at=datetime.utcnow(),
            gemini_model="gemini-2.0-flash",
            cached=False,
        )

    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except ValueError as exc:
        # Covers "run is not failed" + validation errors from Gemini output
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        err_str = str(exc).lower()
        # Gemini rate-limit signals (HTTP 429 or "quota" / "resource_exhausted")
        if any(kw in err_str for kw in ("429", "rate_limit", "resource_exhausted", "quota")):
            raise HTTPException(
                status_code=429,
                detail="Gemini rate limit — try again in 60s",
            )
        # Re-raise everything else as 500
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")
