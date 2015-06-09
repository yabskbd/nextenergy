#!/usr/bin/python
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

Aeon_Lum =[]
Time=[]

file_loc="/Users/yeabserak/Documents/Merit/Code/nextenergy/data_input_grapher/data_input_grapher/20150609/20150609_10.txt"
fig = plt.figure(figsize=(13, 7)) ##Intialize Fig Size


with open(file_loc,"r") as data_file:
    topline_info=data_file.readline()
    
    for cur_data in data_file:
        cur_data=cur_data.split(",")
        Aeon_Lum.append(float(cur_data[3]))
        
        Time.append(int(cur_data[0]))





plt.plot(Time,Aeon_Lum,"r--")
plt.ylabel('Luminasity')
plt.axis([Time[0],Time[len(Time)-1],0,max(Aeon_Lum)+50])
plt.show()

data_file.close()


