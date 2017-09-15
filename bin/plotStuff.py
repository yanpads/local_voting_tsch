#!/usr/bin/python
'''
\brief Plots timelines and topology figures from collected simulation data.

\author Thomas Watteyne <watteyne@eecs.berkeley.edu>
\author Kazushi Muraoka <k-muraoka@eecs.berkeley.edu>
\author Nicola Accettura <nicola.accettura@eecs.berkeley.edu>
\author Xavier Vilajosana <xvilajosana@eecs.berkeley.edu>
'''

import os
import re
import glob
import pprint

import numpy
import scipy
import scipy.stats

import matplotlib.pyplot

#============================ defines =========================================

DATADIR       = '.'
CONFINT       = 0.95

COLORS_TH     = {
    0:        'magenta',
    1:        'blue',
    4:        'green',
    'NA':     'red' ,
    10:       'black',
}

LINESTYLE_TH       = {
    0:        '-',
    1:        '--',
    4:        '-.',
    'NA':        '-.',
    10:       ':',
}

ECOLORS_TH         = {
    0:        'magenta',
    1:        'blue',
    4:        'green',
    'NA':     'red',
    10:       'black',
}

COLORS_PERIOD      = {
    'NA':     'red',
    1:        'blue',
    10:       'green',
    60:       'black',
}

LINESTYLE_PERIOD   = {
    'NA':     '--',
    1:        '--',
    10:       '-.',
    60:       ':',
}

FILLSTYLES_ALG = {
    'otf':    '',
    'local_voting': '/',
}

ECOLORS_PERIOD     = {
    'NA':     'red',
    1:        'blue',
    10:       'green',
    60:       'magenta',
}

pp = pprint.PrettyPrinter(indent=4)

#============================ helpers =========================================

def binDataFiles():
    '''
    bin the data files according to the otfThreshold and pkPeriod.

    Returns a dictionary of format:
    {
        (otfThreshold,pkPeriod): [
            filepath,
            filepath,
            filepath,
        ]
    }
    '''
    infilepaths    = glob.glob(os.path.join(DATADIR,'**','*.dat'))

    dataBins       = {}
    for infilepath in infilepaths:
        with open(infilepath,'r') as f:
            for line in f:
                if not line.startswith('## ') or not line.strip():
                    continue
                # otfThreshold
                m = re.search('otfThreshold\s+=\s+([\.0-9]+)',line)
                if m:
                    otfThreshold = int(m.group(1))
                # pkPeriod
                m = re.search('pkPeriod\s+=\s+([\.0-9]+)',line)
                if m:
                    pkPeriod     = float(m.group(1))
                else:
                    pkPeriod     = 'NA'
                # algorithm
                m = re.search('algorithm\s+=\s+(.+)',line)
                if m:
                    algorithm    = m.group(1)
                # buffer
                m = re.search('buffer_([^_]+)',infilepath)
                if m:
                    buffer_size  = int(m.group(1))
                # parents
                m = re.search('parents_([^_/]+)',infilepath)
                if m:
                    parent_size      = int(m.group(1))

            if (otfThreshold,pkPeriod,algorithm,parent_size,buffer_size) not in dataBins:
                dataBins[(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)] = []
            dataBins[(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)] += [infilepath]

    output  = []
    for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),filepaths) in dataBins.items():
        output         += ['otfThreshold={0} pkPeriod={1} algorithm={2} parents={3} buffer={3}'.format(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)]
        for f in filepaths:
            output     += ['   {0}'.format(f)]
    output  = '\n'.join(output)

    print "OUTPUT: %s" % output
    return dataBins

def gatherPerRunData(infilepaths,elemName):

    valuesPerRun = {}
    for infilepath in infilepaths:

        # print
        print 'Parsing {0} for {1}...'.format(infilepath,elemName),

        # find col_elemName, col_runNum, cpuID
        col_elemName    = None
        col_runNum      = None
        cpuID           = None
        with open(infilepath,'r') as f:
            for line in f:
                if line.startswith('# '):
                    # col_elemName, col_runNum
                    elems        = re.sub(' +',' ',line[2:]).split()
                    numcols      = len(elems)
                    col_elemName = elems.index(elemName)
                    col_runNum   = elems.index('runNum')
                    break

                if line.startswith('## '):
                    # cpuID
                    m = re.search('cpuID\s+=\s+([0-9]+)',line)
                    if m:
                        cpuID = int(m.group(1))
        assert col_elemName!=None
        assert col_runNum!=None
        assert cpuID!=None

        # parse data
        with open(infilepath,'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                m       = re.search('\s+'.join(['([\.0-9]+)']*numcols),line.strip())
                runNum  = int(m.group(col_runNum+1))
                try:
                    elem         = float(m.group(col_elemName+1))
                except:
                    try:
                        elem     =   int(m.group(col_elemName+1))
                    except:
                        elem     =       m.group(col_elemName+1)

                if (cpuID,runNum) not in valuesPerRun:
                    valuesPerRun[cpuID,runNum] = []
                valuesPerRun[cpuID,runNum] += [elem]

        # print
        print 'done.'

    return valuesPerRun

def gatherPerCycleData(infilepaths,elemName):

    valuesPerCycle = {}
    for infilepath in infilepaths:

        # print
        print 'Parsing {0} for {1}...'.format(infilepath,elemName),

        # find colnumelem, colnumcycle
        with open(infilepath,'r') as f:
            for line in f:
                if line.startswith('# '):
                    elems        = re.sub(' +',' ',line[2:]).split()
                    numcols      = len(elems)
                    colnumelem   = elems.index(elemName)
                    colnumcycle  = elems.index('cycle')
                    break

        assert colnumelem
        assert colnumcycle

        # parse data

        with open(infilepath,'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                m       = re.search('\s+'.join(['([\.0-9]+)']*numcols),line.strip())
                cycle   = int(m.group(colnumcycle+1))
                try:
                    elem         = float(m.group(colnumelem+1))
                except:
                    try:
                        elem     =   int(m.group(colnumelem+1))
                    except:
                        elem     =       m.group(colnumelem+1)

                if cycle not in valuesPerCycle:
                    valuesPerCycle[cycle] = []
                valuesPerCycle[cycle] += [elem]

        # print
        print 'done.'

    return valuesPerCycle

def calcMeanConfInt(vals):
    assert type(vals)==list
    for val in vals:
        assert type(val) in [int,float,numpy.float64]

    a         = 1.0*numpy.array(vals)
    se        = scipy.stats.sem(a)
    m         = numpy.mean(a)
    confint   = se * scipy.stats.t._ppf((1+CONFINT)/2., len(a)-1)

    return (m,confint)

def getSlotDuration(dataBins):
    for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),filepaths) in dataBins.items():
        for filepath in filepaths:
            with open(filepath,'r') as f:
                for line in f:
                    if line.startswith('## '):
                        m = re.search('slotDuration\s+=\s+([\.0-9]+)',line)
                        if m:
                            return float(m.group(1))

