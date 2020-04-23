Changelog
=========

quBot 1.0.0-beta (XX-04-2020)
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


