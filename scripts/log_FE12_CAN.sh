#!/bin/bash

LOGFILE="FE12_CAN.csv"

echo "ID,D0,D1,D2,D3,D4,D5,D6,D7,Timestamp" > "$LOGFILE"

candump vcan0 | while read -r line; do
    can_id=$(echo "$line" | awk '{print substr($3, 2, length($3)-2)}')
    data=$(echo "$line" | awk '{for (i=5; i<=NF; i++) printf "%s ", $i; print ""}')

    data_array=($data)
    while [ ${#data_array[@]} -lt 8 ]; do
        data_array+=("00")
    done

    timestamp=$(date +%s%3N)

    echo "$can_id,${data_array[0]},${data_array[1]},${data_array[2]},${data_array[3]},${data_array[4]},${data_array[5]},${data_array[6]},${data_array[7]},$timestamp" >> "$LOGFILE"
done &

CANDUMP_PID=$!
wait $CANDUMP_PID
