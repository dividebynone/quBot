import sqlite3
import discord
import os
import sys
import random
import string
import json

#Check if the bot is running inside a virtual environment
def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

#data.json initialization
def sync_data_get():
    with open('./data/data.json', 'r') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    return json_data

async def data_get():
    with open('./data/data.json', 'r') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    return json_data

def sync_data_set(json_dump: dict):
    with open('./data/data.json', 'w') as json_file: 
        json.dump(json_dump, json_file, indent=4, sort_keys=True,separators=(',', ': '))
    json_file.close()

async def data_set(json_dump: dict):
    with open('./data/data.json', 'w') as json_file: 
        json.dump(json_dump, json_file, indent=4, sort_keys=True,separators=(',', ': '))
    json_file.close()

#Database folder creation(if missing)
if not os.path.exists('./databases'):
    os.makedirs('./databases', exist_ok=True)

class ContextManager(object):
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        self.conn.commit()
        self.conn.close()

#Creating needed database files(if missing)
def user_database_init():
    with ContextManager('./databases/users.db') as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS users(userid INTEGER PRIMARY KEY , currency INTEGER, daily_time BLOB)")
        cursor.execute("CREATE TABLE IF NOT EXISTS giveaway_participants(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, userid INTEGER, msgid INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS giveaways(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, msgid INTEGER, value INTEGER)")

async def user_get(user: discord.User):
    with ContextManager('./databases/users.db') as cursor:
        cursor.execute("INSERT OR IGNORE INTO users(userid, currency) VALUES(?, ?)", (user.id, '0'))
        cursor.execute("SELECT IfNull(currency,0), IfNull(daily_time,0) FROM users WHERE userid=?", (user.id,))
        db_output = list(cursor.fetchone())
        return_dict = dict(currency=db_output[0], daily_time=db_output[1])
        return return_dict

async def user_set(user: discord.User, dict_input):
    with ContextManager('./databases/users.db') as cursor:
        cursor.execute("INSERT OR IGNORE INTO users(userid, currency) VALUES(?, ?)", (user.id, '0'))
        cursor.execute("UPDATE users SET currency=?, daily_time=? WHERE userid=?",
                        (dict_input['currency'], dict_input['daily_time'], user.id))

#Conquest
        
def conquest_database_init():
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS conquest(settlement_id INTEGER PRIMARY KEY ,invite_string BLOB,\
                date_created BLOB,founderid BLOB,leaderid BLOB,name BLOB,treasury INTEGER,tech_attack INTEGER,\
                tech_defence INTEGER, size INTEGER, level INTEGER,tech_tree BLOB,\
                type TEXT,entry_fee INTEGER, wins INTEGER, losses INTEGER, experience INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS members(userid INTEGER PRIMARY KEY, settlement_id INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS resources(settlement_id INTEGER PRIMARY KEY, cloth INTEGER, wood INTEGER, stone INTEGER, food INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS buildings(id INTEGER PRIMARY KEY, name BLOB, mltplr_cloth INTEGER, mltplr_food INTEGER, mltplr_stone INTEGER, mltplr_wood INTEGER, mltplr_gold INTEGER)")
        # Inserting buildings
        cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (1, 'Town Hall', 0 , 1, 1, 1, 250,))
        cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (2, 'Training Grounds', 5, 5, 2, 2, 0,))
        cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (3, 'Market Square', 0, 0, 0, 0, 2500,))
        cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (4, 'Walls', 0, 0, 5, 5, 50,))
        cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (5, 'Quarry', 3, 3, 0, 0, 20))
        cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (6, 'Farms', 0, 0, 0, 7, 20))
        cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (7, 'Weavery', 0, 7, 0, 0, 5))
        cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (8, "Lumberjack's Camp", 2, 7, 0, 0, 5))
        cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (9, 'Warehouse', 0, 0, 0, 0, 5000))
        cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (10, 'Academy', 0, 0, 5, 5, 125))

def string_generator(size):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

