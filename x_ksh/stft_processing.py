#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 18:53:10 2018

@author: kimseunghyuck
"""

import librosa
import numpy as np
from matplotlib import pyplot as plt
#import labels
import tensorflow as tf
tf.set_random_seed(777) 
import pandas as pd
#train = pd.read_csv('/Users/kimseunghyuck/desktop/sound_train.csv')
train = pd.read_csv('/home/paperspace/Downloads/audio_train.csv')

#train/test, Data/Label split
from sklearn.model_selection import train_test_split
train_set, test_set = train_test_split(train, test_size = 0.3)
trainfile = train_set.values[:,0]
testfile = test_set.values[:,0]
trainLabel = train_set.values[:,1]
testLabel = test_set.values[:,1]

#data load and extract mfcc (scaling indluded)
#path = '/Users/kimseunghyuck/desktop/audio_train/'
path = '/home/paperspace/Downloads/audio_train/'

def see_how_long(file):
    c=[]
    for filename in file:
        y, sr = librosa.core.load(path+filename, mono=True, res_type="kaiser_fast")
        stft=librosa.core.stft(y,1024,512)        
        abs_stft=np.abs(stft)
        #1025 X t 형태
        c.append(abs_stft.shape[1])
    return(c)
 
#n=see_how_long(trainfile)
#print(np.max(n), np.min(n))      #1292 14
#n2=see_how_long(testfile)
#print(np.max(n2), np.min(n2))    #1292 13

#show me approximate wave shape
filename= trainfile[1470]
y, sr = librosa.core.load(path+filename, mono=True, res_type="kaiser_fast")
stft=librosa.core.stft(y,1024,512)
print(stft.shape)   #(513, 1148), (513, 25), (513, 28)
plt.plot(stft[3,])
plt.plot(stft[2,])


#2 seconds(100 segments) extract
def two_sec_extract(file):
    #zero padding to file.shape[0] X 513 X 100    
    n=file.shape[0]
    array = np.repeat(0., n * 513 * 100).reshape(n, 513, 100)
    k=0    
    for filename in file:    
        y, sr = librosa.core.load(path+filename, mono=True, res_type="kaaiser_fast")
        stft=librosa.core.stft(y,1024,512)
        length=stft.shape[1]
        if length == 100:
            array[k, :, :]=stft
        elif length < 100:
            array[k, :, :length]=stft
        elif length > 100:
            sample = np.repeat(0., (length - 100)*513).reshape(513,length - 100)
            for j in range(length - 100):
                for i in range(513):
                    sample[i,j]=np.var(stft[i,j:j+100])
            A=np.argmax(sample, axis=1)
            start=np.argmax(np.bincount(A))
            array[k, :, :]=stft[:, start:start+100]
        k+=1
    return(array)

trainData=two_sec_extract(trainfile)
testData=two_sec_extract(testfile)

print(trainData.shape, testData.shape, trainLabel.shape, testLabel.shape)
# (6631, 20, 430) (2842, 20, 430) (6631,) (2842,)

#how many kinds of label?
print(len(np.unique(trainLabel)))   #41
print(len(np.unique(testLabel)))    #41

#label string -> integer(0~40)

def Labeling(label):
    #idx = np.unique(train.values[:,1])     #이건 abc 순
    idx = train.label.unique()
    r=pd.Series(label)
    for i in range(len(idx)):
        r[r.values==idx[i]]=i
    return(r)

trainLabel=Labeling(trainLabel)
testLabel=Labeling(testLabel)
print(min(trainLabel), max(trainLabel), min(testLabel), max(testLabel))
#0 40 0 40

#csv downdload totally about 600MB
trainData2D=trainData.reshape(-1, 513*100)
testData2D=testData.reshape(-1, 513*100)
np.savetxt('/home/paperspace/Downloads/trainData6.csv', 
           trainData2D, delimiter=",")
np.savetxt('/home/paperspace/Downloads/testData6.csv', 
           testData2D, delimiter=",")
np.savetxt('/home/paperspace/Downloads/trainLabel6.csv', 
           trainLabel, delimiter=",")
np.savetxt('/home/paperspace/Downloads/testLabel6.csv', 
           testLabel, delimiter=",")

