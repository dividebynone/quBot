Commands List
===========================

Table of contents
-----------------
* `Administration`_
* `Conquest`_
* `Core`_
* `Economy`_
* `Help`_
* `Localization`_
* `Utility`_


Administration
^^^^^^^^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``purge``", "| Deletes a set number of messages.\
   | Note: *This command requires a single argument - The number of messages you wish the bot to delete.*", "``!purge 10``"
   "``kick``", "| Kicks the mentioned individual for a certain reason. (if any)\
   | Note: *The kick command accepts two arguments: one required (The target user) and one optional (The reason for kicking the user)*", "``!kick``, ``!kick @somebody Spamming``"
   "``ban``", "| Bans the mentioned individual for a certain reason. (if any)\
   | Note: *The ban command accepts three arguments: one required (The target user) and two optional (The days worth of messages that will be deleted by the bot; The reason for banning the user).*", "``!ban @somebody``, ``!ban @somebody 4 Harassment``"

Conquest
^^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``screate`` ``sc``", "| Creates a settlement.\
   | Note: *This command requires three arguments - settlement name (should be in quotes), settlement type (either 'public' or 'private') and entry fee (minimum 100)*", "``!sc 'My Settlement Name' private 100``"
   "``sinfo`` ``si`` ``settlement``", "| Displays a settlement's public information.\
   | Note: *This command has one optional argument - the target individual. If no argument is parsed then the command will display the settlement you currectly reside in.*", "``!sinfo``, ``!sinfo @somebody``"
   "``join public``", "| Joins another individual's settlement.\
   | Note: *This command requires two arguments - the target individual and entry fee (minimum the settlement's entry fee).*", "``!join public @somebody 100``"
   "``join private``", "| Joins another individual's settlement.\
   | Note: *This command requires two arguments - the settlement's invite code and entry fee (minimum the settlement's entry fee).*", "``!join private <code> 100``"
   "``code`` ``code show``", "| Displays your settlement's invide code. The code is sent privately to the author.\
   | Note: *This command can also be used directly in the bot's direct messages.*", "``!code``, ``!code show``"
   "``code new``", "| Generates a new invite code for your settlement.\
   | Note: *This command can also be used directly in the bot's direct messages.*", "``!code new``"
   "``attack``", "| Attacks the target individual's settlement.\
   | Note: *Use it wisely!*", "``!attack @somebody``"
   "``leaderboard`` ``lb``", "| Returns the settlements' leaderboard.\
   | Note: *This command takes one optional argument - the page number. If no argument is passed, then it defaults to 1.*", "``!lb``, ``!lb 2``"
   "``sleave``", "| Leave the settlement you are currently in. (if any)\
   | Note:\
   | - Leaders of settlements with multiple residents cannot leave settlement without transferring ownership.\
   | - Settlements with only one resident will get **DESTROYED** in the process!", "``!sleave``"
   "``promote``", "| Promotes the target individual to settlement leader.\
   | Note: This command can **ONLY** be used by settlement leaders.", "``!promote @somebody``"
   "``skick``", "| Kicks the target individual from the settlement.\
   | Note: This command can **ONLY** be used by settlement leaders.", "``!skick @somebody``"

