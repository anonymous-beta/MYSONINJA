#!/usr/bin/env python3
import os
import sys
import time
import threading
import webbrowser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.banner import show_banner
from web.app import socketio, app
from core.database import init_db

def startup_sequence():
    os.system('clear' if os.name == 'posix' else 'cls')
    show_banner()
    print("\n" + "═" * 60)
    print("  MYSŌNINJA v4.0 — STANDALONE ARSENAL")
    print("  ⚔️  Kill Chain: RECON → WEAPONIZE → DELIVER → EXPLOIT → PERSIST → C2 → EXFIL")
    print("═" * 60 + "\n")

def open_browser():
    time.sleep(2)
    try:
        webbrowser.open('http://127.0.0.1:5000')
    except:
        pass

def main():
    startup_sequence()
    init_db()
    threading.Thread(target=open_browser, daemon=True).start()
    print("🌐 War Room: http://127.0.0.1:5000")
    print("⌨️  Ctrl+C to stop\n")
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)

if __name__ == '__main__':
    main()