async def conquest_get(get_string:str, input_data):
    with ContextManager('./databases/conquest.db') as cursor:
        if get_string is 'user':
            cursor.execute("SELECT * FROM conquest WHERE founderid=? OR leaderid=?", (input_data,input_data,))
        elif get_string is 'settlement':
            cursor.execute("SELECT * FROM conquest WHERE name=?", (input_data,))
        elif get_string is 'code':
            cursor.execute("SELECT * FROM conquest WHERE invite_string=?", (input_data,))
        elif get_string is 'id':
            cursor.execute("SELECT * FROM conquest WHERE settlement_id=?", (input_data,))
        else:
            print('FAILED TO GET FROM CONQUEST DATABASE')
            return None

        db_output = cursor.fetchone()
        if db_output is None:
            return None
        else:
            db_output = list(db_output)
            return_dict = dict(settlement_id=db_output[0], invite_string=db_output[1], date_created=db_output[2], founderid=db_output[3],
                            leaderid=db_output[4], name=db_output[5], treasury=db_output[6], tech_attack=db_output[7],
                            tech_defence=db_output[8], size=db_output[9], level=db_output[10],
                            tech_tree=db_output[11], type=db_output[12], entry_fee=db_output[13], wins=db_output[14],
                            losses=db_output[15], experience=db_output[16])
            return return_dict

async def conquest_set(get_string:str, input_data, dict_input):
    with ContextManager('./databases/conquest.db') as cursor:
        if get_string is 'new':
            cursor.execute("INSERT OR IGNORE INTO conquest(founderid, leaderid, treasury, entry_fee, invite_string, date_created, tech_attack, tech_defence, name, level, tech_tree, type, size, wins, losses, experience) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            [input_data, input_data, dict_input["entry_fee"], dict_input["entry_fee"], dict_input["invite_string"],
                            dict_input["date_created"], '0', '0', dict_input["name"],'1', '0000000000', dict_input["type"],
                            '1', 0, 0, 0])
            return cursor.lastrowid
        elif get_string is 'user':
            cursor.execute("UPDATE conquest SET founderid=?, leaderid=?, treasury=?, entry_fee=?, invite_string=?, date_created=?, tech_attack=?, tech_defence=?, name=?, level=?, tech_tree=?, type=?, size=?, wins=?, losses=?, experience=? WHERE founderid=? OR leaderid=?",
                            [dict_input["founderid"], dict_input["leaderid"], dict_input["treasury"], dict_input["entry_fee"], dict_input["invite_string"],
                            dict_input["date_created"], dict_input["tech_attack"], dict_input["tech_defence"], dict_input["name"], dict_input["level"], dict_input["tech_tree"], dict_input["type"],
                            dict_input["size"], dict_input["wins"], dict_input["losses"], dict_input["experience"], input_data, input_data])
        elif get_string is 'invite':
            cursor.execute("UPDATE conquest SET founderid=?, leaderid=?, treasury=?, entry_fee=?, invite_string=?, date_created=?, tech_attack=?, tech_defence=?, name=?, level=?, tech_tree=?, type=?, size=?, wins=?, losses=?, experience=? WHERE invite_string=?",
                            [dict_input["founderid"], dict_input["leaderid"], dict_input["treasury"], dict_input["entry_fee"], dict_input["invite_string"],
                            dict_input["date_created"], dict_input["tech_attack"], dict_input["tech_defence"], dict_input["name"], dict_input["level"], dict_input["tech_tree"], dict_input["type"],
                            dict_input["size"], dict_input["wins"], dict_input["losses"], dict_input["experience"], input_data])
        elif get_string is 'id':
            cursor.execute("UPDATE conquest SET founderid=?, leaderid=?, treasury=?, entry_fee=?, invite_string=?, date_created=?, tech_attack=?, tech_defence=?, name=?, level=?, tech_tree=?, type=?, size=?, wins=?, losses=?, experience=? WHERE settlement_id=?",
                            [dict_input["founderid"], dict_input["leaderid"], dict_input["treasury"], dict_input["entry_fee"], dict_input["invite_string"],
                            dict_input["date_created"], dict_input["tech_attack"], dict_input["tech_defence"], dict_input["name"], dict_input["level"], dict_input["tech_tree"], dict_input["type"],
                            dict_input["size"], dict_input["wins"], dict_input["losses"], dict_input["experience"], input_data])
    return None

