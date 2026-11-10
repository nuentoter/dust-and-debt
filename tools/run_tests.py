#!/usr/bin/env python3
"""Run every regression in a fresh process with speaker playback disabled.

Usage: xvfb-run -a python3 tools/run_tests.py
Audio integration tests explicitly enable playback only within mocked players.
"""
import os
from pathlib import Path
import subprocess
import sys


def main():
    repo=Path(__file__).resolve().parent.parent
    env=dict(os.environ,DUST_AND_DEBT_SILENT="1")
    failed=[]
    for test in sorted((repo/"tests").glob("*_test.py")):
        result=subprocess.run([sys.executable,str(test)],cwd=repo,env=env,
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        print(("PASS " if result.returncode==0 else "FAIL ")+test.name,flush=True)
        if result.returncode:
            failed.append(test.name)
            print(result.stdout,flush=True)
    print("Failures: "+str(failed),flush=True)
    return bool(failed)


if __name__=="__main__":
    sys.exit(main())