#============================ plotters ========================================

def plot_vs_time(plotData,ymin=None,ymax=None,ylabel=None,filename=None,doPlot=True,withError=True):

    prettyp   = False

    #===== format data

    # calculate mean and confidence interval
    for ((otfThreshold,pkPeriod,algorithm),perCycleData) in plotData.items():
        for cycle in perCycleData.keys():
            (m,confint) = calcMeanConfInt(perCycleData[cycle])
            perCycleData[cycle] = {
                'mean':      m,
                'confint':   confint,
            }

    # plotData = {
    #     (otfThreshold,pkPeriod) = {
    #         0: {'mean': 12, 'confint':12},
    #         1: {'mean': 12, 'confint':12},
    #     }
    # }

    # arrange to be plotted
    for ((otfThreshold,pkPeriod,algorithm),perCycleData) in plotData.items():
        x     = sorted(perCycleData.keys())
        y     = [perCycleData[i]['mean']    for i in x]
        yerr  = [perCycleData[i]['confint'] for i in x] if withError else [ 0 for i in x]
        assert len(x)==len(y)==len(yerr)

        plotData[(otfThreshold,pkPeriod,algorithm)] = {
            'x':        x,
            'y':        y,
            'yerr':     yerr,
        }

    # plotData = {
    #     (otfThreshold,pkPeriod) = {
    #         'x':      [ 0, 1, 2, 3, 4, 5, 6],
    #         'y':      [12,12,12,12,12,12,12],
    #         'yerr':   [12,12,12,12,12,12,12],
    #     }
    # }

    if prettyp:
        with open('templog.txt','w') as f:
            f.write('\n============ {0}\n'.format('arrange to be plotted'))
            f.write(pp.pformat(plotData))

    if not doPlot:
        return plotData

    #===== plot

    pkPeriods           = []
    otfThresholds       = []
    algorithms          = []
    for (otfThreshold,pkPeriod,algorithm) in plotData.keys():
        pkPeriods      += [pkPeriod]
        otfThresholds  += [otfThreshold]
        algorithms     += [algorithm]
    pkPeriods           = sorted(list(set(pkPeriods)))
    otfThresholds       = sorted(list(set(otfThresholds)), reverse=withError)
    algorithms          = sorted(list(set(algorithms)), reverse=withError)

    fig = matplotlib.pyplot.figure()

    def plotForEachPkPeriod(ax,plotData,pkPeriod_p):
        ax.set_xlim(xmin=0,xmax=100)
        ax.set_ylim(ymin=ymin,ymax=ymax)
        if pkPeriod_p!='NA':
            ax.text(2,0.9*ymax,'packet period {0}s'.format(pkPeriod_p))
        plots = []
        for th in otfThresholds:
            for ((otfThreshold,pkPeriod),data) in plotData.items():
                if otfThreshold==th and pkPeriod==pkPeriod_p:
                    plots += [
                        ax.errorbar(
                            x        = data['x'],
                            y        = data['y'],
                            yerr     = data['yerr'],
                            color    = COLORS_TH[th],
                            ls       = LINESTYLE_TH[th],
                            ecolor   = ECOLORS_TH[th],
                        )
                    ]
        return tuple(plots)

    # plot axis


    allaxes = []
    if 'NA' not in pkPeriods:
        subplotHeight = 0.85/len(pkPeriods)
        for (plotIdx,pkPeriod) in enumerate(pkPeriods):
            ax = fig.add_axes([0.10, 0.10+plotIdx*subplotHeight, 0.85, subplotHeight])
            legendPlots = plotForEachPkPeriod(ax,plotData,pkPeriod)
            allaxes += [ax]
    else:
        ax = fig.add_axes([0.10, 0.10, 0.85, 0.85])
        ax.set_xlim(xmin=0,xmax=100)
        ax.set_ylim(ymin=ymin,ymax=ymax)
        plots = []
        legends = []
        for alg in [ 'otf', 'local_voting' ]:
            for th in otfThresholds:
                for ((otfThreshold,pkPeriod,algorithm),data) in plotData.items():
                    if algorithm==alg and otfThreshold == th:

                        if algorithm == 'local_voting' and otfThreshold != 0:
                            continue

                        t = th if alg == 'otf' else 'NA'
                        plots += [
                            ax.errorbar(
                                x        = data['x'],
                                y        = data['y'],
                                yerr     = data['yerr'],
                                color    = COLORS_TH[t],
                                ls       = LINESTYLE_TH[0],
                                ecolor   = ECOLORS_TH[t],
                            )
                        ]
                        legends += ( ['{0}_{1}'.format(alg,th)] if alg == 'otf' else [ alg ] )
		legendPlots = tuple(plots)
        allaxes += [ax]

    # add x label

#   for ax in allaxes[1:]:
#        ax.get_xaxis().set_visible(False)
    allaxes[0].set_xlabel('time (slotframe cycles)')

    # add y label
    allaxes[int(len(allaxes)/2)].set_ylabel(ylabel)

    # add legend
    legendText = tuple(legends)

    fig.legend(
        legendPlots,
        legendText,
#         loc='best',
#        prop={'size':8},
    )

    matplotlib.pyplot.savefig(os.path.join(DATADIR,'{0}.png'.format(filename)))
    matplotlib.pyplot.savefig(os.path.join(DATADIR,'{0}.eps'.format(filename)))
    matplotlib.pyplot.close('all')

def plot_vs_threshold(plotData,ymin,ymax,ylabel,filename):

    prettyp   = False

    #===== format data

    # plotData = {
    #     (otfThreshold,pkPeriod) = {
    #         cycle0: [run0,run1, ...],
    #         cycle1: [run0,run1, ...],
    #     }
    # }

    if prettyp:
        with open('templog.txt','w') as f:
            f.write('\n============ {0}\n'.format('initial data'))
            f.write(pp.pformat(plotData))

    # collapse all cycles
    for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),perCycleData) in plotData.items():
        temp = []
        for (k,v) in perCycleData.items():
            temp += v

        plotData[(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)] = temp

    # plotData = {
    #     (otfThreshold,pkPeriod) = [
    #         cycle0_run0,
    #         cycle0_run1,
    #         ...,
    #         cycle1_run0,
    #         cycle1_run1,
    #         ...,
    #     ]
    # }

    if prettyp:
        with open('templog.txt','a') as f:
            f.write('\n============ {0}\n'.format('collapse all cycles'))
            f.write(pp.pformat(plotData))

    # calculate mean and confidence interval
    for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),perCycleData) in plotData.items():
        (m,confint) = calcMeanConfInt(perCycleData)
        plotData[(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)] = {
            'mean':      m,
            'confint':   confint,
        }

    # plotData = {
    #     (otfThreshold,pkPeriod) = {'mean': 12, 'confint':12},
    # }

    if prettyp:
        with open('templog.txt','a') as f:
            f.write('\n============ {0}\n'.format('calculate mean and confidence interval'))
            f.write(pp.pformat(plotData))

    pkPeriods           = []
    otfThresholds       = []
    algorithms          = []
    buffer_sizes        = []
    parent_sizes        = []
    for (otfThreshold,pkPeriod,algorithm,parent_size,buffer_size) in plotData.keys():
        pkPeriods      += [pkPeriod]
        otfThresholds  += [otfThreshold]
        algorithms     += [algorithm]
        buffer_sizes   += [buffer_size]
        parent_sizes   += [parent_size]
    pkPeriods           = sorted(list(set(pkPeriods)))
    otfThresholds       = sorted(list(set(otfThresholds)), reverse=True)
    algorithms          = sorted(list(set(algorithms)))
    buffer_sizes        = sorted(list(set(buffer_sizes)))
    parent_sizes        = sorted(list(set(parent_sizes)))

    #===== plot

