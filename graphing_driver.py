#!/usr/bin/python
from multiprocessing import Process
import json
import socket
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import urllib2
import numpy as np
from urllib import urlopen as uopen
import time
import os
import gzip
import calendar
import logging

################# START -- Fn's needed for matplotlib FuncAnim #################
## is not allowed to have any inputs by definition in matplotlib
## data_gen is used to get one value from each data feature and return just 
## data point from each feature including time
def data_gen():
    t = data_gen.t 
    while True:
        newdata = []
        t += 0.05
        newdata.append(t)
        #refresh urls 
        for i in range (0,len(sensorinfo["sensors"])):
            if sensorinfo["sensors"][i]["refreshurl"] != "null":
                uopen(sensorinfo["sensors"][i]["refreshurl"])
        #append data
        for i in range (0,len(sensorinfo["sensors"])):
            url = uopen(sensorinfo["sensors"][i]["dataurl"]).read()
            dataArray = url.split('\n')
            val = dataArray[1]
            if "bool" in sensorinfo["sensors"][i]["interpret"]: 
                if "true" in val: 
                    newdata.append(int(sensorinfo["sensors"][i]["graphto"]))
                else: 
                    newdata.append(0)    
            elif "double" in sensorinfo["sensors"][i]["interpret"]: 
                newdata.append(val) 
            elif "string" in sensorinfo["sensors"][i]["interpret"]:
                matchkey = sensorinfo["sensors"][i]["interpret"][7:]
                val = val.replace("\r", "")
                if(val == matchkey): 
                    newdata.append(int(sensorinfo["sensors"][i]["graphto"]))
                else: 
                    newdata.append(0)
            else: 
                matchkey = (str(sensorinfo["sensors"][i]["interpret"])).strip()
                if(val == matchkey):
                    newdata.append(int(sensorinfo["sensors"][i]["graphto"]))
                else: 
                    newdata.append(0)
            
        yield newdata
           
## its input is implicitly defined to be the output from data_gen 
## run(data) is then used to take the values from data and store them
## into an aggregrated list of ALL the data collected. ALL the data is 
## then stored in the lines from each feature and the lines are returned
## and used by the FuncAnimation                   
def run(data):
    t = data[0]
    xmin, xmax = axes[0].get_xlim()
    if t >= xmax:
        logging.info(("Growing X-Axis..."))
        for i in axes:
            current_axis = i
            current_axis.set_xlim(xmin, 2*xmax)
            current_axis.figure.canvas.draw()

    for i,v in enumerate(data):
    	mydata[i].append(v)

    # Reset the lines
    for i in range(len(lines)): 
        current_line = lines[i]
        current_line.set_data(mydata[0], mydata[i+1])
    return lines

def graph_data():
    logging.info("Plotting graph")
    ani = animation.FuncAnimation(fig, run, data_gen, blit=True, interval=int(sensorinfo["delay"]), repeat=False)
    plt.show()

################# END -- Fn's needed for matplotlib FuncAnim #################

################# START -- Fn's needed for writing data to text #################

## EFFECTS: writes a descriptive topline to the text file
##          that describes each data type
def write_topline(open_file):
    
    if sensorinfo["time"]["refreshurl"] != "null":
        open_file.write("Time,")
    
    for i in range (0,len(sensorinfo["sensors"])):  
        open_file.write(sensorinfo["sensors"][i]["legend"])
        open_file.write(",")
        
    open_file.write("\n") 

#returns true if day_str is the current day, else returns false
def day_is_current(day_str):
    if(day_str == time.strftime("%j")): return True
    else: return False
#returns true if hour_str is the current hour, else returns false
def hour_is_current(hour_str):
    if(hour_str == time.strftime("%H")): return True
    else: return False       
                        
#returns a string containing the number of the day before the current day
def dayb4_dirpath():
    # can be indexed using int(time.strftime("%m")) 
    num_days_permonth = ['31','28','31','30','31','30','31','31','30','31','30','31']
    if(calendar.isleap(int(time.strftime("%Y")))): num_days_permonth[1] = '29'
    #if its the first day of the month
    if(int(time.strftime("%d")) == 1): 
        #if its january 1st
        if(int(time.strftime("%m")) == 1): 
            dayb4_str = num_days_permonth[11]
            monthb4_str = '12' #December
            yearb4_str = str(int(time.strftime("%Y")) - 1)      
            return sensorinfo["datadirectory"] + yearb4_str + monthb4_str + dayb4_str + '/'

        dayb4_str = num_days_permonth[int(time.strftime("%m")) - 2]
        monthb4_str = str(int(time.strftime("%m")) - 1)
        if len(monthb4_str) == 1:
            monthb4_str = "0" + monthb4_str
        return sensorinfo["datadirectory"] + time.strftime("%Y") + monthb4_str + dayb4_str + '/'
        
    else:
        dayb4_str = str(int(time.strftime("%d")) - 1)
        if len(dayb4_str) == 1:
            dayb4_str = "0" + dayb4_str 
        return sensorinfo["datadirectory"] + time.strftime("%Y") + time.strftime("%m") + dayb4_str + '/'


