from main import bot_path
import math
import json
import os


def get_color(color: str):
    with open(os.path.join(bot_path, 'data', 'colors.json'), 'r') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    color_lowered = color.lower()
    for entry in json_data:
        if entry['name'].lower() == color_lowered:
            return entry["hex"]
            break


def calculate_hsp(hex: str):
    hex_stripped = hex.lstrip('#')
    RGB = tuple(int(hex_stripped[i:i+2], 16) for i in (0, 2, 4))  # noqa: E226
    return math.sqrt(0.299 * pow(RGB[0], 2) + 0.587 * pow(RGB[1], 2) + 0.114 * pow(RGB[2], 2))


def calculate_luminance(hex: str):
    hex_stripped = hex.lstrip('#')
    RGB = tuple(int(hex_stripped[i:i+2], 16) for i in (0, 2, 4))  # noqa: E226
    return (0.2126 * RGB[0] + 0.7152 * RGB[1] + 0.0722 * RGB[2])
