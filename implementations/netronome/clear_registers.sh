#!/bin/bash

registers=("cfb" "frequency_table" "first_index" "distinct_counter" "old_distinct_counter" "variation" "p_counter" "reset_counter")

for register in "${registers[@]}"; do
    /opt/netronome/p4/bin/rtecli -r cloud141 registers -r "$register" clear
done
