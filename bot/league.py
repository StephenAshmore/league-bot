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

    def isFinished(self):
        if len(self.games) > 0:
            return False
        else:
            return True

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
        i = 0
        for g in self.games:
            if where == 'home' and g['home'] == winner and g['away'] == loser:
                del self.games[i]
            elif where == 'away' and g['away'] == winner and g['home'] == loser:
                del self.games[i]
            i += 1

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
        table += '{:16}:{:^5}|{:^5}|{:^5}|{:^5}|{:^5}|{:^5}|{:^5}|{:^5}\n'.format('Name', 'PL', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'PTS')
        table_players = sorted(self.players, key=lambda k: k['points'], reverse=True)
        for p in table_players:
            goal_differential = int(p['goalsFor']) - int(p['goalsAgainst'])
            table += '{:16}:'.format(p['name'])
            table += '{:^5}|{:^5}'.format(p['games'], p['wins'])
            table += '|{:^5}|{:^5}'.format(p['ties'], p['losses'])
            table += '|{:^5}|{:^5}'.format(p['goalsFor'], p['goalsAgainst'])
            table += '|{:^5}'.format(goal_differential)
            table += '|{:^5}'.format(p['points'])
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

        if reply == '':
            reply = 'The league has ended, there are no more games to play.'

        return reply

    def loadData(filename):
        with open('/leagues/' + filename) as json_data:
            # d = json.load(json_data)
            return jsonpickle.decode(json_data)
        return League('Empty loaded league')

    def saveData(self):
        j = jsonpickle.encode(self)
        with open('/leagues/' + self.name + '.json', "w+") as text_file:
            text_file.write(j)

    def winner(self):
        if self.isFinished():
            table_players = sorted(self.players, key=lambda k: k['points'], reverse=True)
            if table_players[0]['points'] == table_players[1]['points']:
                # need a playoff game
                self.games.append(dict(home=table_players[0]['name'],
                                       away=table_players[1]['name']))
                return 'There is a tie for first place between: {} and {}. A playoff game has been scheduled.'.format(table_players[0]['name'], table_players[1]['name'])
            else:
                return '{} has won the league with {} points!'.format(table_players[0]['name'], table_players[0]['points'])