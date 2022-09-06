
import os
import numpy as np
import shutil
import subprocess as sub

def check_single_log(nu,errors):
    with open(f'{nu}/jade.log','r') as f1:
        last_line=f1.readlines()[-1]
        if last_line.split()[-1] != 'DONE':
            try:
                with open(f'{nu}/current_state.out','r') as f4:
                    if f4.readlines()[-1].split()[2] != '1':
                        # print(nu)
                        with open(f'all_log.dat','a') as f2, open(f'{nu}/qsub_run_jade_bagel.sh','r') as f3:
                            for line in f3:
                                if 'nodes=' in line:
                                    node_nu=line.split()[-1].split(':')[0].split('=')[1]
                                    errors.append(nu)
                                    f2.write(f'{nu}\t{node_nu}\t')
                                    f2.write(last_line)
                                    break
            except:
                print(f'no current_state.log:{nu}')
                with open(f'all_log.dat','a') as f2, open(f'{nu}/qsub_run_jade_bagel.sh','r') as f3:
                    for line in f3:
                        if 'nodes=' in line:
                            node_nu=line.split()[-1].split(':')[0].split('=')[1]
                            errors.append(nu)
                            f2.write(f'{nu}\t{node_nu}\t')
                            f2.write('No current_state.log\n')
                            break
    return errors

def check_uncompleted():
    sub.call('jsa>jsa.log',shell=True)
    path1=os.getcwd()
    uncompleted=[]
    with open('jsa.log','r') as f1:
        f1.readline()
        f1.readline()
        for line in f1:
            path_now=line.split()[-1].split(':')[1].split('/')[-3]
            if line.split()[4] == 'R' and path_now == path1.split('/')[-2]:
                uncompleted.append(f"{int(line.split()[-1].split(':')[1].split('/')[-1])}")
    os.remove('jsa.log')
    return uncompleted
    
def get_all_log(nu1,nu2):
    if os.path.exists('all_log.dat'):
        os.remove('all_log.dat')
    list_all=range(nu1,nu2+1)
    list_uncompleted=check_uncompleted()
    running=[]
    errors=[]
    for i in list_all:
        if str(i) not in list_uncompleted:
            errors=check_single_log(i,errors)
        else:
            running.append(i)
    print(f'Complete : {nu2-nu1+1-len(running)-len(errors)}')
    print(f'Running: {len(running)}')
    print(f'ERROR  : {len(errors)}')


def main():
    print('May 20 1-56 May 30 57-98')
    start_nu=int(input('The first job nu:'))
    end_nu=int(input('The last job nu:'))
    get_all_log(start_nu,end_nu)



if __name__ == '__main__':
    main()
