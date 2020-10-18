from libs.sqlhandler import sqlconnect
from main import bot_path
import os

class ServerToggles(object):

    def __init__(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS toggles(guild_id INTEGER PRIMARY KEY, greeting_status INTEGER, bye_status INTEGER, greeting_msg BLOB, bye_msg BLOB, greeting_cid INTEGER, bye_cid INTEGER)")

    #Wipe guild data
    @classmethod
    async def wipe_guild_data(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("DELETE FROM toggles WHERE guild_id=?", (guild_id,))

    #Message channel controls

    @classmethod
    async def set_greetings_channel(self, guild_id: int, channel_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO toggles (guild_id) VALUES(?)", (guild_id,))
            cursor.execute("UPDATE toggles SET greeting_cid=? WHERE guild_id=?", (channel_id, guild_id,))

    @classmethod
    async def set_bye_channel(self, guild_id: int, channel_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO toggles (guild_id) VALUES(?)", (guild_id,))
            cursor.execute("UPDATE toggles SET bye_cid=? WHERE guild_id=?", (channel_id, guild_id,))

    @classmethod
    async def get_greetings_channel(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT greeting_cid FROM toggles WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            return output[0] if output != None else None

    @classmethod
    async def get_bye_channel(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT bye_cid FROM toggles WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            return output[0] if output != None else None

    #Greetings toggle controls

    @classmethod
    async def get_greet_status(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT greeting_status FROM toggles WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            return output[0] if output != None else None

    @classmethod
    async def enable_greeting(self, guild_id: int, send_to_dms: bool):
        #None = Disabled | 1 = Enabled | 2 = Enabled (DMs)
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            status = 2 if send_to_dms else 1
            cursor.execute("INSERT OR IGNORE INTO toggles (guild_id) VALUES(?)", (guild_id,))
            cursor.execute("UPDATE toggles SET greeting_status=? WHERE guild_id=?", (status, guild_id,))

    @classmethod
    async def disable_greeting(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("UPDATE toggles SET greeting_status=? WHERE guild_id=?", (None, guild_id,))

    @classmethod
    async def set_greet_msg(self, guild_id: int, message: str):
        if len(message) > 0:
            with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
                cursor.execute("UPDATE toggles SET greeting_msg=? WHERE guild_id=?", (message, guild_id,))
        else:
            raise ValueError("[ServerToggles] Invalid server greeting message.")

    @classmethod
    async def reset_greet_msg(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("UPDATE toggles SET greeting_msg=? WHERE guild_id=?", (None, guild_id,))

    @classmethod
    async def has_custom_greeting(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT greeting_msg FROM toggles WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            if output:
                return True if output[0] != None else False
            else:
                return False

    @classmethod
    async def get_custom_greeting(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT greeting_msg FROM toggles WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            return output[0] if output else None

    #Goodbye toggle controls

    @classmethod
    async def get_bye_status(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT bye_status FROM toggles WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            return output[0] if output != None else None

    @classmethod
    async def enable_goodbye(self, guild_id: int):
        #None = Disabled | 1 = Enabled
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO toggles (guild_id) VALUES(?)", (guild_id,))
            cursor.execute("UPDATE toggles SET bye_status=? WHERE guild_id=?", (1, guild_id,))
    
    @classmethod
    async def disable_goodbye(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("UPDATE toggles SET bye_status=? WHERE guild_id=?", (None, guild_id,))

    @classmethod
    async def set_bye_msg(self, guild_id: int, message: str):
        if len(message) > 0:
            with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
                cursor.execute("UPDATE toggles SET bye_msg=? WHERE guild_id=?", (message, guild_id,))
        else:
            raise ValueError("[ServerToggles] Invalid server goodbye message.")

    #TEMP V
    @classmethod
    async def reset_bye_msg(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("UPDATE toggles SET bye_msg=? WHERE guild_id=?", (None, guild_id,))

    @classmethod
    async def has_custom_goodbye(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT bye_msg FROM toggles WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            if output:
                return True if output[0] != None else False
            else:
                return False

    @classmethod
    async def get_custom_goodbye(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT bye_msg FROM toggles WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            return output[0] if output else None