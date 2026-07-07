from langchain_core.tools import tool
import httpx
from typing import Dict

@tool
async def weather_tool(city: str) -> Dict:
    """Get current weather for a city."""

    try:
        async with httpx.AsyncClient(timeout=10) as client:

            geo = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={
                    "name": city,
                    "count": 1,
                    "language": "en",
                    "format": "json",
                },
            )

            geo.raise_for_status()

            results = geo.json().get("results")

            if not results:
                return {
                    "success": False,
                    "message": f"Cannot find '{city}'."
                }

            location = results[0]

            lat = location["latitude"]
            lon = location["longitude"]

            weather = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "wind_speed_10m",
                        "weather_code",
                    ],
                },
            )

            weather.raise_for_status()

            current = weather.json()["current"]

            return {
                "success": True,
                "city": location["name"],
                "country": location["country"],
                "temperature": current["temperature_2m"],
                "humidity": current["relative_humidity_2m"],
                "wind_speed": current["wind_speed_10m"],
                "weather_code": current["weather_code"],
            }
    
    except httpx.HTTPError as e:
        return {
            "success": False,
            "message": "Unable to retrieve weather information at the moment.",
            "error": str(e),
        }