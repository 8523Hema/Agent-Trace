"""
Prompt templates for Gemini-powered root cause analysis.
"""

ANALYSIS_PROMPT = """\
You are an expert AI agent debugger. Your task is to perform a precise root cause analysis \
of a failed AI agent run.

## Agent Information
- Agent Name: {agent_name}
- Original User Input: {user_input}
- Top-Level Error: {top_level_error}

## Execution Steps
{steps_formatted}

## Instructions
Analyse the steps above carefully and identify **exactly** which step failed and why.
Be specific:
- Name the **exact step** (by name and step_type) that caused the failure.
- Name the **exact tool or field** responsible if applicable.
- Classify the failure into one of these categories:
  * wrong_tool      — the agent chose an inappropriate tool for the task
  * bad_input       — the tool/LLM received malformed, missing, or invalid input
  * llm_confusion   — the LLM misunderstood the task or hallucinated
  * api_error       — an external API or service returned an error
  * logic_error     — the agent's reasoning chain had a logical flaw

## Output Format
Respond with ONLY a valid JSON object — no markdown fences, no extra text.
Use these exact keys:

{{
  "root_cause": "<one or two sentences identifying the exact failing step and why it failed>",
  "fix_suggestion": "<concrete actionable fix for the developer>",
  "fix_code_hint": "<optional short code snippet if a code change would fix this; omit key entirely if not applicable>",
  "confidence": <float between 0.0 and 1.0>,
  "failure_category": "<one of: wrong_tool | bad_input | llm_confusion | api_error | logic_error>"
}}
"""


def format_steps(steps: list[dict]) -> str:
    """
    Convert a list of step dicts into a numbered, human-readable block.

    Each step dict is expected to have:
        step_type, name, input, output, error, status
    """
    lines = []
    for i, step in enumerate(steps, start=1):
        lines.append(f"Step {i}: [{step.get('step_type', 'unknown')}] {step.get('name', 'unnamed')}")
        lines.append(f"  Status : {step.get('status', 'unknown')}")
        lines.append(f"  Input  : {step.get('input', {})}")
        lines.append(f"  Output : {step.get('output', None)}")
        if step.get("error"):
            lines.append(f"  Error  : {step['error']}")
        lines.append("")
    return "\n".join(lines)


def build_prompt(agent_name: str, user_input: str, steps: list[dict], top_level_error: str) -> str:
    """Build the full analysis prompt string."""
    return ANALYSIS_PROMPT.format(
        agent_name=agent_name,
        user_input=user_input,
        top_level_error=top_level_error or "None",
        steps_formatted=format_steps(steps),
    )
