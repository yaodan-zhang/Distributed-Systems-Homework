#!/bin/bash

PASSWORD_HASH="0d5418948b089378f36adf01b038b40b"    
MAX_LENGTH=5             
NUM_SERVERS_LIST="10 100 200 300"

echo "NUM_SERVERS, ELAPSED" >> results.csv

for NUM_SERVERS in $NUM_SERVERS_LIST; do
  echo "Running test with $NUM_SERVERS servers"
  
  # 1) Start servers on ports [5000..(5000+NUM_SERVERS-1)]
  for ((i=0; i<$NUM_SERVERS; i++))
  do
    PORT=$((4000 + i))
    python3 cracker_service.py $PORT &
    PIDS[$i]=$!
  done
  
  sleep 1  # Give servers time to fully start
  
  # 2) Capture start time
  START=$(date +%s)
  
  # 3) Run client
  python3 client.py 4000 $((3999 + NUM_SERVERS)) $PASSWORD_HASH $MAX_LENGTH
  
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
