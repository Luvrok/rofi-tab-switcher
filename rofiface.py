#!/usr/bin/env python3
import json
import os
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

def format_tab(tab):
    return (u"%s <span alpha='50%%'>%s</span>\n"
            % (escape(tab.get("title", "<untitled>")),
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

