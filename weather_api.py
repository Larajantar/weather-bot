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

# ✅ универсальная функция получения влажности
def get_current_humidity(data):
    if "hourly" not in data or "time" not in data["hourly"]:
        return 0

    current_time = data["current"]["time"]
    times = data["hourly"]["time"]

    if current_time in times:
        index = times.index(current_time)
        return data["hourly"]["relativehumidity_2m"][index]

    return data["hourly"]["relativehumidity_2m"][0]

# ✅ основная функция
def get_weather(city):
    lat, lon = CITIES[city]

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weathercode",
        "hourly": "relativehumidity_2m"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Ошибка запроса:", e)
        return "Ошибка получения погоды 😢 Попробуй позже"

    if "current" not in data:
        return "Ошибка получения погоды 😢 Попробуй позже"

    # температура
    temp = data["current"]["temperature_2m"]

    # код погоды
    weather_code = data["current"]["weathercode"]
    weather_desc = get_weather_description(weather_code)
    humidity = get_current_humidity(data)

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
        "current": "temperature_2m,weathercode",
        "hourly": "relativehumidity_2m"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Ошибка запроса:", e)
        return 0, 0

    if "current" not in data:
        return 0, 0

    temp = data["current"]["temperature_2m"]   
    humidity = get_current_humidity(data)

    return temp, humidity
