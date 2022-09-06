import os
import numpy as np
import shutil
import subprocess as sub

def copy_files(list1,node):
    now_path=os.getcwd()
    old1='BAGEL_EXAM'
    old2='dyn.inp'
    old3='qsub_run_jade_bagel.sh'
    for i in list1:
        shutil.copytree(f'files/{old1}', f'{i}/{old1}')
        shutil.copyfile(f'files/{old2}', f'{i}/{old2}')
        shutil.copyfile(f'files/{old3}', f'{i}/{old3}')
        with open(f'{i}/{old3}','r') as file1, open(f'{i}/{old3}.bak','w') as file2:
            for line in file1:
                if 'ppn=2' in line:
                    file2.write(f'#PBS -l nodes=node{node}:ppn=2\n')
                elif 'JADE_NAMD' in line:
                    file2.write(f'#PBS -N jade_{i}_node_{node}\n')
                elif '#PBS -q' in line:
                    if int(node) > 36:
                        file2.write(f'#PBS -q eth\n')
                    else:
                        file2.write(f'#PBS -q opa\n')
                else:
                    file2.write(line)
        os.remove(f'{i}/{old3}')
        os.rename(f'{i}/{old3}.bak', f'{i}/{old3}')

def qsub_run_jade_bagel(list1):
    now_path=os.getcwd()
    for i in list1:
        os.chdir(f'{now_path}/{i}')
        sub.call('qsub qsub_run_jade_bagel.sh',shell='True')
        os.chdir(f'{now_path}')


def main():
    choose=input('1-single job\t2-many jobs\n')
    if choose == '1':
        start_nu = input('Input the job:')
        job_list=[start_nu]
    elif choose == '2':
        start_nu = input('Input the first job:')
        end_nu = input('Input the last job:')
        job_list=range(int(start_nu),int(end_nu)+1)
    else:
        print('ERROR: Unknown choice')
        os.exit(1)
    node= input('Choose node available:')
    copy_files(job_list,node)
    qsub_run_jade_bagel(job_list)

if __name__ == '__main__':
    main()
