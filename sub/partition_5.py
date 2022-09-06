#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 23:30:43 2021

@author: zyf
"""
import os
import shutil
import numpy as np
import sys
import matplotlib.pyplot as plt
from sub.descriptor_3 import Descriptor
import sub.sub_interface_json as sub_interface_json

class Regions(Descriptor):
    def __init__(self,para_all):
        super().__init__(para_all)
        self.partition_descriptor = para_all['partition_descriptor']
        self.partition_method = para_all['partition_method']
        self.nu_block=int(para_all['nu_block'])
        self.path_main = f'{self.hopdir}block_{self.partition_method}/'
        self.first_dim = int(para_all['first_dim'])-1
        self.second_dim = int(para_all['second_dim'])-1
        if self.remake != 'yes':
           self.remake_block_nu = 0
        else:
            try:
                self.remake_block_nu = int(para_all['remake_operate_nu'])
            except ValueError:
                print('Remake but the parameter [remake_block_nu] in input.inp is not specified！')
                sys.exit(0)
            
    def all_regions(self,para_all):
        if not os.path.exists(self.path_main):
            os.mkdir(self.path_main)
        else:
            if self.remake == 'yes':
                for i in range(100):
                    nos =i+1
                    try:
                        if not os.path.exists(f'{self.hopdir}block_{self.partition_method}_old_{nos}/'):
                            self.old_path=f'{self.hopdir}block_{self.partition_method}_old_{nos}/'
                            os.rename(self.path_main, self.old_path)
                            os.mkdir(self.path_main)
                            break
                    except:
                        pass
        os.chdir(self.path_main)
        if self.partition_descriptor == 'Coulomb_matrix':
            item = 'Coulomb_matrix'
            x_new = np.load(f'{self.hopdir}{self.partition_method}/{item}/{item}_low_dim_{self.remake_block_nu}.npy')
            self.partition(x_new,para_all,self.path_main,item)
        if self.structural_descriptor:
            for item in self.structural_descriptor:
                if self.partition_descriptor == item:
                    x_new = np.load(f'{self.hopdir}{self.partition_method}/{item}/{item}_low_dim_{self.remake_block_nu}.npy')
                    self.partition(x_new,para_all,item)
                                   
    def partition(self,x_new,para_all,element):
        path=f'{self.path_main}{element}/'
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        os.chdir(path)
        keys = []
        for i in range(self.nu_block):
            keys.append(i+1)
        nu_list = dict([(k, []) for k in keys])
        for i in range(len(x_new)):
            for j in range(self.nu_block):
                xmin=int(para_all[f'xmin{j+1}'])
                xmax=int(para_all[f'xmax{j+1}'])
                ymin=int(para_all[f'ymin{j+1}'])
                ymax=int(para_all[f'ymax{j+1}'])
                if xmin< x_new[i][self.first_dim]< xmax and ymin< x_new[i][self.second_dim]< ymax:
                    if self.remake != 'yes':
                        nu_list[j+1].append(self.hoplist[i])
                    else:
                        if self.remake_after_block == 'yes':
                            hoplist_remake=np.load(f'{self.old_path}{element}/block_info_{self.partition_method}.npy',allow_pickle=True).item().get(self.remake_block_nu)
                        elif self.remake_after_cluster == 'yes':
                            # for m in range(100):
                            #     if not os.path.exists(f'{self.hopdir}cluster_old_{m+1}'):
                            #         self.old_cluster_dir = f'{self.hopdir}cluster_old_{m+1}/'
                            #         break
                            hoplist_remake=np.load(f'{self.cluster_dir}cluster_list.npy',allow_pickle=True).item().get(self.remake_block_nu)
                        nu_list[j+1].append(hoplist_remake[i])
#        np.save(f'{path}block_info.npy',nu_list)
        number_list = []
        for k in keys:
            nus = len(nu_list[k])
            number_list.append(nus)
            print(f'BLOCK_{k}:  {nus}')
            if not nu_list[k]:
                print(f'Partition {k} is empty!!!!')
                os._exit(0)
        np.save(f'{path}block_info_{self.partition_method}.npy',nu_list)
        with open(f'{path}block_info_{self.partition_method}.dat', "w", encoding="utf-8") as file:
            for item in nu_list.items():
                file.write(str(item))
                file.write(' \n')
            file.write(' \n\n')
            for i in range(len(keys)):
                ymax=int(para_all[f'ymax{i+1}'])
                ymin=int(para_all[f'ymin{i+1}'])
                xmax=int(para_all[f'xmax{i+1}'])
                xmin=int(para_all[f'xmin{i+1}'])
                file.write(f'block_{keys[i]}:  {number_list[i]}\t x=[{xmin}:{xmax}]  y=[{ymin}:{ymax}]\n\n')
        for i in range(self.nu_block):
            block_i=f'{path}{i+1}_block'
            if os.path.exists(block_i):
                shutil.rmtree(block_i)
            os.mkdir(block_i)
            for item in nu_list[i+1]:
                shutil.copyfile(f'{self.hopdir}{item}/{item}.gjf',f'{block_i}/{item}.gjf')
                if element != 'Coulomb_matrix':
                    shutil.copyfile(f'{self.hopdir}{item}/{element[-1]}/{element}.dat',f'{block_i}/{item}_{element}.dat')
                with open(f'{self.hopdir}{item}/{item}.xyz','r', encoding="utf-8") as file1,\
                open(f'{path}geom_{i+1}.xyz','a', encoding="utf-8") as file2:
                    file2.write(str(self.natom))
                    file2.write(' \n\n')
                    for line in file1:
                        file2.write(line)
        if element != 'Coulomb_matrix':
            self.average_info(nu_list)
            self.average_analysis()
            self.plot_X_population(nu_list)
            
    def average_info(self,nu_list):
#        nu_list = np.load(f'{self.path_main}{element}/block_info.npy')
        example = int(self.hoplist[0])
        path1 = f'{self.hopdir}{example}/{self.partition_descriptor[-1]}/{self.partition_descriptor}.dat'
        with open(path1,'r', encoding="utf-8") as file1:
                    keys = []
                    for line in file1:
                        keys.append(line.split()[0])
        for i in range(self.nu_block):
            totalnu=float(len(nu_list[i+1])) 
            list_i = dict([(k, [0]) for k in keys])
            for nu in nu_list[i+1]:
                path2 = f'{self.hopdir}{nu}/{self.partition_descriptor[-1]}/{self.partition_descriptor}.dat'
                path3 = f'{self.path_main}{self.partition_descriptor}/{i+1}_block/'
                with open(path2,'r', encoding="utf-8") as file2:
                    for line in file2:
                        list_i[line.split()[0]][0] = float(list_i[line.split()[0]][0])+float(line.split()[2])/totalnu
            with open(path1,'r', encoding="utf-8") as file3,\
            open(f'{path3}average_{i+1}.dat','w', encoding="utf-8") as file4:
                for line in file3:
                    strs = f'{line.split()[0]}\t{line.split()[1]}\t{list_i[line.split()[0]]}\n'
                    file4.write(strs)

    def average_analysis(self):
        for i in range(self.nu_block):
            path1 = f'{self.path_main}{self.partition_descriptor}/{i+1}_block/average_{i+1}.dat'
            for j in range(i):
                path2 = f'{self.path_main}{self.partition_descriptor}/{j+1}_block/average_{j+1}.dat'
                path3 = f'{self.path_main}{self.partition_descriptor}/{j+1}_vs_{i+1}_{self.partition_descriptor}.dat' 
                with open(path1, 'r', encoding="utf-8") as file1,\
                    open(path2, 'r', encoding="utf-8") as file2,\
                    open(path3, 'w', encoding="utf-8") as file3:
                        file3.write(f'{self.partition_descriptor}\t\t\t{j+1}_block\t\t{i+1}_block\n')
                        line1=file1.readlines()
                        line2=file2.readlines()
                        for line_nu in range(len(line1)):
                            res1 = float(line1[line_nu].split()[2].lstrip('[').rstrip(']'))
                            res2 = float(line2[line_nu].split()[2].lstrip('[').rstrip(']'))
                            res = format(abs(res1-res2),'.2f')
                            res1 = format(res1,'.4f')
                            res2 = format(res2,'.4f')
                            if float(res) >= 180:
                                res_new = format(360-float(res),'.2f')
                                file3.write(f'{line1[line_nu].split()[0]}\t{line1[line_nu].split()[1]}\t{res2}\t\t{res1}\t\t{res_new}\t{res}\n')
                            else:
                                file3.write(f'{line1[line_nu].split()[0]}\t{line1[line_nu].split()[1]}\t{res2}\t\t{res1}\t\t{res}\n')

    def plot_X_population(self,nu_list):
        example = int(self.hoplist[0])
        path1 = f'{self.hopdir}{example}/{self.partition_descriptor[-1]}/{self.partition_descriptor}.dat'
        with open(path1,'r', encoding="utf-8") as file1:
            keys_aka,keys_name = [],[]
            for line in file1:
                keys_aka.append(line.split()[0])
                keys_name.append(line.split()[1])
        key_nu=len(keys_aka)
        for i in range(self.nu_block):
            path3 = f'{self.path_main}{self.partition_descriptor}/{i+1}_block/'
            key_average=[]
            with open(f'{path3}average_{i+1}.dat','r', encoding="utf-8") as file2:
                for line in file2:
                    key_average.append(abs(float(line.split()[2].replace('[','').replace(']', ''))))
            totalnu=int(len(nu_list[i+1]))
            matrix_for_one_block = np.zeros((totalnu,key_nu))
            line_nu=-1
            for nu in nu_list[i+1]:
                line_nu += 1
                path2 = f'{self.hopdir}{nu}/{self.partition_descriptor[-1]}/{self.partition_descriptor}.dat'
                with open(path2,'r', encoding="utf-8") as file2:
                    column_nu = -1
                    for line in file2:
                        column_nu += 1
                        matrix_for_one_block[line_nu,column_nu]=abs(float(line.split()[2]))               
            s_result = []
            x = [i+1 for i in range(totalnu)]
            for member in enumerate(keys_name):
                s = 0
                for i in range(totalnu):
                   s += (matrix_for_one_block[i,member[0]] - key_average[member[0]])**2
                standard_deviation = (s/totalnu)**0.5
                s_result.append(standard_deviation)
                plt.figure()
                # matrix_for_one_block[:,member[0]].sort()
                plt.title(f'{member[1]}-distribution')
                #plt.plot(x,matrix_for_one_block[:,member[0]])
                plt.scatter(x,matrix_for_one_block[:,member[0]])
                ax = plt.gca()
                ax.yaxis.set_major_locator(plt.MultipleLocator(10))
                plt.ylim(-10,180)
                plt.xlabel('Sample')
                plt.ylabel('Dihedral Angel')
                # plt.title('Dihedral Angle Distribution')
                plt.text(0,0.9,f's={standard_deviation}',weight="bold",fontsize=10,transform=plt.gca().transAxes)
                plt.savefig(f'{path3}{keys_aka[member[0]]}_{member[1]}.png')
                plt.close()
            sub_nu = 0
            fig_nu = 1
            fig = plt.figure(fig_nu,figsize=(12,8))
            for member in enumerate(keys_name):
                s=s_result[member[0]]
                if sub_nu <= 3:
                    sub_nu += 1
                    plt.subplot(2,2,sub_nu)
                    plt.text(0,0.9,f's={s}',weight="bold",fontsize=15,transform=plt.gca().transAxes)
                    plt.title(f'{member[1]}-distribution')
                    plt.scatter(x,matrix_for_one_block[:,member[0]])
                    ax = plt.gca()
                    ax.yaxis.set_major_locator(plt.MultipleLocator(10))
                    plt.ylim(-10,180)
                    plt.tick_params(labelsize=6)
                else:
                    fig.savefig(f'{path3}{fig_nu}_all_population.png')
                    plt.close()
                    sub_nu =0
                    fig_nu += 1
                    fig = plt.figure(fig_nu,figsize=(12,8))
                    sub_nu += 1
                    plt.subplot(2,2,sub_nu)
                    plt.title(f'{member[1]}-distribution')
                    plt.scatter(x,matrix_for_one_block[:,member[0]])
                    plt.text(0,0.9,f's={s}',weight="bold",fontsize=15,transform=plt.gca().transAxes)
                    ax = plt.gca()
                    ax.yaxis.set_major_locator(plt.MultipleLocator(10))
                    plt.ylim(-10,180)
                    plt.tick_params(labelsize=6)
            fig.savefig(f'{path3}{fig_nu}_all_population.png')
            plt.close()                 
                
def main():
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    region = Regions(para_all)
    region.all_regions(para_all)
    print('\nDone !\n')

if __name__ == '__main__':
    main()