#    fig = matplotlib.pyplot.figure()
    fig, ax = matplotlib.pyplot.subplots()
    matplotlib.pyplot.ylim(ymin=ymin,ymax=ymax)
    ax.set_xlabel('Parameters: (num of parents, buffer size)')
    ax.set_ylabel(ylabel)
    bars = []
    legends = []
    offset = 0
    x = []
    for algorithm in algorithms:
        for threshold in otfThresholds:

            if algorithm == 'local_voting' and threshold != 0:
                continue

            d = {}
            for ((otfThreshold,pkPeriod,pkAlgorithm,parent_size,buffer_size),data) in plotData.items():
                if otfThreshold == threshold and pkAlgorithm == algorithm:
                    d[parent_size,buffer_size] = data

            x     = sorted(d.keys())
            tics  = [i+.25+offset for i in range(len(x))]
            y     = [d[k]['mean'] for k in x]
            yerr  = [d[k]['confint'] for k in x]

            t     = threshold if algorithm == 'otf' else 'NA'

            bars += [ax.bar(tics, y, 0.1, color= COLORS_TH[t], edgecolor='black', ecolor=ECOLORS_TH[t], yerr=yerr)]
            legends += [ '{}, thr={}'.format(algorithm,threshold) ] if algorithm == 'otf' else [ algorithm ]
            offset += 0.15

    ax.set_xticks( [i+.25+offset/2 for i in range(len(x))])
    ax.set_xticklabels(x)
    ax.legend( bars, legends, loc="best")

#            matplotlib.pyplot.errorbar(
#                x        = x,
#                y        = y,
#                yerr     = yerr,
#
#                color    = COLORS_TH[threshold],
#                ls       = LINESTYLE_TH[algorithm=='otf'],
#                ecolor   = ECOLORS_TH[threshold],
#                label    = '{}, thr={}'.format(algorithm,threshold)
#            )
#    matplotlib.pyplot.legend(prop={'size':10})
    matplotlib.pyplot.savefig(os.path.join(DATADIR,'{0}.png'.format(filename)))
    matplotlib.pyplot.savefig(os.path.join(DATADIR,'{0}.eps'.format(filename)))
    matplotlib.pyplot.close('all')

#----- txQueueFill

def gather_per_cycle_data(dataBins, parameter, factor=1.0):

    prettyp   = False

    # gather raw data
    plotData  = {}
    for ((otfThreshold,pkPeriod,algorithm,parents,buffer_size),filepaths) in dataBins.items():
        plotData[(otfThreshold,pkPeriod,algorithm,parents,buffer_size)] = gatherPerCycleData(filepaths,parameter)

    # plotData = {
    #     (otfThreshold,pkPeriod) = {
    #         cycle0: [run0,run1, ...],
    #         cycle1: [run0,run1, ...],
    #     }
    # }

    if prettyp:
        with open('templog.txt','w') as f:
            f.write('\n============ {0}\n'.format('gather raw data'))
            f.write(pp.pformat(plotData))

     # Multiply by factor
    for ((otfThreshold,pkPeriod,algorithm,parent,buffer_size),perCycleData) in plotData.items():
        for cycle in perCycleData.keys():
            perCycleData[cycle] = [ factor * val for val in perCycleData[cycle] ]

    # plotData = {
    #     (otfThreshold,pkPeriod) = {
    #         cycle0: [run0,run1, ...],
    #         cycle1: [run0,run1, ...],
    #     }
    # }

    if prettyp:
        with open('templog.txt','a') as f:
            f.write('\n============ {0}\n'.format('convert slots to seconds'))
            f.write(pp.pformat(plotData))

    return plotData


def plot_txQueueFill_vs_time(dataBins):

    plotData  = gather_per_cycle_data(dataBins, 'txQueueFill')

    for b in [5, 10, 15]:
        for p in [1,2,3]:
            plot_vs_time(
                plotData = dict(((th,per,alg),data) for (th,per,alg,par,buf),data in plotData.items() if buf == b and par == p ),
                ymin     = 0,
                ymax     = 50,
                ylabel   = 'txQueueFill',
                filename = 'txQueueFilllatency_vs_time_buf_{}_par_{}'.format(b,p),
                withError = False,
            )

def plot_appReachesDagroot_vs_time(dataBins):

    plotData  = gather_per_cycle_data(dataBins, 'appReachesDagroot')

    for b in [5, 10, 15]:
        for p in [1,2,3]:
            plot_vs_time(
                plotData = dict(((th,per,alg),data) for (th,per,alg,par,buf),data in plotData.items() if buf == b and par == p ),
                ymin     = 0,
                ymax     = 50,
                ylabel   = 'appReachesDagroot',
                filename = 'appReachesDagroot_vs_time_buf_{}_par_{}'.format(b,p),
                withError = False,
            )


def plot_numRxCells_vs_time(dataBins):

    plotData  = gather_per_cycle_data(dataBins, 'numRxCells')

    for b in [5, 10, 15]:
        for p in [1,2,3]:
            plot_vs_time(
                plotData = dict(((th,per,alg),data) for (th,per,alg,par,buf),data in plotData.items() if buf == b and par == p ),
                ymin     = 0,
                ymax     = 1000,
                ylabel   = 'numRxCells',
                filename = 'numRxCells_vs_time_buf_{}_par_{}'.format(b,p),
                withError = False,
            )

def plot_chargeConsumed_vs_time(dataBins):

    plotData  = gather_per_cycle_data(dataBins, 'chargeConsumed', 1e-5)

    for b in [5, 10, 15]:
        for p in [1,2,3]:
            plot_vs_time(
                plotData = dict(((th,per,alg),data) for (th,per,alg,par,buf),data in plotData.items() if buf == b and par == p ),
                ymin     = 0,
                ymax     = 7,
                ylabel   = 'chargeConsumed x1e5',
                filename = 'chargeConsumed_vs_time_buf_{}_par_{}'.format(b,p),
                withError = False,
            )



#===== latency

