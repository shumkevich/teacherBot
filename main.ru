import os
import json
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Получаем путь к ключу и ID таблицы
KEY_PATH = os.getenv("GOOGLE_KEY_PATH")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Область доступа
SCOPE = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Авторизация
credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_PATH, SCOPE)
service = build('sheets', 'v4', credentials=credentials)

# Чтение данных с листа
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Лист1!A1:E").execute()
values = result.get('values', [])

# Вывод данных
if not values:
    print("Нет данных.")
else:
    for row in values:
        print(row)