Core
^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``load``", "| Loads new modules into the bot application.\
   | Note: *The module file needs to be present in the modules folder of the bot.* This command can only be used by the **BOT OWNER**.", "``!load <module name>``"
   "``unload``", "| Unloads modules from the bot application.\
   | Note: *The module file needs to be present in the modules folder of the bot.* This command can only be used by the **BOT OWNER**.", "``!unload <module name>``"
   "``reload``", "| Reloads modules loaded into the bot application.\
   | Note: *The module file needs to be present in the modules folder of the bot.* This command can only be used by the **BOT OWNER**.", "``!reload <module name>``"
   "``modules hide``", "| Hides a module from the list of loaded modules.\
   | Note: *This is a subcommand of the 'modules' command.* This command can only be used by the **BOT OWNER**.", "``!modules hide <module name>``"
   "``modules unhide``", "| Reveals a hidden module from the list of loaded modules.\
   | Note: *This is a subcommand of the 'modules' command.* This command can only be used by the **BOT OWNER**.", "``!modules unhide <module name>``"
   "``userid`` ``uid``", "| Returns the target individual's Discord ID.\
   | Note: *If no argument is given, the bot will use the author of the message.* This command can only be used by the **BOT OWNER**.", "``!uid``, ``!uid @somebody``"
   "``serverid`` ``sid``", "| Returns the server's ID for the server the command was typed in.\
   | Note: This command can only be used by the **BOT OWNER**.", "``!sid``"
   "``channelid`` ``cid``", "| Returns the channel's ID for the channel the command was typed in.\
   | Note: This command can only be used by the **BOT OWNER**.", "``!cid``"
   "``leave``", "| Politely kicks the bot off your server.\
   | **Needed User Permissions: Kick Members**", "``!leave``"
   "``latencies``", "| Returns the latencies (in miliseconds) for every active shard.\
   | Note: This command can only be used by the **BOT OWNER**.", "``!latencies``"
   "``setname``", "| Changes the name of the bot.\
   | Note: This command can only be used by the **BOT OWNER**.", "``!setname quBot``"
   "``setstatus``", "| Changes the bot's status. (Online by default)\
   | Note: *This command requires one argument and it needs to be one of the following: 'online', 'offline', 'idle', 'dnd', 'invisible'.* This command can only be used by the **BOT OWNER**.", "``!setstatus dnd``"
   "``setactivity``", "| Changes the bot's activity.\
   | Note: *This command requires two arguments: the type of activity(playing, streaming, listening, watching) and the message itself.* This command can only be used by the **BOT OWNER**.", "``!setactivity playing with fire``"
   "``restart``", "| Restarts the bot.\
   | Note: This command can only be used by the **BOT OWNER**.", "``!restart``"
   "``shutdown``", "| Shutdowns the bot.\
   | Note: This command can only be used by the **BOT OWNER**.", "``!shutdown``"

Economy
^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``daily``", "| Lets you claim a set sum of money on a daily basis.\
   | Note: *If you wish to gift your daily reward instead of claiming it for yourself, you can mention the individual when using the command.*", "``!daily``, ``!daily @somebody``"
   "``currency`` ``money`` ``cash`` ``$``", "| Displays the sum of money the target individual has on their profile.\
   | Note: *If no argument is parsed, the bot will display your profile's money*", "``!cash`` ``!cash @somebody``"
   "``adjust``", "| Awards/Subtracts a set amount of money to/from the target individual.\
   | Note: This command can only be used by the **BOT OWNER**.", "``!adjust @somebody 100``, ``!adjust @somebody -50``"
   "``give``", "Transfers a set amount of money to another user.", "``!give @somebody 100``"
   "``betroll`` ``broll`` ``br``", "Lets you bet a certain amount of money on a roll.", "``!broll 100``"

Help
^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``help`` ``h``", "| Help command that returns a help message based on user input.\
   | Note: *The command takes command name as optional argument. Otherwise, it returns a general help message.*", "``!help``, ``!help roll``"
   "``modules`` ``mdls``", "Displays all loaded modules.", "``!modules``"
   "``commands`` ``cmds``", "Displays all commands in a given module", "``!cmds Utility``, ``!cmds Economy``"

Localization
^^^^^^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``languages`` ``langs``", "| Returns a list of locally detected language (localization) packages.\
   | Note: This command can only be used by the **BOT OWNER**.", "``!langs``"
   "``langset``", "| Changes the language of the bot.\
   | Note: This command can only be used by the **BOT OWNER**.", "``!langset en-US``"

Utility
^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``avatar``", "| Returns the target individual's avatar. \
   | Note: *If no argument is parsed, the bot will instead return your avatar.*", "``!avatar``, ``!avatar @somebody``"
   "``roll`` ``r``", "| Rolls a number in a given range. \
   | Note: *If no argument is parsed, the bot will roll a number between 1 and 100.*", "``!roll``, ``!roll 9000``"
   "``uptime``", "| Returns the bot's uptime. \
   | **Needed User Permissions: Administrator**", "``!uptime``"
   "``userinfo`` ``uinfo``", "| Shows the target individual's user information. \
   | Note: *If no argument is parsed, the bot will return your information instead.*", "``!uinfo``, ``!uinfo @somebody``"
