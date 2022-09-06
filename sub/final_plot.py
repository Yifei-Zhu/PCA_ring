'''
Author: zhuyf
Date: 2022-03-18 22:15:48
LastEditTime: 2022-03-23 11:32:44
LastEditors: Please set LastEditors
Description: 
FilePath: /jp6_test/sub/final_plot.py
'''
from cProfile import label
import os
import shutil
import numpy as np
from matplotlib import ticker as tk
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
import seaborn as sns
from sub.pca_4_1 import Sklearn_pca
from sub.cluster_all import main as cluster_plot
import sub.sub_interface_json as sub_interface_json
from matplotlib.gridspec import GridSpec 

class Final_plot(Sklearn_pca):
    def __init__(self,para_all):
        super().__init__(para_all)
        self.pca_path = f'{self.hopdir}PCA/'
        if self.remake == 'yes':
            self.nu = int(para_all['remake_operate_nu'])
        else:
            self.nu = 0
        self.final_plot_dir = f'{self.hopdir}final_plot/'
        if not os.path.exists(self.final_plot_dir):
            os.mkdir(self.final_plot_dir)
        self.item=para_all['partition_descriptor']

    def plot_components(self,font1,font2):
        datafile = f'{self.pca_path}{self.item}/{self.item}_components_{self.nu}.dat'
        x=np.loadtxt(datafile)
        hop_example=np.load(self.hop)[0]
        label_list=[]
        with open(f'{self.hopdir}{hop_example}/{self.item[-1]}/{self.item}.dat','r') as file:
            for line in file:
                list1 = line.split()[1].strip(self.item).lstrip('(').rstrip(')').split(',')
                if len(self.remove_list)!= 0:
                    if not set(self.remove_list)&set(list1):
                        label_list.append(line.split()[1])
                elif len(self.keep_list)!= 0:
                    if set(self.keep_list)&set(list1):
                        label_list.append(line.split()[1])
                else:
                    label_list.append(line.split()[1])
        
        ax3 = sns.heatmap(abs(x.T),cmap=plt.cm.Greys,xticklabels=list(range(1,x.T.shape[1]+1,1)))
        ax3.set_yticklabels(label_list,rotation='horizontal')
        ax3.set_ylabel('Features',font1) 
        ax3.set_xlabel('Dimensions',font1)
        ax3.tick_params(which='major', labelbottom=True, labeltop=False,labelsize=10)
        # cbar = ax3.collections[0].colorbar
        # cbar.set_ticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
        # cbar.set_ticklabels(['','10%','20%','30%','40%','50%','60%','70%','80%','90%',''])
        
    def plot_low_dim(self,font1,font2):
        x= np.load(f'{self.pca_path}{self.item}/{self.item}_low_dim_{self.nu}.npy')
        # np.save(f'{coulomb_pca_dir}{item}_low_dim_{nu}.npy', x_new)
        if self.s0=='yes': 
            x_1,y_1,x_2,y_2=[],[],[],[]
            nus=int(len(x[:,0])/2)
            for n in range(nus):
                x_1.append(x[n,0])
                y_1.append(x[n,1])
                x_2.append(x[nus+n,0])
                y_2.append(x[nus+n,1])  
                plt.scatter(x_1,y_1,color ='#FF0000', label='hop-points')
                plt.scatter(x_2,y_2,color = '#0000FF', label='S0')
            leg=plt.legend(loc='upper right',prop=font2, scatterpoints=1,markerscale=1,scatteryoffsets=[0.5],framealpha=1)
            leg.get_frame().set_linewidth(0.0)
        else:
            plt.scatter(x[:,0],x[:,1])
        plt.xlabel(self.list_name[0],font1)
        plt.ylabel(self.list_name[1],font1)
        # leg=plt.legend(loc='upper right',prop=font2, scatterpoints=3,markerscale=1,scatteryoffsets=[0.5,0.5,0.5],framealpha=1)
        leg=plt.legend(loc='upper right',prop=font2, scatterpoints=1,markerscale=1,scatteryoffsets=[0.5],framealpha=1)
        leg.get_frame().set_linewidth(0.0)
        ax = plt.gca()
        # ax.xaxis.set_major_locator(MultipleLocator(50))
        # ax.yaxis.set_major_locator(MultipleLocator(50))                
        ax.tick_params(labelsize=12)
        
    def plot_variance_ratio(self,font1,font2):
        datafile = f'{self.pca_path}{self.item}/{self.item}_variance_ratio_{self.nu}.dat'
        x2=np.loadtxt(datafile)
        ax2=plt.plot(x2)
        plt.ylim(0,1)
        plt.xlabel('Dimensions',font1)
        plt.ylabel('Variance Ratio',font1)
        ax = plt.gca()
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.yaxis.set_major_locator(MultipleLocator(0.2))
        ax.yaxis.set_major_formatter(tk.PercentFormatter(xmax=1,decimals=0))

    def plot_population(self,font1,font2):

        if self.item != 'Coulomb_matrix':
            hop_example=np.load(self.hop)[0]
            keys_aka,keys_name = [],[]
            with open(f'{self.hopdir}{hop_example}/{self.item[-1]}/{self.item}.dat','r') as file:
                for line in file:
                    list1 = line.split()[1].strip(self.item).lstrip('(').rstrip(')').split(',')
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
        
        x= np.load(f'{self.pca_path}{self.item}/{self.item}_low_dim_{self.nu}.npy')
        xx=np.argsort(x[:,0])
        if self.remake == 'yes':
            list_old= np.loadtxt(f'{self.descriptor_dir}list_all_{self.operate_nu}.dat')
        else:
            list_old=self.hoplist
        list_all=[]
        for i in xx:
            list_all.append(list_old[i])
        
        main_key1=['A(1,4,10)','A(2,3,5)','D(3,2,10,4)','D(10,2,3,5)','R(2,3)','R(2,10)','D(6,1,4,10)','D(6,1,5,3)']
        main_key2=['A(1,5,3)','A(2,10,4)','D(1,4,10,2)','D(2,3,5,1)','R(4,10)','R(3,5)']
        total_nu=int(len(list_all))
        matrix_for_one_cluster = np.zeros((total_nu,key_nu))
        line_nu=-1
        for nu in list_all:
            line_nu += 1
            path2 = f'{self.hopdir}{int(nu)}/{self.item[-1]}/{self.item}.dat'
            with open(path2,'r', encoding="utf-8") as file2:
                column_nu = -1
                for line in file2:
                    # if line.split()[0] in keys_aka and line.split()[1] in main_key:
                    if line.split()[0] in keys_aka:
                        column_nu += 1
                        if line.split()[1] in main_key1:
                            if self.item == 'A':
                                matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))-50
                            elif self.item == 'D':
                                if self.keep_list:
                                    matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))
                                else:
                                    matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))+70
                            elif self.item == 'R':
                                matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))+0.7
                        elif line.split()[1] in main_key2:
                            if self.item == 'A':
                                matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))-100
                            elif self.item == 'D':
                                matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))
                            elif self.item == 'R':
                                matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))
                        else:
                            if self.item == 'A':
                                if self.keep_list:
                                    aa=['A(4,1,6)','A(5,1,6)']
                                    if line.split()[1] in aa:
                                        matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))
                                    else:
                                        matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))-60
                                else:
                                    matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))
                            elif self.item == 'D':
                                matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))+100
                                matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))+140
                            elif self.item == 'R':
                                matrix_for_one_cluster[line_nu,column_nu]=abs(float(line.split()[2]))+1.4
        
        
        # x= np.load(f'{self.pca_path}{self.item}/{self.item}_low_dim_{self.nu}.npy')
        # x_sort=sorted(x[:,0])
        # x_min=int(x_sort[0])-1
        # x_max=int(x_sort[-1])+2
        # x_label=np.arange(x_min,x_max,step=0.1)
        # x_nu=len(x_label)
        # max_nu=len(x_sort)
        # x_index=np.linspace(0,max_nu-1,x_nu)
        
        for member in enumerate(keys_name):
            plt.plot(sorted(x[:,0]),matrix_for_one_cluster[:,member[0]],label=member[1])
                     
        # x = [i+1 for i in range(total_nu)]
        # for member in enumerate(keys_name):
        #     plt.plot(x,matrix_for_one_cluster[:,member[0]],label=keys_name[member[0]])
            # plt.plot(x,sorted(matrix_for_one_cluster[:,member[0]]),label=keys_name[member[0]])
            
        
        plt.xlabel(self.list_name[0],font1)
        if self.item == 'D':
            plt.ylabel('Dihedral Angle',font1)
        elif self.item == 'A':
            plt.ylabel('Angle',font1)
        elif self.item == 'R':
            plt.ylabel('Bond length',font1)
        
        if not self.keep_list:
            leg=plt.legend(ncol=1,bbox_to_anchor=(1.0,1.0),borderaxespad = 0.,framealpha=0,labelspacing=3,handletextpad=0.1)
            leg.get_frame().set_linewidth(0.0)
            ax = plt.gca()
            ax.yaxis.set_major_locator(plt.MultipleLocator(10))
        else:
            leg=plt.legend(fontsize=10,framealpha=0)
            leg.get_frame().set_linewidth(0.0)
        # ax.spines['right'].set_visible(False)

        if self.item == 'A':
            if self.keep_list :
                plt.ylim(30,150)
                ax = plt.gca()
                ax.yaxis.set_major_locator(plt.MultipleLocator(20))
                plt.yticks([40,60,80,100,120,140],[100,120,140,100,120,140])
                plt.axhline(y=90,c='k',lw=0.7)
                # plt.axhline(y=30,c='k',lw=0.7)
            else:
                # plt.ylim(-30,140)
                ax = plt.gca()
                ax.yaxis.set_major_locator(plt.MultipleLocator(10))
                x_lim=np.arange(-10,140,10)
                plt.yticks(x_lim,[90,'',110,'',130,90,'',110,'',130,90,'',110,'',130,])
                plt.axhline(y=90,c='k',lw=0.7)
                plt.axhline(y=40,c='k',lw=0.7)
       
        elif self.item == 'D':
            if self.keep_list:
                # plt.axhline(y=180,c='k',lw=0.5)
                plt.axhline(y=200,c='k',lw=0.5)
                ax=plt.gca()
                ax.yaxis.set_major_locator(plt.MultipleLocator(20))
                # x_lim=np.arange(60,260,step=20)
                # plt.yticks(x_lim,['',180,'',220,'',260,'',200,'',240])
                # x_lim=np.arange(60,340,step=20)
                # plt.yticks(x_lim, [60,'',100,'',140,'',180,'',120,'',160,'',200,''])
                x_lim=np.arange(60,460,step=20)
                plt.yticks(x_lim, [60,'',100,'',140,'',180,'',120,'',160,'',200,'',240,'',280,'',320,''])
            else:
                ax.yaxis.set_major_locator(plt.MultipleLocator(20))
                # plt.yticks([0,20,40,60,80,100,120,140,160,180],[0,20,40,60,10,30,50,70,90,110])
                plt.yticks([0,20,40,60,80,100,120,140,160,180,200,220,240],[0,20,40,60,10,30,50,0,20,40,60,80,100])
                plt.axhline(y=70,c='k',lw=0.5)
                plt.axhline(y=140,c='k',lw=0.5)
        elif self.item == 'R':
            ax = plt.gca()
            ax.yaxis.set_major_locator(plt.MultipleLocator(0.1))
            plt.ylim(1.1,3.2)
            a=np.arange(1.1,3.2,0.1)
            plt.yticks(a,[1.1,'',1.3,'',1.5,'',1.7,1.1,'',1.3,'',1.5,'',1.7,1.1,'',1.3,'',1.5,'',1.7,])
            plt.axhline(y=2.5,c='k',lw=0.5)
            plt.axhline(y=1.8,c='k',lw=0.5)
       
    def plot_4_main(self):
        if self.item == 'R' and self.keep_list:
            print('Out ring bond length needs -f-3!!!!')
            os._exit(0)
        font1 = {#'family' : 'Times New Roman',
            'weight' : 'bold',
            'size' : 15,
            }
        font2={#'family':'Arial',
            'weight':'normal',
            'size':15,
            }
        fig = plt.figure(figsize=(15,9))
        plt.style.use('seaborn-bright')
        ax1= plt.subplot2grid((6, 10), (0, 0), colspan=6, rowspan=4)
        self.plot_low_dim(font1,font2)
        plt.text(0.93,0.04,f'(a)',weight="bold",fontsize=15,transform=plt.gca().transAxes)
        
        ax2=plt.subplot2grid((6,50), (0, 32), colspan=19, rowspan=3)
        self.plot_variance_ratio(font1,font2)
        plt.text(0.88,0.9,f'(b)',weight="bold",fontsize=15,transform=plt.gca().transAxes)
        
        ax3=plt.subplot2grid((6,20), (3, 13), colspan=7, rowspan=3)
        self.plot_components(font1,font2)
        plt.text(3,4,6,f'(c)',weight="bold",fontsize=15,transform=plt.gca().transAxes)

        ax4=plt.subplot2grid((6,10), (4, 0), colspan=6, rowspan=2)
        self.plot_population(font1,font2)
        plt.text(0.94,0.07,f'(d)',weight="bold",fontsize=15,transform=plt.gca().transAxes)

        # plt.tight_layout()
        # plt.tight_layout(pad=0.2,w_pad=0.6)
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=2, hspace=1)
        # plt.show()
        plt.savefig(f'{self.final_plot_dir}/{self.item}_{self.nu}.png')
        plt.close()
        
    def plot_4_equal(self):
        print(self.item)
        if self.item == 'R' and self.keep_list:
            print('Out ring bond length needs -f-3!!!!')
            os._exit(0)
        font1 = {#'family' : 'Times New Roman',
            'weight' : 'bold',
            'size' : 15,
            }
        font2={#'family':'Arial',
            'weight':'normal',
            'size':15,
            }
        fig = plt.figure(figsize=(15,9))
        plt.style.use('seaborn-bright')
        ax1= plt.subplot2grid((6, 10), (0, 0), colspan=5, rowspan=3)
        self.plot_low_dim(font1,font2)
        plt.text(0.93,0.04,f'(a)',weight="bold",fontsize=15,transform=plt.gca().transAxes)
        
        ax2=plt.subplot2grid((6,50), (0, 27), colspan=22, rowspan=3)
        self.plot_variance_ratio(font1,font2)
        plt.text(0.88,0.9,f'(b)',weight="bold",fontsize=15,transform=plt.gca().transAxes)
        
        if self.item == 'D': 
            ax3=plt.subplot2grid((6,50), (3, 29), colspan=21, rowspan=3)
        elif self.item == 'R': 
            ax3=plt.subplot2grid((6,50), (3, 28), colspan=22, rowspan=3)
        elif self.item == 'A': 
            ax3=plt.subplot2grid((6,50), (3, 28), colspan=22, rowspan=3)
        self.plot_components(font1,font2)
        plt.text(1.1,-0.1,f'(c)',weight="bold",fontsize=15,transform=plt.gca().transAxes)

        if self.keep_list:
            ax4=plt.subplot2grid((6,10), (3, 0), colspan=5, rowspan=3)
        else:
            ax4=plt.subplot2grid((6,50), (3, 0), colspan=20, rowspan=3)
        self.plot_population(font1,font2)
        plt.text(1.05,-0.1,f'(d)',weight="bold",fontsize=15,transform=plt.gca().transAxes)


        # plt.tight_layout(pad=0.2,w_pad=0.6)
        plt.subplots_adjust(left=0.1, bottom=0.1, right=None, top=None, wspace=2, hspace=1)
        # plt.show()
        if self.keep_list:
            plt.savefig(f'{self.final_plot_dir}/out_{self.item}_{self.nu}.png')
        else:
            plt.savefig(f'{self.final_plot_dir}/{self.item}_{self.nu}.png')
        plt.close()
        
    def plot_2_equal(self):
        s1=input('Use this codes to plot 2 equal fig?(yes/nno)\n').lower()
        if s1 !='yes':
            os._exit()
        font1 = {#'family' : 'Times New Roman',
            'weight' : 'bold',
            'size' : 15,
            }
        font2={#'family':'Arial',
            'weight':'normal',
            'size':15,
            }
        fig = plt.figure(figsize=(16,6))
        plt.style.use('seaborn-bright')    
        plt.subplot(121)
        list_old= np.loadtxt(f'{self.descriptor_dir}list_all_{self.operate_nu}.dat')
        x_16_1,y_910_1,x_16_2,y_910_2=[],[],[],[]
        x_all,y_all=[],[]
        for nu in list_old:
            path2 = f'{self.hopdir}{int(nu)}/{self.item[-1]}/{self.item}.dat'
            with open(path2,'r') as file1:
                for line in file1:
                    if line.split()[1] == 'R(1,6)' or line.split()[1] == 'D(6,1,5,3)':
                        if int(nu) > 10000:
                            x_16_2.append(float(line.split()[2]))
                        else:
                            x_16_1.append(float(line.split()[2]))
                        x_all.append(float(line.split()[2]))
                    elif  line.split()[1] == 'R(9,10)' or line.split()[1] == 'D(6,1,4,10)':
                        if int(nu) > 10000:
                            y_910_2.append(float(line.split()[2]))
                        else:
                            y_910_1.append(float(line.split()[2]))
                        y_all.append(float(line.split()[2]))
                        
        all_xy=np.zeros((len(y_all),2))
        for i in range(len(y_all)):
            all_xy[i,0] = x_all[i]
            all_xy[i,1] = y_all[i]
        np.save(f'{self.final_plot_dir}two_dim.npy',all_xy)
    
        ax1=plt.gca()
        # xlim=ax1.get_xticks()
        # plt.ylim=xlim
        if self.s0=='yes':
            plt.scatter(x_16_1,y_910_1,color ='#FF0000', label='hop-points')
            plt.scatter(x_16_2,y_910_2,color = '#0000FF', label='S0')
            leg=plt.legend(prop=font2,framealpha=1)           
            leg.get_frame().set_linewidth(0.0) 
        else:
            plt.scatter(x_all,y_all)
        if self.item == 'R':         
            plt.xlabel('R(1,6)',font1)
            plt.ylabel('R(9,10)',font1)
        elif self.item == 'D':
            plt.xlabel('D(6,1,5,3)',font1)
            plt.ylabel('D(6,1,4,10)',font1)
            
        x_ax=np.linspace(1,1+len(list_old),len(list_old))
        plt.subplot(122)
        plt.scatter(x_ax,x_all,color ='#99CC00', label='R(1,6)' if self.item=='R' else 'D(6,1,5,3)' if self.item =='D' else 0)
        plt.scatter(x_ax,y_all,color ='#FF9900', label='R(9,10)' if self.item=='R' else 'D(6,1,4,10)' if self.item =='D' else 0)
        leg=plt.legend(prop=font2,framealpha=1)
        leg.get_frame().set_linewidth(0.0)
        plt.xlabel('Samples',font1)
        plt.ylabel('Bond Length',font1) if self.item == 'R' else plt.ylabel('Dihedral Angle',font1) if self.item == 'D' else 0
        plt.ylim(0.8,1.8) if self.item == 'R' else  plt.ylim() if self.item == 'D' else 0
        
        plt.subplots_adjust(left=0.1, bottom=0.1, right=None, top=None, wspace=0.2, hspace=1)
        # plt.show()
        plt.savefig(f'{self.final_plot_dir}/out_{self.item}_{self.nu}.png')
        
            
    
def main():
    input_file = 'input.inp'
    json_file = 'input.json'
    para_all = sub_interface_json.input_and_read(input_file, json_file)
    PLOT=Final_plot(para_all)
    s1=int(input('1 - 1+3 = 4\n2 - 4=4\n3 - 2=2\n'))
    if s1 == 1:
        PLOT.plot_4_main()
    elif s1 == 2:
        PLOT.plot_4_equal()
    elif s1 == 3:
        PLOT.plot_2_equal()
    elif s1 == 4:
        cluster_plot(3)

if __name__ == '__main__':
    main()