'''
Author: your name
Date: 2022-03-20 19:26:15
LastEditTime: 2022-03-21 09:06:45
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /jp6_test/sub/test.py
'''
# import matplotlib.pyplot as plt
# import numpy as np

# t = np.arange(0.01, 5.0, 0.01)
# s1 = np.sin(2*np.pi*t)
# s2 = np.exp(-t)
# s3 = np.sin(4*np.pi*t)

# ax1 = plt.subplot(311)
# plt.plot(t, s1)
# plt.setp(ax1.get_xticklabels(), fontsize=6)

# # share x only
# ax2 = plt.subplot(312, sharex=ax1)
# plt.plot(t, s2)
# # make these tick labels invisible
# plt.setp(ax2.get_xticklabels(), visible=False)

# # share x and y
# ax3 = plt.subplot(313, sharex=ax1, sharey=ax1)
# plt.plot(t, s3)
# plt.xlim(0.01, 5.0)
# plt.show()


import matplotlib.pyplot as plt
plt.axhline(y=0.5, color='r', linestyle='-')
plt.show()