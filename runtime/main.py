import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from agents.vacation_planner import vacation_planner_agent

async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text = event.content.parts[0].text
    print(f"<<< Agent Response: {final_response_text}")

async def run_conversation():
    session_service = InMemorySessionService()
    APP_NAME, USER_ID, SESSION_ID = "vacation_planner_app", "user_vacation_1", "session_vacation_001"
    
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    
    runner = Runner(agent=vacation_planner_agent, app_name=APP_NAME, session_service=session_service)
    print(f"Runner created for agent '{runner.agent.name}'.")
    
    await call_agent_async("Hi, I want to plan a trip.", runner=runner, user_id=USER_ID, session_id=SESSION_ID)
    await call_agent_async("I'm thinking of going to Paris. I like museums and food, and my hotel budget is $300 per night.", runner=runner, user_id=USER_ID, session_id=SESSION_ID) 