# -*- coding: utf-8 -*-
import tensorflow as tf
import keras.backend.tensorflow_backend as ktf


def get_session(gpu_fraction=0.333):
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_fraction,
                                    allow_growth=True)
    return tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))

ktf.set_session(get_session())

from train import *
model,basemodel = get_model(height=imgH, nclass=nclass)
import os
modelPath = '../pretrain-models/keras.hdf5'
if os.path.exists(modelPath):
       basemodel.load_weights(modelPath)
        
train_loader = torch.utils.data.DataLoader(
    train_dataset, batch_size=batchSize,
    shuffle=True, sampler=sampler,
    num_workers=int(workers),
    collate_fn=dataset.alignCollate(imgH=imgH, imgW=imgW, keep_ratio=keep_ratio))

testSize = int(batchSize / 2)
#print test_dataset[0]
test_loader = torch.utils.data.DataLoader(
    test_dataset, batch_size=testSize,
    shuffle=True, num_workers=int(workers)    )

j = 0
crrentLoss = 1000
loss = 1000
interval  = 50


def input_length(x):
    return [0]


def label_length(labels):
    res = []
    for i in labels:
        res.append(len(i))
    return np.array(res)



for i in range(3):
    for X,Y in train_loader:
                X = X.numpy()
                X = X.reshape((-1,imgH,imgW,1))
                Y = np.array(Y)
                
                Length = int(imgW/4)-2 # sampling length, need to read ctc function
                batch = X.shape[0]
                X,Y = [X, Y, np.ones(batch)*Length, np.ones(batch)*n_len], np.ones(batch)    
                model.train_on_batch( X,Y)  
                if j%interval==0 :
                   X,Y  =  next(iter(test_loader))
                   X = X.numpy()
                   X = X.reshape((-1,imgH,imgW,1))
                   Y = Y.numpy()
                   Y = np.array(Y)
                   batch = X.shape[0]
                   X,Y = [X, Y, np.ones(batch)*Length, label_length(Y)], np.ones(batch) 
                   
                   crrentLoss = model.evaluate(X,Y)
                   print "step:{},loss:{},crrentLoss:{}".format(j,loss,crrentLoss)
                   if crrentLoss<loss:
                        loss = crrentLoss
                        path = 'save_model/model{}.h5'.format(loss)
                        print "save model:".format(path)
                        model.save(path)

                j+=1
                
