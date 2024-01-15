# Geegah Opal Kelly Image Acquisition

# Introduction
This repository contains Python scripts for image acquisition and processing using the Geegah ultrasonic imager with Opal Kelly XEM 7503 FPGA processor. The Geegah Imager consists of a 128 x 128 or 256 x 256 array of transducers that transmit and receive high-frequency ultrasonic waves. Different scripts are tailored to enable single/multi-frequency measurements, controlling individual pixels or regions of interest (ROI), as well as acquiring the whole transmit/receive pulses with multiple echoes. Additionally, scripts are provided to generate images from the raw ".dat" files and further compute the acoustic parameters of the acquired data. 

# Prerequisites
Before you use any of the acquisition of post-processing scripts, ensure you have the following on your computer:
1. Python 3. x installed
2. Opal Kelly FPGA driver: [Download link](https://pins.opalkelly.com/downloads/572/download?category_id=27)
3. Python libraries for operations: sys, os, time, math, NumPy
4. Python libraries for image generation, visualization, and analysis: matplotlib, OpenCV (video generation and analysis)

An example of installing Matplotlib and OpenCV module using pip.

```bash
python -m pip install -U matplotlib
```

```bash
pip install opencv-python
```

# Image acquisition and processing scripts
The following scripts all allow for data acquisition using the Opal Kelly Imager. Each acquisition scripts also contain post-processing scripts that allow users to load the raw data to generate images and compute different acoustic parameters.

1. **Geegah_OK_LiveImaging.py**: Acquisition of whole N number of frames with an option to visualize them in real-time. It also allows the user to select the operating pixels from a single pixel to 128 x 128 or 256 x 256. This operates at a fixed frequency and echo acquisition timing. 
2. **Geegah_OK_FrequencySweep.py**: Acquisition of images at a range of frequencies (1.5 - 2.0 GHz, with a step as low as 0.01 MHz). Allows capturing N frames (128 x 128 or smaller ROIs) at a fixed acquisition echo timing. 
3. **Geegah_OK_SampleHold.py** [A-scan]: Acquisition of images at different echo timing to obtain pulse vs timing data at 5 ns temporal resolution. Allows N frames acquisition at a fixed frequency.


# Helper libraries
These consist of classes or functions that support the acquisition and processing of scripts. These do not have to be run individually.

1. **fpga.py** Helper functions for opal-kelly FPGA pin assignments, settings loading, and acquisition parameters setup.
2. **ok.py** Opal Kelly specific functions
3. **geegah_hf.py** Helper functions for image acquisition and post-processing

# Other files for driver support (included)

1. okFrontPanel.dll
2. _ok.pyd
3. xem7305_GG222.bit

# Getting started: 

**Clone the repository**
```bash
git clone git@github.com:Geegah-Inc/Geegah_OK.git
```

**Or, directly download the zip**
Click on 1) **Code** drop-down menu and click **Download ZIP** 
![alt text](https://github.com/Geegah-Inc/Geegah_OK/blob/main/ZIP_download.png)

**Usage Example**
All the scripts have been divided into the following sections:

1) Importing modules
2) Creating a directory and sub-folders to save raw and processed images
3) Changing parameters of interest
4) Finding and initializing the board
5) Reloading the board after first initialization
6) Acquiring air frames/background frames
7) Acquiring main sample frames
8) Plotting desired acoustic parameters
9) Relevant Post-processing

**1. Importing Modules**<br />
You simply have to run this once to load the necessary helper functions and Python libraries
```python
import fpga 
import sys
import numpy as np
import matplotlib.pyplot as plt
import geegah_hp
import time
import cv2 #optional for video generation
import os
```

**2. Directory assignment** <br />
Change the **foldernam**e to represent the main folder where all the sub-folders will be created, and the raw data files will be saved. <br />
Select the **savedirname** as the filepath where the **foldername** will be created

```python
foldername = "SampleExperiment1"
savedirname = os.path.join("C:/Users/ab2297/Downloads", foldername, "")

if not os.path.exists(savedirname):
    os.makedirs(savedirname)
```

**3. Changing parameters of interest**<br />
This is the section where you need to assign correct values to the parameter that you might want to change for the acquisition

