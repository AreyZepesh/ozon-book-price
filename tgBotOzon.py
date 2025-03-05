from utils import getEnv, dictByKeys, getListFiles
from database import getAllBooks, getLastPrices
import asyncio
import logging
import telegram
from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    InputMediaPhoto,
    InputMediaDocument,
    )
from telegram.constants import ParseMode
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
END, BEGIN, BACK, PREV, NEXT, MESS_ITER = ["sys"+r for r in map(str,range(6))]
CATEGORY, BOOK, TXTLINK, IMAGE, OTHER = ["cat"+r for r in map(str,range(5))]
BOOK_LIST, ADD_BOOK, DEL_BOOK, ADD_ISBN, DEL_ISBN, ADD_ARTICLE, DEL_ARTICLE, B_CSV = ["book"+r for r in map(str,range(8))]
TL_ALL, TL_ONE = ["textlink"+r for r in map(str,range(2))]
IM_TAB, IM_UNION_GR, IM_ONE_GR, IM_ALL_GR = ["image"+r for r in map(str,range(4))]
NO_BOOK = "В списке пока нет книг"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# итератор для сообщений, чтобы можно было делать инлайн смену сообщений, вперед и назад
class MessageIter:
    def __init__(self, data: list) -> None:
        self.data = data
        self.count = None
        self.revers = False

    def __iter__(self):
        for d in self.data:
            yield d 
    
    def __next__(self):
        if self.count is None:
            self.count = 0
            return self.data[self.count]

        if self.revers:
            self.count -= 1
        else:
            self.count += 1
        
        if abs(self.count) >= len(self.data):
            self.count = 0

        return self.data[self.count]
    
    def get_next(self):
        self.revers = False
        return self.__next__()
    
    def get_prev(self):
        self.revers = True
        return self.__next__()
    
    def __len__(self):
        return len(self.data)
    
    def __list__(self):
        return self.data
    
def listHandler(entry_points, state, callback) -> ConversationHandler:
    """entry_points - он и есть entry_points для ConversationHandler;\n
      state - статус, возвращаемой входной и обрабатываемой функцией, так же возращает в него при завершении диалога;\n
      callback - обрабатываемая функция, не забывать добавлять в неё CONV_END"""
    list_conv_hadler = ConversationHandler(
        entry_points = [entry_points],
        states = {state: [
                MessageHandler(filters.Regex(r'^\d+'), callback),
                MessageHandler(filters.Regex(r'^В списке пока нет книг$'), callback),
                    ],},
        fallbacks = [CallbackQueryHandler(callback), MessageHandler(None, callback)],
        map_to_parent= {CONV_END: state}
        )
    return list_conv_hadler

#  обе - слегка порно?, в utils?
def booksList(to_button = False) -> list[str]:
    data = getAllBooks(short=True)
    books = []
    for item in data[:]:
        item = f"{item.get("id")}. {item.get("author")}. {item.get("title")}"
        if "None. " in item:
            item = item.replace("None. ", "")
        if to_button:
            item = [item]
        books.append(item)
    # books = [] # тест пустого списка
    if books == []:
        item = NO_BOOK
        if to_button:
            item = [item]
        books.append(item)
    return books

def lastPricesList(book_id: int = None) -> list[str]:
    # TODO - группировать одинаковые артикли результата
    # TODO - дата в каждом сообщении?
    data = getLastPrices(book_id)
    if data == []:
        return ["По этой книге еще не было результатов"]
    prices = [f"Дата поиска: {data[0].get('datetime')}\n",]
    data = dictByKeys(data, "book_id")
    for dicts in data.values():
        text = f"{dicts[0].get('book_id')}. {dicts[0].get('author')}. {dicts[0].get('title')}\n"
        if "None. " in text:
            text = text.replace("None. ", "")
        for item in dicts:
            # text += (f"Цена: {item.get('price')}, Тип поиска: {item.get('typeSearch')}\n"
            #         f"https://ozon.kz/product/{item.get('article')} \n")
            text += (f"<a href='https://ozon.kz/product/{item.get("article")} '><b>"
                    f"Цена: {item.get('price')}</b>, Тип поиска: {item.get('typeSearch')}"
                    f"</a> \n")
        prices.append(text)
    return prices

