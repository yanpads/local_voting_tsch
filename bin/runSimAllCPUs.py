#!/home/dimitriv/local/bin/python
'''
\brief Start batch of simulations concurrently.
Workload is distributed equally among CPU cores.
\author Thomas Watteyne <watteyne@eecs.berkeley.edu>
'''

import os
import time
import math
import multiprocessing
import fileinput

MIN_TOTAL_RUNRUNS = 10 # 500 # 94 # 500

def runOneSim(params):
    (cpuID,numRuns) = params
    command     = []
    # command     = ['ssh {0} "cd $PWD;'.format(host)]
    command    = ['python runSimOneCPU.py']
    command    += ['--numRuns {0}'.format(numRuns)]
    command    += ['--cpuID {0}'.format(cpuID)]
    # command    += ['--numPacketsBurst {0}'.format(5)]
    command    += ['--burstTimestamp {0}'.format(20)]
    command    += ['--pkPeriod {0}'.format(16)]
    command    += ['--buffer {0}'.format(100)]
    command    += ['--algorithm {0}'.format('local_voting')] # otf
    command    += ['--otfThreshold {0}'.format(0)]
    command    += ['--scheduler {0}'.format('none')] # deBras
    # command    += ['--numChans {0}'.format(1)]
    # command    += ['"']
    #command    += ['&']
    command     = ' '.join(command)
    print "Executing command '{0}'".format(command)
    os.system(command)

def printProgress(num_cpus):
    while True:
        time.sleep(1)
        output     = []
        for cpu in range(num_cpus):
            with open('cpu{0}.templog'.format(cpu),'r') as f:
                output += ['[cpu {0}] {1}'.format(cpu,f.read())]
        allDone = True
        for line in output:
            if line.count('ended')==0:
                allDone = False
        output = '\n'.join(output)
        # os.system('clear')
        # print output
        with open('progress.txt', 'w') as f:
            f.write(output)

        if allDone:
            break
    for cpu in range(num_cpus):
        os.remove('cpu{0}.templog'.format(cpu))

def buildSshParams():
    result = []
    i = 0
    for line in fileinput.input():
        (cores,host)=line.rstrip().split("/")
        cores = int(cores) if len(cores) > 0 else 0
        print "We read {0} {1}".format(cores, host)
        for j in range(int(cores)):
            result.append(host)
    return result


if __name__ == '__main__':
    multiprocessing.freeze_support()
    # ssh_params = buildSshParams()
    # print "The ssh params are {0}".format(ssh_params)
    # num_cpus = len(ssh_params) # multiprocessing.cpu_count()
    num_cpus = multiprocessing.cpu_count()
    runsPerCpu = int(math.ceil(float(MIN_TOTAL_RUNRUNS)/float(num_cpus)))
    pool = multiprocessing.Pool(num_cpus)
    pool.map_async(runOneSim,[(i,runsPerCpu) for i in range(num_cpus)])
    printProgress(num_cpus)
    raw_input("Done. Press Enter to close.")
