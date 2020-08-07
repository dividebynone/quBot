from discord.ext import commands
from datetime import datetime, timedelta
import libs.prefixhandler as prefixhandler
import libs.localizations as localizations
import logging
import os
import sys
import sqlite3
import configparser
import json

#-----------------------------------#
# Utility functions

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

#-----------------------------------#
# Path checks and initalization

bot_path = os.path.dirname(os.path.realpath(__file__))

#TODO: Move directory creation outside of main script file

subfolders = {'databases', 'data', 'data/localization', 'data/images', 'logs', 'libs', 'modules'}
makefolders(bot_path, subfolders)

open(os.path.join(bot_path, 'libs', '__init__.py'), 'a').close()
open(os.path.join(bot_path, 'modules', '__init__.py'), 'a').close()

#-----------------------------------#
# Main config file initialization

if not os.path.isfile(os.path.join(bot_path, 'config.ini')):
    config = configparser.ConfigParser(allow_no_value=False)
    config.optionxform = str
    config['Credentials'] = {'Token': '<Enter token here>'}
    config['Commands'] = {'CommandPrefix': '!',
                          'MaximumPrefixLength': '10'}
    config['Language'] = {'CommandLanguageCode': 'en-US',
                          'ConsoleLanguageCode': 'en-US'}
    config['Logging'] = {'LoggerLevel': 'DEBUG',
                         'LogsAutoDeleteDays': '7'}

    with open(os.path.join(bot_path, 'config.ini'), 'w', encoding="utf_8") as config_file:
        config.write(config_file)
        config_file.close()
        print("Successfully created config.ini file. Please configure the file before starting the bot again.")
        sys.exit()
else:
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
    with open(os.path.join(bot_path, 'config.ini'), 'r', encoding="utf_8") as config_file:
        config.read_file(config_file)
        tokenid = config.get('Credentials', 'Token')
        prefix = config.get('Commands', 'CommandPrefix')
        max_prefix_length = safe_cast(config.get('Commands', 'MaximumPrefixLength'), int, 10)
        languagecode = config.get('Language', 'CommandLanguageCode')
        consolelang = config.get('Language', 'ConsoleLanguageCode')
        logginglevel = config.get('Logging', 'LoggerLevel')
        log_days_delete = config.get('Logging', 'LogsAutoDeleteDays')
        config_file.close()

#-----------------------------------#
# Logging initialization

logging_dict = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20, 'DEBUG':10}
date_today = datetime.today().replace(microsecond=0)
date_today = date_today.strftime("%d-%m-%Y-%Hh-%Mm-%Ss")
logger = logging.getLogger('discord')
if logginglevel in logging_dict:
    logger.setLevel(logging_dict[logginglevel])
    print(f'Logging level has been set to [{logginglevel}]')
else:
    logger.setlevel(logging.DEBUG)
    print(f'ERROR: Failed to change logging level to [{logginglevel}]. Not a valid logging level. Converting back to DEBUG mode')
log_handler = logging.FileHandler(filename=os.path.join(bot_path, f'logs/log-{date_today}.log'), encoding='utf-8', mode='w')
log_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(log_handler)

#-----------------------------------#
#JSON files initialization/writing/loading

with open(os.path.join(bot_path, f'data/localization/language_{languagecode}.json'), 'r', encoding="utf_8") as json_file:
    lang = json.load(json_file)
json_file.close()

with open(os.path.join(bot_path, 'data/data.json'), 'r') as json_file:
    json_data = json.load(json_file)
json_file.close()

version = json_data["appVersion"]

#-----------------------------------#
#Localization

def get_lang(guild_id: int):
    localization = localizations.Localizations()
    language = localization.get_language(guild_id, languagecode)
    with open(os.path.join(bot_path, f'data/localization/language_{language}.json'), 'r', encoding="utf_8") as json_file:
        return_dict = json.load(json_file)
    json_file.close()
    return return_dict

#-----------------------------------#
#Creating modules.mdls to store loaded modules

if not os.path.isfile(os.path.join(bot_path, 'data/modules.mdls')):
    with open(os.path.join(bot_path, 'data/modules.mdls'), 'w') as modules_file:
        print("[modules.mdls] file not found. Creating a new file")
        #The core module is added upon file creation
        modules_file.write("Core\n")
        modules_file.close()

with open(os.path.join(bot_path, 'data/modules.mdls'), 'r') as modules_file:
    modules_list = modules_file.read().split()
    modules_file.close()

module_directory_list = [os.path.splitext(i)[0] for i in os.listdir(os.path.join(bot_path, 'modules'))]
modules = [x for x in modules_list if x in module_directory_list]
modules = [f'modules.{x}' for x in modules]

#-----------------------------------#
#Deleting old logs. All logs older than a week will be deleted by default

def old_logs_delete(days_int: int = 7):
    datetime_seconds = (datetime.now() - timedelta(days=days_int)).timestamp()
    os.chdir(os.path.join(bot_path, 'logs'))
    for file_ in os.listdir():
        file_path = os.path.join(os.getcwd(), file_)
        file_stats = os.stat(file_path)
        if file_stats.st_mtime <= datetime_seconds:
            os.remove(file_path)
            print(f'The system has deleted [{file_}]: The file was either marked for autodeletion or empty.')
    os.chdir(bot_path)

#-----------------------------------#
#Bot Server Prefixes

def get_prefix(bot, message):
    prefixes = prefixhandler.PrefixHandler()
    return_prefix = prefixes.get_prefix(message.guild.id, prefix) if message.guild else prefix
    return commands.when_mentioned_or(return_prefix)(bot, message)

#-----------------------------------#
#Bot initialization

bot = commands.AutoShardedBot(command_prefix = get_prefix)
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



        





