# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 12:33:06 2021

@author: anuj
"""
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kde
#%% convert a number in .dat format
def dat_file_str(n, len1, strused = 'DATA'):
	#gives the .dat file name for the given frame
	#len1 is the max size
	length = len(str(n))
	if length > 0 and length < 6:
		str1 = (len1-length)*'0'
		return strused+str1+str(n)+'.dat'
	else:
		print( 'Please enter valid frame number from 1 to 10000')
        
        
#%%conmvert a number in freq .dat format
def smoothen(A):
	#smoothens array as per the set carrier f 
	f_s = 15 #sampling frequency
	f_c = 1 #carrier frequency
	w=f_c/(f_s/2)

	b, a = signal.butter(1,w)
	zi = signal.lfilter_zi(b, a)
	z, _ = signal.lfilter(b, a,  A, zi=zi*A[0])
	z2, _ = signal.lfilter(b, a, z, zi=zi*z[0])
	y=signal.filtfilt(b, a, A)
	return y

#%%
def flip_mat(A):
    #flips matrix upside down and horizontally
    frame_1 = np.flipud(A)
    #frame_2 = np.flip(frame_1, axis = 1)
    frame_2 = np.rot90(frame_1)
    frame_2 = np.rot90(frame_2)
    frame_2 = np.rot90(frame_2)
    
    return frame_2

 #%%pixel LIST 
def pixel_list(Mat, pixel):
    #Mat is the list of matrices, x,y are the pixels to be plotted over time/frames
    pix_list = []
    for jj in Mat:
        pix_list.append(jj[pixel])
        
    return np.array(pix_list)   

#%%
def combine_str(maintext, addedSTR):
    #combines the addedSTR to the maintext list
    newstr = []
    for jj in maintext:
        newstr.append(jj+addedSTR)
    return newstr


#get amplitude from I, Q lists. Both echo and non echo lists required

#%%
def amplitude_MAT(raw_echo_i, raw_noecho_i, raw_echo_q, raw_noecho_q, air_echo_i, air_noecho_i, air_echo_q, air_noecho_q, water_echo_i, water_noecho_i, water_echo_q, water_noecho_q): 
    #all of these are lists of matrices. each matrix represents one frame of an image. 
    #nematode referred as raw
    #order1: raw, air, water
    #order2: echo, no echo
    #order3: i, q
   #Average of no echo signal for air, water, and nematodes: BOTH I and Q
    A1_I_NOECHO_AVG = np.mean(air_noecho_i, axis=0)
    A1_Q_NOECHO_AVG = np.mean(air_noecho_q, axis=0)
    #print(type(A1_Q_NOECHO_AVG))
    ##print(len(A1_Q_NOECHO_AVG))
    #print(len(A1_Q_NOECHO_AVG[0]))
    W1_I_NOECHO_AVG = np.mean(water_noecho_i, axis=0)
    W1_Q_NOECHO_AVG = np.mean(water_noecho_q, axis=0)
    
    N1_I_NOECHO_AVG = np.mean(raw_noecho_i, axis=0)
    N1_Q_NOECHO_AVG = np.mean(raw_noecho_q, axis=0)
    #print(len(N1_I_NOECHO_AVG))
    
    
    P1_I_NOECHO_AVG = (1/3)*(A1_I_NOECHO_AVG + W1_I_NOECHO_AVG + N1_I_NOECHO_AVG)
    P1_Q_NOECHO_AVG = (1/3)*(A1_Q_NOECHO_AVG+W1_Q_NOECHO_AVG+N1_Q_NOECHO_AVG)
    #print(A1_I_NOECHO_AVG[0][0])
    #print(W1_I_NOECHO_AVG[0][0])
    ##print(N1_I_NOECHO_AVG[0][0])
    #print(P1_I_NOECHO_AVG[0][0])
    #print(len(P1_Q_NOECHO_AVG))
    
   # LIST of amplitudes
    AMP_AIR_1 = []
    AMP_WATER_1 = []
    AMP_RAW_1 = []
    AMP_RAW_div_AIR = [] #amp nematode divided by air
    AMP_RAW_div_WATER = []
    
    for jj in range(84):
        
        #assigning the jj frames
        air_echo_i_v = air_echo_i[jj]
        air_echo_q_v = air_echo_q[jj]
        water_echo_i_v = water_echo_i[jj]
        water_echo_q_v = water_echo_q[jj]
        raw_echo_i_v = raw_echo_i[jj]
        raw_echo_q_v = raw_echo_q[jj]  
        
        #calculating the amplitudes
        AMP_AIR_1_v = np.sqrt(np.square(air_echo_i_v- P1_I_NOECHO_AVG)+np.square(air_echo_q_v - P1_Q_NOECHO_AVG))
        AMP_WATER_1_v = np.sqrt(np.square(water_echo_i_v- P1_I_NOECHO_AVG)+np.square(water_echo_q_v - P1_Q_NOECHO_AVG))
        AMP_RAW_1_v = np.sqrt(np.square(raw_echo_i_v- P1_I_NOECHO_AVG)+np.square(raw_echo_q_v - P1_Q_NOECHO_AVG))
        AMP_RAW_div_AIR_v = np.divide(AMP_RAW_1_v,AMP_AIR_1_v)
        #print(air_echo_i)
        ##print(P1_I_NOECHO_AVG)
        #print(len(air_echo_i_v-P1_I_NOECHO_AVG))
        
    #appending the individual calculated 128 * 128 amplitudes to the respective lists
        AMP_RAW_div_WATER_v = np.divide(AMP_RAW_1_v,AMP_WATER_1_v)
        AMP_AIR_1.append(AMP_AIR_1_v)
        AMP_WATER_1.append(AMP_WATER_1_v)
        AMP_RAW_1.append(AMP_RAW_1_v)
        AMP_RAW_div_AIR.append(AMP_RAW_div_AIR_v)
        AMP_RAW_div_WATER.append(AMP_RAW_div_WATER_v)
    
    return AMP_AIR_1, AMP_WATER_1, AMP_RAW_1,  AMP_RAW_div_AIR,  AMP_RAW_div_WATER


#%%
def amplitude_LIST(raw_echo_i, raw_noecho_i, raw_echo_q, raw_noecho_q, air_echo_i, air_noecho_i, air_echo_q, air_noecho_q, water_echo_i, water_noecho_i, water_echo_q, water_noecho_q):
    AMP_AIR_1 = []
    AMP_WATER_1 = []
    AMP_NEMATODE_1 = []
    AMP_NEM_dWATER = []
    AMP_NEM_dAIR = []
    
    A1_I_NOECHO_AVG = np.average(air_noecho_i)
    N1_I_NOECHO_AVG = np.average(raw_noecho_i)
    W1_I_NOECHO_AVG = np.average(water_noecho_i)
    
    A1_Q_NOECHO_AVG = np.average(air_noecho_q)
    N1_Q_NOECHO_AVG = np.average(raw_noecho_q)
    W1_Q_NOECHO_AVG = np.average(water_noecho_q)
    
    
    P1_I_NOECHO_AVG = (1/3)*(A1_I_NOECHO_AVG+W1_I_NOECHO_AVG+N1_I_NOECHO_AVG)
    P1_Q_NOECHO_AVG = (1/3)*(A1_Q_NOECHO_AVG+W1_Q_NOECHO_AVG+N1_Q_NOECHO_AVG)
    
    #compare air, water and nematode
    AMP_AIR_1 = np.sqrt(np.square(air_echo_i - P1_I_NOECHO_AVG)+np.square(air_echo_q - P1_Q_NOECHO_AVG))
    AMP_WATER_1 = np.sqrt(np.square(water_echo_i - P1_I_NOECHO_AVG)+np.square(water_echo_q - P1_Q_NOECHO_AVG))
    AMP_NEMATODE_1 = np.sqrt(np.square(raw_echo_i- P1_I_NOECHO_AVG)+np.square(raw_echo_q - P1_Q_NOECHO_AVG))
    
    AMP_NEM_dWATER = np.divide(AMP_NEMATODE_1, AMP_WATER_1)
    AMP_NEM_dAIR = np.divide(AMP_NEMATODE_1, AMP_AIR_1)
    
    return AMP_AIR_1, AMP_WATER_1, AMP_NEMATODE_1, AMP_NEM_dWATER, AMP_NEM_dAIR


def phase_LIST(raw_echo_i, raw_noecho_i, raw_echo_q, raw_noecho_q, air_echo_i, air_noecho_i, air_echo_q, air_noecho_q, water_echo_i, water_noecho_i, water_echo_q, water_noecho_q):
    
    A1_I_NOECHO_AVG = np.average(air_noecho_i)
    N1_I_NOECHO_AVG = np.average(raw_noecho_i)
    W1_I_NOECHO_AVG = np.average(water_noecho_i)
    
    A1_Q_NOECHO_AVG = np.average(air_noecho_q)
    N1_Q_NOECHO_AVG = np.average(raw_noecho_q)
    W1_Q_NOECHO_AVG = np.average(water_noecho_q)
    
    diff_I_nem = raw_echo_i - N1_I_NOECHO_AVG
    diff_Q_nem = raw_echo_q - N1_Q_NOECHO_AVG
    
    diff_I_air = air_echo_i - A1_I_NOECHO_AVG
    diff_Q_air = air_echo_q - A1_Q_NOECHO_AVG
    
    diff_I_wat = water_echo_i - W1_I_NOECHO_AVG
    diff_Q_wat = water_echo_q - W1_Q_NOECHO_AVG
    
    IdivQ_nem = np.divide(diff_I_nem, diff_Q_nem)
    IdivQ_air = np.divide(diff_I_air, diff_Q_air)
    IdivQ_wat = np.divide(diff_I_wat, diff_Q_wat)
    
    QdivI_nem = np.divide(diff_Q_nem, diff_I_nem)
    QdivI_air = np.divide(diff_Q_air, diff_I_air)
    QdivI_wat = np.divide(diff_Q_wat, diff_I_wat)
    
    phase_IQ_nem = np.arctan(IdivQ_nem)
    phase_IQ_air = np.arctan(IdivQ_air)
    phase_IQ_wat = np.arctan(IdivQ_wat)
    
    phase_QI_nem = np.arctan(QdivI_nem)
    phase_QI_air = np.arctan(QdivI_air)
    phase_QI_wat = np.arctan(QdivI_wat)
    
    return phase_IQ_nem, phase_IQ_air, phase_IQ_wat, phase_QI_nem, phase_QI_air, phase_QI_wat

##############
# def phase_MAT(raw_echo_i, raw_noecho_i, raw_echo_q, raw_noecho_q, air_echo_i, air_noecho_i, air_echo_q, air_noecho_q, water_echo_i, water_noecho_i, water_echo_q, water_noecho_q): 
#     #all of these are lists of matrices. each matrix represents one frame of an image. 
#     #nematode referred as raw
#     #order1: raw, air, water
#     #order2: echo, no echo
#     #order3: i, q
#    #Average of no echo signal for air, water, and nematodes: BOTH I and Q
#     A1_I_NOECHO_AVG = np.mean(air_noecho_i, axis=0)
#     A1_Q_NOECHO_AVG = np.mean(air_noecho_q, axis=0)
#     #print(type(A1_Q_NOECHO_AVG))
#     ##print(len(A1_Q_NOECHO_AVG))
#     #print(len(A1_Q_NOECHO_AVG[0]))
#     W1_I_NOECHO_AVG = np.mean(water_noecho_i, axis=0)
#     W1_Q_NOECHO_AVG = np.mean(water_noecho_q, axis=0)
    
#     N1_I_NOECHO_AVG = np.mean(raw_noecho_i, axis=0)
#     N1_Q_NOECHO_AVG = np.mean(raw_noecho_q, axis=0)
#     #print(len(N1_I_NOECHO_AVG))

    
#    # LIST of amplitudes
#     AMP_AIR_1 = []
#     AMP_WATER_1 = []
#     AMP_RAW_1 = []
#     AMP_RAW_div_AIR = [] #amp nematode divided by air
#     AMP_RAW_div_WATER = []
    
#     for jj in range(84):
        
#         #assigning the jj frames
#         air_echo_i_v = air_echo_i[jj]
#         air_echo_q_v = air_echo_q[jj]
#         water_echo_i_v = water_echo_i[jj]
#         water_echo_q_v = water_echo_q[jj]
#         raw_echo_i_v = raw_echo_i[jj]
#         raw_echo_q_v = raw_echo_q[jj]  
        
#         #calculating the amplitudes
#         AMP_AIR_1_v = np.sqrt(np.square(air_echo_i_v- P1_I_NOECHO_AVG)+np.square(air_echo_q_v - P1_Q_NOECHO_AVG))
#         AMP_WATER_1_v = np.sqrt(np.square(water_echo_i_v- P1_I_NOECHO_AVG)+np.square(water_echo_q_v - P1_Q_NOECHO_AVG))
#         AMP_RAW_1_v = np.sqrt(np.square(raw_echo_i_v- P1_I_NOECHO_AVG)+np.square(raw_echo_q_v - P1_Q_NOECHO_AVG))
#         AMP_RAW_div_AIR_v = np.divide(AMP_RAW_1_v,AMP_AIR_1_v)
#         #print(air_echo_i)
#         ##print(P1_I_NOECHO_AVG)
#         #print(len(air_echo_i_v-P1_I_NOECHO_AVG))
        
#     #appending the individual calculated 128 * 128 amplitudes to the respective lists
#         AMP_RAW_div_WATER_v = np.divide(AMP_RAW_1_v,AMP_WATER_1_v)
#         AMP_AIR_1.append(AMP_AIR_1_v)
#         AMP_WATER_1.append(AMP_WATER_1_v)
#         AMP_RAW_1.append(AMP_RAW_1_v)
#         AMP_RAW_div_AIR.append(AMP_RAW_div_AIR_v)
#         AMP_RAW_div_WATER.append(AMP_RAW_div_WATER_v)
    
#     return AMP_AIR_1, AMP_WATER_1, AMP_RAW_1,  AMP_RAW_div_AIR,  AMP_RAW_div_WATER

#%%
def matrix_AVG(A):
    #computes pixel to pixel average for the matrices across a list
    #A is a list of matrices
    A_AVG = np.mean(A, axis=0)
    return A_AVG

#%%
def pixel_counter(A, threshold):
    #calculate the number of pixels where the value is greater than the threshold
    count1 = 0
    count2 = 0
    values = []
    for jj in A:
        for kk in jj:
            if kk > threshold:
                count1 = count1 + 1
                values.append(kk)
        count2 = count2 + count1
        count1 = 0
    print("median: "+str(np.median(values)))
    return count2

#%%
def pixel_integration(A, threshold):
    #calculates the sum of all the values in pixels greater than a threshold
    value = 0
    for jj in A:
        for kk in jj:
            if kk > threshold:
                value = value+kk
    return value
        
        
#%%
def thres_median(before_sample, after_sample, threshold = 0.06):
    #before_sample is a matrix, after_sample is a matrix
    #returns the median values of the pixels of the after_sample whose values are a certain threshold
    #above their before_sample values
    flat_list = []
    for rows in range(len(before_sample)):
        for cols in range(len(before_sample[0])):
            if after_sample[rows][cols] > ( threshold + before_sample[rows][cols]):
                flat_list.append(after_sample[rows][cols])
    
    return flat_list, np.median(flat_list)


#%%
def thres_median_check(before_sample, after_sample, threshold = 0.01):
    #before_sample is a matrix, after_sample is a matrix
    #returns the median values of the pixels of the after_sample whose values are a certain threshold
    #above their before_sample values
    max_val = after_sample.max()
    mat_new = after_sample
    for rows in range(len(before_sample)):
        for cols in range(len(before_sample[0])):
            if after_sample[rows][cols] > ( threshold + before_sample[rows][cols]):
                mat_new[rows][cols] = max_val
                
    plt.imshow(mat_new)
###############PLOTTING#############
#%%image generator with saving option

def img_plot(matrix_list,direc,savebool,foldername,stringname, start_frame = 0):
    fps = 7
    fig, ax = plt.subplots()
    net = len(matrix_list)
    
    for i in range(net):
        ax.cla()
        out = matrix_list[i]
        if foldername[:5] == "Phase":
            min_val = -np.pi/2
            max_val = np.pi/2
        elif foldername == "Amplitude":
            min_val = out.min()
            max_val = out.max()
        else:
            #min_val = -0.05
            #max_val = -0.03
            min_val = -0.05
            max_val = 0.05
        #pos = ax.imshow(out, interpolation = 'bilinear')
        pos = ax.imshow(out,vmin = min_val, vmax = max_val, cmap = "inferno")
       # ax.set_title(stringname+" : Time elapsed {}".format(round(start_frame, 2))+" sec")
        ax.set_title(stringname+" : Frame {}".format(round(start_frame, 2)))
        ax.set_xlabel("Columns")
        ax.set_ylabel("Rows")
        cbar = fig.colorbar(pos)
        #cbar.set_label("AMPLITUDE")
        plt.pause(1/fps)
        start_frame = start_frame + 1
        if savebool == True:
            fig.savefig(direc+foldername+'/'+'plot'+str(i)+'.png')
        cbar.remove()
    
    print("Done generating video from frames")
    
#%%
def Average_divider(mat):
    main_list = []
    for jj in range(len(mat)):
        npar = np.array(mat[jj])
        flatlist = npar.flatten()
        avg_val = np.average(flatlist)
        main_list.append(avg_val)
        print(str(jj)+" mat done")
    return main_list

#%%histogram plotting 
def hist_plot(MAIN_list, density = True, bins = 90, alpha = 0.5, string_tuple = [], ylabel = '', title = ''):
    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel(ylabel)
    ax.set_ylabel('Number of pixels');
    ax.set_title(title)
    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'olive', 'chocolate',"lime" ]
    
    flat_list = []
    for jj in MAIN_list:
        bb = np.array(jj)
        flat_list.append(bb.flatten())
   
    for jj in range(len(flat_list)):
       _ = ax.hist(flat_list[jj], density=density, bins=bins, alpha=alpha, color = colors[jj])
          
    #fig.tight_layout()
    # Add a legend
    plt.legend(string_tuple)
    plt.show()

#%%histogram generator with saving option

def hist_video(MAIN_list,direc,savebool,foldername, start_frame = 0, bins = 20, alpha = 0.5):
    
    flat_list = []
    for jj in MAIN_list:
        bb = np.array(jj)
        flat_list.append(bb.flatten())
    fps = 7
    fig, ax = plt.subplots()
   
    for i in range(len(MAIN_list)):
        
        ax.set_ylim(top=35)
        ax.set_title(foldername+" : Time elapsed {}".format(round(start_frame)) + " minutes")
        ax.set_ylabel = ("Pixel count")
        ax.set_xlabel = ("Q (Volts)")
        _ = ax.hist(flat_list[i], density= True, bins=bins, alpha=alpha, range = [-0.05,0.1])
        # prob_density = kde.gaussian_kde(flat_list[i])
        # prob_density.covariance_factor = lambda : 0.3
        # prob_density._compute_covariance()
    
        # x = np.linspace(flat_list[i].min(), flat_list[i].max(),200)
        # y=prob_density(x)

        # plt.plot(x, y)
        
        
        #cbar.set_label("AMPLITUDE")
        plt.pause(1/fps)
        start_frame = start_frame + (1/fps)
        if savebool == True:
            fig.savefig(direc+foldername+'/'+'plot'+str(i)+'.png')
        
        ax.cla()
    
    print("Done generating video from frames")
#%%
def density_plot(MAIN_list, strn, lam1 = 0.3):
  
    for jj in MAIN_list:
        bb = np.array(jj)
        data = bb.flatten()
        prob_density = kde.gaussian_kde(data)
        prob_density.covariance_factor = lambda : lam1
        prob_density._compute_covariance()
    
        x = np.linspace(data.min(), data.max(),200)
        y=prob_density(x)

        plt.plot(x, y)
        
    plt.title("Denisty plot for Q VOLTS distribution")
    plt.xlabel("Q (V)")
    plt.ylabel("Pixel value count")
    plt.legend(strn)
    plt.show()
        
#%%
def region_average(mat, xmin, xmax, ymin, ymax):
    cropped = mat[xmin:xmax, ymin:ymax]
    median = np.median(cropped)
    return median

#%%
def nparray_save(array, directory,filename):
    str1 = filename + '.npy'
    direc_1 = directory + str1
    np.save(direc_1, array)

     
         
         
         
         