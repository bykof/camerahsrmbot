#coding=utf8

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardHide
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    RegexHandler,
    ConversationHandler
)

import logging

from classes.menu import Menu
from passwords import TOKEN

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

MENU_TYPE = 0
MENU = Menu()
MENU_MAPPER = {
    'Heute': MENU.todays_menu,
    'Morgen': MENU.tommorows_menu,
    # 'Woche': MENU.weekly_menu,
}

def options(bot, update):
    reply_keyboard = [MENU_MAPPER.keys()]

    update.message.reply_text(
        'Ay Gude wie! Wähle einen der Optionen!',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        )
    )

    return MENU_TYPE


def menu_type(bot, update):
    menu_text = MENU_MAPPER[update.message.text]()
    update.message.reply_text(menu_text, reply_markup=ReplyKeyboardHide())
    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardHide())

    return ConversationHandler.END


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('essen', options)],
        states={
            MENU_TYPE: [RegexHandler('^(Heute|Morgen|Woche)$', menu_type)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    # log all errors
    dp.add_error_handler(error)
    # Start the Bot
    updater.start_polling()
    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
