import json
import re

from openai import OpenAI

from app.config import AI_MODE, OPENAI_API_KEY, OPENAI_MODEL
from app.prompts import LEAD_AGENT_SYSTEM_PROMPT, LEAD_ANALYSIS_SCHEMA


def analyze_lead(message: str) -> dict:
    if AI_MODE == "openai" and OPENAI_API_KEY:
        try:
            return analyze_lead_with_openai(message)
        except Exception:
            return analyze_lead_demo(message)

    return analyze_lead_demo(message)


def analyze_lead_with_openai(message: str) -> dict:
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": LEAD_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "lead_analysis",
                "schema": LEAD_ANALYSIS_SCHEMA,
                "strict": True,
            }
        },
    )

    data = json.loads(response.output_text)
    return normalize_analysis(data)


def analyze_lead_demo(message: str) -> dict:
    text = message.lower()

    service_type = detect_service_type(text)
    area = detect_area(text)
    location = detect_location(text)
    timeline = detect_timeline(text)
    budget = detect_budget(text)
    lead_score = detect_lead_score(text, area, timeline)
    missing_data = detect_missing_data(area, location, timeline, budget)

    return {
        "summary": build_summary(service_type, area, location, timeline),
        "service_type": service_type,
        "area": area,
        "location": location,
        "timeline": timeline,
        "budget": budget,
        "lead_score": lead_score,
        "missing_data": missing_data,
        "next_step": build_next_step(lead_score),
        "client_reply": build_client_reply(service_type, missing_data),
    }


def normalize_analysis(data: dict) -> dict:
    missing_data = data.get("missing_data", [])

    if not isinstance(missing_data, list):
        missing_data = []

    return {
        "summary": data.get("summary", "Не указано"),
        "service_type": data.get("service_type", "Не определено"),
        "area": data.get("area", "Не указана"),
        "location": data.get("location", "Не указана"),
        "timeline": data.get("timeline", "Не указаны"),
        "budget": data.get("budget", "Не указан"),
        "lead_score": data.get("lead_score", "Холодная"),
        "missing_data": missing_data,
        "next_step": data.get("next_step", "Уточнить детали заявки."),
        "client_reply": data.get("client_reply", "Здравствуйте! Уточните, пожалуйста, детали заявки."),
    }


def detect_service_type(text: str) -> str:
    if "дизайн" in text:
        return "Дизайн-проект"
    if "офис" in text:
        return "Ремонт офиса"
    if "коттедж" in text or "дом" in text:
        return "Ремонт дома"
    if "ванн" in text or "сануз" in text:
        return "Ремонт ванной или санузла"
    if "кухн" in text:
        return "Ремонт кухни"
    if "ремонт" in text or "квартир" in text:
        return "Ремонт квартиры"

    return "Не определено"


def detect_area(text: str) -> str:
    match = re.search(r"(\d+)\s*(м2|м²|кв|квадрат)", text)

    if match:
        return f"{match.group(1)} м²"

    return "Не указана"


def detect_location(text: str) -> str:
    cities = {
        "москва": "Москва",
        "санкт-петербург": "Санкт-Петербург",
        "казань": "Казань",
        "екатеринбург": "Екатеринбург",
        "новосибирск": "Новосибирск",
        "нижний новгород": "Нижний Новгород",
        "краснодар": "Краснодар",
        "самара": "Самара",
        "ростов-на-дону": "Ростов-на-Дону",
    }

    for city_key, city_name in cities.items():
        if city_key in text:
            return city_name

    return "Не указана"


def detect_timeline(text: str) -> str:
    if "срочно" in text:
        return "Срочно"
    if "завтра" in text:
        return "Завтра"
    if "недел" in text:
        return "В течение нескольких недель"
    if "месяц" in text:
        return "В течение месяца"
    if "год" in text:
        return "В течение года"

    return "Не указаны"


def detect_budget(text: str) -> str:
    match = re.search(r"(\d+[\s\d]*)\s*(рублей|руб|₽|тыс|млн)", text)

    if match:
        return match.group(0)

    return "Не указан"


def detect_lead_score(text: str, area: str, timeline: str) -> str:
    if "срочно" in text or timeline != "Не указаны":
        return "Горячая"

    if area != "Не указана":
        return "Теплая"

    return "Холодная"


def detect_missing_data(area: str, location: str, timeline: str, budget: str) -> list:
    missing = []

    if area == "Не указана":
        missing.append("Площадь объекта")
    if location == "Не указана":
        missing.append("Город или район")
    if timeline == "Не указаны":
        missing.append("Сроки начала работ")
    if budget == "Не указан":
        missing.append("Бюджет")

    return missing


def build_summary(service_type: str, area: str, location: str, timeline: str) -> str:
    return (
        f"Клиент интересуется услугой: {service_type}. "
        f"Площадь: {area}. "
        f"Локация: {location}. "
        f"Сроки: {timeline}."
    )


def build_next_step(lead_score: str) -> str:
    if lead_score == "Горячая":
        return "Связаться с клиентом как можно быстрее и предложить консультацию."

    if lead_score == "Теплая":
        return "Уточнить детали объекта и предложить предварительный расчет."

    return "Задать уточняющие вопросы и понять реальную потребность клиента."


def build_client_reply(service_type: str, missing_data: list) -> str:
    if missing_data:
        missing_text = ", ".join(missing_data).lower()
        return (
            f"Здравствуйте! Мы можем помочь с запросом: {service_type}. "
            f"Чтобы подготовить предварительный расчет, уточните, пожалуйста: {missing_text}."
        )

    return (
        f"Здравствуйте! Мы можем помочь с запросом: {service_type}. "
        "Данных достаточно для первичной оценки. Менеджер свяжется с вами, "
        "чтобы уточнить детали и подготовить расчет."
    )