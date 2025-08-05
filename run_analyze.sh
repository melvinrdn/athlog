#!/bin/bash

folder="$1"
if [ -z "$folder" ]; then
  echo "Usage: ./run_analyze.sh /chemin/vers/le_dossier"
  exit 1
fi

logfile=$(python3 analyze_week.py "$folder" | tee /dev/tty | head -n 1)
python3 analyze_week.py "$folder" | tail -n +2 | tee "$logfile"
