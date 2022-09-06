'''
Author: zhuyf
Date: 2022-01-02 20:04:46
LastEditors: zhuyf
LastEditTime: 2022-01-04 15:37:29
Description: file content
FilePath: /jp5_test/Auto_check.py
'''
from sub.JADE_dyn_1 import jade_dyn as JADE
from sub.JADE_dyn_restart import Restart as RESTART
import os
import sys
import time
import math
import shutil
import numpy as np
import subprocess as sub
import sub.sub_interface_json as sub_interface_json

def input_to_json_file (input_file, json_file) :
    xxx = sub_interface_json.read_data_with_label (input_file)
    sub_interface_json.dump_json(json_file, xxx)
def read_from_json (json_file) :
    para_all = sub_interface_json.load_json(json_file)
    return para_all
class check_jade_jobs(JADE):
    def __init__(self,para_all):
        super().__init__(para_all)
        self.auto = para_all['auto'].lower()
        self.limit_end = int(para_all['limit_end'])
        self.step_done_list = f'{self.all_dir}nohop_but_step_done.dat'
        shutil.copyfile(self.step_done_list, f'{self.all_dir}nohop_but_step_done_bak.dat')
        self.total_cores = int(para_all['total_avail_cores'])
        self.limit_job_nu = int(self.total_cores/self.single_task_num)

    def check_cur_jobs(self,para_all):
        sub.call("jsm > jsm.inp",shell = True)
        with open('jsm.inp','r') as file1:
            jobnu = 0
            for line in file1:
                try:
                    if line.split()[3] == 'R':
                        jobnu+=1
                except IndexError:
                    pass
        os.remove('jsm.inp')
        if jobnu < self.limit_job_nu:
            resub_nu = self.limit_job_nu - jobnu
            print('-----------------------------------------')
            print(f'Free : {resub_nu}*{self.single_task_num}')
            print('-----------------------------------------')
            if self.restart == '0':
                self.start_nu,self.end_nu = self.modify_input_inp(jobnu)
                self.file_nu = self.end_nu - self.start_nu + 0
                self.copy_move()
                self.get_infom()
                self.generate_input(para_all,file_nu=resub_nu)
                self.modify_node()
                self.run_qsub(filenu=resub_nu)
            else:
                singal_re = 'yes'
                if singal_re != 'yes':
                    sys.exit(0)
                else:
                    if self.restart == '1':
                        bad_list=np.loadtxt(self.bad_list).tolist()
                    elif self.restart == '2':
                        bad_list=np.loadtxt(self.step_done_list).tolist()
                    need_qsub_list = []
                    try:
                        if resub_nu <= len(bad_list):
                            for i in range(resub_nu):
                                need_qsub_list.append(int(bad_list.pop(0)))
                        else:
                            resub_nu = len(bad_list)
                            for i in range(resub_nu):
                                need_qsub_list.append(int(bad_list.pop(0)))
                        if bad_list == []:
                            print('-----------------------------------------')
                            print('EMPTY!')
                            print('-----------------------------------------')
                        else:
                            if self.restart == '1':
                                np.savetxt(self.bad_list,bad_list)
                            elif self.restart == '2':
                                np.savetxt(self.step_done_list,bad_list)
                    except TypeError:
                        print('-----------------------------------------')
                        print('EMPTY!')
                        print('-----------------------------------------')
                        need_qsub_list.append(int(bad_list))
                    self.get_infom()
                    self.generate_input(para_all,len(need_qsub_list))
                    self.modify_node(bad_list=need_qsub_list)
                    self.qsub_restart_auto(need_qsub_list)
        else:
            print(f'FULL : {jobnu}*{self.single_task_num}/{self.total_cores}')
            sys.exit(0)

    def qsub_restart_auto(self,bad_list):
        for i in bad_list: 
            work_i = f'{self.work_dir}{int(i)}/'   
            command = f'cd {work_i}; qsub qsub_run_molpro_2019_traj.sh'
            sub.call(command,shell = True)
        print(f'QSUB_LIST:\n{bad_list}')

    def modify_input_inp(self,jobnu):
        with open('input.inp','r') as file2, open('input.inp.bak', 'w') as file3:
            for line in file2:
                try:
                    if line.split()[0] == 'start_nu':
                        start_nu = int(line.split()[2])
                        start_new = start_nu+(self.limit_job_nu-jobnu)
                        if start_new > self.limit_end:
                            print('The number of [start_nu] out of range!!')
                            sys.exit(0)
                        strs=line.replace(line.split()[2], str(start_new))
                        file3.write(strs)
                    elif line.split()[0] == 'end_nu':
                        end_nu = int(line.split()[2])
                        end_new = start_new+(self.limit_job_nu-jobnu)-1
                        if end_new > self.limit_end:
                            end_new = self.limit_end
                        strs=line.replace(line.split()[2], str(end_new))
                        file3.write(strs) 
                    else:
                        file3.write(line)                   
                except IndexError:
                    file3.write(line)
                    pass
        os.rename('input.inp.bak','input.inp')
        return start_new, end_new

def main():
        input_file = 'input_auto.inp'
        json_file = 'input_auto.json'
        input_to_json_file (input_file, json_file)
        para_all = read_from_json (json_file)
        CHECK = check_jade_jobs(para_all)
        if CHECK.auto != 'yes':
            print('Please check [auto] in input.inp.')
            sys.exit(0)
        else:
            CHECK.check_cur_jobs(para_all)

if __name__ == '__main__':
    main()
