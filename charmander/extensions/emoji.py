__author__ = 'vikesh'
"""
<~emoji> N : This will return N random emojis!
"""

import re
import random
from emojidic import emojiDict


def randomelect(dic):
    keys = list(dic.keys())
    i = random.randint(0, len(keys)-1)                  # get random emoji
    return dic[keys[i]]


def emoji(n=1):
    emoji = []
    for i in range(n):
        emoji.append(randomelect(emojiDict))

    return "".join(emoji)


def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"(~emoji)\s*(\d+)*", text)
    if not match:
        return

    N = 1 if not  match[0][1] else int(match[0][1])

    return emoji(N)


