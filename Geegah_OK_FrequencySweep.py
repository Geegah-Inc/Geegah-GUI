
"""
Created on Wed Apr 21 12:08:55 2023

@author: jkuo, scottez, anujb
#Frequency sweep over several frames acquiring both echo and no-echo
"""
#%% Import Libraries
import fpga #rainer functions
import sys
import numpy as np
import matplotlib.pyplot as plt
import geegah_hp
import time
import cv2 #need to install opencv for this
import os
import math

#%% Make directories  to save files in
#top directory where files will be stored
 #change this to whatever you want your directory name to be
savedirname = "C:/Users/anujb/Downloads/fsweeptest2/"

if not os.path.exists(savedirname):
    os.makedirs(savedirname)
#folder to dump raw .dat files in 
rawdata_save_dir = savedirname + "rawdata/"
if not os.path.exists(rawdata_save_dir):
    os.makedirs(rawdata_save_dir)
#folder to dump baseline .dat files in 
basedata_save_dir = savedirname + "baseline/"
if not os.path.exists(basedata_save_dir):
    os.makedirs(basedata_save_dir)
#folder to store baseline with no echo files in 
BLNE_save_dir = savedirname + "rawdata_baseline_no_echo/"
if not os.path.exists(BLNE_save_dir):
    os.makedirs(BLNE_save_dir) 
#folder to dump raw .dat files in for no echo
rawdata_ne_save_dir = savedirname + "rawdata_no_echo/"
if not os.path.exists(rawdata_ne_save_dir):
    os.makedirs(rawdata_ne_save_dir)
#folder to store images in
img_save_dir = savedirname + "images/"
if not os.path.exists(img_save_dir):
    os.makedirs(img_save_dir)
#folder to store video in
vid_save_dir = savedirname + "video/"
if not os.path.exists(vid_save_dir):
    os.makedirs(vid_save_dir)

print("Done Setting Up Folders")
#%%IMAGING PARAMETERS

#Frequency sweep start, end, and delta
#Frequencies in MHz
f_start = 1840
f_end = 1841
f_delta = 0.5 #can be as low as 0.01
num_frames =  20#CHANGE THIS TO ACQUIRE MULTIPLE FRAMES at the same frequency. 

#Selection of firing/receiving pixels, ROI 
col_min = 0 #integer, 0<col_min<127
col_max = 64 #integer, 0<col_max<127
row_min = 0 #integer, 0<row_min<127
row_max = 64 #integer, 0<row_max<127
row_no = row_max - row_min
col_no = col_max - col_min
roi_param = [col_min, col_max, row_min, row_max]

#%% FPGA setup 
#YOU ONLY HAVE TO RUN THIS ONCE AT THE BEGINING OF RUNNING THIS SCRIPT
#RE-RUN THIS IF YOU RESTARTED THE CONSOLE or RECONNECTED THE BOARD
#IF THIS IS ALREADY RAN ONCE, YOU ONLY NEED TO RUN THE reload_board() for quick settings load
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
#freq = 1883.7
freq = f_start
OUTEN = 1 #0 to disable, 1 to enable
#Power setting: 0 for -4 dbm, 1 for -1 dbm (2 for +2dbm, 3 for +5 dbm but don't use)
PSET = 3 #RF power setting
#configure VCO
geegah_hp.configureVCO(xem,freq,OUTEN,PSET)
# setup default timing
term_count = 83

#ROI setting######################################
#this is the start and the end rows and column numbers
xem.SinglePixelMode(False)


xem.SetROI(col_min,col_max,row_min,row_max)
col_min = xem.GetRegField(xem.roi_start_col)
col_max = xem.GetRegField(xem.roi_end_col)
row_min = xem.GetRegField(xem.roi_start_row)
row_max = xem.GetRegField(xem.roi_end_row)
print("ROI register is (", col_min, col_max, row_min, row_max, ")")

