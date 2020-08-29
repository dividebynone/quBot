Commands List
===========================

Table of contents
-----------------
* `Administration`_
* `Conquest`_
* `Core`_
* `Dictionaries`_
* `Economy`_
* `Help`_
* `Localization`_
* `Profiles`_
* `Utility`_


Administration
^^^^^^^^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``purge``", "| Deletes a set number of messages.\
   | **Note(s):**\
   | - *This command requires a single argument - The number of messages you wish the bot to delete.* \
   | - Available filters: bot *(Filters are specified after the number of messages)*
   | **Needed User Permissions: Manage Messages**", "``q!purge 10``, ``q!purge 10 bot``"
   "``kick``", "| Kicks the mentioned individual for a certain reason (if any)\
   | **Note(s):**\
   | - *The kick reason is an optional argument.*\
   | **Needed User Permissions: Kick Members**", "``q!kick``, ``q!kick @somebody Spamming``"
   "``ban``", "| Bans the mentioned individual for a certain reason (if any)\
   | **Note(s):**\
   | - *The ban reason is an optional argument.*\
   | **Needed User Permissions: Ban Members**", "``q!ban @somebody``, ``q!ban @somebody Harassment``"
   "``tempban`` ``tban``", "| Temporarily bans the mentioned invidivual for a specified amount of time for a certain reason (if any).\
   | **Note(s):**\
   | - *The ban reason is an optional argument.*\
   | - *This command accepts the following time units: m(inutes), h(ours), d(ays), w(eeks)*\
   | **Needed User Permissions: Ban Members**", "``q!tempban @somebody 30 Harassment``, ``q!tempban @somebody 2d``, ``q!tempban @somebody '2 weeks 7 days' Harassment``"
   "``unban``", "| Unbans the target individual from the server.\
   | **Note(s):**\
   | - *Since the target individual can not be mentioned directly within the server, a <username>#<discriminator>(see example) or user ID must be provided.*\
   | **Needed User Permissions: Ban Members**", "``q!unban user#1234``, ``q!unban 116267141744820233``"
   "``softban``", "| Soft bans the mentioned individual for a specified reason (if any)\
   | **Note(s):**\
   | - *The soft ban reason is an optional argument.*\
   | - *Soft bans in essence kick the target individual from the server while deleting their messages. It's not the same as a normal ban.*\
   | **Needed User Permissions: Kick Members, Manage Messages**", "``q!softban @somebody``, ``q!softban @somebody Spamming``"
   "``mute``", "| Mutes the target individual from chatting on the server.\
   | **Needed User Permissions: Manage Messages**", "``q!mute @somebody``"
   "``tempmute`` ``tmute``", "| Temporarily mutes the target individual from chatting on the server.\
   | **Note(s):**\
   | - *This command accepts the following time units: m(inutes), h(ours), d(ays), w(eeks)*\
   | **Needed User Permissions: Manage Messages**", "``q!tempmute @somebody 30``, ``q!tempmute @somebody 2d``, ``q!tempmute @somebody 2d6h``"
   "``unmute``", "| Unmutes the target individual if they were previously muted using the bot.\
   | **Needed User Permissions: Manage Messages**", "``q!unmute @somebody``"
   "``slowmode`` ``sm``", "| Sets a chatting cooldown for the channel where the command was used.\
   | **Needed User Permissions: Manage Messages, Manage Channels**", "``q!slowmode 30``, ``q!sm 5m30s``"
   "``slowmode disable`` ``slowmode off``", "| Disables slowmode for the channel where the command was used.\
   | **Needed User Permissions: Manage Messages, Manage Channels**", "``q!slowmode disable``, ``q!slowmode off``, ``q!slowmode 0``"
   "``report``", "| Reports the target user for a particular reason.\
   | **Note(s):**\
   | - *A report reason must be provided in order to use this command.*\
   | - *This command will only work when a report channel is set. (Disabled by default)*\
   | **Needed User Permissions: Send Messages**", "``q!report @somebody Spamming``"
   "``report setchannel``", "| Selects a text channel where future user reports are going to be sent.\
   | **Note(s):**\
   | - *Using this command will enable user reports if they were previously disabled. (Disabled by default)*\
   | **Needed User Permissions: Administrator**", "``q!report setchannel #general``"
   "``report disable``", "| Disables user reporting for the server where the command was used.\
   | **Note(s):**\
   | - *To enable user reporting again, you need to set a new report text channel.*\
   | **Needed User Permissions: Administrator**", "``q!report disable``"
   "``warn``", "| Warns the target user for a particular reason. This individual will receive a direct message from the bot.\
   | **Note(s):**\
   | - *A reason for the warning must be provided in order to use this command.*\
   | **Needed User Permissions: Kick Members, Ban Members**", "``q!warn @someone Spamming``"
   "``warnings``", "| Displays a list of warnings for the target individual.\
   | **Note(s):**\
   | - *A total of five warnings are displayed per page. You can navigate through pages by providing a page number after the username.*\
   | **Needed User Permissions: Kick Members, Ban Members**", "``q!warnings @someone``, ``q!warnings @someone 2``"
   "``warnings reset`` ``warnings clear``", "| Resets all warnings for the target individual.\
   | **Needed User Permissions: Kick Members, Ban Members**", "``q!warnings reset @someone``, ``q!warnings clear @someone``"
   "``warnings delete`` ``warnings remove``", "| Deletes a specific warning that was issued to the target individual.\
   | **Note(s):**\
   | - *While deleting warnings WILL NOT trigger any automatic actions, adding a new warning WILL.*\
   | **Needed User Permissions: Kick Members, Ban Members**", "``q!warnings delete @someone 3``, ``q!warnings remove @someone 3``"
   "``warnings auto``", "| Changes the number of warnings needed for a user to trigger an automatic mute/kick/ban from the server. (Disabled by default)\
   | **Note(s):**\
   | - *Using this command will enable the above-mentioned automatic actions if previously disabled.*\
   | - *If any of the number of warnings match for mute, kick or ban, the following will take priority from highest to lowest: ban, kick, mute.*\
   | **Needed User Permissions: Kick Members, Ban Members**", "``q!warnings auto mute 5``, ``q!warnings auto kick 8``, ``q!warnings auto kick 10``"
   "``warnings auto disable``", "| Disables the target automatic action from triggering for future user warnings.\
   | **Needed User Permissions: Kick Members, Ban Members**", "``q!warnings auto disable mute``, ``q!warnings auto disable kick``, ``q!warnings auto disable ban``"
   "``blacklist``", "| Blacklists the target user. As a result, they will no longer be able to use the bot in that server. If the target user is already blacklisted, they will get removed from the blacklist and regain access to bot commands.\
   | **Needed User Permissions: Administrator**", "``q!blacklist @someone``"
   "``blacklist add`` ``blacklist a``", "| Blacklists the target user. As a result, they will no longer be able to use the bot in that server.\
   | **Needed User Permissions: Administrator**", "``q!blacklist add @someone``, ``q!blacklist a @someone``"
   "``blacklist remove`` ``blacklist r``", "| Removes the target user from the bot blacklist. As a result, they will regain access to the bot's commands in that server.\
   | **Needed User Permissions: Administrator**", "``q!blacklist remove @someone``, ``q!blacklist r @someone``"
   "``greet`` ``greetings``", "| Toggles server greeting messages on/off on the server.\
   | **Needed User Permissions: Manage Server**", "``q!greet``, ``q!greetings``"
   "``bye`` ``goodbye``", "| Toggles server goodbye messages on/off on the server.\
   | **Needed User Permissions: Manage Server**", "``q!bye``, ``q!goodbye``"
   "``greet enable`` ``greet on``", "| Enables server greeting messages on the server.\
   | **Needed User Permissions: Manage Server**", "``q!greet enable``, ``q!greet on``"
   "``bye enable`` ``bye on``", "| Enables server goodbye messages on the server.\
   | **Needed User Permissions: Manage Server**", "``q!bye enable``, ``q!bye on``"
   "``greet disable`` ``greet off``", "| Disables server greeting messages on the server.\
   | **Needed User Permissions: Manage Server**", "``q!greet disable``, ``q!greet off``"
   "``bye disable`` ``bye off``", "| Disables server goodbye messages on the server.\
   | **Needed User Permissions: Manage Server**", "``q!bye disable``, ``q!bye off``"
   "``greet test``", "| Command to test your custom server greetings message.\
   | **Needed User Permissions: Manage Server**", "``q!greet test``"
   "``bye test``", "| Command to test your custom server goodbye message.\
   | **Needed User Permissions: Manage Server**", "``q!bye test``"
   "``greet dm``", "| Enables server greetings on the server. Instead of the server's text channel, future messages will instead be sent to users' direct messages.\
   | **Needed User Permissions: Manage Server**", "``q!greet dm``"
   "``greet message`` ``bye message``", "| Changes the greeting or goodbye message to a custom one. Feel free to check the notes to be able to fully utilize this command.\
   | **Note(s):**\
   | - *This command supports Discord Markdown. (Chat formatting: bold, italics, underline, etc.)*\
   | - *You can include the following in your message: {mention} - Mentions the User; {user} - Shows Username; {server} - Shows server name; {membercount} - Shows number of people in server;*\
   | **Needed User Permissions: Manage Server**", "``q!greet message Welcome {mention}!``, ``q!bye message Goodbye, {mention}!``"
   "``greet message default``", "| Resets the server greeting message back to default.\
   | **Needed User Permissions: Manage Server**", "``q!greet message default``"
   "``bye message default``", "| Resets the server goodbye message back to default.\
   | **Needed User Permissions: Manage Server**", "``q!bye message default``"
   "``greet setchannel`` ``bye setchannel``", "| Sets the text channel where greetings and goodbye messages are going to be sent by the bot.\
   | **Note(s):**\
   | - *Greeting and goodbye messages share the same channel.*\
   | - *By default, these messages are sent to #general. If no text channel exists with that name, it uses the first text channel on the list.*\
   | **Needed User Permissions: Manage Server**", "``q!greet setchannel #general``, ``q!bye setchannel #general``"
   "``greet setchannel default`` ``bye setchannel default``", "| Resets the greetings/goodbye messages text channel back to default.\
   | **Note(s):**\
   | - *Greeting and goodbye messages share the same channel.*\
   | - *By default, these messages are sent to #general. If no text channel exists with that name, it uses the first text channel on the list.*\
   | **Needed User Permissions: Manage Server**", "``q!greet setchannel default``, ``q!bye setchannel default``"

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
   "``rename``", "| Renames your settlement to the given name.\
   | **Note(s):**\
   | - *You must be the leader of this settlement to be able to use this command.*\
   | - *In order to rename your settlement, you need to pay a fee of 500 gold.*\
   | - *Settlement names have a character limit of 50 characters.*", "``q!rename My new settlement name``"

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
   "``modules enable``", "| Enables the target cog/module on the server where the command was executed.\
   | **Needed User Permissions: Administrator**", "``q!modules enable Utility``, ``q!modules e Utility``, ``q!mdls e Utility``"
   "``modules disable``", "| Disables the target cog/module on the server where the command was executed.\
   | **Needed User Permissions: Administrator**", "``q!modules disable Utility``, ``q!modules d Utility``, ``q!mdls d Utility``"
   "``modules hide``", "| Hides a module from the list of loaded modules.\
   | Note: *This is a subcommand of the 'modules' command.* This command can only be used by the **BOT OWNER**.", "``q!modules hide <module name>``"
   "``modules unhide``", "| Reveals a hidden module from the list of loaded modules.\
   | Note: *This is a subcommand of the 'modules' command.* This command can only be used by the **BOT OWNER**.", "``q!modules unhide <module name>``"
   "``commands enable``", "| Enables a command for the server where the command was executed in.\
   | **Needed User Permissions: Administrator**", "``q!commands enable userid``, ``q!commands e userid``, ``q!cmds e userid``"
   "``commands disable``", "| Disables a command for the server where the command was executed in.\
   | **Needed User Permissions: Administrator**", "``q!commands disable userid``, ``q!commands d userid``, ``q!cmds d userid``"
   "``userid`` ``uid``", "| Returns the target individual's Discord ID.\
   | Note: *If no argument is given, the bot will use the author of the message.*", "``q!uid``, ``q!uid @somebody``"
   "``serverid`` ``sid``", "| Returns the server's ID for the server the command was typed in.", "``q!sid``"
   "``channelid`` ``cid``", "| Returns the channel's ID for the channel the command was typed in.", "``q!cid``"
   "``roleid`` ``rid``", "| Returns the target role's ID for the server the command was typed in.", "``q!roleid Moderator``, ``q!rid Moderator``"
   "``remove``", "| Politely kicks the bot off your server.\
   | **Needed User Permissions: Kick Members**", "``q!remove``"
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
   "``prefix``", "| Shows or changes the bot's prefix on the server.\
   | **Needed User Permissions: Administrator**", "``q!prefix``, ``q!prefix m!``"
   "``prefix show``", "| Shows the bot's prefix on the server.", "``q!prefix show``"
   "``prefix reset``", "| Resets the bot's prefix on the server back to default.\
   | **Needed User Permissions: Administrator**", "``q!prefix reset``"

