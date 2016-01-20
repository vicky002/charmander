"""
Log all messages to the database only active
If the CHARMANDER_LOG environment variable is set.
"""

import os

DO_LOG = os.environ.get("CHARMANDER_LOG", False)


def on_message(msg, server):
    if DO_LOG:
        server.query("INSERT INTO  log VALUES  (?, ?, ?, ?)",
                     msg["text"], msg["user"], msg["ts"], msg["team"], msg["channel"])


def on_init_(server):
    if DO_LOG:
        server.query("""
CREATE TABLE IF NOT EXISTS  log (msg STRING, sender STRING, time STRING, team STRING, channel STRING)
""")