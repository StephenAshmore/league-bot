from slackclient import SlackClient

import logging
import sys
import os
import re
import time

logger = logging.getLogger(__name__)
slack_token = os.environ["SLACK_API_TOKEN"]


class Bot(object):
    def __init__(self):
        self._client = SlackClient(
            slack_token,
        )

    def run(self):
        logger.info('Booting League Bot..')
        if not self._client.rtm_connect():
            logger.info('Could not connect.')
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

        if 'text' in event.keys() and event['text'].startswith('<@{}>'.format(self.bot_id)):
            botname = 'league_bot'
            if 'user' in event.keys():
                name = self.get_name_from_id(event['user'])

                if name == botname or name == u'slackbot' or name is None:
                    return

                # this is a message for leaguebot. Deal with message:
                text = event['text']
                reply = 'I\'m sorry, but I don\'t understand that command.'
                commands = text.split(' ')
                main_command = commands[0]
                del commands[0]
                if main_command == 'table':
                    if self.current_league is not None:
                        reply = self.current_league.show_table()

                self._client.api_call(
                  "chat.postMessage",
                  channel=event['channel'],
                  text=reply
                )

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
