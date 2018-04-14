Local Voting TSCH
=================

Implementation of the Local Voting algorithm in the 6TiSCH Simulator, and some
simulation results. Comparison of Local Voting with OTF, thresholds 0,1,4,10,
1,2, and 3 parents, and 10 and 100 buffer size.

You can find eps and png figures of the results in folder bin/simData/

Some indicative results:

Aggregated Values vs parameters
===============================

### time_all_root
![time_all_root](bin/simData/time_all_root_vs_threshold_buf_100.png)

### max_latency
![max_latency](bin/simData/max_latency_vs_threshold_buf_100.png)

### latency
![latency](bin/simData/latency_vs_threshold_buf_100.png)

### chargeConsumedPerRecv
![chargeConsumedPerRecv](bin/simData/chargeConsumedPerRecv_vs_threshold_buf_100.png)

### chargeConsumed
![chargeConsumed](bin/simData/chargeConsumed_vs_threshold_buf_100.png)

### reliability
![reliability](bin/simData/reliability_vs_threshold_buf_100.png)

### max_txQueueFill
![max_txQueueFill](bin/simData/max_txQueueFill_vs_threshold_buf_100.png)

### txQueueFill
![txQueueFill](bin/simData/txQueueFill_vs_threshold_buf_100.png)

Some indicative scenarios
===================

Scenario parents: 1, packets: 25
------------------------------
### appGenerated_cum
![appGenerated_cum](bin/simData/appGenerated_cum_vs_time_buf_100_par_1_pkt_25.png)

### appReachesDagroot_cum
![appReachesDagroot_cum](bin/simData/appReachesDagroot_cum_vs_time_buf_100_par_1_pkt_25.png)

### appReachesDagroot
![appReachesDagroot](bin/simData/appReachesDagroot_vs_time_buf_100_par_1_pkt_25.png)

### chargeConsumed
![chargeConsumed](bin/simData/chargeConsumed_vs_time_buf_100_par_1_pkt_25.png)

### latency
![latency](bin/simData/latency_vs_time_buf_100_par_1_pkt_25.png)

### numRxCells
![numRxCells](bin/simData/numRxCells_vs_time_buf_100_par_1_pkt_25.png)

### txQueueFill
![txQueueFill](bin/simData/txQueueFill_vs_time_buf_100_par_1_pkt_25.png)

Scenario parents: 2, packets: 25
------------------------------
### appGenerated_cum
![appGenerated_cum](bin/simData/appGenerated_cum_vs_time_buf_100_par_2_pkt_25.png)

### appReachesDagroot_cum
![appReachesDagroot_cum](bin/simData/appReachesDagroot_cum_vs_time_buf_100_par_2_pkt_25.png)

### appReachesDagroot
![appReachesDagroot](bin/simData/appReachesDagroot_vs_time_buf_100_par_2_pkt_25.png)

### chargeConsumed
![chargeConsumed](bin/simData/chargeConsumed_vs_time_buf_100_par_2_pkt_25.png)

### latency
![latency](bin/simData/latency_vs_time_buf_100_par_2_pkt_25.png)

### numRxCells
![numRxCells](bin/simData/numRxCells_vs_time_buf_100_par_2_pkt_25.png)

### txQueueFill
![txQueueFill](bin/simData/txQueueFill_vs_time_buf_100_par_2_pkt_25.png)

Scenario parents: 3, packets: 25
------------------------------
### appGenerated_cum
![appGenerated_cum](bin/simData/appGenerated_cum_vs_time_buf_100_par_3_pkt_25.png)

### appReachesDagroot_cum
![appReachesDagroot_cum](bin/simData/appReachesDagroot_cum_vs_time_buf_100_par_3_pkt_25.png)

### appReachesDagroot
![appReachesDagroot](bin/simData/appReachesDagroot_vs_time_buf_100_par_3_pkt_25.png)

### chargeConsumed
![chargeConsumed](bin/simData/chargeConsumed_vs_time_buf_100_par_3_pkt_25.png)

### latency
![latency](bin/simData/latency_vs_time_buf_100_par_3_pkt_25.png)

### numRxCells
![numRxCells](bin/simData/numRxCells_vs_time_buf_100_par_3_pkt_25.png)

### txQueueFill
![txQueueFill](bin/simData/txQueueFill_vs_time_buf_100_par_3_pkt_25.png)

Scenario parents: 3, packets: 5
------------------------------
### appGenerated_cum
![appGenerated_cum](bin/simData/appGenerated_cum_vs_time_buf_100_par_3_pkt_25.png)

