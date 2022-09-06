#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  2 09:57:32 2021

@author: zyf
"""
import os
import shutil
import numpy as np
import multiprocessing
from sub.descriptor_3 import Descriptor
import sub.sub_interface_json as sub_interface_json
import sub.mds_homemade as mds_homemade
from sklearn.manifold import Isomap
import matplotlib.pyplot as plt

class mds_descriptor(Descriptor):
    def __init__(self,para_all):
        super().__init__(para_all)
        self.classical_MDS_switch = para_all['classical_MDS']
        if self.classical_MDS_switch == 'yes':
            self.dim_cla_mds = int(para_all['dimension_of_classical_mds'])
        self.Isomap_switch = para_all['Isomap']
        if self.Isomap_switch == 'yes':
            self.dim_isomap = int(para_all['dimension_of_Isomap'])
            self.n_neighbors = int(para_all['n_neighbors'])
        self.n_pro = int(para_all['n_pro'])
        self.plot_show = para_all['plot_show']
        self.remake_block = para_all['remake_block']
        if self.remake == 'yes':
            if self.remake_block != 'all':
                self.remake_block_list = para_all['remake_block'].split(',')
            else:
                self.remake_block_list = []
                for i in range(self.block_nu):
                    self.remake_block_list.append(i+1)
        else:
           self.remake_block_list = [0]
     
    def Euclidean_distance_single(self,vec1,vec2):
        m_feature = len(vec1)
        dis = 0
        for i in range(m_feature):
            dis += (vec1[i] - vec2[i])**2
        distance = dis**0.5
        return distance
    
    def Euclidean_distance(self, method, item,nu):
        if os.path.exists(f'{self.hopdir}{method}/{item}_{nu}/'):
            shutil.rmtree(f'{self.hopdir}{method}/{item}_{nu}/')
        os.mkdir(f'{self.hopdir}{method}/{item}_{nu}/')
        if item == 'Coulomb_matrix':
            x=np.load(f'{self.coulomb_dir}{item}_{nu}.npy')
        elif item in self.structural_descriptor:
            x=np.load(f'{self.X_matrix}{item}_{nu}.npy')
        else:
            print('Worng descriptor!')
        n_samples = x.shape[0]
        dis_matrix = np.zeros((n_samples,n_samples))
        result = []
        lis = []
#        print(n_samples)
        for i_sample in range(n_samples):
            for j_sample in range(i_sample):
                lis.append([i_sample, j_sample])
        pool = multiprocessing.Pool(processes = self.n_pro)
        for i in range(int(n_samples*(n_samples-1)/2)): 
            result.append(pool.apply_async(self.Euclidean_distance_single, (x[lis[i][0]], x[lis[i][1]],)))
#        print(len(result))
        pool.close()
        pool.join()
        print(f'{method}-{item}:Sub-process(es) done.')
        for i_sample in range(n_samples):
            for j_sample in range(i_sample):
                res = result.pop(0)
                dis_matrix[i_sample][j_sample] = res.get()
                dis_matrix[j_sample][i_sample] = dis_matrix[i_sample][j_sample]
        path_i = f'{self.hopdir}{method}/{item}_{nu}/'
        np.savetxt(f'{path_i}distance_{item}_{nu}.dat',dis_matrix)
        
#    def isomap_pretreat():

    def plot_low_dim(self,x,path_main,item,plot_dir,nu):
        plt.figure()
        plt.title(f'{item}_{nu}')
        plt.scatter(x[:,0],x[:,1])
        plt.scatter(x[:,0],x[:,1])
        plt.savefig(f'{path_main}{item}_{nu}/{item}_{nu}.png')
        if self.plot_show == 'yes':
            plt.show()
        shutil.copyfile(f'{path_main}/{item}_{nu}/{item}_{nu}.png',f'{plot_dir}{item}_{nu}.png')
        
        

    def method_selection(self):
        if self.classical_MDS_switch == 'yes':
            method = 'classical_MDS'
            path_main = f'{self.hopdir}{method}/'
            plot_dir = f'{path_main}plot_all/'
            if not os.path.exists(path_main):
                os.mkdir(path_main)
            else:
                if self.remake == 'yes':
                    for i in range(100):
                        nos = i+1
                        if not os.path.exists(f'{self.hopdir}{method}_{nos}/'):
                            os.rename(path_main, f'{self.hopdir}{method}_{nos}/')
                            os.mkdir(path_main)
                            break
            if os.path.exists(plot_dir):
                shutil.rmtree(plot_dir)    
            os.mkdir(plot_dir)
            if self.structural_descriptor:
                for item in self.structural_descriptor:
                    for nu in self.remake_block_list:
                        self.Euclidean_distance(f'{method}',item,nu)
                        path_i = f'{self.hopdir}{method}/{item}_{nu}/'
                        dis = np.loadtxt(f'{path_i}distance_{item}_{nu}.dat')
                        vectors,values = mds_homemade.cla_mds(dis,self.dim_cla_mds)
                        np.savetxt(f'{path_i}vectors_{item}_{nu}.dat',vectors)
                        np.save(f'{path_i}{item}_low_dim_{nu}.npy',vectors)
                        np.savetxt(f'{path_i}value_{item}_{nu}.dat',values)
                        self.plot_low_dim(vectors,path_main,item,plot_dir,nu)
                    
                    
            if self.Coulomb_matrix == 'yes':
                item = 'Coulomb_matrix'
                for nu in self.remake_block_list:
                    self.Euclidean_distance(f'{method}',item,nu)
                    path_i = f'{path_main}Coulomb_matrix_{nu}/'
                    dis = np.loadtxt(f'{path_i}distance_{item}_{nu}.dat')
                    vectors,values = mds_homemade.cla_mds(dis,self.dim_cla_mds)
                    np.savetxt(f'{path_i}vectors_{item}_{nu}.dat',vectors)
                    np.save(f'{path_i}{item}_low_dim_{nu}.npy',vectors)
                    np.savetxt(f'{path_i}value_{item}_{nu}.dat',values)
                    self.plot_low_dim(vectors,path_main,item,plot_dir,nu)
                

        if self.Isomap_switch == 'yes':
            method = 'Isomap'
            path_main = f'{self.hopdir}{method}/'
            plot_dir = f'{path_main}plot_all/'
            if not os.path.exists(path_main):
                    os.mkdir(path_main)
            else:
                if self.remake == 'yes':
                    for i in range(100):
                        nos = i+1
                        if not os.path.exits(f'{self.hopdir}{method}_{nos}/'):
                            os.rename(path_main, f'{self.hopdir}{method}_{nos}/')
                            os.mkdir(path_main)
                            break
            if os.path.exists(plot_dir):
                shutil.rmtree(plot_dir)    
            os.mkdir(plot_dir)
            if self.structural_descriptor:
                for item in self.structural_descriptor:
                    if os.path.exists(f'{path_main}/{item}/'):
                        shutil.rmtree(f'{path_main}/{item}/')
                    os.mkdir(f'{path_main}/{item}/')
                    for nu in self.remake_block_list:
                        x=np.load(f'{self.X_matrix}{item}_{nu}.npy')
                        embedding = Isomap(n_components=self.dim_isomap, n_neighbors=self.n_neighbors)
                        X_transformed = embedding.fit_transform(x)
                        np.savetxt(f'{path_main}/{item}/{item}_{nu}.dat',X_transformed)
                        self.plot_low_dim(X_transformed, path_main, item,plot_dir,nu)

            
            if self.Coulomb_matrix == 'yes':
                item = 'Coulomb_matrix'
                if os.path.exists(f'{path_main}/{item}/'):
                    shutil.rmtree(f'{path_main}/{item}/')
                os.mkdir(f'{path_main}/{item}/')
                for nu in self.remake_block_list:
                    x=np.load(f'{self.coulomb_dir}{item}_{nu}.npy')
                    embedding = Isomap(n_components=self.dim_isomap, n_neighbors=self.n_neighbors)
                    X_transformed = embedding.fit_transform(x)
                    np.savetxt(f'{path_main}/{item}/{item}_{nu}.dat',X_transformed)
                    self.plot_low_dim(X_transformed,path_main,item,plot_dir,nu)

            
                

def main():
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    mds = mds_descriptor(para_all)
    mds.method_selection()



if __name__ == '__main__':
    main()
