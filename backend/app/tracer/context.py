from contextvars import ContextVar
from typing import Optional, List, Dict, Any

current_run_id: ContextVar[Optional[str]] = ContextVar('current_run_id', default=None)
step_buffer: ContextVar[List[Dict[str, Any]]] = ContextVar('step_buffer', default=[])

def get_current_run_id() -> Optional[str]:
    return current_run_id.get()

def set_current_run_id(run_id: Optional[str]) -> None:
    current_run_id.set(run_id)

def get_step_buffer() -> List[Dict[str, Any]]:
    return step_buffer.get()

def add_step_to_buffer(step_dict: Dict[str, Any]) -> None:
    buffer = step_buffer.get()
    buffer.append(step_dict)
