import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Название листа в таблице
SHEET_NAME = "Лист1"  # или твое реальное название листа в гугл-таблице

def authenticate_google_sheets():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
    client = gspread.authorize(creds)
    return client

# Получить все задачи из таблицы
def get_tasks():
    sheet = authenticate_google_sheets().worksheet(SHEET_NAME)
    tasks = sheet.get_all_records()
    return tasks

# Обновить статус задачи
def update_task_status(task_name, new_status):
    sheet = authenticate_google_sheets().worksheet(SHEET_NAME)
    cell = sheet.find(task_name)
    if cell:
        sheet.update_cell(cell.row, 3, new_status)  # Статус в 3-й колонке

# Обновить дату выполнения задачи
def update_task_date(task_name, new_date):
    sheet = authenticate_google_sheets().worksheet(SHEET_NAME)
    cell = sheet.find(task_name)
    if cell:
        sheet.update_cell(cell.row, 2, new_date)  # Дата выполнения во 2-й колонке
