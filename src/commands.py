import random
import logging.config
import sys

import chess

logging.config.fileConfig(fname="logging.conf")

        
def send_command(command: str) -> None:
    """
    Send the given command to the engine.

    Args:
        command: the command to send
    """
    logging.debug(f"command sent: {command}")
    sys.stdout.write(command + "\n")
    sys.stdout.flush()

def uci():
    """Initialize the UCI protocol by sending engine identification details."""
    send_command("id name DummyChessEngine")
    send_command("id author camaral")
    send_command("uciok")

def isready():
    """Tells the GUI the engine is ready to play."""
    send_command("readyok")


def ucinewgame(board):
    """Reset the given board to its starting position.

    Args:
        board: the board to reset
    """
    board.reset()

def position(command_args, board):
    """
    Set the position of the given board to the given position.

    If the command is "position startpos moves <move_list>", the board is reset and the given moves are pushed onto the board.

    If the command is "position fen <fen_board> [moves <move_list>]", the board is set to the given FEN board and the given moves are pushed onto the board.

    Args:
        command_args: the list of command arguments
        board: the board to set the position of
    """
    def push_moves_from_list(board, move_list):
        """Push all moves in the given list onto the given board.

        Args:
            board: the board to push moves onto
            move_list: the list of moves to push
        """
        for move in move_list:
            board.push_san(move)


    if command_args[1] == "startpos" and command_args[2] == "moves":
        board.reset()
        push_moves_from_list(board, command_args[3:])
    elif command_args[1] == "fen":
        board = chess.Board(" ".join(command_args[2:8]))
        if len(command_args) > 8 and command_args[8] == "moves":
            push_moves_from_list(board, command_args[9:])
    else:
        logging.error(f"unknown position command: {command_args}")

def go(command_args, board):
    move = random.choice(list(board.legal_moves))
    send_command(f"bestmove {move.uci()}")

