'''
Author: zhuyf
Date: 2022-03-02 11:39:54
LastEditors: zhuyf
LastEditTime: 2022-03-07 16:15:32
Description: file content
FilePath: /jp6_test/sub/get_s0_info.py
'''
import os
import time
import shutil
import linecache
from unittest import signals
import numpy as np
import subprocess as sub
import sub.sub_interface_json as sub_interface_json
from sub.get_hop_points_2 import get_hop_info
import sub.check_job_info as check_job_info

class get_s0_info(get_hop_info):
    def __init__(self,para_all):
        super().__init__(para_all)
    
    def get_gjf(self):
        optpath= f'{self.opt_dir}{self.optgjf}'
        hoplist=np.load(self.hop,allow_pickle=True).tolist()
        new_hoplist=[]
        for i in hoplist:
            s0_nu=str(int(i)+10000)
            new_hoplist.append(s0_nu)
            if not os.path.exists(f'{self.hopdir}{s0_nu}'):
                os.mkdir(f'{self.hopdir}{s0_nu}')
            with open(optpath,'r') as file1,open(f'{self.hopdir}{s0_nu}/{s0_nu}.gjf','w') as file2:
                for line in file1:
                    if 'Title Card Required' in line:
                        file2.write(line)
                        file2.write('\n')
                        file2.write('0 2\n')#故意设置错能快速拿到键长键角等信息
                        break
                    else:
                        file2.write(line)
            # if int(i) > 10000:
            #     nu = i-10000
            # else:
            #     nu=i\
            
            with open(f'{self.work_dir}{i}/traj_time.out','r') as file3,\
                open(f'{self.hopdir}{s0_nu}/{s0_nu}.gjf','a+') as file4,\
                open(f'{self.hopdir}{s0_nu}/{s0_nu}.xyz','w') as file5:
                    file3.readline()
                    file3.readline()
                    n_line=0
                    for line in file3:
                        n_line+=1
                        file4.write(line)
                        file5.write(line)
                        if n_line == self.natom:
                            break
                    file4.write('\n')
        new_hoplist+=hoplist
        np.save(f'{self.hopdir}hop_s0.npy',new_hoplist)
                        
    
    
    
    
def main():
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    s0_info=get_s0_info(para_all)
    signal=input('1 - get gjf; 2 - sub gaussian; 3- get information \n')
    if signal == '1':
        s0_info.get_gjf()
    elif signal == '2':
        s0_info.sub_gaussian()
    elif signal == '3':
        s0_info.get_info()


if __name__ == '__main__':
    main()
