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

## TXTLINK
@decConvParent
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
    # if update.callback_query.data == BACK: #or context.user_data.get(BACK):
    #     return CONV_END
    return TXTLINK

@decConv(cat_txtlint)
async def txtlint_one(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = await book_buttons(update, context)
    # print(id)
    if id:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=lstToMessage(lastPricesList(id))[0],
                                        parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Что дальше?", 
                                        reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)]))
    return TXTLINK

@decConv(cat_txtlint)
async def txtlint_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    await update.callback_query.answer()

    text = iterMsg( update, context, lstToMessage(lastPricesList()) )

    await update.callback_query.edit_message_text(text = text,
            parse_mode=ParseMode.HTML, disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([buttons.get(PREV+NEXT), buttons.get(BACK+END)]))

    
    return TXTLINK

txtlink_callback = [
    myConvHandler(TL_ONE, TXTLINK, txtlint_one, forKeyboard = 'reply'),
    myConvHandler(TL_ALL, TXTLINK, txtlint_all, forKeyboard = 'inline'),
    # CallbackQueryHandler(txtlint_all, pattern=f"^{TL_ALL}|{PREV}|{NEXT}$"),
    CallbackQueryHandler(cat_txtlint, pattern=f"^{BACK}$"), 
    ]

if __name__ == '__main__':
    pass