import functools
import inspect
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Any, Callable

from app.database import SessionLocal
from app.models import Run, Step
from app.tracer.context import set_current_run_id, current_run_id, step_buffer

async def _create_run(agent_name: str, kwargs: dict) -> Run:
    async with SessionLocal() as db:
        new_run = Run(
            agent_name=agent_name,
            status="running",
            input=kwargs,
            started_at=datetime.now(timezone.utc),
            share_token=uuid.uuid4().hex[:16]
        )
        db.add(new_run)
        await db.commit()
        await db.refresh(new_run)
        return new_run

async def _finalize_run(run_id: uuid.UUID, status: str, output: Any, error: str, start_time: datetime, steps_data: list):
    async with SessionLocal() as db:
        run = await db.get(Run, run_id)
        if run:
            run.status = status
            run.output = output if isinstance(output, dict) else {"result": str(output)} if output is not None else None
            run.error = error
            run.ended_at = datetime.now(timezone.utc)
            run.duration_ms = int((run.ended_at - start_time).total_seconds() * 1000)
            
            for idx, s in enumerate(steps_data):
                db_step = Step(
                    run_id=run.id,
                    step_index=idx,
                    step_type=s.get('step_type'),
                    name=s.get('name'),
                    input=s.get('input', {}),
                    output=s.get('output'),
                    error=s.get('error'),
                    status=s.get('status'),
                    started_at=s.get('started_at'),
                    ended_at=s.get('ended_at'),
                    duration_ms=s.get('duration_ms'),
                    step_metadata=s.get('step_metadata')
                )
                db.add(db_step)
            
            await db.commit()

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Note: running a sync trace decorator inside a running async loop is tricky.
        # This naive fallback works in standard threads.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)

def trace(agent_name: str):
    def decorator(func: Callable):
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = datetime.now(timezone.utc)
                # Filter kwargs to only JSON-serializable inputs if needed, here we just pass kwargs
                run = await _create_run(agent_name, kwargs)
                
                run_id_token = current_run_id.set(str(run.id))
                step_buffer_token = step_buffer.set([])
                
                status = "success"
                output = None
                error = None
                
                try:
                    output = await func(*args, **kwargs)
                except Exception as e:
                    status = "failed"
                    error = str(e)
                    raise
                finally:
                    steps = step_buffer.get()
                    await _finalize_run(run.id, status, output, error, start_time, steps)
                    
                    current_run_id.reset(run_id_token)
                    step_buffer.reset(step_buffer_token)
                    
                return output
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = datetime.now(timezone.utc)
                run = run_async(_create_run(agent_name, kwargs))
                
                run_id_token = current_run_id.set(str(run.id))
                step_buffer_token = step_buffer.set([])
                
                status = "success"
                output = None
                error = None
                
                try:
                    output = func(*args, **kwargs)
                except Exception as e:
                    status = "failed"
                    error = str(e)
                    raise
                finally:
                    steps = step_buffer.get()
                    run_async(_finalize_run(run.id, status, output, error, start_time, steps))
                    
                    current_run_id.reset(run_id_token)
                    step_buffer.reset(step_buffer_token)
                    
                return output
            return sync_wrapper
    return decorator
