from telegram.ext import Updater, CommandHandler
import json
from rating import get_ratings

TOKEN = json.loads(open('secret.json', 'r').read())["telegram_bot"]

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


def get_rating(update, context):
    words = update.message.text.split(' ')
    if len(words) == 1:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Please send the username as well!")
    elif len(words) > 2:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="What are you trying to pull here? Send just one username")
    else:
        player = words[1]
        ratings = get_ratings(player)
        message = f'Ratings for {player}\n'
        for (chess_type, stats) in ratings.items():
            rating = stats['rating']
            rd = stats['rd']
            mode = chess_type.split('chess_')[1]
            message += f'{mode}:  {rating} RD({rd})\n'
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=message)


start_handler = CommandHandler('rating', get_rating)
dispatcher.add_handler(start_handler)
updater.start_polling()
