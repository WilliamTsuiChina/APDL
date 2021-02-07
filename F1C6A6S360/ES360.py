import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from time import strftime
from time import localtime
from time import sleep


os.chdir(os.path.dirname(__file__))
my_data = pd.read_table('ElemRes.txt', sep='|', index_col=[0, 1])

for k in range(0, 6):
    x = range(0, 360)
    y = []
    for i in range(0, 360):
        y.append(my_data.iloc[i * 6 + k, 1])

    elemnum = int(my_data.iloc[k, 0])
    plt.title(f'Axial Force of Element {elemnum}')
    plt.plot(x, y)
    y_min = np.argmin(y)
    y_max = np.argmax(y)
    show_min = '[' + str(y_min) + ' ' + str(y[y_min]) + ']'
    show_max = '[' + str(y_max) + ' ' + str(y[y_max]) + ']'
    plt.plot(y_min, y[y_min], 'ko')
    plt.plot(y_max, y[y_max], 'ko')
    plt.annotate(show_min, xy=(y_min, y[y_min]), xytext=(y_min, y[y_min]))
    plt.annotate(show_max, xy=(y_max, y[y_max]), xytext=(y_max, y[y_max]))
    
    time = strftime("%Y-%m-%d-%H%M%S", localtime())
    plt.savefig(f'Elem-{elemnum}-{time}.jpg')
    sleep(2)
    plt.cla()
    plt.close("all")





