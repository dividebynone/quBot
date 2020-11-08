from libs.sqlhandler import sqlconnect
import main
import os


class ProfilesHandler(object):

    def __init__(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS profiles(user_id INTEGER, guild_id INTEGER, experience INTEGER, level INTEGER, background INTEGER, bio BLOB, PRIMARY KEY (user_id, guild_id))")

    @classmethod
    async def get(self, user_id: int, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO profiles (user_id, guild_id) VALUES(?, ?)", (user_id, guild_id,))
            cursor.execute("SELECT IFNULL(experience, 0), IFNULL(level, 0), background, bio FROM profiles WHERE user_id=? AND guild_id=?", (user_id, guild_id,))
            output = cursor.fetchone()
            if not output:
                return None
            else:
                output = list(output)
                return_dict = dict(experience=output[0], level=output[1], background=output[2], bio=output[3])
                return return_dict

    @classmethod
    async def set_bio(self, user_id: int, guild_id: int, bio: str):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO profiles (user_id, guild_id) VALUES(?, ?)", (user_id, guild_id,))
            cursor.execute("UPDATE profiles SET bio=? WHERE user_id=? AND guild_id=?", (bio, user_id, guild_id,))

    @classmethod
    async def get_bio(self, user_id: int, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT bio FROM profiles WHERE user_id=? AND guild_id=?", (user_id, guild_id,))
            output = cursor.fetchone()
            return output[0] if output else None

    @classmethod
    async def get_rank(self, user_id: int, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT rank FROM (SELECT user_id, DENSE_RANK() OVER (ORDER BY level DESC, experience DESC) as rank FROM profiles WHERE guild_id=?) as p WHERE p.user_id=?", (guild_id, user_id,))
            output = cursor.fetchone()
            return output[0] if output else None

    @classmethod
    async def leaderboard(self, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT user_id, DENSE_RANK() OVER (ORDER BY level DESC, experience DESC) as rank, IFNULL(level, 0), IFNULL(experience, 0) FROM profiles WHERE guild_id=?", (guild_id,))
            output = cursor.fetchall()
            return output

    @classmethod
    async def reset_leveling(self, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("UPDATE profiles SET level=?, experience=? WHERE guild_id=?", (None, None, guild_id,))

    @classmethod
    async def equip_background(self, user_id: int, guild_id: int, new_background):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO profiles (user_id, guild_id) VALUES(?, ?)", (user_id, guild_id,))
            cursor.execute("UPDATE profiles SET background=? WHERE user_id=? AND guild_id=?", (new_background, user_id, guild_id,))

    @classmethod
    async def get_experience(self, user_id: int, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT IFNULL(experience, 0) FROM profiles WHERE user_id=? AND guild_id=?", (user_id, guild_id,))
            output = cursor.fetchone()
            return output[0] if output else 0

    @classmethod
    async def update_experience(self, user_id: int, guild_id: int, user_data: dict):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO profiles (user_id, guild_id) VALUES(?, ?)", (user_id, guild_id,))
            cursor.execute("UPDATE profiles SET experience=?, level=? WHERE user_id=? AND guild_id=?", (user_data['experience'], user_data['level'], user_id, guild_id,))


class ProfileBackgrounds(object):

    def __init__(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS profile_backgrounds (bg_id INTEGER PRIMARY KEY, description TEXT, price INTEGER, category BLOB, thumbnail_url BLOB)")
            cursor.execute("CREATE TABLE IF NOT EXISTS unlocked_backgrounds (user_id INTEGER, background INTEGER, PRIMARY KEY (user_id, background))")

            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (1, "A black and white background featuring Dio Brando from the popular anime **JoJo no Kimyou na Bouken (JoJo's Bizarre Adventure)**", 5000, "Anime", "https://i.imgur.com/32fo4T5.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (2, "An anime themed background featuring Shinobu Kochou from the popular anime **Kimetsu no Yaiba (Demon Slayer)**", 5000, "Anime", "https://i.imgur.com/i455i2C.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (3, "An anime themed background featuring the main characters from the popular anime **Made in Abyss**", 5000, "Anime", "https://i.imgur.com/nuw9Bli.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (4, "An anime themed background featuring Artoria Pendragon(Saber)  from the popular anime franchise **Fate**", 5000, "Anime", "https://i.imgur.com/BPKoNFp.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (5, "Frames (White) - Abstract grid background", 1000, "General", "https://i.imgur.com/Si7FfJf.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (6, "Frames (Red) - Abstract grid background", 1000, "General", "https://i.imgur.com/zgPWZ60.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (7, "Frames (Lime Green) - Abstract grid background", 1000, "General", "https://i.imgur.com/EkbvzQh.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (8, "Frames (Pink) - Abstract grid background", 1000, "General", "https://i.imgur.com/7iDpoRv.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (9, "Frames (Cyan) - Abstract grid background", 1000, "General", "https://i.imgur.com/SJLEMwM.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (10, "Frames (Orange) - Abstract grid background", 1000, "General", "https://i.imgur.com/VdkDpMw.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (11, "Frames (Black) - Abstract grid background", 1000, "General", "https://i.imgur.com/2jULgOI.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (12, "Canvas #1 (Red/Blue/White) - Abstract canvas paint background", 1000, "General", "https://i.imgur.com/sbiiDo4.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (13, "Canvas #2 (Purple/Light Blue/White) - Abstract canvas paint background", 1000, "General", "https://i.imgur.com/rQ6mRPe.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (14, "Mountain Peaks (Red/Black) - Simplistic sketch-style background", 2500, "General", "https://i.imgur.com/6MTwXQY.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (15, "Mountain Peaks (Purple/Black) - A simplistic sketch-style background", 2500, "General", "https://i.imgur.com/auMuqIj.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (16, "Mountain Peaks (Green/Black) - A simplistic sketch-style background", 2500, "General", "https://i.imgur.com/YRkvokM.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (17, "A blue and dark gray abstract background featuring dots that form sun rays.", 2500, "General", "https://i.imgur.com/8DZvwfn.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (18, "A black and white nature background featuring a group of leaves leaning on an empty canvas", 2500, "General", "https://i.imgur.com/lnoj58Q.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (19, "A background drawing of a colourful green field.", 1000, "General", "https://i.imgur.com/LOmp1RC.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (20, "Koi Fish (Gold/Dark Gray) - Background featuring a koi fish pattern.", 100000, "General", "https://i.imgur.com/LOmp1RC.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (21, "Koi Fish (Red/Dark Gray) - Background featuring a koi fish pattern.", 25000, "General", "https://i.imgur.com/g4R6H6W.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (22, "Koi Fish (Cyan/Dark Gray) - Background featuring a koi fish pattern.", 25000, "General", "https://i.imgur.com/mhXwflE.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (23, "Koi Fish (Purple/Dark Gray) - Background featuring a koi fish pattern.", 25000, "General", "https://i.imgur.com/H3oF9rz.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (24, "Summer Days - Background featuring two anime style characters looking at the cloudy sky.", 5000, "Anime", "https://i.imgur.com/xfMSi7E.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (25, "City Ruins #1 - Background featuring a flooded and abandoned city street.", 1000, "Anime", "https://i.imgur.com/xoK5qeR.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (26, "Summer Vibes - An abstract background with colourful silhouettes.", 2500, "General", "https://i.imgur.com/xoK5qeR.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (27, "Dusk - A colourful and simplistic background of a hill during the late hours of the day.", 1000, "General", "https://i.imgur.com/4FPwimt.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (28, "An anime themed background featuring a cheerful girl.", 1000, "Anime", "https://i.imgur.com/ZbhgjyR.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (29, "Melancholy - A simplistic background with colourful silhouettes.", 2500, "General", "https://i.imgur.com/Ni7eKmS.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (30, "An anime themed background featuring two girls with playing cards.", 1000, "Anime", "https://i.imgur.com/1RRHBG4.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (31, "A background displaying a bamboo forest", 1000, "Nature", "https://i.imgur.com/51Ylo85.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (32, "Palm Tree Sunset (Pink/Gray) - A background of a row of palm trees and the sunset", 2500, "Nature", "https://i.imgur.com/wJITQAQ.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (33, "Palm Tree Sunset (Purple/Gray) - A background of a row of palm trees and the sunset", 2500, "Nature", "https://i.imgur.com/rKv8Qea.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (34, "Canyon Overdrive (Orange) - A simplistic background of a sunset in a canyon with a synthwave-like aesthetic", 5000, "Nature", "https://i.imgur.com/MagF8X6.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (35, "Canyon Overdrive (Purple) - A simplistic background of a sunset in a canyon with a synthwave-like aesthetic", 5000, "Nature", "https://i.imgur.com/TBU6rCF.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (36, "The Grid (Red/Black) - A simplistic background of a horizontal flat plane with synthwave-like aesthetic", 2500, "General", "https://i.imgur.com/fnikryx.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (37, "The Moon (Cyan/Dark Gray) - A simplistic background of the moon", 1000, "General", "https://i.imgur.com/6DjTdWW.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (38, "The Moon (Red/Dark Gray) - A simplistic background of the moon", 2500, "General", "https://i.imgur.com/JwNMqts.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (39, "The Moon (Pink/Dark Gray) - A simplistic background of the moon", 1000, "General", "https://i.imgur.com/gzQHPhp.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (40, "A background of a street that resembles an early photograph from the early 20th century.", 1000, "Lifestyle", "https://i.imgur.com/ONE8hC7.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (41, "Tropical Summer (Cyan) - A background of palm trees and a straw umbrella", 5000, "Nature", "https://i.imgur.com/9pdAKWq.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (42, "Tropical Summer (Red) - A background of palm trees and a straw umbrella", 5000, "Nature", "https://i.imgur.com/FuwNGGQ.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (43, "Tropical Summer (Yellow) - A background of palm trees and a straw umbrella", 5000, "Nature", "https://i.imgur.com/enN37qa.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (44, "A gaming themed background featuring 2B from the popular video game **Nier:Automata**", 5000, "Games", "https://i.imgur.com/iGprLqc.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (45, "A gaming themed background featuring Gerald of Rivia from the popular video game franchise **The Witcher**", 2500, "Games", "https://i.imgur.com/HaLxifI.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (46, "A gaming themed background of a scenery taken from the popular video game **Minecraft**", 1000, "Games", "https://i.imgur.com/k0AzAxL.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (47, "A gaming themed background featuring the main characters Saurfang, Nathanos & Sylvanas from the Burning of Teldrassil, **World of Warcraft**", 5000, "Games", "https://i.imgur.com/4ACowh9.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (48, "A gaming themed background of a scenery taken from the popular video game **Dark Souls 3**", 2500, "Games", "https://i.imgur.com/mV0NDb7.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (49, "An anime themed background featuring Eren Yeager from the popular anime **Shingeki no Kyojin (Attack on Titan)**", 5000, "Anime", "https://i.imgur.com/DgI5eqe.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (50, "An anime themed background featuring part of the main cast from the popular anime **Steins;Gate**", 25000, "Anime", "https://i.imgur.com/tdNp4KH.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (51, "An anime themed background featuring short-haired Shinobu Oshino from the popular anime **Monogatari**", 5000, "Anime", "https://i.imgur.com/iTKuDJP.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (52, "A background of a wood flooring", 1000, "Lifestyle", "https://i.imgur.com/0DXkgUu.png"))
            cursor.execute("INSERT OR IGNORE INTO profile_backgrounds (bg_id, description, price, category, thumbnail_url) VALUES (?, ?, ?, ?, ?)",
                           (53, "Coffee Beans (Dark Gray) - A background of coffee beans on a dark gray surface", 5000, "Lifestyle", "https://i.imgur.com/NVTfQqn.png"))

            print("[Profiles] Successfully loaded all available profile background.")

    @classmethod
    async def get_background_info(self, bg_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT description, price, category, thumbnail_url FROM profile_backgrounds WHERE bg_id=?", (bg_id,))
            output = cursor.fetchone()
            if not output:
                return None
            else:
                output = list(output)
                return_dict = dict(description=output[0], price=output[1], category=output[2], url=output[3])
                return return_dict

    @classmethod
    async def get_category(self, category: str):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            output = None
            if category.capitalize() == "All":
                cursor.execute("SELECT bg_id, description, price FROM profile_backgrounds")
                output = cursor.fetchall()
            else:
                cursor.execute("SELECT bg_id, description, price FROM profile_backgrounds WHERE category=?", (category,))
                output = cursor.fetchall()
            return output

    @classmethod
    async def get_categories(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT DISTINCT category FROM profile_backgrounds")
            output = cursor.fetchall()
            return [x[0] for x in output] if output else None

    @classmethod
    async def unlocked_backgrounds(self, user_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT background FROM unlocked_backgrounds WHERE user_id=?", (user_id,))
            output = cursor.fetchall()
            return [x[0] for x in output] if output else None

    @classmethod
    async def user_backgrounds(self, user_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("SELECT ub.background, pb.description FROM unlocked_backgrounds as ub INNER JOIN profile_backgrounds as pb ON ub.background = pb.bg_id WHERE ub.user_id=?", (user_id,))
            output = cursor.fetchall()
            return output

    @classmethod
    async def unlock_background(self, user_id: int, bg_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'users.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO unlocked_backgrounds (user_id, background) VALUES(?, ?)", (user_id, bg_id,))


class LevelingToggle(object):

    def __init__(self):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS disabled_leveling (guild_id INTEGER PRIMARY KEY)")

    @classmethod
    async def disable_leveling(self, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO disabled_leveling (guild_id) VALUES(?)", (guild_id,))

    @classmethod
    def is_disabled(self, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("SELECT guild_id FROM disabled_leveling WHERE guild_id=?", (guild_id,))
            output = cursor.fetchone()
            return True if output else False

    @classmethod
    async def enable_leveling(self, guild_id: int):
        with sqlconnect(os.path.join(main.bot_path, 'databases', 'servers.db')) as cursor:
            cursor.execute("DELETE FROM disabled_leveling WHERE guild_id=?", (guild_id,))
