from typing import Any, Dict, List, Optional
from llama_index.core.callbacks.base_handler import BaseCallbackHandler
from llama_index.core.callbacks.schema import CBEventType
from app.tracer import record_step

class AgentTraceLlamaIndexHandler(BaseCallbackHandler):
    def __init__(
        self,
        event_starts_to_ignore: Optional[List[CBEventType]] = None,
        event_ends_to_ignore: Optional[List[CBEventType]] = None,
    ) -> None:
        super().__init__(
            event_starts_to_ignore=event_starts_to_ignore or [],
            event_ends_to_ignore=event_ends_to_ignore or [],
        )

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        name = event_type.value
        input_data = {}
        if payload:
            input_data = {k: str(v) for k, v in payload.items()}
        record_step(step_type=f"{name}_start", name=name, input_data=input_data)
        return event_id

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        name = event_type.value
        output_data = {}
        status = 'success'
        if payload:
            output_data = {k: str(v) for k, v in payload.items()}
            if 'error' in payload or 'exception' in payload:
                status = 'failed'
        record_step(step_type=f"{name}_end", name=name, input_data={}, output_data=output_data, status=status)

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        pass

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        pass
