import sqlite3
import discord
import sys
import random
import string
import json

#Check if the bot 
def is_venv():
        return (hasattr(sys, 'real_prefix') or
                (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

#data.json initialization
async def data_get():
        with open('./data/data.json', 'r') as json_file:
                json_data = json.load(json_file)
        json_file.close()
        return json_data

async def data_set(json_dump: dict):
        with open('./data/data.json', 'w') as json_file: 
                json.dump(json_dump, json_file, indent=4, sort_keys=True,separators=(',', ': '))
        json_file.close()

#user.db database functions
db_connector = sqlite3.connect('./Databases/users.db')
db_cursor = db_connector.cursor()

async def user_init(user: discord.User):
    db_cursor.execute("INSERT OR IGNORE INTO users(userid, currency) VALUES(?, ?)", (user.id, '0'))
    db_connector.commit()

async def user_get(user: discord.User):
    db_cursor.execute("SELECT IfNull(currency,0), IfNull(daily_time,0) FROM users WHERE userid=?", (user.id,))
    db_output = list(db_cursor.fetchone())
    return_dict = dict(currency=db_output[0], daily_time=db_output[1])
    return return_dict

async def user_set(user: discord.User, dict_input):
    db_cursor.execute("UPDATE users SET currency=?, daily_time=? WHERE userid=?",(dict_input['currency'], dict_input['daily_time'], user.id))
    db_connector.commit()