Dictionaries
^^^^^^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``dict`` ``whatis`` ``meaning`` ``meanings``", "| Returns a list of definitions based on the term you parse to the bot.\
   | **Note(s):**\
   | - *This command only supports English words & phrases* \
   | - *This command can only be used in NSFW text channels*", "``q!dict life``, ``q!whatis life``, ``q!meaning life``, ``q!meanings life``"
   "``synonym`` ``synonyms``", "| Returns a list of the top synonyms from Thesaurus based on the term you parse to the bot.\
   | **Note(s):**\
   | - *This command only supports English words & phrases* \
   | - *This command can only be used in NSFW text channels*", "``q!synonym hot``, ``q!synonyms hot``"
   "``antonym`` ``antonyms``", "| Returns a list of the top antonyms from Thesaurus based on the term you parse to the bot.\
   | **Note(s):**\
   | - *This command only supports English words & phrases* \
   | - *This command can only be used in NSFW text channels*", "``q!antonym hot``, ``q!antonyms hot``"
   "``urbandict`` ``ud``", "| Returns the top urban dictionary definition based on the term you parse to the bot.\
   | **Note(s):**\
   | - *This command only supports English words & phrases* \
   | - *This command can only be used in NSFW text channels*", "``q!urbandict hello``, ``q!ud hello``"