async def conquest_delete_settlement(input_id: str):
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("DELETE FROM conquest WHERE settlement_id=?", (input_id,))

async def conquest_get_leaderboard():
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("SELECT settlement_id, name, experience FROM conquest ORDER BY experience DESC")
        db_output = cursor.fetchall()
        if db_output != None:
            db_output = list(db_output)
        return db_output

async def conquest_add_member(user: discord.User, settlement_id: int):
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("INSERT OR IGNORE INTO members(userid, settlement_id) VALUES(?, ?)", (user.id, None))
        cursor.execute("UPDATE members SET settlement_id=? WHERE userid=?", (settlement_id, user.id))

async def conquest_remove_member(user: discord.User):
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("UPDATE members SET settlement_id=? WHERE userid=?", (None, user.id))

async def conquest_get_settlementid(user: discord.User):
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("INSERT OR IGNORE INTO members(userid, settlement_id) VALUES(?, ?)", (user.id, None))
        cursor.execute("SELECT settlement_id FROM members WHERE userid=?", (user.id,))
        db_output = cursor.fetchone()
        return db_output[0] if db_output != None else None

async def conquest_find_member(user: discord.User, settlement_id: int = None):
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("INSERT OR IGNORE INTO members(userid, settlement_id) VALUES(?, ?)", (user.id, None))
        if settlement_id:
            cursor.execute("SELECT userid FROM members WHERE settlement_id=?", (settlement_id,))
        else: 
            cursor.execute("SELECT settlement_id FROM members WHERE userid=?", (user.id,))
        db_output = cursor.fetchone()
        
        if settlement_id:
            return True if db_output != None else False
        else:
            return True if None not in {db_output, db_output[0]} else False

async def conquest_find_code(input: str):
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("SELECT invite_string FROM conquest WHERE invite_string=?", (input,))
        db_output = cursor.fetchone()
        return db_output[0] if db_output != None else None

async def conquest_new_code(new_code: str, userID : str):
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("UPDATE conquest SET invite_string=? WHERE founderid=? OR leaderid=?", (new_code, userID, userID,))
        return True if cursor.rowcount > 0 else False

async def conquest_get_resources(settlement_id: int):
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("INSERT OR IGNORE INTO resources(settlement_id, cloth, wood, stone, food) VALUES(?, ?, ?, ?, ?)", (settlement_id, '0', '0', '0', '0',))
        cursor.execute("SELECT * FROM resources WHERE settlement_id=?", (settlement_id,))
        db_output = cursor.fetchone()
        if db_output is None:
            return None
        else:
            db_output = list(db_output)
            return_dict = dict(settlement_id=db_output[0], cloth=db_output[1], wood=db_output[2], stone=db_output[3], food=db_output[4])
            return return_dict

async def conquest_set_resources(settlement_id: int, dict_input):
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("UPDATE resources SET cloth=?, wood=?, stone=?, food=? WHERE settlement_id=?",
                      (dict_input["cloth"], dict_input["wood"], dict_input["stone"], dict_input["food"], settlement_id,))
        return True if cursor.rowcount > 0 else False

async def conquest_get_building(building_id: int):
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("SELECT * FROM buildings WHERE id=?", (building_id,))
        db_output = cursor.fetchone()
        if db_output is None:
            return None
        else:
            db_output = list(db_output)
            return_dict = dict(id=db_output[0], name=db_output[1], cloth=db_output[2], food=db_output[3], stone=db_output[4], wood=db_output[5], gold=db_output[6])
            return return_dict

async def conquest_get_buildings():
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM buildings")
        db_output = [dict(row) for row in cursor.fetchall()]
        return db_output

async def conquest_building_upgrade(settlement_id: int , building_id: int):
    with ContextManager('./databases/conquest.db') as cursor:
        cursor.execute("SELECT tech_attack, tech_defence, tech_tree FROM conquest WHERE settlement_id=?", (settlement_id,))
        tech_points = cursor.fetchone()
        if tech_points:
            tech_points = list(tech_points)
            level = int(tech_points[2][building_id-1]) if tech_points[2][building_id-1] != "X" else 10
            new_points = int(pow(1.638, level))
            if building_id == 2:
                tech_points[0] += new_points
            elif building_id == 4:
                tech_points[1] += new_points
            elif building_id == 10:
                new_points = int(pow(1.48, level))
                tech_points[0] += new_points
                tech_points[1] += new_points
            cursor.execute("UPDATE conquest SET tech_attack=?, tech_defence=? WHERE settlement_id=?", (tech_points[0], tech_points[1], settlement_id,))

