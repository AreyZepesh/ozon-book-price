
from .common import (
        dictByKeys, getListFiles, normalizeStr, strToLst,
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
#Вспомогательные функции для добавления/редактирования книг
def build_text(book: dict) -> str:
    """Возвращает текст "карточки" текущей книги"""
    # Генерируем на основе словаря FIELDS
    text = ""
    for k, v in FIELDS.items():
        # Для полей с несколькими значениями выводим кол-во значений
        if k in ["isbns", "articles", "options"]:
            str = f"указано {len(strToLst(book.get(k) or ""))}"
        # Либо само значение, если оно есть
        else:
            str = book.get(k) or ""
        text += f"\n{v}: {str}"

    text = text.replace("Год", "Год издания") 
    return text.strip()

def build_keyboard(save=False) -> InlineKeyboardMarkup:
    """Возвращает inline клавиатуру"""
    # Генерируем на основе словаря FIELDS
    keyboard = [InlineKeyboardButton(text = v, callback_data=f'edit_{k}') for k,v in FIELDS.items()]
    
    # Делаем по 2 в столбец, если не четное кол-во - последний большой кнопкой
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

#Основные функции
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

@decConv(cat_book)
async def add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получаем данные книги от пользователя, и сохраняем в базу данных"""
    # тестовые данные
    # context.user_data["Book"] = {'title': 'Камбер-еретик', 'author': 'Куртц', 'year_start': 1992, 'year_end': 2030, 'options': 'covertype=537, onlyISBN'}
    # context.user_data["Book"]["isbns"] = '5-17-006491-8, 5-93698-049-9, 5-17-006491-8'
    # context.user_data["Book"]["articles"] = "1, 2"

    # Если словаря для книги еще нет - формируем пустой
    if not context.user_data.get("Book"):
        context.user_data["Book"] = {k: None for k in FIELDS.keys()}
    
    # Очистка переменных, при нажатии локального "Назад"
    if context.user_data.get('keyboardMessages'):
        await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                            message_id=context.user_data['keyboardMessages'][0])
        del context.user_data['keyboardMessages']
    if context.user_data.get('edit_field'):
        del context.user_data['edit_field']

    # Обязательный ответ на инлайн нажатие, и выводим карточку и кнопки, сохраняем id сообщения
    await update.callback_query.answer()
    mes = await update.callback_query.edit_message_text(
        text = build_text(context.user_data.get("Book")),
        reply_markup = build_keyboard(context.user_data.get("Book").get("title")),
        )
    context.user_data['toDelete'] = mes.id

    return BOOK

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Реакции на инлайн кнопки от карточки книги. 
    т.е. после нажатия на инлайн кнопку, но до ручного ввода"""
    # TODO приделать update
    await update.callback_query.answer()
    data = update.callback_query.data

    # Определяем базовую клавиатуру, точно понадобится локальное "Назад"
    keyboard = [local_back_button]
    
    # Если нажатая кнопка отновилась к категории редактирования полей, то сохраняем название поля,
    if "edit_" in data:
        field = data.replace("edit_", "")
        context.user_data['edit_field'] = field
        # Если для поля имеется справочная информация - добавляем кнопку на клавиатуру
        if HELPS.get(field):
            keyboard.insert(0, [InlineKeyboardButton("Справка по вводу", callback_data=B_HELP)])
            
    #<TEXT> Переменная text определяется в этом сигменте
    # Базовый текст: приглашение
    text = f"Введите новое значение для поля: <b>{FIELDS.get(context.user_data.get('edit_field'))}</b>\n"

    # Для ввода опций базовый текст заменяется, а так же отправляет дополнительное сообщение с Reply клавиатурой
    if context.user_data.get('edit_field') == "options" and data != B_HELP: 
        text = "Или введите вручную.\n<u>(Только для опытных пользователей, читайте справку по вводу)</u>"
        mes_opt = await context.bot.send_message(chat_id=update.effective_chat.id, 
                        text="Выберите из готовых вариантов ниже",
                        parse_mode=ParseMode.HTML, disable_web_page_preview=True,
                        reply_markup=ReplyKeyboardMarkup([[v] for v in BOOK_OPTIONS.keys()])
                                                    )
        # данная переменная позволяет удалить сообщение как в декараторе, так и при нажатии локального "Назад"
        context.user_data['keyboardMessages'] = [mes_opt.id]

    # Расширение базового текст справкой, если она есть
    if data == B_HELP:
        text += '\n'
        text += HELPS.get(context.user_data.get('edit_field')) or ""

    # Действия если нажата кнопка "Сохранить"
    if data == B_SAVE:
        # Сохранение копии словаря, разделение и преобразование
        book = context.user_data.get("Book")
        isbns = strToLst(book.pop("isbns"))
        articles = strToLst(book.pop("articles"))

        # Пытаемся добавить книгу в ДБ, вернет ошибку если title уже есть в БД
        # Ошибки при добавлении isbn или артикля не возникает, если нет дубля в одной сессии
        # Если добавилось нормально - очищаем словарь, иначе - оставим для редактирования 
        # Удаляем переменные, переопределяем текст и клавиатуру
        # TODO приделать update
        # TODO добавить отдельное сообщение с введенными данными, которое не будет исчезать при перемещении по inline?
        try:
            id = database.addBookToDB(book)
            if isbns:
                database.addISBN(isbns, id)
            if articles:
                database.addArticle(articles, id)
        except Exception as ex:
            text = "Книга с таким названием уже есть в базе"
            # print(ex) # TODO LOG
        else:
            text = f"Добавлено в базу, id {id}!"
            del context.user_data["Book"]
        del book, isbns, articles
        keyboard = [buttons.get(BACK+END)]
        pass
    #</TEXT>

    # Параметры сообщения, чтобы не дублировать в if else
    message_kwargs = {'chat_id': update.effective_chat.id,
                        'text': text, 
                        'parse_mode': ParseMode.HTML, 
                        'disable_web_page_preview': True, 
                        'reply_markup': InlineKeyboardMarkup(keyboard)}

    # Если было доп сообщение, удаляется старое инлайн, и отправляется новое, иначе просто редактируем старое
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
    # определяем текущее поле, нормализуем ввод
    field = context.user_data.get('edit_field') or 'title'
    value = normalizeStr(update.message.text)

    # Обработка дат
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

    # Есть ли поле с несколькими значения
    is_list = field in ["isbns", "articles", "options"] 

    # Интерпретация опций из Reply клавиатуры
    if field == "options" and value in BOOK_OPTIONS.keys():
        value = BOOK_OPTIONS.get(value)

    # Если непустое поле для нескольких значений: дополняем, иначе присваиваем
    if context.user_data["Book"][field] and is_list:
        context.user_data["Book"][field] += f", {value}"
    else: 
        context.user_data["Book"][field] = value
    
    # Если поле с несколькими значения, ожидаем еще ввод, иначе - к выбору и карточке"
    if is_list:
        text = f"Текущие данные:\n{context.user_data["Book"][field]}\n\n"
        text += "Введите дополнительные данные, либо нажмите 'Назад' для возврата в предыдущее меню"
        keyboard = InlineKeyboardMarkup([local_back_button])
    else:
        text = build_text(context.user_data["Book"])
        keyboard = build_keyboard(context.user_data.get("Book").get("title"))

    # Удаление сообщения пользователя
    # TODO Не удалять сообщение пользователя, а удалять сообщение бота и создавать новое?
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
        id_to_del = await book_buttons(update, context)
        if id_to_del:
            mes = await context.bot.send_message(chat_id=update.effective_chat.id, 
                text=f"Вы действиетельно хотите удалить книгу и связанные с ней данные из базы? Если да, то введите '{password_to_del}'", 
                reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
            context.user_data['toDelete'] = (id_to_del, mes.id)
    elif context.user_data.get('toDelete'):
        if update.message and update.message.text == password_to_del:
            book_id = context.user_data.get('toDelete')[0]
            title = database.getBookTitle(book_id)
            
            database.delBook(book_id)

            
            await context.bot.delete_message(chat_id=update.effective_chat.id, 
                                              message_id=update.effective_message.id)
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                              message_id=context.user_data.get("toDelete")[1],
                                              text = f"Книга {book_id}. {title} была стерта из базы!", 
                                              reply_markup=None)
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
            'year_start': 'Год: с', 
            'year_end': 'Год: по', 
            'isbns': "ISBN's",
            'articles': 'Артикли OZON',
            'options': 'Дополнительные опции',
               }