Economy
^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``daily``", "| Lets you claim a set sum of money on a daily basis.\
   | Note: *If you wish to gift your daily reward instead of claiming it for yourself, you can mention the individual when using the command.*", "``q!daily``, ``q!daily @somebody``"
   "``currency`` ``money`` ``cash`` ``$`` ``balance``", "| Displays the sum of money the target individual has on their profile.\
   | Note: *If no argument is parsed, the bot will display your profile's money*", "``q!cash`` ``q!cash @somebody``"
   "``adjust``", "| Awards/Subtracts a set amount of money to/from the target individual.\
   | Note: This command can only be used by the **BOT OWNER**.", "``q!adjust @somebody 100``, ``q!adjust @somebody -50``"
   "``give``", "Transfers a set amount of money to another user.", "``q!give @somebody 100``"
   "``betroll`` ``broll`` ``br``", "Lets you bet a certain amount of money on a roll.", "``q!broll 100``"
   "``vote``", "Gives you more information on bot voting.", "``q!vote``"
   "``giveaway start``", "| Starts a currency giveaway. Users can claim their reward by reacting to the bot message.\
   | **Note(s):**\
   | - This command can only be used by the **BOT OWNER**.", "``q!giveaway start 100``"
   "``giveaway end``", "| Ends a giveaway by a provided bot message ID\
   | **Note(s):**\
   | - This command can only be used by the **BOT OWNER**.", "``q!giveaway end <message_id>``"

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

   "``languages`` ``langs``", "| Returns a list of locally detected language (localization) packages.", "``q!langs``"
   "``langset``", "| Changes the language of the bot.\
   | **Needed User Permissions: Administrator**", "``q!langset en-US``"
   "``translate``", "| Shows general information about the translation of the bot.", "``q!translate``"

