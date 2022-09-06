'''
Author: zhuyf
Date: 2022-02-09 19:34:46
LastEditors: zhuyf
LastEditTime: 2022-02-09 19:46:28
Description: file content
FilePath: /jp5_test/sub/check_job_info.py
'''
import os
import sys
import time
import math
import shutil
import numpy as np
import subprocess as sub
def check_job_info():
    sub.call("jsm > jsm.inp",shell = True)
    with open('jsm.inp','r') as file1:
        used=0
        for line in file1:
            try:
                if line.split()[3] == 'R':
                    used+=int(line.split()[5])
            except IndexError:
                pass
    os.remove('jsm.inp')
    return used
def main():
    used=check_job_info()
    print('-----------------------------------------')
    print(f'USED_core : {used}')
    print(f'FREE_core : 120 - {used} = {120-used}')
    print('-----------------------------------------')

if __name__ == '__main__':
    main()
    

