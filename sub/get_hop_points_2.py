#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 09:00:34 2021

@author: zyf
"""
import os
# from re import A
import time
import shutil
import linecache
import numpy as np
import subprocess as sub
import sub.sub_interface_json as sub_interface_json
from sub.JADE_dyn_1 import jade_dyn
from sub.check_job_info import check_job_info

class get_hop_info(jade_dyn):
    def __init__(self,para_all):
        super().__init__(para_all)
        self.hopdir = f'{self.work_dir}hop_points/'
        self.elements = ['R','A','D']
        self.hop=f'{self.hopdir}hop.npy'
        self.nohop=f'{self.hopdir}nohop.npy'
        path = f'{self.work_dir}{self.start_nu}/traj_time.out'
        with open(path, "r", encoding="utf-8") as file:
            line = file.readline()
            self.natom= int(line.split()[0])
        self.total_cores = int(para_all['total_avail_cores'])
        # self.ring = para_all['whether_on_ring'].lower()
        # self.remake_after_block = para_all['remake_after_block'].lower()
        # self.remake_after_cluster = para_all['remake_after_cluster'].lower()
        # if self.remake_after_block == 'yes' and self.remake_after_cluster == 'yes':
        #     print('At least one of [remake_after_block] and [remake_after_cluster] is [No]!!!')
        #     os._exit()
        # elif self.remake_after_cluster != 'yes' and self.remake_after_block != 'yes':
        #     self.remake = 'no'
        # else:
        #     self.remake = 'yes'
        # if self.remake == 'yes' and para_all['S0_involve'].lower() == 'yes':
        #     os._exit(0)
        # else:
        #     self.s0=para_all['S0_involve'].lower()
        self.s0=para_all['S0_involve'].lower()
        
    def abstract_coor(self):
        if os.path.exists(self.hopdir):
            shutil.rmtree(self.hopdir)
        os.mkdir(self.hopdir)
        os.chdir(self.hopdir)
        nohop,hop,errorlist_nohop, errorlist_nostep = [],[],[],[]
        notcompleted = []
        for i in range(self.file_nu):
            path=f'{self.hopdir}all.xyz'
            path1 = f'{self.work_dir}{self.start_nu+i}/current_state.out'
            path2 = f'{self.work_dir}{self.start_nu+i}/traj_time.out'
            try:
                with open(path1, "r", encoding="utf-8") as file1:
                    linenu =-2 
                    for line in file1:
                        linenu+=1
                        try:
                            state = line.split()[2]
                        except IndexError:
                            line=file1.readline()
                        else:
                            state = line.split()[2]

                        if state == '1':
                            step = int(line.split()[0])-1
    #                        print(step)
                            break
                        else:
                            step='None'


                if step =='None':
                    nohop.append(f'{self.start_nu+i}')
    #                print(linenu)
                    if linenu != self.step:
                        errorlist_nostep.append(f'{self.start_nu+i}')
                    else:
                        errorlist_nohop.append(f'{self.start_nu+i}')
                else:
                    hop.append(f'{self.start_nu+i}')
                    workdir = f'{self.hopdir}{self.start_nu+i}'
                    if os.path.exists(workdir):
                        shutil.rmtree(workdir)
                    os.mkdir(workdir)
                    os.chdir(workdir)
                    try:
                        with open(path2, "r", encoding="utf-8") as file2,\
                        open(f'{self.start_nu+i}.xyz' , "w", encoding="utf-8") as file3,\
                        open(path, "a", encoding="utf-8") as file4:
                            file4.write(str(self.natom))
                            file4.write(' \n')
                            file4.write(' \n')
                            linenum=1
                            for line in file2:
                                if len(line.split())>=2:
                                    if line.split()[2] != str(step):
                                        linenum += 1
                                    else:
                                        linenum += 1
                                        break
                                else:
                                    linenum += 1
                            for i in range(self.natom):
                                num=int(linenum+i)
                                line = linecache.getline(path2,num)
                                for strs in line:   
                                    file3.write(strs)
                                    file4.write(strs)
                    except:
                        pass
            except FileNotFoundError:
                pass
        np.save(self.hop,hop)
        np.save(self.nohop,nohop)
        np.save(f'{self.hopdir}errorlist_nohop_step<{self.step}.npy',errorlist_nostep)
        np.save(f'{self.hopdir}errorlist_nohop_step={self.step}.npy',errorlist_nohop)


    def get_gjf(self):
        hop=np.load(self.hop)
        for i in hop:
            workdir = f'{self.hopdir}{i}/'
            os.chdir(workdir)
            path = f'{self.opt_dir}{self.optgjf}'
            with open(f'{path}', "r", encoding="utf-8") as file1,\
            open(f'{i}.gjf', "w", encoding="utf-8") as file2:
                for line in file1:
                    if 'Title Card Required' in line:
                        file2.write(line)
                        file2.write('\n')
                        file2.write('0 2\n')#故意设置错能快速拿到键长键角等信息
                        break
                    else:
                        file2.write(line)
            with open(f'{i}.xyz', "r", encoding="utf-8") as file3,\
            open(f'{i}.gjf', "a+", encoding="utf-8") as file4:
                for line in file3:
                    file4.write(line)
                file4.write('\n')

    def sub_gaussian(self):
        if self.s0 != 'yes':
            hop=np.load(self.hop)
        else:
            hop=np.load(f'{self.hopdir}hop_s0.npy')
        num = 0
        for i in hop:
            workdir = f'{self.hopdir}{i}/'
            os.chdir(workdir)
            sub.call(f'rung16 {i}.gjf',shell = True)
            num += 1
            used = check_job_info()
            work_limit= (self.total_cores-used)/self.single_task_num
            while num == work_limit:
                time.sleep(10)
                num = 0
        time.sleep(30)

    def testing1(self):
        errorlist1 = []
        errorlist2 = []
        if self.s0 != 'yes':
            hop=np.load(self.hop)
        else:
            hop=np.load(f'{self.hopdir}hop_s0.npy')
        for i in hop:
                workdir = f'{self.hopdir}{i}/'
                os.chdir(workdir)
                files = os.listdir(workdir)
                if len(files) != 5:
                    print(files)
                    errorlist1.append(i)
        for i in hop:
                workdir = f'{self.hopdir}{i}/'
                os.chdir(workdir)
                logpath = f'{workdir}{i}.log'
                if i not in errorlist1:
                    with open(logpath, "r", encoding="utf-8") as file:
                        signal1 = 0
                        for line in file:
                            if 'Initial Parameters' in line:
                                signal1 = 1
                                break
                        if signal1 != 1:
                            errorlist2.append(i)
        if errorlist1:
            print('Wrong number of files.')
            print(errorlist1)
        elif errorlist2:
            print('There is no information in the log file.')
            print(errorlist2)
        else:
            print('Done')
        errorlist = errorlist1+errorlist2
        return errorlist            
  
    def re_sub_gaussian_error(self,errorlist):
        for errordir in errorlist:
            workdir = f'{self.hopdir}{errordir}/'
            os.chdir(workdir)
            sub.call(f'rung16 {errordir}.gjf',shell = True)
            
    def get_info(self):
        if self.s0 != 'yes':
            hop=np.load(self.hop)
        else:
            hop=np.load(f'{self.hopdir}hop_s0.npy')
        self.H_list=[]
        with open(f'{self.hopdir}{hop[0]}/{hop[0]}.gjf', 'r') as f1:
            nus=0
            for line in f1:
                if line.split() and line.split()[0] == '0':
                    nus=-1
                nus+=1
                if line.split() and line.split()[0] == 'H':
                    self.H_list.append(str(nus))
                        
        for i in hop:
            workdir = f'{self.hopdir}{i}/'
            os.chdir(workdir)
            logpath = f'{workdir}{int(i)}.log'
            with open(logpath, "r", encoding="utf-8") as file1,\
            open(f'{logpath}_tmp', "w", encoding="utf-8") as file2:
                # print(f'{logpath}_tmp')
                for line in file1:
                    if len(line.split()) >= 2:
                        while line.split()[0] == '!' and\
                        line.split()[1][0] in self.elements:
                            info = line.split()[1:4]
                            for strs in info:
                                file2.write(f'{strs}\t')
                            file2.write('\n')
                            if ' ------------------------' in line:
                                break
                            break
        errorlist = self.testing2()
        if errorlist:
            os._exit(0)
        for i in hop:
            for element in self.elements:
                workdir = f'{self.hopdir}{i}/'
                logpath = f'{workdir}{i}.log'
                if os.path.exists(f'{workdir}{element}'):
                    shutil.rmtree(f'{workdir}{element}')
                os.mkdir(f'{workdir}{element}')
                with open(f'{logpath}_tmp', "r", encoding="utf-8") as file3,\
                open(f'{workdir}{element}/H_{element}.dat', "w", encoding="utf-8") as file4,\
                open(f'{workdir}{element}/{element}.dat', "w", encoding="utf-8") as file5:
                    # H_list = ['7','8','11','12','13']
                    # print(self.H_list)
                    for line in file3:
                        if line.split()[0][0] == element:
                            list1 = line.split()[1].strip(element).lstrip('(').rstrip(')').split(',')
                            s = list(set(self.H_list)&set(list1))
                            if s:
                                file4.write(line)
                            else:
                                file5.write(line)
                

    def testing2(self):
        errorlist,errornu = [],[]
        if self.s0 != 'yes':
            hop=np.load(self.hop)
        else:
            hop=np.load(f'{self.hopdir}hop_s0.npy')
        logtmppath_ex = f'{self.hopdir}{hop[0]}/{hop[0]}.log_tmp'
        with open(logtmppath_ex, "r", encoding="utf-8") as file1:
            example = file1.readlines()
            linenu= len(example)
        for i in hop:
            workdir = f'{self.hopdir}{i}/'
            os.chdir(workdir)
            logtmppath = f'{workdir}{i}.log_tmp'
            with open(logtmppath, "r", encoding="utf-8") as file2:
                tmp = file2.readlines()
                linenu_tmp = len(tmp)
                # print(f'{self.start_nu+i}: {linenu} {linenu_tmp}\n')
                try:
                    if linenu_tmp == linenu:
                        for j in range(linenu):
                            if example[j].split()[0] == tmp[j].split()[0] and\
                            example[j].split()[1] == tmp[j].split()[1]: 
                                pass
                            else:
                                errorlist.append(f'{i}-{j+1}')
                                errornu.append(int(f'{i}'))
                                break
                    else:
                        errorlist.append(f'{i}-{j+1}')
                        errornu.append(int(f'{i}'))
                except:
                    errorlist.append(f'{i}')
                    errornu.append(int(f'{i}'))
        if errorlist:
            print('!!!The log file indicates that the molecules have changed!!!')
            print(errorlist)
            print(len(errorlist))
            np.savetxt(f'{self.hopdir}errorlist.dat',np.array(errornu))
            cmd=input('Do you want to remove these from hop.npy?(y or n)\n').lower()
            if cmd == 'y' or cmd == 'yes':
                self.del_error_from_hop_npy()
                self.get_info()
        else:
            print('No problem')
        return errorlist
    
    def del_error_from_hop_npy(self):
        if self.s0 != 'yes':
            hop=np.load(self.hop)
        else:
            hop=np.load(f'{self.hopdir}hop_s0.npy')
        errorlist=np.loadtxt(f'{self.hopdir}errorlist.dat')
        for item in errorlist:
            item=np.str_('%d'%item)
            index=np.where(hop==item)
            #index=np.where(hop==item))
            hop=np.delete(hop,index)
        if self.s0 != 'yes':
            np.save(self.hop,hop)
        else:
            np.save(f'{self.hopdir}hop_s0.npy',hop)
            
    def get_hop_points(self):
        self.abstract_coor()
        self.get_gjf()
        self.sub_gaussian()
        errorlist1 = self.testing1()
        if errorlist1:
            os._exit(0)
        self.get_info()
    def input_single(self):    
        print('Enter others to run the full program.')
        print("Enter 'r' to resubmit the gaussian task that just went wrong.")
        print("Enter 't' to recheck the output files of gaussian to determine whether there are |Initial Parameters|'. ")
#        print("Enter 'm' to recheck the output files of gaussian to determine whether the molecules have changed. ")
        print("Enter 'g' to to retrieve coordinate information.")
        print("Enter '1' to run abstract_coor()")
        print("Enter '2' to run get_gjf()")
        print("Enter '3' to run sub_gaussian()")    
        signal=input()
        if signal == 'r':
            errorlist = self.testing1()
            self.re_sub_gaussian_error(errorlist)
            print(errorlist)
        elif signal == 't':
            self.testing1()
    #    elif signal == 'm':
    #        hop_info.testing2()
        elif signal == 'g':
            self.get_info()
        elif signal == '1':
            self.abstract_coor()
#            nohop=np.load(self.nohop)
            hop=np.load(self.hop)
            list_1 = np.load(f'{self.hopdir}errorlist_nohop_step<{self.step}.npy')
            list_2 = np.load(f'{self.hopdir}errorlist_nohop_step={self.step}.npy')
            print(f'nohop and step < {self.step}: \n{list_1}')
            print(f'nohop and step = {self.step}: \n{list_2}')
            print(f'Hop:/t{len(hop)}/t{len(hop)/self.file_nu*100}%')
            print(f'No-hop(step={self.step}):/t{len(list_2)}/t{len(list_2)/self.file_nu*100}%')
            print(f'No-hop(step<{self.step}):/t{len(list_1)}/t{len(list_1)/self.file_nu*100}%')
        elif signal == '2':
            self.get_gjf()
        elif signal == '3':
            self.sub_gaussian()
        else:
            self.get_hop_points()
        
def main():
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    hop_info=get_hop_info(para_all)
    hop_info.input_single()


if __name__ == '__main__':
    main()

    
    
    
