#!/bin/bash

for dir 
do 
    (
        cd "$dir"
        python ../plotStuff.py
        params=(
#            appGenerated 
            appReachesDagroot 
#            appRelayed 
#            aveHops 
            aveLatency 
            aveQueueDelay 
            chargeConsumed 
 #           collidedTxs 
 #           droppedAppFailedEnqueue 
 #           droppedMacRetries 
 #           droppedNoRoute 
 #           droppedNoTxCells 
 #           droppedQueueFull 
 #           effectiveCollidedTxs 
            numRxCells 
            numTx 
  #          numTxCells 
  #          otfAdd 
  #          otfRemove 
 #           probableCollisions 
 #           rplChurnParentSet 
 #           rplChurnPrefParent 
 #           rplChurnRank 
 #           rplRxDIO 
 #           rplTxDIO 
 #           runNum 
 #           scheduleCollisions 
 #           topRxRelocatedCells 
 #           topTxRelocatedBundles 
 #           topTxRelocatedCells 
 #           txQueueFill 
        )
        printf "%s\n" "${params[@]}" | parallel python ../plotAveStatsVsCycles.py --statsName


    )


done
