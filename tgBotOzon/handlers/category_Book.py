
from .common import (
        dictByKeys, getListFiles, normalizeStr,
        database, logging, asyncio,
        Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, 
        InlineKeyboardButton, InputMediaPhoto, InputMediaDocument, ParseMode,
        Message, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler,
        ConversationHandler, CallbackQueryHandler, filters, 
        buttons, 
        CONV_END, END, BEGIN, BACK, PREV, NEXT, MESS_ITER, 
        CATEGORY, BOOK, TXTLINK, IMAGE, OTHER, 
        NO_BOOK, 
        MessageIter, iterMsg, myConvHandler, decConv, decConvParent, booksList, 
        lastPricesList, lstToMessage, book_buttons   
                    )

@decConvParent
async def cat_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # print(update.callback_query.data)
    book_keys = [
        [InlineKeyboardButton("Cписок книг", callback_data=BOOK_LIST)],
        [InlineKeyboardButton("Добавить книгу", callback_data=ADD_BOOK)],
        [InlineKeyboardButton("Удалить книгу", callback_data=DEL_BOOK)],
        # [InlineKeyboardButton("Добавить isbn к книге", callback_data=ADD_ISBN)],
        # [InlineKeyboardButton("Удалить isbn у книги", callback_data=DEL_ISBN)],
        # [InlineKeyboardButton("Добавить артикль к книге", callback_data=ADD_ARTICLE)],
        # [InlineKeyboardButton("Удалить артикль у книги", callback_data=DEL_ARTICLE)],
        # [InlineKeyboardButton("Множественное добавление (CSV)", callback_data=B_CSV)],
        buttons.get(BEGIN+END)
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Действия c книгами", reply_markup=InlineKeyboardMarkup(book_keys))
    return BOOK

@decConv(cat_book)
async def book_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # print(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"Ищу данные", reply_markup=None)
    bookButtons = booksList()
    if len(bookButtons) <= 1 and bookButtons[0] == NO_BOOK:
        await update.callback_query.edit_message_text(NO_BOOK, reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
    else:
        text = iterMsg( update, context, lstToMessage(bookButtons, maxlenght=750, maxline=20) )
        await update.callback_query.edit_message_text(text = text,
                parse_mode=ParseMode.HTML, disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([buttons.get(PREV+NEXT), buttons.get(BACK+END)]))
    return BOOK

#Вспомогательные функции для добавления/редактирования книг
def build_text(book: dict) -> str:
    """Возвращает текст "карточки" текущей книги"""
    text = ""
    for k, v in FIELDS.items():
        text += f"\n{v}: {book.get(k) or ""}"

    return text.strip()

def build_keyboard(save=False) -> InlineKeyboardMarkup:
    """Возвращает inline клавиатуру"""
    keyboard = [InlineKeyboardButton(text = v, callback_data=f'edit_{k}') for k,v in FIELDS.items()]
    
    len_keyboard = len(keyboard)
    if len_keyboard%2 == 0:
        keyboard = [[keyboard[r], keyboard[r+1]] for r in range(0, len_keyboard,2)]
    else:
        keyboard_temp = keyboard.pop(-1)
        keyboard = [[keyboard[r], keyboard[r+1]] for r in range(0, len_keyboard-1,2)]
        keyboard.append([keyboard_temp])
        
    if save:
        keyboard.append([InlineKeyboardButton("Сохранить", callback_data=B_SAVE)])
    keyboard.append(buttons.get(BACK+END) )
    return InlineKeyboardMarkup(keyboard)
 
@decConv(cat_book)
async def add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("Book"):
        context.user_data["Book"] = {k: None for k in FIELDS.keys()}
    
    if context.user_data.get('keyboardMessages'):
        await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                            message_id=context.user_data['keyboardMessages'][0])
        del context.user_data['keyboardMessages']

    await update.callback_query.answer()
    mes = await update.callback_query.edit_message_text(
        text = build_text(context.user_data.get("Book")),
        reply_markup = build_keyboard(context.user_data.get("Book").get("title")),
        )

    context.user_data['toDelete'] = mes.id
    return BOOK

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data

    keyboard = [local_back_button]

    # await context.bot.delete_messages(chat_id=update.effective_chat.id, 
    #                                  message_ids=context.user_data['toDelete'])
    # context.user_data['toDelete'] = []
    
    if "edit_" in data:
        field = data.replace("edit_", "")
        context.user_data['edit_field'] = field
        if HELPS.get(field):
            keyboard.insert(0, [InlineKeyboardButton("Справка по вводу", callback_data=B_HELP)])
            

    #<TEXT>
    text = f"Введите новое значение для поля: <b>{FIELDS.get(context.user_data.get('edit_field'))}</b>\n"

    if context.user_data.get('edit_field') == "options": 
        text = "Или введите вручную. (Только для опытных пользователей, читайте справку по вводу)"
        mes_opt = await context.bot.send_message(chat_id=update.effective_chat.id, 
                        text="Выберите из готовых вариантов ниже\n",
                        parse_mode=ParseMode.HTML, 
                        reply_markup=ReplyKeyboardMarkup([[v] for v in BOOK_OPTIONS.values()])
                                                    )

        context.user_data['keyboardMessages'] = [mes_opt.id]

    if data == B_HELP:
        text += '\n'
        text += HELPS.get(context.user_data.get('edit_field')) or ""
    #</TEXT>

    if data == B_SAVE:
        print(context.user_data.get("Book"))
        text = "Добавлено в базу!"
        keyboard = [buttons.get(BACK+END)]
        del context.user_data["Book"]
        pass

    message_kwargs = {'chat_id': update.effective_chat.id,
                        'text': text, 
                        'parse_mode': ParseMode.HTML, 
                        'reply_markup': InlineKeyboardMarkup(keyboard)}

    if context.user_data.get('keyboardMessages'):
        await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                            message_id=context.user_data['toDelete'])
        mes = await context.bot.send_message(**message_kwargs)
        context.user_data['toDelete'] = mes.id
    else:
        await context.bot.edit_message_text(message_id = context.user_data['toDelete'],
                                            **message_kwargs)    

    return BOOK

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка введенных руками в чат сообщений"""
    field = context.user_data.get('edit_field')
    value = normalizeStr(update.message.text)
    if field in ['year_start', 'year_end']:
        try:
            value = int(value)
        except ValueError:
            await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                            message_id=update.effective_message.id)
            await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                                message_id=context.user_data['toDelete'],
                                                text = "Пожалуйста, введите число.")
            return BOOK

    list_field = field in ["isbns", "articles", "options"]

    if context.user_data["Book"][field] and list_field:
        context.user_data["Book"][field] += f", {value}"
    else: 
        context.user_data["Book"][field] = value
    
    if list_field:
        text = f"Текущие данные:\n{context.user_data["Book"][field]}\n\n"
        text += "Введите дополнительные данные, либо нажмите 'Назад' для возврата в предыдущее меню"
        keyboard = InlineKeyboardMarkup([local_back_button])
    else:
        text = build_text(context.user_data["Book"])
        keyboard = build_keyboard(context.user_data.get("Book").get("title"))

    await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                            message_id=update.effective_message.id)
    await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                                message_id=context.user_data['toDelete'],
                                                text = "Обновлено!\n\n" + text, reply_markup=keyboard)

    return BOOK

@decConv(cat_book)
async def del_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password_to_del = "Exterminate"
    if not context.user_data.get('toDelete'):
        id = await book_buttons(update, context)
        if id:
            mes = await context.bot.send_message(chat_id=update.effective_chat.id, 
                text=f"Вы действиетельно хотите удалить книгу и связанные с ней данные из базы? Если да, то введите '{password_to_del}'", 
                reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
            context.user_data['toDelete'] = (id, mes.id)
    elif context.user_data.get('toDelete'):
        if update.message and update.message.text == password_to_del:
            book_id = context.user_data.get('toDelete')[0]
            title = database.getBookTitle(book_id)
            
            database.delBook(book_id)

            text = f"Книга {book_id}. {title} была стерта из базы!"
            await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                              message_id=update.effective_message.id)
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                              message_id=context.user_data.get("toDelete")[1],
                                              text = text, reply_markup=None)
            # print(text)
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "Что дальше?", 
                                                reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]) )
        elif update.message:
            await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                              message_id=update.effective_message.id)
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                              message_id=context.user_data.get("toDelete")[1],
                                              text = "Отмена операции удаления", 
                                              reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
        # del context.user_data['toDelete']
    return BOOK


BOOK_LIST, ADD_BOOK, DEL_BOOK, ADD_ISBN, DEL_ISBN, ADD_ARTICLE, DEL_ARTICLE, B_CSV = ["book"+r for r in map(str,range(8))]
B_HELP, B_SAVE =  ["b_book"+r for r in map(str,range(2))]

local_back_button = [InlineKeyboardButton('Назад', callback_data=ADD_BOOK)]

FIELDS = {
            'title': 'Название ', 
            'author': 'Автор', 
            'year_start': 'Год издания: с', 
            'year_end': 'Год издания: по', 
            'isbns': "ISBN's",
            'articles': 'Артикли OZON',
            'options': 'Дополнительные опции',
               }

BOOK_OPTIONS = {
    "onlyISBN": "Искать только по ISBN",
    "onlyArticle": "Искать только по артиклю OZON",
    "covertype=537": "Тип обложки: Твердый переплет",
    "publisher=855985": "Издательство: Азбука",
    "publisher=855962": "Издательство: АСТ",
    "publisher=4663491": "Издательство: Corpus",
    "publisher=857671": "Издательство: Эксмо",
    # "": "",
    # "": "",
    }

HELPS = {
        'title': (
            'Допустимы длинные названия, с точками и запятыми.'
            'Старайтесь брать названия с OZON или из описания книги с достоверных ресурсов.\n'
            'Если книга том или многотомник, можете указать (как на OZON) это после точки, для увеличения точности.\n'
            'Например:<i>\n'
            '"Граф Монте-Кристо. Комплект", \n'
            '"Граф Монте-Кристо. Том 1", \n'
            '"Сага о Фафхрде и Сером Мышелове. Книга 1".</i>\n\n'
            '<b><u>ВНИМАНИЕ</u></b>: По названию будет проводится фильтрация результатов поиска на озон.'
            'Будьте точны, но кратки. Избегайте не имеющих отношения к названию слов и символов'
                    ), 
        'author': (
            "Лучше указывать просто фамилию автора. Если больше одного автора, то укажите просто через пробел\n"
            "Можно с именем, и даже отчеством, но это уменьшает количество результатов поиска.\n"
            "При фильтрации результатов поиска не используется, "
            "поэтому в результат могут попасть одноименные книги другого автора. "
            "Так же, поэтому можно использовать и не только автора. "
            "Например, в одной из книг у разработчика стоит название цикла: <i>'Наша старая добрая фантастика'</i>. "
            "Это редко, но случается"
                    ),
        'year_start': (
            "Год, с которого начали издаваться издания книги.\n"
            "Например, чтобы отсеять издания советской эпохи"
                    ), 
        'year_end': (
            "Год, ДО которого начали издаваться издания книги.\n"
            "Например, чтобы отсеять новые редакции.\n"
            "<b><u>ВНИМАНИЕ</u></b>:Работает только при указанном параметре <u>'Год издания: с'</u>"
                    ), 
        'isbns': (
            'ISBN издания книги, нужен для более точного поиска конкретного издания.\n'
            'Отдельно, в дополнительных опциях, можно указать поиск <u>только</u> по этому параметру.\n'
            '<b>Если больше одного - указывайте через запятую, точку, с новой строки или в новом сообщении.</b>\n'
            'Старайтесь брать ISBN из достоверных источников, например с сайта издательства книги, '
            'или с <a href="https://fantlab.ru/">Фантлаба</a>'
                    ),
        'articles': (
            'Артикль карточки книги на OZON, нужен для отслеживания конкретного товара.\n'
            'Отдельно, в дополнительных опциях, можно указать поиск <u>только</u> по этому параметру.\n'
            '<b>Если больше одного - указывайте через запятую, точку, с новой строки или в новом сообщении.</b>\n'
            'Берите только с сайта или из приложения OZON'
                    ),
        'options': (
            # "Дополнительные опции.  ""
            # ""
                    ),
        }

book_card_handler = [CallbackQueryHandler(handle_button, pattern=f"^edit_{k}$") for k in FIELDS.keys()]

book_callback = [
    myConvHandler(BOOK_LIST, BOOK, book_list, forKeyboard = 'inline'),

    myConvHandler(ADD_BOOK, BOOK, add_book, 
        state_handlers= book_card_handler + [
            CallbackQueryHandler(handle_button, pattern=f"^{B_HELP}$"),
            CallbackQueryHandler(handle_button, pattern=f"^{B_SAVE}$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input),
            ],
                ),

    myConvHandler(DEL_BOOK, BOOK, del_book, forKeyboard = 'reply'),
    CallbackQueryHandler(cat_book, pattern=f"^{BACK}$"), 
    ]

if __name__ == '__main__':
    pass