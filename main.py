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
    config = configparser.ConfigParser(allow_no_value=False)
    config.optionxform = str
    config['Credentials'] = {'Token': '<Enter token here>'}
    config['Commands'] = {'CommandPrefix': '!'}
    config['Language'] = {'CommandLanguageCode': 'en-US',
                            'ConsoleLanguageCode': 'en-US'}
    config['Logging'] = {'LoggerLevel': 'DEBUG',
                         'LogsAutoDeleteDays': '7'}

    with open('config.ini', 'w', encoding="utf_8") as config_file:
        config.write(config_file)
        config_file.close()
        print("Successfully created config.ini file. Please configure the file before starting the bot again.")
        sys.exit()
else:
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
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
                "hidden_modules": ["HelpFormatter", "ErrorHandler"],
                "Conquest":
                    {
                        "settlement_image_1": "https://i.imgur.com/8F2hnOS.png",
                        "fight": "https://i.imgur.com/ZYBlee5.png",
                        "defeat_string_1": ("Your settlement's army failed in the attempt to attack **{}**."
                                    " A valley of arrows struck your army's shields. Once your soldiers reached the enemy walls, they swiftly scaled up using ladders."
                                    " A fierce battle erupted on the top. Despite your army's efforts, enemy priests and mages tipped the scales in their favour."
                                    " Their magic managed to pierce your units' armour, fully weakening them. Most of your solders were killed in the process."
                                    " Fortunately, a small group successfully retreated from the battlefield, escorting you back to your kingdom."),
                        "win_string_1": ("Your settlement's army successfully pillaged **{}**."
                                    " Your soldiers reached the enemy walls without much difficulty. A fierce battle erupted."
                                    " A successful breach has been made into the enemy settlement's treasury. Your troops grabbed what they can with their hands."
                                    " You deal a significant amount of damage to your enemy's settlement. However, as enemy forces regroup, your army is forced to retreat."),
                    }
                }#To be deleted at a later date

with open('./data/data.json', 'w') as json_file: 
        json.dump(json_data_input, json_file, indent=4, sort_keys=True,separators=(',', ': '))
json_file.close()