def lstToMessage(data: list[str], maxlenght:int = 1000, maxline:int = 100, sep: str = "\n") -> list[str]:
        messages = []
        text = ""
        for book in data:
            if len(text+book) > 4095 or len(text+book) > maxlenght or (text+book).count("\n") > maxline:
                messages.append(text)
                text = book+sep
            else:
                text += book+sep
        messages.append(text)
        return messages
        
def iterMsg(update: Update, context: ContextTypes.DEFAULT_TYPE, listMsg: list) -> str:
    if not context.user_data.get("last_iter"):
        context.user_data["last_iter"] = update.callback_query.data
        ifQuery = True
    elif update.callback_query.data == PREV or update.callback_query.data == NEXT:
        ifQuery = False
    else:
        ifQuery = context.user_data["last_iter"] != update.callback_query.data
        
    if not context.user_data.get(MESS_ITER) or ifQuery:
        context.user_data[MESS_ITER] = MessageIter(listMsg)
        
    if update.callback_query.data == NEXT:
        text = context.user_data[MESS_ITER].get_next()
    elif update.callback_query.data == PREV:
        text = context.user_data[MESS_ITER].get_prev()
    else:
        text = context.user_data[MESS_ITER].get_next()

    len_msg = len(context.user_data[MESS_ITER])
    
    if text and len_msg > 1:
        iter_count = context.user_data[MESS_ITER].count
        count = f"{( (len_msg+iter_count) % len_msg )+1}/{len_msg}"
        return f'{text}{" "*30}{count}'
    return text
        
    

# Реакция на /start в боте
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if context.user_data.get(MESS_ITER):
    #     del context.user_data[MESS_ITER]
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

