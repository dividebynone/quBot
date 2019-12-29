<p align="center">
  <img src="https://i.imgur.com/dtHZJzu.png">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.7.1b-blue.svg">
  <img src="https://img.shields.io/badge/dev-DivideByNone%239640-brightgreen.svg">
</p>

<p align="center">A modern and simple to use discord bot application written in Python using the <b>discord.py</b> API wrapper.</p>

<p align="center">
The bot is still in early development. It has been created in occasion of Discord's Hack Week. Nevertheless, I have plans to continue development after the event. Planned official release for early 2020.
</p>

## Setup & Installation

The application has been updated to [Python 3.7.6](https://www.python.org/downloads/release/python-376/). While the bot's current features work on older versions of Python 3, this might not be the case in the future. Using the same version on python is highly recommended.

If you're using Windows, feel free to download said Python version from the link above. In case your operating system is Ubuntu(or any other using UNIX), feel free to follow the steps below on how to setup the bot.

After you are done installing python, either use git clone or directly download using the GitHub platform.

### * *On Windows*

> To easily launch the bot on Windows, you could create a batch file in the main directory. Give it a name and write this in the file:
```
@echo off
QBEnv\Scripts\python.exe main.py %*
pause
```
### * *Setting up quBot on Linux*

*Operating System Compatibility* - The bot has only been tested on Ubuntu 19. It is possible that it will not be able to run on systems running versions older than Ubuntu 16.

#### 1 | Intalling Python 3.7

First, you will need to install Python 3.7. In order to do that, you need to type the following commands in your UNIX Terminal in the order you see them.
> 1.1 | ~$ sudo apt-get update

> 1.2 | ~$ sudo apt install software-properties-common

> 1.3 | ~$ sudo add-apt-repository ppa:deadsnakes/ppa

> 1.4 | ~$ sudo apt install python3.7

Feel free to verify if Python 3.7 was successfully installed on your machine by typing:

> 1.5 (Optional) | ~$ python 3.7 --version

#### 2 | Installing Git (Optional)

Since it is possible to directly download the files from GitHub, you can skip this step if you want to.

> 2.1 | ~$ sudo apt-get update

> 2.2 | ~$ sudo apt-get install git

To verify if Git was successfully installed on your machine, use:

> 2.3 (Optional) | ~$  git --version

#### 3 | Downloading bot from GitHub

If you decided to use Git, use the following command to clone the repository to a directory of your choosing.

> 3.1 | ~$ git clone https://github.com/martin-r-georgiev/quBot.git

#### 4 | Creating virtual environment

While not necessary, it is strongly recommended to use a virtual environment to locally store all installed packages without disrupting other applications on your machine that use Python. If you decide not to use a virtual environment, skip to step 4.6

    4.1 | ~$ sudo apt-get install python3-pip
    4.2 | ~$ sudo apt-get install python3-venv
    4.3 | ~$ python3 -m venv QBEnv
    4.4 | ~$ cd QBEnv/bin/
          ~$ source activate
    4.5 | Move the requirements.txt file from the main directory to to ./QBEnv/bin/
    4.6 | ~$ pip3 install -r requirements.txt --no-index
    
#### 5 | Creating an executable bash file

    5.1 | Go back to the bot's main directory (Where main.py is located)
    5.2 | ~$ touch run (Command to create a file)
    5.3 | Open the file in a text editor of your choosing and write the follwing code:
              #!/bin/bash
              ./QBEnv/bin/python main.py

	           ------ Upper bit for users with virtual environment, lower - no virtual environment
              
              #!/bin/bash
              python3 main.py
              
 #### 6 | Running the bot for the first time
 
     6.1 | ~$ source run

If no problems occur during the execution of the file, you will be prompted to enter your token in config.ini before running the script again. After you're done adding your token, use the command again in your Terminal.

After following these steps, you should have a fully working bot. If you are having any difficulties, feel free to contact me on Discord for help.

## Commands

Currently, you'll have to use ```.help``` . The documentation is in WIP and will be linked here **ASAP**

## Links

[**Discord Support Server**](https://discord.gg/TGnfsH2) : If you have any inquiries, suggestions, or just want to chat. You could join at any time. Keep in mind that this is my first python project. Any sort of critism is greatly appreciated!
