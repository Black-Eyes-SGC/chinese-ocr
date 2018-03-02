# -*- coding: utf-8 -*-
# Author: lizhenyang@jd.com
# Description: complement the pic and text

import os
import sys
import glob

from PIL import Image 

text_c = '_'
image_c = 0
imgH = 32

def text(path):
    # 获取最大长度
    maxl = 0
    line = ''
    label_files = glob.glob(os.path.join(path, '*.txt'))

    labels = []
    for f in label_files:
        print f
        with open(f, 'r') as inf:
            text = inf.read().strip()
            print text
            labels.append(text)
            label_len = len(text.decode('utf-8'))
            print label_len
            if maxl < label_len:
                maxl = label_len
                line = text
    print 'max length:', maxl
    print line


    # 使用字符补齐
    for i, f in enumerate(label_files):
        with open(f, 'w') as outf:
            outf.write(labels[i])
            for j in range(len(labels[i].decode('utf-8')), maxl):
                outf.write(text_c)
        

def image(path):
    maxw = 0
    maxf = ''
    files = glob.glob(os.path.join(path, '*.jpg'))
    for f in files:
        img = Image.open(f)
        if img.size[0] > maxw:
            maxw = img.size[0]
            maxf = f
        img.close()

    print 'max width:', maxw
    print maxf

    for f in files:
        img = Image.open(f)
        newp = Image.new('RGB', (maxw, imgH), (image_c,image_c,image_c))
        newp.paste(img)
        newp.save(f)


def main():
    path = sys.argv[1]
    text(path)
    image(path)


if __name__ == '__main__':
    main()
