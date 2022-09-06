'''
Author: zhuyf
Date: 2021-12-08 17:10:25
LastEditors: error: git config user.name && git config user.email & please set dead value or install git
LastEditTime: 2022-08-11 21:59:24
Description: file content
FilePath: /jp6_test/main_all.py
'''

from sub.JADE_dyn_1 import main as step1_1
from sub.JADE_dyn_restart import main as step1_2
from sub.get_hop_points_2 import main as step2
from sub.descriptor_3 import main as step3
from sub.pca_4_1 import main as step4_1
from sub.mds_4_2 import main as step4_2
from sub.partition_5 import main as step5
#from sub.dbscan_5_2 import main as step5_2
from sub.cluster_all import main_main as step5_2
from sub.chirality_6 import main as step6
from sub.JADE_dyn_check_online import main as step1_3
from sub.check_job_info import main as check_info
from sub.get_s0_info import main as get_s0
from sub.final_plot import main as final_plot
from sub.bootstrapping_7 import main as bootstrap

import sys

def main():
    print("-----------------------------------------------------------------------\n")
    print("The age of JADE_patch 5.0 is conming!")
    print("-----------------------------------------------------------------------\n")
    print('Enter the specified character and select the function of jade_patch_5')
    print("-----------------------------------------------------------------------\n")
    print("!!!0 - Check jobs' information!!!")
    print('STEP1:    1 - Submit JADE job;\n')
    print('STEP1.1:  r - Restart;\n')
    print('STEP1.2:  c - Check whether 60 jobs have been submitted. If not, it will be added;\n')
    print('STEP2:    2- Get hop-points and related infomation;\n')
    print('STEP3:    3- Get the matrix of descriptor;\n')
    print('STEP4.1:  pca- PCA;\n')
    print('STEP4.2:  mds- MDS;\n')
    print('STEP5.1:    p- Partition;\n')
    print('STEP5.2:    d- Cluster;\n')
    print('STEP6:    6- Chirality;\n')
    print('s f')
    print("-----------------------------------------------------------------------\n")
    print('After STEP 1-6  Please repeat STEP 3-5\n')
    print("-----------------------------------------------------------------------\n\n")
    print("--------------------------------WARNING--------------------------------\n")
    print("--------------------------------WARNING--------------------------------\n")
    print("--------------------------------WARNING--------------------------------\n")
    # check_info()
    signal1 = input("Are you sure ---'input.inp'--- is correct? Especially 'remake = ?'!! \nEnter 'yes' to continue.\n\n\n\n")
    command_dict={
        '1':'step1_1()', 'r':'step1_2()', 'c':'step1_3()', '2':'step2()',
        '3':'step3()', 'pca':'step4_1()', 'mds':'step4_2()', 
        'p':'step5()', 'd':'step5_2()', 's': 'get_s0()', 'f':'final_plot()',
        '6':'print("------------------------------------------");\
            print("run re_gaussian_after_chiral(),and after entering \'4\' we can get the new information");\
            print("------------------------------------------");\
            step6()',
        'b':'bootstrap()'
    }
    if signal1 == 'yes': 
        print("-----------------------------------------------------------------------\n")
        singal = input('Please enter 1 / r / c / 2 / 3 / pca / mds / p / d / 6 / s / f / b  \n\n')
        exec(command_dict[singal])        
    else:
        sys.exit(0)
          
if __name__ == '__main__':
    main()
