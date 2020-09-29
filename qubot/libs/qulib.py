from libs.sqlhandler import sqlconnect
from main import bot_path
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

def makefolders(root_path, folders_list):
    for folder in folders_list:
        os.makedirs(os.path.join(root_path, folder), exist_ok=True)

def safe_cast(value, to_type, default=None):
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default

#data.json initialization
def sync_data_get():
    with open(os.path.join(bot_path, 'data','data.json'), 'r') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    return json_data

async def data_get():
    with open(os.path.join(bot_path, 'data','data.json'), 'r') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    return json_data

def sync_data_set(json_dump: dict):
    with open(os.path.join(bot_path, 'data','data.json'), 'w') as json_file: 
        json.dump(json_dump, json_file, indent=4, sort_keys=True,separators=(',', ': '))
    json_file.close()

async def data_set(json_dump: dict):
    with open(os.path.join(bot_path, 'data','data.json'), 'w') as json_file: 
        json.dump(json_dump, json_file, indent=4, sort_keys=True,separators=(',', ': '))
    json_file.close()

#Modules configuration

def get_module_config():
    if not os.path.isfile(os.path.join(bot_path, 'data', 'modules.json')):
        print("Creating missing modules.json file...")
        with open(os.path.join(bot_path, 'data','modules.json'), 'w+') as json_file:
            json.dump({}, json_file, indent=4, sort_keys=True, separators=(',', ': '))
        json_file.close()

    with open(os.path.join(bot_path, 'data','modules.json'), 'r') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    return json_data

def update_module_config(json_dump: dict):
    with open(os.path.join(bot_path, 'data', 'modules.json'), 'w') as json_file: 
        json.dump(json_dump, json_file, indent=4, sort_keys=True, separators=(',', ': '))
    json_file.close()

def module_configuration(module_name: str, is_restricted: bool, module_dependencies: list):
    module_directory_list = [os.path.splitext(i)[0] for i in os.listdir(os.path.join(bot_path, 'modules'))]

    module_config = get_module_config()
    if is_restricted and module_name not in module_config.setdefault("restricted_modules", []):
        module_config.setdefault("restricted_modules", []).append(module_name)
    if len(module_dependencies) > 0:
        for dependency in module_dependencies:
            if dependency in module_directory_list and dependency not in module_config.setdefault("dependencies", {}).setdefault(module_name, []):
                module_config.setdefault("dependencies", {}).setdefault(module_name, []).append(dependency)
    else:
        module_config.setdefault("dependencies", {}).pop(module_name, None)
    update_module_config(module_config)

#Exports configuration

def export_commands(json_dump: dict):
    makefolders(bot_path, ['exports'])
    with open(os.path.join(bot_path, 'exports', 'commands.json'), 'w') as json_file: 
        json.dump(json_dump, json_file, indent=4, sort_keys=True, separators=(',', ': '))
    json_file.close()

#Database folder creation(if missing) #TODO: Delete in the future (duplicate code <-> main.py)
if not os.path.exists(os.path.join(bot_path, 'databases')):
    os.makedirs(os.path.join(bot_path, 'databases'), exist_ok=True)

#Creating needed database files(if missing)
def user_database_init():
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS users(userid INTEGER PRIMARY KEY , currency INTEGER, daily_time BLOB)")

async def user_get(user: discord.User):
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("INSERT OR IGNORE INTO users(userid, currency) VALUES(?, ?)", (user.id, '0'))
        cursor.execute("SELECT IfNull(currency,0), IfNull(daily_time,0) FROM users WHERE userid=?", (user.id,))
        db_output = list(cursor.fetchone())
        return_dict = dict(currency=db_output[0], daily_time=db_output[1])
        return return_dict

async def user_set(user: discord.User, dict_input):
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("INSERT OR IGNORE INTO users(userid, currency) VALUES(?, ?)", (user.id, '0'))
        cursor.execute("UPDATE users SET currency=?, daily_time=? WHERE userid=?",
                        (dict_input['currency'], dict_input['daily_time'], user.id))
   
def string_generator(size):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))