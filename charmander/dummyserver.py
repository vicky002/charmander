__author__ = 'vikesh'

from slackrtm.server import User, Bot


class DummyServer(object):
    def __init__(self, slack=None, config=None, hooks=None, db=None):
        self.slack = slack or DummySlack()
        self.config = config
        self.hooks = hooks
        self.db = db

    def query(self, sql, *params):
        if not self.db:
            return None

        cursor = self.db.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        self.db.commit()
        return rows


class DummySlack(object):
    def __init__(self, server=None, users=None, events=None):
        self.server = server or DummySlackServer(users=users)
        self.posted_messages = None
        self.events = events if events else []

    def post_message(self, message, **kwargs):
        self.posted_messages = (message, kwargs)

    def rtm_read(self):
        return self.events.pop() if self.events else []


class DummySlackServer(object):
    def __init__(self, botname="Charmander", users=None, bots=None):
        self.login_data = {
            "self": {
                "name": botname,
            }
        }
        self.username = "replbot"

        self.users = users if users else {
            "1": User(self, "charmander_test", 1, "", 0),
            "2": User(self, "vickyuser", 2, "", 0),
            "3": User(self, "slackbot", 3, "", 0),
        }

        self.bots = bots if bots else {
            "1": Bot("1", "otherbot", [], False)
        }
