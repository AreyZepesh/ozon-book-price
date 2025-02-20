from utils import getEnv
# import logging
import asyncio
from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    KeyboardButton
    )
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler,
    filters,
    CallbackQueryHandler,
    MessageHandler,
    )


TG_TOKEN = getEnv('TG_TOKEN')

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# Реакция на /start в боте
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text)
    if update.effective_user.id not in admins.user_ids:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{update.effective_user.name}, Вы не админ этого бота")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ты молодец", reply_markup=reply_markup)
        # await update.message.reply_text(chat_id=update.effective_chat.id, text=f"Ты молодец", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text)


if __name__ == '__main__':
    # ограничение пользователей
    admins = filters.User()
    admins.add_user_ids(794933751)
    
    keyboard = [[ KeyboardButton('1-1'), KeyboardButton('1-2')],
                [KeyboardButton('2-1')],
                ['3-1','3-2','3-3']]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    
    # Создание "приложения", обертка для api по сути
    application = ApplicationBuilder().token(TG_TOKEN).build()
    
    # Хандлеры, обрабатывают что то, выполняя функцию
    start_handler = CommandHandler('start', start)
    

    # Добавление хандлеров в приложение
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.Regex(r'.*'), button))
    application.run_polling()

