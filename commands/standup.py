import random
import re

import requests


def get_standup():
    welcome = 'Salut Andrey! It\'s time for our standup meeting Daily Standup. When you are ready please answer the following question:'

    return welcome


if __name__ == '__main__':
    print('Getting 3 random moods for our bot: ')
    for i in range(3):
        print(get_mood())
