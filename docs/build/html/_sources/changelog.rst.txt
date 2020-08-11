Changelog
=========

quBot 1.2.5-beta (12-08-2020)
-----------------------------

.. topic:: Description

    This update is essentially a continuation of version 1.2.0. It aims to provide more freedom to server administrators/owners by giving more
    configuration options. That is why ths update introduces features such as: server-side blacklisting, server-side command enabling and disabling,
    server-side cog/module enabling and disabling, a few minor changes and some bug fixes. While this version is almost as big in terms of relevant user content as
    version 1.2.0, I believe that the current version is better suited than 1.3.0. Instead, version 1.3.0 will focus on bringing quality of life improvements, 
    optimizations and better user experience.

New features
^^^^^^^^^^^^

Administration
~~~~~~~~~~~~~~

  - **New feature:** Blacklisting users - A set of commands to prevent users from using the bot's commands in your discord server.

    - **New command:** ``blacklist`` - Blacklists the target user. As a result, they will no longer be able to use the bot in that server. 
      If the target user is already blacklisted, they will get removed from the blacklist and regain access to bot commands.
      This command can only be used by **server administrators**;

    - **New command:** ``blacklist add`` - Blacklists the target user. As a result, they will no longer be able to use the bot in that server.
      This command can only be used by **server administrators**;

    - **New command:** ``blacklist remove`` - Removes the target user from the bot blacklist. As a result, they will regain access to the
      bot's commands in that server.
      This command can only be used by **server administrators**;

  - **New command:** ``greet test`` - Command to test your custom server greetings message. This command requires users to have **Manage Server** permission;

  - **New command:** ``bye test`` - Command to test your custom server goodbye message. This command requires users to have **Manage Server** permission;

Core
~~~~

  - **New feature:** Enabling/disabling command (groups) - A set of commands to enable/disable command(s) and/or command group(s) in your discord server.

    - **New command:** ``commands enable`` - Enables a command for the server where the command was executed in. This command can only be used by **server administrators**;

    - **New command:** ``commands disable`` - Disables a command for the server where the command was executed in. Only commands that are not part of
      integral cogs/modules can be disabled. This command can only be used by **server administrators**;

  - **New feature:** Enabling/disabling modules (also known as cogs) - A set of commands to enable/disable modules in your discord server.

    - **New command:** ``modules enable`` - Enables the target cog/module on the server where the command was executed. This command can only be used
       by **server administrators**;

    - **New command:** ``modules disable`` - Disables the target cog/module on the server where the command was executed. Only non-integral modules can
      be disabled by server administrators. This command can only be used by **server administrators**;

General Changes
^^^^^^^^^^^^^^^

- Administration

  - ``warnings`` command now shows the total number of pages. Acts as a better indication of how many pages of warnings a user has.

- Conquest

  - ``sleave`` command now asks for a confirmation if you want to leave the settlement and are the only person left in it since it gets destroyed in the process.

- Core

  - The bot now shows a welcome message with instructions and general information when it joins your server.

Miscellaneous
^^^^^^^^^^^^^

  - discord.py has been updated to 1.4.1 (previously 1.4.0);

  - Updated bot dependency packages (Updated requirements.txt file);

Bug fixes
^^^^^^^^^

- Administration

  - If the user does not specify a channel, greeting and goodbye messages will now be posted in the first channel where bot has permissions to send messages 
    instead of text channel with position 0. This is considered a bug fix as said messages would not appear if your server's top text channel limits the bot's permission
    to send messages.

  - Fixed an issue preventing the bot from sending a message once a user reaches the maximum number of warnings.

- Conquest

  - User input to confirm action for command ``promote`` is longer case sensitive.

- Core

  - Reverted changes from 1.2.0: 'Case sensitivity prevented the use of commands 'modules hide' and 'modules unhide' in certain situations. Command input is no
    longer case sensitive.' - This caused unexpected issues due to its implementation. It will likely be fixed in version 1.3.0

------------

quBot 1.2.0-beta (07-08-2020)
-----------------------------

.. topic:: Description

    Unlike the bot's previous major updates, this one does not introduce many new commands. However, with this update,
    the bot goes through a lot of backend changes: configurable server-side prefixes, server-side localization, ability
    to use the bot through mentions and much more. There is a lot to cover so a detailed review and explanation of
    all new additions to the bot can be viewed below. 