def gather_latency_data(dataBins):

    prettyp   = False

    # gather raw data
    plotData  = {}
    for ((otfThreshold,pkPeriod,algorithm,parents,buffer_size),filepaths) in dataBins.items():
        plotData[(otfThreshold,pkPeriod,algorithm,parents,buffer_size)] = gatherPerCycleData(filepaths,'aveLatency')

    # plotData = {
    #     (otfThreshold,pkPeriod) = {
    #         cycle0: [run0,run1, ...],
    #         cycle1: [run0,run1, ...],
    #     }
    # }

    if prettyp:
        with open('templog.txt','w') as f:
            f.write('\n============ {0}\n'.format('gather raw data'))
            f.write(pp.pformat(plotData))

    # convert slots to seconds
    slotDuration = getSlotDuration(dataBins)
    for ((otfThreshold,pkPeriod,algorithm,parent,buffer_size),perCycleData) in plotData.items():
        for cycle in perCycleData.keys():
            perCycleData[cycle] = [d*slotDuration for d in perCycleData[cycle]]

    # plotData = {
    #     (otfThreshold,pkPeriod) = {
    #         cycle0: [run0,run1, ...],
    #         cycle1: [run0,run1, ...],
    #     }
    # }

    if prettyp:
        with open('templog.txt','a') as f:
            f.write('\n============ {0}\n'.format('convert slots to seconds'))
            f.write(pp.pformat(plotData))

    # filter out 0 values
    for ((otfThreshold,pkPeriod,algorithm,parents,buffer_size),perCycleData) in plotData.items():
        for cycle in perCycleData.keys():
            i=0
            while i<len(perCycleData[cycle]):
                if perCycleData[cycle][i]==0:
                    del perCycleData[cycle][i]
                else:
                    i += 1

    # plotData = {
    #     (otfThreshold,pkPeriod) = {
    #         cycle0: [run0,run1, ...],
    #         cycle1: [run0,run1, ...],
    #     }
    # }

    if prettyp:
        with open('templog.txt','a') as f:
            f.write('\n============ {0}\n'.format('filter out 0 values'))
            f.write(pp.pformat(plotData))

    return plotData

def plot_latency_vs_time(dataBins):

    plotData  = gather_latency_data(dataBins)

    for b in [5, 10, 15]:
        for p in [1,2,3]:
            plot_vs_time(
                plotData = dict(((th,per,alg),data) for (th,per,alg,par,buf),data in plotData.items() if buf == b and par == p ),
                ymin     = 0,
                ymax     = 18,
                ylabel   = 'end-to-end latency (s)',
                filename = 'latency_vs_time_buf_{}_par_{}'.format(b,p),
                withError = False,
            )

def plot_latency_vs_threshold(dataBins):

    plotData  = gather_ave_data(dataBins, 'aveLatency', 'appReachesDagroot')

    plot_vs_threshold(
        plotData   = plotData,
        ymin       = 0,
        ymax       = 2.5,
        ylabel     = 'average end-to-end latency (s)',
        filename   = 'latency_vs_threshold',
    )

def plot_ave_q_delay_vs_threshold(dataBins):

    plotData  = gather_ave_data(dataBins, 'aveQueueDelay', 'numTx')

    plot_vs_threshold(
        plotData   = plotData,
        ymin       = 0,
        ymax       = 2.5,
        ylabel     = 'average queue delay (s)',
        filename   = 'queue_delay_vs_threshold',
    )

def gather_max_data(dataBins, label):
    plotData  = {}
    unit_factor = getSlotDuration(dataBins) if label == 'aveLatency' else 1
    for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),filepaths) in dataBins.items():
        perCycle = gatherPerCycleData(filepaths, label)

        max_values = [ 0 for i in perCycle[0]]
        print "file: {}, percyle: {}, {}".format(filepaths,perCycle,(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size))
        for k,v in perCycle.items():
            for run,value in enumerate(v):
                lat = unit_factor * value
                if lat > max_values[run]:
                    max_values[run] = lat
            print k,len(v)
        print "max_{}: {}".format(label,max_values)

        plotData[(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)] = {0: max_values}

    return plotData

def gather_ave_data(dataBins, label, count_label):
    plotData  = {}
    unit_factor = getSlotDuration(dataBins) if label == 'aveLatency' else 0.001 if label == 'aveQueueDelay' else 1
    for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),filepaths) in dataBins.items():
        perCycle = gatherPerCycleData(filepaths, label)
        perCycle_count = gatherPerCycleData(filepaths, count_label)
        print "perCyple: {}\n\n, count: {}\n\n".format(perCycle, perCycle_count)

        sum_values = [ 0 for i in perCycle[0]]
        count_values = [ 0 for i in perCycle[0]]

        for k,v in perCycle.items():
            for run,value in enumerate(v):
                lat = unit_factor * value
                sum_values[run] += perCycle_count[k][run] * lat
                count_values[run] += perCycle_count[k][run]


#        values += [ perCycle_count[k] * unit_factor * v_i /sum_perCycle_count for v_i in v]

        plotData[(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)] = {0: [ v / count_values[run] for run,v in enumerate(sum_values) ]  }

    return plotData


def plot_max_latency_vs_threshold(dataBins):

    plotData  = gather_max_data(dataBins, 'aveLatency')

    plot_vs_threshold(
        plotData   = plotData,
        ymin       = 0,
        ymax       = 15,
        ylabel     = 'max end-to-end latency (s)',
        filename   = 'max_latency_vs_threshold',
    )

def plot_max_queue_delay_vs_threshold(dataBins):

    plotData  = gather_max_data(dataBins, 'aveQueueDelay')

    plot_vs_threshold(
        plotData   = plotData,
        ymin       = 0,
        ymax       = 3000,
        ylabel     = 'max queue delay (ms)',
        filename   = 'max_queue_delay_vs_threshold',
    )


def gather_time_all_reached(dataBins):
    plotData  = {}
    for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),filepaths) in dataBins.items():
        perCycle = gatherPerCycleData(filepaths,'appReachesDagroot')

        lastnonzero = [ 1000 for i in perCycle[0]]
        # print "file: {}, percyle: {}, {}".format(filepaths,perCycle,(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size))
        for k,v in perCycle.items():
            for run,value in enumerate(v):
                if value != 0:
                    lastnonzero[run] = k
            # print k,len(v)
        print "lastnonzero: {}".format(lastnonzero)

        plotData[(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)] = {0: lastnonzero}

    return plotData


def plot_time_all_reached_vs_threshold(dataBins):

    plotData  = gather_time_all_reached(dataBins)

    print plotData
    plot_vs_threshold(
        plotData   = plotData,
        ymin       = 60,
        ymax       = 75,
        ylabel     = 'time for last packet to reach root',
        filename   = 'time_all_root_vs_threshold',
    )

#===== numCells

