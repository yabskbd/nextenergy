#!/usr/bin/python
import urllib2
from urllib import urlopen as openurl
import time
import os
import gzip
import calendar
import logging
## Custom Modules ##
import net_check as nc
import settings as st
################# START -- Fn's needed for writing data to text #################

## EFFECTS: writes a descriptive topline to the text file
##          that describes each data type
def write_topline():
    
    if st.sensorinfo["time"]["refreshurl"] != "null":
        st.open_file.write("Time,")
    
    for i in range (0,len(st.sensorinfo["sensors"])):  
        st.open_file.write(st.sensorinfo["sensors"][i]["legend"])
        st.open_file.write(",")
        
    st.open_file.write("\n") 

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
            return st.sensorinfo["datadirectory"] + yearb4_str + monthb4_str + dayb4_str + '/'

        dayb4_str = num_days_permonth[int(time.strftime("%m")) - 2]
        monthb4_str = str(int(time.strftime("%m")) - 1)
        if len(monthb4_str) == 1:
            monthb4_str = "0" + monthb4_str
        return st.sensorinfo["datadirectory"] + time.strftime("%Y") + monthb4_str + dayb4_str + '/'
        
    else:
        dayb4_str = str(int(time.strftime("%d")) - 1)
        if len(dayb4_str) == 1:
            dayb4_str = "0" + dayb4_str 
        return st.sensorinfo["datadirectory"] + time.strftime("%Y") + time.strftime("%m") + dayb4_str + '/'


## EFFECTS: 
##          Checks the current date and time of the file being written to in date_arr
##			if the file is old (a new hour has starts) then file_has_expired() 
##          compresses the file mentioned by dirpath and filename then updates
##          the hour and day as well as the directory path and filename.
##          Returns true if the file_name mentioned in array remains unchanged
##          else, returns false. 
def file_has_expired():
    switched_day = False
    new_file_created = False
    if (not day_is_current(st.date_arr[1])):
        switched_day = True
        dayb4_dirpath_name = dayb4_dirpath()
        st.date_arr[2] = st.sensorinfo["datadirectory"] + time.strftime("%Y") + time.strftime("%m") + time.strftime("%d") + '/'
        if (os.path.exists(st.date_arr[2])):
            logging.info(("Changing to directory: " + st.date_arr[2]))
            os.chdir(st.date_arr[2])
        else:
            logging.info(("Creating directory: " + st.date_arr[2]))
            os.mkdir(st.date_arr[2])
            os.chdir(st.date_arr[2])
        st.date_arr[1] = time.strftime('%j') # 0 - 364
        #open_file = open(date_arr[2] + date_arr[3], 'a')    don't know if this is needed
    if (not hour_is_current(st.date_arr[0])):
        new_file_created = True
        st.open_file.close() #compress the closed file and remove the uncompressed file
        if(switched_day):
            logging.info(("New day!"))
            logging.info(("Compressing: " + st.date_arr[3]))
            data_in = open(dayb4_dirpath_name + st.date_arr[3], 'rb')
            data_compress = gzip.open(dayb4_dirpath_name + st.date_arr[3] + '.gz', 'wb')
            data_compress.writelines(data_in)
            data_compress.close()
            data_in.close()
            os.remove(dayb4_dirpath_name + st.date_arr[3])
        else:
            logging.info(("Compressing: " + st.date_arr[3]))
            data_in = open(st.date_arr[2] + st.date_arr[3], 'rb')
            data_compress = gzip.open(st.date_arr[2] + st.date_arr[3] + '.gz', 'wb')
            data_compress.writelines(data_in)
            data_compress.close()
            data_in.close()
            os.remove(st.date_arr[2] + st.date_arr[3])
        #create new file for the new hour
        logging.info(("Creating: sensordata for hour: " + time.strftime('%H')))
        st.date_arr[3] = time.strftime("%Y") + time.strftime("%m") + time.strftime("%d") + '_' + time.strftime('%H') + '.txt'
        st.date_arr[0] = time.strftime('%H')
        st.open_file = open(st.date_arr[2] + st.date_arr[3], 'a')
        write_topline()
        st.open_file.close()
    
    return new_file_created

## EFFECTS: Updates z-wave sensor values and writes updated 
##          values to file specified by "open_file" (i.e data text file)
def write_data():
    st.SENSOR_DATA_ERR = False
    st.SENSOR_REF_ERR = False
    if(file_has_expired()):
        st.open_file = open(st.date_arr[2] + st.date_arr[3], 'a')
    if st.sensorinfo["time"]["refreshurl"] != "null":
        st.open_file.write(str(int(time.time())))
        st.open_file.write(",")

    for i in range (0,len(st.sensorinfo["sensors"])):
        nc.sustain_conn()
        if (st.sensorinfo["sensors"][i]["refreshurl"] != "null"):
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
                st.open_file.write("-1")
            else:
                try:
                    urldata = (urllib2.urlopen(str(st.sensorinfo["sensors"][i]["dataurl"]))).read()
                    val = urldata.strip()
                    #still have to deal with string/int/etc data! cant graph string
                    if "bool" in st.sensorinfo["sensors"][i]["interpret"]:
                        if "true" in val: st.open_file.write("1")
                        else: st.open_file.write("0")
                    elif "double" in st.sensorinfo["sensors"][i]["interpret"]:
                        rounded = '{0:.2f}'.format(float(val)) 
                        st.open_file.write(rounded)
                    else:
                        matchkey = (str(st.sensorinfo["sensors"][i]["interpret"])).strip()
                        if(val == matchkey): st.open_file.write("1")
                        else: st.open_file.write("0")
                except Exception, err:
                    if(st.SENSOR_DATA_ERR):
                        st.open_file.write("-1")
                        pass
                    else:
                        st.open_file.write("-1")
                        logging.error("Enountered a problem retrieving data from sensors")
                        st.SENSOR_DATA_ERR = True
                        pass
                        
        st.open_file.write(',')
    st.open_file.write('\n')

def loop_and_delay_write():
    while True:
        if(st.open_file.closed):
            st.open_file = open(st.date_arr[2] + st.date_arr[3], 'a')
            
        write_data(st.open_file)
        time.sleep(int(st.sensorinfo["delay"])/1000)
        if(not st.open_file.closed):
            st.open_file.close()


################ END -- Fn's needed for writing data to text #################