New features
^^^^^^^^^^^^

Administration
~~~~~~~~~~~~~~

  - **Changed command:** ``purge`` - The purge command can now filter messages and delete only bot messages (e.g. ``purge 10 bot``).
    Main functionality of this command remains unchanged;

Core
~~~~

  This version introduces server-side bot prefixes and localization. This means that every server will be able to configure 
  these bot settings without affecting other servers. It is worth mentioning that the only language that is currently available
  is US English. With the release of 1.2, my efforts will move towards creating a localization standard and finding translators
  to expand the list of available languages.

  - **Configurable bot prefix on a per-server basis:**

    The bot previously had a configurable prefix. However, it affected the whole bot. In other words, the prefix could only be changed
    by the bot owner. With this update, every **server administrator** can change the prefix the bot uses on a server-wide scale.

    - **New command:** ``prefix`` - Shows or changes the bot’s prefix on the server. This command can only be used by **server administrators**;

    - **New command:** ``prefix reset`` - Resets the bot’s prefix on the server back to default.
      This command can only be used by **server administrators**;

    - **New command:** ``prefix show`` - Shows the bot’s prefix on the server. This command can be used by everyone;

  - **Configurable bot language on a per-server basis:**

    The bot previously had a configurable language option. However, it changed the language for the whole bot and could only be used by
    the bot owner. With this update, every **server administrator** can change the language of the bot on a server-wide scale.

    - **Changed command:** ``langs`` - The function of this command has not changed. **However, now everyone can use this command**;

    - **Changed command:** ``langset`` - This command now changes the bot language for the target server. 
      This command can only be used by **server administrators**;

Utility
~~~~~~~

  - **New command:** ``botinfo`` - Displays general information about the bot. Can be used by people to check bot latency on target guild;

General Changes
^^^^^^^^^^^^^^^

  - The bot can now be used by simply mentioning it. This can be used as an alternative of the prefix if you do not know what prefix the bot uses;

Core
~~~~

  - The following commands **no longer require** bot owner privileges and can be used by everyone: ``userid``, ``serverid``, ``channelid``, ``roleid``;

  - The languages list command **no longer require** bot owner privileges and can be used by everyone;

  - The language set command permission requirements have been changed from **bot owner** to **server administrator**;

HelpFormatter
~~~~~~~~~~~~~

  - The bot's invite link in the general help command now changes bot id dynamically to work with any bot instance.

Economy
~~~~~~~

  - A new command alias has been added to the currency command: ``balance``;

  - Voting for the bot on discordbotlist.com now rewards users (Does not apply to self-hosted instances of the bot);


Miscellaneous
^^^^^^^^^^^^^

  - discord.py has been updated to 1.4.0 (previously 1.3.4);

  - Small changes to documentation installation guides for Windows and Linux;

  - Updated bot dependency packages (Updated requirements.txt file);

Bug fixes
^^^^^^^^^
- Conquest

  - Fixed a few syntax warnings related to the Conquest module;

- Core

  - Case sensitivity prevented the use of command 'commands' in certain situations. Command input is longer case sensitive.

  - Case sensitivity prevented the use of commands 'modules hide' and 'modules unhide' in certain situations. Command input is no
    longer case sensitive.

- Dictionaries

  - Fixed functionality of 'synonym' and 'antonym' commands. Likely changes in Thesaurus' web structure caused issues when extracting
    required information.

- Economy

  - Fixed issues related to on_raw_reaction_add: Event used to raise exceptions about missing access to target user's information.

- HelpFormatter

  - The bot's invite link in the general help command had an outdated permissions code and asked for Administrator privileges.
    This is no longer the case.

- Utility

  - Argument input type for user has been changed from discord.User to discord.Member due to an exception about a missing role attribute on discord.User on
    userinfo command.

------------

quBot 1.1.0-rc3 (03-08-2020)
-----------------------------

.. topic:: Description

    A quick update to fix an issue related to the settlement info command for the Conquest module.

Bug fixes
^^^^^^^^^
- Conquest

  - Fixed an issue preventing users from seeing other people's settlement information. The command used to always
    show the message author's settlement.

