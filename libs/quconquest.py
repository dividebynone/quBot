from libs.SQLConnectionHandler import ConnectionHandler
from libs.qulib import string_generator
import sqlite3
import discord
import random
import string
import json

class quConquest(object):

    @staticmethod
    def database_init():
        with ConnectionHandler('./databases/conquest.db') as cursor:
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

    @staticmethod
    async def level_converter(item: str):
        return int(item) if item != "X" else 10

    @staticmethod
    async def get_settlement(get_string:str, input_data):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            if get_string is 'user':
                cursor.execute("SELECT * FROM conquest WHERE founderid=? OR leaderid=?", (input_data,input_data,))
            elif get_string is 'settlement':
                cursor.execute("SELECT * FROM conquest WHERE name=?", (input_data,))
            elif get_string is 'code':
                cursor.execute("SELECT * FROM conquest WHERE invite_string=?", (input_data,))
            elif get_string is 'id':
                cursor.execute("SELECT * FROM conquest WHERE settlement_id=?", (input_data,))
            else:
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

    @staticmethod
    async def create_settlement(input_data, dict_input):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("INSERT OR IGNORE INTO conquest(founderid, leaderid, treasury, entry_fee, invite_string, date_created, tech_attack, tech_defence, name, level, tech_tree, type, size, wins, losses, experience) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                [input_data, input_data, dict_input["entry_fee"], dict_input["entry_fee"], dict_input["invite_string"],
                                dict_input["date_created"], '0', '0', dict_input["name"],'1', '0000000000', dict_input["type"], '1', 0, 0, 0])
            return cursor.lastrowid

    @staticmethod
    async def update_settlement(get_string:str, input_data, dict_input):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            if get_string is 'user':
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

    @staticmethod
    async def delete_settlement(input_id: str):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("DELETE FROM conquest WHERE settlement_id=?", (input_id,))

    @staticmethod
    async def get_leaderboard():
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("SELECT settlement_id, name, experience FROM conquest ORDER BY experience DESC")
            db_output = cursor.fetchall()
            return list(db_output) if db_output != None else None

    @staticmethod
    async def add_member(user_id: str, settlement_id: int):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("INSERT OR IGNORE INTO members(userid, settlement_id) VALUES(?, ?)", (user_id, None))
            cursor.execute("UPDATE members SET settlement_id=? WHERE userid=?", (settlement_id, user_id))

    @staticmethod
    async def remove_member(user_id: str):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("UPDATE members SET settlement_id=? WHERE userid=?", (None, user_id))

    @staticmethod
    async def find_member(user_id: str, settlement_id: int = None):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("INSERT OR IGNORE INTO members(userid, settlement_id) VALUES(?, ?)", (user_id, None))
            if settlement_id:
                cursor.execute("SELECT userid FROM members WHERE settlement_id=?", (settlement_id,))
            else: 
                cursor.execute("SELECT settlement_id FROM members WHERE userid=?", (user_id,))
            db_output = cursor.fetchone()
            
            if settlement_id:
                return True if db_output != None else False
            else:
                return True if None not in {db_output, db_output[0]} else False

    @staticmethod
    async def get_settlement_id(user_id: str):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("INSERT OR IGNORE INTO members(userid, settlement_id) VALUES(?, ?)", (user_id, None))
            cursor.execute("SELECT settlement_id FROM members WHERE userid=?", (user_id,))
            db_output = cursor.fetchone()
            return db_output[0] if db_output != None else None

    @staticmethod
    async def generate_new_code(user_id: str):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            new_code = string_generator(15)
            cursor.execute("SELECT invite_string FROM conquest WHERE invite_string=?", (new_code,))

            while cursor.fetchone():
                new_code = string_generator(15)
                cursor.execute("SELECT invite_string FROM conquest WHERE invite_string=?", (new_code,))

            cursor.execute("UPDATE conquest SET invite_string=? WHERE founderid=? OR leaderid=?", (new_code, user_id, user_id,))
            return True if cursor.rowcount > 0 else False
    
    @staticmethod
    async def get_unique_code():
        with ConnectionHandler('./databases/conquest.db') as cursor:
            new_code = string_generator(15)
            cursor.execute("SELECT invite_string FROM conquest WHERE invite_string=?", (new_code,))

            while cursor.fetchone():
                new_code = string_generator(15)
                cursor.execute("SELECT invite_string FROM conquest WHERE invite_string=?", (new_code,))

            return new_code
    @staticmethod
    async def get_code(user_id: str):
       with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("SELECT invite_string FROM conquest WHERE founderid=? OR leaderid=?", (user_id, user_id,))
            db_output = cursor.fetchone()
            return db_output[0] if db_output != None else None

    @staticmethod
    async def get_resources(settlement_id: int):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("INSERT OR IGNORE INTO resources(settlement_id, cloth, wood, stone, food) VALUES(?, ?, ?, ?, ?)", (settlement_id, 0, 0, 0, 0,))
            cursor.execute("SELECT * FROM resources WHERE settlement_id=?", (settlement_id,))
            db_output = cursor.fetchone()
            if db_output is None:
                return None
            else:
                db_output = list(db_output)
                return_dict = dict(settlement_id=db_output[0], cloth=db_output[1], wood=db_output[2], stone=db_output[3], food=db_output[4])
                return return_dict
    
    @staticmethod
    async def update_resources(settlement_id: int, dict_input):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("UPDATE resources SET cloth=?, wood=?, stone=?, food=? WHERE settlement_id=?",
                        (dict_input["cloth"], dict_input["wood"], dict_input["stone"], dict_input["food"], settlement_id,))
            return True if cursor.rowcount > 0 else False

    @staticmethod
    async def send_resource_dailies():
        conn = sqlite3.connect('./databases/conquest.db')
        cursor = conn.cursor()
        cursor_update = conn.cursor()
        cursor.row_factory = sqlite3.Row
        for row in cursor.execute("SELECT r.settlement_id, r.cloth, r.wood, r.stone, r.food, c.tech_tree FROM resources AS r INNER JOIN conquest AS c ON r.settlement_id=c.settlement_id"):
            row_info = list(row)
            tech_tree = row_info[5]
            #Indexes: 4 = quarry; 5 = farms ; 6 = weavery; 7 = lumberjack; 8 = warehouse
            for i in range(1, 5):
                row_info[i] += pow(await quConquest.level_converter(tech_tree[3+i]), 2)
                if int(tech_tree[8]) == 0:
                    row_info[i] = row_info[i] if row_info[i] <= 1000 else 1000
            cursor_update.execute("UPDATE resources SET cloth=?, wood=?, stone=?, food=? WHERE settlement_id=?", (row_info[1], row_info[2], row_info[3], row_info[4], row_info[0]))
        conn.commit()
        conn.close()

    @staticmethod
    async def get_resource_production_rate(building_id: int, settlement_id: int):
        if 5 <= building_id <= 8:
            with ConnectionHandler('./databases/conquest.db') as cursor:
                cursor.execute("SELECT tech_tree FROM conquest WHERE settlement_id=?", (settlement_id,))
                db_output = cursor.fetchone()
                if db_output is None:
                    return None
                else:
                    tech_tree = db_output[0]
                    return pow(await quConquest.level_converter(tech_tree[building_id-1]), 2)

    @staticmethod
    async def get_building(building_id: int):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("SELECT * FROM buildings WHERE id=?", (building_id,))
            db_output = cursor.fetchone()
            if db_output is None:
                return None
            else:
                db_output = list(db_output)
                return_dict = dict(id=db_output[0], name=db_output[1], cloth=db_output[2], food=db_output[3], stone=db_output[4], wood=db_output[5], gold=db_output[6])
                return return_dict

    @staticmethod
    async def get_buildings():
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM buildings")
            db_output = [dict(row) for row in cursor.fetchall()]
            return db_output

    @staticmethod
    async def upgrade_building(settlement_id: int , building_id: int):
        with ConnectionHandler('./databases/conquest.db') as cursor:
            cursor.execute("SELECT tech_attack, tech_defence, tech_tree FROM conquest WHERE settlement_id=?", (settlement_id,))
            tech_points = cursor.fetchone()
            if tech_points:
                tech_points = list(tech_points)
                level = await quConquest.level_converter(tech_points[2][building_id-1])
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