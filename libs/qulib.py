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
                date_created BLOB,founderid BLOB,leaderid BLOB,settlement_name BLOB,treasury INTEGER,tech_attack INTEGER,\
                tech_defence INTEGER,member_list BLOB,settlement_size INTEGER,settlement_level INTEGER,tech_tree BLOB,\
                settlement_type TEXT,entry_fee INTEGER,settlement_wins INTEGER,settlement_losses INTEGER, settlement_xp INTEGER)")

def string_generator(size):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

async def conquest_get(get_string:str, input_data):
    with ContextManager('./Databases/conquest.db') as cursor:
        if get_string is 'user':
                cursor.execute("SELECT settlement_id,invite_string,date_created,founderid,leaderid,settlement_name,treasury,tech_attack,tech_defence,member_list,settlement_size,settlement_level,tech_tree,settlement_type,entry_fee,settlement_wins,settlement_losses,settlement_xp FROM conquest WHERE founderid=? OR leaderid=?", (input_data,input_data,))
        elif get_string is 'settlement':
                cursor.execute("SELECT settlement_id,invite_string,date_created,founderid,leaderid,settlement_name,treasury,tech_attack,tech_defence,member_list,settlement_size,settlement_level,tech_tree,settlement_type,entry_fee,settlement_wins,settlement_losses,settlement_xp FROM conquest WHERE settlement_name=?", (input_data,))
        elif get_string is 'code':
                cursor.execute("SELECT settlement_id,invite_string,date_created,founderid,leaderid,settlement_name,treasury,tech_attack,tech_defence,member_list,settlement_size,settlement_level,tech_tree,settlement_type,entry_fee,settlement_wins,settlement_losses,settlement_xp FROM conquest WHERE invite_string=?", (input_data,))
        else:
                print('FAILED TO GET FROM CONQUEST DATABASE')
                return None

        db_output = cursor.fetchone()
        if db_output is None:
                return None
        else:
                db_output = list(db_output)
                return_dict = dict(settlement_id=db_output[0], invite_string=db_output[1], date_created=db_output[2], founderid=db_output[3],
                                leaderid=db_output[4], settlement_name=db_output[5], treasury=db_output[6], tech_attack=db_output[7],
                                tech_defence=db_output[8], member_list=db_output[9], settlement_size=db_output[10], settlement_level=db_output[11],
                                tech_tree=db_output[12],settlement_type=db_output[13],entry_fee=db_output[14],settlement_wins=db_output[15],
                                settlement_losses=db_output[16],settlement_xp=db_output[17])
                return return_dict

async def conquest_set(get_string:str, input_data, dict_input):
    with ContextManager('./Databases/conquest.db') as cursor:
        if get_string is 'new':
                cursor.execute("INSERT OR IGNORE INTO conquest(founderid, leaderid, treasury, entry_fee, invite_string, date_created, tech_attack, tech_defence, settlement_name, settlement_level, tech_tree, settlement_type, settlement_size, member_list, settlement_wins, settlement_losses, settlement_xp) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                [input_data, input_data, dict_input["entry_fee"], dict_input["entry_fee"], dict_input["invite_string"],
                                dict_input["date_created"], '0', '0', dict_input["settlement_name"],'1', '0000000000', dict_input["settlement_type"],
                                '1',','.join(dict_input["member_list"]), 0, 0, 0])
        elif get_string is 'user':
                cursor.execute("UPDATE conquest SET founderid=?, leaderid=?, treasury=?, entry_fee=?, invite_string=?, date_created=?, tech_attack=?, tech_defence=?, settlement_name=?, settlement_level=?, tech_tree=?, settlement_type=?, settlement_size=?, member_list=?, settlement_wins=?, settlement_losses=?, settlement_xp=? WHERE founderid=? OR leaderid=?",
                                [dict_input["founderid"], dict_input["leaderid"], dict_input["treasury"], dict_input["entry_fee"], dict_input["invite_string"],
                                dict_input["date_created"], dict_input["tech_attack"], dict_input["tech_defence"], dict_input["settlement_name"], dict_input["settlement_level"], '0000000000', dict_input["settlement_type"],
                                dict_input["settlement_size"], dict_input["member_list"], dict_input["settlement_wins"], dict_input["settlement_losses"], dict_input["settlement_xp"], input_data, input_data])
        elif get_string is 'invite':
                cursor.execute("UPDATE conquest SET founderid=?, leaderid=?, treasury=?, entry_fee=?, invite_string=?, date_created=?, tech_attack=?, tech_defence=?, settlement_name=?, settlement_level=?, tech_tree=?, settlement_type=?, settlement_size=?, member_list=?, settlement_wins=?, settlement_losses=?, settlement_xp=? WHERE invite_string=?",
                                [dict_input["founderid"], dict_input["leaderid"], dict_input["treasury"], dict_input["entry_fee"], dict_input["invite_string"],
                                dict_input["date_created"], dict_input["tech_attack"], dict_input["tech_defence"], dict_input["settlement_name"], dict_input["settlement_level"], '0000000000', dict_input["settlement_type"],
                                dict_input["settlement_size"], dict_input["member_list"], dict_input["settlement_wins"], dict_input["settlement_losses"], dict_input["settlement_xp"], input_data])

async def conquest_get_leaderboard():
    with ContextManager('./Databases/conquest.db') as cursor:
        cursor.execute("SELECT settlement_id, settlement_name, settlement_xp FROM conquest")
        db_output = cursor.fetchall()
        if db_output != None:
            db_output = list(db_output)
            db_output.sort(key=lambda info: info[2], reverse=True)
        return db_output