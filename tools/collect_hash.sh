#!/bin/bash

tcpdump -vvv -exxXX -i enp2f0np0.1920 -c 5 > dump.txt && cat dump.txt |  awk '
/[0-9]{2}:[0-9]{2}:[0-9]{2}:/ {
    match($0, /^[0-9:.]+ ([0-9a-f:]+).* > ([0-9a-f:]+)/, macs)
    if (macs[1] ~ /^00:00:/ || macs[2] ~ /^00:00:/) {
        gsub(":", "", macs[1])
        gsub(":", "", macs[2])
        printf "Time: %s\nKey: %s\n", $1, macs[1]
    }
}'
