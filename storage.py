import json
import os
from datetime import datetime
from typing import List, Dict, Any

DATA_FILE = "blog_data.json"

def save_data(travelers: List[Dict], journeys: List[Dict], next_traveler_id: int, next_journey_id: int) -> None:
    data = {
        'travelers': travelers,
        'journeys': journeys,
        'next_traveler_id': next_traveler_id,
        'next_journey_id': next_journey_id
    }

    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=str, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")

def load_data() -> tuple:
    if not os.path.exists(DATA_FILE):
        return [], [], 1, 1

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        travelers = _convert_dates(data.get('travelers', []))
        journeys = _convert_dates(data.get('journeys', []))

        return (
            travelers,
            journeys,
            data.get('next_traveler_id', 1),
            data.get('next_journey_id', 1)
        )
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        return [], [], 1, 1

def _convert_dates(data_list: List[Dict]) -> List[Dict]:
    converted = []
    for item in data_list:
        converted_item = item.copy()
        for field in ['createdAt', 'updatedAt']:
            if field in item and isinstance(item[field], str):
                try:
                    date_str = item[field].replace('Z', '+00:00')
                    converted_item[field] = datetime.fromisoformat(date_str)
                except (ValueError, AttributeError):
                    converted_item[field] = datetime.now()
        converted.append(converted_item)
    return converted

def _restore_datetime_fields(data_list: List[Dict]) -> List[Dict]:
    restored = []
    for item in data_list:
        restored_item = item.copy()
        for field in ['createdAt', 'updatedAt']:
            if field in item and isinstance(item[field], str):
                try:
                    restored_item[field] = datetime.fromisoformat(item[field].replace('Z', '+00:00'))
                except:
                    restored_item[field] = datetime.now()
        restored.append(restored_item)
    return restored

def initialize_default_data() -> tuple:
    default_travelers = [{
        "id": 1,
        "email": "wanderer@travel.com",
        "username": "Челик",
        "password": "wander123",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }]

    default_journeys = [{
        "id": 1,
        "travelerId": 1,
        "destination": "Горы Алтая",
        "story": "Мои первые впечатления от путешествия по Алтайским горам. Невероятные пейзажи, чистый воздух и гостеприимные местные жители сделали эту поездку незабываемой...",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }]

    return default_travelers, default_journeys, 2, 2