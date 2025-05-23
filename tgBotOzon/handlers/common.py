# import os, sys
# os.chdir( os.path.abspath( os.path.dirname( os.path.dirname(__file__) ) ) )
# sys.path.append( os.getcwd() )

from utils import getEnv, dictByKeys, getListFiles
import database
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
    Message
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

CONV_END = ConversationHandler.END
END, BEGIN, BACK, PREV, NEXT, MESS_ITER = ["sys"+r for r in map(str,range(6))]
CATEGORY, BOOK, TXTLINK, IMAGE, OTHER = ["cat"+r for r in map(str,range(5))]
NO_BOOK = "В списке пока нет книг"

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

## Итератор
class MessageIter:
    """Итератор для сообщений, позволяет инлайн смену сообщений, вперед и назад"""
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

    def restart(self):
        self.count = None
        self.revers = False
        return self.__next__()

    def __len__(self):
        return len(self.data)
    
    def __list__(self):
        return self.data

# async?
def iterMsg(update: Update, context: ContextTypes.DEFAULT_TYPE, listMsg: list) -> str:
    """Создание экземпляра итератора сообщения, а так же работа с ним.\n
    Хранится только один экземпляр, перезаписывается. \n
    Если нет итератора в user_data - создается.\n
    Если callback_query пуст, или отличается от последнего - создается.\n
    Если callback_query PREV/NEXT - итеририуется.\n
    Счетчик страниц с отображение добавлен в конец сообщения
    """
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
        text = context.user_data[MESS_ITER].restart()

    len_msg = len(context.user_data[MESS_ITER])
    
    # добавляем количество страниц, n/N
    if text and len_msg > 1:
        iter_count = context.user_data[MESS_ITER].count
        count = f"{( (len_msg+iter_count) % len_msg )+1}/{len_msg}"
        return f'{text}{" "*30}{count}'
    return text

## Conversation
def myConvHandler(input_pattern, state, callback, forKeyboard: str = 'both') -> ConversationHandler:
    """
    input_pattern - он и есть entry_points для ConversationHandler;\n
    state - обычно state категории: статус, возвращаемой входной и обрабатываемой функцией, и при завершении диалога;\n
    callback - вызываемая функция;\n
    forKeyboard: может быть str['inline'|'reply'|'both'].\n
    Используй декораторы: 
    @decConv(_parent_func_) для целевой функции и 
    @decConvParent для функции родителя
    """
    # Устарело, но если проблемы будут с декоратором, то:
    # state - статус, возвращаемой входной и обрабатываемой функцией, так же возращает в него при завершении диалога;\n
    # callback - обрабатываемая функция, не забывать добавлять в неё  CONV_END
    # Рекомендую: из callback добавить условие (сразу после update.callback_query.answer):
    #     'if update.callback_query.data == BACK:
    #         return await _parent_func_(update, context)' 
    # и в _parent_func_ добавить (сразу после update.callback_query.answer и сообщения):
    #     'if update.callback_query.data == BACK:
    #         return CONV_END'
    state_handlers = []
    fallback_handlers = [CallbackQueryHandler(callback, pattern=f"^{BACK}$")]
    # если вдруг после первого вызова повторное не получится вызвать, добавь в паттерн выше еще и input_pattern, для диагностики
    if forKeyboard == 'both' or forKeyboard == 'reply':
        state_handlers.append(MessageHandler(filters.Regex(r'^\d+'), callback))
        state_handlers.append(MessageHandler(filters.Regex(f'^{NO_BOOK}$'), callback))
        fallback_handlers.append(MessageHandler(None, callback))
    if forKeyboard == 'both' or forKeyboard == 'inline':
        state_handlers.append(CallbackQueryHandler(callback, pattern=f"^{PREV}|{NEXT}$"))

    list_conv_hadler = ConversationHandler(
        entry_points = [CallbackQueryHandler(callback, pattern=f"^{input_pattern}$")],
        states = {state: state_handlers},
        fallbacks = fallback_handlers,
        allow_reentry = True,
        map_to_parent= {CONV_END: state}
        )
    return list_conv_hadler

def decConv(parent_func):
    """Декоратор функции, исполняемой в myConvHandler, требует указание родительской функции. Для завершения ConversationHandler"""
    def decorator(func):
        async def wrapper(update, context):
            if update.callback_query:
                if update.callback_query.data == BACK and context.user_data.get('Conversation'):
                    # print("! in decConv")
                    return await parent_func(update, context) 
                context.user_data['Conversation'] = True
            return await func(update, context)
        return wrapper
    return decorator

