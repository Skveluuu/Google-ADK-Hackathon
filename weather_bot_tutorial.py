#!/usr/bin/env python3
"""
Weather Bot with Google ADK
Following the official tutorial: https://google.github.io/adk-docs/tutorials/agent-team/
"""

import os
import asyncio
import requests
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from typing import List

import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

# --- API and Model Configuration ---
load_dotenv()
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
print("Environment configured.")


# --- Tool Definitions ---

def get_weather(city: str) -> dict:
    """Retrieves the live, current weather report for a specified city."""
    print(f"--- Tool: get_weather called for city: {city} ---")
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return {"status": "error", "error_message": "OpenWeatherMap API key is not configured."}
    
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    try:
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()
        location_data = geo_response.json()
        if not location_data:
            return {"status": "error", "error_message": f"Could not find geocoding info for {city}."}
        lat, lon = location_data[0]['lat'], location_data[0]['lon']
    except Exception as e:
        return {"status": "error", "error_message": f"Geocoding API failed for {city}. Error: {e}"}
        
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        report = f"The weather in {city} is {weather_data['weather'][0]['description']} with a temperature of {weather_data['main']['temp']}°C."
        return {"status": "success", "report": report}
    except Exception as e:
        return {"status": "error", "error_message": f"Weather API failed for {city}. Error: {e}"}

def find_hotels(city: str, max_price: int = 500) -> dict:
    """Finds a list of hotels in a given city under a specified maximum price."""
    print(f"--- Tool: find_hotels called for {city} with max price ${max_price} ---")
    
    hotels = {
        "paris": [{"name": "Hotel de Louvre", "price": 450}, {"name": "Chic Parisian Flat", "price": 250}, {"name": "Budget Inn Paris", "price": 120}],
        "london": [{"name": "The Savoy", "price": 800}, {"name": "London Marriott Hotel", "price": 350}, {"name": "St. Giles London", "price": 150}],
        "tokyo": [{"name": "Park Hyatt Tokyo", "price": 750}, {"name": "Shinjuku Granbell Hotel", "price": 200}, {"name": "APA Hotel Shinjuku", "price": 90}],
    }
    
    city_normalized = city.lower()
    if city_normalized in hotels:
        available_hotels = [h for h in hotels[city_normalized] if h['price'] <= max_price]
        if not available_hotels:
            return {"status": "error", "error_message": f"No hotels found in {city.title()} under ${max_price}."}
        return {"status": "success", "hotels": available_hotels}
    else:
        return {"status": "error", "error_message": f"Hotel information not available for {city.title()}."}
        
def suggest_activities(city: str, interests: List[str]) -> dict:
    """Suggests activities in a city based on a list of interests."""
    print(f"--- Tool: suggest_activities called for {city} with interests: {interests} ---")

    activities = {
        "paris": {"museum": "Visit the Louvre Museum.", "food": "Take a food tour in Le Marais.", "history": "Explore the Palace of Versailles."},
        "london": {"history": "Tour the Tower of London.", "art": "Visit the Tate Modern art gallery.", "food": "Enjoy afternoon tea at The Ritz."},
        "tokyo": {"technology": "Visit Akihabara.", "food": "Explore the Tsukiji Outer Market.", "culture": "Visit the Senso-ji Temple."},
    }
    
    city_normalized = city.lower()
    if city_normalized in activities:
        suggestions = [activities[city_normalized][interest.lower()] for interest in interests if interest.lower() in activities[city_normalized]]
        if not suggestions:
            return {"status": "error", "error_message": f"Couldn't find activities for your interests in {city.title()}."}
        return {"status": "success", "activities": suggestions}
    else:
        return {"status": "error", "error_message": f"Activity information not available for {city.title()}."}


# --- Agent Definition ---
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


# --- Agent Interaction Function ---
async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text = event.content.parts[0].text
    print(f"<<< Agent Response: {final_response_text}")


# --- Main Execution ---
async def main():
    session_service = InMemorySessionService()
    APP_NAME, USER_ID, SESSION_ID = "vacation_planner_app", "user_vacation_1", "session_vacation_001"
    
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    
    runner = Runner(agent=vacation_planner_agent, app_name=APP_NAME, session_service=session_service)
    print(f"Runner created for agent '{runner.agent.name}'.")
    
    await call_agent_async("Hi, I want to plan a trip.", runner=runner, user_id=USER_ID, session_id=SESSION_ID)
    await call_agent_async("I'm thinking of going to Paris. I like museums and food, and my hotel budget is $300 per night.", runner=runner, user_id=USER_ID, session_id=SESSION_ID)


if __name__ == "__main__":
    print("Starting Vacation Planner Bot...")
    asyncio.run(main()) 