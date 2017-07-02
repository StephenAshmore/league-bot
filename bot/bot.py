from slackclient import SlackClient

import logging
import re
import time

logger = logging.getLogger(__name__)
API_TOKEN = 'xoxb-207584631110-cMz6V5ocdtfLADHPACufjC9I'


class Bot(object):
    def __init__(self):
        self._client = SlackClient(
            API_TOKEN,
        )

    def run(self):
        logger.info('Booting League Bot..')
        if not self._client.rtm_connect():
            logger.info('Could not connect.')
            exit()

        self.channel_users = self._client.api_call("users.list")
        while True:
            events = self._client.rtm_read()
            for event in events:
                event_type = event.get('type')
                if event_type == 'message':
                    logger.info('Handling message.')
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

        if 'text' in event.keys() and event['text'].startswith('@league-bot'):
            botname = 'league-bot'
            if 'user' in event.keys():
                name = self.get_name_from_id(event['user'])

                if name == botname or name == u'slackbot' or name is None:
                    return

                self._client.api_call(
                  "chat.postMessage",
                  channel=event['channel'],
                  text='Hello from League Bot! @{} :tada:'.format(name)
                )

    def get_name_from_id(self, id):
        for user in self.channel_users['members']:
            if id == user['id']:
                return user['name']
        return None