BOOK_OPTIONS = {
    'Искать только по ISBN': 'onlyISBN',
    'Искать только по артиклю OZON': 'onlyArticle',
    'Тип обложки: Твердый переплет': 'covertype=537',
    'Издательство: Азбука': 'publisher=855985',
    'Издательство: АСТ': 'publisher=855962',
    'Издательство: Corpus': 'publisher=4663491',
    'Издательство: Эксмо': 'publisher=857671',
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
            'Дубли игнорируются при добавлении в базу'
            'Старайтесь брать ISBN из достоверных источников, например с сайта издательства книги, '
            'или с <a href="https://fantlab.ru/">Фантлаба</a>'
                    ),
        'articles': (
            'Артикль карточки книги на OZON, нужен для отслеживания конкретного товара.\n'
            'Артикль, по которому закончился (или не найден) товар будет удаляться автоматически.\n'
            'Отдельно, в дополнительных опциях, можно указать поиск <u>только</u> по этому параметру.\n'
            '<b>Если больше одного - указывайте через запятую, точку, с новой строки или в новом сообщении.</b>\n'
            'Дубли игнорируются при добавлении в базу'
            'Берите только с сайта или из приложения OZON'
                    ),
        'options': (
            "Дополнительные опции представляют из себя параметры на которых основывается поиск.\n"
            "Можно выбрать 'Искать только по ISBN/Артиклю', и тогда поиск будет работать соответствующе."
            "Взаимоисключающие опции, артикль выше по приоритету чем ISBN.\n\n"
            "<u>Иные опции более сложны и не рекомендуются для использования неопытными пользателями.</u>\n"
            "Они представляют из себя параметры, указываемые в поисковой строке на сайте OZON, точнее в его адресе (URL)\n"
            "Например: "
                "<s>'https://ozon.kz/category/knigi-16500/?sorting=price&</s>"
                "<u>covertype=537</u>&<b>publisher=855985</b>&<i>writer=239218</i>&"
                "<s>text=цвет</s>'\n"
            "Где covertype - тип обложки (твердая), publisher - издательство (Азбука), writer - автор (Пратчетт)\n"
            "Данные уточнения выбираются из фильтров поиска на сайте. В приложении заглянуть в URL не выйдет\n\n"
            "Вводите данные опции, копируя из адреса (url) поисковой страницы, в формате 'covertype=537'\n"
            '<b>Если больше одного - указывайте через запятую, точку, с новой строки или в новом сообщении.</b>\n'
            "\n<b><u>Если вы не уверены во вводимых параметрах, лучше ничего не вводите, что бы избежать нулевых результатов поиска</u></b>"
                    ),
        }

book_card_handler = [CallbackQueryHandler(handle_button, pattern=f"^edit_{k}$") for k in FIELDS.keys()]

book_callback = [
    myConvHandler(BOOK_LIST, BOOK, book_list, forKeyboard = 'inline'),

    myConvHandler(ADD_BOOK, BOOK, add_book, 
        extra_state_handlers = book_card_handler + [
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