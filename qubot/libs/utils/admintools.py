from libs.sqlhandler import sqlconnect
from main import bot_path
import os

class Reports(object):

    def __init__(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS reports(guild_id INTEGER PRIMARY KEY, report_channel INTEGER)")

    @classmethod
    async def set_channel(self, guild_id: int, channel_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR REPLACE INTO reports(guild_id, report_channel) VALUES(?, ?)", (guild_id, channel_id,))

    @classmethod
    async def get_channel(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT report_channel FROM reports WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            return output[0] if output else None

    @classmethod
    async def disable(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("DELETE FROM reports WHERE guild_id=?",(guild_id,))

class Warnings(object):

    def __init__(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS warnings(user_id INTEGER, warning BLOB, warned_by INTEGER, guild_id INTEGER)")

    @classmethod
    async def add_warning(self, user_id: int, warning: str, warned_by: int, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT INTO warnings (user_id, warning, warned_by, guild_id) VALUES(?, ?, ?, ?)", (user_id, warning, warned_by,guild_id,))

    @classmethod
    async def get_warnings(self, guild_id: int, user_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT warning, warned_by FROM warnings WHERE guild_id=? AND user_id=?",(guild_id, user_id,))
            output = cursor.fetchall()
            return output

    @classmethod
    async def get_warning_count(self, guild_id: int, user_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT COUNT(ALL warning) FROM warnings WHERE guild_id=? AND user_id=?",(guild_id, user_id,))
            output = cursor.fetchone()
            return int(output[0]) if output else 0

    @classmethod
    async def reset_warnings(self, guild_id: int, user_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("DELETE FROM warnings WHERE guild_id=? AND user_id=?",(guild_id, user_id,))

    @classmethod
    async def delete_warning(self, guild_id: int, user_id: int, index: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT rowid FROM warnings WHERE guild_id=? AND user_id=?",(guild_id, user_id,))
            output = cursor.fetchall()
            if output and (index + 1) <= len(output):
                rowid = int(output[index][0])
                cursor.execute("DELETE FROM warnings WHERE rowid=? AND guild_id=? AND user_id=?",(rowid, guild_id, user_id,))
            else:
                raise IndexError       

class AutoWarningActions(object):

    def __init__(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS autoactions(guild_id INTEGER PRIMARY KEY, auto_mute INTEGER, auto_kick INTEGER, auto_ban INTEGER)")

    @classmethod
    async def set_value(self, guild_id: int, action: str, n: int):
        if action.lower() == 'mute':
            await self.set_automute(guild_id, n)
        elif action.lower() == 'kick':
            await self.set_autokick(guild_id, n)
        elif action.lower() == 'ban':
            await self.set_autoban(guild_id, n)

    @classmethod
    async def disable_autoaction(self, guild_id: int, action: str):
        if action.lower() == 'mute':
            await self.set_automute(guild_id, None)
        elif action.lower() == 'kick':
            await self.set_autokick(guild_id, None)
        elif action.lower() == 'ban':
            await self.set_autoban(guild_id, None)

    @classmethod
    async def set_autoban(self, guild_id: int, ban: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO autoactions (guild_id) VALUES(?)", (guild_id,))
            cursor.execute("UPDATE autoactions SET auto_ban=? WHERE guild_id=?", (ban, guild_id,))

    @classmethod
    async def set_autokick(self, guild_id: int, kick: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO autoactions (guild_id) VALUES(?)", (guild_id,))
            cursor.execute("UPDATE autoactions SET auto_kick=? WHERE guild_id=?", (kick, guild_id,))

    @classmethod
    async def set_automute(self, guild_id: int, mute: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO autoactions (guild_id) VALUES(?)", (guild_id,))
            cursor.execute("UPDATE autoactions SET auto_mute=? WHERE guild_id=?", (mute, guild_id,))

    @classmethod
    async def get_actions(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT auto_mute, auto_kick, auto_ban FROM autoactions WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            return output

class MuteRole(object):

    def __init__(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS mute_roles(guild_id INTEGER PRIMARY KEY, mute_role INTEGER)")

    @classmethod
    async def set_mute_role(self, guild_id: int, role_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR REPLACE INTO mute_roles(guild_id, mute_role) VALUES(?, ?)", (guild_id, role_id,))

    @classmethod
    async def get_mute_role(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT mute_role FROM mute_roles WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            return output[0] if output else None

class BlacklistedUsers(object):
    def __init__(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS blacklisted_users(user_id INTEGER NOT NULL, guild_id INTEGER NOT NULL, PRIMARY KEY (user_id, guild_id))")

    @classmethod
    async def blacklist(self, user_id: int, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO blacklisted_users (user_id, guild_id) VALUES(?, ?)", (user_id, guild_id))

    @classmethod
    def is_blacklisted(self, user_id: int, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT user_id FROM blacklisted_users WHERE user_id=? AND guild_id=?",(user_id, guild_id,))
            output = cursor.fetchone()
            return True if output else False

    @classmethod
    async def remove_blacklist(self, user_id: int, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("DELETE FROM blacklisted_users WHERE user_id=? AND guild_id=?",(user_id, guild_id,))

    @classmethod
    async def remove_blacklist_guild(self, guild_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("DELETE FROM blacklisted_users WHERE guild_id=?",(guild_id,))