
from .common import (
        dictByKeys, getListFiles,
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
        buttons.get(BEGIN+END)
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Действия c книгами", reply_markup=InlineKeyboardMarkup(book_keys))
    return BOOK

@decConv(cat_book)
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
                parse_mode=ParseMode.HTML, disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([buttons.get(PREV+NEXT), buttons.get(BACK+END)]))
    return BOOK

async def add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"Выбрано действие с книгой: {update.callback_query.data}", 
                                                  reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
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
        del context.user_data['toDelete']
    return BOOK

BOOK_LIST, ADD_BOOK, DEL_BOOK, ADD_ISBN, DEL_ISBN, ADD_ARTICLE, DEL_ARTICLE, B_CSV = ["book"+r for r in map(str,range(8))]

book_callback = [
    myConvHandler(BOOK_LIST, BOOK, book_list, forKeyboard = 'inline'),
    # CallbackQueryHandler(book_list, pattern=f"^{BOOK_LIST}|{PREV}|{NEXT}$"),
    CallbackQueryHandler(add_book, pattern=f"^{ADD_BOOK}$"),
    myConvHandler(DEL_BOOK, BOOK, del_book, forKeyboard = 'reply'),
    # CallbackQueryHandler(del_book, pattern=f"^{DEL_BOOK}$"),
    CallbackQueryHandler(add_book, pattern=f"^{ADD_ISBN}$"),
    CallbackQueryHandler(add_book, pattern=f"^{DEL_ISBN}$"),
    CallbackQueryHandler(add_book, pattern=f"^{ADD_ARTICLE}$"),
    CallbackQueryHandler(add_book, pattern=f"^{DEL_ARTICLE}$"),
    CallbackQueryHandler(add_book, pattern=f"^{B_CSV}$"),
    CallbackQueryHandler(cat_book, pattern=f"^{BACK}$"), 
    ]

if __name__ == '__main__':
    pass