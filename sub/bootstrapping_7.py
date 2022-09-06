'''
Author: zhuyf
Date: 2022-08-11 20:04
LastEditors: error: git config user.name && git config user.email & please set dead value or install git
LastEditTime: 2022-08-19 15:14:27
Description: file content
FilePath: /jp6_test/sub/bootstrapping_7.py
'''
import os
import sys
import shutil
from turtle import width
import numpy as np
import pandas as pd
from sub.pca_4_1 import Sklearn_pca
from sklearn.decomposition import PCA
import sub.sub_interface_json as sub_interface_json
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import pylab

class bootstrap(Sklearn_pca):
    def __init__(self,para_all):
        super().__init__(para_all)
        self.bt_path=f'{self.hopdir}bootstrap/'
        self.data_from=f'{self.hopdir}cluster/cluster_list.npy'
        
        item=para_all['structural_descriptor']
        self.item_i=self.structural_dict[item]
        
        if self.remake_after_cluster != 'yes':
               self.remake_block_nu = 0
        else:
            try:
                self.remake_block_nu = int(para_all['remake_operate_nu'])
            except ValueError:
                print('Remake but the parameter [remake_block_nu] in input.inp is not specified！')
                sys.exit(0)     
        
        # self.all_time=int(input('Enter a int to specify how many times to cycle:\n'))
        self.all_time=int(para_all['cycle_time'])

    def re_sample(self,times):
        # data = pd.Series(np.array(range(1,100)))
        try:
            data=pd.Series(np.load(self.data_from,allow_pickle=True).item()[self.remake_block_nu])
        except ValueError:
            self.data_from=f'{self.hopdir}cluster/cluster_list_old.npy'
            data=pd.Series(np.load(self.data_from,allow_pickle=True).item()[self.remake_block_nu])

        train = data.sample(frac=1.0,replace=True)
        diff = data.loc[data.index.difference(train.index)].copy()
        print(f'   {"{:.2f}".format(times/self.all_time*100, 3)}%\tTotal:{len(data )}\tReplacement:{len(diff)}')
        
        samples=[int(x)+10000 for x in train]
        samples.extend(list(map(int,train)))

        np.savetxt(f'{self.bt_path}{times}_samples.dat',samples,fmt='%d')
        
        return samples

    
        
    def re_pca(self,samples,time):
        if self.PCA_switch == 'yes':
            
            self.X_matrix=f'{self.bt_path}X_matrix/'

            os.mkdir(self.X_matrix)
            
            save_stdout = sys.stdout
            sys.stdout = open(f'{self.bt_path}tmp', "w")
            self.get_matrix_X(samples,self.remake_block_nu)
            sys.stdout = save_stdout


            x = np.load(f'{self.X_matrix}{self.item_i}_{self.remake_block_nu}.npy')
            pca = PCA(n_components=self.n_components)
            x_new = pca.fit_transform(x)
            np.savetxt(f'{self.bt_path}{time}_{self.item_i}_components_{self.remake_block_nu}.dat', pca.components_)
            
            shutil.rmtree(self.X_matrix)
        else:
            print('Are you sure you want to use this method? Please check input.inp')
            os._exit(0)
            
    def read_results(self, df1, time):
        data_i=np.loadtxt(f'{self.bt_path}{time}_{self.item_i}_components_{self.remake_block_nu}.dat').reshape(1,-1)
        df2 = pd.DataFrame(map(abs,data_i))
        df1 = df1.append(df2)

        return df1
        
    def plot_box(self):
        hop_example=np.load(self.hop)[0]
        label_list=[]
        with open(f'{self.hopdir}{hop_example}/{self.item_i[-1]}/{self.item_i}.dat','r') as file:
            for line in file:
                # if item == 'D' and len(self.remove_list)!= 0:
                list1 = line.split()[1].strip(self.item_i).lstrip('(').rstrip(')').split(',')
                if len(self.remove_list)!= 0:
                    if not set(self.remove_list)&set(list1):
                        label_list.append(line.split()[1])
                elif len(self.keep_list)!= 0:
                    if set(self.keep_list)&set(list1):
                        label_list.append(line.split()[1])
                else:
                    label_list.append(line.split()[1])               
        
        df = pd.read_csv(f'{self.bt_path}dataset.csv')
        # plot_list=np.array(df.mean(axis=0)[1:]).reshape(3,-1).T
        # ax1=sns.heatmap(abs(plot_list),cmap=plt.cm.Greys)
        mean_list = np.array(df.mean(axis=0)[1:int((np.shape(df)[-1]-1)/3+1)])           
        plot_list = df.iloc[:,1:int((np.shape(df)[-1]-1)/3+1)]
        # std_list = np.array(df.std(axis=0)[1:int((np.shape(df)[-1]-1)/3+1)]) 
        
        plt.boxplot(plot_list,showfliers=False,medianprops={'color':'#FFA500'})
        
        x_aix=list(range(1,int((np.shape(df)[-1]-1)/3+1)))
        plt.plot(x_aix,mean_list,'b', linewidth=1.0,label='mean value')
        try:
            shutil.copyfile(f'{self.hopdir}PCA/{self.item_i[-1]}/{self.item_i}_components_{self.remake_block_nu}.dat',f'{self.bt_path}{self.item_i}_components_{self.remake_block_nu}.dat')
            actual_list=abs(np.loadtxt(f'{self.bt_path}{self.item_i}_components_{self.remake_block_nu}.dat')[0,:])
            plt.plot(x_aix,actual_list,'r', linestyle='--', linewidth=1.0,label='actual value')
        except FileNotFoundError:
            print('\nERROR! You should copy the true value file of components\n')
            os._exit()
        

        for col in range(1,int((np.shape(df)[-1]-1)/3+1)):
            nn = stats.anderson(df.iloc[:,col], dist='norm')
            
            #test of normality
            ##1
            # sm.qqplot(df.iloc[:,loc], line='s')
            # pylab.show()
            ##2
            # nn = stats.shapiro(df.iloc[:,col])
            #3
            nn = stats.normaltest(df.iloc[:,col]) 
            ##4
            # nn = stats.anderson(df.iloc[:,col], dist='norm')

            tt = stats.ttest_1samp(df.iloc[:,col], actual_list[col-1])
            print(nn,tt)

        
        plt.legend(prop={'size' : 14},framealpha=0,handletextpad=0.1,borderaxespad=0.2)
        plt.tick_params(labelsize=10)
        plt.xticks(list(range(1,int((np.shape(df)[-1]-1)/3+1))),label_list)
        plt.xlabel('Features of the 1st Dimension',fontdict={'weight':'bold','size' : 14})
        # plt.show()
        plt.savefig(f'{self.bt_path}bt_1st_dim_{self.item_i}.svg')
        plt.savefig(f'{self.bt_path}bt_1st_dim_{self.item_i}.png')
             

    def sub_main(self):
        order=int(input('\n1 - Step1: PCA\n2 - Step2: Dataframe\n3 - Step3: Plot\n'))
        
        if order == 1:
            print('\nStep1: PCA')
            if os.path.exists(self.bt_path):
                for i in range(10000):
                    if not os.path.exists(f'{self.hopdir}bootstrap_old_{i+1}'):
                        os.rename(self.bt_path,f'{self.hopdir}bootstrap_old_{i+1}')
                        break
            os.mkdir(self.bt_path)
            for i in range(self.all_time):
                samples=self.re_sample(i+1)
                self.re_pca(samples, i+1)
            os.remove(f'{self.bt_path}tmp')
            print('PCA Done!\n')
        
        elif order == 2:
            print('\nStep2: Dataframe')
            df1 = pd.DataFrame()
            for j in range(self.all_time):
                df1 = self.read_results(df1, j+1)
            df1.columns += 1
            df1.index += 1
            df1.to_csv(f'{self.bt_path}dataset.csv')
            print(df1)
            print('Construction Done!\n')
        
        elif order == 3:
           self.plot_box()
            

        
def main():
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    bt=bootstrap(para_all)
    bt.sub_main()
    

    
if __name__ == '__main__':
    main()
