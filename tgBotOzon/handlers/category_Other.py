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

## OTHER
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

other_callback = []

if __name__ == '__main__':
    pass