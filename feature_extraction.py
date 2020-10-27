
# coding: utf-8
import numpy as np
import pandas as pd
import math
import biosppy
from scipy import signal
 

def find_idx(data,low,high):
    indices = []
    for i in range(len(data)):
        if data[i] <= high and data[i] >= low:indices.append(i)
    return indices

# ## Calculate LF/HF

def cal_lf_hf(rri):
    n=len(rri)

    VLF, LF, HF = 0.04, 0.15, 0.40
    
    lf_hf = []

    for i in range(len(rri) - n + 1):
      f, p = signal.welch(rri[i:i + n], nperseg=min(n, 256))
      lf_freq_band = (f >= VLF) & (f <= LF)
      lf = np.trapz(y=p[lf_freq_band], x=f[lf_freq_band])
      hf_freq_band = (f >= LF) & (f <= HF)
      hf = np.trapz(y=p[hf_freq_band], x=f[hf_freq_band])
      lf_hf.append((lf / hf).round(6))

    return lf_hf[0]


# ## Feature Extraction

def extract_ecg_features_from_rri(RRI):
    try:
        #RRI = [float(r_pearks[i+1] - r_pearks[i])/float(SAMPLE_RATE_BIO) for i in range(len(r_pearks)-1)]
        N = len(RRI)
        rri = np.mean(RRI)
        rrv = np.var(RRI)
        CVNN = rri/rrv
        consecutive_difference = [np.abs(float(RRI[i+1] - RRI[i])) for i in range(len(RRI)-1)]
        pNN50 = np.sum(np.array([i-0.05>0 for i in consecutive_difference],float)) / len(consecutive_difference)
        RMSSD = np.sqrt( np.sum([np.square(i) for i in consecutive_difference]) / len(consecutive_difference) ) 
        
        lorentz_points = []
        for idx in range(len(RRI)-1):
            lorentz_points.append(np.array([RRI[idx],RRI[idx+1]]))
        lorentz_points = np.array(lorentz_points)
        lorentz_rotated = [ ((point[0] + point[1]) / math.sqrt(2), (-point[0] + point[1]) / math.sqrt(2))
              for point in lorentz_points]
        L, T = (np.std(vals) for vals in zip(*lorentz_rotated))
        CSI = round(L / T, 6)
        if(L*T==0):
            print(len(RRI))
            
        CVI = round(math.log10(L * T), 6)


        f, Pxx_den = signal.welch(RRI, fs=1.0,nperseg=min(N,256))
        #plt.semilogy(f, Pxx_den)
        LF_indices = find_idx(f,low=0.04,high=0.15)
        LF = np.sum(Pxx_den[LF_indices])

        MF_indices = find_idx(f,low=0.08,high=0.15)
        MF = np.sum(Pxx_den[MF_indices])

        HF_indices = find_idx(f,low=0.15,high=0.4)
        HF = np.sum(Pxx_den[HF_indices])

        LF_HF = (LF+MF)/HF
        HF_ratio = HF / (LF+MF+HF)

        HF_peak_power = np.max(Pxx_den[HF_indices])
        HF_peak_freq = f[np.argmax(Pxx_den[HF_indices]) + HF_indices[0]]

        #LF_HF_k = cal_lf_hf(RRI)

        features = {"N":N,"RRI":rri,"RRV":rrv,"CVNN":CVNN,"pNN50":pNN50,"RMSSD":RMSSD,
        "L":L,"T":T,"CVI":CVI,"CSI":CSI,"LF":LF,"HF":HF,"MF":MF,"LF_HF":LF_HF,
        "HF_ratio":HF_ratio,"HF_peak_power":HF_peak_power,"HF_peak_freq":HF_peak_freq}
    except:
        features = {"N":np.NAN,"RRI":np.NAN,"RRV":np.NAN,"CVNN":np.NAN,"pNN50":np.NAN,"RMSSD":np.NAN,
        "L":np.NAN,"T":np.NAN,"CVI":np.NAN,"CSI":np.NAN,"LF":np.NAN,"HF":np.NAN,"MF":np.NAN,"LF_HF":np.NAN,
        "HF_ratio":np.NAN,"HF_peak_power":np.NAN,"HF_peak_freq":np.NAN}

    return features




