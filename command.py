#!/usr/bin/env python3
"""
README:
Requirements:
"""
import argparse
import boto3
import chess
import chess.pgn
import math
import requests
import time
import io
from collections import defaultdict
from subprocess import check_output
from stockfish import Stockfish
from statistics import harmonic_mean


def main():
    parser = argparse.ArgumentParser(
        description="""
    Justin's Chess Tool
    """,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--depth",
                        type=int,
                        default=15,
                        action="store",
                        required=False)
    parser.add_argument("--hash",
                        type=int,
                        default=1536,
                        action="store",
                        required=False)
    parser.add_argument("--url")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--file")
    parser.add_argument("--ecs", type=bool, default=False, action="store")
    args = parser.parse_args()
    stockfish = Stockfish(path="/stockfish/stockfish",
                          depth=args.depth,
                          parameters={
                              "Threads": args.threads,
                              "Minimum Thinking Time": 1000,
                              "Hash": args.hash
                          })
    if args.url:
        game = chess.pgn.read_game(get_pgn_from_url(args.url))
        print(annotate_game(game, stockfish))
    if args.file:
        """
        is_ecs = False
        try:
            is_ecs = requests.get("http://169.254.169.254/latest/meta-data/",
                                  timeout=2).ok
        except:
            pass
        """
        if args.ecs:
            s3 = boto3.client('s3')
            s3.download_file('justinabaum.com', 'chess/{}'.format(args.file),
                             '/tmp/games.pgn')
        games = []
        flag = False
        file = open('/tmp/games.pgn')
        while game := chess.pgn.read_game(file):
            if flag:
                print("\n\n")
            flag = True
            stockfish.set_position([])
            print(annotate_game(game, stockfish))


def evaluate_game(stockfish, game):
    return map(lambda move: make_move_with_eval(stockfish, move),
               game.mainline())


def make_move_with_eval(stockfish, line):
    move = line.move
    comment = line.comment
    new_move = {"Move": move}
    if comment and comment != "":
        new_move["Comment"] = comment
    old_ev = stockfish.get_evaluation()
    turn = is_white_turn_from_fen(stockfish)
    stockfish.make_moves_from_current_position([move])
    ev = stockfish.get_evaluation()
    if ev.get("type") == "cp":
        new_move["Centipawn"] = ev.get("value")
        new_move["Mate"] = None
    else:
        new_move["Centipawn"] = None
        new_move["Mate"] = ev.get("value")
    old_win = Accuracy.win_move(old_ev, turn)
    new_win = Accuracy.win_move(ev, turn)
    accuracy = Accuracy.accuracy(abs(old_win - new_win))
    new_move["Accuracy"] = accuracy
    return new_move


def annotate_game(game, stockfish):
    headers = game.headers
    moves = list(evaluate_game(stockfish, game))
    white_moves = moves[0::2]
    black_moves = moves[1::2]
    white_accuracy = harmonic_mean(
        map(lambda move: move.get("Accuracy") or 0, white_moves))
    black_accuracy = harmonic_mean(
        map(lambda move: move.get("Accuracy") or 0, black_moves))
    annotated_game = write_pgn(moves, headers)
    annotated_game.headers["ZAWhiteAccuracy"] = "{:.1f}%".format(
        white_accuracy * 100)
    annotated_game.headers["ZBBlackAccuracy"] = "{:.1f}%".format(
        black_accuracy * 100)
    return annotated_game


def insufficient_material(stockfish):
    board = get_position_from_fen(stockfish)
    if any(map(lambda x: x in board, list("pPqQrR"))):
        return False
    if board.count("b") == 2:
        return False
    if board.count("B") == 2:
        return False
    if board.count("B") > 1 and board.count("N") > 1:
        return False
    if board.count("b") > 1 and board.count("N") > 1:
        return False
    return True


def get_pgn_from_url(url):
    response = requests.get(url).text
    return io.StringIO(response)


def get_position_from_fen(stockfish):
    return stockfish.get_fen_position().split(' ')[0]


def is_white_turn_from_fen(stockfish):
    return stockfish.get_fen_position().split(' ')[1] == 'w'


def get_comment(move):
    accuracy = move.get("Accuracy")
    if accuracy < 0.7:
        return "Mistake; Accuracy: {:.0f}%".format(accuracy * 100)
    if accuracy < 0.5:
        return "Blunder; Accuracy: {:.0f}%".format(accuracy * 100)


def write_pgn(moves, headers):
    game = chess.pgn.Game()
    game.headers = headers
    node = game
    for move in moves:
        node = node.add_variation(move.get("Move"))
        comment = move.get("Comment")
        if added_comment := get_comment(move):
            if comment is None:
                comment = added_comment
            else:
                comment += ";    {}".format(added_comment)
        node.comment = comment
    return game


class Accuracy:
    @staticmethod
    def win(centipawn, is_white=True):
        cp = centipawn if is_white else -centipawn
        return 0.5 + 0.5 * (2 / (1 + math.exp(-0.00368208 * cp)) - 1)

    def win_move(valuation, is_white=True):
        centipawn = 0
        value = valuation.get("value")
        if valuation.get("type") == "cp":
            centipawn = value
        else:
            centipawn = 2**15 - value * 1000
            if value == 0:
                centipawn = 2**15 if is_white else -2**15
            else:
                centipawn *= value / abs(value)
        cp = centipawn if is_white else -centipawn
        return 0.5 + 0.5 * (2 / (1 + math.exp(-0.00368208 * cp)) - 1)

    @staticmethod
    def accuracy(change_win):
        acc = 1.031668 * math.exp(-4.354 * change_win) - 0.031669
        if acc <= 0:
            return 0.000001
        return acc


if __name__ == "__main__":
    main()
