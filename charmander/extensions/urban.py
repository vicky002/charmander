# -*- coding: UTF-8 -*-
# urban <term> returns the urban dictionary definition and example of a term

import requests
import re

try:
    from urllib import quote
except ImportError:
    from urllib.request import quote


def reply_to(string):
    lines = string.split("\n")
    return "\n".join("> _{0}_".format(l.strip()) for l in lines)


def urban(term):

    # Slack replaces the quote character with a smart quote.
    # Undo that
    term = term.replace(u'’', "'").encode("utf8")

    baseurl = u"http://api.urbandictionary.com/v0/define?term={0}"
    data = requests.get(baseurl.format(quote(term))).json()

    try:
        result = data['list'][0]
        result["example"] = reply_to(result.get("example", ""))
        definition = (u"*{word}*: {definition}.\n"
                        "*Example:*\n{example}".format(**result))

        return definition
    except IndexError:
        return ":boom: No results found for {0}, please try again".format(term)


def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"~urban (.*)", text)
    if not match:
        return
    searchterm = match[0]
    return urban(searchterm)



