#!/bin/bash
# ./runSimOneCPU.py --numRuns=1 --numCyclesPerRun=100 --numChans 1 --pkPeriod 0.3 --pkPeriodVar 0.3 --otfHousekeepingPeriod 1 | tee tmp.out
./runSimOneCPU.py --cpuID 1 --numRuns=1 --numCyclesPerRun=100 --numChans 1 --pkPeriod 0.01 --pkPeriodVar 0.003 --otfHousekeepingPeriod 1 2>&1 | tee tmp.out
