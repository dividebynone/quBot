from libs.sqlhandler import sqlconnect
from main import bot_path
import os

class CommandController(object):
    def __init__(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS disabled_commands (command_name BLOB NOT NULL, guild_id INTEGER NOT NULL, PRIMARY KEY (command_name, guild_id))")

    @classmethod
    async def disable_command(self, command_name: str, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO disabled_commands (command_name, guild_id) VALUES(?, ?)", (command_name, guild_id))

    @classmethod
    def is_disabled(self, command_name: str, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT command_name FROM disabled_commands WHERE command_name=? AND guild_id=?",(command_name, guild_id,))
            output = cursor.fetchone()
            return True if output else False

    @classmethod
    async def enable_command(self, command_name: str, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("DELETE FROM disabled_commands WHERE command_name=? AND guild_id=?",(command_name, guild_id,))

    @classmethod
    async def disabled_commands(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT command_name FROM disabled_commands WHERE guild_id=?",(guild_id,))
            output = cursor.fetchall()
            return [x[0] for x in output] if output else None

    @classmethod
    async def remove_disabled_commands(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("DELETE FROM disabled_commands WHERE guild_id=?",(guild_id,))

class CogController(object):
    def __init__(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS disabled_cogs (cog_name BLOB NOT NULL, guild_id INTEGER NOT NULL, PRIMARY KEY (cog_name, guild_id))")

    @classmethod
    async def disable_cog(self, cog_name: str, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO disabled_cogs (cog_name, guild_id) VALUES(?, ?)", (cog_name, guild_id))

    @classmethod
    def is_disabled(self, cog_name: str, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT cog_name FROM disabled_cogs WHERE cog_name=? AND guild_id=?",(cog_name, guild_id,))
            output = cursor.fetchone()
            return True if output else False

    @classmethod
    async def disabled_cogs(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT cog_name FROM disabled_cogs WHERE guild_id=?",(guild_id,))
            output = cursor.fetchall()
            return [x[0] for x in output] if output else None

    @classmethod
    async def enable_cog(self, cog_name: str, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("DELETE FROM disabled_cogs WHERE cog_name=? AND guild_id=?",(cog_name, guild_id,))
            output = cursor.fetchone()
            return True if output else False

    @classmethod
    async def remove_disabled_cogs(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("DELETE FROM disabled_cogs WHERE guild_id=?",(guild_id,))