#tuples to store timing settings
#(start logic state, I start, I end, Q start, Q end)
TX_SWITCH_EN_SETTINGS = (0, 19, 42, 19, 42) 
PULSE_AND_SETTINGS = (0, 20, 42, 20, 42) 
RX_SWITCH_EN_SETTINGS =( 0, 42, 82, 42, 82) 
GLOB_EN_SETTINGS = (1, 71, 1023, 71, 1023) 
LO_CTRL_SETTINGS = (1, 1023, 1023, 42, 1023) 
ADC_CAP_SETTINGS = (0, 80, 81, 80, 81)   # ADC_CAPTURE #80 81
#set the timing registers in the FPGA
#geegah_hp.configTiming(xem,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS)

#terminal count Noecho
NE_del = 90
term_count_NE = 83+NE_del

#TIME SETTINGS FOR NO ECHO
#tuples to store timing settings
#(start logic state, I start, I end, Q start, Q end)
TX_SWITCH_EN_SETTINGS_NE = (0, 19, 42, 19, 42) 
PULSE_AND_SETTINGS_NE = (0, 20, 42, 20, 42) 
RX_SWITCH_EN_SETTINGS_NE =( 0, 42, 82+NE_del, 42, 82+NE_del) 
GLOB_EN_SETTINGS_NE = (1, 71+NE_del, 1023, 71+NE_del, 1023) 
LO_CTRL_SETTINGS_NE = (1, 1023, 1023, 42, 1023)
ADC_CAP_SETTINGS_NE = (0, 80+NE_del, 81+NE_del, 80+NE_del, 81+NE_del)   # ADC_CAPTURE #80 81


#set all DACs to the same voltage
#2.5V  works well
#don't go above 2.9V, probably best not to go below 1V
DAC_VOLTAGE = 2.8
geegah_hp.setAllPixSameDAC(xem,DAC_VOLTAGE) #comment this line out to skip setting the DACs

#ADC to use
#0 for gain of 5, 1 for no gain
ADC_TO_USE = 0
#Save settings to a file
geegah_hp.saveSettingsFile(savedirname,bit_file_name,freq,OUTEN,PSET,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS,DAC_VOLTAGE,ADC_TO_USE)
#close the XEM (will be reopened later)
xem.Close()
time.sleep(0.05)
geegah_hp.configTiming(xem,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS)

print("Done initializing FPGA")

#%% ONLY RUN THIS AFTER THE FPGA CODE SETUP HAVE BEEN RUN ONCE
geegah_hp.reload_board(xem, f_start, roi_param)
#%%ACQUIRE BASELINE FRAMES FOR DIFFERENCE FREQUENCIES:

for myf in range(f_start*100,f_end*100,math.floor(f_delta*100)):
    
    f_to_use = myf/100
    geegah_hp.configTiming(xem,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,
                          RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS)
    geegah_hp.configureVCO_10khz_fsweep(xem,f_to_use,OUTEN,PSET)
    myf_base_file_name = basedata_save_dir + "basefreqsweep" + str(myf) +".dat"
    myf_base_data = geegah_hp.acqSingleFrameROI(xem, ADC_TO_USE, myf_base_file_name,
                                            roi_param[0], 
                                            roi_param[1], 
                                            roi_param[2],
                                            roi_param[3])
  
    time.sleep(0.1) 
    geegah_hp.configTiming(xem,term_count_NE,TX_SWITCH_EN_SETTINGS_NE,PULSE_AND_SETTINGS_NE,
                          RX_SWITCH_EN_SETTINGS_NE,GLOB_EN_SETTINGS_NE,LO_CTRL_SETTINGS_NE,ADC_CAP_SETTINGS_NE)
    myf_base_file_name_NE = BLNE_save_dir + "basefreqsweepne" + str(myf) +".dat"
    myf_base_data_ne = geegah_hp.acqSingleFrameROI(xem, ADC_TO_USE, myf_base_file_name_NE,
                                            roi_param[0], 
                                            roi_param[1], 
                                            roi_param[2],
                                            roi_param[3])
    time.sleep(0.1)
    print("Currently at frequency: ", myf, " MHz")

xem.Close()
print("Done Sweeping Baseline Frequencies, echo and no-echo")

#%%MEASURE THE SAMPLE FRAMES at different frequencies

#For instance, if you want to acquire continuous frames at few frequencies, you can set the frequency range and
#change the num_frame to the number of frame you want to acquire.
#The code will acquire multiple frequencies at 1 frame before moving on to the next frame. 

