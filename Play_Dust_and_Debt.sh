#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo 'Python 3 is required. On Arch Linux: sudo pacman -S python tk'
  read -r -p 'Press Enter to exit...'
  exit 1
fi
if ! python3 -c 'import tkinter' >/dev/null 2>&1; then
  echo 'Python Tkinter is missing. On Arch Linux: sudo pacman -S tk'
  read -r -p 'Press Enter to exit...'
  exit 1
fi
exec python3 game.py
