from discord.ext import commands
from datetime import datetime, timedelta
import libs.prefixhandler as prefixhandler
import libs.localizations as localizations
import configparser
import discord
import logging
import json
import sys
import os

# ----------------------------------- #
# Utility functions


def is_venv():
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)


def makefolders(root_path, folders_list):
    for folder in folders_list:
        os.makedirs(os.path.join(root_path, folder), exist_ok=True)


def safe_cast(value, to_type, default=None):
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default

# ----------------------------------- #
# Path checks and initalization


bot_path = os.path.dirname(os.path.realpath(__file__))

subfolders = {'databases', 'data', 'data/localization', 'data/images', 'logs', 'libs', 'modules'}
makefolders(bot_path, subfolders)

open(os.path.join(bot_path, 'libs', '__init__.py'), 'a').close()
open(os.path.join(bot_path, 'modules', '__init__.py'), 'a').close()

# ----------------------------------- #
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

# ----------------------------------- #
# Logging initialization


logging_dict = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20, 'DEBUG': 10}
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

# ----------------------------------- #
# JSON files initialization/writing/loading

json_lang_en = {
    "profiles_customization_reset_title": "Color reset back to default",
    "profiles_customization_title": "New color",
    "profiles_customization_not_found_title": "Color not found",
    "profiles_levelbar_reset_description": "{}, your leveling bar color has been reset back to default.",
    "profiles_levelbar_success": "{}, your profile leveling bar color was successfully changed to: **{}**",
    "profiles_levelbar_not_found": "{}, I could not find the color you requested.",
    "command_levelbar_description": "Changes your profile's leveling bar color to the target one.",
    "command_levelbar_reset_description": "Resets your profile's leveling bar color back to default.",

    "moderation_warnings_dashboard_description": "These are the current automatic warning action settings for **{}**. They can be configured and/or changed at any given time using the following command: {}",
    "moderation_warnings_dashboard_header": "Automatic Actions for {}",
    "moderation_not_configured": "Not configured",
    "warning_lower_string": "warning",
    "warnings_lower_string": "warnings",
    "mute_string": "Mute",
    "kick_string": "Kick",
    "ban_string": "Ban",
    "command_warnings_dashboard_description": "Displays your server's automatic warning action settings.",
    "command_warnings_auto_reset_description": "Resets all automatic warning action settings back to their preconfigured state.",
    "moderation_autoaction_reset_title": "Successful reset",
    "moderation_autoaction_reset_desc": "All automatic warning actions have been reset back to their preconfigured state.",
    "moderation_nuke_clone_reason": "Cloned target channel as a result from a nuke command",
    "moderation_nuke_delete_reason": "Deleted target channel as a result from a nuke command",
    "moderation_nuke_success_title": "Channel nuked",
    "moderation_nuke_success_desc": "Successfully nuked **#{}**. All messages in that channel have been deleted.",
    "moderation_nuke_confirmation_desc": "Type `yes` or `no` to confirm your decision.\nAs a result, all messages within that channel will be deleted.",
    "moderation_nuke_confirmation_footer": "Please be careful as this action is irreversible",
    "moderation_nuke_confirmation_title": "Nuking a text channel",
    "command_channel_nuke_description": "Nukes the target text channel. As a result, all messages in that channel will be deleted.",
    "command_premium_add_description": "Manually adds time to the target user's premium access to the bot.",
    "command_premium_end_description": "Manually ends the target user's premium access to the bot.",
    "premium_add_success_title": "Added premium",
    "premium_add_success_desc": "Successfully added premium time to **{}**.\n**Expires:** {}.\n**Tier:** {}",
    "premium_add_failed": "Uh oh, I ran into some issues when trying to manually add premium time to this person.",
    "premium_end_success_title": "Ended premium",
    "premium_end_success_desc": "Successfully ended **{}**'s premium access to the bot.\nThey will no longer be able to use premium-only features.",
    "premium_tier_not_found": "Failed to add premium to user: Premium tier not recognized.",
    "errorhandler_premium_only": "This command is only available to premium users.",

    "and_string": "and",
    "automation_bye_default": "Goodbye, {}. Wishing you all the best.",
    "automation_gbdisable_already_disabled": "Server member goodbye messages are already disabled.",
    "automation_gbdisable_embed_description": "People who leave this server will no longer be announced.",
    "automation_gbdisable_embed_title": "Server member goodbye messages have been disabled",
    "automation_gbenable_already_enabled": "Server member goodbye messages are already enabled.",
    "automation_gbenable_embed_description": "All future goodbye messages will be sent in the respective text channel.",
    "automation_gbenable_embed_title": "Server member goodbye messages have been enabled",
    "automation_gbmessage_default_already_used": "The default goodbye message is already being used.",
    "automation_gbmessage_default_success": "The server goodbye message has been reset back to default",
    "automation_gbmessage_disabled": "Failed to set custom goodbye message. Please enable server goodbye messages first and try again.",
    "automation_gbmessage_invalid": "Invalid custom goodbye message. Please check for any user errors and try again.",
    "automation_gbmessage_success": "Custom goodbye message has been set successfully",
    "automation_gbscdefault": "Goodbye messages text channel has been set back to default",
    "automation_gbsetchannel": "Farewell messages text channel successfully changed to: #{}",
    "automation_gdisable_already_disabled": "Server member greetings are already disabled.",
    "automation_gdisable_embed_description": "New server members will no longer be announced.",
    "automation_gdisable_embed_title": "Server member greetings have been disabled",
    "automation_gdm_embed_description": "All future greeting messages will be sent to users' direct messages.",
    "automation_gdm_embed_title": "Server member greetings have been enabled",
    "automation_genable_already_enabled": "Server member greetings are already enabled.",
    "automation_genable_embed_description": "All future greeting messages will be sent in the respective text channel.",
    "automation_genable_embed_title": "Server member greetings have been enabled",
    "automation_gmessage_default_already_used": "The default server greeting message is already being used.",
    "automation_gmessage_default_success": "The server greeting message has been reset back to default",
    "automation_gmessage_disabled": "Failed to set custom greeting message. Please enable server greetings first and try again.",
    "automation_gmessage_invalid": "Invalid custom greet message. Please check for any user errors and try again.",
    "automation_gmessage_limit": "Custom message is too long. Maximum character limit: **{}**",
    "automation_gmessage_success": "Custom greeting message has been set successfully",
    "automation_greet_default": "Hey {}, welcome to **{}**!",
    "automation_gscdefault": "Greeting messages text channel has been set back to default",
    "automation_gsetchannel": "Greeting messages text channel successfully changed to: #{}",
    "bot_guild_join_description": "My name is {} and I am a multi-purpose bot that can offer a great variety of features from an extensive moderation toolkit to a global economy, dictionaries, fun, utility commands and a unique strategy game called Conquest.\n\nCreate the experience you want. My capabilities include but are not limited to the following available configurations: disabling select commands and modules, setting a custom bot prefix and language for your discord server.\n\nFeel free to explore around by using any of the following bits of information below:\n**Help Command:** `{}help`\n**Commands:** https://qubot.xyz/commands\n**Support Server:** https://discord.gg/TGnfsH2",
    "bot_guild_join_title": "*Beep boop*...Hello world!",
    "category_string": "Category",
    "command_8ball_description": "Returns an answer for a yes or no question.",
    "command_adjust_description": "Awards/Subtracts a set amount of money to/from the target individual.",
    "command_antonyms_description": "Returns a list of the top antonyms from Thesaurus based on the term you parse to the bot.",
    "command_autoaction_description": "Changes the number of warnings needed for a user to trigger an automatic mute/kick/ban from the server. (Disabled by default)",
    "command_autoaction_disable_description": "Disables the target automatic action from triggering for future user warnings.",
    "command_autoaction_help": "- Using this command will enable the above-mentioned automatic actions if previously disabled.\n- If any of the number of warnings match for mute, kick or ban, the following will take priority from highest to lowest: ban > kick > mute.",
    "command_avatar_description": "Returns the target individual's avatar.",
    "command_avatar_help": "If no user is provided with the command, the bot will instead return your avatar.",
    "command_background_description": "Provides further information about all available profile backgrounds.",
    "command_background_help": "- Providing a number will display a preview of the profile background.\n- Providing a category will display all available backgrounds within that category.",
    "command_ban_description": "Bans the mentioned individual for the provided reason and time length. (Optional)",
    "command_ban_help": "- This command accepts the following time units:\n`m(inutes), h(ours), d(ays), w(eeks)`\n*If no time unit is specified, the input defaults to minutes.*",
    "command_betroll_description": "Lets you bet a certain amount of money on a roll between 1 and 100.",
    "command_bg_buy_description": "Purchases a profile background from the shop for its' corresponding price",
    "command_bg_buy_help": "All bought backgrounds are stored in your inventory and can be used cross-server. You only need to buy it once.",
    "command_bg_equip_description": "Equips a profile background for the server where the command was executed.",
    "command_bg_equip_help": "If you are not sure which profile backgrounds you own, you can view them by using one of the bot's commands to display your profile background inventory.",
    "command_bg_inventory_description": "Shows all profile backgrounds you currently own.",
    "command_bg_inventory_help": "Profile background purchases are global and can be used cross-server.",
    "command_bg_unequip_description": "Changes your profile background back to default.",
    "command_binfo_description": "Displays general information about the bot.",
    "command_binfo_help": "Server bot latency is directly tied to which shard your server is placed in.",
    "command_bio_description": "Sets (or resets) your profile's biography paragraph to the provided text.",
    "command_bio_help": "If you wish to reset your biography paragraph, provide no text to the command.",
    "command_blacklist_add_description": "Blacklists the target user. As a result, they will no longer be able to use the bot in that server.",
    "command_blacklist_description": "Blacklists the target user. As a result, they will no longer be able to use the bot in that server. If the target user is already blacklisted, they will get removed from the blacklist and regain access to bot commands.",
    "command_blacklist_remove_description": "Removes the target user from the bot blacklist. As a result, they will regain access to the bot's commands in that server.",
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
    "command_cjoin_description": "A help command that shows information about the type of settlements based on access.",
    "command_cmds_description": "Displays all commands in a given module",
    "command_code_description": "A command group. If no subcommands are invoked by the user, this command will display your settlement's invide code.",
    "command_code_help": "This command can also be used directly in the bot's direct messages.",
    "command_code_new_description": "Generates a new invite code for your settlement.",
    "command_code_show_description": "Displays your settlement's invite code. The code is sent privately to the author.",
    "command_command_disable_description": "Disables a command for the server where the command was executed in.",
    "command_command_enable_description": "Enables a command for the server where the command was executed in.",
    "command_conquest_withdraw_description": "Withdraws gold from the settlement's treasury",
    "command_conquest_withdraw_help": "- A specified tax rate is applied on the withdrawal process.\n- This command can only be used by **settlement leaders**.",
    "command_currency_description": "Displays the sum of money the target individual has on their profile.",
    "command_currency_help": "If no user is provided with the command, the bot will display the sum of money that you have on your profile.",
    "command_daily_description": "Lets you claim a set sum of money on a daily basis.",
    "command_daily_help": "If you wish to gift your daily reward instead of claiming it for yourself, you can mention the individual when using the command.",
    "command_delsettlement_description": "Deletes the settlement that matches the provided identifier.",
    "command_deposit_description": "Deposits a sum of money into the treasury of the settlement you are currently part of.",
    "command_deposit_help": "You need to be part of a settlement to be able to use this command.",
    "command_duel_description": "Duels other people for money.",
    "command_export_commands_description": "Exports all command metadata into a JSON file. The target file is saved in the folder 'exports'.",
    "command_export_description": "Exports various bot data into a file.",
    "command_export_help": "**Available export functions:**\n\u2022 **commands** = Exports command metadata into a JSON file.",
    "command_give_description": "Transfers a set amount of money to another user.",
    "command_giveaway_end_description": "Ends a giveaway by a provided bot message ID",
    "command_giveaway_group_description": "Giveaway command group. Please refer to `giveaway start` and `giveaway end` for more information.",
    "command_giveaway_start_description": "Starts a currency giveaway. Users can claim their reward by reacting to the bot message.",
    "command_goodbye_description": "Toggles server member goodbye messages on/off on the server.",
    "command_goodbye_disable_description": "Disables server member goodbye messages on the server.",
    "command_goodbye_enable_description": "Enables server member goodbye messages on the server.",
    "command_goodbye_mdefault_description": "Resets the server member goodbye message back to default.",
    "command_goodbye_message_description": "Changes the goodbye message to a custom one. Feel free to check the notes to be able to fully utilize this command.",
    "command_goodbye_message_help": "- This command supports Discord Markdown. (Chat formatting: bold, italics, underline, etc.)\n- You can include the following in your message:\n**{mention}** - Mentions the User;\n**{user}** - Shows Username;\n**{server}** - Shows server name;\n**{membercount}** - Shows number of people in server;",
    "command_goodbye_scdefault_description": "Resets the server goodbye messages text channel back to default.",
    "command_goodbye_setchannel_description": "Sets the text channel where server goodbye messages are going to be sent by the bot.",
    "command_goodbye_test_description": "Command to test your custom server goodbye message.",
    "command_greetings_description": "Toggles server member greeting messages on/off on the server.",
    "command_greetings_disable_description": "Disables server member greeting messages on the server.",
    "command_greetings_dm_description": "Enables server member greetings on the server. Instead of a text channel on your server, future messages will instead be sent directly to users' direct messages.",
    "command_greetings_enable_description": "Enables server member greeting messages on the server.",
    "command_greetings_mdefault_description": "Resets the server greeting message back to default.",
    "command_greetings_message_description": "Changes the greeting message to a custom one. Feel free to check the notes to be able to fully utilize this command.",
    "command_greetings_message_help": "- This command supports Discord Markdown. (Chat formatting: bold, italics, underline, etc.)\n- You can include the following in your message:\n**{mention}** - Mentions the User;\n**{user}** - Shows Username;\n**{server}** - Shows server name;\n**{membercount}** - Shows number of people in server;",
    "command_greetings_scdefault_description": "Resets the server greeting messages text channel back to default.",
    "command_greetings_setchannel_description": "Sets the text channel where server greeting messages are going to be sent by the bot.",
    "command_greetings_setchannel_help": "By default, these messages are sent to **#general**. If no text channel exists with that name, it uses the first text channel on the list.",
    "command_greetings_test_description": "Command to test your custom server member greetings message.",
    "command_jprivate_description": "Command to join a private settlement.",
    "command_jpublic_description": "Command to join a public settlement.",
    "command_kick_description": "Kicks the mentioned individual for the provided reason. (Optional)",
    "command_langs_description": "Returns a list of locally detected language(localization) packages",
    "command_langset_description": "Changes the language of the bot",
    "command_lastjoined_description": "Displays the newest members of your server.",
    "command_lastjoined_help": "A maximum of 20 users can be displayed at once.",
    "command_latencies_description": "Returns the latencies (in miliseconds) for every active shard.",
    "command_leaderboard_description": "Shows your server's experience leaderboard.",
    "command_leveling_disable_description": "Disables experience gain and leveling on your server.",
    "command_leveling_enable_description": "Enables experience gain and leveling on your server.",
    "command_leveling_reset_description": "Resets experience and level progression for all users on your server back to 0.",
    "command_leveling_toggle_description": "Toggles (enables/disables) experience gain and leveling on your server.",
    "command_load_description": "Loads modules into the bot application.",
    "command_market_description": "A command group. If no subcommands are invoked by the user, this command will display the resource market.",
    "command_market_help": "This command can also be used directly in the bot's direct messages.",
    "command_massnick_description": "Changes the nickname of all mentioned individuals",
    "command_massnick_reset_description": "Resets all mentioned individuals' nicknames",
    "command_mbuy_description": "Buys a set amount of resources from the market.",
    "command_meanings_definition": "This command also supports phrases.",
    "command_meanings_description": "Returns a list of definitions based on the term you parse to the bot.",
    "command_modlog_channel_description": "Moves all moderation action messages to a separate channel.",
    "command_modlog_default_description": "Restores the modlog channel settings back to default. As a result, future moderation actions will be displayed in the channel where the command was executed.",
    "command_module_help": "The module file needs to be present in the modules folder of the bot.",
    "command_modules_description": "Displays all loaded modules.",
    "command_modules_disable_description": "Disables the target cog/module on the server where the command was executed.",
    "command_modules_enable_description": "Enables the target cog/module on the server where the command was executed.",
    "command_modules_hide_description": "Hides a module from the list of loaded modules.",
    "command_modules_unhide_description": "Reveals a hidden module from the list of loaded modules.",
    "command_msell_description": "Sells a set amount of resources on the market.",
    "command_mute_description": "Mutes the target individual from chatting on the server for a provided time period. (Optional)",
    "command_mute_help": "This command accepts the following time units:\n`m(inutes), h(ours), d(ays), w(eeks)`\n*If no time unit is specified, the input defaults to minutes.*",
    "command_prefix_description": "Shows or changes the bot's prefix on the server.",
    "command_prefix_help": "If you do not include a new prefix, the command will instead display the bot's current prefix on the server.",
    "command_prefix_reset_description": "Resets the bot's prefix on the server back to default.",
    "command_prefix_show_description": "Shows the bot's prefix on the server.",
    "command_profile_description": "Displays the profile of the target user.",
    "command_profile_help": "If you do not specify a user, the bot will display your profile.",
    "command_promote_description": "Promotes the target individual to settlement leader.",
    "command_promote_help": "This command can **ONLY** be used by settlement leaders.",
    "command_purge_description": "Deletes a set number of messages.",
    "command_purge_help": "**Available filters:**\n\u2022 **bot/bots** = Deletes only bot messages.\n\u2022 **me/author** = Deletes only the command author's messages.\n\u2022 **embed/embeds** = Deletes only embeds.\n\u2022 **file/attachment** = Deletes only file attachments.\n\u2022 **user/member <@somebody>** = Deletes only the specified user's messages.\n\u2022 **has <text>** = Deletes all messages that contain the provided bit of text.\n\u2022 **regex <regex>** = Deletes only messages that match the provided regular expression.",
    "command_reload_description": "Reloads modules loaded into the bot application.",
    "command_remove_description": "Politely kicks the bot off your server.",
    "command_report_description": "Reports the target user for a particular reason.",
    "command_report_disable_description": "Disables user reporting for the server where the command was used.",
    "command_report_help": "- A report reason must be provided in order to use this command.\n- This command will only work when a report channel is set. (Disabled by default)",
    "command_report_setchannel_description": "Selects a text channel where future user reports are going to be sent.",
    "command_report_setchannel_help": "Using this command will enable user reports if they were previously disabled. (Disabled by default)",
    "command_reqs_description": "Displays target settlement building upgrade requirements for every level from 1 to 10.",
    "command_resources_description": "Displays the amount of resources currently stored in your settlement.",
    "command_restart_description": "Restarts the bot",
    "command_roleid_description": "Returns the target role's ID for the server the command was typed in.",
    "command_roll_description": "Rolls a number in a given range.",
    "command_roll_help": "If no number is provided with the command, the bot will roll a number between 1 and 100.",
    "command_sconvert_description": "Converts the settlement access type to public/private for your settlement.",
    "command_sconvert_help": "You must be the leader of this settlement to be able to use this command.",
    "command_serverid_description": "Returns the server's ID for the server the command was typed in.",
    "command_setactivity_description": "Changes the bot's activity",
    "command_setactivity_help": "This command requires two arguments: the type of activity (playing, listening, watching) and the message itself.",
    "command_setactivity_stats_description": "Starts an automatic bot activity rotation.",
    "command_setactivity_stats_reset_description": "Stops the automatic bot activity rotation.",
    "command_setname_description": "Changes the name of the bot.",
    "command_setstatus_description": "Changes the bot's status. (Online by default)",
    "command_setstatus_help": "This command requires one argument and it needs to be one of the following: `online, offline, idle, dnd, invisible`",
    "command_settings_description": "Displays your server's bot settings.",
    "command_settings_reset_description": "Resets all server bot settings back to default. Be careful, this action is irreversible.",
    "command_shutdown_description": "Shutdowns the bot",
    "command_skick_description": "Kicks the target individual from the settlement.",
    "command_sleader": "This command can **ONLY** be used by settlement leaders.",
    "command_sleaderboard_description": "Returns the settlements' leaderboard",
    "command_sleaderboard_help": "This command takes one optional argument - the page number. If no argument is passed, then it defaults to 1.",
    "command_sleave_description": "Leave the settlement you are currently in.",
    "command_sleave_help": "- Leaders of settlements with multiple residents cannot leave settlement without transferring ownership.\n- Settlements with only one resident will get **DESTROYED** in the process!",
    "command_slowmode_description": "Sets a chatting cooldown for the channel where the command was used.",
    "command_slowmode_disable_description": "Disables slowmode for the channel where the command was used.",
    "command_slowmode_help": "This command accepts the following time units: `s(econds), m(inutes), h(ours)`",
    "command_softban_description": "Soft bans the mentioned individual for the provided reason. (Optional)",
    "command_softban_help": "Soft bans in essence kick the target individual from the server while deleting their messages. It's not the same as a normal ban.",
    "command_srename_description": "Renames your settlement to the given name.",
    "command_srename_force_description": "Force renames the target settlement to the provided input.",
    "command_srename_help": "- You must be the leader of this settlement to be able to use this command.\n- In order to rename your settlement, you need to pay a fee of 500 gold.\n- Settlement names have a character limit of 50 characters.",
    "command_synonyms_description": "Returns a list of the top synonyms from Thesaurus based on the term you parse to the bot.",
    "command_translate_description": "Shows general information about the translation of the bot.",
    "command_uinfo_description": "Shows the target individual's user information.",
    "command_uinfo_help": "If no user is provided with the command, the bot will return your information instead.",
    "command_unban_description": "Unbans the target individual from the server.",
    "command_unban_help": "Since the target individual can not be mentioned directly within the server, a **<username>#<discriminator>** or a **User ID** should be provided.",
    "command_unload_description": "Unloads modules from the bot application.",
    "command_unmute_description": "Unmutes the target individual if they were previously muted using the bot.",
    "command_uptime_description": "Returns the bot's uptime.",
    "command_urbandict_description": "Returns the top urban dictionary definition based on the term you parse to the bot.",
    "command_userid_description": "Returns the target individual's Discord ID.",
    "command_userid_help": "If no user is provided with the command, the bot will use the user who executed it.",
    "command_vote_description": "A help command that provides further information about bot voting.",
    "command_warn_description": "Warns the target user for a particular reason. As a result, this individual will receive a direct message from the bot.",
    "command_warnings_delete_description": "Deletes a specific warning that was issued to the target individual.",
    "command_warnings_description": "Displays a list of warnings for the target individual.",
    "command_warnings_help": "You can navigate through pages by providing a page number after the username.",
    "command_warnings_reset_description": "Resets all warnings for the target individual.",
    "conquest_attack_args": "No target user was specified.",
    "conquest_attack_enemy_no": "The settlement you're trying to attack does not exist!",
    "conquest_attack_enemy_part_of": "The person you're trying to attack does not seem to be part of any settlements.",
    "conquest_attack_enemy_self": "You cannot attack this user because they are part of your settlement.",
    "conquest_attack_result_defeat": "Defeat",
    "conquest_attack_result_victory": "Victory",
    "conquest_attack_self": "You can't attack your own settlement.",
    "conquest_attack_wd": "Your Wins/Defeats",
    "conquest_attack_you_no": "You can not attack without a settlement.",
    "conquest_building_description_1": "The Town Hall is the main structure in your settlement. Upgrading this building increases the level limit of all other buildings.",
    "conquest_building_description_10": "The Academy is a mixed offensive and defensive building. With technological advancements, your settlement learns how to attack and defend more efficiently. Upgrading your academy slightly increases your settlement's overall attack and defense.",
    "conquest_building_description_2": "The Training Grounds are the core offensive structure in your settlement. Upgrading this building increases your settlement's overall offense. Therefore, upgrades will increase your chances in battle.",
    "conquest_building_description_3": "The Market Square offers resource trading for your settlement. This structure unlocks the possibility to buy and sell resources.",
    "conquest_building_description_4": "The Walls are the core defensive structure of your settlement. Upgrading this construction increases your settlement's overall defense. Therefore, upgrades will increase your chances of withstanding enemy attacks.",
    "conquest_building_description_5": "The Quarry produces the resource: Stone. Upgrading this structure will increase the daily production rate of stone for your settlement.",
    "conquest_building_description_6": "The Farms produce the resource: Food. Upgrading this structure will increase the daily production rate of food for your settlement.",
    "conquest_building_description_7": "The Weavery produces the resource: Cloth. Upgrading this structure will increase the daily production rate of cloth for your settlement.",
    "conquest_building_description_8": "The Lumberjack's Camp produces the resource: Wood. Upgrading this structure will increase the daily production rate of wood for your settlement.",
    "conquest_building_description_9": "The Warehouse, also known as your settlement's treasury, is a key part of your settlement. The default settlement treasury has a limited capacity. Unlocking this building removes that resource amount limit.",
    "conquest_building_next_upgrade": "Next Upgrade",
    "conquest_building_string": "Building",
    "conquest_buildings_title": "Settlement Status",
    "conquest_buy_no_market": "Failed to buy resources: Your settlement does not have a **Market Square**.",
    "conquest_chances": "Your chance of winning this battle was **{}%**",
    "conquest_code_fail": "You aren't the leader of any settlement.",
    "conquest_code_new_fail": "Failed to change invite code. You do not seem to be the leader of any settlements.",
    "conquest_code_new_success": "Successfully changed code. Your new settlement invite code is **{}**",
    "conquest_code_success": "Your settlement's invite code is `{}`",
    "conquest_convert_success": "Successfully converted settlement access to `{}`",
    "conquest_create_args": "Failed to create a settlement: Please check if all arguments are correctly structured and try again.",
    "conquest_create_part_of": "I could not create your settlement. You can only be part of one settlement at a time.",
    "conquest_create_public_private": "The settlement's type can either be **public** or **private**.",
    "conquest_create_success": "{}, your settlement was created successfully.",
    "conquest_create_title": "New Settlement",
    "conquest_defeat_string_1": "Unsuccessful attempt to pillage **{}**: As you approached the enemy settlement, a volley of arrows struck your army's shields. Your soldiers managed to reach the enemy walls and swiftly scaled up using ladders. A fierce battle erupted at the top. Despite your army's efforts, enemy swordsmen and spearmen tipped the scales in their favour. Some of your soldiers were killed in the process. Forced to pull back, the rest of your army successfully retreats from the battlefield, escorting you back to your kingdom.",
    "conquest_defeat_string_2": "Unsuccessful attempt to pillage **{}**: As you approached the enemy settlement, a volley of arrows struck your army's shields. Your soldiers managed to reach the enemy walls and slowly but steadily scaled up using ladders. A fierce battle erupted at the top. Despite your army's efforts, enemy swordsmen and spearmen tipped the scales in their favour. Most of your soldiers were killed in the process. Fortunately, a small group successfully retreated from the battlefield, escorting you back to your kingdom.",
    "conquest_defeat_string_3": "Unsuccessful attempt to pillage **{}**: As you approached the enemy settlement, a volley of arrows struck your army's shields. Your soldiers managed to reach the enemy walls and slowly but steadily scaled up using ladders. A fierce battle erupted at the top. Despite your army's efforts, most of your soldiers were killed in the battle. Fortunately, a small group successfully retreated from the battlefield, escorting you back to your kingdom.",
    "conquest_defeat_string_4": "Unsuccessful attempt to pillage **{}**: As you approached the enemy settlement, a volley of arrows struck your army's shields. Your soldiers managed to reach the enemy walls and slowly and painfully scaled up using ladders. A heated battle erupted at the top. Despite your army's efforts, most of your soldiers were killed in the battle. Fortunately, a small group successfully retreated from the battlefield, escorting you back to your kingdom.",
    "conquest_defeat_string_5": "Unsuccessful attempt to pillage **{}**: As you approached the enemy settlement, a volley of arrows struck your army's shields. Your soldiers managed to reach the enemy walls and slowly and painfully scaled up using ladders. A heated battle erupted at the top. Despite your army's efforts, they fail miserably. Most of your troops were massacred on the spot. A very small group successfully retreated from the battlefield, escorting you back to your kingdom.",
    "conquest_dels_confirmation_description": "Type `yes` or `no` to confirm your decision. As a result, settlement with `ID {}` will be deleted.",
    "conquest_dels_confirmation_title": "Deleting a settlement",
    "conquest_dels_success": "Successfully deleted settlement with matching ID {}",
    "conquest_deposit_success": "You successfully deposited {} {} into the settlement's treasury.",
    "conquest_entry_requirement": "The entry fee doesn't meet the minimal entry fee requirement!",
    "conquest_experience": "Experience Points",
    "conquest_info_args": "No settlement name detected. Please try again.",
    "conquest_info_fail": "This settlement could not be found.",
    "conquest_info_population": "Population",
    "conquest_info_settlement": "Settlement",
    "conquest_info_type": "Settlement Type",
    "conquest_insufficient_funds": "Funds not sufficient to deposit for the settlement's starting fee.",
    "conquest_invalid_settlement_id": "No settlement found with that ID. Please check for input errors and try again",
    "conquest_invalid_settlement_name": "Invalid settlement name provided. Please use standard characters.",
    "conquest_join_age_restriction": "Your discord account needs to be at least one week old to be able to join a settlement!",
    "conquest_join_embed_description": "There are two type of settlements based on their access:\n\n> {} **public** - Anyone can join this type of settlement. The only thing you need to do is to cover the minimum entry fee.\n> `{}join public <@somebody>`\n\n> {} **private** - Only people with an invite code can join this type of settlement. This invite code can either be provided by the leader of the settlement or anyone who already has it. Be careful when sharing your code with others!\n> `{}join private <code>`\n\nIf you are not sure what kind of settlement it is, check the lock icon on its info page.",
    "conquest_join_embed_title": "Joining a settlement",
    "conquest_join_fail_user": "The target user does not seem to be part of a settlement.",
    "conquest_join_min_entry": "Your personal funds are not sufficient to cover this settlement's entry fee (**{}**).",
    "conquest_join_not_found": "Failed to join settlement: Settlement not found.",
    "conquest_join_part_of": "You are already part of a settlement.",
    "conquest_join_private_msg": "Failed to join settlement: You are trying to join a private settlement without an invite code.",
    "conquest_join_success": "You successfully joined: {}",
    "conquest_join_target_fail": "Failed to join settlement: This user is not part of any settlement.",
    "conquest_leaderboard_description": "The current settlement leaderboard for **{}**.",
    "conquest_leaderboard_empty": "The settlement leaderboard is empty. I could not find any settlements to rank.",
    "conquest_leaderboard_ranked": "Your settlement is currently ranked **#{}** in this server.",
    "conquest_leaderboard_title": "Settlements Leaderboard",
    "conquest_leave_confirmation_description": "Type `yes` or `no` to confirm your decision.",
    "conquest_leave_confirmation_title": "Leaving a settlement",
    "conquest_leave_leader": "You cannot leave a settlement with more than one resident where you are still the leader.",
    "conquest_leave_not_found": "Failed to leave settlement: Settlement not found.",
    "conquest_leave_single": "You are the only person in this settlement. If you leave it, it will be destroyed in the process!",
    "conquest_leave_success": "You successfully left this settlement.",
    "conquest_losses": "Losses",
    "conquest_market_buy_fail": "Failed to buy resources: Insufficient funds.",
    "conquest_market_buy_success": "Successfully bought {:,} {}, costing your settlement {:,} {}",
    "conquest_market_buy_warehouse": "Failed to buy resources: The requested quantity is more than what you can hold in your warehouse. Consider upgrading it.",
    "conquest_market_reminder": "Market prices change once every 24 hours.",
    "conquest_market_sell_fail": "Failed to sell resources: Insufficient quantity in warehouse.",
    "conquest_market_sell_success": "Successfully sold {:,} {}. Your settlement earned {:,} {}",
    "conquest_market_title": "Market daily prices:",
    "conquest_max_reached": "Building maximum level reached.",
    "conquest_not_leader": "Only the leader of this settlement can use this command.",
    "conquest_not_part_of": "You do not seem to be part of any settlements.",
    "conquest_piece": "piece",
    "conquest_pillaged_gold": "Pillaged Gold",
    "conquest_promote_confirmation": "Please type **'yes'** or **'no'** to confirm whether you want to proceed with settlement ownership transfer to {}.",
    "conquest_promote_self": "You cannot promote yourself.",
    "conquest_promote_settlement_fail": "This person is not in your settlement.",
    "conquest_promote_success": "Successfully transfered ownership to {}",
    "conquest_rename_force": "The target settlement (ID: {}) was successfully renamed to: *{}*",
    "conquest_rename_no_funds": "You do not have enough funds to rename your settlement.\n**Required amount:** {} {}",
    "conquest_rename_success": "Your settlement was successfully renamed to: *{}*.\nAs a result, {} {} was deducted from you treasury.",
    "conquest_requirements_header": "Needed resources to upgrade this building:",
    "conquest_requirements_range": "Invalid building index: Please use numbers between (including) 1 and 10",
    "conquest_requirements_title": "**{}** | Resource Requirements",
    "conquest_resources_cloth": "Cloth",
    "conquest_resources_food": "Food",
    "conquest_resources_gold": "Gold",
    "conquest_resources_needed": "Needed Resources",
    "conquest_resources_stone": "Stone",
    "conquest_resources_wood": "Wood",
    "conquest_roll": "**Roll**",
    "conquest_sell_no_market": "Failed to sell resources: Your settlement does not have a **Market Square**.",
    "conquest_sell_price": "Sell price",
    "conquest_settlement_footer": "Settlement: {}",
    "conquest_sinfo_part_of": "{}, you are currently not part of any settlements.",
    "conquest_skick_self": "You cannot kick yourself out of the settlement. Instead, consider leaving.",
    "conquest_skick_success": "You successfully kicked {} from the settlement.",
    "conquest_sname_too_long": "The settlement's name must between 3 and {} characters long.",
    "conquest_summary": "Summary",
    "conquest_target_not_part_of": "This person is not part of any settlements.",
    "conquest_upgrade_fail": "You do not have enough resources to upgrade **{}**.",
    "conquest_upgrade_max_level": "You have already reached the maximum level of this building.",
    "conquest_upgrade_success": "You upgraded {} to Level {}.",
    "conquest_upgrade_th": "Upgrade the Town hall to unlock next building level.",
    "conquest_warehouse_title": "Warehouse",
    "conquest_win_percentage": "*Win Percentage*",
    "conquest_win_string_1": "Your settlement's army successfully pillaged **{}**. Your soldiers reached the enemy walls without much difficulty. A fierce battle erupted at the top. A successful breach has been made into the enemy settlement's treasury. Your troops grabbed what they can with their hands. You deal a significant amount of damage to your enemy's settlement. However, as enemy forces regroup, your army is forced to retreat.",
    "conquest_win_string_2": "Your settlement's army successfully pillaged **{}**. Your soldiers slowly reached the enemy walls as enemy archers fired volleys of arrows. A fierce battle erupted at the top. A successful breach has been made into the enemy settlement's treasury. Your troops grabbed what they can with their hands. You deal a significant amount of damage to your enemy's settlement. However, as enemy forces regroup, your army is forced to retreat.",
    "conquest_win_string_3": "Your settlement's army successfully pillaged **{}**. Your soldiers slowly reached the enemy walls as enemy archers fired volleys of arrows. Your army's battering ram was used to breach into the enemy's fortress. A fierce battle erupted on the streets. After a long while, a successful breach has been made into the enemy settlement's treasury. Your troops grabbed what they can with their hands. You deal some damage to your enemy's settlement. However, as enemy forces regroup, your army is forced to retreat.",
    "conquest_win_string_4": "Your settlement's army successfully pillaged **{}**. Your soldiers slowly reached the enemy walls as enemy archers fired volleys of arrows. Your army's battering ram was used to breach into the enemy's fortress. A fierce battle erupted on the streets. After a long while, your troops decided to instead pillage the nearby houses as breaching into the treasury deemed too difficult. You deal some damage to your enemy's settlement. Enemy forces regroup and your army is forced to retreat.",
    "conquest_win_string_5": "Your settlement's army successfully pillaged **{}**. Your soldiers slowly reached the enemy walls as enemy archers fired volleys of arrows. Your army's battering ram was used to breach into the enemy's fortress. A fierce battle erupted on the streets. After a long while, your troops decided to instead pillage the nearby houses as breaching into the treasury deemed too difficult. Almost no damage was dealt to your enemy's settlement. Enemy forces regroup and your army is forced to retreat.",
    "conquest_wins": "Wins",
    "conquest_withdraw_confirmation": "Do you really want to withdraw money from your settlement? Please type **'yes' (y)** or **'no' (n)** to confirm your choice.",
    "conquest_withdraw_confirmation_note": "*Please note that there is a {}% tax rate on the withdrawal process.*",
    "conquest_withdraw_insufficient_funds": "The requested amount is greater than what you have in your settlement's treasury",
    "conquest_withdraw_success": "Successfully withdrawn {} gold from the settlement: *{}*",
    "core_activity_help": "{}h for help",
    "core_channelid_msg": "{} | #{}'s ID is: **{}**",
    "core_cmds_embed_title": "**{}** Commands",
    "core_cmds_list_marg": "Please specify a module.",
    "core_cmds_list_not_found": "**{}** module not found.",
    "core_command_already_disabled": "Command ({}) is already disabled on this server.",
    "core_command_already_enabled": "Command ({}) is already enabled on this server.",
    "core_command_disable": "Successfully disabled command ({}) in server.",
    "core_command_enable": "Successfully enabled command ({}) in server.",
    "core_command_restricted_module": "This command is part of a module (**{}**) that is marked as integral and can't be disabled.",
    "core_export_commands_success": "Successfully exported all bot commands to local JSON file.",
    "core_latencies": "Shard **{}** ({} Servers) | Latency: {}ms {}\n",
    "core_latencies_msg": "Shards Overview",
    "core_module_disable_already_disabled": "Module '**{}**' is already disabled on this server.",
    "core_module_disable_dependencies": "This module cannot be disabled as the following currently enabled modules depend on it: *{}*",
    "core_module_disable_dependencies_hint": "If you wish to disable this module, consider disabling the abovementioned first.",
    "core_module_disable_msg": "Successfully disabled module '**{}**' on this server.",
    "core_module_disable_not_found": "Could not disable module. Invalid module name was provided.",
    "core_module_disable_restricted": "Module '**{}**' is marked as integral and can't be disabled.",
    "core_module_enable_already_enabled": "Module '**{}**' is already enabled on this server.",
    "core_module_enable_dependencies": "This module cannot be enabled as it depends on the following modules that need to be enabled first: *{}*",
    "core_module_enable_msg": "Successfully enabled the module '**{}**' on this server.",
    "core_module_enable_not_found": "Could not enable module. Invalid module name was provided.",
    "core_module_hide_fail": "Failed to hide module. Please check if said module has been loaded or is spelled correctly",
    "core_module_hide_hidden": "This module is already hidden!",
    "core_module_hide_success": "Module **{}** successfully hidden.",
    "core_module_load_fail": "This module has either already been loaded or does not exist.",
    "core_module_load_success": "Module **{}** successfully loaded.",
    "core_module_reload_fail": "This module could not be reloaded as it has not been loaded in yet.",
    "core_module_reload_success": "Module **{}** successfully reloaded.",
    "core_module_unhide_fail": "Failed to unhide module. Please check if said module has been loaded or is spelled correctly",
    "core_module_unhide_success": "Module **{}** successfully unhidden.",
    "core_module_unhide_visible": "This module is already visible!",
    "core_module_unload_fail": "This module has either already been unloaded or does not exist.",
    "core_module_unload_success": "Module **{}** successfully unloaded.",
    "core_modules_list": "List of modules:",
    "core_remove_msg": "Thank you for having me on this server. Have a nice day!",
    "core_restart": "Restarting bot...",
    "core_roleid_msg": "{} | The ID for role {} is: **{}**",
    "core_serverid_msg": "{}'s ID is: **{}**",
    "core_setactivity": "The bot is now {}",
    "core_setactivity_reset": "The bot's activity has been reset",
    "core_setactivity_stats": "Started an automatic bot activity rotation",
    "core_setactivity_stats_reset": "Stopped the automatic bot activity rotation",
    "core_shutdown": "Shutting down bot...",
    "core_translate_description": "Localization for the bot is done and supported by the community.\nIf you wish to contribute, visit the **following link**:\nhttps://crowdin.com/project/qubot",
    "core_translate_title": "Bot Translation",
    "core_userid_msg": "{}'s Discord ID is: **{}**",
    "created_string": "Created",
    "day_string": "day",
    "days_string": "days",
    "description_string": "Description",
    "dictionaries_antonyms": "**Antonyms**",
    "dictionaries_english_only": "This command supports only **English words & phrases**",
    "dictionaries_synonyms": "**Synonym(s)**",
    "dictionaries_term": "Term: {}",
    "dictionaries_urbandict_title": "**Top urban dictionary definition(s)**",
    "dictionaries_word_not_found": "This word could not be found in the dictionary.",
    "disabled_commands_string": "Disabled Commands",
    "disabled_modules_string": "Disabled Modules",
    "economy_adjust_award_msg": "**{}** was awarded {:,} {}.",
    "economy_adjust_subtract_msg": "**{}** was withheld {:,} {}.",
    "economy_betroll_fail_msg": "Oops! You rolled {} but did not win anything. Please try again.",
    "economy_betroll_jackpot": "**JACKPOT!!!** Congratulations, you rolled {} and won {:,} {}.",
    "economy_betroll_msg": "Congratulations, you rolled {} and won {:,} {}.",
    "economy_cgiveaway_msg": "React with {} to this message to claim **{:,} {}**",
    "economy_cgiveaway_title": "Currency Giveaway",
    "economy_currency_msg": "**{}** has {:,} {}",
    "economy_daily_claimed_description": "The next daily reward available in: {}.",
    "economy_daily_claimed_title": "You already claimed your daily reward!",
    "economy_daily_gifted": "**{}**, you gifted your daily reward of {:,} {} to **{}**.",
    "economy_daily_received": "**{}**, you claimed your daily reward of {:,} {}.",
    "economy_duel_author_no_funds": "{}, you do not have enough funds to initiate this duel.",
    "economy_duel_cancel": "{}, {} declined your offer to duel.",
    "economy_duel_confirm_description": "{} {}, {} wants to duel you for {:,} {}. Do you accept this fight?\n\nType `yes` or `no` to confirm your decision.",
    "economy_duel_confirm_title": "Duel Proposal",
    "economy_duel_duel_self": "{}, you can't duel yourself.",
    "economy_duel_result": "{} {} stands victorious! They won {:,} {}.",
    "economy_duel_target_no_funds": "{}, your target does not have enough funds to accept your offer.",
    "economy_duel_timeout": "{}, your opponent did not respond within the given time limit.",
    "economy_give_self": "You can't transfer money to yourself!",
    "economy_give_success": "**{}** has given **{}** {:,} {}",
    "economy_insufficient_funds": "You have insufficient funds to use this command. Please make sure you have enough!",
    "empty_string": "*Empty*",
    "errorhandler_cooldown": "This command ({}) is currently on cooldown. Please try again after **{}** seconds.",
    "errorhandler_dcmd": "This command ({}) is currently disabled.",
    "errorhandler_missing_perms": "The bot is missing the following permissions to execute this command: {}",
    "errorhandler_nsfw_channel_required": "This command ({}) can only be used in NSFW channels.",
    "exp_string": "EXP",
    "goodbye_channel_string": "Goodbye Channel",
    "greetings_channel_string": "Greetings Channel",
    "guild_status_premium": "Premium",
    "guild_status_standard": "Standard",
    "guild_status_string": "Server Status",
    "guilds_string": "Servers",
    "helpformatter_cmd_not_found": "This command either does not exist or was typed in incorrectly.",
    "helpformatter_help": "General Help",
    "helpformatter_help_description": "You can use `{}modules` to see a list of all available modules.\nYou can use `{}commands <module>` to see all commands inside a certain module.\n\nYou can also view a detailed profile of every command using `{}h <command>`\n\nIf you need help with my configuration for your server, use `{}settings` in your server.\n\nHave a nice day!\n[Add to Server](https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=1073212790) | [Website](https://qubot.xyz/) | [Support Server](https://discord.gg/TGnfsH2)",
    "helpformatter_nohelp_parameter": "This command does not have a description/help string attached to it yet.",
    "helpformatter_optional": "{ } = Optional",
    "hour_string": "hour",
    "hours_string": "hours",
    "id_string": "ID",
    "joined_string": "Joined",
    "language_string": "Language",
    "level_string": "Level",
    "minute_string": "minute",
    "minutes_string": "minutes",
    "moderation_autoaction_ban": "Your last warning triggered an automatic ban action from this server.",
    "moderation_autoaction_disable": "Automatic {} disabled. To enable it again, set it to a new value.",
    "moderation_autoaction_kick": "Your last warning triggered an automatic kick action from this server.",
    "moderation_autoaction_max": "Automatic actions cannot exceed the maximum warnings limit, which is {}",
    "moderation_autoaction_success": "Gotcha, an automatic ` {} ` will be triggered when a user reaches **{}** warnings!",
    "moderation_ban_dm": "You have been banned from **{}** for the following reason: {}.",
    "moderation_ban_embed_footer": "Banned by: {}",
    "moderation_ban_embed_title": "The following users were banned out of the server",
    "moderation_ban_embed_users": "Banned Users",
    "moderation_ban_empty": "{}, I could not ban the provided users. They might already be banned or have higher role privileges than me.",
    "moderation_ban_not_found": "The user(s) you are trying to ban could not be found.",
    "moderation_ban_temp_dm": "You have been temporarily banned from **{}** for the following reason: {}. Your ban will expire on {}.",
    "moderation_blacklist_embed_description": "The following users were blacklisted. If any of the target users is not on this list, they are probably already blacklisted.",
    "moderation_blacklist_embed_footer": "Blacklisted by: {}",
    "moderation_blacklist_embed_title": "Blacklisted Users",
    "moderation_blacklist_empty": "{}, I could not blacklist the provided users. They are probably already blacklisted or are no longer in this server.",
    "moderation_blacklist_remove_embed_description": "The following users' blacklisted status was discharged. If any of the target users is not on this list, they are probably not blacklisted.",
    "moderation_blacklist_remove_embed_footer": "Approved by: {}",
    "moderation_blacklist_remove_embed_title": "Discharged Blacklisted Users",
    "moderation_blacklist_remove_empty": "{}, I could not discharge the provided users' blacklist status. They are probably not blacklisted or are no longer in this server.",
    "moderation_blacklist_remove_self": "{}, you can't remove yourself from the blacklist.",
    "moderation_blacklist_self": "{}, you can't blacklist yourself.",
    "moderation_channel_forbidden": "{}, I don't have access to this channel. You could either grant me access to it or pick another text channel.",
    "moderation_embed_expiration": "Expires",
    "moderation_kick_embed_footer": "Kicked by: {}",
    "moderation_kick_embed_title": "The following users were kicked out of the server",
    "moderation_kick_embed_users": "Kicked Users",
    "moderation_kick_empty": "{}, I could not kick the provided users. They might no longer be in this server or have higher role privileges than me.",
    "moderation_kick_not_found": "The user(s) you are trying to kick could not be found.",
    "moderation_lastjoined_header": "Newest Members of {}",
    "moderation_modlog_default_embed_description": "Future messages will be displayed in the same channel where the command was executed.",
    "moderation_modlog_default_embed_title": "Moderation actions channel has been reset back to default",
    "moderation_modlog_embed_description": "All future moderation action messages will be displayed in {}.",
    "moderation_modlog_embed_title": "Moderation actions channel successfully changed",
    "moderation_mute_dm": "You have been muted from **{}**. You can no longer send messages in that server.",
    "moderation_mute_embed_footer": "Muted by: {}",
    "moderation_mute_embed_title": "The following users were muted from the server",
    "moderation_mute_embed_users": "Muted Users",
    "moderation_mute_empty": "{}, I could not mute the provided users. They are most likely already muted.",
    "moderation_mute_not_found": "The user(s) you are trying to mute could not be found.",
    "moderation_mute_temp_dm": "You have been muted in **{}**. Your mute will expire on {}.",
    "moderation_purge_invalid_filter": "Failed to delete message(s): Invalid message filter was provided",
    "moderation_purge_success": "Deleted {} message(s)",
    "moderation_purge_usernotfound": "Failed to delete message(s): Target user not found",
    "moderation_report_disable_disabled": "Reporting is already disabled on this server. To enable it again, set a report channel.",
    "moderation_report_disable_success": "Reporting has been disabled. To enable it again, set a new report channel.",
    "moderation_report_embed_footer": "Reported by: {}",
    "moderation_report_embed_title": "Report",
    "moderation_report_not_enabled": "Reports are not enabled on this server.",
    "moderation_report_setchannel": "Report channel has been set to **#{}**",
    "moderation_slowmode_disabled": "Disabled slowmode",
    "moderation_slowmode_enabled": "Enabled slowmode and cooldown was set to `{}`",
    "moderation_slowmode_max": "The maximum slowmode period is `{} hour(s)`",
    "moderation_softban_embed_footer": "Softbanned by: {}",
    "moderation_softban_embed_title": "The following users were softbanned out of the server",
    "moderation_softban_embed_users": "Softbanned Users",
    "moderation_softban_empty": "{}, I could not softban the provided users. They might no longer be in this server or have higher role privileges than me.",
    "moderation_softban_not_found": "The user(s) you are trying to softban could not be found.",
    "moderation_unban_embed_footer": "Unbanned by: {}",
    "moderation_unban_embed_title": "The following users were unbanned from the server",
    "moderation_unban_embed_users": "Unbanned Users",
    "moderation_unban_empty": "{}, I could not unban the provided users. They might already be unbanned.",
    "moderation_unban_not_found": "The user(s) you are trying to unban could not be found.",
    "moderation_unmute_dm": "You have been unmuted from **{}**. You can now chat in that server again.",
    "moderation_unmute_embed_footer": "Unmuted by: {}",
    "moderation_unmute_embed_title": "The following users were unmuted from the server",
    "moderation_unmute_embed_users": "Unmuted Users",
    "moderation_unmute_empty": "{}, I could not unmute the provided users. They are most likely already unmuted.",
    "moderation_warn_dm_footer": "Server: {}",
    "moderation_warn_dm_title": "Your actions have resulted in a warning",
    "moderation_warn_dm_warnedby": "You have been warned by: **{}**",
    "moderation_warn_embed_description": "The following users have been warned successfully. If any of them reach the maximum warnings limit, they must be reset in order to issue new ones.",
    "moderation_warn_embed_footer": "Warned by: {}",
    "moderation_warn_embed_reached_limit": "Reached Warning Limit",
    "moderation_warn_embed_title": "Issued warnings",
    "moderation_warn_embed_users": "Warned Users",
    "moderation_warn_empty": "{}, I could not issue a warning to the provided users. It is likely that they have reached their maximum warnings limit. Reset their warnings before issuing new ones.",
    "moderation_warn_not_found": "The user(s) you are trying to issue a warning to could not be found.",
    "moderation_warnings_delete": "Successfully deleted warning with corresponding number '{}' for {}.",
    "moderation_warnings_delete_embed_footer": "Deleted by: {}",
    "moderation_warnings_embed_issuedby": "*Issued by: {}*",
    "moderation_warnings_embed_title": "List of warnings for {}",
    "moderation_warnings_empty": "{}, {} does not have any warnings.",
    "moderation_warnings_outofrange": "The warning you are trying to delete does not exist. Are you sure you have entered the correct value?",
    "moderation_warnings_reset_embed_description": "All server-wide warnings have been reset for the following users:",
    "moderation_warnings_reset_embed_footer": "Cleared by: {}",
    "moderation_warnings_reset_embed_title": "Warnings Reset",
    "moderation_warnings_reset_empty": "{}, I could not reset warnings for the provided users. They might no longer be in this server.",
    "modlog_channel_string": "Modlog Channel",
    "module_string": "Module",
    "month_string": "month",
    "months_string": "months",
    "needed_permissions": "Needed Permissions",
    "notes_string": "Note(s)",
    "now_string": "now",
    "other_settings_string": "Other Settings",
    "other_string": "other",
    "others_string": "others",
    "owner_string": "Owner",
    "page_string": "Page",
    "pager_outofrange": "The page you're trying to reach does not exist.",
    "prefix_string": "Prefix",
    "price_string": "Price",
    "profile_bio_char_limit": "Your biography paragraph exceeds the {} character limit.",
    "profile_bio_reset": "Successfully reset bio back to default.",
    "profile_bio_success": "Successfully changed bio",
    "profile_bio_title": "Bio",
    "profile_disabled_exp": "Disabled EXP",
    "profile_empty_bio": "Empty",
    "profile_level_up_message": "Congratulations {}, You've reached level **{}**!",
    "profile_rank": "Rank",
    "profiles_background_category_not_found": "Profile background category not found. Please check your spelling and try again",
    "profiles_background_category_title": "{} Backgrounds",
    "profiles_background_footer": "General information about this command's usage",
    "profiles_background_general_body": "Welcome to the general page of the profile background shop.\nThe following information aims to provide help to nagivate through backgrounds with ease.\n\n**Available categories:**\n- {}\n\n**Usage:**\n\u2022 Providing a specific number to this command will display a preview of its corresponding profile background. (**Example:** `{}bg 15`)\n\u2022 Providing a category to this command will display all available backgrounds within that category. (**Example:** `{}bg General`)",
    "profiles_background_general_title": "Profile backgrounds",
    "profiles_background_owned": "*OWNED*",
    "profiles_background_specific_not_found": "Profile background not found",
    "profiles_background_specific_title": "Background Information",
    "profiles_buy_confirmation": "Do you really want to purchase this profile background for {} {}? Please type **'yes' (y)** or **'no' (n)** to confirm your choice.",
    "profiles_buy_insufficient_funds": "You have insufficient funds to buy this background.\n**Missing funds**: {} {}",
    "profiles_buy_not_found": "The background you're trying to buy cannot be found.\nPlease check if you're typing the correct number.",
    "profiles_buy_owned": "You already own this background (#{}).",
    "profiles_buy_success": "You successfully purchased background #{} for {:,} {}",
    "profiles_equip_not_found": "Profile background not found",
    "profiles_equip_not_owned": "You do not own this profile background",
    "profiles_equip_success": "{}, Your profile background was sucessfully changed to *#{}*",
    "profiles_inventory_empty": "You don't own any profile backgrounds",
    "profiles_inventory_title": "{}'s Inventory",
    "profiles_leaderboard_description": "The current leveling leaderboard for **{}**.\nYou are currently rank **#{}** in this server.\n\n",
    "profiles_leaderboard_disabled": "No leaderboard. Leveling is disabled on this server",
    "profiles_leaderboard_empty": "The server leaderboard is empty",
    "profiles_leaderboard_title": "Server Leaderboard",
    "profiles_leveling_already_disabled": "Leveling is already disabled on this server",
    "profiles_leveling_already_enabled": "Leveling is already enabled on this server",
    "profiles_leveling_disabled": "Disabled leveling on this server",
    "profiles_leveling_enabled": "Enabled leveling on this server",
    "profiles_leveling_reset_confirmation": "Please type **'yes' (y)** or **'no' (n)** to confirm whether you want to reset experience progress on this server.",
    "profiles_leveling_reset_message": "Confirmed request. Experience progress has been reset for all users",
    "profiles_unequip_message": "{}, Your profile profile background has been reset back to default",
    "reason_string": "Reason",
    "second_string": "second",
    "seconds_string": "seconds",
    "server_string": "server",
    "servers_string": "servers",
    "settings_disabled_cmds_default": "No commands are disabled on this server",
    "settings_disabled_modules_default": "No modules are disabled on this server",
    "settings_goodbye_default": "Goodbye channel is not set",
    "settings_greetings_default": "Greetings channel is not set",
    "settings_info_description": "These are the current settings for **{}**. They can be changed at any given time using their corresponding commands, which can be found using the bot's help command.",
    "settings_info_header": "Settings for {}",
    "settings_info_other_settings": "Only the more important settings are displayed in order not to clutter this dashboard too much. If you want to check any other setting, you can always use their applicable command.",
    "settings_langs_footer": "Current bot language",
    "settings_langs_title": "Available language pack(s)",
    "settings_langset_notfound": "This language does not seem to exist in the system. Please make sure your spelling is correct.",
    "settings_langset_same": "The language you're trying to set the bot to is already being used.",
    "settings_langset_success": "Language was set to **{}**.",
    "settings_modlog_default": "Modlog channel is not set",
    "settings_prefix_info": "The bot's prefix on this server is ` {} `",
    "settings_prefix_length_limit": "The bot's prefix can have a maximum length of {} characters.",
    "settings_prefix_reset": "The bot's prefix has been set back to: ` {} `",
    "settings_prefix_success": "Changed bot server prefix to: ` {} `",
    "settings_reset_confirmation_description": "Resetting all settings will revert the bot's **prefix, language, disabled modules and commands, welcome and goodbye toggles and moderation log** back to default for this server.\n\nType `yes` or `no` to confirm your decision.",
    "settings_reset_confirmation_footer": "Please be careful as this action is irreversible",
    "settings_reset_confirmation_title": "Resetting Settings",
    "settings_reset_success_description": "All server-side settings have been successfully reverted back to their default configuration.",
    "settings_reset_success_title": "Successfully reset all settings",
    "shard_string": "shard",
    "shards_string": "shards",
    "timeago": "{} ago",
    "uptime_string": "Uptime",
    "usage_string": "Usage",
    "user_string": "User",
    "users_string": "Users",
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
    "utility_binfo_author_footer": "Bot developed by DivideByNone#9640",
    "utility_binfo_bname": "Bot Name",
    "utility_binfo_latency": "Shard latency",
    "utility_binfo_title": "Bot Information",
    "utility_binfo_version": "Version",
    "utility_choose_msg": "{} I randomly picked: **{}**",
    "utility_massnick_embed_desc": "The following users have been given the nickname: **{}**.",
    "utility_massnick_embed_footer": "Named by: {}",
    "utility_massnick_embed_title": "Changed Nickname",
    "utility_massnick_empty": "{}, I ran into issues when trying to change the names of the provided users. Make sure I have enough permissions to perform this action.",
    "utility_massnick_not_found": "{}, I could not find the users you provided for a nickname change.",
    "utility_massnick_reset_embed_desc": "The following users' nicknames have been reset.",
    "utility_massnick_reset_embed_footer": "Reset by: {}",
    "utility_massnick_reset_embed_title": "Nickname Reset",
    "utility_roll_msg": "You rolled **{}**.",
    "utility_uinfo_activity": "Activity",
    "utility_uinfo_created": "Account Created",
    "utility_uinfo_id": "ID",
    "utility_uinfo_joined": "Joined Server",
    "utility_uinfo_nickname": "Nickname",
    "utility_uinfo_sroles": "Server Roles ({})",
    "utility_uptime_msg": "The bot has been running for {}.",
    "version_brief_string": "ver.",
    "version_string": "Version",
    "voting_user_vote_embed_description": "Thank you for supporting this bot on **{}**!\nAs a reward, you were given **{}** {} **(Combo: {})**\n\n*Your combo resets if you don't vote within 48 hours of your last vote*",
    "voting_user_vote_embed_title": "Thank you for voting!",
    "voting_vote_embed_description": "Voting is one of the ways you can directly support me and my creator. We are grateful to every single one of you doing so.\n\n1) **Discordbotlist.com:** [Click here](https://discordbotlist.com/bots/qubot/upvote) (12 hour cooldown)\n\n**Voting will reward the following:**\n\u2022 **Discordbotlist.com** - {} {}",
    "voting_vote_embed_title": "Voting",
    "wait_for_cancelled": "The confirmation was cancelled by the user.",
    "wait_for_timeout": "Failed to respond to the command within the given time limit.",
    "warning_string": "Warning",
    "week_string": "week",
    "weeks_string": "weeks",
    "year_string": "year",
    "years_string": "years"
}


