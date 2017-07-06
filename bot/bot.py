from slackclient import SlackClient

import logging
import sys
import os
import re
import time

from league import League
from player import Player

logger = logging.getLogger(__name__)
slack_token = os.environ["SLACK_API_TOKEN"]


class Bot(object):
    def __init__(self):
        self._client = SlackClient(
            slack_token,
        )
        self.previous_leagues = []
        self.current_league = None
        self.league_count = 0
        self.players = []

    def run(self):
        print('Booting League Bot..')
        if not self._client.rtm_connect():
            print('Could not connect.')
            exit()

        self.channel_users = self._client.api_call("users.list")
        self.bot_id = self. get_id_from_name("league_bot")
        while True:
            events = self._client.rtm_read()
            for event in events:
                event_type = event.get('type')
                if event_type == 'message':
                    self.handle_message(event)
                if (event_type == 'member_joined_channel ' or
                   event_type == 'member_left_channel'):
                    self.channel_users = self._client.api_call("users.list")

            time.sleep(1)

    def handle_message(self, event):
        # ignore edits
        subtype = event.get('subtype', '')
        if subtype == u'message_changed':
            return

        if ('text' in event.keys() and
           event['text'].startswith('<@{}>'.format(self.bot_id))):
            botname = 'league_bot'
            if 'user' in event.keys():
                userid = event['user']
                name = self.get_name_from_id(userid)

                if name == botname or name == u'slackbot' or name is None:
                    return

                # this is a message for leaguebot. Deal with message:
                text = event['text'].lower()
                reply = 'I\'m sorry, but I don\'t understand that command.'
                commands = text.split(' ')
                cmd_len = len(commands) - 1
                del commands[0]
                main_command = commands[0]

                if main_command == 'table':
                    if self.current_league is not None:
                        reply = self.current_league.show_table()
                    else:
                        reply = '<@{}> there is no current league, start one!'.format(userid)
                elif main_command == 'league':
                    if cmd_len > 1 and commands[1] == 'start':
                        if self.current_league is None:
                            reply = '<@{}> you must create a league first. Use @league_bot league [league name].'.format(userid)
                        elif self.current_league.started:
                            reply = '<@{}> there is already a league happening.'.format(userid)
                        else:
                            success = self.current_league.start()
                            if success:
                                reply = '<@{}> League has been started, table has been generated!.'.format(userid)
                            else:
                                reply = '<@{}> Looks like you don\'t have enough players! Try an ad hoc game with @league_bot challenge <opponent>.'.format(userid)
                    else:
                        default_name = 'League ' + str(self.league_count + 1)
                        if cmd_len > 1:
                            league_name = commands[1]
                        else:
                            league_name = default_name
                        self.current_league = League(name)
                        reply = 'League "{}" created. Please say @league_bot join <team name> to register.'.format(league_name)
                elif main_command == 'join':
                    if (self.current_league is None or
                        self.current_league.started):
                        reply = '<@{}>, the current league is closed.'.format(userid)
                    else:
                        self.current_league.add_player(self.confirm_player(name))
                        reply = '<@{}> you\'ve joined the current league!'.format(userid)
                elif main_command == 'register':
                    self.players.append(Player(name))
                    reply = '<@{}>, you\'ve been registered to play.'.format(userid)
                elif main_command == 'help':
                    reply = 'League Bot Help Menu:\n'
                    reply += '```'
                    reply += 'League bot uses the format: @league_bot <commands>. The following commands are available:\n'
                    reply += 'help: Displays this help message.\n'
                    reply += 'league [league name]: Creates a league with optional league name.\n'
                    reply += 'league start: Starts the league with the joined players, and creates the league table.\n'
                    reply += 'table: This displays the current league table.\n'
                    reply += 'join [team name]: This allows you to join the current league, and will register you as a player if you weren\'t already.\n'
                    reply += 'register: Registers you as a new player.\n'
                    reply += 'lost <opponent> <your score>:<opponent score> <home|away>. Home|Away must specify whether you were home or away.\n'
                    reply += 'won <opponent> <your score>:<opponent score> <home|away>. Home|Away must specify whether you were home or away.\n'
                    reply += 'tie <opponent> <your score>:<opponent score> <home|away>. Home|Away must specify whether you were home or away.\n'
                    reply += 'games: See the games left to play in the league.\n'
                    reply += 'leaderboard: See the leaderboard for all players.\n'
                    reply += 'profile: See the details of your profile.\n'
                    reply += '```'
                elif main_command == 'lost':
                    if cmd_len != 4:
                        reply = 'Whoops, the format for lost must be:\n```lost <opponent> <your score>:<opponent score> <home|away>\n```'
                    else:
                        winner = self.getPlayer(commands[1])
                        loser = self.getPlayer(name)

                        if commands[2].find(':') == -1:
                            reply = 'Whoops, the format for the scores in command lost must be:\n```<your score>:<opponent score>\n```'
                        else:
                            score = commands[2].split(':')
                            # Need game validation here.
                            where = ''
                            if commands[3] == 'home':
                                where = 'away'
                            else:
                                where = 'home'
                            self.current_league.win(commands[1], name, score[1],
                                                    score[0], where)
                            winner.win()
                            loser.lose()
                            reply = 'Sorry you lost <@{}>! Match recorded.'.format(userid)
                elif main_command == 'won':
                    if cmd_len != 4:
                        reply = 'Whoops, the format for won must be:\n```won <opponent> <your score>:<opponent score> <home|away>\n```'
                    else:
                        winner = self.getPlayer(name)
                        loser = self.getPlayer(commands[1])

                        if commands[2].find(':') == -1:
                            reply = 'Whoops, the format for the scores in command won must be:\n```<your score>:<opponent score>\n```'
                        else:
                            score = commands[2].split(':')
                            # Need game validation here.
                            self.current_league.win(name, commands[1], score[0],
                                                    score[1], commands[3])
                            winner.win()
                            loser.lose()
                            reply = 'Congrats <@{}>! Match recorded.'.format(userid)
                elif main_command == 'tie':
                    reply = 'Close game <@{}>! Match recorded.'.format(userid)
                elif main_command == 'games':
                    reply = self.current_league.getGames()
                elif main_command == 'test_register' and name == 'stephen':
                    self.current_league.add_player(self.confirm_player(commands[1]))
                    reply = ''
                elif main_command == 'profile':
                    reply2 = self.getPlayer(name).profile()
                    if reply2:
                        reply = reply2
                    else:
                        reply = 'Whoops <@{}> you aren\'t registered!'.format(userid)

                self._client.api_call(
                  "chat.postMessage",
                  channel=event['channel'],
                  text=reply
                )

    def getPlayer(self, player):
        for p in self.players:
            if p.name == player:
                return p
        return None

    def confirm_player(self, name):
        for p in self.players:
            if p.name == name:
                p.leagues = self.current_league.name
                return name
        self.players.append(Player(name))
        return name

    def get_name_from_id(self, id):
        for user in self.channel_users['members']:
            if id == user['id']:
                return user['name']
        return None

    def get_id_from_name(self, name):
        for user in self.channel_users['members']:
            if name == user['name']:
                return user['id']
        return None