### appReachesDagroot_cum
![appReachesDagroot_cum](bin/simData/appReachesDagroot_cum_vs_time_buf_100_par_3_pkt_25.png)

### appReachesDagroot
![appReachesDagroot](bin/simData/appReachesDagroot_vs_time_buf_100_par_3_pkt_25.png)

### chargeConsumed
![chargeConsumed](bin/simData/chargeConsumed_vs_time_buf_100_par_3_pkt_25.png)

### latency
![latency](bin/simData/latency_vs_time_buf_100_par_3_pkt_25.png)

### numRxCells
![numRxCells](bin/simData/numRxCells_vs_time_buf_100_par_3_pkt_25.png)

### txQueueFill
![txQueueFill](bin/simData/txQueueFill_vs_time_buf_100_par_3_pkt_25.png)


The Remainder of this document is orginal README from the parent repository,
https://bitbucket.org/6tisch/simulator/src




The 6TiSCH Simulator
====================

Brought to you by:

* Thomas Watteyne (watteyne@eecs.berkeley.edu)
* Kazushi Muraoka (k-muraoka@eecs.berkeley.edu)
* Nicola Accettura (nicola.accettura@eecs.berkeley.edu)
* Xavier Vilajosana (xvilajosana@eecs.berkeley.edu)

Scope
-----

6TiSCH is an active IETF standardization working group which defines mechanisms to build and maintain communication schedules in tomorrow's Internet of (Important) Things. This simulator allows you to measure the performance of those different mechanisms under different conditions.

What is simulated:

* protocols
    * IEEE802.15.4e-2012 TSCH (http://standards.ieee.org/getieee802/download/802.15.4e-2012.pdf)
    * RPL (http://tools.ietf.org/html/rfc6550)
    * 6top (http://tools.ietf.org/html/draft-wang-6tisch-6top-sublayer)
    * On-The-Fly scheduling (http://tools.ietf.org/html/draft-dujovne-6tisch-on-the-fly)
* the "Pister-hack" propagation model with collisions
* the energy consumption model taken from
    * [A Realistic Energy Consumption Model for TSCH Networks](http://ieeexplore.ieee.org/xpl/login.jsp?tp=&arnumber=6627960&url=http%3A%2F%2Fieeexplore.ieee.org%2Fiel7%2F7361%2F4427201%2F06627960.pdf%3Farnumber%3D6627960). Xavier Vilajosana, Qin Wang, Fabien Chraim, Thomas Watteyne, Tengfei Chang, Kris Pister. IEEE Sensors, Vol. 14, No. 2, February 2014.

What is *not* simulated:

* downstream traffic

More about 6TiSCH:

| what             | where                                                               |
|------------------|---------------------------------------------------------------------|
| charter          | http://tools.ietf.org/wg/6tisch/charters                            |
| data tracker     | http://tools.ietf.org/wg/6tisch/                                    |
| mailing list     | http://www.ietf.org/mail-archive/web/6tisch/current/maillist.html   |
| source           | https://bitbucket.org/6tisch/                                       |

Gallery
-------

|  |  |  |
|--|--|--|
| ![](https://bytebucket.org/6tisch/simulator/raw/master/examples/run_0_topology.png) | ![](https://bytebucket.org/6tisch/simulator/raw/master/examples/run_0_timelines.png) | ![](https://bytebucket.org/6tisch/simulator/raw/master/examples/gui.png) |

Installation
------------

* Install Python 2.7
* Clone or download this repository
* To plot the graphs, you need Matplotlib and scipy. On Windows, Anaconda (http://continuum.io/downloads) is a good on-stop-shop.

Running
-------

* Run a simulation: `bin/simpleSim/runSim.py`
* Plot fancy graphs: `bin/simpleSim/plotStuff.py`

Use `bin/simpleSim/runSim.py --help` for a list of simulation parameters. In particular, use `--gui` for a graphical interface.

Code Organization
-----------------

* `bin/`: the script for you to run
* `SimEngine/`: the simulator
    * `Mote.py`: Models a 6TiSCH mote running the different standards listed above.
    * `Propagation.py`: Wireless propagation model.
    * `SimEngine.py`: Event-driven simulation engine at the core of this simulator.
    * `SimSettings.py`: Data store for all simulation settings.
    * `SimStats.py`: Periodically collects statistics and writes those to a file.
    * `Topology.py`: creates a topology of the motes in the network.
* `SimGui/`: the graphical user interface to the simulator

Issues and bugs
---------------

* Report at https://bitbucket.org/6tsch/simulator/issues
