import os
import json
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем данные из переменной окружения
google_creds = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

# Определяем область доступа (scope) для Google Sheets API
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Создаем объект учетных данных
credentials = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, SCOPE)

# Подключаемся к Google Sheets API
try:
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key("1NcoQVZwdK5u-GJk96H3rTgMElEtKJm2MUOlXhUOchKA").sheet1
    print("Подключение к Google Sheets успешно.")
except Exception as e:
    print(f"Ошибка при подключении к Google Sheets: {e}")
    exit()

# Пример функции для получения задач из таблицы
def get_active_tasks():
    try:
        data = sheet.get_all_records()
        active = []
        for idx, row in enumerate(data):
            if row['статус'].lower() not in ['выполнено', 'отменено']:
                row['id'] = idx + 2  # +2: первая строка — заголовок, индексация с 1
                active.append(row)
        return active
    except Exception as e:
        print(f"Ошибка при получении активных задач: {e}")
        return []