def gather_numCells_data(dataBins):

    prettyp   = False

    # gather raw data
    plotData  = {}
    for ((otfThreshold,pkPeriod,algorithm),filepaths) in dataBins.items():
        plotData[(otfThreshold,pkPeriod)] = gatherPerCycleData(filepaths,'numTxCells')

    # plotData = {
    #     (otfThreshold,pkPeriod) = {
    #         0: [12,12,12,12,12,12,12,12,12],
    #         1: [12,12,12,12,12,0,0,0,0],
    #     }
    # }

    if prettyp:
        with open('templog.txt','w') as f:
            f.write('\n============ {0}\n'.format('gather raw data'))
            f.write(pp.pformat(plotData))

    return plotData

def plot_numCells_vs_time(dataBins):

    plotData  = gather_numCells_data(dataBins)

    plot_vs_time(
        plotData = plotData,
        ymin     = 0,
        ymax     = 200,
        ylabel   = 'number of scheduled cells',
        filename = 'numCells_vs_time',
    )

def plot_numCells_vs_threshold(dataBins):

    plotData  = gather_numCells_data(dataBins)

    plot_vs_threshold(
        plotData   = plotData,
        ymin       = 0,
        ymax       = 600,
        ylabel     = 'number of scheduled cells',
        filename   = 'numCells_vs_threshold',
    )

def plot_numCells_otfActivity_vs_time(dataBins):

    plotData  = gather_numCells_data(dataBins)

    plotDataNumCells = plot_vs_time(
        plotData   = plotData,
        doPlot     = False,
    )

    (otfAddData,otfRemoveData) = plot_otfActivity_vs_time(
        dataBins   = dataBins,
        doPlot     = False,
    )

    #===== plot

    allaxes = []
    pkPeriods           = []
    otfThresholds       = []
    for (otfThreshold,pkPeriod) in plotDataNumCells.keys():
        pkPeriods      += [pkPeriod]
        otfThresholds  += [otfThreshold]
    pkPeriods           = sorted(list(set(pkPeriods)))
    otfThresholds       = sorted(list(set(otfThresholds)), reverse=True)

    fig = matplotlib.pyplot.figure(figsize=(8, 4))

    #=== otfActivity

    def plotForEachPkPeriodOtfActivity(ax,plotData,pkPeriod_p):
        plots = []
        for th in otfThresholds:
            for ((otfThreshold,pkPeriod),data) in plotData.items():
                if otfThreshold==th and pkPeriod==pkPeriod_p:
                    plots += [
                        ax.errorbar(
                            x        = data['x'],
                            y        = data['y'],
                            yerr     = data['yerr'],
                            color    = COLORS_TH[th],
                            ls       = LINESTYLE_TH[th],
                            ecolor   = ECOLORS_TH[th],
                        )
                    ]
        return tuple(plots)

    def maxY(plotData):
        returnVal = []
        for ((otfThreshold,pkPeriod),data) in plotData.items():
            returnVal += data['y']
        return max(returnVal)

    # plot axis
    ax = fig.add_axes([0.12, 0.54, 0.85, 0.40])
    ax.set_xlim(xmin= 0,xmax=100)
    ax.set_ylim(ymin=-4,ymax=8)
    ax.annotate(
        'max. value {0:.0f}'.format(maxY(otfAddData)),
        xy=(10, 7.9),
        xycoords='data',
        xytext=(22, 4),
        textcoords='data',
        arrowprops=dict(arrowstyle="->",facecolor='black'),
        horizontalalignment='right',
        verticalalignment='top',
    )
    ax.annotate(
        'add cells',
        xytext=(50,0.2),
        xy    =(50,3.8),
        xycoords='data',
        textcoords='data',
        arrowprops=dict(arrowstyle="->",facecolor='black'),
        horizontalalignment='center',
        verticalalignment='bottom',
    )
    ax.annotate(
        'remove cells',
        xytext=(50,-0.2),
        xy    =(50,-3.8),
        xycoords='data',
        textcoords='data',
        arrowprops=dict(arrowstyle="->",facecolor='black'),
        horizontalalignment='center',
        verticalalignment='top',
    )
    plotForEachPkPeriodOtfActivity(ax,otfAddData,pkPeriod)
    plotForEachPkPeriodOtfActivity(ax,otfRemoveData,pkPeriod)
    allaxes += [ax]

    # add x/y labels
    ax.set_xticks([])
    ax.set_ylabel('num. add/remove OTF\noperations per cycle')

    #=== numCells

    # plot axis
    ax = fig.add_axes([0.12, 0.14, 0.85, 0.40])
    ax.set_xlim(xmin=0,xmax=100)
    ax.set_ylim(ymin=0,ymax=199)
    plots = []
    for th in otfThresholds:
        for ((otfThreshold,pkPeriod),data) in plotDataNumCells.items():
            if otfThreshold==th:
                plots += [
                    ax.errorbar(
                        x        = data['x'],
                        y        = data['y'],
                        yerr     = data['yerr'],
                        color    = COLORS_TH[th],
                        ls       = LINESTYLE_TH[th],
                        ecolor   = ECOLORS_TH[th],
                    )
                ]
    legendPlots = tuple(plots)

    # add x/y labels
    ax.set_xlabel('time (slotframe cycles)')
    ax.set_ylabel('number of\nscheduled cells')
    ax.annotate(
        'first burst\n(5 packets per node)',
        xy=(20, 120),
        xycoords='data',
        xytext=(20, 35),
        textcoords='data',
        arrowprops=dict(arrowstyle="->",facecolor='black'),
        horizontalalignment='center',
        verticalalignment='center',
    )
    ax.annotate(
        'second burst\n(5 packets per node)',
        xy=(60, 120),
        xycoords='data',
        xytext=(60, 35),
        textcoords='data',
        arrowprops=dict(arrowstyle="->",facecolor='black'),
        horizontalalignment='center',
        verticalalignment='center',
    )

    #=== legend

    legendText = tuple(['OTF threshold {0} cells'.format(t) for t in otfThresholds])
    fig.legend(
        legendPlots,
        legendText,
        'upper right',
        prop={'size':11},
    )

    allaxes += [ax]

    matplotlib.pyplot.savefig(os.path.join(DATADIR,'numCells_otfActivity_vs_time.png'))
    matplotlib.pyplot.savefig(os.path.join(DATADIR,'numCells_otfActivity_vs_time.eps'))
    matplotlib.pyplot.close('all')

#===== otfActivity

