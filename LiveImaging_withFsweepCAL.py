
"""
Created on Tue Dec 19 16:15:13 2023

@author: jkuo, ab2297
"""
#%% Import Libraries
import fpga #rainer functions
import sys
import numpy as np
import matplotlib.pyplot as plt
import geegah_hp
import time
import os

#%% Make directories  to save files in
foldername = "OIL_ALC"
path = "C:/Users/anujb/Downloads"

savedirname = os.path.join(path, foldername, "")

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
img_save_dir2 = savedirname + "images/"
if not os.path.exists(img_save_dir2):
    os.makedirs(img_save_dir2)

#folder to store video in
vid_save_dir = savedirname + "video/"
if not os.path.exists(vid_save_dir):
    os.makedirs(vid_save_dir)
    
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

#folder to store baseline with no echo files in 
Fsweep_save_dir = savedirname + "Fsweep_CAL/"
if not os.path.exists(Fsweep_save_dir):
    os.makedirs(Fsweep_save_dir)

print("Done Setting Up Folders")

#%% Parameter selections

liveplot = True #boolean for plotting images real-time, True or False, set this as True for live plotting
frequency = 1853.5 #Pulse frequency in MHz, with resolution of 0.1 MHz

#Selection of firing/receiving pixels, ROI 
col_min = 0 #integer, 0<col_min<127
col_max = 127 #integer, 0<col_max<127
row_min = 0 #integer, 0<row_min<127
row_max = 127 #integer, 0<row_max<127

row_no = row_max - row_min
col_no = col_max - col_min
roi_param = [col_min, col_max, row_min, row_max]
num_Frames = 20 #Number of frames to acquire for sample, integer, num_Frames > 0

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
freq = frequency
OUTEN = 1 #0 to disable, 1 to enable
#Power setting: 0 for -4 dbm, 1 for -1 dbm (2 for +2dbm, 3 for +5 dbm but don't use)
PSET = 3 #RF power setting
#configure VCO
geegah_hp.configureVCO(xem,freq,OUTEN,PSET)
# setup default timing
term_count = 83

#ROI setting######################################
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

#%%RUN A FREQUENCY SWEEP FOR CALIBRATION
start_frequency = 1780
end_frequency = 1860
frequency_interval = 0.5

#frequency sweep
i,q,freqs = [],[],[]
#plot setup
plt.ion()
fig, ax = plt.subplots()
line1, = ax.plot([], [], label='I echo')  # Line for I values
line2, = ax.plot([], [], label='Q echo')  # Line for Q values
ax.set_xlabel('Frequency (MHz)')
ax.set_ylabel('Echo (V)')
ax.legend()
# lims
ax.set_xlim(start_frequency, end_frequency) 
ax.set_ylim(1,3)  
i_mat = []
q_mat = []

for freq in range(start_frequency*100,end_frequency*100,math.floor(frequency_interval*100)):
    freq = freq/100
    freqs.append(freq) 
    
    geegah_hp.configureVCO_10khz_fsweep(xem,freq,OUTEN,PSET) #SWITCH FREQUENCY
    myf_meas_data = geegah_hp.acqSingleFrameCAL(xem, ADC_TO_USE)

    geegah_hp.configureVCO_10khz_fsweep(xem,f_to_use,OUTEN,PSET)
    geegah_hp.configTiming(xem,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,
                          RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS)
    
    myf_file_name_echo = Fsweep_save_dir + "Frequecyecho" + str(f_to_use) +".dat"
    myf_data_echo = geegah_hp.acqSingleFrame_FSWEEP(xem, ADC_TO_USE, myf_file_name_echo)
    time.sleep(0.1) 
    geegah_hp.configTiming(xem,term_count_NE,TX_SWITCH_EN_SETTINGS_NE,PULSE_AND_SETTINGS_NE,
                          RX_SWITCH_EN_SETTINGS_NE,GLOB_EN_SETTINGS_NE,LO_CTRL_SETTINGS_NE,ADC_CAP_SETTINGS_NE)
    myf_file_name_noecho = Fsweep_save_dir + "Frequecynoecho" + str(f_to_use) +".dat"
    myf_base_data_ne = geegah_hp.acqSingleFrame_FSWEEP(xem, ADC_TO_USE, myf_file_name_noecho)                     
    time.sleep(0.1)
    
    I_ADC,Q_ADC,I_VOLTS,Q_VOLTS = geegah_hp.loadSavedRawDataFromBytes(myf_data_echo)
    i.append(I_VOLTS[64,64])
    q.append(Q_VOLTS[64,64])
    i_mat.append(I_VOLTS)
    q_mat.append(Q_VOLTS)
    
    # Set new data for the lines
    line1.set_xdata(freqs)
    line1.set_ydata(i)
    line2.set_xdata(freqs)
    line2.set_ydata(q)
    
    # Adjust the plot limits
    ax.relim()
    ax.autoscale_view()
    # Redraw the plot
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.01)
        