def decConvParent(func):
    """Декоратор родительской функции, исполняемой в myConvHandler. Для завершения ConversationHandler"""
    async def wrapper(update, context):
        if update.callback_query:
            if update.callback_query.data == BACK and context.user_data.get('Conversation'):
                # print("! in decConvParent")
                await func(update, context)
                #секция для удаления reply клавиатуры
                if context.user_data.get("keyboardMessages"):
                    await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                                      message_id=context.user_data.get("keyboardMessages")[0])
                    del context.user_data["keyboardMessages"]
                if context.user_data.get('toDelete'):
                    del context.user_data['toDelete']

                if context.user_data.get(MESS_ITER):
                    del context.user_data[MESS_ITER]
                context.user_data['Conversation'] = False
                return CONV_END
        return await func(update, context)
    return wrapper


## Списки и сообщения/кнопки с ними
def booksList(to_button = False) -> list[str|list]:
    """Получам список книг из БД, преобразуем в list[str] или list[list[str]] для reply кнопок."""
    data = database.getAllBooks(short=True)
    books = []
    for item in data[:]:
        item = f"{item.get("id")}. {item.get("author")}. {item.get("title")}"
        if "None. " in item:
            item = item.replace("None. ", "")
        books.append(item)
    # books = [] # тест пустого списка
    if books == []:
        books.append(NO_BOOK)
    if to_button and books[0] != NO_BOOK:
        # books.insert(0, '0. Назад')
        books = [[b] for b in books]
    return books

def lastPricesList(book_id: int = None) -> list[str]:
    """Получам список цен последнего парсинга из БД. Может вернуть одну конкретную книгу по id."""
    # TODO - дата в каждом сообщении?
    data = database.getLastPrices(book_id)
    if data == []:
        return [f"По книге c id {book_id} еще не было результатов"]
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
        """Преобразует список любых строк, в список строк не более определенной длины"""
        messages = []
        text = ""
        for item in data:
            if len(text+item) > 4095 or len(text+item) > maxlenght or (text+item).count("\n") > maxline:
                messages.append(text)
                while len(item) > 4095:
                    messages.append(item[0:4090]+"...")
                    item = item[4090:]
                text = item+sep
            else:
                text += item+sep
        messages.append(text)
        return messages
        
async def book_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int|None:
    """Добавляем клавиатуру со списком книг. При выборе пользователя возвращает id"""
    if update.callback_query and not context.user_data.get("keyboardMessages"):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Ok, давай получим список книг", 
                                                    reply_markup=None)
        bookButtons = booksList(to_button=True)
        if len(bookButtons) <= 1 and bookButtons[0][0] == NO_BOOK:
            await update.callback_query.edit_message_text(NO_BOOK, 
                            reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]) )
        else:
            await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                                message_id=update.effective_message.id)
            # добавить в user_data и удалять при следующем шаге? или просто отмену 
            mes1 =  await context.bot.send_message(chat_id=update.effective_chat.id, 
                                            text="Выберете книгу в меню или введите ID", 
                                            reply_markup=ReplyKeyboardMarkup(bookButtons))
            mes2 = await context.bot.send_message(chat_id=update.effective_chat.id,
                                                text="Ваш выбор?",
                                                reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]) )
            context.user_data["keyboardMessages"] = [mes1.id, mes2.id]
        return None
    
    if update.message and context.user_data.get("keyboardMessages"):
        id = update.message.text.split(". ")[0]
        if not id.isdigit() or not database.getBookTitle(id):
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.id)
            mes = await context.bot.send_message(chat_id=update.effective_chat.id, 
                    text="По указанным данным не найдена книга. Пожалуйста, выберите книгу из списка",
                    reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]) )
            if context.user_data.get("keyboardMessages"):
                await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                                 message_id=context.user_data.get("keyboardMessages").pop(-1) )
                context.user_data.get("keyboardMessages").append(mes.id) 
        else:
            if context.user_data.get("keyboardMessages"):
                await context.bot.delete_messages(chat_id=update.effective_chat.id, message_ids=context.user_data.get("keyboardMessages"))
                del context.user_data["keyboardMessages"]
            return id 
    return None

if __name__ == '__main__':
    pass