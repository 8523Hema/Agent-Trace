import asyncio
import json
from app.tracer import trace, record_step
from app.database import engine, Base
from app.database import SessionLocal
from app.models import Run, Step
from sqlalchemy import select

@trace(agent_name='test_agent')
async def run_agent(task_name: str):
    record_step(
        step_type='llm', 
        name='analyze_task', 
        input_data={'task': task_name}, 
        output_data={'plan': 'Use tools to solve'}
    )
    
    record_step(
        step_type='tool', 
        name='search_internet', 
        input_data={'query': 'FastAPI trace decorator'}, 
        status='failed', 
        error='Timeout fetching results'
    )
    
    record_step(
        step_type='llm', 
        name='generate_response', 
        input_data={'context': 'Partial results'}, 
        output_data={'response': 'Here is what I found...'}
    )
    return {"message": "Agent execution finished"}

async def main():
    # Setup tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("Running @trace decorated agent...")
    await run_agent(task_name="test_trace")
    
    print("\nVerifying DB records...")
    async with SessionLocal() as db:
        runs = (await db.execute(select(Run))).scalars().all()
        for r in runs:
            print(f"Run ID: {r.id}")
            print(f"  Agent: {r.agent_name}")
            print(f"  Status: {r.status}")
            print(f"  Output: {json.dumps(r.output)}")
            print(f"  Steps:")
            
            steps = (await db.execute(select(Step).where(Step.run_id == r.id).order_by(Step.step_index))).scalars().all()
            for s in steps:
                print(f"    - [{s.step_index}] {s.name} ({s.step_type}) -> Status: {s.status}")
                if s.error:
                    print(f"        Error: {s.error}")

if __name__ == '__main__':
    asyncio.run(main())