def plot_otfActivity_vs_time(dataBins,doPlot=True):

    prettyp   = False

    # gather raw add/remove data
    otfAddData     = {}
    otfRemoveData  = {}
    for ((otfThreshold,pkPeriod),filepaths) in dataBins.items():
        otfAddData[   (otfThreshold,pkPeriod)] = gatherPerCycleData(filepaths,'otfAdd')
        otfRemoveData[(otfThreshold,pkPeriod)] = gatherPerCycleData(filepaths,'otfRemove')

    # otfAddData = {
    #     (otfThreshold,pkPeriod) = {
    #         0: [12,12,12,12,12,12,12,12,12],
    #         1: [12,12,12,12,12,0,0,0,0],
    #     }
    # }
    # otfRemoveData = {
    #     (otfThreshold,pkPeriod) = {
    #         0: [12,12,12,12,12,12,12,12,12],
    #         1: [12,12,12,12,12,0,0,0,0],
    #     }
    # }

    if prettyp:
        with open('templog.txt','w') as f:
            f.write('\n============ {0}\n'.format('gather raw add/remove data'))
            f.write(pp.pformat(otfAddData))
            f.write(pp.pformat(otfRemoveData))

    #===== format data

    # calculate mean and confidence interval
    for ((otfThreshold,pkPeriod),perCycleData) in otfAddData.items():
        for cycle in perCycleData.keys():
            (m,confint) = calcMeanConfInt(perCycleData[cycle])
            perCycleData[cycle] = {
                'mean':      m,
                'confint':   confint,
            }
    for ((otfThreshold,pkPeriod),perCycleData) in otfRemoveData.items():
        for cycle in perCycleData.keys():
            (m,confint) = calcMeanConfInt(perCycleData[cycle])
            perCycleData[cycle] = {
                'mean':      -m,
                'confint':   confint,
            }

    # otfAddData = {
    #     (otfThreshold,pkPeriod) = {
    #         0: {'mean': 12, 'confint':12},
    #         1: {'mean': 12, 'confint':12},
    #     }
    # }
    # otfRemoveData = {
    #     (otfThreshold,pkPeriod) = {
    #         0: {'mean': 12, 'confint':12},
    #         1: {'mean': 12, 'confint':12},
    #     }
    # }

    if prettyp:
        with open('templog.txt','w') as f:
            f.write('\n============ {0}\n'.format('calculate mean and confidence interval'))
            f.write(pp.pformat(otfAddData))
            f.write(pp.pformat(otfRemoveData))

    # arrange to be plotted
    for ((otfThreshold,pkPeriod),perCycleData) in otfAddData.items():
        x     = sorted(perCycleData.keys())
        y     = [perCycleData[i]['mean']    for i in x]
        yerr  = [perCycleData[i]['confint'] for i in x]
        assert len(x)==len(y)==len(yerr)

        otfAddData[(otfThreshold,pkPeriod)] = {
            'x':        x,
            'y':        y,
            'yerr':     yerr,
        }
    for ((otfThreshold,pkPeriod),perCycleData) in otfRemoveData.items():
        x     = sorted(perCycleData.keys())
        y     = [perCycleData[i]['mean']    for i in x]
        yerr  = [perCycleData[i]['confint'] for i in x]
        assert len(x)==len(y)==len(yerr)

        otfRemoveData[(otfThreshold,pkPeriod)] = {
            'x':        x,
            'y':        y,
            'yerr':     yerr,
        }

    # otfAddData = {
    #     (otfThreshold,pkPeriod) = {
    #         'x':      [ 0, 1, 2, 3, 4, 5, 6],
    #         'y':      [12,12,12,12,12,12,12],
    #         'yerr':   [12,12,12,12,12,12,12],
    #     }
    # }
    # otfRemoveData = {
    #     (otfThreshold,pkPeriod) = {
    #         'x':      [ 0, 1, 2, 3, 4, 5, 6],
    #         'y':      [12,12,12,12,12,12,12],
    #         'yerr':   [12,12,12,12,12,12,12],
    #     }
    # }

    if prettyp:
        with open('templog.txt','w') as f:
            f.write('\n============ {0}\n'.format('arrange to be plotted'))
            f.write(pp.pformat(otfAddData))
            f.write(pp.pformat(otfRemoveData))

    if not doPlot:
        return (otfAddData,otfRemoveData)

    pkPeriods           = []
    otfThresholds       = []
    for (otfThreshold,pkPeriod) in otfAddData.keys():
        pkPeriods      += [pkPeriod]
        otfThresholds  += [otfThreshold]
    pkPeriods           = sorted(list(set(pkPeriods)))
    otfThresholds       = sorted(list(set(otfThresholds)), reverse=True)

    #===== plot

    fig = matplotlib.pyplot.figure()

    def plotForEachPkPeriod(ax,plotData,pkPeriod_p):
        #ax.set_xlim(xmin=poi,xmax=poi)
        #ax.set_ylim(ymin=0,ymax=50)
        if pkPeriod_p!='NA':
            ax.text(1,70,'packet period {0}s'.format(pkPeriod_p))
        plots = []
        for th in otfThresholds:
            for ((otfThreshold,pkPeriod),data) in plotData.items():
                if otfThreshold==th and pkPeriod==pkPeriod_p:
                    plots += [
                        ax.errorbar(
                            x        = data['x'],
                            y        = data['y'],
                            yerr     = data['yerr'],
                            color    = COLORS_TH[th],
                            ls       = LINESTYLE_TH[th],
                            ecolor   = ECOLORS_TH[th],
                        )
                    ]
        return tuple(plots)

    # plot axis
    allaxes = []
    subplotHeight = 0.85/len(pkPeriods)
    for (plotIdx,pkPeriod) in enumerate(pkPeriods):
        ax = fig.add_axes([0.12, 0.10+plotIdx*subplotHeight, 0.85, subplotHeight])
        legendPlots = plotForEachPkPeriod(ax,otfAddData,pkPeriod)
        legendPlots = plotForEachPkPeriod(ax,otfRemoveData,pkPeriod)
        allaxes += [ax]

    # add x label
    for ax in allaxes[1:]:
        ax.get_xaxis().set_visible(False)
    allaxes[0].set_xlabel('time (slotframe cycles)')

    # add y label
    allaxes[int(len(allaxes)/2)].set_ylabel('number of add/remove OTF\noperations per cycle')

    # add legend
    legendText = tuple(['OTF threshold {0} cells'.format(t) for t in otfThresholds])
    fig.legend(
        legendPlots,
        legendText,
        'upper right',
        prop={'size':8},
    )

    matplotlib.pyplot.savefig(os.path.join(DATADIR,'otfActivity_vs_time.png'))
    matplotlib.pyplot.savefig(os.path.join(DATADIR,'otfActivity_vs_time.eps'))
    matplotlib.pyplot.close('all')

