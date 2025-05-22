from .common import (
        # database, dictByKeys, 
        getEnv, getListFiles, sys, logging, asyncio,
        Update, InlineKeyboardMarkup, 
        # ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaDocument, 
        InlineKeyboardButton, InputMediaPhoto, ParseMode,
        ApplicationBuilder, ContextTypes, CommandHandler,
        ConversationHandler, CallbackQueryHandler,
        # Message, MessageHandler, filters, 
        admins, buttons, 
        CONV_END, END, BEGIN, BACK, PREV, NEXT,
        CATEGORY, BOOK, TXTLINK, IMAGE, OTHER,
        # BOOK_LIST, ADD_BOOK, DEL_BOOK, ADD_ISBN, 
        # DEL_ISBN, ADD_ARTICLE, DEL_ARTICLE, B_CSV, 
        TL_ALL, TL_ONE, IM_TAB, 
        IM_UNION_GR, IM_ONE_GR, IM_ALL_GR, 
        # NO_BOOK, MessageIter, booksList, MESS_ITER, 
        iterMsg, myConvHandler, decConv, decConvParent, 
        lastPricesList, lstToMessage, book_buttons    
                        )

# from . import c_main
from . import handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)


# async def ext(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    pass