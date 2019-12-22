#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json
import re
import sys

from slackclient import SlackClient

# Your app's Slack bot user token
SLACK_BOT_TOKEN = 'xoxb-XXXXXXXXXXX'

USAGE_MESSAGE = """Please run with arguments:
slack_alert.py #channel_name "error subject" "error message" """

if len(sys.argv)<3:
    print(USAGE_MESSAGE)
    sys.exit(1)

slack_channel = sys.argv[1]
zabbix_event_id = sys.argv[2]
slack_messages = sys.argv[3]
slack_message_list = slack_messages.splitlines()
slack_subject = slack_message_list[0]
slack_message = '\n'.join(slack_message_list[1:])

slack_actions = []
slack_emoji = 'WTF: :ghost:'
slack_color = '#439FE0OB'
# Change emoji depending on the subject - smile (RECOVERY/OK), frowning (PROBLEM), or ghost (for everything else)
if re.match(r'^RECOVER(Y|ED)?$', slack_subject):
    slack_emoji = ":smile:"
    slack_color = '#76C858'
elif re.match(r'^OK', slack_subject):
    slack_emoji = ':smile:'
    slack_color = '#76C858'
elif re.match(r'^PROBLEM', slack_subject):
    slack_emoji = ':fire:'
    slack_color = '#DC513F'
    slack_actions = [{"type": "button",
                       "text": "Acknowledge",
                       "value": zabbix_event_id,
                       "name": "acknowledge",
                       "confirm": {"title": "Are you sure?",
                                   "text": "Acknowledge event on zabbix?",
                                   "ok_text": "Yes",
                                   "dismiss_text": "No"
                                   }
                       }]


# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# # A Dictionary of message attachment options
attachments_json = [{ "text": "{}".format(slack_message),
                      "color": slack_color,
                      "callback_id": "ack",
                      "actions": slack_actions
                      }]

# # Send a message with the above attachment
slack_client.api_call(
    "chat.postMessage",
    channel=slack_channel,
    text="{} {}".format(slack_emoji,slack_subject),
    attachments=attachments_json,
    mrkdwn=True
)