------------

quBot 1.1.0-rc2 (18-07-2020)
-----------------------------

.. topic:: Description

    A quick update to fix an issue that was reported by a user.

Bug fixes
^^^^^^^^^
- Conquest

  - Fixed an issue preventing users from buying materials on the conquest game mode market.

------------

quBot 1.1.0-rc1 (18-07-2020)
-----------------------------

.. topic:: Description

    A quick update to fix an issue I noticed to the purge command in the Administration module. Server is also now using discord.py 1.3.4
    to fix issue #5109 (https://github.com/Rapptz/discord.py/issues/5109) which potentially caused stability issues to the bot.

Bug fixes
^^^^^^^^^
- Administration    

  - Purge command, part of the Administration module, was raising a 404 message not found due to execution of the purge function prior to the
    deletion of the user's command message.

- General

  - Python module 'discord.py' was updated from version 1.3.3 to 1.3.4 to fix issue #5109.

------------

quBot 1.1.0-beta (25-04-2020)
-----------------------------

.. topic:: Description

    This update introduces additional features to the Administration module: softbans, ability to delete specific user warning
    and a server system for greeting and farewell messages. In addition to that, a few bugs were found and fixed.

New features
^^^^^^^^^^^^

Administration
~~~~~~~~~~~~~~

  Version 1.0 felt incomplete without the ability to delete specific user warning. It is, in fact, the reason why 1.1.0 was
  pushed this early after version 1.0. 

  - **New command:** ``warnings delete`` - Deletes a specific warning that was issued to the target individual;

  - **New command:** ``softban`` - Soft bans the mentioned individual for a specified reason (if any); It essentially kicks the user
    from the server and deletes their messages;

  - **Server Greeting/Goodbye Toggles:**

    Server greetings/goodbye messages are not something new and revolutionary. In fact, Discord also offers an in-built simplified version
    of that system. However, compared to Discord's solution, this implementation offers a lot more freedom and customization to the end user.

    - **New command:** ``greet`` - Toggles server greeting messages on/off on the server;

    - **New command:** ``bye`` - Toggles server goodbye messages on/off on the server;

    - **New command:** ``greet enable`` - Enables server greeting messages on the server;

    - **New command:** ``bye enable`` - Enables server goodbye messages on the server;

    - **New command:** ``greet disable`` - Disables server greeting messages on the server;

    - **New command:** ``bye disable`` - Disables server goodbye messages on the server;

    - **New command:** ``greet dm`` - Enables server greetings on the server. Instead of the server's text channel, future
      messages will instead be sent to users' direct messages;

    - **New command:** ``greet message`` - Changes the greeting message to a custom one;

    - **New command:** ``greet message default`` - Resets the server greeting message back to default;

    - **New command:** ``bye message`` - Changes the goodbye message to a custom one;

    - **New command:** ``bye message default`` - Resets the server goodbye message back to default;

    - **New commands:** ``greet setchannel`` ``bye setchannel`` - Sets the text channel where greetings and goodbye messages are going to be sent by the bot;

    - **New commands:** ``greet setchannel default`` ``bye setchannel default`` - Resets the greetings/goodbye messages text channel back to default;

Bug fixes
^^^^^^^^^
- HelpFormatter now works with subcommand aliases;

- Automatic warning actions did not trigger on the exact warning value but on the next one. That has been fixed.

------------

quBot 1.0.0-beta (23-04-2020)
-----------------------------

.. topic:: Description

    This update introduces many new features to the Administraton module, a new Dictionaries module and a few new
    commands to Core, Conquest, Economy & Utility modules. There is a lot to cover so a detailed review and explanation of
    all new additions to the bot can be viewed below. This update marks version 1.0 of the bot. 

    The next few updates will most likely be of a smaller scale and will only cover very specific parts of the bot's codebase.
    Thank you for your time.

New features
^^^^^^^^^^^^

