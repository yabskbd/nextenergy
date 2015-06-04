#!/usr/bin/python
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import logging
import settings as st
import urllib2
from urllib import urlopen as openurl

################# START -- Fn's needed for matplotlib FuncAnim #################
## is not allowed to have any inputs by definition in matplotlib
## data_gen is used to get one value from each data feature and return just 
## data point from each feature including time
def data_gen():
    st.SENSOR_REF_ERR = False
    st.SENSOR_DATA_ERR = False
    t = data_gen.t 
    while True:
        newdata = []
        t += 0.05
        newdata.append(t)
        #refresh urls 
        for i in range (len(st.sensorinfo["sensors"])):
            if st.sensorinfo["sensors"][i]["refreshurl"] != "null":
                try:
		    openurl(str(st.sensorinfo["sensors"][i]["refreshurl"]))
                except Exception, err:
                    if(st.SENSOR_REF_ERR):
                        pass
                    else:
                        st.SENSOR_REF_ERR = True
                        logging.error("Encountered a problem refreshing devices")
                        pass
                if(st.SENSOR_REF_ERR):
                    newdata.append(-1)
                else:		
                    try:
                        urldata = (urllib2.urlopen(str(st.sensorinfo["sensors"][i]["dataurl"]), timeout=1)).read()
                        val = urldata.strip()
                        if "bool" in st.sensorinfo["sensors"][i]["interpret"]:
                            if "true" in val:
                                newdata.append(int(st.sensorinfo["sensors"][i]["graphto"]))
                            else:
                                newdata.append(0)
                        elif "double" in st.sensorinfo["sensors"][i]["interpret"]:
                            newdata.append(val)
                        elif "string" in st.sensorinfo["sensors"][i]["interpret"]:
                            matchkey = (str(st.sensorinfo["sensors"][i]["interpret"])).strip()
                            if(val == matchkey): 
                                newdata.append(int(st.sensorinfo["sensors"][i]["graphto"]))
                            else: 
                                newdata.append(0)
                        else:
                            matchkey = (str(st.sensorinfo["sensors"][i]["interpret"])).strip()
                            if(val == matchkey): 
                                newdata.append(int(st.sensorinfo["sensors"][i]["graphto"]))
                            else: 
                                newdata.append(0)
                            logging.warning("Unrecognized data type from sensor %02d ", (i+1))
                    except Exception, err:
                        if(st.SENSOR_DATA_ERR):
                            newdata.append(-1)
                            pass
                        else:
                            logging.error("Encountered a problem retrieving data from devices")
                            newdata.append(-1)
                            st.SENSOR_DATA_ERR = True
                            pass
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

def init_graph():
    #data matrix, fist is x data
    mydata = []
    for i in range(len(st.sensorinfo["sensors"])+1):
        mydata.append([])
    data_gen.t = 0
    fig = plt.figure(figsize=(13, 7)) #Set figure size

    #Add axes (as many as unique plots in JSON)
    axes = [] #list of all axes
    axespos = [] #list of each sensor's axis number
    maxyvals = [] #Determine y axis max limit
    for i in range (0,len(st.sensorinfo["sensors"])):
        axespos.append(st.sensorinfo["sensors"][i]["graphnumber"])
    axespos = list(set(axespos))
    for i in range (0,len(axespos)):
        axes.append(fig.add_subplot(len(axespos),1,i+1))
        maxyvals.append(0)

    #Generate lines
    lines = []
    for i in range (0,len(st.sensorinfo["sensors"])):
        line, = axes[int(st.sensorinfo["sensors"][i]["graphnumber"])].plot([], [], lw=2, color = st.sensorinfo["sensors"][i]["linecolor"], label=st.sensorinfo["sensors"][i]["legend"])
        lines.append(line)
    
     #Determine each axis max y value
    for i in range (0,len(st.sensorinfo["sensors"])):
        if(maxyvals[int(st.sensorinfo["sensors"][i]["graphnumber"])] < int(st.sensorinfo["sensors"][i]["graphto"])):
            maxyvals[int(st.sensorinfo["sensors"][i]["graphnumber"])] = int(st.sensorinfo["sensors"][i]["graphto"]) + int(st.sensorinfo["sensors"][i]["graphto"])*0.1

    #Set axis specs. Must be done AFTER lines are added.
    for i in range (0,len(axes)):
        axes[i].grid()
        axes[i].set_ylim(-2, maxyvals[i])
        box = axes[i].get_position()
        axes[i].set_position([box.x0, box.y0, box.width * 0.8, box.height])
        axes[i].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        axes[i].set_xlim(0, 5)

def graph_data():
    logging.info("Plotting graph")
    graphani = animation.FuncAnimation(fig, run, data_gen, blit=True, interval=int(st.sensorinfo["delay"]), repeat=False)
    plt.show()
################# END -- Fn's needed for matplotlib FuncAnim #################

