from datetime import datetime, timezone
from .decorator import trace
from .context import add_step_to_buffer

def record_step(step_type: str, name: str, input_data: dict, output_data: dict = None, error: str = None, metadata: dict = None, status: str = 'success'):
    now = datetime.now(timezone.utc)
    step_dict = {
        'step_type': step_type,
        'name': name,
        'input': input_data,
        'output': output_data,
        'error': error,
        'status': status,
        'started_at': now,
        'ended_at': now,
        'duration_ms': 0,
        'step_metadata': metadata
    }
    add_step_to_buffer(step_dict)

__all__ = ['trace', 'record_step']
