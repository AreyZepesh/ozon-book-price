# from .common import *
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

## OTHER
async def cat_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.callback_query.data)
    # if context.user_data.get(MESS_ITER):
    #     del context.user_data[MESS_ITER]
    other_keys = [
        [InlineKeyboardButton("Получить последний лог", callback_data=str(CATEGORY))],
        buttons.get(BEGIN+END)
        # bottomButtons
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Действия c", reply_markup=InlineKeyboardMarkup(other_keys))
    return CATEGORY

async def sendLog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

OTHER_LOG, OTHER_TODO = ["textlink"+r for r in map(str,range(2))]

other_callback = [
    # CallbackQueryHandler(sendLog, pattern=f'^{}$'),
    ]

if __name__ == '__main__':
    pass