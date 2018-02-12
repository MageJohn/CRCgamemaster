import pickle

class Room:
    def __init__(self, channel, game=None, players=None, turn=None, game_state=None):
        self.channel = channel
        self.game = game
        self.players = players
        self.turn = turn
        self.game_state = game_state

class IllegalMoveError(Exception):
    """Raised when an illegal move is made

    Attributes:
        message: explains what rule was broken
    """
    def __init__(self, message):
        self.message = message

def get(filename):
    """retrieves object from file"""
    with open(filename, "rb") as fp:
        return pickle.load(fp)

def save(theObject, filename):
    """saves object to file"""
    with open(filename, "wb") as fp:
        pickle.dump(theObject, fp)
