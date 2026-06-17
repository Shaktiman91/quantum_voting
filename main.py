"""
main.py -- Orchestration script.

Assumes the SimulaQron network for nodes Commission, Voter1, Voter2, Voter3
is already running. Start it first with:

    simulaqron start --nrnodes 4 --nodes "Commission,Voter1,Voter2,Voter3"

Then run:

    python main.py
"""

import subprocess
import sys
import time


def run_demo() -> None:
    print("[Orchestrator] Starting Commission...")
    commission = subprocess.Popen([sys.executable, "commission.py"])
    time.sleep(1)

    print("[Orchestrator] Starting voters...")
    voters = [
        subprocess.Popen([sys.executable, "voter1.py"]),
        subprocess.Popen([sys.executable, "voter2.py"]),
        subprocess.Popen([sys.executable, "voter3.py"]),
    ]

    for proc in voters:
        proc.wait()
    commission.wait()
    print("[Orchestrator] All processes finished.")


if __name__ == "__main__":
    run_demo()
