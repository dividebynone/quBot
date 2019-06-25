from discord.ext import commands
from datetime import datetime, timedelta
from libs.qulib import is_venv
import logging
import os
import sys
import sqlite3
import configparser
import json

#-----------------------------------#
#Path checks and initalization
bot_path = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists('./Databases'):
    os.makedirs('./databases')

if not os.path.exists('./data'):
    os.makedirs('./data')
    os.makedirs('./data/localization')
    os.makedirs('./data/images')

if not os.path.exists('./logs'):
    os.makedirs('./logs')

if not os.path.exists('./libs'):
    os.makedirs('./libs')
    open('./Modules/__init__.py', 'a').close()

if not os.path.exists('./modules'):
    os.makedirs('./modules')
    open('./Modules/__init__.py', 'a').close()

#-----------------------------------#
#Main config file initialization 
if not os.path.isfile('config.ini'):
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
    config['Credentials'] = {'Token': '<Enter token here>',
                                '## You can find your token key here: https://discordapp.com/developers/applications/': None,
                                '# The token is necessary in order to establish a connection between your bot application and this software.': None}
    config['Commands'] = {'CommandPrefix': '!',
                            '## The prefix is what triggers the bot to execute commands. Consider changing it if conflicts with other bots occur.': None}
    config['Language'] = {'CommandLanguageCode': 'en-US',
                            'ConsoleLanguageCode': 'en-US'}
    config['Logging'] = {'LoggerLevel': 'DEBUG',
                            'LogsAutoDeleteDays': 7,
                            '## This software auto-deletes all logs older than the days specified above.': None,
                            '# By default this value is 7(it deletes all logs older than a week)': None}

    with open('config.ini', 'w', encoding="utf_8") as config_file:
        config.write(config_file)
        config_file.close()
        print("Successfully created config.ini file. Please configure the file before starting the bot again.")
        sys.exit()
else:
    config = configparser.ConfigParser(allow_no_value=True)
    with open('config.ini', 'r', encoding="utf_8") as config_file:
        config.read_file(config_file)
        tokenid = config.get('Credentials', 'Token')
        prefix = config.get('Commands', 'CommandPrefix')
        languagecode = config.get('Language', 'CommandLanguageCode')
        consolelang = config.get('Language', 'ConsoleLanguageCode')
        logginglevel = config.get('Logging', 'LoggerLevel')
        log_days_delete = config.get('Logging', 'LogsAutoDeleteDays')
        config_file.close()

#-----------------------------------#
#Logging initialization
logging_dict = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20, 'DEBUG':10}
date_today = datetime.today().replace(microsecond=0)
date_today = date_today.strftime("%d-%m-%Y-%Hh-%Mm-%Ss")
logger = logging.getLogger('discord')
if logginglevel in logging_dict:
    logger.setLevel(logging_dict[logginglevel])
    print(f'Logging level has been set to [{logginglevel}]')
else:
    logger.setlevel(logging.DEBUG)
log_handler = logging.FileHandler(filename=f'./logs/log-{date_today}.log', encoding='utf-8', mode='w')
log_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(log_handler)

#-----------------------------------#
#Creating main databases
#Users(Database)
users_connector = sqlite3.connect('./Databases/users.db')
users_cursor = users_connector.cursor()
users_cursor.execute("CREATE TABLE IF NOT EXISTS users(userid INTEGER PRIMARY KEY , currency INTEGER, daily_time BLOB)")
users_cursor.close()
users_connector.close()

#Servers(Database)
servers_connector = sqlite3.connect('./Databases/servers.db')
servers_cursor = servers_connector.cursor()
servers_cursor.execute("CREATE TABLE IF NOT EXISTS servers(guildid INTEGER PRIMARY KEY, blacklist BLOB)")
servers_cursor.close()
servers_connector.close()

#-----------------------------------#
#JSON files initialization/writing/loading
json_data_input = {
        "appVersion": "0.1.1a",
        }

json_lang_en = {
        "temp": "temp",
        }

with open('./data/data.json', 'w') as json_file: 
    json_file.write(json.dumps(json_data_input, indent=4, sort_keys=True,separators=(',', ': ')))
json_file.close()#To be deleted in the future

with open('./data/data.json', 'r') as json_file:
    json_data = json.load(json_file)
json_file.close()

with open('./data/localization/language_{}.json'.format(languagecode), 'w') as json_file:
    json_file.write(json.dumps(json_lang_en, indent=4, sort_keys=True,separators=(',', ': ')))
json_file.close()#To be deleted in the future

with open('./data/localization/language_{}.json'.format(languagecode), 'r') as json_file:
    json_lang = json.load(json_file)
json_file.close()

#-----------------------------------#
#Creating modules.mdls to store loaded modules
if not os.path.isfile('./data/modules.mdls'):
    with open('./data/modules.mdls', 'w') as modules_file:
        print("[modules.mdls] file not found. Creating a new file")
        #The core module is added upon file creation
        modules_file.write("Core\n")
        modules_file.close()

with open('./data/modules.mdls', 'r') as modules_file:
    modules_list = modules_file.read().split()
    modules_file.close()

module_directory_list = [os.path.splitext(i)[0] for i in os.listdir('./modules')]
modules = [x for x in modules_list if x in module_directory_list]
modules = [f'modules.{x}' for x in modules]

#-----------------------------------#
#Deleting old logs. All logs older than a week will be deleted by default
def old_logs_delete(days_int: int = 7):
    datetime_seconds = (datetime.now() - timedelta(days=days_int)).timestamp()
    os.chdir('logs')
    for file_ in os.listdir():
        file_path = os.path.join(os.getcwd(), file_)
        file_stats = os.stat(file_path)
        if file_stats.st_mtime <= datetime_seconds or file_stats.st_size == 0:
            os.remove(file_path)
            print(f'The system has deleted [{file_}]: The file was either marked for autodeletion or empty.')
    os.chdir(os.pardir)
    
#-----------------------------------#
#Bot initialization
bot = commands.AutoShardedBot(command_prefix= prefix)
bot_starttime = datetime.today().replace(microsecond=0)

#-----------------------------------#
#Bot startup events
@bot.event
async def on_shard_ready(shard_id):
    print(f'Shard {shard_id} ready.')
 
@bot.event
async def on_ready():
    print("The bot has sucessfully established a connection with Discord API. Booting up...")
    server_count = 0
    for _ in bot.guilds:
        server_count+= 1
    print("Bot is currently in {} servers".format(server_count))

#-----------------------------------#
if __name__=="__main__":

    old_logs_delete(int(log_days_delete))

    #virtualenv check
    if is_venv():
        print('This bot is currently running inside a virtual environment.')

    #Loading bot modules
    for module in modules:
        try:
            bot.load_extension(module)
            failed_load = False
        except Exception as e:
            print("{} failed to load.\n{}: {}".format(module, type(e).__name__, e))
            failed_load = True
        finally:
            if failed_load == True:
                failed_load = False
                print("Retrying to load {}".format(module))
                bot.load_extension(module)

    #Run
    print("Bot starting up in directory {}".format(bot_path))
    bot.run(tokenid)



        





