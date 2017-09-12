#!/bin/bash

for parents in 1 3
do
    for buffer in 10 100
    do
        for algorithm in local_voting otf
        do
            for otfThreshold in 0 1 4 10
            do
                [[ $algorithm == "local_voting" && $otfThreshold != 0 ]] && continue
                cp "../simData_${parents}_parents_${buffer}_queue/algorithm_${algorithm}_burstTimestamp_20.0_numMotes_50_numPacketsBurst_5_otfThreshold_${otfThreshold}"/output_cpu{1..3}.dat "algorithm_${algorithm}_buffer_${buffer}_parents_${parents}_burstTimestamp_20.0_numMotes_50_numPacketsBurst_5_otfThreshold_${otfThreshold}"/
            done
        done 
    done
done
