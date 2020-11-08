from libs.sqlhandler import sqlconnect
import main
import os


class VotingTracker(object):

    def __init__(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS voting (user_id INTEGER PRIMARY KEY, combo INTEGER, last_voted INTEGER)")

    @classmethod
    async def get_user(self, user_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO voting (user_id) VALUES(?)", (user_id,))
            cursor.execute("SELECT IFNULL(combo, 0), last_voted FROM voting WHERE user_id=?", (user_id,))
            output = cursor.fetchone()
            return dict(combo=output[0], last_voted=output[1]) if output else None

    @classmethod
    async def update_user(self, user_id: int, user_data: dict):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("UPDATE voting SET combo=?, last_voted=? WHERE user_id=?", (user_data['combo'], user_data['last_voted'], user_id,))