with open(os.path.join(bot_path, f'data/localization/language_{languagecode}.json'), 'w') as json_file:
    json_file.write(json.dumps(json_lang_en, indent=4, sort_keys=True, separators=(',', ': ')))
json_file.close()  # Used only temporarily to update localization JSON file

with open(os.path.join(bot_path, f'data/localization/language_{languagecode}.json'), 'r', encoding="utf_8") as json_file:
    lang = json.load(json_file)
json_file.close()

with open(os.path.join(bot_path, 'data/data.json'), 'r') as json_file:
    json_data = json.load(json_file)
json_file.close()

version = json_data["appVersion"]

# ----------------------------------- #
# Localization


def get_lang(guild_id: int):
    localization = localizations.Localizations()
    language = localization.get_language(guild_id, languagecode)
    with open(os.path.join(bot_path, f'data/localization/language_{language}.json'), 'r', encoding="utf_8") as json_file:
        return_dict = json.load(json_file)
    json_file.close()
    return return_dict

# ----------------------------------- #
# Creating modules.mdls to store loaded modules


if not os.path.isfile(os.path.join(bot_path, 'data', 'modules.mdls')):
    with open(os.path.join(bot_path, 'data', 'modules.mdls'), 'w') as modules_file:
        print("[modules.mdls] file not found. Creating a new file")
        # The core module is added upon file creation
        modules_file.write("Core\n")
        modules_file.close()

