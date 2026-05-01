from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Any, Dict
import uuid

from .. import models, schemas
from ..database import get_db

router = APIRouter(tags=["runs"])

@router.get("/runs", response_model=Dict[str, Any])
async def list_runs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    # Total count
    total_query = select(func.count()).select_from(models.Run)
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Get runs ordered by started_at desc
    query = select(models.Run).options(
        selectinload(models.Run.steps),
        selectinload(models.Run.analysis)
    ).order_by(models.Run.started_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    runs = result.scalars().all()
    
    for r in runs:
        r.steps.sort(key=lambda s: s.step_index)
        
    # We serialize them using the Pydantic schema model_validate so it matches schemas.Run output
    runs_serialized = [schemas.Run.model_validate(r).model_dump(mode="json") for r in runs]
    
    return {"runs": runs_serialized, "total": total}

@router.get("/runs/{run_id}", response_model=schemas.Run)
async def get_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    query = select(models.Run).options(
        selectinload(models.Run.steps),
        selectinload(models.Run.analysis)
    ).where(models.Run.id == run_id)
    result = await db.execute(query)
    run = result.scalar_one_or_none()
    
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
        
    run.steps.sort(key=lambda s: s.step_index)
    
    return run

@router.get("/share/{share_token}", response_model=schemas.Run)
async def get_run_by_share_token(share_token: str, db: AsyncSession = Depends(get_db)):
    query = select(models.Run).options(
        selectinload(models.Run.steps),
        selectinload(models.Run.analysis)
    ).where(models.Run.share_token == share_token)
    result = await db.execute(query)
    run = result.scalar_one_or_none()
    
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
        
    run.steps.sort(key=lambda s: s.step_index)
    
    return run
