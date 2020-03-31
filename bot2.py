import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

import re 

import requests
import urllib.request
import time
from bs4 import BeautifulSoup


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BIO = 1


def start(update, context):

    update.message.reply_text(
        'Hi! Reply to me with the ticker of the stock you are interested in and I will tell you its price and price change!'
        '\n\nSend /cancel to stop talking to me.\n\n')

    return BIO


def bio(update, context):
    user = update.message.from_user
    logger.info("Stock of %s: %s", user.first_name, update.message.text)

    stock_ticker = update.message.text
    stock_ticker = stock_ticker.lower()


    if not re.match('[a-zA-Z0-9.]',stock_ticker):
        update.message.reply_text('Please enter an actual stock!')
    elif any(word in stock_ticker for word in ['fuck','cunt','ccb','knn','chibai','bitch']):
        update.message.reply_text('fuck u dont swear at me')

    else:

        url =  'https://sg.finance.yahoo.com/quote/'+ stock_ticker + '/'

        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")

        find1 = str(soup.find_all('h1'))
        stock_name = find1[54:-6]


        find2 = str(soup.find_all('span','Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)'))
        stock_price = find2[86:-8]


        find3 = list(soup.find_all('span', 'Trsdu(0.3s) Fw(500) Fz(14px) C($dataGreen)'))

        find4 = str(soup.find_all('span'))
        false_stock = find4[-91:-8]



        if false_stock == 'Please check your spelling. Try our suggested matches or see results in other tabs.':
            update.message.reply_text('That is not a valid stock. Please try again.')
        elif find3 == []:
            find3 = str(soup.find_all('span', 'Trsdu(0.3s) Fw(500) Fz(14px) C($dataRed)'))
            stock_change = find3[74:-8]
            update.message.reply_text('*'+stock_name+'*'+'\n\nStock Price: '+stock_price+'\nChange in Price: '+ stock_change, parse_mode='Markdown')
            update.message.reply_text('Type in another stock name to continue or click on /cancel to stop.')
        else: 
            find3 = str(find3)
            stock_change = find3[76:-8]
            update.message.reply_text('*'+stock_name+'*'+'\n\nStock Price: '+stock_price+'\nChange in Price: '+ stock_change, parse_mode='Markdown')
            update.message.reply_text('Type in another stock name to continue or click on /cancel to stop.')





def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text("Bye! Click on /start again to input new stock.",
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def unknown(update, context):
    update.message.reply_text("Sorry, I didn't understand that command.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("792803744:AAHqwZU7QjMyjg9mdej-NxCTJ_XSeuVq0Z8", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={

            BIO: [MessageHandler(Filters.text, bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    #unknown commands
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()