```python
liveplot = True #boolean for plotting images real-time, True or False
frequency = 1853.0 #Pulse frequency in MHz, with resolution of 0.1 MHz

#Selection of firing/receiving pixels, ROI 

col_min = 0 #integer, 0<col_min<127
col_max = 127 #integer, 0<col_max<127
row_min = 0 #integer, 0<row_min<127
row_max = 127 #integer, 0<row_max<127

num_Frames = 200 #Number of frames to acquire for sample, integer, num_Frames > 0
```
Please ensure the Geegah Imager is powered on and connected to the PC via USB A/C before proceeding.  <br />

**4. Finding and initializing the board**<br />
The first section of the code sets up the connection with the FPGA board. If the board is not connected, or if the driver is missing, an error message appears. 

```python
xem = fpga.fpga()
board_name = xem.BoardName()
if board_name != "XEM7305":
    print("Problem: board name = " + board_name)  
    sys.exit()
print("Board: " + xem.di.deviceID + " " + xem.di.serialNumber)
```
The second part of the code is loading the DAC in the board, which prepares individual pixels for imaging. It further loads other timing and pulse settings as well. <br /> 
You do not have to change anything here. You also only need to run this section once, as it takes approximately 30 seconds - 1.5 minutes to load all the pixels (128 x 128) <br />
Re-run this if you restarted the console or the board connection was interrupted mid-acquisition. 

```python
#bit file to use (before DAC changes)
bit_file_name = "xem7305.bit"
xem.Configure(bit_file_name) # use older bit file
print("Version: " + xem.Version() + " serial number " + str(xem.SerialNumber()))
print("Sys clock = %8.4f MHz" % xem.SysclkMHz())
...
...
...
#code continues#
```
**5. Reloading the board after first initialization** <br />
This function can be run to re-initialize the board once the FPGA setup code has already been run.

```python
geegah_hp.reload_board(xem, frequency)
```

Please ensure the chip surface is cleaned properly before running this section.


**6. Acquiring baseline frames** <br />
Enter the number of air frames/baseline frames to acquire for the experiment by changing  **NAIRSAMPLES** variable. 

```python
NAIRSAMPLES = 10
N_ZERO_PAD = len(str(NAIRSAMPLES))
myt_E = time.time()

xem.Open()
# Select ADC 2 and make sure the fake ADC is not selected
xem.SelectADC(ADC_TO_USE) #1 for ADC2, 0 for ADC1
...
...
...
#code continues#
```
**7. Acquiring sample frames** <br />
Enter the number of sample frames to acquire for the experiment by changing  the **NUM_IMAGE_SAMPLES** variable. <br />
If you have enabled the plotting (liveplot = True), a plot window pops up displaying the calculated Magnitude (V) of the signal real time.
```python

NUM_IMAGE_SAMPLES =  100
N_ZERO_PAD_IM = len(str(NUM_IMAGE_SAMPLES))
time_stamp = []
xem.Open()
# Select ADC 2 and make sure the fake ADC is not selected
xem.SelectADC(ADC_TO_USE) #1 for ADC2, 0 for ADC1
xem.SelectFakeADC(0) #to deselect the fake ADC
# Disable pattern generator
xem.EnablePgen(0)
...
...
...
#code continues#
```

**8. Process the images** <br />
Enter the number of sample frames to acquire for the experiment by changing  the **NUM_IMAGE_SAMPLES** variable. <br />
If you have enabled the plotting (liveplot = True), a plot window pops up displaying the calculated Magnitude (V) of the signal real time.
```python

NUM_IMAGE_SAMPLES =  100
N_ZERO_PAD_IM = len(str(NUM_IMAGE_SAMPLES))
time_stamp = []
xem.Open()
# Select ADC 2 and make sure the fake ADC is not selected
xem.SelectADC(ADC_TO_USE) #1 for ADC2, 0 for ADC1
xem.SelectFakeADC(0) #to deselect the fake ADC
# Disable pattern generator
xem.EnablePgen(0)
...
...
...
#code continues#
```





**Contact**
Anuj Baskota
anuj@geegah.com


   

   


