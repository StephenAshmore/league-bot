import time


class League(object):
    """A league object which represents a group of players, rankings, and games.

    Attributes:
        start_date: Start Date
        end_date: End Date
        players: A list of players
    """

    def __init__(self, name):
        """Return a Customer object whose name is *name* and starting
        balance is *balance*."""
        self.name = name
        self.start_date = time.localtime()
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def start(self):
        """This creates the league with the current players, along
        with the table, and set of games to be played."""

    def show_table(self):
        table = self.name + ' League Table:'
        return table