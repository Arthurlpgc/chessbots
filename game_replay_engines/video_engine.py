from chess import *
import cv2
from datetime import datetime
import numpy as np
import os

from chessdotcom_lib.games import get_game_id

PIECE_SIZE = 60
BOARD_SIZE = PIECE_SIZE * 8

WHITE_COLOR = (210,238,237)
BLACK_COLOR = (85,150,117)

def _start_pixel(idx):
    return idx * PIECE_SIZE

def _end_pixel(idx):
    return (idx + 1) * PIECE_SIZE

def _piece_to_asset(piece):
    piece = piece.symbol()
    color = 'w' if piece.isupper() else 'b'
    piece = piece.lower()
    return cv2.imread(f'assets/pieces/{color}{piece}.png', -1)

def _overlay_piece(frame, piece, rank_idx, file_idx):
    piece_alpha = piece[:, :, 3] / 255.0
    board_alpha = 1.0 - piece_alpha

    [x1, x2, y1, y2] = [_start_pixel(rank_idx), _end_pixel(rank_idx), _start_pixel(file_idx), _end_pixel(file_idx)]

    for c in range(0, 3):
        frame[x1:x2, y1:y2, c] = (
            piece_alpha * piece[:, :, c] +
            board_alpha * frame[x1:x2, y1:y2, c]
        )

def _draw_chess_board_empty():
    img = np.full((BOARD_SIZE,BOARD_SIZE,3), WHITE_COLOR)
    for rank_idx in range(0, 8):
        for file_idx in range(0, 8):
            if (rank_idx + file_idx) % 2:
                img[
                    _start_pixel(rank_idx):_end_pixel(rank_idx),
                    _start_pixel(file_idx):_end_pixel(file_idx),
                ] = BLACK_COLOR
    return img.astype(np.uint8)

def _draw_chess_board(board, reverse):
    frame = _draw_chess_board_empty()
    pieces_order = SQUARES_180 if not reverse else list(reversed(SQUARES_180))
    for idx in range(len(pieces_order)):
        rank_idx = idx // 8
        file_idx = idx % 8
        piece = board.piece_at(pieces_order[idx])
        if piece:
            _overlay_piece(frame, _piece_to_asset(piece), rank_idx, file_idx)
    return frame

def game_to_video(game, fps=1.2):
    game_id = get_game_id(game)
    board = game.board()
    reverse = game.headers["playing_as"] == "black"

    video_path = f'output/{game_id}.mp4'
    video = cv2.VideoWriter(video_path,cv2.VideoWriter_fourcc(*'avc1'),fps,(BOARD_SIZE,BOARD_SIZE))

    while True:
        frame = _draw_chess_board(game.board(), reverse)
        video.write(frame)
        if game.is_end():
            break
        game = game.next()

    video.release()
    cv2.destroyAllWindows()

    def clean_up():
        os.remove(video_path)

    return video_path, clean_up
