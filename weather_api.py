import requests
import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


# ✅ запрос к API
def fetch_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()

    except Exception as e:
        print("Ошибка запроса:", e, flush=True)
        return None


# ✅ обычный ответ
def get_weather(city):
    data = fetch_weather(city)

    if not data:
        return "❌ Город не найден"

    try:
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()

        return (
            f"{city}\n"
            f"🌡 Температура: {temp}°C\n"
            f"💧 Влажность: {humidity}%\n"
            f"🌤 Состояние: {desc}"
        )

    except Exception:
        return "⚠️ Ошибка обработки данных"


# ✅ для сравнения
def get_raw_weather(city):
    data = fetch_weather(city)

    if not data:
        return 0, 0

    try:
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        return temp, humidity
    except Exception:
        return 0, 0
