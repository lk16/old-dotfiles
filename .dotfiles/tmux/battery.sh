#!/bin/bash
which acpitool 2>&1 > /dev/null
if [ $? -eq 0 ]; then
    output=$(acpitool -B | grep 'Remaining capacity' | cut -d ' ' -f 10 | cut -d '.' -f 1)
    echo $output'%'
else
    echo "??%"
fi