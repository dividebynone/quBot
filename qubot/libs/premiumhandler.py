from libs.sqlhandler import sqlconnect
from discord.ext import commands
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


class PremiumHandler(object):

    def __init__(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, expires INTEGER)")

    @classmethod
    async def get_expiration(self, user_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES(?)", (user_id,))
            cursor.execute("SELECT expires FROM users WHERE user_id=?", (user_id,))
            output = cursor.fetchone()
            return output[0] if output else None

    @classmethod
    async def update_premium(self, user_id: int, expiration_unix: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES(?)", (user_id,))
            cursor.execute("UPDATE users SET expires=? WHERE user_id=?", (expiration_unix, user_id))
            return True if cursor.rowcount > 0 else False

    @classmethod
    async def end_premium(self, user_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))

    @classmethod
    async def is_premium(self, user_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'premium.db')) as cursor:
            cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
            output = cursor.fetchone()
            return True if output else False
