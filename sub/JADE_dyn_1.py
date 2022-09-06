'''
Autor: zhuyf
Date: 2021-09-05 09:32:27
LastEditors: zhuyf
LastEditTime: 2022-02-23 16:37:39
Descriptor: 
'''
import os
import sys
import time
import math
import shutil
import subprocess as sub
import sub.sub_interface_json as sub_interface_json

class jade_dyn():
    def __init__(self,para_all):
        self.all_dir = para_all['all_dir']
        self.file_dir = f'{self.all_dir}files/'
        self.work_dir = f'{self.all_dir}workspace/'
        self.optgjf = para_all['optgjf']
        self.opt_dir = f'{self.file_dir}opt/'
        self.cas_dir =f'{self.file_dir}cas/'
        self.jade_patch_dir = para_all['jade_patch_dir']
        self.start_nu = int(para_all['start_nu'])
        self.end_nu = int(para_all['end_nu'])
        self.file_nu = self.end_nu-self.start_nu+1 
        self.single_task_num = int(para_all['single_task_num_cores'])
        self.queue_node_num = int(para_all['queue_node_num'])
        self.input_inp = f'{self.jade_patch_dir}input.inp' 
        self.input_node = f'{self.jade_patch_dir}node.inp'
        self.json_node = f'{self.jade_patch_dir}node.json'
        self.infom_input = f'{self.jade_patch_dir}infom.inp'
        self.cut_off = 4
        self.restart = para_all['restart']
        self.step = int(para_all['step'])
        self.auto = para_all['auto']
        warning = 0
#        if not os.path.exists(self.opt_dir):
#            print(f'No such file or directory: {self.opt_dir}')
#            warning = 1
#        elif not os.path.exists(self.cas_dir):
#            print(f'No such file or directory: {self.cas_dir}')
#            warning = 1
#        elif not os.path.exists(self.file_dir):
#            print(f'No such file or directory: {self.file_dir}')
#            warning = 2
#        if warning == 2:
#            sys.exit(0)
#        elif warning==1:
#            signal1=input('Enter \'yes\' to continue:\n').lower()
#            if  signal1 != 'yes':
#                sys.exit(0)
                
    def opt(self):
        os.chdir(self.opt_dir)
        sub.call(f'rung16 {self.optgjf}',shell = True)
#        while not os.path.exists()      
    #计算cas并且将生成的wfu文件copy到dynamics/MOLPRO_EXAM
    def cas(self):
        os.chdir(self.cas_dir)
        wfu_path = f'{self.cas_dir}wfu'
        if os.path.exists(wfu_path):
            os.remove(wfu_path)
        sub.call('python2 qmolpro.py -q opa -a 16 example.in',shell = True)
        wfu_path = f'{self.cas_dir}wfu'
        wfu_new_dir = f'{self.file_dir}/MOLPRO_EXAM/wfu'
        while not os.path.exists(wfu_path):
            time.sleep(1)
        shutil.copyfile(wfu_path, wfu_new_dir)
    def copy_move(self):
    #将{dyn.inp,MOLPRO_EXAM/,qsub_run_molpro_2019_traj.sh}copy到workspace下每个文件夹中
        old1 = f'{self.file_dir}dyn.inp'
        old2 = f'{self.file_dir}MOLPRO_EXAM'
        old3 = f'{self.file_dir}qsub_run_molpro_2019_traj.sh'
