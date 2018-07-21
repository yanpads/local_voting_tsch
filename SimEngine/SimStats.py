#!/usr/bin/python
'''
\brief Collects and logs statistics about the ongoing simulation.

\author Thomas Watteyne <watteyne@eecs.berkeley.edu>
\author Kazushi Muraoka <k-muraoka@eecs.berkeley.edu>
\author Nicola Accettura <nicola.accettura@eecs.berkeley.edu>
\author Xavier Vilajosana <xvilajosana@eecs.berkeley.edu>
'''

#============================ logging =========================================

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SimStats')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

#============================ imports =========================================

import SimEngine
import SimSettings

#============================ defines =========================================

#============================ body ============================================

class SimStats(object):
    
    #===== start singleton
    _instance      = None
    _init          = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SimStats,cls).__new__(cls, *args, **kwargs)
        return cls._instance
    #===== end singleton
    
    def __init__(self,runNum):
        
        #===== start singleton
        if self._init:
            return
        self._init = True
        #===== end singleton
        
        # store params
        self.runNum                         = runNum
        
        # local variables
        self.engine                         = SimEngine.SimEngine()
        self.settings                       = SimSettings.SimSettings()
        
        # stats
        self.stats                          = {}
        self.columnNames                    = []
        
        # start file
        if self.runNum==0:
            self._fileWriteHeader()
        
        # schedule actions
        self.engine.scheduleAtStart(
            cb          = self._actionStart,
        )
        self.engine.scheduleAtAsn(
            asn         = self.engine.getAsn()+self.settings.slotframeLength-1,
            cb          = self._actionEndCycle,
            uniqueTag   = (None,'_actionEndCycle'),
            priority    = 10,
        )
        self.engine.scheduleAtEnd(
            cb          = self._actionEnd,
        )
        
    
    def destroy(self):
        # destroy my own instance
        self._instance                      = None
        self._init                          = False
    
    #======================== private =========================================
    
    def _actionStart(self):
        '''Called once at beginning of the simulation.'''
	#schedule a pause
        #self.engine.pauseAtAsn(13130)
        pass
    
    def _actionEndCycle(self):
        '''Called at each end of cycle.'''
        
        cycle = int(self.engine.getAsn()/self.settings.slotframeLength)
        
	#emunicio        
	# start probing at cycle 63 
        if (self.engine.asn > (63*self.settings.slotframeLength)) and self.engine.initTimeStampTraffic==0:	
            self.engine.initTimeStampTraffic=self.engine.asn*self.settings.slotDuration

        # stop probing at cycle 96   
        if (self.engine.asn >= (96*self.settings.slotframeLength)) and self.engine.endTimeStampTraffic==0:
            self.engine.endTimeStampTraffic=self.engine.asn*self.settings.slotDuration
            self.engine.timeElapsedFlow=self.engine.endTimeStampTraffic-self.engine.initTimeStampTraffic        
            print "Elapsed time: "+str(self.engine.timeElapsedFlow)        
        
        # write statistics to output file
        self._fileWriteStats(
            dict(
                {
                    'runNum':              self.runNum,
                    'cycle':               cycle,
                }.items() +
                self._collectSumMoteStats().items()  +
                self._collectScheduleStats().items()
            )
        )
        
        # schedule next statistics collection
        self.engine.scheduleAtAsn(
            asn         = self.engine.getAsn()+self.settings.slotframeLength,
            cb          = self._actionEndCycle,
            uniqueTag   = (None,'_actionEndCycle'),
            priority    = 10,
        )
        
    def _actionEndSecond(self):
        '''Called at each end of cycle.'''
                
        # schedule next statistics collection
        self.engine.scheduleAtAsn(
            asn         = self.engine.getAsn()+100,
            cb          = self._actionEndSecond,
            uniqueTag   = (None,'_actionEndSecond'),
            priority    = 10,
        )
    
    def _actionEnd(self):
        '''Called once at end of the simulation.'''
        self._fileWriteTopology()
    
    #=== collecting statistics
    
    def _collectSumMoteStats(self):
        returnVal = {}
        
        for mote in self.engine.motes:
            moteStats        = mote.getMoteStats()
            if not returnVal:
                returnVal    = moteStats
            else:
                for k in returnVal.keys():
                    returnVal[k] += moteStats[k]
        
        return returnVal

    
        
    def _collectScheduleStats(self):
        
        # compute the number of schedule collisions
        
        # Note that this cannot count past schedule collisions which have been relocated by 6top
        # as this is called at the end of cycle   
        scheduleCollisions = 0
        txCells = []
        for mote in self.engine.motes:
            for ((ts,chan),cell) in mote.schedule.items():
                (ts,ch) = (ts,cell['ch'])
                if cell['dir']==mote.DIR_TX:
                    if (ts,ch) in txCells:
                        scheduleCollisions += 1
                    else:
                        txCells += [(ts,ch)]
        
        # collect collided links
        txLinks = {}
        for mote in self.engine.motes:
            for ((ts,chan),cell) in mote.schedule.items():
                if cell['dir']==mote.DIR_TX:
                    (ts,ch) = (ts,cell['ch'])
                    (tx,rx) = (mote,cell['neighbor'])
                    if (ts,ch) in txLinks:
                        txLinks[(ts,ch)] += [(tx,rx)] 
                    else:
                        txLinks[(ts,ch)]  = [(tx,rx)]
                        
        collidedLinks = [txLinks[(ts,ch)] for (ts,ch) in txLinks if len(txLinks[(ts,ch)])>=2]
        
        # compute the number of Tx in schedule collision cells
        collidedTxs = 0
        for links in collidedLinks:
            collidedTxs += len(links)
              
        # compute the number of effective collided Tx    
        effectiveCollidedTxs = 0
        insufficientLength   = 0 
        for links in collidedLinks:
            for (tx1,rx1) in links:
                for (tx2,rx2) in links:
                    if tx1!=tx2 and rx1!=rx2:
                        # check whether interference from tx1 to rx2 is effective
                        if tx1.getRSSI(rx2) >= rx2.minRssi:
                            effectiveCollidedTxs += 1
        return {'scheduleCollisions':scheduleCollisions, 'collidedTxs': collidedTxs, 'effectiveCollidedTxs': effectiveCollidedTxs}
    
    #=== writing to file
    
    def _fileWriteHeader(self):
        output          = []
        output         += ['## {0} = {1}'.format(k,v) for (k,v) in self.settings.__dict__.items() if not k.startswith('_')]
        output         += ['\n']
        output          = '\n'.join(output)
        
        with open(self.settings.getOutputFile(),'w') as f:
            f.write(output)
    
    def _fileWriteStats(self,stats):
        output          = []
        
        # columnNames
        if not self.columnNames:
            self.columnNames = sorted(stats.keys())
            output     += ['\n# '+' '.join(self.columnNames)]
        
        # dataline
        formatString    = ' '.join(['{{{0}:>{1}}}'.format(i,len(k)) for (i,k) in enumerate(self.columnNames)])
        formatString   += '\n'
        
        vals = []
        for k in self.columnNames:
            if type(stats[k])==float:
                vals += ['{0:.3f}'.format(stats[k])]
            else:
                vals += [stats[k]]
        
        output += ['  '+formatString.format(*tuple(vals))]
        
        # write to file
        with open(self.settings.getOutputFile(),'a') as f:
            f.write('\n'.join(output))
    
    def _fileWriteTopology(self):
        output  = []
        output += [
            '#pos runNum={0} {1}'.format(
                self.runNum,
                ' '.join(['{0}@({1:.5f},{2:.5f})@{3}'.format(mote.id,mote.x,mote.y,mote.rank) for mote in self.engine.motes])
            )
        ]
        links = {}
        for m in self.engine.motes:
            for n in self.engine.motes:
                if m==n:
                    continue
                if (n,m) in links:
                    continue
                try:
                    links[(m,n)] = (m.getRSSI(n),m.getPDR(n))
                except KeyError:
                    pass
        output += [
            '#links runNum={0} {1}'.format(
                self.runNum,
                ' '.join(['{0}-{1}@{2:.0f}dBm@{3:.3f}'.format(moteA.id,moteB.id,rssi,pdr) for ((moteA,moteB),(rssi,pdr)) in links.items()])
            )
        ]
	#emunicio
	output += [
            '#results runNum={0} totalPacketSent {1} totalPacketReceived {2} totalOLGenerated {3} totalThReceived {4} dropsByCollisions {5} totalTX {6} totalRX {7} dropsPropagation {8} -'.format(
                self.runNum,self.engine.packetsSentToRoot,self.engine.packetReceivedInRoot,self.engine.olGeneratedToRoot/(self.settings.numMotes-1),self.engine.thReceivedInRoot/(self.settings.numMotes-1), self.engine.dropByCollision, self.engine.totalTx, self.engine.totalRx, self.engine.dropByPropagation 
            )
        ]

        output += [
            '#aveChargePerCycle runNum={0} {1}'.format(
                self.runNum,
                ' '.join(['{0}@{1:.2f}'.format(mote.id,mote.getMoteStats()['chargeConsumed']/self.settings.numCyclesPerRun) for mote in self.engine.motes])
            )
        ] 
	
	output += [ ''
        ]
	       
        output  = '\n'.join(output)
        
        with open(self.settings.getOutputFile(),'a') as f:
            f.write(output)