def gather_sumOtfActivity_data(dataBins):

    prettyp   = False

    # gather raw add/remove data
    otfAddData     = {}
    otfRemoveData  = {}
    for ((otfThreshold,pkPeriod),filepaths) in dataBins.items():
        otfAddData[   (otfThreshold,pkPeriod)] = gatherPerCycleData(filepaths,'otfAdd')
        otfRemoveData[(otfThreshold,pkPeriod)] = gatherPerCycleData(filepaths,'otfRemove')

    # otfAddData = {
    #     (otfThreshold,pkPeriod) = {
    #         0: [12,12,12,12,12,12,12,12,12],
    #         1: [12,12,12,12,12,0,0,0,0],
    #     }
    # }
    # otfRemoveData = {
    #     (otfThreshold,pkPeriod) = {
    #         0: [12,12,12,12,12,12,12,12,12],
    #         1: [12,12,12,12,12,0,0,0,0],
    #     }
    # }

    assert sorted(otfAddData.keys())==sorted(otfRemoveData.keys())
    for otfpk in otfAddData.keys():
        assert sorted(otfAddData[otfpk].keys())==sorted(otfRemoveData[otfpk].keys())

    # sum up number of add/remove operations

    plotData = {}
    for otfpk in otfAddData.keys():
        plotData[otfpk] = {}
        for cycle in otfAddData[otfpk].keys():
            plotData[otfpk][cycle] = [sum(x) for x in zip(otfAddData[otfpk][cycle],otfRemoveData[otfpk][cycle])]

    # plotData = {
    #     (otfThreshold,pkPeriod) = {
    #         0: [12,12,12,12,12,12,12,12,12],
    #         1: [12,12,12,12,12,0,0,0,0],
    #     }
    # }

    if prettyp:
        with open('templog.txt','w') as f:
            f.write('\n============ {0}\n'.format('gather raw data'))
            f.write(pp.pformat(plotData))

    return plotData

def plot_otfActivity_vs_threshold(dataBins):

    plotData  = gather_sumOtfActivity_data(dataBins)

    plot_vs_threshold(
        plotData   = plotData,
        ymin       = 0,
        ymax       = 25,
        ylabel     = 'number of add/remove OTF operations per cycle',
        filename   = 'otfActivity_vs_threshold',
    )


#===== reliability

def plot_reliability_vs_time(dataBins):

    prettyp = True

    #===== gather data

    for val_str in 'appGenerated', 'appReachesDagroot', 'txQueueFill':

        # gather raw add/remove data
        plotdata    = {}
        for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),filepaths) in dataBins.items():
            plotdata[(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)] = {
                i: list(k) for i,k in enumerate(
                    zip(*gatherPerRunData(filepaths, val_str).values())
                )
            }

        for b in [5, 10, 15]:
            for p in [1,2,3]:
                plot_vs_time(
                    plotData = dict(((th,per,alg),data) for (th,per,alg,par,buf),data in plotdata.items() if buf == b and par == p ),
                    ymin     = 0,
                    ymax     = 50,
                    ylabel   = val_str,
                    filename = val_str + '_vs_time_buf_{}_par_{}'.format(b,p),
                    withError = False,
                )

        plotdataCum = {}
        for ((otfThreshold,pkPeriod,algorith,parent_size,buffer_sizem),filepaths) in dataBins.items():
            plotdataCum[(otfThreshold,pkPeriod,algorith,parent_size,buffer_sizem)] = {
                i: list(k) for i,k in enumerate(
                   zip(*map(numpy.cumsum,
                            gatherPerRunData(filepaths, val_str).values()))
                )
            }

        for b in [5, 10, 15]:
            for p in [1,2,3]:
                plot_vs_time(
                    plotData = dict(((th,per,alg),data) for (th,per,alg,par,buf),data in plotdataCum.items() if buf == b and par == p ),
                    ymin     = 0,
                    ymax     = (400 if val_str == 'txQueueFill' else 105 ),
                    ylabel   = val_str + '_cum',
                    filename = val_str + '_cum_vs_time_buf_{}_par_{}'.format(b,p),
                    withError = False,
                )

def plot_reliability_vs_threshold(dataBins):

    prettyp = True

    #===== gather data

    # gather raw add/remove data
    appGeneratedData    = {}
    appReachedData      = {}
    txQueueFillData     = {}
    for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),filepaths) in dataBins.items():
        appGeneratedData[(otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)]=gatherPerRunData(filepaths,'appGenerated')
        appReachedData[  (otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)]=gatherPerRunData(filepaths,'appReachesDagroot')
        txQueueFillData[ (otfThreshold,pkPeriod,algorithm,parent_size,buffer_size)]=gatherPerRunData(filepaths,'txQueueFill')

    # appGeneratedData = {
    #     (otfThreshold,pkPeriod) = {
    #         (cpuID,runNum): [12,12,12,12,12,12,12,12,12],
    #         (cpuID,runNum): [12,12,12,12,12,0,0,0,0],
    #     }
    # }
    # appReachedData = {
    #     (otfThreshold,pkPeriod) = {
    #         (cpuID,runNum): [12,12,12,12,12,12,12,12,12],
    #         (cpuID,runNum): [12,12,12,12,12,0,0,0,0],
    #     }
    # }
    # txQueueFillData = {
    #     (otfThreshold,pkPeriod) = {
    #         (cpuID,runNum): [12,12,12,12,12,12,12,12,12],
    #         (cpuID,runNum): [12,12,12,12,12,0,0,0,0],
    #     }
    # }

    if prettyp:
        with open('templog.txt','w') as f:
            f.write('\n============ {0}\n'.format('gather raw add/remove data'))
            f.write('appGeneratedData={0}'.format(pp.pformat(appGeneratedData)))
            f.write('appReachedData={0}'.format(pp.pformat(appReachedData)))
            f.write('txQueueFillData={0}'.format(pp.pformat(txQueueFillData)))

    #===== format data

    # sum up appGeneratedData
    for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),perRunData) in appGeneratedData.items():
        for cpuID_runNum in perRunData.keys():
            perRunData[cpuID_runNum] = sum(perRunData[cpuID_runNum])
    # sum up appReachedData
    for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),perRunData) in appReachedData.items():
        for cpuID_runNum in perRunData.keys():
            perRunData[cpuID_runNum] = sum(perRunData[cpuID_runNum])
    # get last of txQueueFillData
    for ((otfThreshold,pkPeriod,algorithm,parent_size,buffer_size),perRunData) in txQueueFillData.items():
        for cpuID_runNum in perRunData.keys():
            perRunData[cpuID_runNum] = perRunData[cpuID_runNum][-1]

    # appGeneratedData = {
    #     (otfThreshold,pkPeriod) = {
    #         (cpuID,runNum): sum_over_all_cycles,
    #         (cpuID,runNum): sum_over_all_cycles,
    #     }
    # }
    # appReachedData = {
    #     (otfThreshold,pkPeriod) = {
    #         (cpuID,runNum): sum_over_all_cycles,
    #         (cpuID,runNum): sum_over_all_cycles,
    #     }
    # }
    # txQueueFillData = {
    #     (otfThreshold,pkPeriod) = {
    #         (cpuID,runNum): value_last_cycles,
    #         (cpuID,runNum): value_last_cycles,
    #     }
    # }

    if prettyp:
        with open('templog.txt','a') as f:
            f.write('\n============ {0}\n'.format('format data'))
            f.write('\nappGeneratedData={0}'.format(pp.pformat(appGeneratedData)))
            f.write('\nappReachedData={0}'.format(pp.pformat(appReachedData)))
            f.write('\ntxQueueFillData={0}'.format(pp.pformat(txQueueFillData)))

    #===== calculate the end-to-end reliability for each runNum

    reliabilityData = {}
    for otfThreshold_pkPeriod in appReachedData.keys():
        reliabilityData[otfThreshold_pkPeriod] = {}
        for cpuID_runNum in appReachedData[otfThreshold_pkPeriod]:
            g = float(appGeneratedData[otfThreshold_pkPeriod][cpuID_runNum])
            r = float(appReachedData[otfThreshold_pkPeriod][cpuID_runNum])
            q = float(txQueueFillData[otfThreshold_pkPeriod][cpuID_runNum])
            assert g>0
            reliability = (r+q)/g
            assert reliability>=0
            assert reliability<=1
            reliabilityData[otfThreshold_pkPeriod][cpuID_runNum] = reliability

    # reliabilityData = {
    #     (otfThreshold,pkPeriod) = {
    #         (cpuID,runNum): 0.9558,
    #         (cpuID,runNum): 1.0000,
    #     }
    # }

    if prettyp:
        with open('templog.txt','a') as f:
            f.write('\n============ {0}\n'.format('calculate the end-to-end reliability for each cycle'))
            f.write('reliabilityData={0}'.format(pp.pformat(reliabilityData)))

    # calculate the end-to-end reliability per (otfThreshold,pkPeriod)
    for otfThreshold_pkPeriod in reliabilityData.keys():
        vals = reliabilityData[otfThreshold_pkPeriod].values()
        (m,confint) = calcMeanConfInt(vals)
        reliabilityData[otfThreshold_pkPeriod] = {
            'mean':      m,
            'confint':   confint,
        }

    # reliabilityData = {
    #     (otfThreshold,pkPeriod) = {
    #         'mean': 12,
    #         'confint':12,
    #     }
    # }

    if prettyp:
        with open('templog.txt','a') as f:
            f.write('\n============ {0}\n'.format('calculate the end-to-end reliability per (otfThreshold,pkPeriod)'))
            f.write('reliabilityData={0}'.format(pp.pformat(reliabilityData)))

    pkPeriods           = []
    otfThresholds       = []
    algorithms          = []
    parent_sizes        = []
    buffer_sizes        = []
    for (otfThreshold,pkPeriod,algorithm,parent_size,buffer_size) in reliabilityData.keys():
        pkPeriods      += [pkPeriod]
        otfThresholds  += [otfThreshold]
        algorithms     += [algorithm]
        parent_sizes   += [parent_size]
        buffer_sizes   += [buffer_size]
    pkPeriods           = sorted(list(set(pkPeriods)))
    otfThresholds       = sorted(list(set(otfThresholds)), reverse=True)
    algorithms          = sorted(list(set(algorithms)))
    parent_sizes        = sorted(list(set(parent_sizes)))
    buffer_sizes        = sorted(list(set(buffer_sizes)))

     #===== plot

    fig, ax = matplotlib.pyplot.subplots()
    # matplotlib.pyplot.ylim(ymin=ymin,ymax=ymax)
    matplotlib.pyplot.ylim(ymin=0.94,ymax=1.015)
