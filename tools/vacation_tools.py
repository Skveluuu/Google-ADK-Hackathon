import os
import requests
from typing import List

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