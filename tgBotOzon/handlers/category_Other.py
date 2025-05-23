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
    # print(update.callback_query.data)
    other_keys = [
        [InlineKeyboardButton("Последний лог", callback_data=str(OTHER_LOG))],
        # [InlineKeyboardButton("TODO", callback_data=str(OTHER_TODO))],
        buttons.get(BEGIN+END)
        # bottomButtons
        ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Прочии действия", reply_markup=InlineKeyboardMarkup(other_keys))
    return OTHER

async def sendLog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.id)
    logmedia = [ InputMediaDocument( open( getListFiles(path='./logs', filetype=".txt")[-1] ) ) ]
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=logmedia)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вот лог, что дальше?", 
                                                  reply_markup=InlineKeyboardMarkup([buttons.get(BACK+END)])
                                                  )

OTHER_LOG, OTHER_TODO = ["textlink"+r for r in map(str,range(2))]

other_callback = [
    CallbackQueryHandler(sendLog, pattern=f'^{OTHER_LOG}$'),
    # CallbackQueryHandler(cat_other, pattern=f'^{OTHER_TODO}$'),
    CallbackQueryHandler(cat_other, pattern=f'^{BACK}$'),
    ]

if __name__ == '__main__':
    pass