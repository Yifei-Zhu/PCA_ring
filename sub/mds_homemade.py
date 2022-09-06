#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 09:20:40 2021

@author: zyf
"""
import numpy as np


def cla_mds(distance, i_dimension):

    """                                                                                       
    Classical multidimensional scaling (MDS)                                                  
    -------------------------------------------                                                                                              
    Input Parameters:                                                                                
    ----------                                                                                
    distance : (n_point, n_point) array                                                                          
        Symmetric distance matrix.                                                            
                                                                                               
    Return results:                                                                                   
    -------------------------------------                                                                                   
    YY : (n_point, p_dim) array                                                                          
        Configuration matrix in the low-dimensional space. 
        Each row represents a point.
        Each column represents a dimension. 
        Only the p dimensions corresponding to positive eigenvalues of B are returned.                 
                                                                                               
    eigenvalue : (n_point,) array                                                                            
        Eigenvalues of B matrix.                                                                     
               
    Reference by http://www.nervouscomputer.com/hfs/cmdscale-in-python/
                                                                                
    """

    # Number of points                                                                        
    n_point = len(distance)
 
    # Centering matrix                                                                        
    H = np.eye(n_point) - np.ones((n_point, n_point))/n_point
 
    # YY^T                                                                                    
    B = -H.dot(distance**2).dot(H)/2
 
    # Diagonalize             
    eigen_value, eigen_vec = np.linalg.eigh(B)
 
    # Sort by eigenvalue in descending order                                                  
    eigen_value_sort_index = np.argsort(eigen_value)[::-1]
 
    eigen_value = eigen_value[eigen_value_sort_index]
    eigen_vec = eigen_vec[:, eigen_value_sort_index]
   
    # Compute the coordinates using positive-eigenvalued components only                      
    eigen_value_positive_index, = np.where(eigen_value > 0)

    n_dim_index = len(eigen_value_positive_index)

    if n_dim_index > i_dimension:
       select_eigen_value_index = eigen_value_positive_index[0: i_dimension]
    else : 
       select_eigen_value_index = eigen_value_positive_index

    L_eigen_value_select = np.diag(np.sqrt(eigen_value[select_eigen_value_index]))
    V_eigen_vector_select = eigen_vec[:, select_eigen_value_index]
    Y_embedding  = V_eigen_vector_select.dot(L_eigen_value_select)
#    print("##############################")
#    print(np.shape(Y_embedding), eigen_value)
 
    return Y_embedding, eigen_value 
    