for cf in range(num_frames):
    for myf in range(f_start*100,f_end*100,math.floor(f_delta*100)):
  
        f_to_use = myf/100
        myf_data_file_name = rawdata_save_dir + "frame_" + str(cf) + "_freq_"+ str(myf) +".dat"
        geegah_hp.configTiming(xem,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS)
        geegah_hp.configureVCO_10khz_fsweep(xem,f_to_use,OUTEN,PSET)
        myf_meas_data = geegah_hp.acqSingleFrameROI(xem, ADC_TO_USE, myf_data_file_name,
                                                roi_param[0], 
                                                roi_param[1], 
                                                roi_param[2],
                                                roi_param[3])
        
        time.sleep(0.1)
        myf_data_file_name_ne = rawdata_ne_save_dir + "frame_" + str(cf) + "_freq_"+ str(myf) +".dat"
        geegah_hp.configTiming(xem,term_count_NE,TX_SWITCH_EN_SETTINGS_NE,PULSE_AND_SETTINGS_NE,RX_SWITCH_EN_SETTINGS_NE,GLOB_EN_SETTINGS_NE,LO_CTRL_SETTINGS_NE,ADC_CAP_SETTINGS_NE)
        myf_meas_data_ne = geegah_hp.acqSingleFrameROI(xem, ADC_TO_USE, myf_data_file_name_ne,
                                                roi_param[0], 
                                                roi_param[1], 
                                                roi_param[2],
                                                roi_param[3])
        time.sleep(0.1)
        
        
        
        print("Currently at frequency: ", myf, " MHz", "frame ", cf)
    print("Finished frame # ", cf)

xem.Close()
print("Done Sweeping DATA")

#%% PROCESSING DATA
#LOADING FRAMES
#CHANGE THE FOLLOWING VARIABLES IF LOADING AN OLD DATASET

savedirname = savedirname 
#Frequency sweep start, end, and delta
#Frequencies in MHz
f_start = 1840
f_end = 1841
f_delta = 0.5 #can be as low as 0.01
num_frames =  20#CHANGE THIS TO ACQUIRE MULTIPLE FRAMES at the same frequency. 
#Selection of firing/receiving pixels, ROI 
col_min = 0 #integer, 0<col_min<127
col_max = 64 #integer, 0<col_max<127
row_min = 0 #integer, 0<row_min<127
row_max = 64 #integer, 0<row_max<127
row_no = row_max - row_min
col_no = col_max - col_min
roi_param = [col_min, col_max, row_min, row_max]

#EXTRACTING AIR FREQUENCIES, frames
I_A_E = []#In phase, baseline, 
Q_A_E = []#Out of phase, baseline, Echo
I_A_NE = []#In phase, baseline, NoEcho
Q_A_NE = []#Out of phase, baseline,No Echo
MAG_A = []
PHASE_A = []
for myf in range(f_start*100,f_end*100,math.floor(f_delta*100)):

    AE_filename = savedirname+"baseline/"+"basefreqsweep" + str(myf) + ".dat"
    ANE_filename = savedirname+"rawdata_baseline_no_echo/"+"basefreqsweepne" + str(myf) + ".dat"

    I_ADC_AE, Q_ADC_AE, I_VOLTS_AE, Q_VOLTS_AE = geegah_hp.loadSavedRawDataROI(AE_filename,roi_param[0], 
    roi_param[1], 
    roi_param[2],
    roi_param[3])
    I_ADC_ANE, Q_ADC_ANE, I_VOLTS_ANE, Q_VOLTS_ANE = geegah_hp.loadSavedRawDataROI(ANE_filename,roi_param[0], 
    roi_param[1], 
    roi_param[2],
    roi_param[3])
    
    I_A_E.append(I_VOLTS_AE)
    Q_A_E.append(Q_VOLTS_AE)
    I_A_NE.append(I_VOLTS_ANE)
    Q_A_NE.append(Q_VOLTS_ANE)
    
    MAG_AIR =  np.abs((I_VOLTS_AE - I_VOLTS_ANE) + 1j * (Q_VOLTS_AE - Q_VOLTS_ANE))
    PHASE_AIR = np.angle((I_VOLTS_AE - I_VOLTS_ANE) + 1j * (Q_VOLTS_AE - Q_VOLTS_ANE))
    MAG_A.append(MAG_AIR)
    PHASE_A.append(PHASE_AIR)