async def cat_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    # if context.user_data.get(MESS_ITER):
    #     del context.user_data[MESS_ITER]
    book_keys = [
        [InlineKeyboardButton("Cписок книг", callback_data=BOOK_LIST)],
        [InlineKeyboardButton("Добавить книгу", callback_data=ADD_BOOK)],
        [InlineKeyboardButton("Удалить книгу", callback_data=DEL_BOOK)],
        [InlineKeyboardButton("Добавить isbn к книге", callback_data=ADD_ISBN)],
        [InlineKeyboardButton("Удалить isbn у книги", callback_data=DEL_ISBN)],
        [InlineKeyboardButton("Добавить артикль к книге", callback_data=ADD_ARTICLE)],
        [InlineKeyboardButton("Удалить артикль у книги", callback_data=DEL_ARTICLE)],
        [InlineKeyboardButton("Множественное добавление (CSV)", callback_data=B_CSV)],
        buttons.get(BEGIN+END)
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Действия c книгами", reply_markup=InlineKeyboardMarkup(book_keys))
    return BOOK


async def book_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"Ищу данные", reply_markup=None)
    bookButtons = booksList()
    if len(bookButtons) <= 1 and bookButtons[0] == NO_BOOK:
        await update.callback_query.edit_message_text(NO_BOOK, reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
    else:
        text = iterMsg( update, context, lstToMessage(bookButtons, maxlenght=750, maxline=20) )
        await update.callback_query.edit_message_text(text = text,
                reply_markup=InlineKeyboardMarkup([buttons.get(PREV+NEXT), buttons.get(BACK+END)]))
    return BOOK


async def add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"Выбрано действие с книгой: {update.callback_query.data}", 
                                                  reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
    return BOOK

async def del_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"Выбрано действие с книгой: {update.callback_query.data}", 
                                                  reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
    return BOOK

async def cat_txtlint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    txtlint_keys= [
        [InlineKeyboardButton("Получить данные по книге", callback_data=TL_ONE)],
        [InlineKeyboardButton("Получить данные по всем книгам", callback_data=TL_ALL)],
        buttons.get(BEGIN+END)
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Выдаст данные по последнему парсингу: название книги, дату парсинга, цены и ссылки на товар с этой ценой", 
                                                  reply_markup=InlineKeyboardMarkup(txtlint_keys))
    # if context.user_data.get(MESS_ITER):
    #     print(f"Удаляем данные итератора, количество сообщенией: {len(context.user_data.get(MESS_ITER))}")
    #     del context.user_data[MESS_ITER]
    return TXTLINK


async def txtlint_one(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        print(update.callback_query.data)
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Ok, давай получим список книг", 
                                                    reply_markup=None)
        bookButtons = booksList(to_button=True)
        if len(bookButtons) <= 1 and bookButtons[0][0] == NO_BOOK:
            await update.callback_query.edit_message_text(NO_BOOK, reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
        else:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберете книгу в меню или введите ID", reply_markup=ReplyKeyboardMarkup(bookButtons))
    
        return TXTLINK
    
    if update.message:
        id = update.message.text.split(". ")[0]
        if not id.isdigit():
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, выберите книгу из списка")
            return TXTLINK
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=lstToMessage(lastPricesList(id))[0],
                                        parse_mode=ParseMode.HTML, disable_web_page_preview=True,
                                        reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Что дальше?", reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
        return CONV_END

async def txtlint_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()

    text = iterMsg( update, context, lstToMessage(lastPricesList()) ) #, TL_ALL)

    await update.callback_query.edit_message_text(text = text,
            parse_mode=ParseMode.HTML, disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([buttons.get(PREV+NEXT), buttons.get(BACK+END)]))
    # for msg in context.user_data[MESS_ITER]:
    #     await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, 
    #              parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    return TXTLINK

async def cat_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    image_keys = [
        [InlineKeyboardButton("Таблицы с последними ценами", callback_data=IM_TAB)],
        [InlineKeyboardButton("Общий график всё время", callback_data=IM_UNION_GR)],
        [InlineKeyboardButton("График цен на книгу", callback_data=IM_ONE_GR)],
        [InlineKeyboardButton("Графики цен на ВСЕ книг", callback_data=IM_ALL_GR)],
        buttons.get(BEGIN+END)
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Действия c таблицами и графиками", reply_markup=InlineKeyboardMarkup(image_keys))
    return IMAGE

async def image_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.id)
    # media = [InputMediaDocument(open(im, 'rb')) for im in getListFiles(0)]
    media = [InputMediaPhoto(open(im, 'rb')) for im in getListFiles(0)]
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media)
    # await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("./graphics/aBooksTable0.png", 'rb'), has_spoiler=True)
    # await context.bot.send_document(chat_id=update.effective_chat.id, document="./graphics/aBooksTable0.png")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вот фото, что дальше?", reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
    # await update.callback_query.edit_message_text("Что делать будем?", reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
    return IMAGE


async def cat_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    # if context.user_data.get(MESS_ITER):
    #     del context.user_data[MESS_ITER]
    other_keys = [
        [InlineKeyboardButton("TODO", callback_data=str(CATEGORY))],
        buttons.get(BEGIN+END)
        # bottomButtons
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Действия c", reply_markup=InlineKeyboardMarkup(other_keys))
    return CATEGORY

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get(MESS_ITER):
        del context.user_data[MESS_ITER]
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Конец диалога", reply_markup=None)
    return CONV_END

async def ext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import sys
    sys.exit()


if __name__ == '__main__':
    g_books = getAllBooks(short=True)
    g_books = [[". ".join( map( str, b.values() ) )] for b in g_books]
    # print(g_books)
    # books_markup = ReplyKeyboardMarkup(books)

    # ограничение пользователей
    admins = filters.User()
    admins.add_user_ids(794933751)
    
    buttons = {
        BACK: InlineKeyboardButton('Назад', callback_data=BACK),
        BEGIN: InlineKeyboardButton('В начало', callback_data=BEGIN),
        END: InlineKeyboardButton("Закончить", callback_data=END),
        PREV: InlineKeyboardButton('<<<', callback_data=PREV),
        NEXT: InlineKeyboardButton('>>>', callback_data=NEXT),
               }
    buttons[BEGIN+END] = [buttons.get(BEGIN), buttons.get(END)]
    buttons[BACK+END] = [buttons.get(BACK), buttons.get(END)]
    buttons[PREV+NEXT] = [buttons.get(PREV), buttons.get(NEXT)]

    # Создание "приложения", обертка для api по сути
    application = ApplicationBuilder().token(TG_TOKEN).build()
    
    # Хандлеры, обрабатывают что то, выполняя функцию
    start_handler = CommandHandler('start', start, filters=admins)

    cat_callback = [
        CallbackQueryHandler(start, pattern=f"^{CATEGORY}$"),
        CallbackQueryHandler(cat_book, pattern=f"^{BOOK}$"), 
        CallbackQueryHandler(cat_txtlint, pattern=f"^{TXTLINK}$"), 
        CallbackQueryHandler(cat_image, pattern=f"^{IMAGE}$"), 
        CallbackQueryHandler(cat_other, pattern=f"^{OTHER}$"),
        ]

    book_callback = [
        CallbackQueryHandler(book_list, pattern=f"^{BOOK_LIST}|{PREV}|{NEXT}$"),
        CallbackQueryHandler(add_book, pattern=f"^{ADD_BOOK}$"),
        CallbackQueryHandler(del_book, pattern=f"^{DEL_BOOK}$"),
        CallbackQueryHandler(add_book, pattern=f"^{ADD_ISBN}$"),
        CallbackQueryHandler(add_book, pattern=f"^{DEL_ISBN}$"),
        CallbackQueryHandler(add_book, pattern=f"^{ADD_ARTICLE}$"),
        CallbackQueryHandler(add_book, pattern=f"^{DEL_ARTICLE}$"),
        CallbackQueryHandler(add_book, pattern=f"^{B_CSV}$"),
        CallbackQueryHandler(cat_book, pattern=f"^{BACK}$"), 
        ]

    txtlink_callback = [
        listHandler(CallbackQueryHandler(txtlint_one, pattern=f"^{TL_ONE}$"), TXTLINK, txtlint_one),
        CallbackQueryHandler(txtlint_all, pattern=f"^{TL_ALL}|{PREV}|{NEXT}$"),
        CallbackQueryHandler(cat_txtlint, pattern=f"^{BACK}$"), 
        ]
    
    image_callback = [
        CallbackQueryHandler(image_table, pattern=f"^{IM_TAB}$"),
        CallbackQueryHandler(image_table, pattern=f"^{IM_UNION_GR}$"),
        CallbackQueryHandler(image_table, pattern=f"^{IM_ONE_GR}$"),
        CallbackQueryHandler(image_table, pattern=f"^{IM_ALL_GR}$"),
        CallbackQueryHandler(cat_image, pattern=f"^{BACK}$"), 
        ]


    start_conv_handler = ConversationHandler(
        entry_points = [start_handler],
        states = {
            CATEGORY: cat_callback, 
            BOOK: book_callback,
            TXTLINK: txtlink_callback,
            IMAGE: image_callback, 
            # OTHER: ,
            },
        fallbacks = [
            CallbackQueryHandler(end, pattern=f"^{END}$"), 
            CallbackQueryHandler(start, pattern=f"^{BEGIN}$"),
            start_handler
            ]
        )

    # Добавление хандлеров в приложение
    application.add_handler(CommandHandler('exit', ext))
    application.add_handler(start_conv_handler)
    application.run_polling()

