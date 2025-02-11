#!/bin/bash

PASSWORD_HASH="f7b2f9b1b21f81463cd21849773e0a9b"        # The MD5 hash of your test password
MAX_LENGTH=7               # Or 5, 6, depending on the scenario
#CHUNK_SIZE=...             # If you’re controlling chunk sizes
NUM_SERVERS_LIST="1 2 3 4" # Number of services to spawn

for NUM_SERVERS in $NUM_SERVERS_LIST; do
  echo "Running test with $NUM_SERVERS servers"
  
  # 1) Start servers on ports [5000..(5000+NUM_SERVERS-1)]
  for ((i=0; i<$NUM_SERVERS; i++))
  do
    PORT=$((8000 + i))
    python3 cracker_service.py $PORT &
    PIDS[$i]=$!
  done
  
  sleep 1  # Give servers time to fully start
  
  # 2) Capture start time
  START=$(date +%s)
  
  # 3) Run client
  python3 client.py 8000 $((7999 + NUM_SERVERS)) $PASSWORD_HASH $MAX_LENGTH
  
  # 4) Capture end time
  END=$(date +%s)
  
  ELAPSED=$((END - START))
  echo "$NUM_SERVERS, $ELAPSED" >> results.csv
  
  # 5) Kill servers
  for PID in "${PIDS[@]}"; do
    kill $PID
  done
  wait
done
