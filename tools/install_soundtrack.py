#!/usr/bin/env python3
"""Install user's Dust & Debt M4A recordings from a local folder.

Usage:
  python tools/install_soundtrack.py ~/Music/Dust-and-Debt

Files retain their original names and are copied to assets/audio/music.
No audio is downloaded, synthesized, renamed or changed.
"""
import argparse
import os
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from soundtrack_manifest import SOURCE_FILES

def install(source, destination, replace=False):
    source=Path(source).expanduser().resolve()
    dest=Path(destination).expanduser().resolve()
    if not source.is_dir():
        raise ValueError("No such soundtrack folder: "+str(source))
    dest.mkdir(parents=True,exist_ok=True)
    installed=[]
    skipped=[]
    missing=[]
    for title in SOURCE_FILES:
        path=source/title
        # Allow the duplicate name exported by ChatGPT's earlier upload.
        if title=="Forsaken to This Land.m4a" and not path.is_file():
            alternate=source/"Forsaken to This Land(1).m4a"
            if alternate.is_file():path=alternate
        target=dest/title
        if not path.is_file():
            if target.is_file():skipped.append(title)
            else:missing.append(title)
            continue
        if target.is_file() and not replace:
            skipped.append(title)
            continue
        if path==target:
            skipped.append(title)
            continue
        shutil.copy2(path,target)
        installed.append(title)
    return installed,skipped,missing

def main():
    parser=argparse.ArgumentParser(description="Install original Dust & Debt soundtrack M4As")
    parser.add_argument("source",help="Folder containing the actual .m4a files")
    parser.add_argument("--destination",default=str(ROOT/"assets"/"audio"/"music"))
    parser.add_argument("--replace",action="store_true",help="Replace existing tracks")
    args=parser.parse_args()
    try:installed,skipped,missing=install(args.source,args.destination,args.replace)
    except (OSError,ValueError) as ex:
        parser.error(str(ex))
    print(f"Installed {len(installed)} original M4A tracks; {len(skipped)} already present; {len(missing)} missing.")
    for title in missing:print("Missing:",title)
    if missing:print("Copy the missing recordings into your source folder and rerun.")
    print("Destination:",os.path.abspath(os.path.expanduser(args.destination)))

if __name__=="__main__":main()
