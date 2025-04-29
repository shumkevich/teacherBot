import os
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
    with open(CREDS_FILE_PATH, 'wb') as file:
        file.write(response.content)
    print("Файл с ключами успешно скачан.")

# Определение области доступа
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Подключение к Google Sheets с использованием учетных данных
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE_PATH, SCOPE)

# Авторизация
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(os.getenv("SPREADSHEET_ID")).sheet1  # Получаем ID из переменных окружения


def get_active_tasks():
    data = sheet.get_all_records()
    active = []
    for idx, row in enumerate(data):
        if row['статус'].lower() not in ['выполнено', 'отменено']:  # Фильтруем задачи по статусу
            row['id'] = idx + 2  # Индекс строки (учитываем, что индексация с 2)
            active.append(row)
    return active


def update_task_status(row_index, new_status):
    sheet.update_cell(row_index, 3, new_status)  # Обновляем статус задачи (столбец C)


def update_task_date(row_index, days):
    from datetime import datetime, timedelta
    new_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    sheet.update_cell(row_index, 2, new_date)  # Обновляем дату (столбец B)
    sheet.update_cell(row_index, 3, "отложено")  # Обновляем статус на "отложено"
