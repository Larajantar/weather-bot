import requests

CITIES = {
    "Москва": (55.75, 37.62),
    "Одинцово": (55.68, 37.26),
    "Питер": (59.93, 30.31),
    "Гатчина": (59.57, 30.12)
}

# перевод кода погоды в текст
def get_weather_description(code):
    weather_codes = {
        0: "Ясно ☀️",
        1: "Преимущественно ясно 🌤",
        2: "Переменная облачность ⛅",
        3: "Пасмурно ☁️",
        45: "Туман 🌫",
        48: "Туман с инеем 🌫",
        51: "Лёгкий дождь 🌦",
        61: "Дождь 🌧",
        71: "Снег ❄️",
        95: "Гроза ⛈"
    }
    return weather_codes.get(code, "Неизвестно")

def get_weather(city):
    lat, lon = CITIES[city]

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "relativehumidity_2m,weathercode"
    }

    data = requests.get(url, params=params).json()

    # температура
    temp = data["current_weather"]["temperature"]

    # код погоды
    weather_code = data["current_weather"]["weathercode"]
    weather_desc = get_weather_description(weather_code)

    # влажность (берём текущий час)
    humidity = data["hourly"]["relativehumidity_2m"][0]

    return f"""{city}
    🌡 Температура: {temp}°C
    💧 Влажность: {humidity}%    
    🌤 Состояние: {weather_desc}"""

def get_raw_weather(city):
    lat, lon = CITIES[city]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "relativehumidity_2m"
    }

    data = requests.get(url, params=params).json()

    temp = data["current_weather"]["temperature"]
    humidity = data["hourly"]["relativehumidity_2m"][0]

    return temp, humidity