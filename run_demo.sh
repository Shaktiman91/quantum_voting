#!/bin/bash
# run_demo.sh -- Start SimulaQron network and all voting processes.
#
# PROTOTYPE NOTICE: research demo only; not for real elections.

set -e

echo "[demo] Starting SimulaQron network..."
simulaqron start --nrnodes 4 --nodes "Commission,Voter1,Voter2,Voter3" &
SQRON_PID=$!
sleep 2

echo "[demo] Starting Commission..."
python commission.py &
COM_PID=$!
sleep 1

echo "[demo] Starting voters..."
python voter1.py &
python voter2.py &
python voter3.py &

wait $COM_PID
echo "[demo] Commission done."

echo "[demo] Stopping SimulaQron..."
simulaqron stop || true