## EFFECTS: takes in a an array consisting of 
##          [hour, day, directory path (DEPENDENT UPON THE CURRENT DAY), filename]
##          then checks if the hour and day are out of date and if so it 
##          compresses the file mentioned by dirpath and filename then updates
##          the hour and day as well as the directory path and filename.
##          Returns true if the file_name mentioned in array remains unchanged
##          else, returns false. 
def file_has_expired(open_file):
    switched_day = False
    new_file_created = False
    if (not day_is_current(date_arr[1])):
        switched_day = True
        dayb4_dirpath_name = dayb4_dirpath()
        date_arr[2] = sensorinfo["datadirectory"] + time.strftime("%Y") + time.strftime("%m") + time.strftime("%d") + '/'
        if (os.path.exists(date_arr[2])):
            logging.info(("Changing to directory: " + date_arr[2]))
            os.chdir(date_arr[2])
        else:
            logging.info(("Creating directory: " + date_arr[2]))
            os.mkdir(date_arr[2])
            os.chdir(date_arr[2])
        date_arr[1] = time.strftime('%j') # 0 - 364
        #open_file = open(date_arr[2] + date_arr[3], 'a')    don't know if this is needed
    if (not hour_is_current(date_arr[0])):
        new_file_created = True
        open_file.close() #compress the closed file and remove the uncompressed file
        if(switched_day):
            logging.info(("New day!"))
            logging.info(("Compressing: " + date_arr[3]))
            data_in = open(dayb4_dirpath_name + date_arr[3], 'rb')
            data_compress = gzip.open(dayb4_dirpath_name + date_arr[3] + '.gz', 'wb')
            data_compress.writelines(data_in)
            data_compress.close()
            data_in.close()
            os.remove(dayb4_dirpath_name + date_arr[3])
        else:
            logging.info(("Compressing: " + date_arr[3]))
            data_in = open(date_arr[2] + date_arr[3], 'rb')
            data_compress = gzip.open(date_arr[2] + date_arr[3] + '.gz', 'wb')
            data_compress.writelines(data_in)
            data_compress.close()
            data_in.close()
            os.remove(date_arr[2] + date_arr[3])
        #create new file for the new hour
        logging.info(("Creating: sensordata hour: " + time.strftime('%H')))
        date_arr[3] = time.strftime("%Y") + time.strftime("%m") + time.strftime("%d") + '_' + time.strftime('%H') + '.txt'
        date_arr[0] = time.strftime('%H')
        open_file = open(date_arr[2] + date_arr[3], 'a')
        write_topline(open_file)
        open_file.close()
    
    return new_file_created

## EFFECTS: Updates z-wave sensor values and writes updated 
##          values to file specified by "open_file" (i.e data text file)
def write_data(open_file):

    if(file_has_expired(open_file)):
        open_file = open(date_arr[2] + date_arr[3], 'a')
    if sensorinfo["time"]["refreshurl"] != "null":
        open_file.write(str(int(time.time())))
        open_file.write(",")
    for i in range (0,len(sensorinfo["sensors"])):
	if (sensorinfo["sensors"][i]["refreshurl"] != "null"):
            uopen(sensorinfo["sensors"][i]["refreshurl"])
        url = uopen(sensorinfo["sensors"][i]["dataurl"]).read()
        dataArray = url.split('\n')
        val = (dataArray[1]).strip()
        #still have to deal with string/int/etc data! cant graph string
        if "bool" in sensorinfo["sensors"][i]["interpret"]:
            if "true" in val: open_file.write("1")
            else: open_file.write("0")
            
        elif "double" in sensorinfo["sensors"][i]["interpret"]:
            rounded = '{0:.2f}'.format(float(val)) 
            open_file.write(rounded)

        else:
            matchkey = (str(sensorinfo["sensors"][i]["interpret"])).strip()
            if(val == matchkey): open_file.write("1")
            else: open_file.write("0")
            
        open_file.write(',')
                     
    open_file.write('\n')

def loop_and_delay_write():
    global open_file
    global logserverconnect
    counter = 0
    while True:
        if(open_file.closed):
            open_file = open(date_arr[2] + date_arr[3], 'a')
        if(counter % 5 == 0):
            if(not check_conn()):
                if(not logserverconnect):
                    logging.warning("Connection to z-way server lost...")
                    logserverconnect = True
            else:
	        if(logserverconnect):
                    logging.info("Connection to z-way server reestablished.")
                    logserverconnect = False
            
        write_data(open_file)
        time.sleep(int(sensorinfo["delay"])/1000)
        if(not open_file.closed):
            open_file.close()


################ END -- Fn's needed for writing data to text #################

################ START -- Error Checking Functions ##############

def check_conn():
    try:
        response = urllib2.urlopen("http://10.0.0.3:8083/", timeout=5)
        response.close()
        return True
    except urllib2.URLError, err: 
        logging.error("urllib2 URLError raised! No connection to server...")
        pass
    except socket.timeout, err: 
        logging.warning("Connection to server timed out...")
        return True
    return False

