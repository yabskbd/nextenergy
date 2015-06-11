#!/usr/bin/python
import numpy as np
import gzip
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
from datetime import datetime
import matplotlib.dates as mdates

Aeon_Lum =[]
Time=[]
Temp=[]
header_info=[]

temp_Time=[]
temp_Aeon_Lum=[]
temp_Temp=[]

#file_loc_1="/Users/yeabserak/Documents/Merit/Code/nextenergy/data_input_grapher/data_input_grapher/20150609/20150609_09.txt"
#file_loc_2="/Users/yeabserak/Documents/Merit/Code/nextenergy/data_input_grapher/data_input_grapher/20150609/20150609_10.txt"
fig = plt.figure(figsize=(15, 10)) ##Intialize Fig Size


def data_array(file):
    temp_time=[]
    temp_lum=[]
    temp_temp=[]
    with file as data_file:
        topline_info=data_file.readline()
        topline_info=topline_info.split(",")
        #print (topline_info)
        for cur_data in data_file:
            cur_data=cur_data.split(",")
            temp_lum.append(float(cur_data[3]))
            temp_temp.append(float(cur_data[2]))
            temp_time.append(datetime.fromtimestamp(int(cur_data[0])))
    return temp_time, temp_temp, temp_lum,topline_info

for j in range(20150610,20150611):
    for i in range(0,24):

        i=str(i)
        j=str(j)
        if len(i)==1:
            i='0'+i
        
        f = gzip.open('/Users/yeabserak/Documents/Merit/Code/nextenergy/data_input_grapher/data_input_grapher/'+j+'/'+j+'_'+i+'.txt.gz', 'rb')
        
        temp_Time,temp_Temp, temp_Aeon_Lum,header_info = data_array(f)
        Time.extend(temp_Time)
        Temp.extend(temp_Temp)
        Aeon_Lum.extend(temp_Aeon_Lum)




f.close()





plt.subplot(311)
plt.plot(Time,Aeon_Lum,"r--")
plt.axis([min(Time), max(Time), 0, max(Aeon_Lum)+1000])
plt.ylabel((header_info[3]))


plt.subplot(312)
plt.plot(Time,Temp,"b--")
plt.axis([min(Time), max(Time), 0, max(Temp)+20])
plt.ylabel((header_info[2]))


plt.xlabel('Time')
fig.autofmt_xdate()
plt.fmt_xdata = mdates.DateFormatter('%H-%M-%S')



plt.show()


#formatter = ticker.FormatStrFormatter('$%1.2f')
#ax.yaxis.set_major_formatter(formatter)
#
#for tick in ax.yaxis.get_major_ticks():
#    tick.label1On = False
#    tick.label2On = True
#    tick.label2.set_color('green')
#