print("FINISHED LOADING AIR FREQUENCY DATA")

#EXTRACTING SAMPLE FREQUENCIES, frames
#THESE LISTS would contain lists represingting different frequencies
#Each frequency list would contain the N frames acquired

I_S_E_f = [] #In phase, sample, Echo,
Q_S_E_f = []#Out of phase, sample, Echo
I_S_NE_f = []#In phase, sample, NoEcho
Q_S_NE_f = []#Out of phase, sample, NoEcho
MAG_f = []
PHASE_f = []
REF_COEF_f = []
ACOUSTIC_IMP_f = []
for myf in range(f_start*100,f_end*100,math.floor(f_delta*100)):
    I_S_E = [] #In phase, sample, Echo
    Q_S_E = []#Out of phase, sample, Echo
    I_S_NE = []#In phase, sample, NoEcho
    Q_S_NE = []#Out of phase, sample, NoEcho
    
    MAG= []
    PHASE = []
    REF_COEF = []
    ACOUSTIC_IMP = []
    f_counter = 0
    for frames in range(num_frames):

        ME_filename = savedirname+"rawdata/"+"frame_"+str(frames)+"_freq_"+str(myf)+".dat"
        MNE_filename = savedirname+"rawdata_no_echo/"+"frame_"+str(frames)+"_freq_"+str(myf)+".dat"
     
        I_ADC_SE, Q_ADC_SE, I_VOLTS_SE, Q_VOLTS_SE = geegah_hp.loadSavedRawDataROI(ME_filename,roi_param[0], 
        roi_param[1], 
        roi_param[2],
        roi_param[3])
        I_ADC_SNE, Q_ADC_SNE, I_VOLTS_SNE, Q_VOLTS_SNE = geegah_hp.loadSavedRawDataROI(MNE_filename,roi_param[0], 
        roi_param[1], 
        roi_param[2],
        roi_param[3])
        
        I_S_E.append(I_VOLTS_SE)
        Q_S_E.append(Q_VOLTS_SE)
        I_S_NE.append(I_VOLTS_SNE)
        Q_S_NE.append(Q_VOLTS_SNE)
        
        MAG_SAMP =  np.abs((I_VOLTS_SE - I_VOLTS_SNE) + 1j * (Q_VOLTS_SE - Q_VOLTS_SNE))
        PHASE_SAMP = np.angle((I_VOLTS_SE - I_VOLTS_SNE) + 1j * (Q_VOLTS_SE - Q_VOLTS_SNE))
        
        MAG.append(np.array(MAG_SAMP)-np.array(MAG_AIR[f_counter]))
        PHASE.append(np.array(PHASE_SAMP)-np.array(PHASE_AIR[f_counter]))
        Rcoef_MAT = np.array(MAG_SAMP)/np.array(MAG_AIR[f_counter])
        REF_COEF.append(Rcoef_MAT)
        Z = [geegah_hp.impedance_si(jj, array = True) for jj in Rcoef_MAT]
        ACOUSTIC_IMP.append(Z)
    
    f_counter = f_counter+1    
    I_S_E_f.append(I_S_E)
    Q_S_E_f.append(Q_S_E)
    I_S_NE_f.append(Q_S_NE)
    Q_S_NE_f.append(Q_S_NE)
    MAG_f.append(MAG)
    PHASE_f.append(PHASE)
    REF_COEF_f.append(Rcoef_MAT)
    ACOUSTIC_IMP_f.append(ACOUSTIC_IMP)
    
print("FINISHED LOADING SAMPLE FREQUENCY DATA with N FRAMES")

#%%PLOTTING

LIST_to_PLOT = ACOUSTIC_IMP_f
foldername = "Acoustic Impedance"
geegah_hp.imgvid_plot_fsweep(LIST_to_PLOT, savedirname, foldername, 
             start_freq = f_start, end_freq = f_end,
             step_freq = f_delta ,
             vmin = 0.3, vmax = 2)
