Linux Installation Guide
========================

Setting up quBot on Linux
-------------------------

If you're looking to install and self-host the bot on your Ubuntu machine, then this guide is for you.

.. attention:: **Guide Accuracy**

    While I tried to be as concise as possible, I have limited experience with Linux distributions.
    This is the exact reason why the guide is available only for the *Ubuntu* distro.
    
    If you feel like you can contribute with the documentation, feel free to contact me.

.. note:: **Operating System Compatibility**

    The bot has only been tested on Ubuntu 19. It is possible that it will not be able to run on systems running versions older than Ubuntu 16.

1. **Intalling Python 3.7**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, you will need to install Python 3.7. Open a UNIX Terminal of your choice and 
follow the instructions below.

Type these commands in the following order:

.. code-block:: bash

    1.1 ) ~$ sudo apt-get update
    1.2 ) ~$ sudo apt install software-properties-common
    1.3 ) ~$ sudo add-apt-repository ppa:deadsnakes/ppa
    1.4 ) ~$ sudo apt install python3.7

.. tip:: **Installation verification**

    Feel free to verify if Python 3.7 was successfully installed on your machine by typing:

    .. code-block:: bash

        ~$ python 3.7 --version

2. **Installing Git (Optional)**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since it is possible to directly download the bot's files from GitHub, you can skip this step if you want to.
Nevertheless, it is recommended to have git on your machine.

Type these commands in the following order:

.. code-block:: bash

    2.1 ) ~$ sudo apt-get update
    2.2 ) ~$ sudo apt-get install git

.. tip:: **Installation verification**

    To verify if Git was successfully installed on your machine, use:

    .. code-block:: bash

        ~$ git --version

3. **Downloading bot from GitHub**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you decided to use Git, use the following command to clone the repository to a directory of your choosing.

.. code-block:: bash

    git clone https://github.com/martin-r-georgiev/quBot.git

4. **Creating virtual environment**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While not necessary, it is strongly recommended to use a virtual environment to locally store all installed packages without disrupting other applications on your machine that use Python.
If you decide not to use a virtual environment, skip to step 4.6

.. code-block:: bash

    4.1 ) ~$ sudo apt-get install python3-pip
    4.2 ) ~$ sudo apt-get install python3-venv
    4.3 ) ~$ python3 -m venv QBEnv
    4.4 ) ~$ cd QBEnv/bin/
          ~$ source activate

4.5 ) Copy the requirements.txt file from the main directory to to ./QBEnv/bin/

.. code-block:: bash

    4.6 ) ~$ pip3 install -r requirements.txt --no-index

5. **Creating an executable bash file**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

5.1 ) Go back to the bot's main directory (Where main.py is located)

.. code-block:: bash

    5.2 ) ~$ touch run (Command to create a file)
    5.3 ) Open the file in a text editor of your choosing and write the follwing code:

            #!/bin/bash
            ./QBEnv/bin/python main.py

            ------ Upper bit for users with virtual environment, lower - no virtual environment

            #!/bin/bash
            python3 main.py

6. **Running the bot for the first time**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    6.1 ) ~$ source run

If no problems occur during the execution of the file, you will be prompted to enter your token in **config.ini** before running the script again.
After you're done adding your token, use the command again in your Terminal.

After following these steps, you should have a fully working bot. If you are having any difficulties, feel free to contact me on Discord for help.