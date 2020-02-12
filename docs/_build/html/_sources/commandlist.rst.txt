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
   | Note:\
   | - *This command requires a single argument - The number of messages you wish the bot to delete.*\
   | - **Needed User Permissions: Manage Messages**", "``q!purge 10``"
   "``kick``", "| Kicks the mentioned individual for a certain reason. (if any)\
   | Note:\
   | - *The kick command accepts two arguments: one required (The target user) and one optional (The reason for kicking the user)*\
   | - **Needed User Permissions: Kick Members**", "``q!kick``, ``q!kick @somebody Spamming``"
   "``ban``", "| Bans the mentioned individual for a certain reason. (if any)\
   | Note:\
   | - *The ban command accepts three arguments: one required (The target user) and two optional (The days worth of messages that will be deleted by the bot; The reason for banning the user).*\
   | - **Needed User Permissions: Ban Members**", "``q!ban @somebody``, ``q!ban @somebody 4 Harassment``"

Conquest
^^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``screate`` ``sc``", "| Creates a settlement.\
   | Note: *This command requires three arguments - settlement name (should be in quotes), settlement type (either 'public' or 'private') and entry fee (minimum 100)*", "``q!sc 'My Settlement Name' private 100``"
   "``sinfo`` ``si`` ``settlement``", "| Displays a settlement's public information.\
   | Note: *This command has one optional argument - the target individual. If no argument is parsed then the command will display the settlement you currectly reside in.*", "``q!sinfo``, ``q!sinfo @somebody``"
   "``join public``", "| Joins another individual's settlement.\
   | Note: *This command requires two arguments - the target individual and entry fee (minimum the settlement's entry fee).*", "``q!join public @somebody 100``"
   "``join private``", "| Joins another individual's settlement.\
   | Note: *This command requires two arguments - the settlement's invite code and entry fee (minimum the settlement's entry fee).*", "``q!join private <code> 100``"
   "``code`` ``code show``", "| Displays your settlement's invide code. The code is sent privately to the author.\
   | Note: *This command can also be used directly in the bot's direct messages.*", "``q!code``, ``q!code show``"
   "``code new``", "| Generates a new invite code for your settlement.\
   | Note: *This command can also be used directly in the bot's direct messages.*", "``q!code new``"
   "``attack``", "| Attacks the target individual's settlement.\
   | Note: *Use it wisely!*", "``q!attack @somebody``"
   "``leaderboard`` ``lb``", "| Returns the settlements' leaderboard.\
   | Note: *This command takes one optional argument - the page number. If no argument is passed, then it defaults to 1.*", "``q!lb``, ``q!lb 2``"
   "``sleave``", "| Leave the settlement you are currently in. (if any)\
   | Note:\
   | - Leaders of settlements with multiple residents cannot leave settlement without transferring ownership.\
   | - Settlements with only one resident will get **DESTROYED** in the process!", "``q!sleave``"
   "``promote``", "| Promotes the target individual to settlement leader.\
   | Note: This command can **ONLY** be used by settlement leaders.", "``q!promote @somebody``"
   "``skick``", "| Kicks the target individual from the settlement.\
   | Note: This command can **ONLY** be used by settlement leaders.", "``q!skick @somebody``"
   "``resources``", "Displays the amount of resources currently stored in your settlement.", "``q!resources``"
   "``buildings`` ``buildings list``", "Displays the buildings' status of the settlement you are part of. (if any)", "``q!buildings``, ``q!buildings list``"
   "``buildings upgrade``", "| Upgrades the target settlement building to the next level.\
   | Note: This command can **ONLY** be used by settlement leaders.", "``q!buildings upgrade 1``"
   "``requirements`` ``reqs``", "Displays target settlement building upgrade requirements for every level from 1 to 10.", "``q!requirements 1``, ``q!reqs 3``"
   "``market``", "| A command group. If no subcommands are invoked by the user, this command will display the resource market.\
   | Note: This command can also be used directly in the bot's direct messages.", "``q!market``"
   "``market buy``", "| Buys a set amount of resources from the market.\
   | Note: This command can **ONLY** be used by settlement leaders.", "``q!market buy wood 10``, ``q!market buy 1 10``"
   "``market sell``", "| Sells a set amount of resources on the market.\
   | Note: This command can **ONLY** be used by settlement leaders.", "``q!market sell wood 10``, ``q!market sell 1 10``"
   "``deposit``", "| Deposits a sum of money into the treasury of the settlement you are currently part of.\
   | Note: You need to be part of a settlement to be able to use this command.", "``q!deposit 100``"

