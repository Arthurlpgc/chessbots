import json
from chessdotcom import get_player_stats


def get_ratings(player):
    stats = get_player_stats(player).json
    ret = {}
    for chess_type in stats:
        if type(stats[chess_type]) is not dict:
            continue
        if 'last' not in stats[chess_type]:
            continue
        if 'rating' not in stats[chess_type]['last']:
            continue
        rating = stats[chess_type]['last']['rating']
        rd = None
        if 'rd' in stats[chess_type]['last']:
            rd = stats[chess_type]['last']['rd']
        ret[chess_type] = {'rd': rd, 'rating': rating}
    return ret
