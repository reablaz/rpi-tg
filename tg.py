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

camera = PiCamera()

def botsend(userid, fpath):
    bot.send_photo(chat_id=userid, photo=open(fpath, 'rb'))
    bot.send_message(chat_id=tid, text=msgtext)


def takephoto():
    filepath = '/tmp/image.jpg'

    camera.start_preview()
    sleep(5)
    camera.capture(filepath)
    camera.stop_preview()

    camera.close()

    colorImage = Image.open(filepath)
    transposed = colorImage.transpose(Image.ROTATE_180)
    transposed.save(filepath)


    return filepath

def takevideo():
    filepath = '/tmp/video.h264'

    camera.start_preview()
    camera.start_recording('/home/pi/video.h264')
    sleep(10)
    camera.stop_recording()
    camera.stop_preview()
    camera.close()

    return filepath

def start(bot, update):
    keyboard = [[InlineKeyboardButton("RPI Photo", callback_data='takephoto'),
                 InlineKeyboardButton("Video", callback_data='takevideo')],

                [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    chatid = query.message.chat_id

    bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

    if query.data == 'takephoto':
        file = takephoto()
        bot.send_photo(chat_id=chatid, photo=open(file, 'rb'))
        os.remove(file)
    elif query.data == 'takevideo':
        file = takevideo()
        bot.send_video(chat_id=chatid, video=open(file, 'rb'))

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