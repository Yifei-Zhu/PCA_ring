'''
Author: zhuyf
Date: 2021-12-25
LastEditors: zhuyf
LastEditTime: 2022-02-23 16:37:27
Description: file content
FilePath: /jp6_test/sub/JADE_dyn_check_online.py
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
import sub.check_job_info as check_job_info

class check_jade_jobs(JADE):
    def __init__(self,para_all):
        super().__init__(para_all)
        self.auto = para_all['auto'].lower()
        self.limit_end = int(para_all['limit_end'])
        self.step_done_list = f'{self.all_dir}nohop_but_step_done.dat'
        if os.path.exists(self.step_done_list):
            shutil.copyfile(self.step_done_list, f'{self.all_dir}nohop_but_step_done_bak.dat')
        self.total_cores = int(para_all['total_avail_cores'])
        # self.limit_job_nu = int(self.total_cores/self.single_task_num)


    def check_cur_jobs(self,para_all):
        used = check_job_info()
        if used < self.total_cores:
            resub_nu = int((self.total_cores - used)/self.single_task_num)
            if self.restart == '0':
                self.start_nu,self.end_nu = self.modify_input_inp(resub_nu)
                self.file_nu = self.end_nu - self.start_nu + 0
                self.copy_move()
                self.get_infom()
                self.generate_input(para_all,file_nu=resub_nu)
                self.modify_node()
                self.run_qsub(filenu=resub_nu)
            else:
                singal_re = input('At first, you should run [r] [1] to check results and prepare floders of restart.\nEnter \'yes\' to continue:\n').lower()
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
            print(f'FULL : {used}/{self.total_cores}')
            sys.exit(0)

    def qsub_restart_auto(self,bad_list):
        for i in bad_list: 
            work_i = f'{self.work_dir}{int(i)}/'   
            command = f'cd {work_i}; qsub qsub_run_molpro_2019_traj.sh'
            sub.call(command,shell = True)
        print(f'QSUB_LIST:\n{bad_list}')

    def modify_input_inp(self,jobnu):
        with open('input_auto.inp','r') as file2, open('input_auto.inp.bak', 'w') as file3:
            for line in file2:
                try:
                    if line.split()[0] == 'start_nu':
                        start_nu = int(line.split()[2])
                        start_new = start_nu+jobnu
                        if start_new > self.limit_end:
                            print('The number of [start_nu] out of range!!')
                            sys.exit(0)
                        strs=line.replace(line.split()[2], str(start_new))
                        file3.write(strs)
                    elif line.split()[0] == 'end_nu':
                        end_nu = int(line.split()[2])
                        end_new = start_new+jobnu-1
                        if end_new > self.limit_end:
                            end_new = self.limit_end
                        strs=line.replace(line.split()[2], str(end_new))
                        file3.write(strs) 
                    else:
                        file3.write(line)                   
                except IndexError:
                    file3.write(line)
                    pass
        os.rename('input_auto.inp.bak','input_auto.inp')
        return start_new, end_new

def main():
        input_file = 'input_auto.inp'
        json_file = 'input_auto.json'
        para_all = sub_interface_json.input_and_read(input_file, json_file)
        CHECK = check_jade_jobs(para_all)
        if CHECK.auto != 'yes':
            print('Please check [auto] in input.inp.')
            sys.exit(0)
        else:
            CHECK.check_cur_jobs(para_all)

if __name__ == '__main__':
    main()
