import logging.config
import selectors
import sys
from queue import Queue


EXIT_GAME = False

logging.config.fileConfig(fname="logging.conf")


def produce_input(queue):
    """
    Produce input for the game.
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


def main():
    queue = Queue()
    produce_input(queue)

if __name__ == "__main__":
    main()