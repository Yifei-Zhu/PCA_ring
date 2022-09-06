#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 09:54:32 2021

@author: zyf
"""
from audioop import add
import os
import shutil
import numpy as np
import linecache

from sklearn import cluster
from sub.get_hop_points_2 import get_hop_info
import sub.sub_interface_json as sub_interface_json

class Descriptor(get_hop_info):
    def __init__(self,para_all):
        super().__init__(para_all)
        self.descriptor_dir = f'{self.hopdir}descriptor/'
        self.X_matrix = f'{self.descriptor_dir}X_matrix/'
        self.coulomb_dir = f'{self.descriptor_dir}Coulomb_matrix/'
        if self.s0 != 'yes':
            self.hoplist = np.load(self.hop)
        else:
            self.hoplist = np.load(f'{self.hopdir}hop_s0.npy')
        self.remake_after_block = para_all['remake_after_block'].lower()
        self.remake_after_cluster = para_all['remake_after_cluster'].lower()
        
        if self.remake_after_block == 'yes' and self.remake_after_cluster == 'yes':
            print('At least one of [remake_after_block] and [remake_after_cluster] is [No]!!!')
            os._exit()
        elif self.remake_after_cluster != 'yes' and self.remake_after_block != 'yes':
            self.remake = 'no'
        else:
            self.remake = 'yes'

        if self.remake == 'yes' :
            # self.block_nu = int(para_all['nu_block'])
            self.remake_block=para_all['remake_block'].split(',')
            self.partition_method = para_all['partition_method']
            self.partition_descriptor = para_all['partition_descriptor']
            self.block_info = f'{self.hopdir}block_{self.partition_method}/{self.partition_descriptor}/block_info_{self.partition_method}.npy'
        
            self.cluster_dir=f'{self.hopdir}cluster/'
            self.cluster_info = f'{self.cluster_dir}cluster_list.npy'
        
        
        self.Coulomb_matrix = para_all['Coulomb_matrix']
        structural_list = para_all['structural_descriptor'].lower().split(',')
        #D - Dihedral_angle; B - Bond_length; A - Angle; H is to indicate whether it contains H atoms.
        self.structural_dict={
            'd':'D', 'hd':'H_D', 'a':'A', 'ha':'H_A', 'r':'R', 'hr':'H_R'
        }
        
        self.structural_descriptor = []
        for i in structural_list:
            self.structural_descriptor.append(self.structural_dict[i])

        # self.operate_descriptor=['D', 'A', 'R', 'H_D', 'H_A', 'H_R']
        self.remove_list,self.keep_list = [],[]
        
        if para_all['remove_list'].lower() != 'none':
            self.remove_list = para_all['remove_list'].split(',')
        if para_all['keep_list'].lower() != 'none':
            self.keep_list = para_all['keep_list'].split(',')
        if self.remove_list and self.keep_list:
            print('At least one of the two [remove_list] & [keep_list] is None')
            os._exit(0)
        self.s0 = para_all['S0_involve'].lower()

    def get_coulomb_matrix(self,list_i,nu):
        coulomb_matrix = np.zeros((len(list_i),self.natom*self.natom))
        sample_nu =-1
        for i in range(len(list_i)):
            sample_nu += 1
            path= f'{self.hopdir}{list_i[i]}/{list_i[i]}.xyz'
            charge=[0]*self.natom
            distance=np.zeros((self.natom, self.natom))
            for i in range(self.natom):
                lines = linecache.getlines(path)
                atom = lines[i][0]
                if atom == 'C':
                    charge[i]=6
                elif atom == 'O':
                    charge[i]=8
                elif atom == 'N':
                    charge[i]=7
                elif atom == 'H':
                    charge[i]=1
                else:
                    print(f'The number of electrons of {atom} is un-available')
                    os._exit(0)
            
            for i in range(self.natom):
                for j in range(self.natom):
                    if i == j:
                        coulomb_matrix[sample_nu][i*self.natom+j] = 0.5*charge[i]**2.4
                    else:
                        xi = float(lines[i].split()[1])
                        yi = float(lines[i].split()[2])
                        zi = float(lines[i].split()[3])
                        xj = float(lines[j].split()[1])
                        yj = float(lines[j].split()[2])
                        zj = float(lines[j].split()[3])
                        distance[i][j]=((xi-xj)**2+(yi-yj)**2+(zi-zj)**2)**0.5
                        coulomb_matrix[sample_nu][i*self.natom+j] = charge[i]*charge[j]/distance[i][j]

        np.save(f'{self.coulomb_dir}Coulomb_matrix_{nu}.npy',coulomb_matrix)


    def get_matrix_X(self,list_i,nu):

        for element in self.structural_descriptor:
            filename = element[-1]
            example = f'{self.hopdir}{list_i[0]}/{filename}/{element}.dat'
            with open(example, "r", encoding="utf-8") as file1:
                num = len(file1.readlines())       
            if len(self.remove_list) != 0:
                with open(example, "r", encoding="utf-8") as file2:
                    for line in file2:
                        list1 = line.split()[1].strip(element).lstrip('(').rstrip(')').split(',')
                        # if self.O_atom in list1:
                        if list(set(self.remove_list) & set(list1)):
                            # num_remove=len(list(set(self.remove_list) & set(list1)))
                            num-=1
            # elif element[-1] in self.operate_descriptor and len(self.keep_list) != 0:
            elif len(self.keep_list) != 0:
                with open(example, "r", encoding="utf-8") as file2:
                    for line in file2:
                        list1 = line.split()[1].strip(element).lstrip('(').rstrip(')').split(',')
                        # if self.O_atom in list1:
                        if not list(set(self.keep_list) & set(list1)):
                            # num_keep=len(list(set(self.keep_list) & set(list1)))
                            num-=1
            
            X = np.zeros((len(list_i), num))
            # X_remove=np.zeros((len(list_i), num_remove))
            for i in range(len(list_i)):
                workdir = f'{self.hopdir}{list_i[i]}/{filename}'
                # print(workdir)
                os.chdir(workdir)
                with open(f'{element}.dat', "r", encoding="utf-8") as file3:
                    line_nu = 0
                    for line in file3:
                        if self.s0 == 'yes' and self.keep_list and  filename == 'D':
                            a = abs(float(line.split()[2]))
                            # a = line.split()[2]
                        else:
                            # a = abs(float(line.split()[2]))
                            a = line.split()[2]

                        
                        list1 = line.split()[1].strip(element).lstrip('(').rstrip(')').split(',')
                        if len(self.remove_list) != 0: 
                            if not list(set(self.remove_list) & set(list1)):
                                X[i][line_nu] = a
                                line_nu += 1
                        elif len(self.keep_list) != 0:
                            if list(set(self.keep_list) & set(list1)):
                                X[i][line_nu] = a
                                line_nu += 1
                        else:
                            X[i][line_nu] = a
                            line_nu += 1

            np.save(f'{self.X_matrix}{element}_{nu}.npy',X)
            print(f'{element} : {np.shape(X)}')

    
    def main_control(self):
        if self.structural_descriptor:
            if os.path.exists(self.X_matrix):
                shutil.rmtree(self.X_matrix)
            os.mkdir(self.X_matrix)
            os.chdir(self.X_matrix)
            if self.remake != 'yes':
                self.get_matrix_X(self.hoplist, 0)
            else:
                if self.remake_after_block == 'yes':
                    for i in self.remake_block:
                        add_1=input('Add corresponding S0 ? (yes/no)\n')
                        if add_1 == 'yes':
                            list_a = np.load(self.block_info, allow_pickle=True).item()[int(i)]
                            list_i = []
                            for nus in list_a:
                                if int(nus) < 10000:
                                    list_i.append(int(nus))
                            for nus in list_a:
                                list_i.append(int(nus)+10000)
                            if not os.path.exists(f'{self.block_info}_old'):
                                os.rename(self.block_info,f'{self.block_info}_old')
                                np.save(self.block_info,list_i)
                            else:
                                print('NO!')
                                os.exit(0)
                        else:
                            list_i = np.load(self.block_info, allow_pickle=True).item()[int(i)]
                        print(list_i)
                        np.savetxt(f'{self.descriptor_dir}list_all_{i}.dat',list_i,fmt='%s')
                        self.get_matrix_X(list_i, int(i))
                elif self.remake_after_cluster == 'yes':
                    for i in self.remake_block:
                        if self.s0=='yes':
                            add_2=input('Add corresponding S0 ? (yes/no)\n')
                        else:
                            add_2='no'
                        if add_2 == 'yes':
                            try:
                                list_a = np.load(self.cluster_info, allow_pickle=True).item()[int(i)]
                            except:
                                list_a = np.load(f'{self.cluster_dir}cluster_list_old.npy', allow_pickle=True).item()[int(i)]
                            
                            list_i = []
                            for nus in list_a:
                                if int(nus) < 10000:
                                    list_i.append(int(nus))
                            for nus in list_a:
                                list_i.append(int(nus)+10000)
                            if not os.path.exists(f'{self.cluster_dir}cluster_list_old.npy'):
                                os.rename(self.cluster_info,f'{self.cluster_dir}cluster_list_old.npy')
                                np.save(self.cluster_info,list_i)
                            # else:
                            #     print('NO!')
                            #     sys.exit(0)

                        else:
                            list_i=[]
                            list_old = np.load(self.cluster_info, allow_pickle=True).item()[int(i)]
                            for nn in list_old:    
                                list_i.append(str(nn))

                        np.savetxt(f'{self.descriptor_dir}list_all_{i}.dat',list_i,fmt='%s')
                        self.get_matrix_X(list_i, int(i))
                    
        if self.Coulomb_matrix == 'yes':
            if os.path.exists(self.coulomb_dir):
                shutil.rmtree(self.coulomb_dir)
            os.mkdir(self.coulomb_dir)
            os.chdir(self.coulomb_dir)  
            if self.remake != 'yes':
                self.get_coulomb_matrix(self.hoplist, 0)
            else:
                if self.remake_after_block == 'yes':
                    for i in self.remake_block:
                        list_i = np.load(self.block_info, allow_pickle=True).item()[int(i)]
                        self.get_coulomb_matrix(list_i, int(i))
                elif self.remake_after_cluster == 'yes':
                    for i in self.remake_block:
                        list_i = np.load(self.cluster_info, allow_pickle=True).item()[int(i)]
                        self.get_coulomb_matrix(list_i, int(i))
        # if self.s0 == 'yes':
        #     self.add_s0()
        

def main():
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    descriptor = Descriptor(para_all)
    if not os.path.exists(descriptor.descriptor_dir):
        os.mkdir(descriptor.descriptor_dir)
    else:
        if descriptor.remake == 'yes':
            for i in range(100):
                nos = i+1
                if not os.path.exists(f'{descriptor.hopdir}descriptor_old_{nos}/'):
                    os.rename(descriptor.descriptor_dir,f'{descriptor.hopdir}descriptor_old_{nos}/')
                    os.mkdir(descriptor.descriptor_dir)
                    break
    descriptor.main_control()
    print('\nDONE !\n')



if __name__ == '__main__':
    main()