#    matplotlib.pyplot.xlabel('Parameters, (buffer,parents)')
    ax.set_ylabel('end-to-end reliability')
    bars = []
    legends = []
    offset = 0
    x = []
    for algorithm in algorithms:
        for threshold in otfThresholds:

            if algorithm == 'local_voting' and threshold != 0:
                continue

            d = {}
            for ((otfThreshold,pkPeriod,pkAlgorithm,parent_size,buffer_size),data) in reliabilityData.items():
                if otfThreshold == threshold and pkAlgorithm == algorithm:
                    d[buffer_size,parent_size] = data

            x     = sorted(d.keys())
            tics  = [i+.25+offset for i in range(len(x))]
            y     = [d[k]['mean'] for k in x]
            yerr  = [d[k]['confint'] for k in x]
            bars += [ax.bar(tics, y, 0.1, color= COLORS_TH[threshold ], edgecolor='black', hatch=FILLSTYLES_ALG[algorithm], ecolor=ECOLORS_TH[threshold], yerr=yerr)]
            legends += [ '{}, thr={}'.format(algorithm,threshold) ]
            offset += 0.15

    ax.set_xticks( [i+.25+offset/2 for i in range(len(x))])
    ax.set_xticklabels(x)
#    ax.legend( bars, legends)

##===== plot

#    fig = matplotlib.pyplot.figure()
#    matplotlib.pyplot.ylim(ymin=0.94,ymax=1.015)
#    matplotlib.pyplot.xlabel('OTF threshold (cells)')
#    matplotlib.pyplot.ylabel('end-to-end reliability')
#    for period in pkPeriods:

#       d = {}
#       for ((otfThreshold,pkPeriod),data) in reliabilityData.items():
#           if pkPeriod==period:
#               d[otfThreshold] = data
#       x     = sorted(d.keys())
#       y     = [d[k]['mean'] for k in x]
#       yerr  = [d[k]['confint'] for k in x]
#
#       matplotlib.pyplot.errorbar(
#           x        = x,
#           y        = y,
#           yerr     = yerr,
#           color    = COLORS_PERIOD[period],
#           ls       = LINESTYLE_PERIOD[period],
#           ecolor   = ECOLORS_PERIOD[period],
#           label    = 'packet period {0}s'.format(period)
#       )
#    matplotlib.pyplot.legend(prop={'size':10})
    matplotlib.pyplot.savefig(os.path.join(DATADIR,'reliability_vs_threshold.png'))
    matplotlib.pyplot.savefig(os.path.join(DATADIR,'reliability_vs_threshold.eps'))
    matplotlib.pyplot.close('all')

#============================ main ============================================

def main():

    dataBins = binDataFiles()

    plot_txQueueFill_vs_time(dataBins)
    plot_appReachesDagroot_vs_time(dataBins)
    plot_time_all_reached_vs_threshold(dataBins)
    plot_max_latency_vs_threshold(dataBins)
    plot_numRxCells_vs_time(dataBins)
    plot_chargeConsumed_vs_time(dataBins)
    plot_reliability_vs_time(dataBins)

#  OLD PLOTS

    # latency
#    plot_latency_vs_time(dataBins)
#    plot_latency_vs_threshold(dataBins)
#    plot_max_latency_vs_threshold(dataBins)
#    plot_time_all_reached_vs_threshold(dataBins)

    # Queue Delay
#    plot_max_queue_delay_vs_threshold(dataBins)
#    plot_ave_q_delay_vs_threshold(dataBins)


    # numCells
#    plot_numCells_vs_time(dataBins)
#    plot_numCells_vs_threshold(dataBins)
#    plot_numCells_otfActivity_vs_time(dataBins)

    # otfActivity
#    plot_otfActivity_vs_time(dataBins)
#    plot_otfActivity_vs_threshold(dataBins)

    # reliability
#    plot_reliability_vs_threshold(dataBins)

if __name__=="__main__":
    main()
