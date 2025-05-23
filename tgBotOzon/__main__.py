from .common import (
        getEnv, logging, 
        ApplicationBuilder,
        # Update, ContextTypes,
                        )

from . import handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)


# async def ext(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     import sys
#     sys.exit()

def run():
    # Создание "приложения", обертка для api по сути
    application = ApplicationBuilder().token(getEnv('TG_TOKEN')).build()

    # Добавление хандлеров в приложение
    application.add_handler(handlers.start_conv_handler)
    # application.add_handler(CommandHandler('exit', ext))

    # Запуск приложения
    application.run_polling()

if __name__ == '__main__':
    run()