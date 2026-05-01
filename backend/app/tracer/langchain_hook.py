from typing import Any, Dict, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.agents import AgentAction, AgentFinish
from app.tracer import record_step

class AgentTraceCallbackHandler(BaseCallbackHandler):
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        name = serialized.get('name', 'llm') if serialized else 'llm'
        record_step(step_type='llm_call', name=name, input_data={'prompts': prompts})

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        text = ""
        if response.generations and len(response.generations) > 0 and len(response.generations[0]) > 0:
            generation = response.generations[0][0]
            if hasattr(generation, 'message'):
                text = generation.message.content
            else:
                text = generation.text
        record_step(step_type='llm_call', name='llm_end', input_data={}, output_data={'text': text}, status='success')

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        record_step(step_type='llm_call', name='llm_error', input_data={}, status='failed', error=str(error))

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        name = serialized.get('name', 'tool') if serialized else 'tool'
        record_step(step_type='tool_call', name=name, input_data={'input': input_str})

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        record_step(step_type='tool_result', name='tool_end', input_data={}, output_data={'output': output}, status='success')

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        record_step(step_type='tool_result', name='tool_error', input_data={}, status='failed', error=str(error))

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        record_step(step_type='agent_action', name=action.tool, input_data={'tool_input': action.tool_input})

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        record_step(step_type='agent_finish', name='agent_finish', input_data={}, output_data={'return_values': finish.return_values})
