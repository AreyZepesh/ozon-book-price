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

from . import c_Book
from . import c_TxtLink
from . import c_Image
from . import c_Other

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        print(update.callback_query.data)
    cat_keys = [
        [InlineKeyboardButton('Книги в базе', callback_data=BOOK)], 
        [InlineKeyboardButton('Ссылки и цены', callback_data=TXTLINK)],
        [InlineKeyboardButton('Таблицы и графики', callback_data=IMAGE)],
        [InlineKeyboardButton('Разное', callback_data=OTHER)],
        [buttons.get(END)]
        ]
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text="Выбери категорию действий", reply_markup=InlineKeyboardMarkup(cat_keys))
    else:
        await update.message.reply_text(text="Выбери категорию действий", reply_markup=InlineKeyboardMarkup(cat_keys))
    return CATEGORY

## SYS
async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        if context.user_data.get("keyboardMessages"):
            await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                    message_id=context.user_data.get("keyboardMessages")[0])
        for x in list(context.user_data.keys()):
            del context.user_data[x] 
        await update.callback_query.edit_message_text("Полный конец обеда. Впиливаешь?", reply_markup=None)
        await asyncio.sleep(5)
        await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                    message_id=update.effective_message.id)
    return CONV_END

async def ext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sys.exit()

# Создание "приложения", обертка для api по сути
application = ApplicationBuilder().token(getEnv('TG_TOKEN')).build()

# Хандлеры, обрабатывают что то, выполняя функцию
start_handler = CommandHandler('start', start, filters=admins)

cat_callback = [
    CallbackQueryHandler(start, pattern=f"^{CATEGORY}$"),
    CallbackQueryHandler(c_Book.cat_book, pattern=f"^{BOOK}$"), 
    CallbackQueryHandler(c_TxtLink.cat_txtlint, pattern=f"^{TXTLINK}$"), 
    CallbackQueryHandler(c_Image.cat_image, pattern=f"^{IMAGE}$"), 
    CallbackQueryHandler(c_Other.cat_other, pattern=f"^{OTHER}$"),
    ]

start_conv_handler = ConversationHandler(
    entry_points = [start_handler],
    states = {
        CATEGORY: cat_callback, 
        BOOK: c_Book.book_callback,
        TXTLINK: c_TxtLink.txtlink_callback,
        IMAGE: c_Image.image_callback, 
        # OTHER: c_Other.other_callback,
        },
    fallbacks = [
        CallbackQueryHandler(end, pattern=f"^{END}$"), 
        CallbackQueryHandler(start, pattern=f"^{BEGIN}$"),
        start_handler
        ],
    allow_reentry=True
    )

def run():
    # ограничение пользователей
    admins.add_user_ids(794933751)
    
    # Добавление хандлеров в приложение
    application.add_handler(CommandHandler('exit', ext))
    application.add_handler(start_conv_handler)
    application.run_polling()

if __name__ == '__main__':
    pass