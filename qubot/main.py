from discord.ext import commands
from datetime import datetime, timedelta
from libs.qulib import is_venv, data_get, makefolders, safe_cast
import libs.prefixhandler as prefixhandler
import logging
import os
import sys
import sqlite3
import configparser
import json

#-----------------------------------#
#Path checks and initalization
bot_path = os.path.dirname(os.path.realpath(__file__))

#TODO: Move directory creation outside of main script file

subfolders = {'databases', 'data', 'data/localization', 'data/images', 'logs', 'libs', 'modules'}
makefolders(bot_path, subfolders)

open(os.path.join(bot_path, 'libs', '__init__.py'), 'a').close()
open(os.path.join(bot_path, 'modules', '__init__.py'), 'a').close()

#-----------------------------------#
#Main config file initialization 
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
    print(f'ERROR: Failed to change logging level to [{logginglevel}]. Not a valid logging level. Converting back to DEBUG mode')
log_handler = logging.FileHandler(filename=os.path.join(bot_path, f'logs/log-{date_today}.log'), encoding='utf-8', mode='w')
log_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(log_handler)

#-----------------------------------#
#JSON files initialization/writing/loading

json_lang_en = {
    "administration_autoaction_ban": "Your last warning triggered an automatic ban action from this server.",
    "administration_autoaction_disable_msg": "Automatic {} disabled. To enable it again, set it to a new value.",
    "administration_autoaction_kick": "Your last warning triggered an automatic kick action from this server.",
    "administration_autoaction_max": "Automatic actions can only be set to a maximum number of {}",
    "administration_autoaction_msg": "An automatic {} will be triggered when a user reaches {} warnings.",
    "administration_ban_msg": "{} has been banned from this server. Reason: {}",
    "administration_ban_out_of_range": "The number is out of range.",
    "administration_bye_default": "Goodbye, {}. Wishing you all the best.",
    "administration_gbdisable_disabled": "Server goodbye messages are already disabled.",
    "administration_gbdisable_success": "Server goodbye messages have been disabled.",
    "administration_gbenable_enabled": "Server goodbye messages are already enabled.",
    "administration_gbenable_success": "Server goodbye messages have been enabled.\nFuture greeting messages will be sent in the respective text channel.",
    "administration_gbmessage_default_success": "Custom goodbye message has been reset back to default.",
    "administration_gbmessage_default_used": "Default goodbye message is already being used.",
    "administration_gbmessage_disabled": "Failed to set custom goodbye message. Please enable goodbye messages first and try again.",
    "administration_gbmessage_invalid": "Invalid custom goodbye message",
    "administration_gbmessage_success": "Custom goodbye message has been set successfully.",
    "administration_gdisable_disabled": "Server greetings are already disabled.",
    "administration_gdisable_success": "Server greetings have been disabled.",
    "administration_gdm_msg": "Server greetings have been enabled.\nFuture greeting messages will be sent to users' direct messages.",
    "administration_genable_enabled": "Server greetings are already enabled.",
    "administration_genable_success": "Server greetings have been enabled.\nFuture greeting messages will be sent in the respective text channel.",
    "administration_gmessage_default_success": "Custom greeting message has been reset back to default.",
    "administration_gmessage_default_used": "Default greeting message is already being used.",
    "administration_gmessage_disabled": "Failed to set custom greeting message. Please enable greetings first and try again.",
    "administration_gmessage_invalid": "Invalid custom greet message",
    "administration_gmessage_limit": "Custom message is too long. Maximum character limit: {}",
    "administration_gmessage_success": "Custom greeting message has been set successfully.",
    "administration_greet_default": "Hey {}, welcome to **{}**!",
    "administration_gscdefault_msg": "Greeting/goodbye messages text channel has been set back to default.",
    "administration_gsetchannel": "Greeting/Goodbye messages channel successfully changed to **#{}**",
    "administration_kick_msg": "{} has been kicked from this server. Reason: {}",
    "administration_mute_muted": "{} is already muted.",
    "administration_mute_success": "{} has been muted.",
    "administration_purge_delmsg": "Deleted {} message(s)",
    "administration_purge_prmsg": "Failed to purge set messages. You can't delete a negative number of messages.",
    "administration_report_disable_fail": "Reporting is already disabled on this server. To enable it again, set a report channel.",
    "administration_report_disable_success": "Reporting has been disabled. To enable it again, set a new report channel.",
    "administration_report_reportedby": "Reported by: {}",
    "administration_report_title": "Report",
    "administration_setchannel_msg": "Report channel has been set to **#{}**",
    "administration_softban_msg": "{} has been soft banned from this server. Reason: {}",
    "administration_unban_msg": "{} has been unbanned from this server.",
    "administration_unmute_success": "{} has been unmuted.",
    "administration_unmute_unmuted": "{} is not muted.",
    "administration_warn_dm_footer": "Server: {}",
    "administration_warn_dm_title": "Your actions have resulted in a warning",
    "administration_warn_dm_warnedby": "Warned by",
    "administration_warn_max": "Maximum user warnings reached ({}). Their warnings must be reset in order to issue new ones.",
    "administration_warn_success": "{} has been warned successfully.",
    "administration_warnings_delete": "Warning number {} has been deleted for {}.",
    "administration_warnings_issuedby": "*Issued by: {}*",
    "administration_warnings_outofrange": "The warning you're trying to delete does not exist",
    "administration_warnings_reset": "All server-wide warnings have been reset for {}",
    "administration_warnings_title": "List of warnings for {}",
    "command_8ball_description": "Returns an answer for a yes or no question.",
    "command_adjust_description": "Awards/Subtracts a set amount of money to/from the target individual.",
    "command_adjust_help": "This command requires two arguments - the target user and the amount of money.\nThis command can only be used by the **BOT OWNER**.",
    "command_antonyms_description": "Returns a list of the top antonyms from Thesaurus based on the term you parse to the bot.",
    "command_autoaction_description": "Changes the number of warnings needed for a user to trigger an automatic mute/kick/ban from the server. (Disabled by default)",
    "command_autoaction_disable_description": "Disables the target automatic action from triggering for future user warnings.",
    "command_autoaction_disable_help": "This command can only be used by users with the ability to **kick** and **ban** members.",
    "command_autoaction_help": "- Using this command will enable the above-mentioned automatic actions if previously disabled.\n- If any of the number of warnings match for mute, kick or ban, the following will take priority from highest to lowest: ban, kick, mute.\n- This command can only be used by users with the ability to **kick** and **ban** members.",
    "command_avatar_description": "Returns the target individual's avatar.",
    "command_avatar_help": "If no argument is parsed, the bot will instead return your avatar.",
    "command_ban_description": "Bans the mentioned individual for a certain reason (if any)",
    "command_ban_help": "- The ban reason is an optional argument.\n- This command can only be used by users with the ability to **ban** members.",
    "command_betroll_description": "Lets you bet a certain amount of money.",
    "command_betroll_help": "This command requires one argument - the amount you are willing to bet.",
    "command_blist_description": "Displays the buildings' status of the settlement you are part of. (if any)",
    "command_buildings_description": "A command group. If no subcommands are invoked by the user, this command will display the buildings' status of the settlement you are part of. (if any)",
    "command_bupgrade_description": "Upgrades the target settlement building to the next level.\nBuildings can be upgraded to Level 10.",
    "command_cattack_description": "Attacks the target individual's settlement.",
    "command_cattack_help": "Use it wisely!",
    "command_ccreate_description": "Creates a settlement.",
    "command_ccreate_help": "This command requires three arguments - settlement name (should be in quotes), settlement type (either *public* or *private) and entry fee (minimum 100)",
    "command_channelid_description": "Returns the channel's ID for the channel the command was typed in.",
    "command_choose_description": "Picks a random item from a provided list of items, separated by a semicolon.",
    "command_cinfo_description": "Displays a settlement's public information.",
    "command_cinfo_help": "This command has one optional argument - the target individual. If no argument is parsed then the command will display the settlement you currectly reside in.",
    "command_cjoin_description": "Joins another individual's settlement",
    "command_cjoin_help": "This command requires two arguments - the settlement's invite code and entry fee (minimum the settlement's entry fee).",
    "command_cmds_description": "Displays all commands in a given module",
    "command_code_description": "A command group. If no subcommands are invoked by the user, this command will display your settlement's invide code.",
    "command_code_help": "This command can also be used directly in the bot's direct messages.",
    "command_code_new_description": "Generates a new invite code for your settlement.",
    "command_code_show_description": "Displays your settlement's invite code. The code is sent privately to the author.",
    "command_currency_description": "Displays the sum of money the target individual has on their profile.",
    "command_currency_help": "If no argument is parsed, the bot will display the sum of money that you have on your profile.",
    "command_daily_description": "Lets you claim a set sum of money on a daily basis.",
    "command_daily_help": "If you wish to gift your daily reward instead of claiming it for yourself, you can mention the individual when using the command.",
    "command_deposit_description": "Deposits a sum of money into the treasury of the settlement you are currently part of.",
    "command_deposit_help": "You need to be part of a settlement to be able to use this command.",
    "command_give_description": "Transfers a set amount of money to another user.",
    "command_give_help": "This command requires two arguments - the target user and the amount of money.",
    "command_giveaway_end_description": "Ends a giveaway by a provided bot message ID",
    "command_giveaway_group_description": "Giveaway command group. Please refer to `giveaway start` and `giveaway end` for more information.",
    "command_giveaway_start_description": "Starts a currency giveaway. Users can claim their reward by reacting to the bot message.",
    "command_goodbye_description": "Toggles server goodbye messages on/off on the server.",
    "command_goodbye_disable_description": "Disables server goodbye messages on the server.",
    "command_goodbye_disable_help": "This command can only be used by users with the ability to **manage servers**.",
    "command_goodbye_enable_description": "Enables server goodbye messages on the server.",
    "command_goodbye_enable_help": "This command can only be used by users with the ability to **manage servers**.",
    "command_goodbye_help": "This command can only be used by users with the ability to **manage servers**.",
    "command_goodbye_mdefault_description": "Resets the server goodbye message back to default.",
    "command_goodbye_mdefault_help": "This command can only be used by users with the ability to **manage servers**.",
    "command_goodbye_message_description": "Changes the goodbye message to a custom one. Feel free to check the notes to be able to fully utilize this command.",
    "command_goodbye_message_help": "- This command supports Discord Markdown. (Chat formatting: bold, italics, underline, etc.)\n- You can include the following in your message:\n**{mention}** - Mentions the User;\n**{user}** - Shows Username;\n**{server}** - Shows server name;\n**{membercount}** - Shows number of people in server;\n- This command can only be used by users with the ability to **manage servers**.",
    "command_greetings_description": "Toggles server greeting messages on/off on the server.",
    "command_greetings_disable_description": "Disables server greeting messages on the server.",
    "command_greetings_disable_help": "This command can only be used by users with the ability to **manage servers**.",
    "command_greetings_dm_description": "Enables server greetings on the server. Instead of the server's text channel, future messages will instead be sent to users' direct messages.",
    "command_greetings_dm_help": "This command can only be used by users with the ability to **manage servers**.",
    "command_greetings_enable_description": "Enables server greeting messages on the server.",
    "command_greetings_enable_help": "This command can only be used by users with the ability to **manage servers**.",
    "command_greetings_help": "This command can only be used by users with the ability to **manage servers**.",
    "command_greetings_mdefault_description": "Resets the server greeting message back to default.",
    "command_greetings_mdefault_help": "This command can only be used by users with the ability to **manage servers**.",
    "command_greetings_message_description": "Changes the greeting message to a custom one. Feel free to check the notes to be able to fully utilize this command.",
    "command_greetings_message_help": "- This command supports Discord Markdown. (Chat formatting: bold, italics, underline, etc.)\n- You can include the following in your message:\n**{mention}** - Mentions the User;\n**{user}** - Shows Username;\n**{server}** - Shows server name;\n**{membercount}** - Shows number of people in server;\n- This command can only be used by users with the ability to **manage servers**.",
    "command_greetings_scdefault_description": "Resets the greetings/goodbye messages text channel back to default.",
    "command_greetings_scdefault_help": "- By default, these messages are sent to **#general**. If no text channel exists with that name, it uses the first text channel on the list.\n- This command can only be used by users with the ability to **manage servers**.",
    "command_greetings_setchannel_description": "Sets the text channel where greetings and goodbye messages are going to be sent by the bot.",
    "command_greetings_setchannel_help": "- By default, these messages are sent to **#general**. If no text channel exists with that name, it uses the first text channel on the list.\n- This command can only be used by users with the ability to **manage servers**.",
    "command_jprivate_description": "Command to join a private settlement.",
    "command_jpublic_description": "Command to join a public settlement.",
    "command_kick_description": "Kicks the mentioned individual for a certain reason (if any)",
    "command_kick_help": "- The kick reason is an optional argument.\n- This command can only be used by users with the ability to **kick** members.",
    "command_langs_description": "Returns a list of locally detected language(localization) packages",
    "command_langset_description": "Changes the language of the bot",
    "command_latencies_description": "Returns the latencies (in miliseconds) for every active shard.",
    "command_leaderboard_description": "Returns the settlements' leaderboard",
    "command_leaderboard_help": "This command takes one optional argument - the page number. If no argument is passed, then it defaults to 1.",
    "command_leave_description": "Politely kicks the bot off your server.",
    "command_load_description": "Loads new modules into the bot application.",
    "command_market_description": "A command group. If no subcommands are invoked by the user, this command will display the resource market.",
    "command_market_help": "This command can also be used directly in the bot's direct messages.",
    "command_mbuy_description": "Buys a set amount of resources from the market.",
    "command_meanings_definition": "This command also supports phrases.",
    "command_meanings_description": "Returns a list of definitions based on the term you parse to the bot.",
    "command_module_help": "The module file needs to be present in the modules folder of the bot.\nThis command can only be used by the **BOT OWNER**.",
    "command_modules_description": "Displays all loaded modules.",
    "command_modules_hide_description": "Hides a module from the list of loaded modules.",
    "command_modules_hide_help": "This is a subcommand of the **modules** command.\nThis command can only be used by the **BOT OWNER**.",
    "command_modules_unhide_description": "Reveals a hidden module from the list of loaded modules.",
    "command_modules_unhide_help": "This is a subcommand of the **modules** command.\nThis command can only be used by the **BOT OWNER**.",
    "command_msell_description": "Sells a set amount of resources on the market.",
    "command_mute_description": "Mutes the target individual from chatting on the server.",
    "command_owner_only": "This command can only be used by the **BOT OWNER**.",
    "command_promote_description": "Promotes the target individual to settlement leader.",
    "command_promote_help": "This command can **ONLY** be used by settlement leaders.",
    "command_purge_description": "Deletes a set number of messages.",
    "command_purge_help": "This command requires a single argument - The number of messages you wish the bot to delete.",
    "command_reload_description": "Reloads modules loaded into the bot application.",
    "command_report_description": "Reports the target user for a particular reason.",
    "command_report_disable_description": "Disables user reporting for the server where the command was used.",
    "command_report_disable_help": "- To enable user reporting again, you need to set a new report text channel.\n- This command can only be used by server **administrators**.",
    "command_report_help": "- A report reason must be provided in order to use this command.\n- This command will only work when a report channel is set. (Disabled by default)",
    "command_reqs_description": "Displays target settlement building upgrade requirements for every level from 1 to 10.",
    "command_resources_description": "Displays the amount of resources currently stored in your settlement.",
    "command_restart_description": "Restarts the bot",
    "command_roleid_description": "Returns the target role's ID for the server the command was typed in.",
    "command_roll_description": "Rolls a number in a given range.",
    "command_roll_help": "If no argument is parsed, the bot will roll a number between 1 and 100.",
    "command_serverid_description": "Returns the server's ID for the server the command was typed in.",
    "command_setactivity_description": "Changes the bot's activity",
    "command_setactivity_help": "This command requires two arguments: the type of activity(playing, streaming, listening, watching) and the message itself.\nThis command can only be used by the **BOT OWNER**.",
    "command_setchannel_description": "Selects a text channel where future user reports are going to be sent.",
    "command_setchannel_help": "- Using this command will enable user reports if they were previously disabled. (Disabled by default)\n- This command can only be used by server **administrators**.",
    "command_setname_description": "Changes the name of the bot.",
    "command_setstatus_description": "Changes the bot's status. (Online by default)",
    "command_setstatus_help": "This command requires one argument and it needs to be one of the following: *online, offline, idle, dnd, invisible*.\nThis command can only be used by the **BOT OWNER**.",
    "command_shutdown_description": "Shutdowns the bot",
    "command_skick_description": "Kicks the target individual from the settlement.",
    "command_skick_help": "This command can **ONLY** be used by settlement leaders.",
    "command_sleader": "This command can only be used by the leader of the settlement.",
    "command_sleave_description": "Leave the settlement you are currently in. (if any)",
    "command_sleave_help": "- Leaders of settlements with multiple residents cannot leave settlement without transferring ownership.\n- Settlements with only one resident will get **DESTROYED** in the process!",
    "command_softban_description": "Soft bans the mentioned individual for a specified reason (if any)",
    "command_softban_help": "- The soft ban reason is an optional argument.\n- Soft bans in essence kick the target individual from the server while deleting their messages. It's not the same as a normal ban.\n- This command can only be used by users with the ability to **kick** members and **manage** messages.",
    "command_srename_description": "Renames your settlement to the given name.",
    "command_srename_help": "- You must be the leader of this settlement to be able to use this command.\n- In order to rename your settlement, you need to pay a fee of 500 gold.\n- Settlement names have a character limit of 50 characters.",
    "command_synonyms_description": "Returns a list of the top synonyms from Thesaurus based on the term you parse to the bot.",
    "command_uinfo_description": "Shows the target individual's user information.",
    "command_uinfo_help": "If no argument is parsed, the bot will return your information instead.",
    "command_unban_description": "Unbans the target individual from the server.",
    "command_unban_help": "Since the target individual can not be mentioned directly within the server, a <username>#<discriminator>(see example) or user ID should be provided.",
    "command_unload_description": "Unloads modules from the bot application.",
    "command_unmute_description": "Unmutes the target individual if they were previously muted using the bot.",
    "command_uptime_description": "Returns the bot's uptime.",
    "command_urbandict_description": "Returns the top urban dictionary definition based on the term you parse to the bot.",
    "command_userid_description": "Returns the target individual's Discord ID.",
    "command_userid_help": "If no argument is given, the bot will use the author of the message.\nThis command can only be used by the **BOT OWNER**.",
    "command_warn_description": "Warns the target user for a particular reason. This individual will receive a direct message from the bot.",
    "command_warn_help": "- A reason for the warning must be provided in order to use this command.\n- This command can only be used by users with the ability to **kick** and **ban** members.",
    "command_warnings_delete_description": "Deletes a specific warning that was issued to the target individual.",
    "command_warnings_delete_help": "- While deleting warnings **WILL NOT** trigger any automatic actions, adding a new warning **WILL**.\n- This command can only be used by users with the ability to **kick** and **ban** members.",
    "command_warnings_description": "Displays a list of warnings for the target individual.",
    "command_warnings_help": "- A total of five warnings are displayed per page. You can navigate through pages by providing a page number after the username.\n- This command can only be used by users with the ability to **kick** and **ban** members.",
    "command_warnings_reset_description": "Resets all warnings for the target individual.",
    "command_warnings_reset_help": "This command can only be used by users with the ability to **kick** and **ban** members.",
    "command_prefix_help": "- If you do not include a new prefix, the command will instead display the bot's current prefix on the server.\n- This command can only be used by server **administrators**.",
    "command_prefix_description": "Shows or changes the bot's prefix on the server.",
    "command_prefix_reset_help": "This command can only be used by server **administrators**.",
    "command_prefix_reset_description": "Resets the bot's prefix on the server back to default.",
    "command_prefix_show_description": "Shows the bot's prefix on the server.",
    "conquest_attack_args": "No target user was specified.",
    "conquest_attack_enemy_no": "The settlement you're trying to attack does not exist!",
    "conquest_attack_enemy_part_of": "The person you're trying to attack does not seem to be part of any settlements.",
    "conquest_attack_result_defeat": "Result: **DEFEAT**",
    "conquest_attack_result_victory": "Result: **VICTORY**",
    "conquest_attack_self": "You can't attack your own settlement.",
    "conquest_attack_wd": "Your Wins/Defeats",
    "conquest_attack_you_no": "You can not attack without a settlement.",
    "conquest_buildings_title": "Settlement: {}\nBuildings Status",
    "conquest_buy_no_market": "Failed to buy resources: Your settlement does not have a **Market Square**.",
    "conquest_chances": "Your chance of winning this battle was **{}%**",
    "conquest_code_fail": "You aren't a founder or leader of any settlement.",
    "conquest_code_new_fail": "Failed to change invite code. You do not seem to own a settlement.",
    "conquest_code_new_success": "Successfully changed code. Your new settlement invite code is **{}**",
    "conquest_code_success": "Your settlement's invite code is **{}**",
    "conquest_create_already_has": "You already have a settlement.",
    "conquest_create_args": "Failed to create a settlement: Please check if all arguments are correctly structured and try again.",
    "conquest_create_part_of": "Failed to create a settlement: You can only be part of one settlement at a time.",
    "conquest_create_public_private": "The settlement's type can either be **public** or **private**.",
    "conquest_create_success": "Settlement has been successfully created.",
    "conquest_deposit_success": "You successfully deposited {} {} into the settlement's treasury.",
    "conquest_entry_requirement": "The entry fee doesn't meet the minimal entry fee requirement!",
    "conquest_exp": "EXP",
    "conquest_experience": "Experience Points",
    "conquest_info_args": "No settlement name detected. Please try again.",
    "conquest_info_created": "Date Created",
    "conquest_info_fail": "This settlement could not be found.",
    "conquest_info_founder": "Founder",
    "conquest_info_info": "Settlement Information:",
    "conquest_info_leader": "Leader",
    "conquest_info_level": "Settlement Level",
    "conquest_info_name": "Settlement Name",
    "conquest_info_population": "Population",
    "conquest_info_treasury": "Treasury",
    "conquest_info_type": "Settlement Type",
    "conquest_info_win_ratio": "win ratio",
    "conquest_info_wins_losses": "Settlement Wins & Losses",
    "conquest_insufficient_funds": "Funds not sufficient to deposit for the settlement's starting fee.",
    "conquest_join_fail_user": "The target user does not seem to be part of a settlement.",
    "conquest_join_min_entry": "The written value is lower than the minimal entry fee of **{}** for this settlement.",
    "conquest_join_no_subcommands": "Conquest 'join' command group.\nIf you do not know how to join a settlement, please refer to the help command.",
    "conquest_join_not_found": "Failed to join settlement: Settlement not found.",
    "conquest_join_part_of": "You are already part of a settlement.",
    "conquest_join_private_msg": "Failed to join settlement: You are trying to join a private settlement without an invite code.",
    "conquest_join_success": "You successfully joined {}",
    "conquest_join_target_fail": "Failed to join settlement: Target user is not part of any settlements.",
    "conquest_leaderboard_negative": "The page value should be more than or equal to 1.",
    "conquest_leaderboard_title": "Settlements Leaderboard",
    "conquest_leave_leader": "You cannot leave a settlement with more than one resident where you are still the leader.",
    "conquest_leave_not_found": "Failed to leave settlement: Settlement not found.",
    "conquest_leave_success": "You successfully left the settlement.",
    "conquest_leave_success_alone": "You successfully left the settlement. You were the only resident so it was destroyed in the process.",
    "conquest_level": "Level",
    "conquest_losses": "Losses",
    "conquest_market_buy_fail": "Failed to buy resources: Insufficient funds.",
    "conquest_market_buy_success": "Successfully bought {} {}, costing your settlement {} {}",
    "conquest_market_reminder": "Market prices change once every 24 hours.",
    "conquest_market_sell_fail": "Failed to sell resources: Insufficient quantity in warehouse.",
    "conquest_market_sell_success": "Successfully sold {} {}. Your settlement earned {} {}",
    "conquest_market_title": "Market daily prices:",
    "conquest_max_reached": "Building maximum level reached.",
    "conquest_not_leader": "You are not the leader of this settlement.",
    "conquest_not_part_of": "You do not seem to be part of any settlements.",
    "conquest_piece": "piece",
    "conquest_pillaged_gold": "Pillaged Gold",
    "conquest_promote_confirmation": "Please type **'yes'** or **'no'** to confirm whether you want to proceed with settlement ownership transfer to {}.",
    "conquest_promote_self": "You cannot promote yourself.",
    "conquest_promote_settlement_fail": "This person is not in your settlement.",
    "conquest_promote_success": "Successfully transfered ownership to {}",
    "conquest_rename_no_funds": "You do not have enough funds to rename your settlement.\n**Required amount:** {} {}",
    "conquest_rename_success": "Your settlement was successfully renamed to: *{}*.\nAs a result, {} {} was deducted from you treasury.",
    "conquest_requirements_range": "Invalid building index: Please use numbers between (including) 1 and 10",
    "conquest_requirements_title": "**{}** | Resource requirements:",
    "conquest_resources_cloth": "Cloth",
    "conquest_resources_food": "Food",
    "conquest_resources_gold": "Gold",
    "conquest_resources_needed": "Needed Resources",
    "conquest_resources_stone": "Stone",
    "conquest_resources_wood": "Wood",
    "conquest_roll": "**Roll**",
    "conquest_sell_no_market": "Failed to sell resources: Your settlement does not have a **Market Square**.",
    "conquest_sell_price": "Sell price",
    "conquest_skick_self": "You cannot kick yourself out of the settlement. Instead, consider leaving.",
    "conquest_skick_success": "You successfully kicked {} from the settlement.",
    "conquest_sname_too_long": "The settlement's name is too long. There is a 50 character limit.",
    "conquest_summary": "Summary",
    "conquest_target_not_part_of": "This person is not part of any settlements.",
    "conquest_upgrade_fail": "You do not have enough resources to upgrade **{}**.",
    "conquest_upgrade_max_level": "You have already reached the maximum level of this building.",
    "conquest_upgrade_success": "You upgraded {} to Level {}.",
    "conquest_upgrade_th": "Upgrade Town hall to unlock next building level.",
    "conquest_warehouse_title": "*{}* 's Warehouse",
    "conquest_win_percentage": "*Win Percentage*",
    "conquest_wins": "Wins",
    "core_channelid_msg": "{} | #{}'s ID is: **{}**",
    "core_cmds_list": "List of commands for **{}**:",
    "core_cmds_list_empty": "Either **{}** does not have any commands or all of them are hidden.",
    "core_cmds_list_marg": "Please specify a module.",
    "core_cmds_list_not_found": "**{}** module not found.",
    "core_langs_footer": "Current bot language",
    "core_langs_title": "Available language pack(s)",
    "core_langset_notfound": "This language does not seem to exist in the system. Please make sure your spelling is correct.",
    "core_langset_same": "The language you're trying to set the bot to is already being used.",
    "core_langset_success": "Language was set to **{}**. Reloading modules...",
    "core_latencies": "Shard **{}** ({} Servers) | Latency: {}ms\n",
    "core_latencies_msg": "Shards Overview",
    "core_leave_msg": "Thank you for having me on this server. Have a nice day!",
    "core_module_hide_fail": "Failed to hide module. Please check if said module has been loaded or is spelled correctly",
    "core_module_hide_hidden": "This module is already hidden!",
    "core_module_hide_success": "Module **{}** successfully hidden.",
    "core_module_load_fail": "This module has either already been loaded or does not exist.",
    "core_module_load_success": "Module **{}** successfully loaded.",
    "core_module_reload_fail": "This module could not be reloaded as it has not been loaded yet.",
    "core_module_reload_success": "Module **{}** successfully reloaded.",
    "core_module_unhide_fail": "Failed to unhide module. Please check if said module has been loaded or is spelled correctly",
    "core_module_unhide_success": "Module **{}** successfully unhidden.",
    "core_module_unhide_visible": "This module is already visible!",
    "core_module_unload_fail": "This module has either already been unloaded or does not exist.",
    "core_module_unload_success": "Module **{}** successfully unloaded.",
    "core_modules_list": "List of modules:",
    "core_roleid_msg": "{} | The ID for role {} is: **{}**",
    "core_serverid_msg": "{}'s ID is: **{}**",
    "core_userid_msg": "{}'s Discord ID is: **{}**",
    "core_prefix_info": "The bot's prefix on this server is ` {} `",
    "core_prefix_length_limit": "The bot's prefix can have a maximum length of {} characters.",
    "core_prefix_success": "Changed bot server prefix to: ` {} `",
    "core_prefix_reset": "The bot's prefix has been set back to: ` {} `",
    "day_string": "day",
    "dictionaries_antonyms": "**Antonyms**",
    "dictionaries_english_only": "This command supports only **English words & phrases**",
    "dictionaries_synonyms": "**Synonym(s)**",
    "dictionaries_term": "Term: {}",
    "dictionaries_urbandict_title": "**Top urban dictionary definition(s)**",
    "dictionaries_word_not_found": "This word could not be found in the dictionary.",
    "economy_adjust_award_msg": "**{}** was awarded {} {}.",
    "economy_adjust_subtract_msg": "**{}** was withheld {} {}.",
    "economy_betroll_fail_msg": "Oops! You rolled {} but did not win anything. Please try again.",
    "economy_betroll_jackpot": "**JACKPOT!!!** Congratulations, you rolled {} and won {} {}.",
    "economy_betroll_msg": "Congratulations, you rolled {} and won {} {}.",
    "economy_currency_return_msg": "**{}** has {} {}.",
    "economy_daily_claimed": "You already claimed your daily reward! Next daily reward available in {} hour(s) {} minute(s) and {} second(s).",
    "economy_daily_gifted": "**{}**, you gifted your daily reward of {} {} to **{}**.",
    "economy_daily_received": "**{}**, you claimed your daily reward of {} {}.",
    "economy_give_self": "You can't transfer money to yourself!",
    "economy_give_success": "**{}** has given **{}**   {} {}",
    "economy_insufficient_funds": "You have insufficient funds to use this command. Please make sure you have enough!",
    "empty_string": "*Empty*",
    "errorhandler_cooldown": "This command ({}) is currently on cooldown. Please try again after **{}** seconds.",
    "errorhandler_dcmd": "This command ({})has been disabled.",
    "errorhandler_missing_perms": "The bot is missing the following permissions to execute this command: {}",
    "helpformatter_cmd_not_found": "This command either does not exist or your spelling is incorrect.",
    "helpformatter_help": "**General Help Command**",
    "helpformatter_help_description": "You can use **{}modules** to see a list of all available modules.\nYou can use **{}commands <Module>** to see all commands inside a certain module.\n\nYou could also view a detailed profile of every command using **{}h <command>**\n\nYou can add me to your server using this link: https://discordapp.com/oauth2/authorize?client_id=593082021325045760&scope=bot&permissions=8\n\nIf you have any inquiries, suggestions or just want to chat, you could join\nthe **quBot Support Server** here: https://discord.gg/TGnfsH2\n\nHave a nice day!",
    "helpformatter_nohelp_parameter": "This command does not have a description/help string attached to it yet.",
    "module_string": "Module",
    "notes_string": "Note(s)",
    "page_string": "Page",
    "pager_outofrange": "The page you're trying to reach does not exist.",
    "reason_string": "Reason",
    "usage_string": "Usage",
    "user_string": "User",
    "utility_8ball_1": "It is certain.",
    "utility_8ball_10": "Signs point to yes.",
    "utility_8ball_11": "Reply hazy, try again.",
    "utility_8ball_12": "Ask again later.",
    "utility_8ball_13": "Better not tell you now.",
    "utility_8ball_14": "Cannot predict now.",
    "utility_8ball_15": "Concentrate and ask again.",
    "utility_8ball_16": "Don't count on it.",
    "utility_8ball_17": "My reply is no.",
    "utility_8ball_18": "My sources say no.",
    "utility_8ball_19": "Outlook not so good.",
    "utility_8ball_2": "It is decidedly so.",
    "utility_8ball_20": "Very doubtful.",
    "utility_8ball_3": "Without a doubt.",
    "utility_8ball_4": "Yes \u2013 definitely.",
    "utility_8ball_5": "You may rely on it.",
    "utility_8ball_6": "As I see it, yes.",
    "utility_8ball_7": "Most likely.",
    "utility_8ball_8": "Outlook good.",
    "utility_8ball_9": "Yes.",
    "utility_avatar_msg": "{}'s Avatar:",
    "utility_choose_msg": "I randomly picked: {}",
    "utility_roll_msg": "You rolled **{}**.",
    "utility_uinfo_activity": "Activity",
    "utility_uinfo_created": "Account Created",
    "utility_uinfo_id": "ID",
    "utility_uinfo_joined": "Joined Server",
    "utility_uinfo_nickname": "Nickname",
    "utility_uinfo_sroles": "Server Roles ({})",
    "utility_uptime_msg": "Bot has been running for **{}** days, **{}** hours, **{}** minutes and **{}** seconds.",
    "warning_string": "Warning",
}

with open(os.path.join(bot_path, f'data/localization/language_{languagecode}.json'), 'w') as json_file:
    json_file.write(json.dumps(json_lang_en, indent=4, sort_keys=True,separators=(',', ': ')))
json_file.close()#To be deleted at a later date(Used to update json file)

with open(os.path.join(bot_path, f'data/localization/language_{languagecode}.json'), 'r', encoding="utf_8") as json_file:
    lang = json.load(json_file)
json_file.close()

with open(os.path.join(bot_path, 'data/data.json'), 'r') as json_file:
    json_data = json.load(json_file)
json_file.close()

version = json_data["appVersion"]

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



        





