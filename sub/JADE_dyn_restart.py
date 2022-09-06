'''
Autor: zhuyf
Date: 2021-11-22 10:20:09
LastEditors: zhuyf
LastEditTime: 2022-02-23 16:38:07
Descriptor: 
'''
import os
import sys
import numpy as np
import shutil
import subprocess as sub
from sub.JADE_dyn_1 import jade_dyn
import sub.sub_interface_json as sub_interface_json

class Restart(jade_dyn):
    def __init__(self,para_all):
        super().__init__(para_all)
        self.old_workspace_dir = f'{self.all_dir}old_workspace/'
        self.all_completed_list = f'{self.all_dir}all_completed.npy'
        self.bad_list = f'{self.all_dir}nohop_and_step_not_enough.dat'
        self.step_done_list = f'{self.all_dir}nohop_but_step_done.dat'
        self.final_dir = f'{self.old_workspace_dir}workspace/'
        # with open(f'{self.file_dir}dyn.inp','r') as file:
        #     for line in file:
        #         if 'ntime =' in line:
        #             self.target_step = int(line.split()[-1].replace(',',''))
        self.completed_step_file = f'{self.all_dir}completed_step.npy'
           
    def check_complete(self,old_n):
        if os.path.exists(self.all_completed_list):
            completed = np.load(self.all_completed_list,allow_pickle=True).tolist()
        else:
            completed = []
        bad_list, step_done = [],[]
        for i in range(self.file_nu):
            check_nu = f'{self.start_nu + i}'
            check_file = f'{old_n}{check_nu}/current_state.out'
            try:
                with open(check_file,'r', encoding="utf-8") as file1:
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
                            completed.append(int(check_nu))
                            break
                    if state != '1':
                        if linenu == self.step:
                            completed.append(int(check_nu))
                            step_done.append(int(check_nu))
                        else:
                            bad_list.append(int(check_nu))
            except FileNotFoundError:
                # bad_list.append(int(check_nu))
                pass
        print(f'Completed: {len(completed)}\n{completed}')
        print(f'Nohop and step < {self.step}: {len(bad_list)} \n{bad_list}')
        print(f'Nohop but step = {self.step}: {len(step_done)} \n{step_done}')
        np.save(self.all_completed_list, list(set(completed)))
        np.savetxt(self.bad_list, bad_list,fmt="%i")
        np.savetxt(self.step_done_list, step_done,fmt="%i")
        
    def final_workspace(self,old_n):
        completed = np.load(self.all_completed_list).tolist()
        if len(completed)==0:
            print("There are no finished tasks !!!!!!!")
        else:
            if not os.path.exists(self.final_dir):
                os.makedirs(self.final_dir)
            for i in range(self.file_nu):
                nu = int(f'{self.start_nu+i}')
                if nu in completed:
                    final_i = f'{old_n}{nu}/'
                    shutil.move(final_i,self.final_dir)
                    
    def modify_dyn_step(self, nu, last_step_dict, dyn_dir): 
        check_file= f'{dyn_dir}current_state.out'
        with open(check_file,'r', encoding="utf-8") as file1:  
            last_line = file1.readlines()[-1]
            completed_step_cur = last_line.split()[0]
            last_step = last_step_dict.get('nu',0)
            completed_step_now = int(completed_step_cur) + int(last_step)
            couple = {nu:completed_step_now}
            last_step_dict.update(couple)
        os.remove(check_file)
        with open(f'{dyn_dir}dyn.inp', 'r', encoding="utf-8") as file2,\
            open(f'{dyn_dir}dyn.inp_tmp', 'w', encoding="utf-8") as file3:
            for line in file2:
                if 'ntime =' in line:
                    ntime_new = self.step - completed_step_now
                    str_line = f'ntime = {ntime_new},\n'
                    file3.write(str_line)
                else:
                    file3.write(line)
        os.remove(f'{dyn_dir}dyn.inp')
        os.rename(f'{dyn_dir}dyn.inp_tmp', f'{dyn_dir}dyn.inp') 
                
    def prepare_restart(self,old_n):
        dyninp_path = f'{self.file_dir}dyn.inp'
        with open(dyninp_path,'r') as file1,\
        open(f'{self.file_dir}dyn_restart.inp','w') as file_dyn:
            for line in file1:
                if 'label_restart' in line:
                    line = 'label_restart = 1,\n'
                elif 'ntime =' in line:
                    line = f'ntime = {self.step},\n' 
                file_dyn.write(line)  
        try:
            if os.path.splitext(sys.argv[1])[-1] == '.npy':
                uncompleted = np.load(sys.argv[1], allow_pickle=True).tolist()
            elif os.path.splitext(sys.argv[1])[-1] == '.dat':
                uncompleted = np.loadtxt(sys.argv[1])
            self.restart = '2'
        except IndexError:
            if self.restart == '2':
                uncompleted = np.loadtxt(self.step_done_list).tolist()
            else:
                uncompleted = np.loadtxt(self.bad_list).tolist()
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
        os.makedirs(self.work_dir)
        if os.path.exists(self.completed_step_file):
            last_step_dict = np.load(self.completed_step_file,allow_pickle=True).item()
        else:
            last_step_dict = dict() 
        for i in range(self.file_nu):
            number = f'{self.start_nu+i}'
            if int(number) in uncompleted:          
                #jobid_cur = self.jobid_start + int(i/self.last_jobnupernode)
                old_i = f'{old_n}{number}/'           
                work_i = f'{self.work_dir}{number}/'
                os.makedirs(work_i)
                restart_file_1 = f'{self.file_dir}dyn_restart.inp'
                restart_file_2 = f'{self.file_dir}qsub_run_molpro_2019_traj.sh'
                restart_file_3 = f'{old_i}restart_all'
                restart_file_4 = f'{old_i}vel_xyz.in'                
                restart_file_5 = f'{old_i}stru_xyz.in'                
                restart_file_6 = f'{old_i}MOLPRO_EXAM'
                restart_file_7 = f'{old_i}current_state.out'
                shutil.copyfile(restart_file_1, f'{work_i}dyn.inp')
                shutil.copyfile(restart_file_2, f'{work_i}qsub_run_molpro_2019_traj.sh')
                shutil.copyfile(restart_file_3, f'{work_i}restart_all')
                shutil.copyfile(restart_file_4, f'{work_i}vel_xyz.in')
                shutil.copyfile(restart_file_5, f'{work_i}stru_xyz.in')
                shutil.copytree(restart_file_6, f'{work_i}MOLPRO_EXAM')
                shutil.copyfile(restart_file_7, f'{work_i}current_state.out')               
                self.modify_dyn_step(int(number), last_step_dict, work_i)
        np.save(self.completed_step_file, last_step_dict)
        
    def qsub_restart(self):
        try:
            if os.path.splitext(sys.argv[1])[-1] == '.npy':
                need_qsub = np.load(sys.argv[1], allow_pickle=True).tolist()
            elif os.path.splitext(sys.argv[1])[-1] == '.dat':
                need_qsub = np.loadtxt(sys.argv[1])
        except IndexError:
            if self.restart == '2':
                need_qsub = np.loadtxt(self.step_done_list).tolist()
            else:
                need_qsub = np.loadtxt(self.bad_list).tolist()
        finally:
            qsub_list = []
        for i in range(self.file_nu):
            number = f'{self.start_nu+i}'
            if int(number) in need_qsub: 
                work_i = f'{self.work_dir}{int(number)}/'   
                qsub_list.append(int(number))
                command = f'cd {work_i}; qsub qsub_run_molpro_2019_traj.sh'
                sub.call(command,shell = True)
        print(f'QSUB_LIST:\n{qsub_list}')
        
    def finally_move(self):
        if not os.path.exists(self.old_workspace_dir):
            os.mkdir(self.old_workspace_dir)
        for i in range(50):
            n = i+1
            old_n = f'{self.old_workspace_dir}old_{n}/'
            if not os.path.exists(old_n):
                break
        shutil.move(f'{self.work_dir}', f'{old_n}')    
        list_file = os.listdir(f'{old_n}') 
        print(list_file)
        os.chmod(old_n) 
        for nu in list_file:
            final_i = f'{nu}/'
            shutil.copytree(f'{nu}/',self.final_dir)
            
    def main_check_and_prepare(self):
        if not os.path.exists(self.old_workspace_dir):
            os.makedirs(self.old_workspace_dir)
        for i in range(50):
            n = i+1
            old_n = f'{self.old_workspace_dir}old_{n}'
            if not os.path.exists(old_n):
                old_n = f'{self.old_workspace_dir}old_{n-1}/'
                break
        signal1 = input('1_check_complete;\n2_final_workspace;\n3_prepare_restart;\n')
        if signal1 == '1':
            if self.restart == '2':
                print('[check_complete] is not required for jobs that do not jump but have enough steps to restart!!!')
                sys.exit(0)
            shutil.move(f'{self.work_dir}', f'{old_n}')
            self.check_complete(old_n)
        elif signal1 == '2':
            self.final_workspace(old_n)
        elif signal1 == '3':
            self.prepare_restart(old_n)
            
def main():
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    restart = Restart(para_all)
    if restart.restart == '0':
        print('Check input.inp - restart!')
        sys.exit(0)
    singal = input('\n1 - check_complete and prepare restart\n'+\
                   '2 - qsub_restart\n'+\
                   '3 - finally_move_after_all_completed\n')
    if singal == '1':
        restart.main_check_and_prepare()
    elif singal == '2':
        restart.get_infom()
        if restart.restart == '1':
            bad_list=np.loadtxt(restart.bad_list)
        elif restart.restart == '2':
            bad_list=np.loadtxt(restart.step_done_list)
        file_nu=len(bad_list)
        if restart.file_nu < file_nu:
            file_nu = restart.file_nu
        restart.generate_input(para_all,file_nu)
        restart.modify_node(bad_list=bad_list)
        restart.qsub_restart()
    elif singal == '3':
        restart.finally_move()
   
if __name__ == '__main__':
    main()
    
    