Administration
~~~~~~~~~~~~~~

  The first public version of the bot featured only three administration commands: purge, kick & ban. With this version, I aimed to greatly
  expand the moderation toolkit. While there is still more that I can add to this module, I do not wish to delay this version any further.
  More commands are planned for future updates (temporary mutes & bans, blacklisting users, slowmode controls, etc.).

  - **New command:** ``unban`` - Unbans the target user from the server where the command was executed;

  - **New command:** ``mute`` - Mutes the target individual from chatting on the server;

  - **New command:** ``unmute`` - Unmutes the target individual if they were previously muted using the bot;

  - **User reporting:**

    User reporting is a feature that allows for normal users to report malicious behaviour/content on a server to the respective server
    authorities (moderators/administrators) without directly contacting them. As a result, it hopefully makes chat moderation a little bit easier.

    *This feature is disabled by default. To enable it, a person with administrator privileges needs to set a report channel.*

    - **New command:** ``report`` - Reports the target user for a particular reason;

    - **New command:** ``report setchannel`` - Selects a text channel where future user reports are going to be sent;

    - **New command:** ``report disable`` - Disables user reporting for the server where the command was executed;

  - **User warnings:**

    User warnings are a system to help keep track of....you guessed it - user warnings. All users with the ability to kick and ban other members
    can use it to issue warnings. By default, users can issue up to 20 warnings per user. In all honesty, this by itself is a rather lackluster system.
    However, it arrives out of the box with automatic warning actions. This gives the power to moderators/administrators to set up automatic (mute, kick, ban) actions
    that will trigger once users reach a set number of warnings.

    *Automatic warning actions are disabled by default. To enable them, a person with the aforementioned privileges needs to set them up*

    - **New command:** ``warn`` - Warns the target user with a provided reason. This individual will receive a direct message from the bot;

    - **New command:** ``warnings`` - Displays a list of warnings for the target individual;

    - **New command:** ``warnings reset`` - Resets all warnings for the target individual;

    - **New command:** ``warnings auto`` - Changes the number of warnings needed for a user to trigger an automatic mute/kick/ban from the server;

    - **New command:** ``warnings auto disable`` - Disables the target automatic action from triggering for future user warnings;

Conquest
~~~~~~~~

  - **New command:** ``rename`` - Renames your settlement to the specified name. Settlement renaming costs 500 gold;

Core
~~~~

  - **New command:** ``roleid`` - Returns the target role's ID for the server where the command was executed;

Dictionaries (New)
~~~~~~~~~~~~~~~~~~

  - **New command:** ``dict`` - Returns a list of definitions based on the term you parse to the bot;

  - **New command:** ``synonym`` - Returns a list of the top synonyms from Thesaurus based on the term you parse to the bot;

  - **New command:** ``antonym`` - Returns a list of the top antonyms from Thesaurus based on the term you parse to the bot;

  - **New command:** ``urbandict`` - Returns the top urban dictionary definition based on the term you parse to the bot;

Economy
~~~~~~~

  This update features a set of commands to help bot owners organise currency giveaways

  - **New command:** ``giveaway start`` - Starts a currency giveaway. Users can claim their reward by reacting to the bot message;

  - **New command:** ``giveaway end`` - Ends a giveaway by the provided bot giveaway message ID;

Utility
~~~~~~~

  - **New command:** ``8ball`` - Returns an answer for a yes or no question;

  - **New command:** ``choose`` - Picks a random item from a provided list of items, separated by a semicolon;

General Changes
^^^^^^^^^^^^^^^
- The bot's HelpFormatter (the help command) has been improved to now accept command aliases. In addition to that, the formatter now
  works with subcommands that have depth more than one. The latter was introduced to function properly for commands
  such as: ``warnings auto disable``;

Miscellaneous
^^^^^^^^^^^^^
- PyDictionary has been removed from the package dependency list. Instead, a custom module was created for the Dictionaries module;

  - I was dissatisfied with the limited features the module provided. That is why I opted for a custom module;

- discord.py has been updated to 1.3.3 (previously 1.3.1);

Bug fixes
^^^^^^^^^
- Administration

  - Command ``purge`` did not return an embed message when the input number was negative. This has been addressed and fixed;

- Core

  - Command ``channelid`` returned the wrong reply upon exection. This has also been addressed and fixed;

