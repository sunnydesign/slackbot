import os
import sys
import time
import json

from starterbot import slack_client, parse_slack_output, BOT_ID

from commands.mood import get_mood
from commands.special import celebration
from commands.articles import get_num_posts
from commands.challenge import create_tweet
from commands.weather import get_weather
from commands.standup import get_standup

cmd_names = ('standup', 'mood', 'celebration', 'num_posts', '100day_tweet', 'weather')
cmd_functions = (get_standup, get_mood, celebration, get_num_posts, create_tweet, get_weather)
COMMANDS = dict(zip(cmd_names, cmd_functions))
START_TIME = "12:30:00"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = PROJECT_ROOT + "/users.txt"

def handle_command(cmd, channel):
    cmd = cmd.split()
    cmd, args = cmd[0], cmd[1:]

    if cmd in COMMANDS:
        if args:
            response = COMMANDS[cmd](*args)
        else:
            response = COMMANDS[cmd]()
    else:
        response = ('Not sure what you mean? '
            'I can help you with these commands:\n'
            '{}'.format('\n'.join(cmd_names)))

    slack_client.api_call("chat.postMessage", text = response, as_user = True)


def write_users(users):
    f = open(USERS_FILE, 'w')

    for user in users:
        f.write(json.dumps(user) + '\n')
    f.close


def get_users_local():
    f = open(USERS_FILE, 'r')
    lines = f.readlines()
    users_list = []

    for line in lines:
        data  = json.loads(line)
        users_list.append(data)

    f.close

    return users_list


def start_standup():
    get_users()
    users = get_users_local() # get users from file

    for user in users:
        response = 'Salut ' + user['name'] + '! It\'s time for our standup meeting Daily Standup. When you are ready please answer the following question:'
        message_attachments = [{
            "fallback": "Upgrade your Slack client to use messages like these.",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [{
                "name": "quick_reply_list",
                "text": "Quick reply",
                "type": "select",
                "options": [{
                    "text": "Skip",
                    "value": "skip"
                }, {
                    "text": "Same as last time",
                    "value": "same"
                }, {
                    "text": "i\'m on vacation :palm_tree:",
                    "value": "vacation"
                }]
            }]
        }]

        slack_client.api_call("chat.postMessage", channel = user['id'],
            text = response, attachments = message_attachments, as_user = True)



def get_users():
    api_call = slack_client.api_call("users.list")

    if api_call.get('ok'):
        users = api_call.get('members')
        users_list = []

        for user in users:
            if (user.get('is_bot') == False and user.get('name') != "slackbot"):
                users_list.append(user)

        write_users(users_list)

    else:
        print("could not find users")


def daily_message():
    current_time = time.strftime("%H:%M:%S")
    if (current_time == START_TIME):
        start_standup()
        print(current_time)


if __name__ == '__main__':
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Bot connected and running!")
        while True:
            daily_message()
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                #write_channel(channel)
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
