import matplotlib.pyplot as plt
import numpy as np
from secrets import choice
from utils.iterable_utils import OverloadedList, OverloadedSet

from utils import logger

def draw_3d_plot(x_axis:OverloadedList=None, y_axis:OverloadedList=None, z_axis:OverloadedList=None, size:int=1):
    if not z_axis:
        z_axis = OverloadedList([0 for _ in range(0, x_axis.len)])
    plt.axes(projection="3d")
    plt.plot(x_axis, y_axis, z_axis, color='#5d9c25', linewidth=0, marker=',', markerfacecolor='#6be302', markersize=size)
    plt.title(f'Frequency of Values')
    plt.xlabel("Values -->")
    plt.ylabel("Frequencies -->")
    plt.show()

def draw_scatter(x_axis:OverloadedList=None, y_axis:OverloadedList=None, size:int=1, *args, **kargs):
    plt.scatter(x=x_axis, y=y_axis, s=np.array([size]), color = 'hotpink', marker = ',', linewidths = 0.25)
    plt.title(f'Frequency of Values')
    plt.xlabel("Values -->")
    plt.ylabel("Frequencies -->")
    plt.show()

def draw_hist(_list:OverloadedList = None, bins:int=0, *args, **kargs):
    plt.hist(x=_list, bins=bins, histtype="step", align='mid', orientation='vertical', log=False)
    plt.title(f'{bins} Bins')
    plt.xlabel("Values -->")
    plt.ylabel("Frequencies -->")
    plt.show()

def draw(x_axis: OverloadedList = None, y_axis: OverloadedList = None, _list:OverloadedList = None, *args, **kwargs):
    ## NOTE: This is not exactly needed and it is not very helpful for the current dataset, either.
    # _ = draw_3d_plot(x_axis=x_axis, y_axis=y_axis, size=1)
    _ = draw_scatter(x_axis=x_axis, y_axis=y_axis, size=1)
    _ = draw_hist(_list=_list, bins=10)
    _ = draw_hist(_list=_list, bins=100)
    _ = draw_hist(_list=_list, bins=1_000)
    _ = draw_hist(_list=_list, bins=OverloadedSet(_list).len)
    

    return True


def check(start: int = 0, end: int = 10_000, step: int = 1, *args, **kwargs):
    logger.info(f"Start: {start}\tEnd: {end}\tStep: {step}")

    choices = [i for i in range(0, 1_000_000, 1)]
    arr = [choice(choices) for _ in range(start, end, step)]
    
    arr_list = OverloadedList(arr)
    arr_set = OverloadedSet(arr)

    logger.info(f"RMS (List): {arr_list.rms()}\tRMS (Set): {arr_set.rms()}")
    logger.info(f"Mean (List): {arr_list.mean()}\t Mean (Set): {arr_set.mean()}")
    logger.info(f"Median (List): {arr_list.median()}\t Median (Set): {arr_set.median()}")

    values, frequencies = arr_list.frequencies
    if values.len > 0 and frequencies.len > 0 and values.len == frequencies.len:
        draw(x_axis=values, y_axis=frequencies, _list=arr_list)
    else:
        logger.exception(f"Values: {values.len}\t Frequencies: {frequencies.len}")
        return False
    return True

if __name__ == "__main__":
    check()