def good_conn():
    good_conn= False

    while(not good_conn):
        good_conn = check_conn()
        time.sleep(10)
        if(not good_conn):
            logging.warning("Cannot connect to z-way server... Attempting again")
    else:
        logging.info("Connection established...")

def sustain_conn():
    global logserverconnect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if os.system("ping -c 1 -W 1 10.0.0.3 2>&l >/dev/null") == 0:
        if(logserverconnect):
            logging.info("Connection to ZWay server reestablished!")
            logserverconnect = False
        result = sock.connect_ex(('10.0.0.3', 8083))
    else:
        logging.error("Connection to ZWay Server lost...")
        logserverconnect = True
        return

################ END -- Error Checking Functions ######################

################# START -- MAIN #################

logserverconnect = False

with open('/home/mjmor/PyScripts/json_files/ne_sensors.json') as json_file:
    sensorinfo = json.load(json_file)

FORMAT='%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT= '%m/%d/%Y %I:%M:%S %p'
logging.basicConfig(filename='/home/mjmor/SensorLog/ne_outlog.txt',level=logging.DEBUG, format=FORMAT, datefmt=DATE_FORMAT)

logging.info("RUNNING PI DATA GENERATION")

logging.info("Checking z-way server connection...")

good_conn()

################# START -- graph-only procedure #################

if(sensorinfo["generate"] == "graph" or sensorinfo["generate"] == "both"):
    logging.info("Initializing graph variables...")
    #data matrix, fist is x data
    mydata = []
    for i in range(len(sensorinfo["sensors"])+1):
        mydata.append([])         
    data_gen.t = 0
    fig = plt.figure(figsize=(13, 7)) #Set figure size
    
    #Add axes (as many as unique plots in JSON)
    axes = [] #list of all axes
    axespos = [] #list of each sensor's axis number
    maxyvals = [] #Determine y axis max limit
    for i in range (0,len(sensorinfo["sensors"])):
        axespos.append(sensorinfo["sensors"][i]["graphnumber"])   
    axespos = list(set(axespos))         
    for i in range (0,len(axespos)):
        axes.append(fig.add_subplot(len(axespos),1,i+1))
        maxyvals.append(0)  
    
    #Generate lines
    lines = []
    for i in range (0,len(sensorinfo["sensors"])):
        line, = axes[int(sensorinfo["sensors"][i]["graphnumber"])].plot([], [], lw=2, color = sensorinfo["sensors"][i]["linecolor"], label=sensorinfo["sensors"][i]["legend"])
        lines.append(line)
    
    #Determine each axis max y value
    for i in range (0,len(sensorinfo["sensors"])):
        if(maxyvals[int(sensorinfo["sensors"][i]["graphnumber"])] < int(sensorinfo["sensors"][i]["graphto"])):
            maxyvals[int(sensorinfo["sensors"][i]["graphnumber"])] = int(sensorinfo["sensors"][i]["graphto"]) + int(sensorinfo["sensors"][i]["graphto"])*0.1       
        
    #Set axis specs. Must be done AFTER lines are added.
    for i in range (0,len(axes)):  
        axes[i].grid()
        axes[i].set_ylim(-2, maxyvals[i])
        box = axes[i].get_position()
        axes[i].set_position([box.x0, box.y0, box.width * 0.8, box.height])
        axes[i].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        axes[i].set_xlim(0, 5)

    if(sensorinfo["generate"] == "graph"):
        graph_data()
################# END -- graph-only procedure #################

################# START -- data-only procedure #################

if(sensorinfo["generate"] == "data" or sensorinfo["generate"] == "both"):
    logging.info("Initialing data file variables...")
    dayof_dirpath = sensorinfo["datadirectory"] + time.strftime("%Y") + time.strftime("%m") + time.strftime("%d") + '/'
    if (os.path.exists(dayof_dirpath)):
        logging.info("Changing to directory: " + dayof_dirpath)
        os.chdir(dayof_dirpath)
    else:
        logging.info(("Creating directory: " + dayof_dirpath))
        os.mkdir(dayof_dirpath)
        os.chdir(dayof_dirpath)
    #create files on the hour
    logging.info("Creating: sensordata hour: " + time.strftime("%H"))
    temp_filename = time.strftime("%Y") + time.strftime("%m") + time.strftime("%d") + '_' + time.strftime("%H") + '.txt'
    open_file = open(dayof_dirpath + temp_filename,'w')
    hour_str = time.strftime("%H") #0 - 23
    day_str = time.strftime("%j") # 0 - 364
    write_topline(open_file)
    open_file.close()
    #create an array of the valuable information (info that can change) so that the variables within the array can 
    # be changed by functions that take the array as input
    date_arr = [hour_str, day_str, dayof_dirpath, temp_filename]

    if(sensorinfo["generate"] == "data"):
        loop_and_delay_write()

################# END -- data-only procedure #################

if(sensorinfo["generate"] == "both"):
    if __name__ == '__main__':
        p1 = Process(target = loop_and_delay_write)
        p1.start()
        graph_data()

################# END -- MAIN #################
