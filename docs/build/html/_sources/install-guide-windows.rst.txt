Windows Installation Guide
==========================

Setting up quBot on Windows
---------------------------

If you're looking to install and self-host the bot on your Windows machine, then this guide is for you.

1. **Intalling Python 3.7**
^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, you will need to install `Python 3.7.6 <https://www.python.org/downloads/release/python-376/>`_.
After you download the executable, run it and follow the installation instructions.

.. warning:: **When installing Python**

    Please make that you include Python to the PATH. Otherwise, you may run into issues later on.

2. **Installing Git (Optional)**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since it is possible to directly download the bot's files from GitHub, you can skip this step if you want to.
Nevertheless, it is recommended to have git on your machine.

`Click here to download Git <https://git-scm.com/downloads>`_

3. **Downloading bot from GitHub**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you decided to use Git, use the following command in your Git Bash to clone the repository to a directory of your choosing.

.. code-block:: bash

    git clone https://github.com/martin-r-georgiev/quBot.git

4. **Creating a virtual environment**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Go to the main directory of the bot (the folder with main.py and requirements.txt) via
Command Prompt and write the following code:

.. code-block:: bash

    python3 -m venv QBEnv

Now you must navigate to **./QBEnv/Scripts/** to activate the virtual environment

Once you navigated to the desired folder, write the following snippet into the terminal:

.. code-block:: bash

    activate

.. important::

    You must activate the virtual environment every time you open a new Command Prompt.

.. note::

    Once you're done with everything in regards to the virtual environment in the Command Prompt,
    write the following snippet:

    .. code-block:: bash

        deactivate

5. **Installing needed packages to virtual environment**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you activated your virtual environment, copy the requirements.txt file to **./QBEnv/Scripts/**
and write the following code:

.. code-block:: bash

    pip install -r requirements.txt --no-index

6. **Creating an executable batch file**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If everything went smoothly with the package installation, you are ready to run the bot for the first time.

Create a batch file in the main directory. Give it a name and write this in the file:

.. code-block::

    @echo off
    QBEnv\Scripts\python.exe main.py %*
    pause

.. note::

    The batch file is not needed, but makes running the bot less of a hassle.

7. **Running the bot for the first time**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If no problems occur during the execution of the file, you will be prompted to enter your token in **config.ini** before running the script again.
After you're done adding your token, run the .bat file again.

After following these steps, you should have a fully working bot. If you are having any difficulties, feel free to contact me on Discord for help.

