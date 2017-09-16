#!/bin/bash

printf 'Aggregated Values vs parameters\n'
printf '===============================\n'
printf "\n"
for pkt in 1 5 25
do
    printf '%d packet(s) per node per burst\n' "$pkt"
    printf -- '------------------------------\n'

    for metric in chargeConsumed reliability time_all_root max_latency latency max_queue_delay queue_delay
    do
        printf '### %s, %s packets/node/burst\n' "$metric" "$pkt"
        printf '![%s](bin/simData/%s_vs_threshold_pkt_%d.png)\n' "$metric" "$metric" "$pkt"
        printf "\n"
    done
done

printf 'Some indicative scenarios\n'
printf '===================\n'
printf "\n"

buf=(100 100 10)
par=(1 2 3)
pkt=(25 5 1)

for i in 0 1 2
do
    printf 'Scenario buffer: %s, parents: %d, packets: %s\n'  "${buf[i]}" "${par[i]}" "${pkt[i]}"
    printf -- '------------------------------\n'

    for metric in chargeConsumed appReachesDagroot_cum appReachesDagroot txQueueFill numRxCells 
    do
        printf '### %s\n' "$metric" 
        printf '![%s](bin/simData/%s_vs_time_buf_%d_par_%d_pkt_%d.png)\n' "$metric" "$metric" "${buf[$i]}" "${par[$i]}" "$pkt"
        printf "\n"
    done
done
 
