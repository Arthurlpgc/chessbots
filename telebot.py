from telegram.ext import Updater, CommandHandler
import json
from datetime import timedelta, datetime
from rating import get_ratings
from games import get_top_eco_analysis, get_games
from db import link_account, get_linked_account, get_all_linked_accounts

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


def results_for_player_handler(player, update, context):
    now = datetime.now()
    all_games = []
    for game_type in TRACKED_MODES:
        all_games.extend(get_games(player, game_type, now.year, now.month, now.year, now.month))
    ret = []
    for game in all_games:
        game_date = game.headers["UTCDate"]
        game_time = game.headers["UTCTime"]
        datetime_str = f"{game_date} {game_time} UTC"
        set_date = datetime.strptime(datetime_str, '%Y.%m.%d %H:%M:%S %Z')
        if set_date > (now - timedelta(minutes=30)):
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

def results_handler(update, context):
    words = update.message.text.split(' ')
    if len(words) == 1:
        uid = str(update.message.from_user.id)
        player = get_linked_account(uid)
        if player is not None:
            results_for_player_handler(player, update, context)
        else:
            send_message(context, update, "Please send the username as well or link your accounts!")
    elif len(words) > 2:
        send_message(context, update, "What are you trying to pull here? Send just one username!")
    else:
        player = words[1]
        results_for_player_handler(player, update, context)

def get_rating_for_player_handler(player, update, context):
    ratings = get_ratings(player)
    message = f'Ratings for {player}\n'
    for (chess_type, stats) in ratings.items():
        rating = stats['rating']
        rd = stats['rd']
        mode = chess_type.split('chess_')[-1]
        message += f'{mode}:  {rating} RD({rd})\n'
    send_message(context, update, message)


def get_rating_handler(update, context):
    words = update.message.text.split(' ')
    if len(words) == 1:
        uid = str(update.message.from_user.id)
        player = get_linked_account(uid)
        if player is not None:
            get_rating_for_player_handler(player, update, context)
        else:
            send_message(context,
                         update, "Please send the username as well or link your accounts!")
    elif len(words) > 2:
        send_message(context,
                     update, "What are you trying to pull here? Send just one username!")
    else:
        player = words[1]
        get_rating_for_player_handler(player, update, context)


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

    accounts = get_all_linked_accounts()
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


def format_ecos(ecos):
    eco_list = [{
        "avg_points": (ecos[eco]["win"] + ecos[eco]["draw"]/2.0) / ecos[eco]["games"],
        "eco": eco,
        "win": ecos[eco]["win"]/ecos[eco]["games"],
        "loss": ecos[eco]["loss"]/ecos[eco]["games"],
        "draw": ecos[eco]["draw"]/ecos[eco]["games"],
        "games": ecos[eco]["games"]
    } for eco in ecos]
    eco_list.sort(key=lambda eco: (eco["avg_points"], -eco["games"]))
    return eco_list


def get_ecos_info_handler(update, context):
    words = update.message.text.split(' ')
    if len(words) == 2:
        today = datetime.today()
        last_month = today.replace(day=1) - timedelta(days=1)
        player = words[1]
        ecos = get_top_eco_analysis(
            player, 'rapid', last_month.year, last_month.month, today.year, today.month)
        message = ""
        for color in ecos:
            message += f"For games in {color}:\n"
            formatted_ecos = format_ecos(ecos[color])
            for eco in formatted_ecos:
                eco_code = eco["eco"]
                points = "{:.2f}".format(eco["avg_points"])
                win = int(eco["win"] * 100)
                draw = int(eco["draw"] * 100)
                loss = int(eco["loss"] * 100)
                games = eco["games"]
                message += f"{eco_code}: {points} (W: {win}%, D: {draw}%, L: {loss}%, G: {games})\n"
        send_message(context, update, message)
    else:
        send_message(context, update, "Try again, lul..")


handlers = [
    CommandHandler('get_top_ecos', get_ecos_info_handler),
    CommandHandler('link_account', link_account_handler),
    CommandHandler('rating', get_rating_handler),
    CommandHandler('ratings', get_ratings_handler), 
    CommandHandler('result', results_handler)
]
for handler in handlers:
    dispatcher.add_handler(handler)
updater.start_polling()
