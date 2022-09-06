'''
Author: zhuyf
Date: 2022-02-23 16:25:28
LastEditors: error: git config user.name && git config user.email & please set dead value or install git
LastEditTime: 2022-05-30 21:56:18
Description: file content
FilePath: /jp6_test/sub/cluster_all.py
'''
import os
import shutil
# from this import d
import numpy as np
import sys
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import shape
from sklearn.neighbors import kneighbors_graph
from sklearn.cluster import DBSCAN, KMeans, MiniBatchKMeans, SpectralClustering, Birch
from sklearn.cluster import AffinityPropagation, AgglomerativeClustering, MeanShift
from sub.descriptor_3 import Descriptor
import sub.sub_interface_json as sub_interface_json
import subprocess as sub

class Cluster_all(Descriptor):
    def __init__(self,para_all):
        super().__init__(para_all)
        
        method_dict={
            'db':'DBSCAN', 'op':'OPTICS', 'km':'Kmeans', 'mb':'MiniBatchKmeans', 
            'ms':'MeansShift', 'ap':'AffinityPropagation', 'hi':'HierarchicalClustering',
            'bi':'BIRCH'
                     }
        self.method_abb = para_all['cluster_method']
        self.cluster_method=method_dict[self.method_abb]
        
        self.descriptor=para_all['partition_descriptor']
        self.reduction_method=para_all['partition_method']
        self.first_dim = int(para_all['first_dim'])-1
        self.second_dim = int(para_all['second_dim'])-1
        self.main_path = f'{self.hopdir}{self.reduction_method}/{self.descriptor}/'
        self.cluster_dir=f'{self.hopdir}cluster/'
        self.list_name=['RCⅠ','RCⅡ','RCⅢ','RCⅣ','RCⅤ']
        if not os.path.exists(self.cluster_dir):
            os.mkdir(self.cluster_dir)
        else:
            for i in range(100):
                if not os.path.exists(f'{self.hopdir}cluster_old_{i+1}'):
                    shutil.move(self.cluster_dir,f'{self.hopdir}cluster_old_{i+1}')
                    os.mkdir(self.cluster_dir)
                    self.old_cluster_dir = f'{self.hopdir}cluster_old_{i+1}/'
                    break

            
        if self.remake != 'yes':
               self.remake_block_nu = 0
        else:
            try:
                self.remake_block_nu = int(para_all['remake_operate_nu'])
            except ValueError:
                print('Remake but the parameter [remake_block_nu] in input.inp is not specified！')
                sys.exit(0)


    #DBSCAN
    def dbscan(self,X,eps1,min1):
        db=DBSCAN(eps=eps1, min_samples=min1).fit(X)
        # print(db.core_sample_indices_)
        return db
    
    #OPTICS
    def optics(self,X,eps1,min1):
        op = OPTICS(max_eps=eps1, min_samples=min1).fit(X)
        return op
    
    #K-Means
    def kmeans(self,X,n_clusters):
        km=KMeans(n_clusters=3, random_state=0).fit(X)
        centers=km.cluster_centers_
        np.savetxt(f'{self.cluster_dir}cluster_centers.dat',centers)
        return km

    #MiniBatchKmeans
    def minbatch(self,X,n_clu):
        mb=MiniBatchKMeans(n_clusters=n_clu,random_state=0, batch_size=6,max_iter=10).fit(X)
        centers=mb.cluster_centers_
        np.savetxt(f'{self.cluster_dir}cluster_centers.dat',centers)
        return mb
    
    #MeanShift
    def meanshift(self,X,bw):
        ms= MeanShift(bandwidth=bw,cluster_all=False).fit(X)
        centers=ms.cluster_centers_
        np.savetxt(f'{self.cluster_dir}cluster_centers.dat',centers)
        return ms
    
    #AffinityPropagation
    def affinitypropagation(self,X):
        ap=AffinityPropagation(damping=0.5,preference=None,random_state=0).fit(X)
        print(ap.preference)
        centers=ap.cluster_centers_
        center_index=ap.cluster_centers_indices_
        np.savetxt(f'{self.cluster_dir}cluster_centers.dat',centers)
        np.savetxt(f'{self.cluster_dir}center_index.dat',center_index)
        return ap
    
    #SpectralClustering
    def spectralcluster(self,X,n_clu,para1):
        sp=SpectralClustering(n_clusters=n_clu,assign_labels='discretize',gamma=para1,random_state=0).fit(X)
        return sp
    
    #BIRCH
    def birch(self,X,th,bf,n_clu):
        bi=Birch(threshold=th,branching_factor=bf,n_clusters=n_clu).fit(X)
        centers=bi.subcluster_centers_
        center_index=bi.subcluster_labels_
        np.savetxt(f'{self.cluster_dir}centers.dat',centers)
        np.savetxt(f'{self.cluster_dir}center_index.dat',center_index)
        return bi
    
    #HierarchicalClustering
    def agglomerative(self,X,th):
        # A = kneighbors_graph(X, 2, mode='connectivity', include_self=True)
        # hi=AgglomerativeClustering(n_clusters=None,distance_threshold=th,connectivity=A).fit(X)
        hi=AgglomerativeClustering(n_clusters=None,distance_threshold=th).fit(X)
        # hi=AgglomerativeClustering(n_clusters=2).fit(X)
        return hi
    
    def method_choose(self,s1):
        if s1 == 1:
            low_dim_file = f'{self.main_path}{self.descriptor}_low_dim_{self.remake_block_nu}.npy'
        # 1 - Perform clustering after PCA
        # 2 - Perfrom clustering without PCA since there are only two dimensions
        # 3 - final_plot.py only want to get the plot of clustering results without PCA 
        else:
            low_dim_file = f'{self.hopdir}final_plot/two_dim.npy'
        
        X = np.load(low_dim_file)
 
        if self.method_abb == 'db':
            # for i in np.arange(1,20,0.1):
            #     for j in range(1,10):
            #         cluster_obj=self.dbscan(X,i,j)
            #         labels = cluster_obj.labels_
            #         n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
            #         labels = cluster_obj.labels_

            #         noise_nu = 0
            #         for m in labels:
            #             if m == -1:
            #                 noise_nu +=1
            #         if n_clusters_ == 2 and noise_nu<20:
            #             print(i,j)    
            print('DBSCAN method needs two parameters (eps and min_samples):\n')
            eps1=float(input('eps=\n'))
            min1=int(input('mi_samples=\n'))
            cluster_obj=self.dbscan(X,eps1,min1)
        elif self.method_abb == 'op':
            print('OPTICS method needs two parameters (max_eps and min_samples):\n')
            eps1=float(input('max_eps=\n'))
            min1=int(input('mi_samples=\n'))
            cluster_obj = self.optics(X,eps1,min1)
        elif self.method_abb == 'km':
            n_clu=int(input('The K-Means requires the input of n_clusters:'))
            cluster_obj=self.kmeans(X,n_clu)
        elif self.method_abb == 'mb':
            n_clu=int(input('The MiniBatchKmeans requires the input of n_clusters:'))
            cluster_obj = self.minbatch(X,n_clu)
        elif self.method_abb == 'ap':
            cluster_obj=self.affinitypropagation(X)
        elif self.method_abb == 'ms':
            bw=float(input('The MeanShift requires the input of bandwidth:'))
            cluster_obj=self.meanshift(X,bw)
        elif self.method_abb == 'sp':
            print('SpectralCluster method needs two parameters (n_clusters and gamma):\n')
            n_clu=int(input('n_clusters = \n'))
            para1=float(input('gamma = \n'))
            cluster_obj=self.spectralcluster(X,n_clu,para1)
        elif self.method_abb == 'bi':
            print('BIRCH method needs 3 parameters (threshold, branching_factor and n_clusters):\n')
            th=float(input('threshold(default=0.5) =\n'))
            bf=int(input('branching_factor(default=50) = \n'))
            n_clu=input(input('n_clusters(int or None):\n'))
            if not n_clu.isdigit():
                n_clu = None
            else:
                n_clu=int(n_clu)
            cluster_obj = self.birch(X,th,bf,n_clu)
        elif self.method_abb == 'hi':
            th=float(input('The Hierarchical Clustering requires the input of distance_threshold:\n'))
            cluster_obj = self.agglomerative(X,th)

            # cluster_nu=[]
            # indeies=[]
            # for i in range(0,600):
                # cluster_obj = self.agglomerative(X,i)
                # labels = cluster_obj.labels_
                # n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
            #     cluster_nu.append(n_clusters_)
            #     indeies.append(i)
            # plt.plot(indeies,cluster_nu)
            # plt.ylim(0,20)
        self.cluster_analysis(self.cluster_method,cluster_obj,X,s1)

    def cluster_analysis(self,cluster_method,cluster_obj,X,s1):
        core_samples_mask = np.zeros_like(cluster_obj.labels_, dtype=bool)
        for i in range(shape(cluster_obj.labels_)[0]):
            if cluster_obj.labels_[i] != -1:
                core_samples_mask[i] = True
        labels = cluster_obj.labels_

        noise_nu = 0
        for i in labels:
            if i == -1:
                noise_nu +=1
        print(f'The number of noise points is {noise_nu}!\n')
        # np.savetxt(f'{self.cluster_dir}{cluster_method}_label.dat', labels)
    
        # Number of clusters in labels, ignoring noise if present.
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        print(f'Estimated number of clusters: {n_clusters_}')

        
        # Black removed and is used for noise instead.
        unique_labels = set(labels)
                             
        # colors = plt.cm.Spectral(np.linspace(0, 2, len(unique_labels)))
        colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
        # colors=['#B22222','#00BFFF','#B8860B']
        fig, ax = plt.subplots()
        for k, col in zip(unique_labels, colors):
            if k == -1:
                # Black used for noise.
                col = 'k'
                
            class_member_mask = (labels == k)
            xy = X[class_member_mask & core_samples_mask]
            plt.plot(xy[:,self.first_dim], xy[:,self.second_dim], 'o', markerfacecolor=col,
                        markeredgecolor='k', markersize=10,label='outliers' if k == -1 else f'cluster A\'{k+1}')
            
            #plt.ylim(-80,120)
            
            xy = X[class_member_mask & ~core_samples_mask]
            plt.plot(xy[:, self.first_dim], xy[:, self.second_dim], 'o', markerfacecolor=col,
                        markeredgecolor='k', markersize=1)
            font1 = {#'family' : 'Times New Roman',
                'weight' : 'bold',
                'size' : 15,
                }
            font2={#'family':'Arial',
                'weight':'normal',
                'size':15,
                }
            if s1 == 1:
                plt.xlabel(self.list_name[0],font1)
                plt.ylabel(self.list_name[1],font1)
            else:
                plt.xlabel('D(6,1,5,3)',font1)
                plt.ylabel('D(6,1,4,10)',font1)
            plt.tick_params(labelsize=12)

            ax = plt.gca()
            ax.xaxis.set_major_locator(plt.MultipleLocator(50))
            ax.yaxis.set_major_locator(plt.MultipleLocator(50))
            leg=plt.legend(loc=9,prop=font2, scatterpoints=1,markerscale=1,scatteryoffsets=[0.5],framealpha=0,handletextpad=0.1)
            leg.get_frame().set_linewidth(0.0)
            
        ax.spines['top'].set_linewidth(3)
        ax.spines['bottom'].set_linewidth(3)
        ax.spines['right'].set_linewidth(3)
        ax.spines['left'].set_linewidth(3)
        if s1 == 3:
            fig.savefig(f'{self.hopdir}final_plot/{cluster_method}_{n_clusters_}.svg',format='svg',dpi=600,bbox_inches='tight')
        else:
            fig.savefig(f'{self.cluster_dir}{cluster_method}_{n_clusters_}.svg',format='svg',dpi=600,bbox_inches='tight')
            plt.show()
            if s1 == 2:
                shutil.copyfile(f'{self.cluster_dir}{cluster_method}_{n_clusters_}.svg',f'{self.hopdir}final_plot/{cluster_method}_{n_clusters_}.svg')
            cluster_list=self.get_list(labels,n_clusters_)
            print(cluster_list)
            np.save(f'{self.cluster_dir}cluster_list.npy',cluster_list)
            # np.savetxt(f'{self.cluster_dir}cluster_list.dat',cluster_list)
            self.cluster_file(labels,n_clusters_,cluster_list)
            self.plot_population(cluster_list,n_clusters_)
            self.average_item(cluster_list,n_clusters_)
            self.cluster_center_xyz(cluster_list,n_clusters_)

    def cluster_file(self,labels,n_clusters,cluster_list):
        unique_labels = set(labels)
        for i in list(unique_labels):
            if i !=-1:
                with open(f'{self.cluster_dir}cluster_{i+1}.xyz','w') as file1:
                    for j in cluster_list[i+1]:
                        file1.write(f'{self.natom}\n')
                        file1.write('\n')
                        with open(f'{self.hopdir}{j}/{j}.xyz','r') as file2:
                            for line in file2:
                                file1.write(line)
                                   
        already_have_center=['bi','ap','ms','mb','km']
        if self.method_abb not in already_have_center:
            for i in list(unique_labels):
                if i != -1:
                    n_mol = len(cluster_list[i+1])
                    mol_i=np.zeros((self.natom,3))
                    for j in cluster_list[i+1]:
                        atom_name=[]
                        with open(f'{self.hopdir}{j}/{j}.xyz','r') as file3:
                            nu=-1
                            for line in file3:
                                nu+=1
                                atom_name.append(line.split()[0])
                                for m in range(3):
                                    mol_i[nu][m]+=float(line.split()[m+1])/n_mol
                    with open(f'{self.cluster_dir}average_mol_{i+1}.xyz','w') as file4:
                        file4.write(f'{self.natom}\n\n')
                        for n in range(self.natom):
                            file4.write(f'{atom_name[n]}\t{round(mol_i[n][0],8)}\t{round(mol_i[n][1],8)}\t{round(mol_i[n][2],8)}\t\n')


    def average_item(self,cluster_list,n_cluster):                
        item_list=['R','D','A','H_R','H_A','H_D']
        # item_list=['D']
        for item in item_list:
            nu1=0
            item_name=[]
            # try:
            with open(f'{self.hopdir}{cluster_list[1][0]}/{item[-1]}/{item}.dat','r') as file1:
                for line in file1:
                    nu1+=1
                    item_name.append(line.split()[1])

            for i in range(n_cluster):
                num=len(cluster_list[i+1])
                item_all=np.zeros((num,nu1))
                average_all= [0]*nu1
                sign_ne=[0]*nu1
                nu2=-1
                for j in cluster_list[i+1]:
                    nu2+=1
                    line_nu=-1
                    with open(f'{self.hopdir}{j}/{item[-1]}/{item}.dat','r') as file2:
                        for line in file2:
                            line_nu+=1
                            if float(line.split()[2]) < 0 :
                                sign_ne[line_nu]+=1
                            average_all[line_nu] += round(abs(float(line.split()[2])/num),6)
                            item_all[nu2, line_nu]=round(float(line.split()[2]),6)
                
                np.savetxt(f'{self.cluster_dir}all_elements_{item}_{i+1}.dat',item_all,fmt='%1.6f')
                
                # remove_nu=int(round(num*0.1))
                # new_nu=num-remove_nu
                # average_all=np.zeros((new_nu,nu1))
                # for nu1s in range(nu1):
                #     average_all[:,nu1s] = self.cal_similarity(item_all[:,nu1s],remove_nu)
                # average_one=np.mean(average_all,axis=0)
                
                with open(f'{self.cluster_dir}{item}_{i+1}.dat','w') as file3:
                    for m in range(line_nu+1):
                        if sign_ne[m] > round( len(cluster_list[i+1])/2):
                            # print(sign_ne[m],round(len(cluster_list[i+1])/2))
                            average_all[m] *= -1
                            # average_one[m] *= -1
                        # file3.write(f'{item_name[m]}\t{average_one[m]}\n')
                        file3.write(f'{item_name[m]}\t{average_all[m]}\n')
                        



    # def cal_similarity(self,list1,remove_nu):
    #     # print(remove_nu)
    #     # print(len(list1))
    #     for iters in range(remove_nu):
    #         nums = len(list1)
    #         list_dis=[0]*len(list1)
    #         for i in range(nums):
    #             for j in range(nums):
    #                 list_dis[i]+=abs(abs(list1[i])-abs(list1[j]))
    #         nu = list_dis.index(max(list_dis))
    #         list1=np.delete(list1,nu)
    #     # print(len(list1))
    #     return list1
        
    def cluster_center_xyz(self,cluster_list,n_cluster):
        item_list=['R','H_R','A','H_A','D','H_D']
        # item_list=['D']
        for i in range(n_cluster):
            fileA=f'{self.cluster_dir}cluster{i+1}_.gjf'
            shutil.copyfile(f'{self.file_dir}redundant_ic.gjf',fileA)
            for item in item_list:
                if item[-1] == 'R':
                    itemname='B'
                else:
                    itemname=item[-1]
                with open(fileA,'a') as f1, \
                    open(f'{self.cluster_dir}{item}_{i+1}.dat','r') as f2:
                        # print(f'{self.cluster_dir}{item}_{i+1}.dat')
                        for line in f2:
                            f1.write(f'{itemname} ')
                            str2 = line.split()[0].replace('(', '').replace(')','').replace(f'{item[-1]}', '').replace(',',f' ')
                            f1.write(f'{str2} ')
                            f1.write(f'{round(float(line.split()[1]),4)} F\n')
            with open(fileA,'a') as f1:
                f1.write(f'\n\n')
            os.chdir(f'{self.cluster_dir}')
            sub.call(f'dos2unix {fileA}', shell=True)
            sub.call(f'rung16 {fileA}', shell=True)
                

    def plot_population(self,nu_list,n_cluster):

        if self.descriptor != 'Coulomb_matrix':
            hop_example=np.load(self.hop)[0]
            keys_aka,keys_name = [],[]
            with open(f'{self.hopdir}{hop_example}/{self.descriptor[-1]}/{self.descriptor}.dat','r') as file:
                for line in file:
                    list1 = line.split()[1].strip(self.descriptor).lstrip('(').rstrip(')').split(',')
                    if len(self.remove_list)!= 0:
                        if not set(self.remove_list)&set(list1):
                            keys_aka.append(line.split()[0])
                            keys_name.append(line.split()[1])
                    elif len(self.keep_list)!= 0:
                        if set(self.keep_list)&set(list1):
                            keys_aka.append(line.split()[0])
                            keys_name.append(line.split()[1])
                    else:
                        keys_aka.append(line.split()[0])
                        keys_name.append(line.split()[1])
        
        key_nu=len(keys_aka)

        for i in range(n_cluster):
            total_nu=int(len(nu_list[i+1]))
            matrix_for_one_cluster = np.zeros((total_nu,key_nu))
            line_nu=-1
            for nu in nu_list[i+1]:
                line_nu += 1
                path2 = f'{self.hopdir}{nu}/{self.descriptor[-1]}/{self.descriptor}.dat'
                with open(path2,'r', encoding="utf-8") as file2:
                    column_nu = -1
                    for line in file2:
                        if line.split()[0] in keys_aka:
                            column_nu += 1
                            matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))

            x = [i+1 for i in range(total_nu)]
            for member in enumerate(keys_name):
                # s = 0
                # for i in range(totalnu):
                #    s += (matrix_for_one_block[i,member[0]] - key_average[member[0]])**2
                # standard_deviation = (s/totalnu)**0.5
                # s_result.append(standard_deviation)
                plt.figure()
                # matrix_for_one_block[:,member[0]].sort()
                plt.title(f'{member[1]}-distribution')
                #plt.plot(x,matrix_for_one_block[:,member[0]])
                plt.scatter(x,sorted(matrix_for_one_cluster[:,member[0]]))
                ax = plt.gca()
                ax.yaxis.set_major_locator(plt.MultipleLocator(10))
                #if self.remake != 'yes':
                #plt.ylim(-10,180)
                plt.xlabel('Sample')
                plt.ylabel(f'{member[1]}')
                # plt.title('Dihedral Angle Distribution')
                # plt.text(0,0.9,f's={standard_deviation}',weight="bold",fontsize=10,transform=plt.gca().transAxes)
                plt.savefig(f'{self.cluster_dir}{keys_aka[member[0]]}_{member[1]}_cluster{i+1}.svg',format='svg',dpi=600,bbox_inches='tight')
                plt.close()
                
            sub_nu = 0
            fig_nu = 1
            fig = plt.figure(fig_nu,figsize=(12,8))
            for member in enumerate(keys_name):
                # s=s_result[member[0]]
                if sub_nu <= 3:
                    sub_nu += 1
                    plt.subplot(2,2,sub_nu)
                    # plt.text(0,0.9,f's={s}',weight="bold",fontsize=15,transform=plt.gca().transAxes)
                    plt.title(f'{member[1]}-distribution')
                    plt.scatter(x,matrix_for_one_cluster[:,member[0]])
                    ax = plt.gca()
                    ax.yaxis.set_major_locator(plt.MultipleLocator(10))
                    if self.remake != 'yes':
                        plt.ylim(-10,180)
                    plt.tick_params(labelsize=6)
                else:
                    fig.savefig(f'{self.cluster_dir}{fig_nu}_all_population_cluster{i+1}.svg')
                    plt.close()
                    sub_nu =0
                    fig_nu += 1
                    fig = plt.figure(fig_nu,figsize=(12,8))
                    sub_nu += 1
                    plt.subplot(2,2,sub_nu)
                    plt.title(f'{member[1]}-distribution')
                    plt.scatter(x,matrix_for_one_cluster[:,member[0]])
                    # plt.text(0,0.9,f's={s}',weight="bold",fontsize=15,transform=plt.gca().transAxes)
                    ax = plt.gca()
                    ax.yaxis.set_major_locator(plt.MultipleLocator(10))
                    if self.remake != 'yes':
                        plt.ylim(-10,180)
                    plt.tick_params(labelsize=6)
            fig.savefig(f'{self.cluster_dir}{fig_nu}_all_population_cluster{i+1}.svg',format='svg',dpi=600,bbox_inches='tight')
            plt.close()                 
        
        
    def get_list(self,labels,cluster_nu):
        if self.remake != 'yes':
            hoplist = self.hoplist
        else:
            if self.remake_after_block == 'yes':
                hoplist=np.load(f'{self.hopdir}block_{self.partition_method}/{self.partition_descriptor}/block_info_{self.partition_method}.npy',allow_pickle=True).item().get(self.remake_block_nu)
            elif self.remake_after_cluster == 'yes':
                # for i in range(100):
                #     if not os.path.exists(f'{self.hopdir}cluster_method_old_{i+1}'):
                #         self.old_cluster_dir = f'{self.hopdir}cluster_old_{i+1}/'
                #         break
                try:
                    hoplist=np.load(f'{self.old_cluster_dir}cluster_list.npy',allow_pickle=True).item().get(self.remake_block_nu)
                except ValueError:
                    hoplist=np.load(f'{self.old_cluster_dir}cluster_list.npy',allow_pickle=True).tolist()
        nu = -1
        cluster_list = dict([(k+1, []) for k in range(cluster_nu)])
        for i in labels:
            nu+=1
            for j in range(cluster_nu):
                if i == j:
                    cluster_list[j+1].append(hoplist[nu])
        return cluster_list
    

def main(s1):
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    clusters = Cluster_all(para_all)
    clusters.method_choose(s1)
    print('\nDone !\n')

def main_main():
    s=input('Perform clustering after PCA ? (yes/no)')
    s1 = 1 if s == 'yes' else 2
    main(s1)

if __name__ == '__main__':
    s=input('Perform clustering after PCA ? (yes/no)')
    s1 = 1 if s == 'yes' else 2
    main(s1)
