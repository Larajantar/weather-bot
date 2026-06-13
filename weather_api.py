import requests
import time

#координаты городов
CITIES = {
    "Москва": (55.75, 37.62),
    "Одинцово": (55.68, 37.26),
    "Питер": (59.93, 30.31),
    "Гатчина": (59.57, 30.12)
}

BASE_URL = "https://api.open-meteo.com/v1/forecast"

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
    try:
        current_time = data["current"]["time"]
        times = data["hourly"]["time"]

        if current_time in times:
            i = times.index(current_time)
            return data["hourly"]["relativehumidity_2m"][i]

        return data["hourly"]["relativehumidity_2m"][0]
    except Exception:
        return 0

# ✅ универсальный запрос (с retry)
def fetch_weather(lat, lon, retries=2):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weathercode,time",
        "hourly": "relativehumidity_2m"
    }

    for attempt in range(retries):
        try:
            response = requests.get(BASE_URL, params=params, timeout=5)

            # если 429 → подождать и попробовать снова
            if response.status_code == 429:
                print("⚠️ Rate limit hit, retry...", flush=True)
                time.sleep(1)
                continue

            response.raise_for_status()
            return response.json()

        except Exception as e:
            print("Ошибка запроса:", e, flush=True)
            time.sleep(1)
    return None


# ✅ для обычного ответа
def get_weather(city):
    lat, lon = CITIES.get(city, (None, None))
    if not lat:
        return "❌ Город не найден"

    data = fetch_weather(lat, lon)

    if not data or "current" not in data:
        return "⚠️ Погода временно недоступна"

    try:
        temp = data["current"]["temperature_2m"]
        code = data["current"]["weathercode"]
        humidity = get_current_humidity(data)

        desc = get_weather_description(code)

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
    lat, lon = CITIES.get(city, (None, None))
    if not lat:
        return 0, 0

    data = fetch_weather(lat, lon)

    if not data or "current" not in data:
        return 0, 0

    try:
        temp = data["current"]["temperature_2m"]
        humidity = get_current_humidity(data)
        return temp, humidity
    except Exception:
        return 0, 0
