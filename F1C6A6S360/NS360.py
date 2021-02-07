import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from time import strftime
from time import localtime
from time import sleep


os.chdir(os.path.dirname(__file__))
my_data = pd.read_table('NodeRes.txt', sep='|', index_col=[0, 1])

for k in range(0, 6):
    x = range(0, 360)
    yfx = []
    yfy = []
    yfz = []
    for i in range(0, 360):
        yfx.append(my_data.iloc[i * 6 + k, 1])
        yfy.append(my_data.iloc[i * 6 + k, 2])
        yfz.append(my_data.iloc[i * 6 + k, 3])

    nodenum = int(my_data.iloc[k, 0])
    plt.title(f'Force Reaction of Node {nodenum}')
    plt.plot(x,yfx,label='Fx')
    plt.plot(x,yfy,label='Fy')
    plt.plot(x,yfz,label='Fz')
    plt.legend()
    y_min = np.argmin(yfx)
    y_max = np.argmax(yfx)
    show_min = '[' + str(y_min) + ' ' + str(yfx[y_min]) + ']'
    show_max = '[' + str(y_max) + ' ' + str(yfx[y_max]) + ']'
    plt.plot(y_min, yfx[y_min], 'ko')
    plt.plot(y_max, yfx[y_max], 'ko')
    plt.annotate(show_min, xy=(y_min, yfx[y_min]), xytext=(y_min, yfx[y_min]))
    plt.annotate(show_max, xy=(y_max, yfx[y_max]), xytext=(y_max, yfx[y_max]))

    y_min = np.argmin(yfy)
    y_max = np.argmax(yfy)
    show_min = '[' + str(y_min) + ' ' + str(yfy[y_min]) + ']'
    show_max = '[' + str(y_max) + ' ' + str(yfy[y_max]) + ']'
    plt.plot(y_min, yfy[y_min], 'ko')
    plt.plot(y_max, yfy[y_max], 'ko')
    plt.annotate(show_min, xy=(y_min, yfy[y_min]), xytext=(y_min, yfy[y_min]))
    plt.annotate(show_max, xy=(y_max, yfy[y_max]), xytext=(y_max, yfy[y_max]))

    y_min = np.argmin(yfz)
    y_max = np.argmax(yfz)
    show_min = '[' + str(y_min) + ' ' + str(yfz[y_min]) + ']'
    show_max = '[' + str(y_max) + ' ' + str(yfz[y_max]) + ']'
    plt.plot(y_min, yfz[y_min], 'ko')
    plt.plot(y_max, yfz[y_max], 'ko')
    plt.annotate(show_min, xy=(y_min, yfz[y_min]), xytext=(y_min, yfz[y_min]))
    plt.annotate(show_max, xy=(y_max, yfz[y_max]), xytext=(y_max, yfz[y_max]))
    
    time = strftime("%Y-%m-%d-%H%M%S", localtime())
    plt.savefig(f'Node-{nodenum}-{time}.jpg')
    sleep(2)
    plt.cla()
    plt.close("all")





