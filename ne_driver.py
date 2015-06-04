#!/usr/bin/python
from multiprocessing import Process
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import os
import logging
## CUSTOM MODULES ##
import settings as st
import animate as ani
import data_logger as dl
import net_check as nc

################# START -- MAIN #################

FORMAT='%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT='%m/%d/%Y %I:%M:%S %p'
logging.basicConfig(filename='/var/log/nextenergy.log', level=logging.DEBUG, format=FORMAT, datefmt=DATE_FORMAT)

logging.info("RUNNING PI DATA GENERATION")

logging.info("Checking z-way server connection...")

nc.init_conn()

st.init()
st.check_settings()

################# START -- graph-only procedure #################

if(st.sensorinfo["generate"] == "graph" or st.sensorinfo["generate"] == "both"):
    logging.info("Initializing graph variables...")
    ani.init_graph()

    if(st.sensorinfo["generate"] == "graph"):
        ani.graph_data()
################# END -- graph-only procedure #################

################# START -- data-only procedure #################

if(st.sensorinfo["generate"] == "data" or st.sensorinfo["generate"] == "both"):
    dl.write_topline(st.open_file)
    st.open_file.close()

    if(st.sensorinfo["generate"] == "data"):
        dl.loop_and_delay_write()

################# END -- data-only procedure #################

if(st.sensorinfo["generate"] == "both"):
    if __name__ == '__main__':
        p1 = Process(target = loop_and_delay_write)
        p1.start()
        ani.graph_data()

################# END -- MAIN #################