#        files= os.listdir(self.work_dir)
#        for file in files:
        with open(old1,'r') as file1, open(f'{self.file_dir}dyn.inp.bak','w') as file2:
            for line in file1:
                if 'label_restart' in line:
                    line = 'label_restart = 0,\n'
                elif 'ntime =' in line:
                    line = f'ntime = {self.step},\n' 
                file2.write(line)
        os.remove(old1)
        os.rename(f'{self.file_dir}dyn.inp.bak', old1)
        for i in range(self.file_nu):
            new = f'{self.work_dir}{self.start_nu+i}/dyn.inp'
            shutil.copyfile(old1, new)
            new = f'{self.work_dir}{self.start_nu+i}/MOLPRO_EXAM'
            if os.path.exists(new):
                shutil.rmtree(new)
            shutil.copytree(old2, new)
            new = f'{self.work_dir}{self.start_nu+i}/qsub_run_molpro_2019_traj.sh'
            shutil.copyfile(old3, new)
    def get_infom(self):
    #获取空闲节点
        os.chdir(self.jade_patch_dir)
        sub.call("infom > infom.inp",shell = True)
        file = './infom.inp'
        old_str1 = 'job-exclusive'
        old_str2 = 'offline'
        with open(self.infom_input, "r", encoding="utf-8") as file1,\
        open(f'{self.infom_input}.bak', "w", encoding="utf-8") as file2:
            for line in file1:
                if old_str1 not in line and old_str2 not in line:
                    file2.write(line)
        os.remove(self.infom_input)
        os.rename(f'{self.infom_input}.bak', self.infom_input)            
        with open(file, "r", encoding="utf-8") as filei:    
            line_nu=0
            for line in filei:
                line_nu+=1
        with open(file, "r", encoding="utf-8") as file3,\
        open(f'{self.infom_input}.bak', "w", encoding="utf-8") as file4:
            queue_list = ['opa', 'eth']
            queue = 'None'
            for i in range(line_nu):
                line = file3.readline()
                if 'Queue' in line:
                    queue = line.split()[2]
                    if queue in queue_list:
                        file4.write(line)
                else:
                    if queue in queue_list:
                        number = line.split()[1]
                        free_num = int(number.split('/')[0])
                        self.cut_off = 2*self.single_task_num
                        if free_num > self.cut_off:
                            task_num = int((free_num-self.cut_off)/self.single_task_num)
                            line = line.replace(number, str(task_num))
                            file4.write(line)
        os.remove(self.infom_input)
        os.rename(f'{self.infom_input}.bak', self.infom_input)
    def generate_input(self,para_all,file_nu):
    #安排好哪些节点，生成输入文件，若当前节点数目不够就在提前规划好的备用节点下排队
        total_task = 0
        node_num = 0
        with open(self.infom_input, "r", encoding="utf-8") as file1,\
        open(self.input_node, "w+", encoding="utf-8") as file2:
            for line in file1:
                if 'Queue' in line:
                    queue_cur = line.split()[-1]
                else:
                    node_cur = line.split()[0]
                    free_task = int(line.split()[1])
                    total_task += free_task
                    if total_task < file_nu:
                        line1 = 'queue%s = '%node_num + queue_cur + "\n"
                        line2 = 'node%s = '%node_num + node_cur + "\n"
                        line3 = 'run_num%s = '%node_num + str(free_task) + "\n"
                        file2.write(line1)
                        file2.write(line2)
                        file2.write(line3)
                        node_num += 1
                    else:
                        tasknum = file_nu - total_task + free_task
                        line1 = 'queue%s = '%node_num + queue_cur + "\n"
                        line2 = 'node%s = '%node_num + node_cur + "\n"
                        line3 = 'run_num%s = '%node_num + str(tasknum) + "\n"
                        file2.write(line1)
                        file2.write(line2)
                        file2.write(line3)
                        node_num += 1
                        break
            if total_task < file_nu:
                if self.auto != 'yes':
                    print("Insufficient nodes, whether to use spare nodes?\n")
                    signal = input('Please enter NO to stop，others to continue:')
                else:
                    signal = 'NO'
                if signal == 'NO':
                    sys.exit(0)
                else:
                    for i in range(self.queue_node_num):
                        backup_queue_cur = para_all['backup_queue%s'%i]
                        backup_node_cur = para_all['backup_node%s'%i]
                        backup_runnum_cur = int(para_all['backup_run_num%s'%i])
                        total_task += backup_runnum_cur
                        if total_task < file_nu:
                            line1 = 'queue%s = '%node_num + backup_queue_cur + "\n"
                            line2 = 'node%s = '%node_num + backup_node_cur + "\n"
                            line3 = 'run_num%s = '%node_num + str(backup_runnum_cur) + "\n"
                            file2.write(line1)
                            file2.write(line2)
                            file2.write(line3)
                            node_num += 1
                        else:
                            tasknum = file_nu - total_task + backup_runnum_cur
                            line1 = 'queue%s = '%node_num + backup_queue_cur + "\n"
                            line2 = 'node%s = '%node_num + backup_node_cur + "\n"
                            line3 = 'run_num%s = '%node_num + str(backup_runnum_cur) + "\n"
                            file2.write(line1)
                            file2.write(line2)
                            file2.write(line3)
                            node_num += 1
                            break
            line_last = 'node_num = '+str(node_num) + "\n"
            file2.write(line_last)
            os.remove(self.infom_input)
    def alter(self,number,new_str,queue_cur):
    #modify_node()的子函数，修改qsub_run_molpro_2019_traj.sh中队列和节点
