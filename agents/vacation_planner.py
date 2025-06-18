from google.adk.agents import Agent
from tools.vacation_tools import get_weather, find_hotels, suggest_activities

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

vacation_planner_agent = Agent(
    name="vacation_planner_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="A helpful agent for planning vacations.",
    instruction="You are a friendly and helpful vacation planning assistant. "
                "Your goal is to help the user plan their perfect trip. "
                "1. First, understand the user's needs. If the destination, budget for hotels (max price), or their interests (e.g., food, history, art) are missing, ask for them. "
                "2. Once you have enough information, use your available tools (`get_weather`, `find_hotels`, `suggest_activities`) to gather information. You can use multiple tools in one turn. "
                "3. Finally, combine all the information into a helpful summary for the user. "
                "4. Be conversational and friendly.",
    tools=[get_weather, find_hotels, suggest_activities],
)

print(f"Agent '{vacation_planner_agent.name}' created.") 