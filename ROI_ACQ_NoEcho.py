# -*- coding: utf-8 -*-
"""
Created on Sat 10262023

@author: scottez, jkuo, abaskota
"""

#%% Import Libraries
import fpga #rainer functions
import sys
import j_fp_vco #justin functions
import time
import os
import math
import matplotlib.pyplot as plt
#%%HELPER FUNCTIONS FOR POST PROCESSING

def loadSavedRawDataROI(file_name, c1 = 0,c2 = 128,r1 = 0,r2 = 128):
    f = open(file_name, 'rb')
    MYDAT = f.read()
    f.close()
    I_RAW, Q_RAW = convertToIQImageROI(MYDAT, c1, c2, r1, r2)
    I_ADC, Q_ADC, I_VOLTS, Q_VOLTS = convertADCToVolts(I_RAW, Q_RAW)
    return I_ADC, Q_ADC, I_VOLTS, Q_VOLTS


def convertADCToVolts(I_IMAGE, Q_IMAGE):
    I_IMAGE_ADC = I_IMAGE/16 #correct bit shift
    Q_IMAGE_ADC = Q_IMAGE/16 #correct bit shift
    I_IMAGE_VOLTS = I_IMAGE_ADC*1e-3 #convert to volts
    Q_IMAGE_VOLTS = Q_IMAGE_ADC*1e-3 #convert to volts
    return I_IMAGE_ADC, Q_IMAGE_ADC, I_IMAGE_VOLTS, Q_IMAGE_VOLTS


def convertToIQImageROI(byte_data, c1 = 0, c2 = 128, r1 = 0, r2 = 128):
    import numpy as np
    wi = 0
    rows = r2 - r1
    cols = c2 - c1
    imgBytesI = np.zeros(rows*cols)
    imgBytesQ = np.zeros(rows*cols)
    for row in range (rows):
        for col in range(cols):
            wi = row*rows + col
            iwrd = (byte_data[4 * wi + 0] + 256*byte_data[4 * wi + 1])
            qwrd = (byte_data[4 * wi + 2] + 256*byte_data[4 * wi + 3])
            imgBytesI[wi] = iwrd
            imgBytesQ[wi] = qwrd
            
            
            
    J_MYIMAGE_I=imgBytesI.reshape([rows,cols])
    J_MYIMAGE_Q=imgBytesQ.reshape([rows,cols])
    return J_MYIMAGE_I, J_MYIMAGE_Q

#%% Make directories  to save files in

#top directory where files will be stored
#CHANGE THE VARIABLE savedirname
#################################################################
savedirname = "C:/Users/anujb/Downloads/ROITEST/" #change this to whatever you want your directory name to be
#################################################################

if not os.path.exists(savedirname):
    os.makedirs(savedirname)

#folder to dump raw .dat files in for 1st acoustic echo data
rawdata_save_dir = savedirname + "rawdata_echo/"
if not os.path.exists(rawdata_save_dir):
    os.makedirs(rawdata_save_dir)

#folder to dump raw .dat files in for no echo
rawdata_ne_save_dir = savedirname + "rawdata_no_echo/"
if not os.path.exists(rawdata_ne_save_dir):
    os.makedirs(rawdata_ne_save_dir)

#folder to store images in
img_save_dir = savedirname + "images/"
if not os.path.exists(img_save_dir):
    os.makedirs(img_save_dir)

#folder to store images in
img_save_dir2 = savedirname + "images2/"
if not os.path.exists(img_save_dir2):
    os.makedirs(img_save_dir2)


#folder to store video in
vid_save_dir = savedirname + "video/"
if not os.path.exists(vid_save_dir):
    os.makedirs(vid_save_dir)
    
#folder to store video in
vid_save_dir2 = savedirname + "video2/"
if not os.path.exists(vid_save_dir2):
    os.makedirs(vid_save_dir2)

#folder to store csv files in 
csv_save_dir = savedirname + "csv/"
if not os.path.exists(csv_save_dir):
    os.makedirs(csv_save_dir)


#folder to store baseline with echo files in 
BLE_save_dir = savedirname + "rawdata_baseline_echo/"
if not os.path.exists(BLE_save_dir):
    os.makedirs(BLE_save_dir)