Core
^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``load``", "| Loads new modules into the bot application.\
   | Note: *The module file needs to be present in the modules folder of the bot.* This command can only be used by the **BOT OWNER**.", "``q!load <module name>``"
   "``unload``", "| Unloads modules from the bot application.\
   | Note: *The module file needs to be present in the modules folder of the bot.* This command can only be used by the **BOT OWNER**.", "``q!unload <module name>``"
   "``reload``", "| Reloads modules loaded into the bot application.\
   | Note: *The module file needs to be present in the modules folder of the bot.* This command can only be used by the **BOT OWNER**.", "``q!reload <module name>``"
   "``modules hide``", "| Hides a module from the list of loaded modules.\
   | Note: *This is a subcommand of the 'modules' command.* This command can only be used by the **BOT OWNER**.", "``q!modules hide <module name>``"
   "``modules unhide``", "| Reveals a hidden module from the list of loaded modules.\
   | Note: *This is a subcommand of the 'modules' command.* This command can only be used by the **BOT OWNER**.", "``q!modules unhide <module name>``"
   "``userid`` ``uid``", "| Returns the target individual's Discord ID.\
   | Note: *If no argument is given, the bot will use the author of the message.* This command can only be used by the **BOT OWNER**.", "``q!uid``, ``q!uid @somebody``"
   "``serverid`` ``sid``", "| Returns the server's ID for the server the command was typed in.\
   | Note: This command can only be used by the **BOT OWNER**.", "``q!sid``"
   "``channelid`` ``cid``", "| Returns the channel's ID for the channel the command was typed in.\
   | Note: This command can only be used by the **BOT OWNER**.", "``q!cid``"
   "``leave``", "| Politely kicks the bot off your server.\
   | **Needed User Permissions: Kick Members**", "``q!leave``"
   "``latencies``", "| Returns the latencies (in miliseconds) for every active shard.\
   | Note: This command can only be used by the **BOT OWNER**.", "``q!latencies``"
   "``setname``", "| Changes the name of the bot.\
   | Note: This command can only be used by the **BOT OWNER**.", "``q!setname quBot``"
   "``setstatus``", "| Changes the bot's status. (Online by default)\
   | Note: *This command requires one argument and it needs to be one of the following: 'online', 'offline', 'idle', 'dnd', 'invisible'.* This command can only be used by the **BOT OWNER**.", "``q!setstatus dnd``"
   "``setactivity``", "| Changes the bot's activity.\
   | Note: *This command requires two arguments: the type of activity(playing, streaming, listening, watching) and the message itself.* This command can only be used by the **BOT OWNER**.", "``q!setactivity playing with fire``"
   "``restart``", "| Restarts the bot.\
   | Note: This command can only be used by the **BOT OWNER**.", "``q!restart``"
   "``shutdown``", "| Shutdowns the bot.\
   | Note: This command can only be used by the **BOT OWNER**.", "``q!shutdown``"

Economy
^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``daily``", "| Lets you claim a set sum of money on a daily basis.\
   | Note: *If you wish to gift your daily reward instead of claiming it for yourself, you can mention the individual when using the command.*", "``q!daily``, ``q!daily @somebody``"
   "``currency`` ``money`` ``cash`` ``$``", "| Displays the sum of money the target individual has on their profile.\
   | Note: *If no argument is parsed, the bot will display your profile's money*", "``q!cash`` ``q!cash @somebody``"
   "``adjust``", "| Awards/Subtracts a set amount of money to/from the target individual.\
   | Note: This command can only be used by the **BOT OWNER**.", "``q!adjust @somebody 100``, ``q!adjust @somebody -50``"
   "``give``", "Transfers a set amount of money to another user.", "``q!give @somebody 100``"
   "``betroll`` ``broll`` ``br``", "Lets you bet a certain amount of money on a roll.", "``q!broll 100``"
   "``vote``", "Gives you more information on bot voting.", "``q!vote``"

Help
^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``help`` ``h``", "| Help command that returns a help message based on user input.\
   | Note: *The command takes command name as optional argument. Otherwise, it returns a general help message.*", "``q!help``, ``q!help roll``"
   "``modules`` ``mdls``", "Displays all loaded modules.", "``q!modules``"
   "``commands`` ``cmds``", "Displays all commands in a given module", "``q!cmds Utility``, ``q!cmds Economy``"

Localization
^^^^^^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``languages`` ``langs``", "| Returns a list of locally detected language (localization) packages.\
   | Note: This command can only be used by the **BOT OWNER**.", "``q!langs``"
   "``langset``", "| Changes the language of the bot.\
   | Note: This command can only be used by the **BOT OWNER**.", "``q!langset en-US``"

Utility
^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``avatar``", "| Returns the target individual's avatar. \
   | Note: *If no argument is parsed, the bot will instead return your avatar.*", "``q!avatar``, ``q!avatar @somebody``"
   "``roll`` ``r``", "| Rolls a number in a given range. \
   | Note: *If no argument is parsed, the bot will roll a number between 1 and 100.*", "``q!roll``, ``q!roll 9000``"
   "``uptime``", "| Returns the bot's uptime. \
   | **Needed User Permissions: Administrator**", "``q!uptime``"
   "``userinfo`` ``uinfo``", "| Shows the target individual's user information. \
   | Note: *If no argument is parsed, the bot will return your information instead.*", "``q!uinfo``, ``q!uinfo @somebody``"
