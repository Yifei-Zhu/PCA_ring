#!/data/home/zhuyf/programs/anaconda3/bin/python
import os
import sys
import math
import numpy as np
# import sub_interface_json
import matplotlib.pyplot as plt

class Population():
    def __init__(self):
        self.work_dir = os.getcwd()
        self.status_dir = f'/data/home/zhuyf/job_status/'
        # self.workspace_dir = f'/data/home/zhuyf/all_work/workspace/'
        self.workspace_dir = f'/data/home/zhuyf/cytosine_all/zyf_work/all_completed/original/'
        # self.step = 
        self.n_traj=1000
        
    def get_status(self):
        state_nu = int(input('How many states ? (an int) >>> '))
        step = int(input('How many steps ? (an int) >>> '))
        if not os.path.exists(self.status_dir):
                os.mkdir(self.status_dir)
        else:
            s1 = input(f'The {self.status_dir} already exists. Continue ? (y/n) >>> ').lower()
            if s1 != 'yes' and s1 != 'y':
                sys.exit(1)
    
        restart=input('Restart?(y/n) >>> ').lower()
        
        if restart == 'n' or restart == 'no':
            traj1 = int(input('Enter the number of first traj (an int) >>> '))
            traj2 = int(input('The second (an int) >>> '))
            trajs = list(range(traj1,traj2+1))
            
            # trajs=['2', '3', '7', '13', '20', '23', '26', '27', '28', '30', '36', '45', '48', '53', '56', '62', '63', '64', '65', '69', '71', '75', '77', '83', '85', '91', '95', '99']
            
            # trajs=[ '1', '5', '9', '12', '14', '17', '19', '29', '31', '32', '35', '41', '44', '46', '47', '49', '54', '57', '59', '60', '61', '66', '70', '74', '76', '80', '82', '84', '88', '596', '598']
            
            # trajs= ['4', '6', '8', '16', '21', '33', '34', '37', '38', '42', '50', '51', '55', '58', '73', '86', '89', '92', '94', '97']
            
            # trajs=[ '10', '11', '15', '18', '22', '24', '25', '39', '40', '43', '52', '67', '68', '72', '78', '79', '81', '87', '90', '93', '00']

            nu_traj = len (trajs)
            
            with open(f'{self.status_dir}status.dat','w') as f1:
                f1.write(f'states_nu {state_nu}\tsteps {step}\n')
        
        elif restart == 'y' or restart == 'yes':
            list1 = os.listdir(self.work_dir)
            trajs = []
            for i in list1:
                if i.isdigit():
                     trajs.append(int(i))
            nu_traj = len(trajs)
            
        else:
            sys.exit(1)
        
            
        for i in trajs:
            try:
                with open(f'{i}/hop_all_time.out','r') as f1, open(f'{i}/current_state.out','r') as f2, open(f'{self.status_dir}{i}.dat','a') as f3:
                                        
                    if restart == 'y' or restart == 'yes':
                        f2.readline()
                        for n in range(10):
                            f1.readline()
                    f2.readline()
                    for line in f1:
                        if 'population' in line:
                            for j in range(state_nu):
                                f3.write(f'{line.split()[3+j]}\t')
                            # f2.readline()
                            f2_line=f2.readline()
                            strs=f2_line.split()
                            if strs:
                                # print(strs)
                                f3.write(f'{strs[2]}\n')
                            else:                            
                                f2_line=f2.readline()
                                strs=f2_line.split()
                                f3.write(f'{strs[2]}\n')
            except FileNotFoundError:
                print(f'FileNotFoundError : {i}')
                
        print('\nDone !')
        return 
                
    def job_filter(self):
        with open(f'{self.status_dir}status.dat','r') as fs:
            step = int(fs.readline().split()[3])
        list1 = os.listdir(self.status_dir)
        filter_list, uncompleted = [], []

        # a,b=[],[]
        
        for dat in list1:
            nu = dat.split('.')[0]
            if nu.isdigit():
                filter_list.append(int(nu))
        filter_list.sort()
        
        with open(f'{self.status_dir}status.dat','a') as f1:
            for dat in filter_list:
                with open(f'{self.status_dir}{dat}.dat','r') as f2:
                    f1.write(f'{dat}\t')
                    lines=f2.readlines()
                    nus = len(lines)
                    if nus == step+1:
                        f1.write('completed\n')
                    else:
                        f1.write(f'{nus}\t')
                        if lines:
                            try:
                                if int(lines[-1].split()[-1]) == 1:
                                    f1.write('hop_but_step_not_enough\tcompleted\n')
                                else:
                                    f1.write('uncompleted\n')
                                    uncompleted.append(dat)
                                    # if nus < 2000:
                                    #     a.append(dat)
                                    # else:
                                    #     b.append(dat)
                            except:
                                # print(dat,lines[-1])
                                sys.exit()
                        else:
                            f1.write('uncompleted\n')
                            
        print(f'uncompleted: {len(uncompleted)}')
        # print(len(a),len(b))
        print('\nDone !')
                        # for strs in lines:
                        #     if int(strs.split()[-1]) == 1:
                        #         hop=1
                        #         break
                        #     else:
                        #         hop=0
                        # if hop == 1:
                        #     f1.write('hop_but_step_not_enough\tcompleted\n')
                        # else:
                        #     f1.write('uncompleted\n')

           
        return 

        
    def plot_main(self):
        # with open(f'{self.status_dir}status.dat','r') as fs:
        #    line1 = fs.readline().split()
        #    state_nu = int(line1[1])
        #   step = int(line1[3])

        state_nu=3
        step=3000

        option = input('p - Population or o - Occupation\n')
        
        completed = []
        
        states=[]
        for i in range(state_nu):
            states.append('state'+str(i+1))
        state_all={key:[0]*(step+1) for key in states}
        #####
        state_all2={key:[0]*(step+1) for key in states}
            
        with open(f'{self.status_dir}status.dat','r') as f1:
            for line in f1:
                if line.split()[-1] == 'completed':
                    completed.append(int(line.split()[0]))
                    
        nus=len(completed)

        for i in completed:
            line_nu=-1
            with open(f'{self.status_dir}{i}.dat','r') as f2:
                for line in f2:
                    # print(line)
                    line_nu+=1
                    if line_nu > step:
                        break
                    for st_nu in range(len(state_all)):
                        if option == 'p':
                            state_all[f'state{st_nu+1}'][line_nu] += float(line.split()[st_nu])/nus
                        elif option == 'o':
                            if int(line.split()[-1]) == st_nu+1:
                                state_all[f'state{st_nu+1}'][line_nu] += 1/nus
                                #####
                                state_all2[f'state{st_nu+1}'][line_nu] += float(line.split()[st_nu])/nus

                        
                 
                if line_nu < step:
                    # print(line_nu)
                    for n in range(step-line_nu):
                        line_nu+=1
                        state_all['state1'][line_nu] += 1/nus
                        state_all2['state1'][line_nu] += 1/nus
        
        x_axis=np.linspace(0,step/2,num=step+1)
        
        if option == 'o':
            y_label='Occupation'
        elif option == 'p':
            y_label='Population'
            