plt.ioff()  # Turn off interactive mode
plt.show()     

#%% ONLY RUN THIS AFTER THE FPGA CODE SETUP HAVE BEEN RUN ONCE
geegah_hp.reload_board(xem, frequency, roi_param)
#%% ACQUIRE BASELINE FRAMES: 
#CLEAN THE IMAGER RIGHT BEFORE YOU RUN THIS SECTION
#THIS ACQUIRES 10 baseline frames by default

NAIRSAMPLES = 1
N_ZERO_PAD = len(str(NAIRSAMPLES))
i_time = time.time()

xem.Open()
xem.SelectADC(0)
xem.SelectFakeADC(0)
xem.EnablePgen(0)
xem.Close()

for mycount in range(NAIRSAMPLES):
   
    geegah_hp.configTiming(xem,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS)
    
    air_baseline_echo_filename = BLE_save_dir + "DATA"+str(mycount).zfill(N_ZERO_PAD)+".dat"
    
    geegah_hp.acqSingleFrameROI(xem, ADC_TO_USE, air_baseline_echo_filename,
                                            roi_param[0], 
                                            roi_param[1], 
                                            roi_param[2],
                                            roi_param[3])

    time.sleep(0.1)
    geegah_hp.configTiming(xem,term_count_NE,TX_SWITCH_EN_SETTINGS_NE,PULSE_AND_SETTINGS_NE,RX_SWITCH_EN_SETTINGS_NE,GLOB_EN_SETTINGS_NE,LO_CTRL_SETTINGS_NE,ADC_CAP_SETTINGS_NE)
    air_baseline_noecho_filename = BLNE_save_dir + "DATA"+str(mycount).zfill(N_ZERO_PAD)+".dat"
    geegah_hp.acqSingleFrameROI(xem, ADC_TO_USE, air_baseline_noecho_filename,
                                            roi_param[0], 
                                            roi_param[1], 
                                            roi_param[2],
                                            roi_param[3])
    time.sleep(0.1)
    
    print("Currently at ", mycount)

f_time = time.time()
fps = NAIRSAMPLES/(f_time - i_time)
xem.Close()
print("FRAME RATE = "+str(fps))
print("Done acquiring multiple baselines over echo and no echo")


#%% LOAD THE SAMPLE NOW
#do real time imaging #ECHO AND NO-ECHO for your sample
NUM_IMAGE_SAMPLES =  20
N_ZERO_PAD_IM = len(str(NUM_IMAGE_SAMPLES))

#extract air echo magnitude, average of N frames acquired for AIR
xem.Open()
xem.SelectADC(0)
xem.SelectFakeADC(0)
xem.EnablePgen(0)
xem.Close()
if liveplot == True:
    MAG_AIR = []
    for mycount in range(NAIRSAMPLES):
        AE_filename = BLE_save_dir + "DATA"+str(mycount).zfill(N_ZERO_PAD)+".dat"
        I_ADC_AE, Q_ADC_AE, I_VOLTS_AE, Q_VOLTS_AE = geegah_hp.loadSavedRawDataROI(AE_filename, col_min, col_max, row_min, row_max)   
        MAG_AIR_MAT = np.sqrt(np.square(I_VOLTS_AE)+np.square(Q_VOLTS_AE))
        MAG_AIR.append(MAG_AIR_MAT)
    MAG_AIR_AV = np.average(MAG_AIR, axis = 0)
    
    # Preparing the plot before the loop
    fig2, ax2 = plt.subplots(1)
    mytitle = fig2.suptitle('Real-time Magnitude (V): ')
    base_title = 'Real-time Magnitude (V): '
    # Initialize the plot with the first image
    initial_image = MAG_AIR_AV-MAG_AIR_MAT
    pos201 = ax2.imshow(initial_image , vmin=-0.05, vmax=0.05, cmap = 'ocean')
    fig2.colorbar(pos201)
    # Draw the plot initially to cache the renderer
    plt.show(block=False)
