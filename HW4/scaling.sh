#!/bin/bash

PASSWORD_HASH="684484958e240db822eb842634ca82b5"    
MAX_LENGTH=6             
NUM_SERVERS_LIST="1 2 3 4"

echo "NUM_SERVERS, ELAPSED" >> results.csv

for NUM_SERVERS in $NUM_SERVERS_LIST; do
  echo "Running test with $NUM_SERVERS servers"
  
  # 1) Start servers on ports [5000..(5000+NUM_SERVERS-1)]
  for ((i=0; i<$NUM_SERVERS; i++))
  do
    PORT=$((5000 + i))
    python3 cracker_service.py $PORT &
    PIDS[$i]=$!
  done
  
  sleep 1  # Give servers time to fully start
  
  # 2) Capture start time
  START=$(date +%s)
  
  # 3) Run client
  python3 client.py 5000 $((4999 + NUM_SERVERS)) $PASSWORD_HASH $MAX_LENGTH
  
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
