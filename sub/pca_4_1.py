#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  2 15:10:50 2021

@author: zyf
"""
import dufte
import os
import shutil
# from turtle import color
import numpy as np
from matplotlib import ticker as tk
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
import seaborn as sns 
from sklearn.decomposition import PCA
from sub.descriptor_3 import Descriptor
import sub.sub_interface_json as sub_interface_json


class Sklearn_pca(Descriptor):
    def __init__(self, para_all):
        super().__init__(para_all)
        self.PCA_switch = para_all['PCA']
        self.remake_block = para_all['remake_block']
        self.operate_nu = int(para_all['remake_operate_nu'])
        self.main_dim_nu = int(para_all['pca_main_dim_nu'])
        n_components = para_all['pca_n_components']
        if n_components == 'mle':
            self.n_components = n_components
        else:
            self.n_components = int(n_components)
        if self.remake == 'yes':
            self.remake_block_list = para_all['remake_block'].split(',')
        else:
           self.remake_block_list = [0]
        #plot options
        self.list_name=['RCⅠ','RCⅡ','RCⅢ','RCⅣ','RCⅤ']
        self.plot_2D_option = para_all['plot_2D']
        self.plot_3D_option = para_all['plot_3D'].lower()
        self.plot_components_option = para_all['plot_components'].lower()
        self.plot_variance_ratio_option = para_all['plot_variance_ratio'].lower()
        self.font1 = {#'family' : 'Times New Roman',
            'weight' : 'bold',
            'size' : 25,
            }
        self.font2={#'family':'Arial',
            'weight':'normal',
            'size' : 20}
    
    def plot_low_dim(self, x, path_main, item, plot_dir,nu,signal):
        for i in range(self.main_dim_nu):
            for j in range(i):
                # with plt.style.context(dufte.style):
                plt.figure()
                plt.style.use('seaborn-deep')
                # plt.title(f'{item}_{j+1}vs{i+1}')
                
                if self.s0 == 'yes':

                    x_1,y_1,x_2,y_2=[],[],[],[]
                    nus=int(len(x[:,0])/2)
                    for n in range(nus):
                        x_1.append(x[n,0])
                        y_1.append(x[n,1])
                        x_2.append(x[nus+n,0])
                        y_2.append(x[nus+n,1])
                        
                            
                    plt.scatter(x_1,y_1,color ='#FF0000', label='hop-points')
                    plt.scatter(x_2,y_2,color = '#0000FF', label='S0')
                    leg=plt.legend(prop=self.font2,framealpha=0,handletextpad=0.1,borderaxespad=0.2)
                    # leg=plt.legend(prop=self.font2,framealpha=0,handletextpad=0.1,bbox_to_anchor=(0.535,0.8))
                    leg.get_frame().set_linewidth(0.0)
                
                else:
                    plt.scatter(x[:,0],x[:,1],color = '#0000FF',)
                #plt.ylim(-80,120)
                ax = plt.gca()
                if item =='D':
                    ax.xaxis.set_major_locator(MultipleLocator(20))
                    # ax.yaxis.set_major_locator(MultipleLocator(50))
                elif item == 'A':
                    ax.xaxis.set_major_locator(MultipleLocator(10))
                    ax.yaxis.set_major_locator(MultipleLocator(10))
                else:
                    #ax.xaxis.set_major_locator(MultipleLocator(0.1))
                    #ax.yaxis.set_major_locator(MultipleLocator(0.1))
                    pass
                # plt.ylim(-60,90)
                # plt.xlim(-80,100)            
                ax.tick_params(labelsize=20)
                if signal==2:
                    if item == 'R':
                        plt.xlabel('R(9,10)',self.font1)
                        plt.ylabel('R(1,6)',self.font1)
                    elif item == 'D':
                        plt.xlabel('D(6,1,5,3)',self.font1)
                        plt.ylabel('D(6,1,4,10)',self.font1)
                else:
                    plt.xlabel(self.list_name[j],self.font1)
                    plt.ylabel(self.list_name[i],self.font1)


                # plt.grid()
                plt.savefig(f'{path_main}{item}/{item}_{nu}_{j+1}vs{i+1}.svg',format='svg',dpi=600,bbox_inches='tight')
                shutil.copyfile(f'{path_main}{item}/{item}_{nu}_{j+1}vs{i+1}.svg',f'{plot_dir}{item}_{nu}_{j+1}vs{i+1}.svg')
                if self.plot_2D_option == '2':
                    plt.show()
                plt.close()

    #Decorator
    def plot_show_option(name=None):
        def func_first(func):
            def func_in(self, path_main, item, plot_dir,nu,):
                func(self, path_main, item, plot_dir,nu)
                plt.savefig(f'{path_main}/{item}/{item}_{name}.svg',format='svg',dpi=600,bbox_inches='tight')
                shutil.copyfile(f'{path_main}/{item}/{item}_{name}.svg',f'{plot_dir}{item}_{name}.svg')
                option = self.__dict__[f'plot_{name}_option']
                if  option == '2':
                    plt.show()
                plt.close()
            return func_in
        return func_first
        # if _func is None:
        #     return func_first
        # else:
        #     return func_first(_func)
    
    @plot_show_option(name='3D')
    def plot_3D(self, path_main, item, plot_dir,nu):
        datafile = f'{path_main}{item}/{item}_low_dim_{nu}.dat'
        x=np.loadtxt(datafile)
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(x[:, 0], x[:, 1], x[:, 2])
        ax.set_xlabel(self.list_name[0])
        ax.set_ylabel(self.list_name[1])
        ax.set_zlabel(self.list_name[2])
        
    
    @plot_show_option(name='components')
    def plot_components(self,path_main, item, plot_dir, nu):
        datafile = f'{path_main}{item}/{item}_components_{nu}.dat'
        x=np.loadtxt(datafile)
        if item != 'Coulomb_matrix':
            hop_example=np.load(self.hop)[0]
            label_list=[]
            with open(f'{self.hopdir}{hop_example}/{item[-1]}/{item}.dat','r') as file:
                for line in file:
                    # if item == 'D' and len(self.remove_list)!= 0:
                    if item in self.structural_descriptor:
                        list1 = line.split()[1].strip(item).lstrip('(').rstrip(')').split(',')
                        if len(self.remove_list)!= 0:
                            if not set(self.remove_list)&set(list1):
                                label_list.append(line.split()[1])
                        elif len(self.keep_list)!= 0:
                            if set(self.keep_list)&set(list1):
                                label_list.append(line.split()[1])
                        else:
                            label_list.append(line.split()[1])
                    # else:
                    #     label_list.append(line.split()[1])
        # plt.imshow(1-abs(x.T),cmap=plt.cm.gray,aspect='auto')
        # plt.gca().xaxis.set_major_locator(MultipleLocator(1))
        # plt.gca().yaxis.set_major_locator(MultipleLocator(1))
        ax1=sns.heatmap(abs(x.T),cmap=plt.cm.Greys,xticklabels=list(range(1,x.T.shape[1]+1,1)),yticklabels=label_list)
        ax1.set_yticklabels(label_list,rotation='horizontal')
        ax1.set_ylabel('Features',self.font1) 
        ax1.set_xlabel('Dimensions',self.font1)
        plt.tick_params(labelsize=12)
        plt.subplots_adjust(left=0.2)
        # plt.title(f'Components (Dimensions-{x.shape[0]} Features-{x.shape[1]})')
        # plt.text(0,0.9,f'asdasdasdasdasdasd=11111',weight="bold",fontsize=15,transform=plt.gca().transAxes)

    
    @plot_show_option(name='variance_ratio')
    def plot_variance_ratio(self,path_main, item, plot_dir, nu):
 
        datafile = f'{path_main}{item}/{item}_variance_ratio_{nu}.dat'
        x=np.loadtxt(datafile)

    # with plt.style.context(dufte.style):
        var_plt = plt.figure()
        plt.plot(x)
        plt.ylabel('Variance Ratio',self.font1)
        plt.xlabel('Dimensions',self.font1)
        plt.ylim(0,1)
        plt.xticks(np.arange(len(x)), np.arange(1, len(x)+1))
        ax = plt.gca()
        # ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.yaxis.set_major_locator(MultipleLocator(0.2))
        ax.yaxis.set_major_formatter(tk.PercentFormatter(xmax=1,decimals=0))
        ax.tick_params(labelsize=15)
        
    
    def plot_all_option(self, x,path_main, item, plot_dir,nu,signal):
        if self.plot_2D_option != '0':
            self.plot_low_dim(x, path_main, item, plot_dir, nu,signal)
        if signal == 1:
            if self.plot_3D_option != '0' :
                self.plot_3D(path_main, item, plot_dir, nu)
            if self.plot_components_option != '0' and item != 'Coulomb_matrix':
                self.plot_components(path_main, item, plot_dir, nu)
            if self.plot_variance_ratio_option != '0' and item != 'Coulomb_matrix':
                self.plot_variance_ratio(path_main, item, plot_dir, nu)

    def pca_X(self, para_all):
        if self.PCA_switch == 'yes':
            path_main = f'{self.hopdir}PCA/'
            plot_dir = f'{path_main}plot_all/'
            if not os.path.exists(path_main):
                os.mkdir(path_main)
            else:
                if self.remake == 'yes':
                    for i in range(10000):
                        nos = i+1
                        if not os.path.exists(f'{self.hopdir}PCA_old_{nos}/'):
                            os.rename(path_main, f'{self.hopdir}PCA_old_{nos}/')
                            break
                    os.mkdir(path_main)
            if os.path.exists(plot_dir):
                shutil.rmtree(plot_dir)
            os.mkdir(plot_dir)
            if self.Coulomb_matrix == 'yes':
                item = 'Coulomb_matrix'
                coulomb_pca_dir = f'{path_main}{item}/'
                if os.path.exists(coulomb_pca_dir):
                    shutil.rmtree(coulomb_pca_dir)
                os.mkdir(coulomb_pca_dir)
                for nu in self.remake_block_list:
                    x = np.load(f'{self.coulomb_dir}{item}_{nu}.npy')
                    pca = PCA(n_components=self.n_components)
                    x_new = pca.fit_transform(x)
                    np.save(f'{coulomb_pca_dir}{item}_low_dim_{nu}.npy', x_new)
                    np.savetxt(f'{coulomb_pca_dir}{item}_low_dim_{nu}.dat',x_new)
                    np.savetxt(f'{coulomb_pca_dir}variance_ratio_{nu}.dat', pca.explained_variance_ratio_)
                    np.savetxt(f'{coulomb_pca_dir}variance_{nu}.dat', pca.explained_variance_)
                    np.savetxt(f'{coulomb_pca_dir}components_{nu}.dat', pca.components_)
                    if self.remake_after_block == 'yes':
                        print(f'!!!Re-perform PCA to NO.{nu} block!!!')
                        # list_all = np.load(self.block_info, allow_pickle=True)
                    elif self.remake_after_cluster == 'yes':
                        print(f'!!!Re-perform PCA to NO.{nu} cluster!!!')
                        # list_all = np.load(self.cluster_info, allow_pickle=True)
                    else:
                        print(f'Perform PCA to all hop-points')
                        # list_all=np.load(f'{self.hopdor}hop.npy',allow_pickle=True)
                    print(f'descriptor: Coulomb_matrix')
                    print(f'number of samples: {pca.n_samples_}')
                    print(f'number of features: {pca.n_features_}\n')
                    self.plot_all_option(x_new, path_main, item, plot_dir,nu,1)

            if self.structural_descriptor:
                for item in self.structural_descriptor:
                    stru_pca_dir = f'{path_main}{item}/'
                    if os.path.exists(stru_pca_dir):
                        shutil.rmtree(stru_pca_dir)
                    os.mkdir(stru_pca_dir)
                    for nu in self.remake_block_list:
                        try:
                            # aaaaa
                            x = np.load(f'{self.X_matrix}{item}_{nu}.npy')
                            pca = PCA(n_components=self.n_components)
                            x_new = pca.fit_transform(x)
                            np.save(f'{stru_pca_dir}{item}_low_dim_{nu}.npy', x_new)
                            np.savetxt(f'{stru_pca_dir}{item}_low_dim_{nu}.dat',x_new)
                            np.savetxt(f'{stru_pca_dir}{item}_variance_ratio_{nu}.dat', pca.explained_variance_ratio_)
                            np.savetxt(f'{stru_pca_dir}{item}_variance_{nu}.dat', pca.explained_variance_)
                            np.savetxt(f'{stru_pca_dir}{item}_components_{nu}.dat', pca.components_)

                            # print(pca.components_.shape)
                            if self.remake_after_block == 'yes':
                                print(f'!!!Re-perform PCA to NO.{nu} block!!!')
                                # list_all = np.load(self.block_info, allow_pickle=True)[self.operate_nu ]
                            elif self.remake_after_cluster == 'yes':
                                print(f'!!!Re-perform PCA to NO.{nu} cluster!!!')
                                # list_all = np.load(self.cluster_info, allow_pickle=True)
                            else:
                                print(f'Perform PCA to all hop-points')
                                # list_all=np.load(f'{self.hopdor}hop.npy',allow_pickle=True)   
                            print(f'descriptor: {item}')
                            print(f'number of samples: {pca.n_samples_}')
                            print(f'number of features: {pca.n_features_}\n')
                            signal=1
                        except:
                            x_new=self.get_two_dim(item,stru_pca_dir)
                            signal=2 
                            
                        finally:
                            self.main_plot_population(item,stru_pca_dir,signal)
                            self.plot_all_option(x_new, path_main, item, plot_dir,nu,signal)
                            
        else:
            print('Are you sure you want to use this method? Please check input.inp')
            os._exit(0)
            
    def main_plot_population(self,item,paths,signal):
        path_main = f'{self.hopdir}PCA/'
        plot_dir = f'{path_main}plot_all/'
        main_dim = 1
        main_key_nu = 3
        
        if signal==1:
            hop_example=np.load(self.hop)[0]
            keys_aka,keys_name = [],[]
            with open(f'{self.hopdir}{hop_example}/{item[-1]}/{item}.dat','r') as file:
                for line in file:
                    list1 = line.split()[1].strip(item).lstrip('(').rstrip(')').split(',')
                    if len(self.remove_list)!= 0:
                        if not set(self.remove_list)&set(list1):
                            keys_name.append(line.split()[1])
                    elif len(self.keep_list)!= 0:
                        if set(self.keep_list)&set(list1):
                            keys_name.append(line.split()[1])
                    else:
                        keys_name.append(line.split()[1])     
            key_nu=len(keys_aka)
            if self.remake != 'yes':
                self.operate_nu=0
            components=np.loadtxt(f'{paths}{item}_components_{self.operate_nu}.dat')[main_dim-1]
            abs_components=list(map(abs,components))
            nus=list(reversed(np.argsort(abs_components)))
            keys_name_main=[]
            
            for i_nu in range(main_key_nu):
                keys_name_main.append(keys_name[nus[i_nu]])
                
        else:
            if item == 'R':
                keys_name_main = ['R(9,10)','R(1,6)']
            elif item == 'D':
                keys_name_main = ['D(6,1,5,3)','D(6,1,4,10)']

        
        x= np.load(f'{path_main}{item}/{item}_low_dim_{self.operate_nu}.npy')
        xx=np.argsort(x[:,main_dim-1])
        if self.remake == 'yes':
            list_old= np.loadtxt(f'{self.descriptor_dir}list_all_{self.operate_nu}.dat')
        else:
            list_old=self.hoplist
        if signal == 1:
            list_all=[]
            for i in xx:
                list_all.append(list_old[i])
        else:
            list_all = list_old

        total_nu=int(len(list_all))
        matrix_for_one_cluster = np.zeros((total_nu,int(len(keys_name_main))))
        
        column_nu = -1
        for key in keys_name_main:
            column_nu += 1
            line_nu=-1
            for nu in list_all:
                line_nu += 1
                path2 = f'{self.hopdir}{int(nu)}/{item[-1]}/{item}.dat'
                with open(path2,'r', encoding="utf-8") as file2:
                    for line in file2:
                        # if line.split()[0] in keys_aka and line.split()[1] in main_key:
                        if line.split()[1] == key:
                            matrix_for_one_cluster[line_nu,column_nu]=float(line.split()[2])
                            # matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))


        plt.figure()
        plt.style.use('seaborn-bright')
        if signal == 1:
            for member in enumerate(keys_name_main):
                # print(member)
                # plt.plot(sorted(x[:,0]),matrix_for_one_cluster[:,member[0]],label=member[1],color='r' if member[0]==0 else 'b' if member[0]==1 else 'lime')
                plt.plot(sorted(x[:,0]),abs(matrix_for_one_cluster[:,member[0]]),label=member[1],color='r' if member[0]==0 else 'b' if member[0]==1 else 'lime')
            plt.xlabel(self.list_name[main_dim-1],self.font1)
        else:
            x_ax=np.arange(1,1+len(matrix_for_one_cluster[:,0]),1)
            plt.scatter(x_ax,matrix_for_one_cluster[:,0],color = 'r',label=keys_name_main[0])
            plt.scatter(x_ax,matrix_for_one_cluster[:,1],color = 'b',label=keys_name_main[1])
            plt.xlabel('Samples',self.font1)

        if item == 'D':
            plt.ylabel('Dihedral Angle',self.font1)
            ax = plt.gca()
            ax.xaxis.set_major_locator(MultipleLocator(100))
            # ax.yaxis.set_major_locator(MultipleLocator(50))
            # plt.ylim(-190,290)
            # plt.xlim(-80,100)            
        elif item == 'A':
            plt.ylabel('Angle',self.font1)
            ax = plt.gca()
            ax.xaxis.set_major_locator(MultipleLocator(10))
            ax.yaxis.set_major_locator(MultipleLocator(10))
            # plt.ylim(100,150)
            # plt.xlim(-80,100)            
        elif item == 'R':
            plt.ylabel('Bond length',self.font1)
            ax = plt.gca()
            if signal == 1:
                ax.xaxis.set_major_locator(MultipleLocator(0.2))
            else:
                ax.xaxis.set_major_locator(MultipleLocator(100))
                plt.ylim(1.05,1.79)
                # plt.yticks([1.1,1,2,1.3,1.4,1.5,1.6,1.7],['',1.1,'',1.3,'',1.5,'',1.7])
            # ax.yaxis.set_major_locator(MultipleLocator(0.2))
            # plt.ylim(-60,90)
            # plt.xlim(-80,100)            
            ax.tick_params(labelsize=20)
            
        leg=plt.legend(loc=1,prop=self.font2,framealpha=0,handletextpad=0.1,borderaxespad=0.1)
        leg.get_frame().set_linewidth(0.0)
        plt.savefig(f'{path_main}/{item}/{item}_population.svg',format='svg',dpi=600,bbox_inches='tight')
        shutil.copyfile(f'{path_main}/{item}/{item}_population.svg',f'{plot_dir}{item}_population.svg')
        plt.close()
        
    
    def get_two_dim(self,item,paths):
        fig = plt.figure()
        plt.style.use('seaborn-bright')    
        plt.subplot(121)
        list_old= np.loadtxt(f'{self.descriptor_dir}list_all_{self.operate_nu}.dat')
        x_16_1,y_910_1,x_16_2,y_910_2=[],[],[],[]
        x_all,y_all=[],[]
        for nu in list_old:
            path2 = f'{self.hopdir}{int(nu)}/{item[-1]}/{item}.dat'
            with open(path2,'r') as file1:
                for line in file1:
                    if line.split()[1] == 'R(9,10)' or line.split()[1] == 'D(6,1,5,3)':
                        if int(nu) > 10000:
                            x_16_2.append(float(line.split()[2]))
                        else:
                            x_16_1.append(float(line.split()[2]))
                        x_all.append(float(line.split()[2]))
                    elif  line.split()[1] == 'R(1,6)' or line.split()[1] == 'D(6,1,4,10)':
                        if int(nu) > 10000:
                            y_910_2.append(float(line.split()[2]))
                        else:
                            y_910_1.append(float(line.split()[2]))
                        y_all.append(float(line.split()[2]))
                        
        all_xy=np.zeros((len(y_all),2))
        for i in range(len(y_all)):
            all_xy[i,0] = x_all[i]
            all_xy[i,1] = y_all[i]
        np.save(f'{paths}{item}_low_dim_{self.operate_nu}.npy',all_xy)
        return all_xy


def main():
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    sklearn_pca = Sklearn_pca(para_all)
    sklearn_pca.pca_X(para_all)
    print('\nDONE !\n')

if __name__ == '__main__':
    main()