#folder to store baseline with no echo files in 
BLNE_save_dir = savedirname + "rawdata_baseline_no_echo/"
if not os.path.exists(BLNE_save_dir):
    os.makedirs(BLNE_save_dir)

print("Done Setting Up Folders")

#%% FPGA setup

#initialize FPGA
xem = fpga.fpga()
board_name = xem.BoardName()
if board_name != "XEM7305":
    print("Problem: board name = " + board_name)  
    sys.exit()
print("Board: " + xem.di.deviceID + " " + xem.di.serialNumber)

#bit file to use (before DAC changes)
bit_file_name = "xem7305_GG222.bit"
xem.Configure(bit_file_name) # use older bit file
print("Version: " + xem.Version() + " serial number " + str(xem.SerialNumber()))
print("Sys clock = %8.4f MHz" % xem.SysclkMHz())


#setup vco
#frequency in MHz with resolution of 0.1MHz
freq = 1853.0
OUTEN = 1 #0 to disable, 1 to enable
#Power setting: 0 for -4 dbm, 1 for -1 dbm (2 for +2dbm, 3 for +5 dbm but don't use)
PSET = 3 #RF power setting
#configure VCO
j_fp_vco.configureVCO(xem,freq,OUTEN,PSET)

# setup default timing

#terminal count
#if you make this longer, you also need to sample ADC (ADC_CAP_SETTINGS) later to see an effect
#otherwise the timing ends as soon as the ADC is done
term_count =  83

#tuples to store timing settings
#(start logic state, I start, I end, Q start, Q end)
TX_SWITCH_EN_SETTINGS = (0, 19, 42, 19, 42) 
PULSE_AND_SETTINGS = (0, 20, 42, 20, 42) 
RX_SWITCH_EN_SETTINGS =( 0, 42, 82, 42, 82) 
GLOB_EN_SETTINGS = (1, 71, 1023, 71, 1023) 
LO_CTRL_SETTINGS = (1, 1023, 1023, 42, 1023)
ADC_CAP_SETTINGS = (0, 80, 81, 80, 81)   # ADC_CAPTURE #80 81
#set the timing registers in the FPGA


#ROI setting######################################
#this is the start and the end rows and column numbers
col_start = 0
col_end = 63

row_start = 0
row_end = 63

row_no = row_end - row_start
col_no = col_end - col_start

xem.SetROI(col_start,col_end,row_start,row_end)
####################################################

col_min = xem.GetRegField(xem.roi_start_col)
col_max = xem.GetRegField(xem.roi_end_col)
row_min = xem.GetRegField(xem.roi_start_row)
row_max = xem.GetRegField(xem.roi_end_row)

print("ROI register is (", col_min, col_max, row_min, row_max, ")")

############################################
# SINGLE PIXEL SETTINGS###########

## Set single pixel mode and set the row and column of interest
xem.SinglePixelMode(False)
xem.SinglePixelRowCol(10, 10)

#############################################
xem.SetListeningOffsets(0, 0)

#xem.EnableVCOOutput(1)
xem.SelectFakeADC(0)

j_fp_vco.configTiming(xem,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS)

#don't go above 2.9V, probably best not to go below 1V
DAC_VOLTAGE = 2.8
j_fp_vco.setAllPixSameDAC(xem,DAC_VOLTAGE) #comment this line out to skip setting the DACs


#close the XEM (will be reopened later)
xem.Close()
time.sleep(0.05)
print("Done initializing FPGA")

#%% Select ADC to use and save settings to file
#ADC to use
#0 for gain of 5, 1 for no gain
ADC_TO_USE = 0

#Save settings to a file
j_fp_vco.saveSettingsFile(savedirname,bit_file_name,freq,OUTEN,PSET,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS,DAC_VOLTAGE,ADC_TO_USE)

#%%settings for no echo

term_count_NE = 83+90

#tuples to store timing settings
#(start logic state, I start, I end, Q start, Q end)
TX_SWITCH_EN_SETTINGS_NE = (0, 19, 42, 19, 42) 
PULSE_AND_SETTINGS_NE = (0, 20, 42, 20, 42) 
RX_SWITCH_EN_SETTINGS_NE =( 0, 42, 82+90, 42, 82+90) 
GLOB_EN_SETTINGS_NE = (1, 71+90, 1023, 71+90, 1023) 
LO_CTRL_SETTINGS_NE = (1, 1023, 1023, 42, 1023)
ADC_CAP_SETTINGS_NE = (0, 80+90, 81+90, 80+90, 81+90)   # ADC_CAPTURE #80 81

