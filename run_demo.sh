#!/bin/bash
# run_demo.sh -- Start SimulaQron network and all voting processes.
#
# PROTOTYPE NOTICE: research demo only; not for real elections.
#
# Correct simulaqron start command taken from Quantum_week8 README:
#   simulaqron start --nodes=Commission,Voter1,Voter2,Voter3 \
#     --network-config-file simulaqron_network.json \
#     --simulaqron-config-file simulaqron_settings.json

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[demo] Starting SimulaQron network..."
simulaqron start \
  --nodes=Commission,Voter1,Voter2,Voter3 \
  --network-config-file simulaqron_network.json \
  --simulaqron-config-file simulaqron_settings.json &
SQRON_PID=$!
sleep 3

echo "[demo] Starting Commission (Referee)..."
python3 commission.py &
COM_PID=$!
sleep 1

echo "[demo] Starting voters..."
python3 voter3.py &
python3 voter2.py &
python3 voter1.py &

wait $COM_PID
echo "[demo] Commission done."

echo "[demo] Stopping SimulaQron..."
simulaqron stop || true
