import os
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем путь к файлу с ключами из переменной окружения
CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE")

# Проверка, что переменная окружения правильно установлена
if not CREDS_FILE:
    raise ValueError("Переменная окружения GOOGLE_CREDS_FILE не установлена или пуста. Проверьте файл .env.")
else:
    print(f"Используем файл с ключами: {CREDS_FILE}")

# Определение области доступа
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Подключение к Google Sheets с использованием учетных данных
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)

# Авторизация
import gspread
gc = gspread.authorize(credentials)
sheet = gc.open_by_key("1NcoQVZwdK5u-GJk96H3rTgMElEtKJm2MUOlXhUOchKA").sheet1


def get_active_tasks():
    data = sheet.get_all_records()
    active = []
    for idx, row in enumerate(data):
        if row['статус'].lower() not in ['выполнено', 'отменено']:
            row['id'] = idx + 2  # +2: первая строка — заголовок, индексация с 1
            active.append(row)
    return active


def update_task_status(row_index, new_status):
    sheet.update_cell(row_index, 3, new_status)  # Статус — 3-й столбец


def update_task_date(row_index, days):
    new_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    sheet.update_cell(row_index, 2, new_date)  # Дата — 2-й столбец
    sheet.update_cell(row_index, 3, "отложено")
