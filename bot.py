import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.daily import DailyTrigger
from datetime import datetime, timedelta
import pytz
import config
import sheets_service

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Вспомогательная функция для авторизации пользователей
def is_authorized(user_id):
    return user_id in config.ALLOWED_USERS

# Обработчик команды /start
def start(update, context):
    user_id = update.message.from_user.id
    if is_authorized(user_id):
        update.message.reply_text("Добро пожаловать! Ты авторизован.")
        send_daily_tasks(update, context)  # Отправить задачи сразу после старта
    else:
        update.message.reply_text("Неизвестный пользователь. Доступ запрещён.")

# Обработчик команды /sync
def sync(update, context):
    user_id = update.message.from_user.id
    if is_authorized(user_id):
        send_daily_tasks(update, context)
    else:
        update.message.reply_text("Неавторизованный доступ.")

# Отправка списка задач
def send_daily_tasks(update, context):
    tasks = sheets_service.get_tasks()
    message = "Текущие задачи:\n"
    
    keyboard = []
    for task in tasks:
        if task['Статус'] not in ['выполнено', 'отменено']:
            message += f"\n{task['Название задачи']}: {task['Описание']} (Статус: {task['Статус']})"
            keyboard.append([
                InlineKeyboardButton(task['Название задачи'], callback_data=f"task_{task['Название задачи']}")
            ])
    
    if keyboard:
        keyboard.append([InlineKeyboardButton("Обновить задачи", callback_data="sync")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(message, reply_markup=reply_markup)
    else:
        update.message.reply_text("Нет задач для выполнения.")

# Обработчик выбора задачи
def task_handler(update, context):
    query = update.callback_query
    task_name = query.data.split("_")[1]
    task_details = next(task for task in sheets_service.get_tasks() if task['Название задачи'] == task_name)
    
    keyboard = [
        [InlineKeyboardButton("Выполнено", callback_data=f"completed_{task_name}")],
        [InlineKeyboardButton("Отложить на сутки", callback_data=f"delay_1d_{task_name}")],
        [InlineKeyboardButton("Отложить на неделю", callback_data=f"delay_7d_{task_name}")],
        [InlineKeyboardButton("Отменить задачу", callback_data=f"cancel_{task_name}")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ]
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        f"{task_name}\n\nОписание: {task_details['Описание']}\nСтатус: {task_details['Статус']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработчик действий по задачам
def task_action_handler(update, context):
    query = update.callback_query
    action_data = query.data.split("_")
    
    action = action_data[0]
    task_name = action_data[1]
    
    if action == "completed":
        sheets_service.update_task_status(task_name, "выполнено")
        query.edit_message_text(f"Задача '{task_name}' выполнена.")
    elif action == "delay_1d":
        new_date = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=1)).date()
        sheets_service.update_task_date(task_name, new_date)
        sheets_service.update_task_status(task_name, f"отложено до {new_date}")
        query.edit_message_text(f"Задача '{task_name}' отложена на сутки.")
    elif action == "delay_7d":
        new_date = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(weeks=1)).date()
        sheets_service.update_task_date(task_name, new_date)
        sheets_service.update_task_status(task_name, f"отложено до {new_date}")
        query.edit_message_text(f"Задача '{task_name}' отложена на неделю.")
    elif action == "cancel":
        sheets_service.update_task_status(task_name, "отменено")
        query.edit_message_text(f"Задача '{task_name}' отменена.")
    elif action == "back":
        send_daily_tasks(update, context)

# Запуск ежедневного напоминания
def schedule_daily_notification(context):
    job = context.job
    send_daily_tasks(job.context, context)

# Главная функция
def main():
    updater = Updater(config.TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Команды
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("sync", sync))

    # Обработчики кнопок
    dispatcher.add_handler(CallbackQueryHandler(task_handler, pattern="task_"))
    dispatcher.add_handler(CallbackQueryHandler(task_action_handler, pattern="completed|delay_1d|delay_7d|cancel|back"))
    
    # Планировщик задач
    scheduler = BackgroundScheduler()
    scheduler.add_job(schedule_daily_notification, DailyTrigger(hour=9, minute=0, second=0), args=[updater.bot], id="daily_task_check")
    scheduler.start()

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()