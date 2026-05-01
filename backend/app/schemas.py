from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, Dict, List
import uuid
from datetime import datetime

class StepBase(BaseModel):
    step_index: int
    step_type: str
    name: str
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    step_metadata: Optional[Dict[str, Any]] = Field(None, validation_alias="step_metadata", serialization_alias="metadata")

class StepCreate(StepBase):
    pass

class Step(StepBase):
    id: uuid.UUID
    run_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AnalysisCacheBase(BaseModel):
    root_cause: str
    fix_suggestion: str
    fix_code_hint: Optional[str] = None
    confidence: float
    failure_category: str
    analyzed_at: datetime
    gemini_model: str

class AnalysisCacheCreate(AnalysisCacheBase):
    pass

class AnalysisCache(AnalysisCacheBase):
    id: uuid.UUID
    run_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

class RunBase(BaseModel):
    agent_name: str
    status: str
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    share_token: str

class RunCreate(RunBase):
    pass

class Run(RunBase):
    id: uuid.UUID
    steps: List[Step] = []
    analysis: Optional[AnalysisCache] = None

    model_config = ConfigDict(from_attributes=True)
