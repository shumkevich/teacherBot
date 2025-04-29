import os
import json
import requests
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import gspread
from googleapiclient.discovery import build

# Загружаем переменные окружения из .env файла
load_dotenv()

# Путь для хранения файла с ключами
CREDS_FILE_PATH = 'apigooglebotdasha.json'

# Проверка, если файл не существует, скачиваем его
if not os.path.exists(CREDS_FILE_PATH):
    print("Ключи Google API не найдены. Скачиваем файл...")
    url = "https://raw.githubusercontent.com/shumkevich/teacherBot/main/apigooglebotdasha.json"
    response = requests.get(url)
    if response.status_code == 200:
        with open(CREDS_FILE_PATH, 'wb') as file:
            file.write(response.content)
        print("Файл с ключами успешно скачан.")
    else:
        print("Ошибка при скачивании файла с ключами.")
        exit()

# Определение области доступа
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Подключение к Google Sheets с использованием учетных данных
try:
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE_PATH, SCOPE)
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key("1NcoQVZwdK5u-GJk96H3rTgMElEtKJm2MUOlXhUOchKA").sheet1
    print("Подключение к Google Sheets успешно.")
except Exception as e:
    print(f"Ошибка при подключении к Google Sheets: {e}")
    exit()

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

def update_task_status(row_index, new_status):
    try:
        sheet.update_cell(row_index, 3, new_status)  # Статус — 3-й столбец
    except Exception as e:
        print(f"Ошибка при обновлении статуса задачи: {e}")

def update_task_date(row_index, days):
    from datetime import datetime, timedelta
    try:
        new_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        sheet.update_cell(row_index, 2, new_date)  # Дата — 2-й столбец
        sheet.update_cell(row_index, 3, "отложено")
    except Exception as e:
        print(f"Ошибка при обновлении даты задачи: {e}")
