from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from .. import models, schemas
from ..database import get_db

router = APIRouter(tags=["steps"])

@router.get("/runs/{run_id}/steps", response_model=List[schemas.Step])
async def list_run_steps(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # check if run exists
    run_query = select(models.Run.id).where(models.Run.id == run_id)
    run_result = await db.execute(run_query)
    if run_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Run not found")
        
    query = select(models.Step).where(models.Step.run_id == run_id).order_by(models.Step.step_index.asc())
    result = await db.execute(query)
    steps = result.scalars().all()
    
    return steps
