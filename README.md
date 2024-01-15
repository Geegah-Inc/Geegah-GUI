# Geegah Opal Kelly Image Acquisition

# Introduction
This repository contains Python scripts for image acquisition and processing using the Geegah ultrasonic imager with Opal Kelly XEM 7503 FPGA processor. The Geegah Imager consists of a 128 x 128 or 256 x 256 array of transducers that transmit and receive high-frequency ultrasonic waves. Different scripts are tailored to enable single/multi-frequency measurements, controlling individual pixels or regions of interest (ROI), as well as acquiring the whole transmit/receive pulses with multiple echoes. Additionally, scripts are provided to generate images from the raw ".dat" files and further compute the acoustic parameters of the acquired data. 

# Prerequisites
Before you use any of the acquisition of post-processing scripts, ensure you have the following on your computer:
1. Python 3. x installed
2. Python libraries for operations: sys, os, time, math, NumPy
3. Python libraries for image generation, visualization, and analysis: matplotlib, OpenCV (video generation and analysis)

An example of installing Matplotlib and OpenCV module using pip.

```bash
python -m pip install -U matplotlib
```

```bash
pip install opencv-python
```

#
# Image acquisition scripts