myt_F = time.time()

for mycount in range(NUM_IMAGE_SAMPLES): 
    #$#xem.Open()
    geegah_hp.configTiming(xem,term_count,TX_SWITCH_EN_SETTINGS,PULSE_AND_SETTINGS,RX_SWITCH_EN_SETTINGS,GLOB_EN_SETTINGS,LO_CTRL_SETTINGS,ADC_CAP_SETTINGS)
    meas_echo_filename = rawdata_save_dir + "DATA"+str(mycount).zfill(N_ZERO_PAD_IM)+".dat"
    meas_bytes = geegah_hp.acqSingleFrameROI(xem, ADC_TO_USE, meas_echo_filename,
                                            roi_param[0], 
                                            roi_param[1], 
                                            roi_param[2],
                                            roi_param[3])
    
    
    time.sleep(0.1)

    geegah_hp.configTiming(xem,term_count_NE,TX_SWITCH_EN_SETTINGS_NE,PULSE_AND_SETTINGS_NE,RX_SWITCH_EN_SETTINGS_NE,GLOB_EN_SETTINGS_NE,LO_CTRL_SETTINGS_NE,ADC_CAP_SETTINGS_NE)
    meas_noecho_filename = rawdata_ne_save_dir + "DATA"+str(mycount).zfill(N_ZERO_PAD_IM)+".dat"
    geegah_hp.acqSingleFrameROI(xem, ADC_TO_USE, meas_noecho_filename,
                                            roi_param[0], 
                                            roi_param[1], 
                                            roi_param[2],
                                            roi_param[3])
    time.sleep(0.1)
    if liveplot == True: 
        #convert binary data to matrix
        I_ADC_RT, Q_ADC_RT, I_VOLTS_RT, Q_VOLTS_RT  = geegah_hp.loadSavedRawDataROI(meas_echo_filename,
                                                                                    roi_param[0], 
        roi_param[1], 
        roi_param[2],
        roi_param[3])
        #convert matrix to volts and actual ADC value
        MAG_SAMP = np.sqrt(np.square(I_VOLTS_RT)+np.square(Q_VOLTS_RT))
        #Update the plot title
        mytitle.set_text(base_title + str(mycount) + ' of ' + str(NUM_IMAGE_SAMPLES - 1))
        # Update the image data
        sub_image = np.flipud(np.rot90(MAG_SAMP-MAG_AIR_AV, 1))
        pos201.set_data(sub_image)
        
        # Efficiently update and redraw only the necessary parts
        fig2.canvas.draw_idle()
        fig2.canvas.flush_events()
        # Optionally, save the frame
        fig2.savefig(img_save_dir2 + '/' + 'plot' + str(mycount) + '.png')
        
    print("Currently at ", mycount)
xem.Close()
print("Done acquiring image data over echo and no echo")
myt_D = time.time()
total_time = myt_D - myt_F
print('fps = '+str(NUM_IMAGE_SAMPLES/total_time))

#%%###############################################################%%
#POST-PROCESSING SECTION
#LOADING FRAMES
foldername_PP = "OIL_ALC"
path_PP = "C:/Users/anujb/Downloads"
savedirname_PP = os.path.join(path_PP, foldername_PP, "")
BLE_save_dir = savedirname_PP+'rawdata_baseline_echo/'
BLNE_save_dir = savedirname_PP+'rawdata_baseline_no_echo/'
rawdata_save_dir = savedirname_PP+'rawdata_echo/'
rawdata_ne_save_dir = savedirname_PP+'rawdata_no_echo/'
#Selection of firing/receiving pixels, ROI
#THIS MUST MATCH WITH THE SAME VARIABLES THAT WERE USED DURING ACQUISITION
col_min = 0 #integer, 0<col_min<127
col_max = 64  #integer, 0<col_max<127
row_min = 0 #integer, 0<row_min<127
row_max = 64 #integer, 0<row_max<127

roi_param = [col_min, col_max, row_min, row_max]
num_AIR_Frames = 1 #Number of air/baseline frames to consider during computation
num_SAMPLE_Frames = 20 #Number of frames to measured sample frames

