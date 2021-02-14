from chessdotcom import get_player_games_by_month
import io
import chess.pgn
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime


result_map = {
    'black': {
        '1-0': 'loss',
        '1/2-1/2': 'draw',
        '0-1': 'win',
    },   
    'white': {
        '1-0': 'win',
        '1/2-1/2': 'draw',
        '0-1': 'loss',
    },
}


def get_games_by_month(player, time_class, year, month):
    c_games = get_player_games_by_month(player, year, month).json['games']
    games = []
    for c_game in c_games:
        if c_game['time_class'] == time_class:
            playing_as = 'white' if c_game['white']['username'] == player else 'black'
            pgn = io.StringIO(c_game['pgn'])
            game = chess.pgn.read_game(pgn)
            game.headers['playing_as'] = playing_as
            game.headers['PlayerResult'] = result_map[playing_as][game.headers['Result']]
            games.append(game)
    return games

def get_games(player, time_class, from_year, from_month, to_year, to_month):
    start = datetime(from_year, from_month, 1)
    end = datetime(to_year, to_month, 1)
    months = [(d.month, d.year) for d in rrule(MONTHLY, dtstart=start, until=end)]
    games = []
    for (month, year) in months:
        games.extend(get_games_by_month(player, time_class, year, month))
    return games

def get_games_eco(player, time_class, from_year, from_month, to_year, to_month):
    games = get_games(player, time_class, from_year, from_month, to_year, to_month)
    ecos = {"black": {}, "white": {}}
    for game in games:
        playing_as = game.headers['playing_as']
        eco = game.headers.get("ECO")
        g_result = game.headers["Result"]
        if eco not in ecos[playing_as]:
            ecos[playing_as][eco] = {'win': 0, 'loss': 0, 'draw': 0, 'games': 0}
        result = result_map[playing_as][g_result]
        ecos[playing_as][eco][result] += 1
        ecos[playing_as][eco]['games'] += 1

    return ecos

def get_top_eco_analysis(player, time_class, from_year, from_month, to_year, to_month):
    ecos = get_games_eco(player, time_class, from_year, from_month, to_year, to_month)
    filtered_ecos = {}
    for color in ecos:
        filtered_ecos[color] = {}
        for eco in ecos[color]:
            if ecos[color][eco]['games'] > 5:
                filtered_ecos[color][eco] = ecos[color][eco]
    return filtered_ecos