#%% Measure air baseline simplified
N_AIR_FRAMES = 1
N_ZERO_PAD = len(str(N_AIR_FRAMES))
myt_E = time.time()

xem.Open()
# Select ADC 2 and make sure the fake ADC is not selected
xem.SelectADC(ADC_TO_USE) #1 for ADC2, 0 for ADC1
xem.SelectFakeADC(0) #to deselect the fake ADC
# Disable pattern generator
xem.EnablePgen(0)

for mycount in range(N_AIR_FRAMES):
    #$#xem.Open()
    j_fp_vco.configTiming(xem,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS)
    air_baseline_echo_filename = BLE_save_dir + "DATA"+str(mycount).zfill(N_ZERO_PAD)+".dat"
    #air_baseline_echo_data = j_fp_vco.acqSingleFrame(xem, ADC_TO_USE, air_baseline_echo_filename)
    # Acquire a frame
    
    ## Reset the pipe FIFO
    xem.ResetFifo()
    ## Enable pipe transfers
    xem.EnablePipeTransfer(1)
    ## Start an acquisition
    xem.StartAcq()
    # Get one frame

    nbytes = ((col_max - col_min + 1) * (row_max - row_min + 1))*2*2
    nbytes = 1024 * math.ceil(nbytes/1024)

    air_baseline_echo_data = bytearray(nbytes)
    #check nbytes 
    #
    nbytes_r = xem.GetPipeData(air_baseline_echo_data) #return value should match the nbytes above 

    time.sleep(1)
    j_fp_vco.configTiming(xem,term_count_NE,TX_SWITCH_EN_SETTINGS_NE,PULSE_AND_SETTINGS_NE,RX_SWITCH_EN_SETTINGS_NE,GLOB_EN_SETTINGS_NE,LO_CTRL_SETTINGS_NE,ADC_CAP_SETTINGS_NE)
    air_baseline_noecho_filename = BLNE_save_dir + "DATA"+str(mycount).zfill(N_ZERO_PAD)+".dat"
    
    
    ## Reset the pipe FIFO
    xem.ResetFifo()
    ## Enable pipe transfers
    xem.EnablePipeTransfer(1)
    ## Start an acquisition
    xem.StartAcq()
    # Get one frame
    nbytes = ((col_max - col_min + 1) * (row_max - row_min + 1))*2*2
    nbytes = 1024 * math.ceil(nbytes/1024)
    air_baseline_noecho_data = bytearray(nbytes)
    nbytes = xem.GetPipeData(air_baseline_noecho_data)
    
    # write to file
    f = open(air_baseline_echo_filename, "wb")
    f.write(air_baseline_echo_data)
    f.close()
    # write to file
    f2 = open(air_baseline_noecho_filename, "wb")
    f2.write(air_baseline_noecho_data)
    f2.close()
    print("Currently at ", mycount)
    
    
xem.Close()

print("Done acquiring multiple baselines over echo and no echo")
myt_F = time.time()

#%% do real time imaging

N_SAMPLE_FRAMES = 10
N_ZERO_PAD_IM = len(str(N_SAMPLE_FRAMES))
time_stamp = []
i_myt_F = time.time()

xem.Open()
# Select ADC 2 and make sure the fake ADC is not selected
xem.SelectADC(ADC_TO_USE) #1 for ADC2, 0 for ADC1
xem.SelectFakeADC(0) #to deselect the fake ADC
# Disable pattern generator
xem.EnablePgen(0)

