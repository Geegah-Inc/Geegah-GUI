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
3. **Geegah_hf.py** Helper functions for image acquisition and post-processing

# Other files for driver support (included)

1. okFrontPanel.dll
2. _ok.pyd

   