##plot each state respectively      
        for i in range(3):        
            plt.figure(i+1)
            plt.title(f'S{i}')
            plt.plot(x_axis,state_all[f'state{i+1}'],label='Occupation')
            plt.plot(x_axis,state_all2[f'state{i+1}'],label='Population',linestyle='--')
           
            plt.legend()
            plt.ylabel('Population/Occupation')
            plt.xlabel('Time (fs)')
            plt.xscale('log')
            plt.savefig(f'{self.status_dir}{i+1}.svg')
        
       # plt.figure(1)
       # for st_nu in range(len(state_all)):
       #     plt.plot(x_axis,state_all[f'state{st_nu+1}'],'r',label=f'S{st_nu}')
       #     # plt.plot(x_axis,state_all2[f'state{st_nu+1}'],'b',label=f'Popolation')
       # plt.legend()
       #  plt.ylabel(f'{y_label}')
       #  plt.xlabel('Time (fs)')
       #  
       #  if step < 1500:
       #      ax=plt.gca()
       #      ax.xaxis.set_major_locator(plt.MultipleLocator(20))
       #  else:
       #      plt.xscale('log')
       # 
       #  # plt.show()
       # #plt.savefig(f'{self.status_dir}population.svg')
       # plt.savefig(f'{self.status_dir}{y_label}.png')
                
    def get_some_hop(self):
        
        # step1=int(input('The begin step :'))
        # step2=int(input('The end step :'))
        # state1=int(input('The initial state :'))
        # state2=int(input('The final state :'))
        step1=60
        step2=120
        state1=2
        state2=3
        
        
        completed = []    
            
        with open(f'{self.status_dir}status.dat','r') as f1:
            for line1 in f1:
                if line1.split()[-1] == 'completed':
                    completed.append(int(line1.split()[0]))
        hop_traj={}      
        for i in completed:
        # for i in [14]:
            step=-1
            with open(f'{self.status_dir}{i}.dat','r') as f2:
                for j in range(step1+1):
                    step+=1
                    line2=f2.readline()
                    if line2.split():
                        st1=int(line2.split()[-1])

                line_nu=0                   
                
                for line in f2:
                    step+=1
                    # print(line)
                    line_nu+=1
                    st2=int(line.split()[-1])
                    # print(st1,st2)
                    if st1 == state1 and st2 == state2:
                        hop_traj.update({i:step-1})

                        break
                    elif line_nu == step2-step1:
                        break
                    st1=st2

        # print(hop_traj)        
        
        if os.path.exists(f'{self.status_dir}stru_{step1}_{step2}_{state1}to{state2}.xyz'):
            os.remove(f'{self.status_dir}stru_{step1}_{step2}_{state1}to{state2}.xyz')
        if  os.path.exists(f'{self.status_dir}not_stru_{step1}_{step2}_{state1}to{state2}.xyz'):
            os.remove(f'{self.status_dir}not_stru_{step1}_{step2}_{state1}to{state2}.xyz')
        
        with open(f'{self.workspace_dir}{int(list(hop_traj.keys())[0])}/traj_time.out','r') as f:
            n_atoms=int(f.readline())
        for traj in hop_traj.keys():
            with open(f'{self.status_dir}stru_{step1}_{step2}_{state1}to{state2}.xyz','a') as f1, \
                open(f'{self.workspace_dir}{traj}/traj_time.out','r') as f2:
                    for m in range(hop_traj[traj]):
                        for n in range(n_atoms+2):
                            f2.readline()
                    for w in range(n_atoms+2):
                        f1.write(f2.readline())
        
        for other in range(self.n_traj):
            if other+1 not in hop_traj.keys():
                with open(f'{self.status_dir}not_stru_{step1}_{step2}_{state1}to{state2}.xyz','a') as f1, \
                    open(f'{self.workspace_dir}{traj}/traj_time.out','r') as f2:
                        for m in range(step1):
                            for n in range(n_atoms+2):
                                f2.readline()
                        # for x in range(step2-step1):
                        for w in range(n_atoms+2):
                            f1.write(f2.readline())

        n_get=len(list(hop_traj.keys()))
        # print((self.n_traj-n_get)*(step2-step1))
        
        res1=0
        with open(f'{self.status_dir}stru_{step1}_{step2}_{state1}to{state2}.xyz','r') as f1:
            for line in f1:
                if 'O' in line:
                    x1=float(line.split()[1]);y1=float(line.split()[2]);z1=float(line.split()[3])
                    c_line=f1.readline()
                    x2=float(c_line.split()[1]);y2=float(c_line.split()[2]);z2=float(c_line.split()[3])
                    res1+=((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)**0.5/n_get
                    # print(((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)**0.5)
        res2=0   
        with open(f'{self.status_dir}not_stru_{step1}_{step2}_{state1}to{state2}.xyz','r') as f2:

            for line in f2:
                if 'O' in line:
                    x1=float(line.split()[1]);y1=float(line.split()[2]);z1=float(line.split()[3])
                    c_line=f2.readline()
                    x2=float(c_line.split()[1]);y2=float(c_line.split()[2]);z2=float(c_line.split()[3])
                    res2+=((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)**0.5/(self.n_traj-n_get)
                    # print(((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)**0.5)
                         
        print(res1,res2)          
                

def main():
    pop = Population()
    s1=int(input('1 - get each_traj_status\n2 - check_job_status\n3 - plot the population\n4 - get some hop points in a certain period of time\n'))
    if s1 == 1:
        pop.get_status()
    elif s1 == 2:
        pop.job_filter()
    elif s1 == 3:
        pop.plot_main()
    elif s1 == 4:
        pop.get_some_hop()
    else:
        pass

if __name__ == '__main__':
    main()