#        old_str = "nodes=node93"
#        files= os.listdir(self.work_dir)
#        file = f'{self.work_dir}/{files[number]}/qsub_run_molpro_2019_traj.sh'
        if self.restart == '0':
            filenu = self.start_nu+int(number)
        else:
            filenu = int(number)
        file = f'{self.work_dir}{filenu}/qsub_run_molpro_2019_traj.sh'
        with open(file, "r", encoding="utf-8") as file1,\
        open("%s.bak" % file, "w", encoding="utf-8") as file2:
            for line in file1:
                if 'nodes=' in line:
                    line = f'#PBS -l {new_str}:ppn={self.single_task_num}\n'
#                    line = line.replace(old_str, new_str)
#                    newstr = 'ppn=%s'%self.single_task_num
#                    line = line.replace('ppn=2',newstr)
                elif '#PBS -N' in line:
                    if self.restart == '0':
                        line = f'#PBS -N {filenu}\n' 
                    else:
                        line = f'#PBS -N {filenu}_restart\n'
                elif '-q' in line:
                    queue_old = line.split()[2]
                    line = line.replace(queue_old,queue_cur)
                file2.write(line)
        os.remove(file)
        os.rename(f'{file}.bak', file)
    def modify_node(self, bad_list=[]):
    #借助alter，修改qsub_run_molpro_2019_traj.sh中队列和节点
        input_to_json_file (self.input_node, self.json_node)
        para_all = read_from_json(self.json_node)
        node_num = int(para_all['node_num'])
        number_node = 0
        number_traj = 0
        for i in range(node_num):
            node_cur = para_all['node%s'%i]
            queue_cur = para_all['queue%s'%i]
            run_num = int(para_all['run_num%s'%i])
            # if run_num != 0:
            #     print('node :  ',node_cur)
            for n in range(run_num):
                if self.auto == 'yes':
                    new_str='nodes=1'
                else:
                    new_str = f'nodes={node_cur}'
                if self.restart == '0':
                    nu = number_traj
                    print(f'Changed -traj-{self.start_nu+int(nu)} {n+1}/{run_num}')
                else:
                    nu = int(bad_list[number_traj])
                    while nu < self.start_nu:
                        number_traj += 1
                        nu = int(bad_list[number_traj])
                        print(f'Changed -traj-{int(nu)} {n+1}/{run_num}')
                number_traj += 1
                self.alter(nu,new_str,queue_cur)
                number_node += 1
                if number_traj == self.file_nu:
                    print(f"All -{number_traj}- tasks's node have been changed")
        os.remove(self.json_node)
    def run_qsub(self,*,filenu = None):
    #提交任务
#        files= os.listdir(self.work_dir)
#        for file in files:
        for i in range(filenu):
            path = f'{self.work_dir}{self.start_nu+i}/'
            command = f'cd {path};qsub qsub_run_molpro_2019_traj.sh'
            sub.call(command,shell = True)
                
def main():
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    jade = jade_dyn(para_all)
    if jade.restart != '0':
        print('Check input.inp - restart!')
        sys.exit(0)
    print('This procedure consists of 6 steps:\n',\
          '1 - opt geometery\n',\
          '2 - cas\n',\
          '3 - Copy three file\n',\
          '4 - Use infom to get free nodes\n',\
          '5 - Modify each file\n',\
          '6 - Run qsub\n')
    signal = input('Enter a number to run a specific step，othres to run 1-7:\n')
    if signal == '1':
        jade.opt()
    elif signal == '2':
        jade.cas()
    elif signal == '3':
        jade.copy_move()
    elif signal == '4':
        jade.get_infom()
        jade.generate_input(para_all,file_nu=jade.file_nu)
    elif signal == '5':
        jade.modify_node()
    elif signal == '6':
        jade.run_qsub(filenu= jade.file_nu)

    else:
        jade.cas()
        jade.copy_move()
        jade.get_infom()
        jade.generate_input(para_all,file_nu=jade.file_nu)
        jade.modify_node()
        jade.run_qsub()
        
if __name__ == '__main__':
    main()