with open(os.path.join(bot_path, 'data/modules.mdls'), 'r') as modules_file:
    modules_list = modules_file.read().split()
    modules_file.close()

module_directory_list = [os.path.splitext(i)[0] for i in os.listdir(os.path.join(bot_path, 'modules'))]
modules = [x for x in modules_list if x in module_directory_list]
modules = [f'modules.{x}' for x in modules]

# ----------------------------------- #
# Deleting old logs. All logs older than a week will be deleted by default


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

# ----------------------------------- #
# Bot Server Prefixes


def get_prefix(bot, message):
    prefixes = prefixhandler.PrefixHandler()
    return_prefix = prefixes.get_prefix(message.guild.id, prefix) if message.guild else prefix
    return commands.when_mentioned_or(return_prefix)(bot, message)

# ----------------------------------- #
# Bot initialization


intents = discord.Intents.default()
intents.guilds = True
intents.members = True
bot = commands.AutoShardedBot(command_prefix=get_prefix, intents=intents)
bot_starttime = datetime.today().replace(microsecond=0)

# ----------------------------------- #
# Bot startup events


@bot.event
async def on_shard_ready(shard_id):
    print(f'Shard {shard_id} ready.')


@bot.event
async def on_ready():
    print("The bot has sucessfully established a connection with Discord API. Booting up...")
    server_count = 0
    for _ in bot.guilds:
        server_count += 1
    print("Bot is currently in {} servers".format(server_count))

# ----------------------------------- #


if __name__ == "__main__":

    old_logs_delete(int(log_days_delete))

    # Checking if the application is running in a virtual environment
    if is_venv():
        print('This bot is currently running inside a virtual environment.')

    # Loading bot modules
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

    # Run
    print("Bot starting up in directory {}".format(bot_path))
    bot.run(tokenid)
