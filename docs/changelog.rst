Changelog
=========


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
^^^^^^^^^^^^^^^
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