json_lang_en = {
        "module_string": "Module",
        "notes_string": "Note(s)",
        "usage_string": "Usage",
        "empty_string": "*Empty*",
        "core_module_load_fail": "This module has either already been loaded or does not exist.",
        "core_module_load_success": "Module **{}** successfully loaded.",
        "core_module_unload_fail": "This module has either already been unloaded or does not exist.",
        "core_module_unload_success": "Module **{}** successfully unloaded.",
        "core_module_reload_fail": "This module could not be reloaded as it has not been loaded yet.",
        "core_module_reload_success": "Module **{}** successfully reloaded.",
        "core_modules_list": "List of modules:",
        "core_cmds_list_empty": "Either **{}** does not have any commands or all of them are hidden.",
        "core_cmds_list": "List of commands for **{}**:",
        "core_cmds_list_not_found": "**{}** module not found.",
        "core_cmds_list_marg": "Please specify a module.",
        "core_userid_msg": "{}'s Discord ID is: **{}**",
        "core_serverid_msg": "{}'s ID is: **{}**",
        "core_channelid_msg": "{} | #{}'s ID is: **{}**",
        "core_leave_msg": "Thank you for having me on this server. Have a nice day!",
        "core_latencies": "Shard **{}** ({} Servers) | Latency: {}ms\n",
        "core_latencies_msg": "Shards Overview",
        "core_module_hide_success": 'Module **{}** successfully hidden.',
        "core_module_hide_hidden": 'This module is already hidden!',
        "core_module_hide_fail": "Failed to hide module. Please check if said module has been loaded or is spelled correctly",
        "core_module_unhide_success": 'Module **{}** successfully unhidden.',
        "core_module_unhide_visible": 'This module is already visible!',
        "core_module_unhide_fail": "Failed to unhide module. Please check if said module has been loaded or is spelled correctly",
        "utility_avatar_msg": "{}'s Avatar:",
        "utility_roll_msg": "You rolled **{}**.",
        "utility_uptime_msg": "Bot has been running for **{}** days, **{}** hours, **{}** minutes and **{}** seconds.",
        "utility_uinfo_id": "ID",
        "utility_uinfo_nickname": "Nickname",
        "utility_uinfo_activity": "Activity",
        "utility_uinfo_created": "Account Created",
        "utility_uinfo_joined": "Joined Server",
        "utility_uinfo_sroles": "Server Roles ({})",
        "errorhandler_dcmd": "This command ({})has been disabled.",
        "errorhandler_cooldown":"This command ({}) is currently on cooldown. Please try again after **{}** seconds.",
        "errorhandler_missing_perms":"The bot is missing the following permissions to execute this command: {}",
        "helpformatter_help": "**General Help Command**",
        "helpformatter_help_description": ("You can use **!modules** to see a list of all available modules.\n"
                                           "You can use **!commands <Module>** to see all commands inside a certain module.\n\n"
                                           "You could also view a detailed profile of every command using **!h <command>**\n\n"
                                           "You can add me to your server using this link: https://discordapp.com/oauth2/authorize?client_id=593082021325045760&scope=bot&permissions=8\n\n"
                                           "If you have any inquiries, suggestions or just want to chat, you could join\nthe **quBot Support Server** here: https://discord.gg/TGnfsH2\n\n"
                                           "Have a nice day!"),
        "helpformatter_nohelp_parameter": "This command does not have a description/help string attached to it yet.",
        "helpformatter_cmd_not_found": "This command either does not exist or your spelling is incorrect.",
        "economy_daily_claimed": "You already claimed your daily reward! Next daily reward available in {} hour(s) {} minute(s) and {} second(s).",
        "economy_daily_received": "**{}**, you claimed your daily reward of {} {}.",
        "economy_daily_gifted": "**{}**, you gifted your daily reward of {} {} to **{}**.",
        "economy_currency_return_msg": "**{}** has {} {}.",
        "economy_adjust_award_msg": "**{}** was awarded {} {}.",
        "economy_adjust_subtract_msg": "**{}** was withheld {} {}.",
        "economy_insufficient_funds": "You have insufficient funds to use this command. Please make sure you have enough!",
        "economy_give_self": "You can't transfer money to yourself!",
        "economy_give_success": "**{}** has given **{}**   {} {}",
        "economy_betroll_fail_msg": "Oops! You rolled {} but did not win anything. Please try again.",
        "economy_betroll_msg":"Congratulations, you rolled {} and won {} {}.",
        "economy_betroll_jackpot": "**JACKPOT!!!** Congratulations, you rolled {} and won {} {}.",
        "conquest_create_args": "Failed to create a settlement. Please check if all arguments are correctly structured and try again.",
        "conquest_create_public_private": "The settlement's type can either be **public** or **private**.",
        "conquest_create_success": "Settlement has been successfully created.",
        "conquest_create_already_has": "You already have a settlement.",
        "conquest_entry_requirement": "The entry fee doesn't meet the minimal entry fee requirement!",
        "conquest_insufficient_funds": "Funds not sufficient to deposit for the settlement's starting fee.",
        "conquest_info_args": "No settlement name detected. Please try again.",
        "conquest_info_fail": "This settlement could not be found. Either it does not exist or your spelling is incorrect.",
        "conquest_wins": "Wins",
        "conquest_losses": "Losses",
        "conquest_info_info": "Settlement Information:",
        "conquest_info_name": "Settlement Name",
        "conquest_info_founder": "Founder",
        "conquest_info_created": "Date Created",
        "conquest_info_population": "Population",
        "conquest_info_treasury": "Treasury",
        "conquest_info_type": "Settlement Type",
        "conquest_info_level": "Settlement Level",
        "conquest_info_wins_losses": "Settlement Wins & Losses",
        "conquest_info_win_ratio": "win ratio",
        "conquest_join_args": "Please check all of your arguments and try again.",
        "conquest_join_not_found": "Failed to join settlement. Settlement not found.",
        "conquest_join_min_entry": "The written value is lower than the minimal entry fee of **{}** for this settlement.",
        "conquest_join_success": "You successfully joined {}",
        "conquest_join_part_of": "You are already part of this settlement.",
        "conquest_code_success": "Your settlement's invite code is **{}**",
        "conquest_code_fail": "You aren't a founder or leader of any settlement.",
        "conquest_attack_args": "No target user was specified.",
        "conquest_attack_self": "You can't attack your own settlement.",
        "conquest_attack_enemy_no": "The settlement you're trying to attack does not exist!",
        "conquest_attack_you_no": "You can not attack without a settlement.",
        "conquest_attack_result_victory": "Result: **VICTORY**",
        "conquest_attack_result_defeat": "Result: **DEFEAT**",
        "conquest_roll": "**Roll**",
        "conquest_summary": "Summary",
        "conquest_experience": "Experience Points",
        "conquest_exp": "EXP",
        "conquest_chances": "Your chance of winning this battle was **{}%**",
        "conquest_win_percentage": "*Win Percentage*",
        "conquest_attack_wd": "Your Wins/Defeats",
        "conquest_pillaged_gold": "Pillaged Gold",
        "command_owner_only": "This command can only be used by the **BOT OWNER**.",
        "command_module_help": "The module file needs to be present in the modules folder of the bot.\nThis command can only be used by the **BOT OWNER**.",
        "command_load_description": "Loads new modules into the bot application.",
        "command_unload_description": "Unloads modules from the bot application.",
        "command_reload_description": "Reloads modules loaded into the bot application.",
        "command_modules_description": "Displays all loaded modules.",
        "command_modules_hide_help": "This is a subcommand of the **modules** command.\nThis command can only be used by the **BOT OWNER**.",
        "command_modules_hide_description": "Hides a module from the list of loaded modules.",
        "command_modules_unhide_help": "This is a subcommand of the **modules** command.\nThis command can only be used by the **BOT OWNER**.",
        "command_modules_unhide_description": "Reveals a hidden module from the list of loaded modules.",
        "command_cmds_description": "Displays all commands in a given module",
        "command_userid_help": "If no argument is given, the bot will use the author of the message.\nThis command can only be used by the **BOT OWNER**.",
        "command_userid_description": "Returns the target individual's Discord ID.",
        "command_serverid_description": "Returns the server's ID for the server the command was typed in.",
        "command_channelid_description": "Returns the channel's ID for the channel the command was typed in.",
        "command_leave_description": "Politely kicks the bot off your server. We are polite, mkay?",
        "command_latencies_description": "Returns the latencies (in miliseconds) for every active shard.",
        "command_setname_description": "Changes the name of the bot.",
        "command_setstatus_help": "This command requires one argument and it needs to be one of the following: *online, offline, idle, dnd, invisible*.\nThis command can only be used by the **BOT OWNER**.",
        "command_setstatus_description": "Changes the bot's status. (Online by default)",
        "command_setactivity_help": "This command requires two arguments: the type of activity(playing, streaming, listening, watching) and the message itself.\nThis command can only be used by the **BOT OWNER**.",
        "command_setactivity_description": "Changes the bot's activity",
        "command_avatar_help": "If no argument is parsed, the bot will instead return your avatar.",
        "command_avatar_description": "Returns the target individual's avatar.",
        "command_roll_help": "If no argument is parsed, the bot will roll a number between 1 and 100.",
        "command_roll_description": "Rolls a number in a given range.",
        "command_uptime_description": "Returns the bot's uptime.",
        "command_uinfo_help": "If no argument is parsed, the bot will return your information instead.",
        "command_uinfo_description": "Shows the target individual's user information.",
        "command_daily_help": "If you wish to gift your daily reward instead of claiming it for yourself, you can mention the individual when using the command.",
        "command_daily_description": "Lets you claim a set sum of money on a daily basis.",
        "command_currency_help": "If no argument is parsed, the bot will display the sum of money that you have on your profile.",
        "command_currency_description": "Displays the sum of money the target individual has on their profile.",
        "command_adjust_help": "This command requires two arguments - the target user and the amount of money.\nThis command can only be used by the **BOT OWNER**.",
        "command_adjust_description": "Awards/Subtracts a set amount of money to/from the target individual.",
        "command_give_help": "This command requires two arguments - the target user and the amount of money.",
        "command_give_description": "Transfers a set amount of money to another user.",
        "command_betroll_help": "This command requires one argument - the amount you are willing to bet.",
        "command_betroll_description": "Lets you bet a certain amount of money.",
        "command_ccreate_help": ("This command requires three arguments - settlement name (should be in quotes),"
                                 " settlement type (either *public* or *private) and entry fee (minimum 100)"),
        "command_ccreate_description": "Creates a settlement.",
        "command_cinfo_help": "This command requires one argument - settlement name (without quotes).",
        "command_cinfo_description": "Displays a settlement's public information.",
        "command_cjoin_help": "This command requires two arguments - the settlement's invite code and entry fee (minimum the settlement's entry fee).",
        "command_cjoin_description": "Joins another individual's settlement",
        "command_ccode_help": "This command can also be used directly in the bot's direct messages.",
        "command_ccode_description": "Displays your settlement's invite code. Be careful where you use the command!",
        "command_cattack_help": "Use it wisely!",
        "command_cattack_description": "Attacks the target individual's settlement.",
        }#To be deleted at a later date

'''To be deleted at a later date
with open('./data/data.json', 'w') as json_file: 
        json.dump(json_data_input, json_file, indent=4, sort_keys=True,separators=(',', ': '))
json_file.close()
'''

with open('./data/localization/language_{}.json'.format(languagecode), 'w') as json_file:
    json_file.write(json.dumps(json_lang_en, indent=4, sort_keys=True,separators=(',', ': ')))
json_file.close()#To be deleted at a later date

with open('./data/localization/language_{}.json'.format(languagecode), 'r') as json_file:
    lang = json.load(json_file)
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



        





