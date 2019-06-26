import sys
import random
import string
import json

#Check if the bot 
def is_venv():
        return (hasattr(sys, 'real_prefix') or
                (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

#data.json initialization
async def data_get():
        with open('./data/data.json', 'r') as json_file:
                json_data = json.load(json_file)
        json_file.close()
        return json_data

async def data_set(json_dump: dict):
        with open('./data/data.json', 'w') as json_file: 
                json.dump(json_dump, json_file, indent=4, sort_keys=True,separators=(',', ': '))
        json_file.close()