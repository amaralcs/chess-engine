import logging.config
import selectors
import sys
from queue import Queue
import chess
from concurrent.futures import ThreadPoolExecutor


EXIT_GAME = False

logging.config.fileConfig(fname="logging.conf")


def produce_input(queue: Queue) -> None:
    """
    Produce input from stdin.

    This function runs an infinite loop, reading input from stdin. Input is
    processed by the given queue. If the input is "exit", EXIT_GAME is set
    to True.

    :param queue: the queue to put the input into
    """
    def read_input(stdin, mask):
        """
        Read input from stdin.
        """
        line = stdin.readline()
        
        if line:
            return line.strip()
        else:
            # no more imputs
            selector.unregister(sys.stdin)
            return None

    global EXIT_GAME
    selector = selectors.DefaultSelector()
    selector.register(fileobj=sys.stdin, events=selectors.EVENT_READ, data=read_input)

    while not EXIT_GAME:
        logging.debug(f"producer exit game: {EXIT_GAME}")
        
        for key, events in selector.select(timeout=1):
            callback = key.data # function to read input
            line = callback(sys.stdin, events)
            if line:
                logging.debug(f"producer line: {line}")
                queue.put(line)
                if line == "exit":
                    EXIT_GAME = True
    
    logging.debug("producer done")

def consume_input(queue: Queue, board: chess.Board, idx: int) -> None:
    """
    Consume input from the given queue and process the commands.

    Args:
        queue: queue to consume from
        board: the chess board
        idx: the index of the consumer

    """
    global EXIT_GAME
    while not EXIT_GAME:
        logging.debug(f"consumer {idx} exit game: {EXIT_GAME}")
        try:
            line = queue.get(timeout=1)
            logging.debug(f"consumer line: {line}")
            if line == "exit":
                EXIT_GAME = True

            process_command(line, board)
        except queue.Empty:
            logging.debug(f"consumer {idx}: queue empty")
    logging.debug(f"consumer {idx} done")

def process_command(line: str, board: chess.Board) -> None:
    """
    Process the given command.

    Args:
        line: the command to process
        board: the chess board
    """
    send_command(line)
    print(board)
        
def send_command(command: str) -> None:
    """
    Send the given command to the engine.

    Args:
        command: the command to send
    """
    logging.debug(f"command sent: {command}")
    sys.stdout.write(command + "\n")
    sys.stdout.flush()

def main():
    queue = Queue()
    board = chess.Board()

    n_players = 2

    with ThreadPoolExecutor(max_workers=n_players+1) as executor:

        executor.submit(produce_input, queue) # Start listening to inputs
        [executor.submit(consume_input, queue, board, i) for i in range(n_players)]

if __name__ == "__main__":
    main()