I_A_E, Q_A_E, I_A_NE, Q_A_NE = [],[],[],[]
I_S_E, Q_S_E, I_S_NE, Q_S_NE = [],[],[],[]

#LOAD AIR DATA
for frame in range(num_AIR_Frames):

    N_ZERO_PAD = len(str(num_AIR_Frames))
    AE_filename = BLE_save_dir + "DATA"+str(frame).zfill(N_ZERO_PAD)+".dat"
    ANE_filename =  BLNE_save_dir + "DATA"+str(frame).zfill(N_ZERO_PAD)+".dat"
    
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
    
    
    print("Currently loading AIR FRAME: "+str(frame))
print("FINISHED LOADING AIR FRAMES")

#LOADING SAMPLE DATA
for frame in range(num_SAMPLE_Frames):
    
    N_ZERO_PAD_IM = len(str(num_SAMPLE_Frames))
    SE_filename = rawdata_save_dir+"DATA"+str(frame).zfill(N_ZERO_PAD_IM)+".dat"
    SNE_filename =  rawdata_ne_save_dir+"DATA"+str(frame).zfill(N_ZERO_PAD_IM)+".dat"
    
    I_ADC_SE, Q_ADC_SE, I_VOLTS_SE, Q_VOLTS_SE = geegah_hp.loadSavedRawDataROI(SE_filename,roi_param[0], 
    roi_param[1], 
    roi_param[2],
    roi_param[3])
    
    I_ADC_SNE, Q_ADC_SNE, I_VOLTS_SNE, Q_VOLTS_SNE = geegah_hp.loadSavedRawDataROI(SNE_filename,roi_param[0], 
    roi_param[1], 
    roi_param[2],
    roi_param[3])
    
    I_S_E.append(I_VOLTS_SE)
    Q_S_E.append(Q_VOLTS_SE)
    I_S_NE.append(I_VOLTS_SNE)
    Q_S_NE.append(Q_VOLTS_SNE)
    
    print("Currently loading SAMPLE FRAME: "+str(frame))
print("FINISHED LOADING SAMPLE FRAMES")

#NUMPY ARRAY CONVERSION
I_A_E, Q_A_E, I_A_NE, Q_A_NE = np.array(I_A_E),np.array(Q_A_E),np.array(I_A_NE),np.array(Q_A_NE)
I_S_E, Q_S_E, I_S_NE, Q_S_NE = np.array(I_S_E),np.array(Q_S_E),np.array(I_S_NE),np.array(Q_S_NE)

#COMPUTING MAGNITUDE, PHASE, REFLECTION COEFFICIENT, and ACOUSTIC IMPEDANCE

MAG_AIR = np.sqrt(np.square(I_A_E - I_A_NE)+np.square(Q_A_E - Q_A_NE))
PHASE_AIR = np.arctan2(I_A_E-I_A_NE, Q_A_E-Q_A_NE)



MAG_SAMPLE = []
PHASE_SAMPLE = []
RCOEF = []

for frame in range(num_SAMPLE_Frames):
    MAG = np.sqrt(np.square(I_S_E[frame] - I_S_NE[frame])+np.square(Q_S_E[frame] - Q_S_NE[frame]))
    PHASE = np.arctan2(I_S_E[frame]-I_S_NE[frame], Q_S_E[frame]-Q_S_NE[frame])
   
    MAG_SAMPLE.append(MAG)
    PHASE_SAMPLE.append(PHASE)
    RCOEF.append(MAG/MAG_AIR)
    
#ACOUSTIC PARAMETERS COMPUTATION

MAGNITUDE_ADJ = np.array(MAG_SAMPLE)-np.array(MAG_AIR)
PHASE_ADJ = np.array(PHASE_SAMPLE) - np.array(PHASE_AIR)
REFLECTION_COEFFICIENT = np.array(MAG_SAMPLE)/MAG_AIR

ACOUSTIC_IMP = [geegah_hp.impedance_si(jj, array = True) for jj in REFLECTION_COEFFICIENT]

#%%
LIST_to_PLOT = PHASE_ADJ
Parameter = "Acoustic Impedance"
geegah_hp.imgvid_plot_IMG(LIST_to_PLOT,savedirname_PP, 
                          foldername = Parameter,
                          vmin = -0.1,vmax = 0.1)
    
    

