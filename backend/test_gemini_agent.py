"""
test_gemini_agent.py
Runs a tool-calling agent (Gemini 2.0 Flash) that deliberately fails
via a RuntimeError in process_refund -- producing a 'failed' Run in DB.
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from app.tracer import trace, record_step
from app.tracer.langchain_hook import AgentTraceCallbackHandler
from app.database import engine, Base, SessionLocal
from app.models import Run, Step
from sqlalchemy import select

# Fix Windows cp1252 console encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def process_refund(order_id: str) -> str:
    """Processes a refund for a given order ID."""
    raise RuntimeError(
        f"Payment gateway timeout: could not process refund for order {order_id}"
    )


@tool
def create_shipment(order_id: str) -> str:
    """Creates a new shipment for a given order ID."""
    return f"Shipment created for {order_id}"


# ---------------------------------------------------------------------------
# Traced agent
# ---------------------------------------------------------------------------

@trace("customer_support_agent")
async def run_support_agent(user_input: str):
    """
    Minimal tool-calling loop using Gemini 2.0 Flash via bind_tools.
    The @trace decorator captures the run; AgentTraceCallbackHandler
    captures individual LLM steps.
    """
    tracer = AgentTraceCallbackHandler()
    tools_list = [process_refund, create_shipment]

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        callbacks=[tracer],
    ).bind_tools(tools_list)

    messages = [HumanMessage(content=user_input)]

    # LLM call (step 1)
    record_step(
        step_type="llm_call",
        name="gemini-2.0-flash",
        input_data={"messages": [user_input]},
    )

    ai_msg = await llm.ainvoke(messages)

    record_step(
        step_type="llm_call",
        name="llm_end",
        input_data={},
        output_data={
            "content": ai_msg.content or "",
            "tool_calls": [tc["name"] for tc in (ai_msg.tool_calls or [])],
        },
        status="success",
    )

    messages.append(ai_msg)

    # Execute every tool the LLM requested
    tool_map = {t.name: t for t in tools_list}

    for tc in ai_msg.tool_calls or []:
        tool_name = tc["name"]
        tool_args = tc["args"]

        record_step(
            step_type="tool_call",
            name=tool_name,
            input_data=tool_args,
        )

        try:
            result = tool_map[tool_name].invoke(tool_args)
            record_step(
                step_type="tool_result",
                name=f"{tool_name}_result",
                input_data={},
                output_data={"output": result},
                status="success",
            )
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

        except Exception as tool_err:
            record_step(
                step_type="tool_result",
                name=f"{tool_name}_error",
                input_data={},
                status="failed",
                error=str(tool_err),
            )
            # Re-raise so @trace marks the run as 'failed'
            raise

    return {"output": ai_msg.content}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY is not set in .env")
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("=" * 60)
    print("Running customer support agent (expect a failure)...")
    print("=" * 60)

    try:
        await run_support_agent("customer wants refund for order #9023")
    except Exception as e:
        print(f"\n[Expected error captured by @trace]: {type(e).__name__}: {e}")

    print("\n-- Verifying DB records --")
    async with SessionLocal() as db:
        runs = (
            await db.execute(select(Run).order_by(Run.started_at.desc()))
        ).scalars().all()

        if not runs:
            print("No runs found in DB!")
            return

        r = runs[0]
        print(f"\nRun ID   : {r.id}")
        print(f"Agent    : {r.agent_name}")
        print(f"Status   : {r.status}")
        print(f"Error    : {r.error}")

        steps = (
            await db.execute(
                select(Step)
                .where(Step.run_id == r.id)
                .order_by(Step.step_index)
            )
        ).scalars().all()

        print(f"Steps    : {len(steps)} captured")
        for s in steps:
            marker = "[FAIL]" if s.status == "failed" else "[ OK ]"
            print(f"  {marker} [{s.step_index}] {s.name} ({s.step_type}) -> {s.status}")
            if s.error:
                print(f"          Error: {s.error}")

        print()
        print("=" * 60)
        if r.status == "failed":
            print("Run is 'failed' -- ready to analyze!")
            print(f"\n  POST http://127.0.0.1:8000/runs/{r.id}/analyze")
        else:
            print(f"Run status is '{r.status}' -- re-run to get a failed run.")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
