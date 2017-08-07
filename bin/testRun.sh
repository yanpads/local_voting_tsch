#!/bin/bash
# ./runSimOneCPU.py --numRuns=1 --numCyclesPerRun=100 --numChans 1 --pkPeriod 0.3 --pkPeriodVar 0.3 --otfHousekeepingPeriod 1 | tee tmp.out
./runSimOneCPU.py --cpuID 1 --numRuns=10 --numCyclesPerRun=50 --numChans 1 --pkPeriod 1.0 --pkPeriodVar 0.3 --otfHousekeepingPeriod 1 | tee tmp.out
