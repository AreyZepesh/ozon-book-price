from utils import getEnv, dictByKeys
from database import getAllBooks, getLastPrices
import asyncio
import logging
from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
    InlineKeyboardMarkup, 
    InlineKeyboardButton
    )
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
    )


TG_TOKEN = getEnv('TG_TOKEN')

CONV_END = ConversationHandler.END
BACK, END = range(-2, 0)
CATEGORY, BOOK, TXTLINK, IMAGE, OTHER = ["cat"+r for r in map(str,range(5))]
BOOK_LIST, ADD_BOOK, DEL_BOOK, ADD_ISBN, DEL_ISBN, ADD_ARTICLE, DEL_ARTICLE, B_CSV = ["book"+r for r in map(str,range(8))]
TL_ALL, TL_ONE = ["tl"+r for r in map(str,range(2))]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# обе - слегка порно?, в utils?
def booksList() -> list[str]:
    data = getAllBooks()
    books = []
    for item in data[:]:
        item = f"{item.get("id")}. {item.get("author")}. {item.get("title")}"
        if "None. " in item:
            item = item.replace("None. ", "")
        books.append([item])

    return books

def lastPricesList(book_id: int = None) -> list[str]:
    data = getLastPrices(book_id)
    prices = [[f"Дата поиска: {data[0].get('datetime')}\n"]]
    data = dictByKeys(data, "book_id")
    for dicts in data.values():
        text = f"{dicts[0].get('book_id')}. {dicts[0].get('author')}. {dicts[0].get('title')}\n"
        if "None. " in text:
            text = text.replace("None. ", "")
        for item in dicts:
            text += (f"Цена: {item.get('price')}, Тип поиска: {item.get('typeSearch')}\n"
                    f"https://ozon.kz/product/{item.get('article')} \n")
        prices.append([text])
    return prices

def lstToMessage(data: list[list[str]], sep: str = "\n") -> list[str]:
        messages = []
        text = ""
        for book in data:
            if len(text+book[0]) > 4095:
                messages.append(text)
                text = book[0]+sep
            else:
                text += book[0]+sep
        messages.append(text)
        return messages
        

# Реакция на /start в боте
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat_keys = [
        [InlineKeyboardButton('Книги в базе', callback_data=BOOK)], 
        [InlineKeyboardButton('Ссылки и цены', callback_data=TXTLINK)],
        [InlineKeyboardButton('Таблицы и графики', callback_data=IMAGE)],
        [InlineKeyboardButton('Разное', callback_data=OTHER)],
        [endButton]
        ]
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text="Выбери категорию действий", reply_markup=InlineKeyboardMarkup(cat_keys))
    else:
        await update.message.reply_text(text="Выбери категорию действий", reply_markup=InlineKeyboardMarkup(cat_keys))
    return CATEGORY

async def cat_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    book_keys = [
        [InlineKeyboardButton("Cписок книг", callback_data=BOOK_LIST)],
        [InlineKeyboardButton("Добавить книгу", callback_data=ADD_BOOK)],
        [InlineKeyboardButton("Удалить книгу", callback_data=DEL_BOOK)],
        [InlineKeyboardButton("Добавить isbn к книге", callback_data=ADD_ISBN)],
        [InlineKeyboardButton("Удалить isbn у книги", callback_data=DEL_ISBN)],
        [InlineKeyboardButton("Добавить артикль к книге", callback_data=ADD_ARTICLE)],
        [InlineKeyboardButton("Удалить артикль у книги", callback_data=DEL_ARTICLE)],
        [InlineKeyboardButton("Множественное добавление (CSV)", callback_data=B_CSV)],
        bottomButtons
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Действия c книгами", reply_markup=InlineKeyboardMarkup(book_keys))
    return BOOK


async def book_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"Ищу данные", reply_markup=None)
    for book in lstToMessage(booksList()):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=book)
    # Построчный вариант - медленно
    # for book in booksList():
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=book[0])
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Это весь список", reply_markup=InlineKeyboardMarkup([bottomButtons]))
    # Вариант с выводом списка, как меню-клавиатура. Если работать с этим вариаентом не забыть удалить клаву и обработчик по id ("^\d+\.") 
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Вывел список в меню", reply_markup=ReplyKeyboardMarkup(booksList()))
    return BOOK


async def add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"Выбрано действие с книгой: {update.callback_query.data}", 
                                                  reply_markup=InlineKeyboardMarkup([bottomButtons]))
    return BOOK

async def cat_txtlint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    txtlint_keys= [
        [InlineKeyboardButton("Получить данные по книге", callback_data=TL_ONE)],
        [InlineKeyboardButton("Получить данные по всем книгам", callback_data=TL_ALL)],
        bottomButtons
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Получения данных по последнему парсингу.\nВыдаст название книги, дату парсинга, цены и ссылки на товар с этой ценой", 
                                                  reply_markup=InlineKeyboardMarkup(txtlint_keys))
    return TXTLINK

