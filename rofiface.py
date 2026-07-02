#!/usr/bin/env python3
import json
import os
import random
import struct
import subprocess
import sys
from xml.sax.saxutils import escape

# --- native messaging I/O ---

def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) < 4:
        sys.exit(0)
    (length,) = struct.unpack("=I", raw_length)
    data = b""
    while len(data) < length:
        chunk = sys.stdin.buffer.read(length - len(data))
        if not chunk:
            sys.exit(0)
        data += chunk
    return json.loads(data)

def send_message(content):
    data = json.dumps(content).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("=I", len(data)))  # длина в БАЙТАХ
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()

# --- rofi ---

colors = ["AliceBlue","AntiqueWhite","Aqua","Aquamarine","Azure","Beige","Bisque","BlanchedAlmond","Blue","BlueViolet","Brown","BurlyWood","CadetBlue","Chartreuse","Chocolate","Coral","CornflowerBlue","Cornsilk","Crimson","Cyan","DarkBlue","DarkCyan","DarkGoldenRod","DarkGray","DarkGrey","DarkGreen","DarkKhaki","DarkMagenta","DarkOliveGreen","Darkorange","DarkOrchid","DarkRed","DarkSalmon","DarkSeaGreen","DarkSlateBlue","DarkSlateGray","DarkSlateGrey","DarkTurquoise","DarkViolet","DeepPink","DeepSkyBlue","DimGray","DimGrey","DodgerBlue","FireBrick","FloralWhite","ForestGreen","Fuchsia","Gainsboro","GhostWhite","Gold","GoldenRod","Gray","Grey","Green","GreenYellow","HoneyDew","HotPink","IndianRed","Indigo","Ivory","Khaki","Lavender","LavenderBlush","LawnGreen","LemonChiffon","LightBlue","LightCoral","LightCyan","LightGoldenRodYellow","LightGray","LightGrey","LightGreen","LightPink","LightSalmon","LightSeaGreen","LightSkyBlue","LightSlateGray","LightSlateGrey","LightSteelBlue","LightYellow","Lime","LimeGreen","Linen","Magenta","Maroon","MediumAquaMarine","MediumBlue","MediumOrchid","MediumPurple","MediumSeaGreen","MediumSlateBlue","MediumSpringGreen","MediumTurquoise","MediumVioletRed","MidnightBlue","MintCream","MistyRose","Moccasin","NavajoWhite","Navy","OldLace","Olive","OliveDrab","Orange","OrangeRed","Orchid","PaleGoldenRod","PaleGreen","PaleTurquoise","PaleVioletRed","PapayaWhip","PeachPuff","Peru","Pink","Plum","PowderBlue","Purple","Red","RosyBrown","RoyalBlue","SaddleBrown","Salmon","SandyBrown","SeaGreen","SeaShell","Sienna","Silver","SkyBlue","SlateBlue","SlateGray","SlateGrey","Snow","SpringGreen","SteelBlue","Tan","Teal","Thistle","Tomato","Turquoise","Violet","Wheat","Yellow","YellowGreen"]
colormap = {}

def get_color(win_id):
    if win_id not in colormap:
        colormap[win_id] = random.choice(colors)
    return colormap[win_id]

def format_tab(tab):
    win = tab.get("window", -1)
    return (u"<span color='%s'>(%d)</span>\t%s <span alpha='50%%'>%s</span>\n"
            % (get_color(win), win,
               escape(tab.get("title", "<untitled>")),
               escape(tab.get("url", "<undefined>"))))

def theme_args():
    theme = os.environ.get("ROFI_TAB_SWITCHER_THEME")
    if not theme:
        cfg = os.path.join(
            os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
            "rofi-tab-switcher", "theme.rasi")
        theme = cfg if os.path.exists(cfg) else None
    return ["-theme", theme] if theme else []

def pick_tab(message):
    cmd = ["rofi", "-dmenu", "-i", "-scroll-method", "1", "-format", "i",
           "-p", "Go to tab", "-markup-rows", "-no-custom",
           "-selected-row", str(max(message.get("active", 0), 0))]
    cmd += theme_args()
    rofi = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, _ = rofi.communicate(u"".join(map(format_tab, message["tabs"])).encode("utf-8"))
    return out.strip()

# --- main ---

def main():
    while True:
        message = get_message()
        out = pick_tab(message)
        if out:
            send_message(message["tabs"][int(out)]["id"])

if __name__ == "__main__":
    main()

