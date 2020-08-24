from libs.sqlhandler import sqlconnect
import main
import math
import os

class ProfilesHandler(object):

    def __init__(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS profiles(user_id INTEGER, guild_id INTEGER, experience INTEGER, level INTEGER, background INTEGER, bio BLOB, PRIMARY KEY (user_id, guild_id))")

    @classmethod
    async def get(self, user_id: int, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO profiles (user_id, guild_id) VALUES(?, ?)", (user_id, guild_id,))
            cursor.execute("SELECT IFNULL(experience, 0), IFNULL(level, 0), background, bio FROM profiles WHERE user_id=? AND guild_id=?",(user_id, guild_id,))
            output = cursor.fetchone()
            if not output:
                return None
            else:
                output = list(output)
                return_dict = dict(experience=output[0], level=output[1], background=output[2], bio=output[3])
                return return_dict

    @classmethod
    async def set_bio(self, user_id: int, guild_id: int, bio: str):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO profiles (user_id, guild_id) VALUES(?, ?)", (user_id, guild_id,))
            cursor.execute("UPDATE profiles SET bio=? WHERE user_id=? AND guild_id=?", (bio, user_id, guild_id,))

    @classmethod
    async def get_bio(self, user_id: int, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT bio FROM profiles WHERE user_id=? AND guild_id=?",(user_id, guild_id,))
            output = cursor.fetchone()
            return output[0] if output else None

    @classmethod
    async def get_rank(self, user_id: int, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT RANK() OVER (ORDER BY experience DESC) FROM profiles WHERE user_id=? AND guild_id=?", (user_id, guild_id,))
            output = cursor.fetchone()
            return output[0] if output else None

    @classmethod
    async def get_experience(self, user_id: int, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT IFNULL(experience, 0) FROM profiles WHERE user_id=? AND guild_id=?", (user_id, guild_id,))
            output = cursor.fetchone()
            return output[0] if output else 0

    @classmethod
    async def update_experience(self, user_id: int, guild_id: int, user_data: dict):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO profiles (user_id, guild_id) VALUES(?, ?)", (user_id, guild_id,))
            cursor.execute("UPDATE profiles SET experience=?, level=? WHERE user_id=? AND guild_id=?", (user_data['experience'], user_data['level'], user_id, guild_id,))