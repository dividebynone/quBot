from libs.sqlhandler import sqlconnect
import main
import os

class PrefixHandler(object):

    def __init__(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS servers(guild_id INTEGER PRIMARY KEY, prefix BLOB, language BLOB)")

    @classmethod
    def set_prefix(self, guild_id: int, prefix: str):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO servers (guild_id) VALUES(?)", (guild_id,))
            cursor.execute("UPDATE servers SET prefix=? WHERE guild_id=?", (prefix, guild_id,))

    @classmethod
    def get_prefix(self, guild_id: int, default_prefix: str):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT IFNULL(prefix, ?) FROM servers WHERE guild_id=?",(default_prefix, guild_id,))
            output = cursor.fetchone()
            return str(output[0]) if output else default_prefix

    @classmethod
    def remove_guild(self, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("DELETE FROM servers WHERE guild_id=?",(guild_id,))