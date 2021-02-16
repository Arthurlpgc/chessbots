from games import get_games
import chess.svg
import pgn2gif
import random
import string


def random_title():
    letters = string.ascii_lowercase
    title = ''.join(random.choice(letters) for i in range(10))
    return title


def game_to_gif(game, duration=0.5):
    reverse = game.headers["playing_as"] == "black"
    title = random_title()
    pgn_file = open(f'output/{title}.pgn', 'w')
    pgn_file.write(str(game))
    pgn_file.close()
    pgn_creator = pgn2gif.PgnToGifCreator(
        reverse=reverse, duration=duration, ws_color='#eeeed2', bs_color='#baca44')
    pgn_creator.create_gif(
        f'output/{title}.pgn', out_path=f'output/{title}.gif')
    return f'output/{title}.gif'
