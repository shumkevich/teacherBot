import logging
import os
import json
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler,
                          ContextTypes, MessageHandler, filters)

from google_service import get_active_tasks, update_task_status, update_task_date

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER_ID = 154058788
BOT_PASSWORD = "4815162342"

# Время для ежедневной проверки задач
CHECK_HOUR = 9  # 9 утра

# Переменные
user_authenticated = False

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_authenticated
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Доступ запрещён.")
        return

    if not user_authenticated:
        await update.message.reply_text("Введите пароль:")
        return

    await update.message.reply_text("Добро пожаловать! Ожидайте уведомлений о задачах.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_authenticated

    if update.effective_user.id != ALLOWED_USER_ID:
        return

    if not user_authenticated:
        if update.message.text == BOT_PASSWORD:
            user_authenticated = True
            await update.message.reply_text("Пароль принят. Доступ открыт.")
        else:
            await update.message.reply_text("Неверный пароль. Попробуйте снова.")


async def send_tasks(context: ContextTypes.DEFAULT_TYPE):
    if not user_authenticated:
        return

    tasks = get_active_tasks()
    if not tasks:
        return

    buttons = []
    for idx, task in enumerate(tasks):
        buttons.append([InlineKeyboardButton(task['название задачи'], callback_data=f"task_{idx}")])

    markup = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(chat_id=ALLOWED_USER_ID, text="Ваши задачи на сегодня:", reply_markup=markup)

    context.chat_data['tasks'] = tasks


async def task_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    task_index = int(query.data.split('_')[1])
    task = context.chat_data['tasks'][task_index]
    context.chat_data['selected_task'] = task

    buttons = [
        [InlineKeyboardButton("Выполнено", callback_data="done"),
         InlineKeyboardButton("Отложить на сутки", callback_data="postpone_day")],
        [InlineKeyboardButton("Отложить на неделю", callback_data="postpone_week"),
         InlineKeyboardButton("Отменить задачу", callback_data="cancel")],
        [InlineKeyboardButton("Вернуться назад", callback_data="back")]
    ]
    markup = InlineKeyboardMarkup(buttons)

    text = f"\ud83d\udccb <b>{task['название задачи']}</b>\n\n<b>Описание:</b> {task['описание задачи']}"
    await query.edit_message_text(text=text, reply_markup=markup, parse_mode="HTML")


async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    task = context.chat_data.get('selected_task')
    if not task:
        return

    action = query.data

    if action == "done":
        update_task_status(task['id'], "выполнено")
    elif action == "postpone_day":
        update_task_date(task['id'], days=1)
    elif action == "postpone_week":
        update_task_date(task['id'], days=7)
    elif action == "cancel":
        update_task_status(task['id'], "отменено")
    elif action == "back":
        await send_tasks(context)
        return

    await query.edit_message_text(text="Задача обновлена.")

    context.chat_data.pop('selected_task', None)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(task_menu, pattern=r'^task_'))
    app.add_handler(CallbackQueryHandler(handle_action, pattern=r'^(done|postpone_day|postpone_week|cancel|back)$'))

    # Планировщик
    job_queue = app.job_queue
    job_queue.run_daily(send_tasks, time=datetime.strptime(f"{CHECK_HOUR}:00", "%H:%M").time())

    app.run_polling()


if __name__ == "__main__":
    main()
