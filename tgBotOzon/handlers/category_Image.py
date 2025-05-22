# from .common import *
from ..common import (
        dictByKeys, getListFiles,
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

## IMAGE
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
    for rng in range(0, len(media), 10):
        await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media[1*rng:10+rng])
    # await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("./graphics/aBooksTable0.png", 'rb'), has_spoiler=True)
    # await context.bot.send_document(chat_id=update.effective_chat.id, document="./graphics/aBooksTable0.png")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вот фото, что дальше?", reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
    # await update.callback_query.edit_message_text("Что делать будем?", reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
    return IMAGE

image_callback = [
    CallbackQueryHandler(image_table, pattern=f"^{IM_TAB}$"),
    CallbackQueryHandler(image_table, pattern=f"^{IM_UNION_GR}$"),
    CallbackQueryHandler(image_table, pattern=f"^{IM_ONE_GR}$"),
    CallbackQueryHandler(image_table, pattern=f"^{IM_ALL_GR}$"),
    CallbackQueryHandler(cat_image, pattern=f"^{BACK}$"), 
    ]

if __name__ == '__main__':
    pass