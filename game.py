#!/usr/bin/env python3
from stockfish import Stockfish
from collections import defaultdict 
import chess
import chess.pgn

TIME = "15 Ply" #1000
TOP3 = False

stockfish = Stockfish(path="/stockfish/stockfish", parameters={"Threads": 16}, depth=3)
stockfish.update_engine_parameters({"Hash": 1536})
moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"]
moves = []
moves2 = [None, None, None, None, None]
moves2 = []
stockfish.set_position(moves)

boards = defaultdict(int)

def insufficient_material(board):
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

def play_game(stockfish):
  boards = defaultdict(int)
  boards[stockfish.get_fen_position] += 1
  end = "Insufficient Materials"
  while not insufficient_material(stockfish.get_fen_position()):
    boards[stockfish.get_fen_position().split(' ')[0]] += 1
    top_moves = []
    if TOP3:
      top_moves = stockfish.get_top_moves(3, TIME)
    moves2.append(top_moves)
    if len(top_moves) == 0:
      move = stockfish.get_best_move()#_time(TIME)
    else:
      move = top_moves[0].get("Move")
    if boards[stockfish.get_fen_position().split(' ')[0]] == 3:
      end = "Draw by repetition"
      break

    if move is None:
      end = None
      break
    #print("Making move: {}".format(move))
    stockfish.make_moves_from_current_position([move])
    #print(stockfish.get_board_visual())
    moves.append(move)
  return moves, moves2, end

moves, moves2, end = play_game(stockfish)

def pgn_from_moves(moves, end=None):
  game = chess.pgn.Game()
  node = game

  game.headers["Event"] = ""
  game.headers["Date"] = ""
  game.headers["White"] = "Stockfish {} Compute 8 Threads M1 Macbook Air".format(TIME)
  game.headers["Black"] = "Stockfish {} Compute 8 Threads M1 Macbook Air".format(TIME)
  if end:
    game.headers["Result"] = "1/2 1/2"
  for move, top2 in zip(moves, moves2):
    last = node
    node = node.add_main_variation(chess.Move.from_uci(move))
    if top2:
      for move in top2:
        print(move)
        last.add_variation(chess.Move.from_uci(move.get("Move")), comment="Rated: {}".format(move.get("Centipawn")))

  return str(game) + ("" if end == None else "{ " + end + " }")

print(pgn_from_moves(moves, end))