async def conquest_daily_resources():
    conn = sqlite3.connect('./databases/conquest.db')
    cursor = conn.cursor()
    cursor_update = conn.cursor()
    cursor.row_factory = sqlite3.Row
    for row in cursor.execute("SELECT r.settlement_id, r.cloth, r.wood, r.stone, r.food, c.tech_tree FROM resources AS r INNER JOIN conquest AS c ON r.settlement_id=c.settlement_id"):
        row_info = list(row)
        tech_tree = row_info[5]
        #5 = quarry; 6 = farms ; 7 = weavery; 8 = lumberjack; 9 = warehouse
        level_quarry = int(tech_tree[4]) if tech_tree[4] != "X" else 10
        level_farms = int(tech_tree[5]) if tech_tree[4] != "X" else 10
        level_weavery = int(tech_tree[6]) if tech_tree[4] != "X" else 10
        level_lumberjack = int(tech_tree[7]) if tech_tree[4] != "X" else 10
        row_info[1] += pow(level_weavery, 2)
        row_info[2] += pow(level_lumberjack, 2)
        row_info[3] += pow(level_quarry, 2)
        row_info[4] += pow(level_farms, 2)
        if int(tech_tree[8]) == 0:
            row_info[1] = row_info[1] if row_info[1] <= 1000 else 1000
            row_info[2] = row_info[2] if row_info[2] <= 1000 else 1000
            row_info[3] = row_info[3] if row_info[3] <= 1000 else 1000
            row_info[4] = row_info[4] if row_info[4] <= 1000 else 1000
        cursor_update.execute("UPDATE resources SET cloth=?, wood=?, stone=?, food=? WHERE settlement_id=?", (row_info[1], row_info[2], row_info[3], row_info[4], row_info[0]))
    conn.commit()
    conn.close()

#Giveaway (Economy)

async def start_giveaway(msg_id: int, value: int):
    with ContextManager('./databases/users.db') as cursor:
        cursor.execute("INSERT OR IGNORE INTO giveaways(msgid, value) VALUES(?, ?)", (msg_id, value,))

async def get_giveaway_value(msg_id: int):
    with ContextManager('./databases/users.db') as cursor:
        cursor.execute("SELECT value FROM giveaways WHERE msgid=?", (msg_id,))
        db_output = cursor.fetchone()
        if db_output:
            db_output = list(db_output)
            return db_output[0] if db_output else None
        else:
            return None

async def get_giveaway_list():
    with ContextManager('./databases/users.db') as cursor:
        cursor.execute("SELECT msgid FROM giveaways")
        db_output = cursor.fetchall()
        return list(db_output[0]) if db_output else None

async def has_entered_giveaway(user_id: int, msg_id: int):
    with ContextManager('./databases/users.db') as cursor:
        cursor.execute("SELECT ID FROM giveaways WHERE msgid=?", (msg_id,))
        check = cursor.fetchone()
        if check:
            cursor.execute("SELECT ID FROM giveaway_participants WHERE userid=? AND msgid=?", (user_id, msg_id,))
            db_output = cursor.fetchone()
            return True if db_output else False
        else:
            return None

async def enter_giveaway(user_id: int, msg_id: int):
    with ContextManager('./databases/users.db') as cursor:
        cursor.execute("INSERT OR IGNORE INTO giveaway_participants(userid, msgid) VALUES(?, ?)", (user_id, msg_id,))

async def end_giveaway(msg_id: int):
    with ContextManager('./databases/users.db') as cursor:
        cursor.execute("DELETE FROM giveaway_participants WHERE msgid=?", (msg_id,))
        cursor.execute("DELETE FROM giveaways WHERE msgid=?", (msg_id,))
        result = cursor.rowcount
        return True if result > 0 else False