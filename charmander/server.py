__author__ = 'vikesh'

class CharmanderServer(object):
    def __init__(self, slack, config, hooks, db):
        self.slack = slack
        self.config = config
        self.hooks = hooks
        self.db = db

    def query(self, sql, *params):
         curser = self.db.cursor()
         curser.execute(sql, params)
         rows = curser.fetchall()
         curser.close()
         self.db.commit()
         return rows