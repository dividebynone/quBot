from libs.sqlhandler import sqlconnect
import main
import os


class GiveawayHandler(object):

    def __init__(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS giveaway_participants(userid INTEGER, msgid INTEGER)")
            cursor.execute("CREATE TABLE IF NOT EXISTS giveaways(msgid INTEGER, value INTEGER)")

    @classmethod
    async def start_giveaway(self, msg_id: int, value: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO giveaways(msgid, value) VALUES(?, ?)", (msg_id, value,))

    @classmethod
    async def get_giveaway_value(self, msg_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT value FROM giveaways WHERE msgid=?", (msg_id,))
            db_output = cursor.fetchone()
            if db_output:
                db_output = list(db_output)
                return db_output[0] if db_output else None
            else:
                return None

    @classmethod
    async def get_giveaway_list(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT msgid FROM giveaways")
            db_output = cursor.fetchall()
            return [x[0] for x in db_output] if db_output else None

    @classmethod
    async def has_entered_giveaway(self, user_id: int, msg_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT rowid FROM giveaways WHERE msgid=?", (msg_id,))
            check = cursor.fetchone()
            if check:
                cursor.execute("SELECT rowid FROM giveaway_participants WHERE userid=? AND msgid=?", (user_id, msg_id,))
                db_output = cursor.fetchone()
                return True if db_output else False
            else:
                return None

    @classmethod
    async def enter_giveaway(self, user_id: int, msg_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO giveaway_participants(userid, msgid) VALUES(?, ?)", (user_id, msg_id,))

    @classmethod
    async def end_giveaway(self, msg_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("DELETE FROM giveaway_participants WHERE msgid=?", (msg_id,))
            cursor.execute("DELETE FROM giveaways WHERE msgid=?", (msg_id,))
            result = cursor.rowcount
            return True if result > 0 else False
