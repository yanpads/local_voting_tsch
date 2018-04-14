#!/bin/bash

printf 'Aggregated Values vs parameters\n'
printf '===============================\n'
printf "\n"

for metric in time_all_root max_latency latency chargeConsumedPerRecv chargeConsumed reliability max_txQueueFill txQueueFill
do
    printf '### %s \n' "$metric"
    printf '![%s](bin/simData/%s_vs_threshold_buf_100.png)\n' "$metric" "$metric"
    printf "\n"
done

printf 'Some indicative scenarios\n'
printf '===================\n'
printf "\n"

buf=(100 100 100 100)
par=(1 2 3 3)
pkt=(25 25 25 5)

for i in 0 1 2 3
do
    printf 'Scenario parents: %d, packets: %s\n' "${par[i]}" "${pkt[i]}"
    printf -- '------------------------------\n'

    for metric in appGenerated_cum appReachesDagroot_cum appReachesDagroot chargeConsumed latency numRxCells txQueueFill
    do
        printf '### %s\n' "$metric" 
        printf '![%s](bin/simData/%s_vs_time_buf_%d_par_%d_pkt_%d.png)\n' "$metric" "$metric" "${buf[$i]}" "${par[$i]}" "$pkt"
        printf "\n"
    done
done
 
