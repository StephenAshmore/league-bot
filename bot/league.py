import time
import jsonpickle
import json


class League(object):
    """A league object which represents a group of players, rankings, and games.

    Attributes:
        start_date: Start Date
        end_date: End Date
        players: A list of player objects
    """

    def __init__(self, name):
        """Return a Customer object whose name is *name* and starting
        balance is *balance*."""
        self.name = name
        self.start_date = time.localtime()
        self.players = []
        self.started = False
        self.games = []
        self.played = []

    def add_player(self, player):
        self.players.append(dict(
            name=player,
            wins=0,
            losses=0,
            ties=0,
            games=0,
            goalsFor=0,
            goalsAgainst=0,
            points=0
        ))

    def start(self):
        """This creates the league with the current players, along
        with the table, and set of games to be played."""
        if len(self.players) > 1:
            self.started = True
            for p in self.players:
                for o in self.players:
                    if p['name'] != o['name']:
                        self.games.append(dict(home=p['name'], away=o['name']))
        return self.started

    def win(self, winner, loser, score1, score2, where):
        self.played.append(dict(winner=winner,
                                loser=loser,
                                score1=score1,
                                score2=score2))
        for p in self.players:
            if p['name'] == winner:
                p['wins'] += 1
                p['games'] += 1
                p['goalsFor'] += int(score1)
                p['goalsAgainst'] += int(score2)
                p['points'] += 3
            elif p['name'] == loser:
                p['losses'] += 1
                p['games'] += 1
                p['goalsFor'] += int(score2)
                p['goalsAgainst'] += int(score1)
        # Find the game in the games list and remove it.
        for i, g in self.games.items():
            if where == 'home' and g['home'] == winner and g['away'] == loser:
                del self.games[i]
            elif where == 'away' and g['away'] == winner and g['home'] == loser:
                del self.games[i]

    def tie(self, winner, loser, score1, score2, where):
        self.played.append(dict(winner=winner,
                                loser=loser,
                                score1=score1,
                                score2=score2))

        for p in self.players:
            if p['name'] == winner:
                p['ties'] += 1
                p['games'] += 1
                p['goalsFor'] += score1
                p['goalsAgainst'] += score2
                p['points'] += 3
            elif p['name'] == loser:
                p['ties'] += 1
                p['games'] += 1
                p['goalsFor'] += score2
                p['goalsAgainst'] += score1
        # Find the game in the games list and remove it.
        for i, g in self.games.items():
            if g['home'] == winner or g['away'] == winner:
                if g['away'] == loser or g['home'] == loser:
                    del self.games[i]

    def show_table(self):
        table = '```'
        table += self.name + ' League Table:\n'
        table += '*Name*: PL | W | D | L | GF | GA | GD | PTS\n'
        table_players = sorted(self.players, key=lambda k: k['points'])
        for p in table_players:
            table += '*' + p['name'] + '*: '
            table += p['games'] + ' ' + p['wins']
            table += ' ' + p['ties'] + ' ' + p['losses']
            table += ' ' + p['goalsFor'] + ' ' + p['goalsAgainst']
            table += ' ' + str(int(p['goalsFor']) - int(p['goalsAgainst']))
            table += ' ' + p['points']
            table += '\n'
        table += '```'
        return table

    def getGames(self):
        reply = ''
        for g in self.games:
            reply += g['home']
            reply += '[Home] versus '
            reply += g['away']
            reply += '[Away]\n'

        return reply

    def load(filename):
        with open('strings.json') as json_data:
            d = json.load(json_data)
            return jsonpickle.decode(d)
        return League()

    def save(self):
        j = jsonpickle.encode(self)
        with open(self.name + '.json', "w") as text_file:
            text_file.write(j)
