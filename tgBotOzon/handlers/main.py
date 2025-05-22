# from .common import *
from ..common import (
        getEnv, dictByKeys, getListFiles,
        database, sys, logging, asyncio,
        Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, 
        InlineKeyboardButton, InputMediaPhoto, InputMediaDocument, ParseMode,
        Message, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler,
        ConversationHandler, CallbackQueryHandler, filters, 
        admins, buttons, 
        CONV_END, END, BEGIN, BACK, PREV, NEXT, MESS_ITER, CATEGORY, BOOK, 
        TXTLINK, IMAGE, OTHER, BOOK_LIST, ADD_BOOK, DEL_BOOK, ADD_ISBN, 
        DEL_ISBN, ADD_ARTICLE, DEL_ARTICLE, B_CSV, TL_ALL, TL_ONE, IM_TAB, 
        IM_UNION_GR, IM_ONE_GR, IM_ALL_GR, NO_BOOK, 
        MessageIter, iterMsg, myConvHandler, decConv, decConvParent, booksList, 
        lastPricesList, lstToMessage, book_buttons    
                    )

from . import category_Book
from . import category_TxtLink
from . import category_Image
from . import category_Other

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

# Хандлеры, обрабатывают что то, выполняя функцию
start_handler = CommandHandler('start', start, filters=admins)

cat_callback = [
    CallbackQueryHandler(start, pattern=f"^{CATEGORY}$"),
    CallbackQueryHandler(category_Book.cat_book, pattern=f"^{BOOK}$"), 
    CallbackQueryHandler(category_TxtLink.cat_txtlint, pattern=f"^{TXTLINK}$"), 
    CallbackQueryHandler(category_Image.cat_image, pattern=f"^{IMAGE}$"), 
    CallbackQueryHandler(category_Other.cat_other, pattern=f"^{OTHER}$"),
    ]

start_conv_handler = ConversationHandler(
    entry_points = [start_handler],
    states = {
        CATEGORY: cat_callback, 
        BOOK: category_Book.book_callback,
        TXTLINK: category_TxtLink.txtlink_callback,
        IMAGE: category_Image.image_callback, 
        OTHER: category_Other.other_callback,
        },
    fallbacks = [
        CallbackQueryHandler(end, pattern=f"^{END}$"), 
        CallbackQueryHandler(start, pattern=f"^{BEGIN}$"),
        start_handler
        ],
    allow_reentry=True
    )


if __name__ == '__main__':
    pass