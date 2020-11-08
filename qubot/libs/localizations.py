from libs.sqlhandler import sqlconnect
import main
import os


class Localizations(object):

    def __init__(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS servers(guild_id INTEGER PRIMARY KEY, prefix BLOB, language BLOB)")

    @classmethod
    def set_language(self, guild_id: int, language: str):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO servers (guild_id) VALUES(?)", (guild_id,))
            cursor.execute("UPDATE servers SET language=? WHERE guild_id=?", (language, guild_id,))

    @classmethod
    def get_language(self, guild_id: int, default_language: str):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT IFNULL(language, ?) FROM servers WHERE guild_id=?", (default_language, guild_id,))
            output = cursor.fetchone()
            return str(output[0]) if output else default_language

    @classmethod
    def remove_guild(self, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("DELETE FROM servers WHERE guild_id=?", (guild_id,))
