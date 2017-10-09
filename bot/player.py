import jsonpickle
import json


class Player(object):
    def __init__(self, name):
        self.name = name
        self.elo = 1000
        self.number_games = 0
        self.number_wins = 0
        self.number_leagues = 0
        self.ratio = 0
        self.leagues = []
        self.games = []

    def win(self):
        self.number_games += 1
        self.number_wins += 1
        self.ratio = self.number_wins / self.number_games

    def lose(self):
        self.number_games += 1

    def tie(self):
        self.number_games += 1
        self.number_wins += 0.5

    def profile(self):
        wins = self.number_wins
        loses = self.number_games - self.number_wins
        ratio = 0
        if self.number_games > 0:
            ratio = wins / self.number_games
        reply = '```Player {}\'s Profile:\n'.format(self.name)
        reply += 'Wins: {}. Losses: {}. Ratio: {}\n'.format(wins, loses, ratio)
        reply += 'Total Games Played: {}'.format(self.number_games)
        reply += ' Total Leagues Played: {}\n'.format(self.number_leagues)
        reply += 'Your ELO is {}.\n'.format(self.elo)
        reply += '```'
        return reply

    def loadData(filename):
        with open('/players/' + filename) as json_data:
            print(json_data)
            d = json.dumps(json.load(json_data))
            print(d)
            return jsonpickle.decode(d)
        return Player('Failed to load')

    def saveData(self):
        print('Saving a player in player.save()')
        j = jsonpickle.encode(self)
        print('Saving player {} with data {}'.format(self.name, j))
        with open('/players/' + self.name + '.json', "w+") as text_file:
            text_file.write(j)
            print('Data written.')
        print('Done saving.')
