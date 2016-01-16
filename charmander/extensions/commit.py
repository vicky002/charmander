__author__ = 'vikesh'

# Get random commit messages
""" ~commit returns random commit messages"""

import re
import requests


def commit():
    return requests.get("http://whatthecommit.com/index.txt").text


def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"~commit( .*)?", text)

    if not match:
        return

    return commit()



