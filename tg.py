import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import configparser
from picamera import PiCamera
from time import sleep
import os
from PIL import Image

config = configparser.ConfigParser()
config.read('config.ini')
tg_token = config['telegram']['token']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def botsend(userid, fpath):
    bot.send_photo(chat_id=userid, photo=open(fpath, 'rb'))
    bot.send_message(chat_id=tid, text=msgtext)


def takephoto():
    filepath = '/tmp/image.jpg'

    camera = PiCamera()
    camera.start_preview()
    sleep(5)
    camera.capture(filepath)
    camera.stop_preview()

    colorImage = Image.open(filepath)
    transposed = colorImage.transpose(Image.ROTATE_180)
    transposed.save(filepath)

    return filepath

def start(bot, update):
    keyboard = [[InlineKeyboardButton("RPI Photo", callback_data='takephoto'),
                 InlineKeyboardButton("Option 2", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

    if query.data == 'takephoto':
        file = takephoto()
        bot.send_photo(chat_id=query.message.chat_id, photo=open(file, 'rb'))
        os.remove(file)

def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(tg_token)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()