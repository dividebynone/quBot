import sqlite3
import discord
import os
import sys
import random
import string
import json

#Check if the bot is running inside a virtual environment
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

#Database folder creation(if missing)
if not os.path.exists('./Databases'):
    os.makedirs('./databases')

class ContextManager(object):
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        self.conn.commit()
        self.conn.close()

#Creating needed database files(if missing)
def user_database_init():
    with ContextManager('./Databases/users.db') as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS users(userid INTEGER PRIMARY KEY , currency INTEGER, daily_time BLOB)")

async def user_init(user: discord.User):
    with ContextManager('./Databases/users.db') as cursor:
        cursor.execute("INSERT OR IGNORE INTO users(userid, currency) VALUES(?, ?)", (user.id, '0'))

async def user_get(user: discord.User):
    with ContextManager('./Databases/users.db') as cursor:
        cursor.execute("SELECT IfNull(currency,0), IfNull(daily_time,0) FROM users WHERE userid=?", (user.id,))
        db_output = list(cursor.fetchone())
        return_dict = dict(currency=db_output[0], daily_time=db_output[1])
        return return_dict

async def user_set(user: discord.User, dict_input):
    with ContextManager('./Databases/users.db') as cursor:
        cursor.execute("UPDATE users SET currency=?, daily_time=? WHERE userid=?",
                        (dict_input['currency'], dict_input['daily_time'], user.id))

#Conquest
        
def conquest_database_init():
    with ContextManager('./Databases/conquest.db') as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS conquest(settlement_id INTEGER PRIMARY KEY ,invite_string BLOB,\
                date_created BLOB,founderid BLOB,leaderid BLOB,name BLOB,treasury INTEGER,tech_attack INTEGER,\
                tech_defence INTEGER, size INTEGER, level INTEGER,tech_tree BLOB,\
                type TEXT,entry_fee INTEGER, wins INTEGER, losses INTEGER, experience INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS members(userid INTEGER PRIMARY KEY, settlement_id INTEGER)")

def string_generator(size):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

async def conquest_get(get_string:str, input_data):
    with ContextManager('./Databases/conquest.db') as cursor:
        if get_string is 'user':
                cursor.execute("SELECT * FROM conquest WHERE founderid=? OR leaderid=?", (input_data,input_data,))
        elif get_string is 'settlement':
                cursor.execute("SELECT * FROM conquest WHERE name=?", (input_data,))
        elif get_string is 'code':
                cursor.execute("SELECT * FROM conquest WHERE invite_string=?", (input_data,))
        else:
                print('FAILED TO GET FROM CONQUEST DATABASE')
                return None

        db_output = cursor.fetchone()
        if db_output is None:
                return None
        else:
                db_output = list(db_output)
                return_dict = dict(settlement_id=db_output[0], invite_string=db_output[1], date_created=db_output[2], founderid=db_output[3],
                                leaderid=db_output[4], name=db_output[5], treasury=db_output[6], tech_attack=db_output[7],
                                tech_defence=db_output[8], size=db_output[9], level=db_output[10],
                                tech_tree=db_output[11], type=db_output[12], entry_fee=db_output[13], wins=db_output[14],
                                losses=db_output[15], experience=db_output[16])
                return return_dict

async def conquest_set(get_string:str, input_data, dict_input):
    with ContextManager('./Databases/conquest.db') as cursor:
        if get_string is 'new':
            cursor.execute("INSERT OR IGNORE INTO conquest(founderid, leaderid, treasury, entry_fee, invite_string, date_created, tech_attack, tech_defence, name, level, tech_tree, type, size, wins, losses, experience) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            [input_data, input_data, dict_input["entry_fee"], dict_input["entry_fee"], dict_input["invite_string"],
                            dict_input["date_created"], '0', '0', dict_input["name"],'1', '0000000000', dict_input["type"],
                            '1', 0, 0, 0])
            return cursor.lastrowid
        elif get_string is 'user':
            cursor.execute("UPDATE conquest SET founderid=?, leaderid=?, treasury=?, entry_fee=?, invite_string=?, date_created=?, tech_attack=?, tech_defence=?, name=?, level=?, tech_tree=?, type=?, size=?, wins=?, losses=?, experience=? WHERE founderid=? OR leaderid=?",
                            [dict_input["founderid"], dict_input["leaderid"], dict_input["treasury"], dict_input["entry_fee"], dict_input["invite_string"],
                            dict_input["date_created"], dict_input["tech_attack"], dict_input["tech_defence"], dict_input["name"], dict_input["level"], '0000000000', dict_input["type"],
                            dict_input["size"], dict_input["wins"], dict_input["losses"], dict_input["experience"], input_data, input_data])
        elif get_string is 'invite':
            cursor.execute("UPDATE conquest SET founderid=?, leaderid=?, treasury=?, entry_fee=?, invite_string=?, date_created=?, tech_attack=?, tech_defence=?, name=?, level=?, tech_tree=?, type=?, size=?, wins=?, losses=?, experience=? WHERE invite_string=?",
                            [dict_input["founderid"], dict_input["leaderid"], dict_input["treasury"], dict_input["entry_fee"], dict_input["invite_string"],
                            dict_input["date_created"], dict_input["tech_attack"], dict_input["tech_defence"], dict_input["name"], dict_input["level"], '0000000000', dict_input["type"],
                            dict_input["size"], dict_input["wins"], dict_input["losses"], dict_input["experience"], input_data])
    return None

async def conquest_get_leaderboard():
    with ContextManager('./Databases/conquest.db') as cursor:
        cursor.execute("SELECT settlement_id, name, experience FROM conquest")
        db_output = cursor.fetchall()
        if db_output != None:
            db_output = list(db_output)
            db_output.sort(key=lambda info: info[2], reverse=True)
        return db_output

async def conquest_member_init(user: discord.User):
    with ContextManager('./Databases/conquest.db') as cursor:
        cursor.execute("INSERT OR IGNORE INTO members(userid, settlement_id) VALUES(?, ?)", (user.id, None))

async def conquest_add_member(user: discord.User, settlement_id: int):
    with ContextManager('./Databases/conquest.db') as cursor:
        cursor.execute("UPDATE members SET settlement_id=? WHERE userid=?", (settlement_id, user.id))

async def conquest_remove_member(user: discord.User):
    with ContextManager('./Databases/conquest.db') as cursor:
        cursor.execute("UPDATE members SET settlement_id=? WHERE userid=?", (None, user.id))

async def conquest_find_code(input: str):
    with ContextManager('./Databases/conquest.db') as cursor:
        cursor.execute("SELECT invite_string FROM conquest WHERE invite_string=?", (input,))
        db_output = cursor.fetchone()
        return db_output[0] if db_output != None else None

async def conquest_new_code(new_code: str, userID : str):
    with ContextManager('./Databases/conquest.db') as cursor:
        cursor.execute("UPDATE conquest SET invite_string=? WHERE founderid=? OR leaderid=?", (new_code, userID, userID,))
        return True if cursor.rowcount > 0 else False
                        