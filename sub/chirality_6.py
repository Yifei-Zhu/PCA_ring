#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 15:28:32 2021

@author: zyf
"""

import os
import shutil
import numpy as np
import time
import subprocess as sub
from sub.partition_5 import Regions
from sub.get_hop_points_2 import get_hop_info
import sub.sub_interface_json as sub_interface_json
from sub.descriptor_3 import main as main_descriptor_3
from sub.pca_4_1 import main as main_pca_4_1
from sub.mds_4_2 import main as main_mds_4_2
from sub.partition_5 import main as main_partition_5
from sub.check_job_info import check_job_info

class Chirality(Regions):
    def __init__(self,para_all):
        super().__init__(para_all)
        self.Chirality_swith = para_all['Chirality']
        self.Chiral_block = para_all['Chiral_block'].split(',')
        self.Chiral_block_nu = int(len(self.Chiral_block))
        self.basis=para_all['Chiral_basis'].lower()
        if self.basis == 'd':
            self.path_main=f'{self.hopdir}cluster/'
    def chiral_all(self):
        if self.Chirality_swith == 'yes':
            if self.basis == 'p':
                path_old = f'{self.path_main}{self.partition_descriptor}/'
                for i in range(100):
                    nos =i+1
                    path_rename = f'{self.path_main}{self.partition_descriptor}_before_chiral_{nos}/'
                    if not os.path.exists(path_rename):
                        os.rename(path_old,path_rename)
                        break
                block_dict = np.load(f'{path_rename}block_info_{self.partition_method}.npy',\
                                allow_pickle=True).item()
            elif self.basis == 'd':
                for i in range(100):
                    nos =i+1
                    path_rename = f'{self.hopdir}cluster_before_chara_{nos}/'
                    if not os.path.exists(path_rename):
                        os.rename(self.path_main,path_rename)
                        break
                    os.mkdir(self.path_main)
                    shutil.move(path_rename,self.path_main)
                    path_rename = f'{self.path_main}cluster_before_chara_{nos}/' 
                block_dict = np.load(f'{path_rename}cluster_list.npy',\
                                allow_pickle=True).item()
                
            print(block_dict.keys())
            for iblock in range(self.Chiral_block_nu):
                i_block = int(self.Chiral_block[iblock])
                if self.basis == 'p':
                    print(f'block: {i_block}\n')
                elif self.basis == 'd':
                    print(f'cluster: {i_block}\n')
                for i_file in block_dict[i_block]:
                    print(i_file)
                    os.rename(f'{self.hopdir}{i_file}/{i_file}.xyz',f'{self.hopdir}{i_file}/{i_file}.xyz_old')
                    os.rename(f'{self.hopdir}{i_file}/{i_file}.gjf',f'{self.hopdir}{i_file}/{i_file}.gjf_old')
                    with open(f'{self.hopdir}{i_file}/{i_file}.xyz_old','r') as file1,\
                    open(f'{self.hopdir}{i_file}/{i_file}.xyz','w') as file2:
                        for i in range(self.natom):
                            line=file1.readline()
                            atom, x_coor, y_coor, z_tmp = line.split()
                            z_coor = -float(z_tmp)
                            line_file2 = f'{atom}\t{x_coor}\t{y_coor}\t{z_coor}\n'
                            file2.write(line_file2)
    def re_gaussian_after_chiral(self):
        if self.basis == 'p':
            for i in range(100):
                nos =i+1
                path_rename = f'{self.path_main}{self.partition_descriptor}_before_chiral_{nos}/'
                if not os.path.exists(path_rename):
                    path_rename = f'{self.path_main}{self.partition_descriptor}_before_chiral_{i}/'
                    break
            block_dict = np.load(f'{path_rename}block_info_{self.partition_method}.npy',allow_pickle=True).item()
        elif self.basis == 'd':            
            for i in range(100):
                nos =i+1
                path_rename = f'{self.path_main}cluster_before_chiral_{nos}/'
                if not os.path.exists(path_rename):
                    path_rename = f'{self.path_main}cluster_before_chiral_{i}/'
                    break
            block_dict = np.load(f'{path_rename}cluster_list.npy',allow_pickle=True).item()
        with open(f'{self.path_main}qsub_chiral_all.sh','w') as f1:
            f1.write('#PBS -N chiral\n#PBS -l walltime=999:00:00\n#PBS -j oe\n#PBS -q eth\n#PBS -l nodes=1:ppn=4\n#PBS -V\n\n')
            run=[]
            for iblock in range(self.Chiral_block_nu):
                i_block = int(self.Chiral_block[iblock])
                # print(block_dict.keys())
                for i_file in block_dict[i_block]:
                    workdir = f'{self.hopdir}{i_file}/'
                    run.append(int(i_file))
            #         f1.write(f'cd {workdir}\n')
            #         f1.write(f'output= \'rung16 {i_file}.gjf\'\n')
            strs=f'{run}'.lstrip('[').rstrip(']').replace(' ','')
            # f1.write(f'cd {self.hopdir}\n')
            # f1.write(f'for i in {{{strs}}};do cd $i;rung16 $i.gjf;cd ..;done\n')
            f1.write(f'rung16 {{{strs}}}/*.gjf\n')
            # f1.write(f'cd {self.path_main}\n')
            
            # os.chdir(f'{self.path_main}')
            # # sub.call(f'qsub qsub_chiral_all.sh',shell = True)


        # num = 0
        # for iblock in range(self.Chiral_block_nu):
        #     i_block = int(self.Chiral_block[iblock])
        #     # print(block_dict.keys())
        #     for i_file in block_dict[i_block]:
        #         workdir = f'{self.hopdir}{i_file}/'
        #         os.chdir(workdir)
        #         # print(i_file)
        #         sub.call(f'rung16 {i_file}.gjf',shell = True)
        #         num += 1
        #         used = check_job_info()
        #         #work_limit= (self.total_cores-used)/self.single_task_num
        #         work_limit=10
        #         while num == work_limit:
        #             time.sleep(5)
        #             num = 0
        #     time.sleep(10)



def control(para_all):
    hopinfo = get_hop_info(para_all)
    chirality = Chirality(para_all)
    print("Step1:Enter '1' or 'c' to perform the mirror symmetry operation")
    print("Step2:Enter '2' to run get_gjf()")
    print("Step3:Enter '3' to run re_gaussian_after_chiral()")
    print("Step4:Enter '4' or 'g' to retrieve coordinate information.")

    signal=input()
    if signal == '1' or signal == 'c':
        chirality.chiral_all()
    elif signal == '2':
        hopinfo.get_gjf()
    elif signal == '3':
        chirality.re_gaussian_after_chiral()
    elif signal == '4' or signal == 'g':
        hopinfo.get_info()
       

      
def main():
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    control(para_all)


if __name__ == '__main__':
    main()
    
    
    
    