for mycount in range(N_SAMPLE_FRAMES):

    j_fp_vco.configTiming(xem,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS)
    meas_echo_filename = rawdata_save_dir + "DATA"+str(mycount).zfill(N_ZERO_PAD_IM)+".dat"
    # Acquire a frame

    ## Reset the pipe FIFO
    xem.ResetFifo()
    ## Enable pipe transfers
    xem.EnablePipeTransfer(1)
    ## Start an acquisition
    xem.StartAcq()
    # Get one frame
     
    nbytes = ((col_max - col_min + 1) * (row_max - row_min + 1))*2*2
    nbytes = 1024 * math.ceil(nbytes/1024)
    meas_echo_data = bytearray(nbytes)
    nbytes = xem.GetPipeData(meas_echo_data)

    time.sleep(1)
    j_fp_vco.configTiming(xem,term_count_NE,TX_SWITCH_EN_SETTINGS_NE,PULSE_AND_SETTINGS_NE,RX_SWITCH_EN_SETTINGS_NE,GLOB_EN_SETTINGS_NE,LO_CTRL_SETTINGS_NE,ADC_CAP_SETTINGS_NE)
    meas_noecho_filename = rawdata_ne_save_dir + "DATA"+str(mycount).zfill(N_ZERO_PAD_IM)+".dat"
    
    
    ## Reset the pipe FIFO
    xem.ResetFifo()
    ## Enable pipe transfers
    xem.EnablePipeTransfer(1)
    ## Start an acquisition
    xem.StartAcq()
    # Get one frame
    nbytes = ((col_max - col_min + 1) * (row_max - row_min + 1))*2*2
    nbytes = 1024 * math.ceil(nbytes/1024)
    meas_noecho_data = bytearray(nbytes)
    nbytes = xem.GetPipeData(meas_noecho_data)
    
    f = open(meas_echo_filename, "wb")
    f.write(meas_echo_data)
    f.close()

    # write to file
    f2 = open(meas_noecho_filename, "wb")
    f2.write(meas_noecho_data)
    f2.close()
    
    print("Currently at ", mycount)
    time.sleep(1)
xem.Close()

print("Done acquiring image data over echo and no echo")

myt_D = time.time()
total_time = myt_D - i_myt_F
print(total_time)
print('fps = '+str(N_SAMPLE_FRAMES/total_time))

######################POST PROCESSING#######################################
#%% LOADING BASELINE I, Q (echo and no-echo) 4 matrices for n acquisitions
#############################################################################

I_AE = []
I_ANE = []
Q_AE = []
Q_ANE = []

for mycount in range(N_AIR_FRAMES):
    air_baseline_echo_filename = BLE_save_dir + "DATA0.dat"
    air_baseline_noecho_filename = BLNE_save_dir + "DATA0.dat"
    I_ADC_AE, Q_ADC_AE, I_VOLTS_AE, Q_VOLTS_AE = loadSavedRawDataROI(air_baseline_echo_filename, col_start, col_end, row_start, row_end)
    I_ADC_ANE, Q_ADC_ANE, I_VOLTS_ANE, Q_VOLTS_ANE = loadSavedRawDataROI(air_baseline_noecho_filename, col_start, col_end, row_start, row_end)

    I_AE.append(I_VOLTS_AE)
    Q_AE.append(Q_VOLTS_AE)
    I_ANE.append(I_VOLTS_ANE)
    Q_ANE.append(Q_VOLTS_ANE)
    


    
#%% LOADING SAMLES I, Q (echo and no-echo) 4 matrices for n acquisitions

I_SE = []
I_SNE = []
Q_SE = []
Q_SNE = []
N_ZERO_PAD = 2
for mycount in range(N_SAMPLE_FRAMES):
    sample_baseline_echo_filename = rawdata_save_dir + "DATA"+str(mycount).zfill(N_ZERO_PAD)+".dat"
    sample_baseline_noecho_filename = rawdata_ne_save_dir + "DATA"+str(mycount).zfill(N_ZERO_PAD)+".dat"
    I_ADC_SE, Q_ADC_SE, I_VOLTS_SE, Q_VOLTS_SE = loadSavedRawDataROI(sample_baseline_echo_filename, col_start, col_end, row_start, row_end)
    I_ADC_SNE, Q_ADC_SNE, I_VOLTS_SNE, Q_VOLTS_SNE = loadSavedRawDataROI(sample_baseline_noecho_filename, col_start, col_end, row_start, row_end)

    I_SE.append(I_VOLTS_SE)
    Q_SE.append(Q_VOLTS_SE)
    I_SNE.append(I_VOLTS_SNE)
    Q_SNE.append(Q_VOLTS_SNE)

#%%
frame1 = Q_SE[0] - Q_AE[0]
frame8 = Q_SE[9] - Q_AE[0]
plt.imshow(frame8)
