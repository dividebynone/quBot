from discord.ext import commands
from datetime import datetime, timedelta
import logging
import os
import sys
import sqlite3
import configparser
import json

#Path checks and initalization
def paths_init(): 
    paths_init.bot_path = os.path.dirname(os.path.realpath(__file__))

    if not os.path.exists('./Databases'):
        os.makedirs('./databases')
    
    if not os.path.exists('./data'):
        os.makedirs('./data')
        os.makedirs('./data/localization')
        os.makedirs('./data/images')
    
    if not os.path.exists('./logs'):
        os.makedirs('./logs')
    
    if not os.path.exists('./modules'):
        os.makedirs('./modules')
        open('./Modules/__init__.py', 'a').close()

#Main config file initialization
def config_init(): 
    if not os.path.isfile('config.ini'):
        config = configparser.ConfigParser()
        config.optionxform = str
        config['Credentials'] = {'Token': '<Enter token here>'}
        config['Commands'] = {'CommandPrefix': '!'}
        config['Language'] = {'CommandLanguageCode': 'en-US',
                              'ConsoleLanguageCode': 'en-US'}
        config['Logging'] = {'LoggerLevel': 'DEBUG',
                             'LogsAutoDeleteDays': 7}

        with open('config.ini', 'w', encoding="utf_8") as config_file:
            config.write(config_file)
            config_file.close()
            print("Successfully created config.ini file. Please configure the file before starting the bot again.")
            sys.exit()
    else:
        config = configparser.ConfigParser(allow_no_value=True)
        with open('config.ini', 'r', encoding="utf_8") as config_file:
            config.read_file(config_file)
            config_init.tokenid = config.get('Credentials', 'Token')
            config_init.prefix = config.get('Commands', 'CommandPrefix')
            config_init.languagecode = config.get('Language', 'CommandLanguageCode')
            config_init.consolelang = config.get('Language', 'ConsoleLanguageCode')
            config_init.logginglevel = config.get('Logging', 'LoggerLevel')
            config_init.log_delete_days = config.get('Logging', 'LogsAutoDeleteDays')
            config_file.close()

#Logging initialization
def logging_init():
    logging_dict = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20, 'DEBUG':10}
    date_today = datetime.today().replace(microsecond=0)
    date_today = date_today.strftime("%d-%m-%Y-%Hh-%Mm-%Ss")
    logger = logging.getLogger('discord')
    if config_init.logginglevel in logging_dict:
        logger.setLevel(logging_dict[config_init.logginglevel])
        print(f'Logging level has been set to [{config_init.logginglevel}]')
    else:
        logger.setlevel(logging.DEBUG)
    log_handler = logging.FileHandler(filename=f'./logs/log-{date_today}.log', encoding='utf-8', mode='w')
    log_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(log_handler)

#Deleting old logs. The function will delete all logs that are older than a week by default
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

if __name__=="__main__":

    paths_init()
    config_init()  
    old_logs_delete(int(config_init.log_delete_days))
    logging_init()
        





