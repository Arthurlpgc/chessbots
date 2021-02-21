from telegram.ext import Updater, CommandHandler
import json
from datetime import timedelta, datetime
from rating import get_ratings
from games import get_top_eco_analysis, get_games, get_game_datetime
from db import link_account, add_to_group, remove_from_group, get_linked_account, get_all_linked_accounts
from game_gif_converter import game_to_gif
TOKEN = json.loads(open('secret.json', 'r').read())["telegram_bot"]

TRACKED_MODES = ['rapid', 'blitz', 'bullet', 'daily']

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


def send_message(context, update, message):
    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message)
    except:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message)


def send_photo(context, update, pic):
    try:
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=pic)
    except:
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=pic)


def send_animation(context, update, pic):
    try:
        context.bot.send_animation(
            chat_id=update.effective_chat.id, animation=pic)
    except:
        context.bot.send_animation(
            chat_id=update.effective_chat.id, animation=pic)


def last_game_handler(update, context, player):
    now = datetime.now()
    all_games = []
    for game_type in TRACKED_MODES:
        all_games.extend(get_games(player, game_type, now.year,
                                   now.month, now.year, now.month))
    all_games.sort(key=get_game_datetime)
    if len(all_games) > 0:
        send_animation(context, update, pic=open(
            game_to_gif(all_games[-1]), 'rb'))
    else:
        send_message(context, update, "No games")


def results_handler(update, context, player):
    now = datetime.now()
    all_games = []
    for game_type in TRACKED_MODES:
        all_games.extend(get_games(player, game_type, now.year,
                                   now.month, now.year, now.month))
    all_games.sort(key=get_game_datetime)
    ret = []
    for game in all_games:
        set_date = get_game_datetime(game)
        if set_date > (now - timedelta(hours=24)):
            ret.append(game.headers["PlayerResult"])
    if len(ret) > 0:
        if ret[-1] == "loss":
            send_photo(context, update, pic=open('risitas.jfif', 'rb'))
        elif ret[-1] == "win":
            send_photo(context, update, pic=open('5head.png', 'rb'))
        else:
            send_message(context, update, "Boooooring")
    else:
        send_message(context, update, "No games")


def get_rating_handler(update, context, player):
    ratings = get_ratings(player)
    message = f'Ratings for {player}\n'
    for (chess_type, stats) in ratings.items():
        rating = stats['rating']
        rd = stats['rd']
        mode = chess_type.split('chess_')[-1]
        message += f'{mode}:  {rating} RD({rd})\n'
    send_message(context, update, message)


def format_mode_ratings(mode, bucket):
    message = f'Leaderboard for {mode} (top 10):\n'
    for player, rating in bucket:
        message += f'{player} - {rating}\n'
    return message + f'\n'


def get_ratings_handler(update, context):
    args = update.message.text.split(' ')

    modes = []
    if len(args) > 1:
        for arg in args[1:]:
            if arg not in TRACKED_MODES:
                send_message(
                    context, update, "Why would you be interested in {}? This is not supported, remove it!".format(arg))
                return
            modes.append(arg)
    else:
        modes = TRACKED_MODES

    send_message(context, update, "Alright, give me a second...")

    accounts = get_all_linked_accounts(update.message.chat.id)
    modes_buckets = {}
    for chess_user in accounts:
        ratings = get_ratings(chess_user)
        for (chess_type, stats) in ratings.items():
            mode = chess_type.split('chess_')[-1]
            if mode not in modes:
                continue

            rd = stats['rd']
            rating = stats['rating']

            if rd > 80:
                continue

            if mode not in modes_buckets.keys():
                modes_buckets[mode] = []
            modes_buckets[mode].append((chess_user, rating))

    for mode, players_ratings in modes_buckets.items():
        modes_buckets[mode] = sorted(
            players_ratings, key=lambda x: x[1], reverse=True)[:9]

    message = ''
    for mode in modes:
        if mode in modes_buckets.keys():
            message += format_mode_ratings(mode, modes_buckets[mode])

    if len(message) > 0:
        message = message[:-1]
        send_message(context, update, message)
    else:
        send_message(
            context, update, "Nothing to show here. Are you sure the people are playing this?")


def link_account_handler(update, context):
    words = update.message.text.split(' ')
    if len(words) == 2:
        player = words[1]
        link_account(update.message.from_user.id, player)
        send_message(context, update, "Linked accounts!")
    else:
        send_message(
            context, update, "Linked accounts! JK, just trolling since u don't know how to use this command...")


def CommandPlayerHandler(command, handler_func, error_message="Please send the username as well or link your accounts!"):
    def handler(update, context):
        words = update.message.text.split(' ')
        if len(words) == 1:
            uid = str(update.message.from_user.id)
            player = get_linked_account(uid)
            if player is not None:
                handler_func(update, context, player)
            else:
                send_message(context,
                             update, error_message)
        elif len(words) > 2:
            send_message(context,
                         update, error_message)
        else:
            player = words[1]
            handler_func(update, context, player)
    return CommandHandler(command, handler)


def add_to_group_handler(update, context):
    words = update.message.text.split(' ')
    if len(words) >= 2:
        for player in words[1:]:
            add_to_group(update.message.chat.id, player)
            send_message(context, update, "Account added! "+player)
    else:
        send_message(
            context, update, "No accounts really?")


def remove_from_group_handler(update, context):
    words = update.message.text.split(' ')
    if len(words) >= 2:
        for player in words[1:]:
            remove_from_group(update.message.chat.id, player)
            send_message(context, update, "Account removed! "+player)
    else:
        send_message(
            context, update, "No accounts really?")


handlers = [
    CommandHandler('link_account', link_account_handler),
    CommandPlayerHandler('rating', get_rating_handler),
    CommandHandler('add_to_group', add_to_group_handler),
    CommandHandler('remove_from_group', remove_from_group_handler),
    CommandHandler('ratings', get_ratings_handler),
    CommandPlayerHandler('last_game', last_game_handler),
    CommandPlayerHandler('result', results_handler)
]
for handler in handlers:
    dispatcher.add_handler(handler)
updater.start_polling()
