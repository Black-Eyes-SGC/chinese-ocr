# -*- coding: utf-8 -*-
import torch
import dataset
import keys
import numpy as np

characters = keys.alphabet[:]
from model import get_model

nclass = len(characters)+1

import keras.backend as K

# trainroot = '../data/lmdb/train'
trainroot = './data'
valroot   = '../data/lmdb/val'
batchSize = 32
workers = 1
imgH = 32
imgW = 256
keep_ratio = False
random_sample = False


def one_hot(text,characters=characters):
    text = text.decode('utf-8')
    label = np.zeros(len(text))
    for i,char in enumerate(text):
        index = characters.find(char)
        if index==-1:
            index = characters.find(u' ')
        label[i] = index
    return label

n_len = 29 
def gen(loader,flag='train'):
    while True:
        i =0 
        n = len(loader)
        for X,Y in loader:
            X = X.numpy()
            X = X.reshape((-1,imgH,imgW,1))
            if flag=='test':
                Y = Y.numpy()
                
            Y = np.array(Y)
            Length = int(imgW/4)-1
            batchs = X.shape[0]
            #Y = Y.numpy()
            if i>n-1:
                i = 0
                break
                
            yield [X, Y, np.ones(batchs)*int(Length), np.ones(batchs)*n_len], np.ones(batchs)
        
if random_sample:
    sampler = dataset.randomSequentialSampler(train_dataset, batchSize)
else:
    sampler = None
train_dataset = dataset.lmdbDataset(root=trainroot,target_transform=one_hot)

'''
#sampler (Sampler, optional) – defines the strategy to draw samples from the dataset. If specified, shuffle must be False. http://pytorch.org/docs/master/data.html
train_loader = torch.utils.data.DataLoader(
    train_dataset, batch_size=batchSize,
    shuffle=False, sampler=sampler,
    num_workers=int(workers),
    collate_fn=dataset.alignCollate(imgH=imgH, imgW=imgW, keep_ratio=keep_ratio))
'''

train_loader = torch.utils.data.DataLoader(
    train_dataset, batch_size=batchSize,
    shuffle=True,
    num_workers=int(workers),
    collate_fn=dataset.alignCollate(imgH=imgH, imgW=imgW, keep_ratio=keep_ratio))

test_dataset = dataset.lmdbDataset(
    root=valroot, transform=dataset.resizeNormalize((imgW, imgH)),target_transform=one_hot)


test_loader = torch.utils.data.DataLoader(
        test_dataset, shuffle=True, batch_size=batchSize, num_workers=int(workers))


if __name__=='__main__':
    from keras.callbacks import ModelCheckpoint,ReduceLROnPlateau
    model,basemodel = get_model(height=imgH, nclass=nclass)
    import os
    if os.path.exists('../pretrain-models/keras.hdf5'):
       basemodel.load_weights('../pretrain-models/keras.hdf5')
    
    ##注意此处保存的是model的权重
    checkpointer = ModelCheckpoint(filepath="save_model/model{epoch:02d}-{val_loss:.4f}.hdf5",monitor='val_loss',         verbose=0,save_weights_only=False, save_best_only=True)
    rlu = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=1, verbose=0, mode='auto', epsilon=0.0001, cooldown=0, min_lr=0)

    model.fit_generator(gen(train_loader,flag='train'), 
                    steps_per_epoch=102400, 
                    epochs=200,
                    validation_data=gen(test_loader,flag='test'),
                    callbacks=[checkpointer,rlu],
                    validation_steps=1024)
