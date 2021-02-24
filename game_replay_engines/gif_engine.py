import chess.svg
import pgn2gif
import random
import string

from chessdotcom_lib.games import get_game_id, get_games


def game_to_gif(game, duration=0.75):
    reverse = game.headers["playing_as"] == "black"
    title = get_game_id(game)
    pgn_path = f'output/{title}.pgn'
    gif_path = f'output/{title}.gif'

    pgn_file = open(pgn_path, 'w')
    pgn_file.write(str(game))
    pgn_file.close()
    pgn_creator = pgn2gif.PgnToGifCreator(
        reverse=reverse, duration=duration, ws_color='#eeedd5', bs_color='#7c945d')
    pgn_creator.create_gif(pgn_path, out_path=gif_path)
    
    def clean_up():
        os.remove(pgn_path)
        os.remove(gif_path)

    return gif_path, clean_up
