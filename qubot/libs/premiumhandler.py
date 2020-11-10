from libs.sqlhandler import sqlconnect
from discord.ext import commands
import enum
import main
import os


class PremiumOnlyException(commands.CheckFailure):
    pass


# Custom Premium Only Check
def premium_only():
    async def predicate(ctx):
        handler = PremiumHandler()
        if await handler.is_premium(ctx.author.id):
            return True
        else:
            raise PremiumOnlyException(f"Failed to execute the command '{ctx.command.qualified_name}'. User does not have premium access.")
    return commands.check(predicate)


class PremiumTier(enum.IntEnum):
    Standard = 1
    Plus = 2


class PremiumHandler(object):

    def __init__(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, expires INTEGER, tier INTEGER)")

    @classmethod
    async def get_expiration(self, user_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("SELECT expires FROM users WHERE user_id=?", (user_id,))
            output = cursor.fetchone()
            return output[0] if output else None

    @classmethod
    async def update_premium(self, user_id: int, expiration_unix: int, tier: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES(?)", (user_id,))
            cursor.execute("UPDATE users SET expires=?, tier=? WHERE user_id=?", (expiration_unix, tier, user_id))
            return True if cursor.rowcount > 0 else False

    @classmethod
    async def get_status(self, user_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("SELECT expires, tier FROM users WHERE user_id=?", (user_id,))
            output = cursor.fetchone()
            return output if output else None

    @classmethod
    async def get_tier(self, user_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("SELECT tier FROM users WHERE user_id=?", (user_id,))
            output = cursor.fetchone()
            return output[0] if output else None

    @classmethod
    async def end_premium(self, user_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))

    @classmethod
    async def clear_expired(self, unix_time):
        with sqlconnect(os.path.join(bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("DELETE FROM users WHERE expires <= ?", (unix_time,))

    @classmethod
    async def is_premium(self, user_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
            output = cursor.fetchone()
            return True if output else False
