#Useful functions for 1.Data Preprocessing
# coding: utf-8
import numpy as np
import pandas as pd
import time
import datetime

# ## for converting raw signals to meaningful signal
def convert_ECG(signal):
    #refer to bioplux ECG datasheet
    signal = np.array(signal)
    n = 8
    VCC = 3
    G_ecg = 1000
    ECG = (signal/2**n - 0.5)*VCC*1000 / G_ecg 
    return ECG

def convert_RESP(signal):
    #refer to bioplux RESP(PZT) datasheet
    signal = np.array(signal)
    n = 8
    RESP = (signal/2**n - 0.5)*100
    return RESP

def convert_EDA(signal):
    #refer to bioplux EDA datasheet
    signal = np.array(signal)
    n=8
    VCC=3
    EDA = (signal*VCC)/(0.12*(2**n))
    return EDA

def convert_TEMP(signal):
    #refer to bioplux TEMP datasheet
    signal = np.array(signal)
    VCC=3
    a_0 = 1.12764514 * 1e-3
    a_1 = 2.34282709 * 1e-4
    a_2 = 8.77303013 * 1e-8
    n = 8
    NTC_V = signal*VCC / (2**n)
    NTC_omiga = 1e4*NTC_V / (VCC-NTC_V)
    TMP_K = 1/(a_0 + a_1*np.log(NTC_omiga) + a_2*(np.log(NTC_omiga)**3))
    TMP_C = TMP_K - 273.15
    return TMP_C
    
def convert_bio(name,signal):
    if name == "ECG":
        return convert_ECG(signal)
    elif name == "RESPIRATION":
        return convert_RESP(signal)
    elif name == "TEMP":
        return convert_TEMP(signal)
    elif name == "EDA":
        return convert_EDA(signal)


# ## for processing biosignals file
def bio_header_process(header, filename):
    #日付取得
    temp_date = filename.split("_")
    date = temp_date[2]
    #センサ名取得
    sensor_index1 = header[1].find("[")
    sensor_index2 = header[1].find("]")
    used_sensor = header[1][sensor_index1+1:sensor_index2]	#使用したセンサ名
    used_sensor = eval("["+used_sensor+"]")	#used_sensorの型の変換
    #時間取得
    time_index1 = header[1].find("time")
    time_index2 = header[1].find(".", time_index1,time_index1+30)
    temp_time = header[1][time_index1+8:time_index2]
    #タイムスタンプ作成
    temp_datetime = date + ' ' + temp_time
    timestamp = time.mktime(datetime.datetime.strptime(temp_datetime, "%Y-%m-%d %H:%M:%S").timetuple())
    #サンプリングレート取得
    samplingrate_index1 = header[1].find("sampling rate")
    samplingrate_index2 = header[1].find(",", samplingrate_index1, samplingrate_index1+30)
    samplingrate = int(header[1][samplingrate_index1+16:samplingrate_index2])
    return used_sensor, timestamp, samplingrate


def read_bio_data(file_path):
    
    '''
    usage: bio_data = read_bio_data(file_path)
    return pd.DataFrame [ECG,RESPIRATION,TEMP,EDA,TIME]  //TIME is absolute timestamp , unit is second.
    '''
    
    f = open(file_path,'r')
    header = [0]*3
    for i in range(3):
        header[i] = f.readline()
    temp_data = f.readlines()
    f.close()
    file_name = file_path.split("/")[-1]
    bio_channels, bio_start_time, samplingrate = bio_header_process(header, file_name)

    
    bio_data = []
    for idx,i in enumerate(temp_data):
        bio_data.append([float(j) for j in i.rstrip().split("\t")]+[idx/samplingrate+bio_start_time])
    bio_data = np.array(bio_data)[:,2:]
    
    
    df = pd.DataFrame(columns=bio_channels+["TIME"],data=bio_data)
    for bio_channel in  bio_channels:
        df[bio_channel] = convert_bio(bio_channel,df[bio_channel])

    return df,samplingrate