- Conquest

  - Fixed page display issues for the leaderboard command;

    - The leaderboard command did not display settlements properly beyond the first page. Settlements were not inlined. Moreover,
      settlements were ranked 1-9 regardless of the page number. The way settlements are sorted before display has also been improved.

  - Fixed issue that was raising exceptions when a user who is not part of a settlement called the ``code show`` command;

------------

quBot 0.9.6-beta (09-02-2020)
-----------------------------

.. topic:: Description

    Implemented bot intergration with top.gg - Top.gg will now update the bot's server count every 30 minutes on its website.
    Furthermore, every bot vote will now reward the user with 50 bot currency on weekdays and 100 on weekends.

General Changes
^^^^^^^^^^^^^^^
- Server counter intergration with Top.GG;
- Vote rewards to users who vote for the bot on Top.GG;

Bug fixes
^^^^^^^^^
- Fixed issues with logs auto-deletion on files with file size less than 1kb;

------------

quBot 0.9.5-beta (09-02-2020)
-----------------------------

.. topic:: Description

    This is the first rather large update to the bot since its public open beta release. It introduces new features
    to the Conquest game mode: upgradable settlement buildings, settlement resource system and a resource market that
    resets every 24 hours. This is the first step going forward with the Conquest game with more planned features such
    as tournaments, alliances(guilds) and achievements. While I am ready to start work on that, I feel like I need to
    focus my attention to the bot's moderation toolkit and utility commands. The next bot update will mainly focus on
    these two things.

New features
^^^^^^^^^^^^
- Conquest

    - Upgradable settlement buildings:

        - Town Hall (Level 1 - 10) - This is the main building of any settlement. Upgrading the town hall will
          increase the max Level limit for all other buildings;

        - Training Grounds (Level 1 - 10) - Building and leveling the Training Grounds will increase the settlement's attack points;

        - Market Square (Level 1) - Building the Market Square will allow settlement leaders to buy and sell resources
          on the market;

        - Walls (Level 1 - 10) - Building and leveling the settlement walls will increase the settlement's defence points;

        - Quarry (Level 1 - 10) (Produces Stone) - Building the quarry will allow settlements to produce a certain amount of stone every day.
          Upgrading the quarry will increase the daily amount of stone your settlement produces;

        - Farms (Level 1 - 10) (Produces Food) - Building farms will allow settlements to produce a certain amount of food every day.
          Upgrading the farms will increase the daily amount of food your settlement produces;

        - Weavery (Level 1 - 10) (Produces Cloth) - Building the weavery will allow settlements to produce a certain amount of cloth every day.
          Upgrading the weavery will increase the daily amount of cloth your settlement produces;

        - Lumberjack's Camp (Level 1 - 10) (Produces Wood) - Building the lumberjack's camp will allow settlements to produce a certain amount
          of wood every day. Upgrading the lumberjack's camp will increase the daily amount of wood your settlement produces;

        - Warehouse (Level 1) - Building the Warehouse will remove the 1000 resource limit (per item);

        - Academy (Level 1 - 10) - Building and leveling the Academy will slightly increase the settlement's attack and defence points;

    - Resource market - Integral part of the settlement resource system, the market allows users to buy and sell resources for gold;

    - Settlement resource system - Part of the building upgrade system, settlements can now produce: Cloth, Food, Stone & Wood;

    - New command: ``deposit`` - Allows users to deposit a certain amount of bot currency to the settlement they are part of;

    - New command: ``requirements`` - Displays target settlement building upgrade requirements for every level from 1 to 10;

Miscellaneous
^^^^^^^^^^^^^

- Added .pyc, .pyo & .log files to .gitignore

  - I noticed that these temporary/cache files cause unnecessary merge conflicts;

Bug fixes
^^^^^^^^^
- Fixed missing conquest join public/private help and description JSON strings;

------------

quBot 0.9.1-beta (24-01-2020)
-----------------------------

.. topic:: Description

    Since this is the first version that is getting tracked via the changelog, I will not be writing
    everything that has been implemented by this point. Therefore, this is here to serve as a template
    for future use.

General Changes
^^^^^^^^^^^^^^^
- Placeholder

Bug fixes
^^^^^^^^^
- Placeholder

.. note:: **Versions prior 0.9.1-beta**

    Since I did not keep track of all the changes prior to 0.9.1-beta, this will be the first entry
    in the changelog