Profiles
^^^^^^^^

.. csv-table::
   :header: "Commands & Aliases", "Description", "Usage"
   :widths: 20, 60, 30

   "``profile`` ``p`` ``me`` ``level``", "| Displays the profile of the target user. \
   | Note: If you do not specify a user, the bot will display your profile.*", "``q!profile``, ``q!profile @somebody``"
   "``bio``", "| Sets (or resets) your profile's biography paragraph to the provided text. \
   | Note: *If you wish to reset your biography paragraph, provide no text to the command.*", "``q!bio``, ``q!bio Some text about me``"
   "``background`` ``bg`` ``backgrounds`` ``bgs``", "| Provides further information about all available profile backgrounds.\
   | **Note(s):**\
   | - *Providing a number will display a preview of the profile background.* \
   | - *Providing a category will display all available backgrounds within that category.*", "``q!bg 1``, ``q!bg All``, ``q!bg General``"
   "``background buy`` ``background purchase``", "| Purchases a profile background from the shop for its' corresponding price. \
   | Note: *All bought backgrounds are stored in your inventory and can be used cross-server. You only need to buy it once.*", "``q!bgs buy 1``, ``q!bgs purchase 1``"
   "``background inventory`` ``background inv``", "| Shows all profile backgrounds you currently own. \
   | Note: *Profile background purchases are global and can be used cross-server.*", "``q!bgs inventory``, ``q!bgs inv``"
   "``background equip``", "| Equips a profile background for the server where the command was executed. \
   | Note: *If you are not sure which profile backgrounds you own, you can view them by using one of the bot's commands to display your profile background inventory.*", "``q!bgs equip`` ``q!bgs equip 4``"
   "``background unequip`` ``background default``", "| Changes your profile background back to default.", "``q!bgs unequip``, ``q!bgs default``"
   "``leaderboard`` ``lb`` ``xplb`` ``top``", "| Shows your server's experience leaderboard.", "``q!leaderboard``, ``q!lb``, ``q!xplb``, ``q!top``"
   "``leveling``", "| Toggles (enables/disables) experience gain and leveling on your server. \
   | **Needed User Permissions: Administrator**", "``q!leveling``"
   "``leveling enable`` ``leveling e``", "| Enables experience gain and leveling on your server. \
   | **Needed User Permissions: Administrator**", "``q!leveling enable``, ``q!leveling e``"
   "``leveling disable`` ``leveling d``", "| Disables experience gain and leveling on your server. \
   | **Needed User Permissions: Administrator**", "``q!leveling disable``, ``q!leveling d``"
   "``leveling reset``", "| Resets experience and level progression for all users on your server back to 0. \
   | **Needed User Permissions: Server Owner**", "``q!leveling reset``"

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
   "``botinfo`` ``binfo``", "| Displays general information about the bot. \
   | Note: *Server bot latency is directly tied to which shard the target server is placed in.*", "``q!binfo``"
   "``8ball`` ``8b``", "| Returns an answer for a yes or no question.", "``q!8ball Should I believe you?``, ``q!8b Should I believe you?``"
   "``choose`` ``pick``", "| Picks a random item from a provided list of items, separated by a semicolon.", "``q!choose item 1;item 2;item 3``, ``q!pick item 1;item 2;item 3``"
