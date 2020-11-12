from libs.sqlhandler import sqlconnect
from discord.ext import commands
from main import bot_path
import random
import string
import json
import os

# Check if the bot is running inside a virtual environment


def makefolders(root_path, folders_list):
    for folder in folders_list:
        os.makedirs(os.path.join(root_path, folder), exist_ok=True)


def safe_cast(value, to_type, default=None):
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default

# data.json initialization


def sync_data_get():
    with open(os.path.join(bot_path, 'data', 'data.json'), 'r') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    return json_data


async def data_get():
    with open(os.path.join(bot_path, 'data', 'data.json'), 'r') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    return json_data


def sync_data_set(json_dump: dict):
    with open(os.path.join(bot_path, 'data', 'data.json'), 'w') as json_file:
        json.dump(json_dump, json_file, indent=4, sort_keys=True, separators=(',', ': '))
    json_file.close()


async def data_set(json_dump: dict):
    with open(os.path.join(bot_path, 'data', 'data.json'), 'w') as json_file:
        json.dump(json_dump, json_file, indent=4, sort_keys=True, separators=(',', ': '))
    json_file.close()

# Modules configuration


def get_module_config():
    if not os.path.isfile(os.path.join(bot_path, 'data', 'modules.json')):
        print("Creating missing modules.json file...")
        with open(os.path.join(bot_path, 'data', 'modules.json'), 'w+') as json_file:
            json.dump({}, json_file, indent=4, sort_keys=True, separators=(',', ': '))
        json_file.close()

    with open(os.path.join(bot_path, 'data', 'modules.json'), 'r') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    return json_data


def update_module_config(json_dump: dict):
    with open(os.path.join(bot_path, 'data', 'modules.json'), 'w') as json_file:
        json.dump(json_dump, json_file, indent=4, sort_keys=True, separators=(',', ': '))
    json_file.close()


def module_configuration(module_name: str, is_restricted: bool, module_dependencies: list):
    module_directory_list = [os.path.splitext(i)[0] for i in os.listdir(os.path.join(bot_path, 'modules'))]

    module_config = get_module_config()
    if is_restricted and module_name not in module_config.setdefault("restricted_modules", []):
        module_config.setdefault("restricted_modules", []).append(module_name)
    if len(module_dependencies) > 0:
        for dependency in module_dependencies:
            if dependency in module_directory_list and dependency not in module_config.setdefault("dependencies", {}).setdefault(module_name, []):
                module_config.setdefault("dependencies", {}).setdefault(module_name, []).append(dependency)
    else:
        module_config.setdefault("dependencies", {}).pop(module_name, None)
    update_module_config(module_config)

# Exports configuration


def export_commands(json_dump: dict):
    makefolders(bot_path, ['exports'])
    with open(os.path.join(bot_path, 'exports', 'commands.json'), 'w') as json_file:
        json.dump(json_dump, json_file, indent=4, sort_keys=True, separators=(',', ': '))
    json_file.close()

# Database folder creation(if missing) #TODO: Delete in the future (duplicate code <-> main.py)


if not os.path.exists(os.path.join(bot_path, 'databases')):
    os.makedirs(os.path.join(bot_path, 'databases'), exist_ok=True)

# Creating needed database files(if missing)


def user_database_init():
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS users(userid INTEGER PRIMARY KEY , currency INTEGER, daily_time BLOB)")


async def user_get(user_id: int):
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("INSERT OR IGNORE INTO users(userid, currency) VALUES(?, ?)", (user_id, '0'))
        cursor.execute("SELECT IfNull(currency,0), IfNull(daily_time,0) FROM users WHERE userid=?", (user_id,))
        db_output = list(cursor.fetchone())
        return_dict = dict(currency=db_output[0], daily_time=db_output[1])
        return return_dict


async def user_set(user_id: int, dict_input):
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("INSERT OR IGNORE INTO users(userid, currency) VALUES(?, ?)", (user_id, '0'))
        cursor.execute("UPDATE users SET currency=?, daily_time=? WHERE userid=?", (dict_input['currency'], dict_input['daily_time'], user_id))

# Auxiliary functions


def string_generator(size):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def plural(number: int, singular: str, plural: str):
    if number > 0:
        return f"{number:,} {singular if number == 1 else plural}"
    else:
        return ""


def humanize_join(sequence, final, delim=', '):
    size = len(sequence)

    if size == 0:
        return ''
    if size == 1:
        return sequence[0]
    if size == 2:
        return f'{sequence[0]} {final} {sequence[1]}'

    return delim.join(sequence[:-1]) + f' {final} {sequence[-1]}'


def humanize_time(lang, time, accuracy=3, past=False):
    from datetime import datetime, timezone
    from dateutil.relativedelta import relativedelta

    if type(time) is float:
        time = datetime.fromtimestamp(time)
    now = datetime.now().replace(tzinfo=timezone.utc)
    time = time.replace(tzinfo=timezone.utc)
    if time < now:
        delta = relativedelta(now, time).normalized()
        structured = lang["timeago"] if past else "{}"
    else:
        delta = relativedelta(time, now).normalized()
        structured = "{}"

    accuracy = max(accuracy, 1)
    attrs = ['years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds']
    local = {
        'years': [lang["year_string"], lang["years_string"]],
        'months': [lang["month_string"], lang["months_string"]],
        'weeks': [lang["week_string"], lang["weeks_string"]],
        'days': [lang["day_string"], lang["days_string"]],
        'hours': [lang["hour_string"], lang["hours_string"]],
        'minutes': [lang["minute_string"], lang["minutes_string"]],
        'seconds': [lang["second_string"], lang["seconds_string"]],
    }

    def formatted(elem, attr):
        return plural(elem, local[attr][0], local[attr][1])

    output = []
    counter = 0
    for attr in attrs:
        elem = getattr(delta, attr)
        if counter >= accuracy:
            break
        if not elem or elem <= 0:
            continue
        else:
            output.append(formatted(elem, attr))

        counter += 1

    if len(output) == 0:
        return lang["now_string"]
    else:
        return structured.format(humanize_join(output, lang["and_string"]))

# Extended Command


class ExtendedCommand(commands.Command):
    def __init__(self, *args, **kwargs):
        self.permissions = kwargs.pop('permissions')
        super().__init__(*args, **kwargs)


class ExtendedGroup(commands.Group):
    def __init__(self, *args, **kwargs):
        self.permissions = kwargs.pop('permissions')
        super().__init__(*args, **kwargs)