async def txtlint_one(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Ok, давай получим список книг", 
                                                  reply_markup=None)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вывел список в меню", reply_markup=ReplyKeyboardMarkup(booksList()))
    
    # TODO
    return CONV_END

async def txtlint_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Грузим список сообщений", 
                                                  reply_markup=None)
    # TODO
    for msg in lstToMessage(lastPricesList()):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    return CONV_END

async def cat_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    image_keys = [
        [InlineKeyboardButton("Таблицы с последними ценами", callback_data=str(CATEGORY))],
        [InlineKeyboardButton("Общий график всё время", callback_data=str(CATEGORY))],
        [InlineKeyboardButton("График цен на книгу", callback_data=str(CATEGORY))],
        [InlineKeyboardButton("Графики цен на ВСЕ книг", callback_data=str(CATEGORY))],
        bottomButtons
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Действия c таблицами и графиками", reply_markup=InlineKeyboardMarkup(image_keys))
    return CATEGORY

async def cat_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    other_keys = [
        [InlineKeyboardButton("TODO", callback_data=str(CATEGORY))],
        bottomButtons
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Действия c", reply_markup=InlineKeyboardMarkup(other_keys))
    return CATEGORY

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Конец?", reply_markup=None)
    return CONV_END


if __name__ == '__main__':
    g_books = getAllBooks(short=True)
    g_books = [[". ".join( map( str, b.values() ) )] for b in g_books]
    # print(g_books)
    # books_markup = ReplyKeyboardMarkup(books)

    # ограничение пользователей
    admins = filters.User()
    admins.add_user_ids(794933751)
    
    
    endButton = InlineKeyboardButton("Закончить", callback_data=END)
    backButton = InlineKeyboardButton('Назад', callback_data=BACK)
    bottomButtons = [backButton, endButton]

    # Создание "приложения", обертка для api по сути
    application = ApplicationBuilder().token(TG_TOKEN).build()
    
    # Хандлеры, обрабатывают что то, выполняя функцию
    start_handler = CommandHandler('start', start, filters=admins)

    cat_callback = [
        CallbackQueryHandler(start, pattern=f"^{CATEGORY}$"),
        CallbackQueryHandler(cat_book, pattern=f"^{BOOK}$"), 
        CallbackQueryHandler(cat_image, pattern=f"^{IMAGE}$"), 
        CallbackQueryHandler(cat_txtlint, pattern=f"^{TXTLINK}$"), 
        CallbackQueryHandler(cat_other, pattern=f"^{OTHER}$"),
        ]

    book_callback = [
        CallbackQueryHandler(book_list, pattern=f"^{BOOK_LIST}$"),
        CallbackQueryHandler(add_book, pattern=f"^{ADD_BOOK}$"),
        CallbackQueryHandler(add_book, pattern=f"^{DEL_BOOK}$"),
        CallbackQueryHandler(add_book, pattern=f"^{ADD_ISBN}$"),
        CallbackQueryHandler(add_book, pattern=f"^{DEL_ISBN}$"),
        CallbackQueryHandler(add_book, pattern=f"^{ADD_ARTICLE}$"),
        CallbackQueryHandler(add_book, pattern=f"^{DEL_ARTICLE}$"),
        CallbackQueryHandler(add_book, pattern=f"^{B_CSV}$"),
        #  CallbackQueryHandler(cat_book, pattern=f"^{BACK}$"), 
        ]
    
    txtlink_callback = [
        CallbackQueryHandler(txtlint_one, pattern=f"^{TL_ONE}$"),
        CallbackQueryHandler(txtlint_all, pattern=f"^{TL_ALL}$"),
        ]
    # cat_states = 
            # BOOK: [CallbackQueryHandler(cat_book, pattern="^" + str(BOOK) + "$")], 
            # IMAGE: [CallbackQueryHandler(cat_image, pattern="^" + str(IMAGE) + "$")], 
            # TXTLINK: [CallbackQueryHandler(cat_txtlint, pattern="^" + str(TXTLINK) + "$")], 
            # OTHER: [CallbackQueryHandler(cat_other)],
            # END: [CallbackQueryHandler(end, pattern="^" + str(END) + "$")]
    start_conv_handler = ConversationHandler(
        entry_points = [start_handler],
        states = {
            CATEGORY: cat_callback, 
            BOOK: book_callback,
            TXTLINK: txtlink_callback,
            },
        fallbacks = [
            CallbackQueryHandler(end, pattern=f"^{END}$"), 
            CallbackQueryHandler(start, pattern=f"^{BACK}$")
            ]
        )

    # Добавление хандлеров в приложение
    # application.add_handler(start_handler)
    application.add_handler(start_conv_handler)
    application.run_polling()

