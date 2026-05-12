#!/usr/bin/env python3
"""
Generate comprehensive plots for VRPTW comparative analysis
Results data provided in CSV format
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path
import io

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Paste your data here as raw text
DATA_CSV = """Dataset,TW,Solver,Neighbor,Params,Veh,Distance,Time(ms),Solutions,NeighborsAttempted,NeighborsAccepted
data101,off,Random Walk,relocate,iterations=5000,8,3493.62,6.41,4599,5000,4598
data101,off,Random Walk,relocate+swap,iterations=5000,8,3819.52,5.78,4739,5000,4738
data101,off,Random Walk,relocate+swap+2opt,iterations=5000,8,3639.70,5.21,4920,5000,4919
data101,off,Descent,relocate,iterations=5000,8,1334.70,10.07,4641,5000,227
data101,off,Descent,relocate+swap,iterations=5000,8,1324.44,9.60,4712,5000,207
data101,off,Descent,relocate+swap+2opt,iterations=5000,8,1303.58,9.32,4924,5000,214
data101,off,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1147.87,46.54,18345,25000,500
data101,off,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1179.10,42.86,16923,25000,500
data101,off,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1218.93,42.60,20580,25000,500
data101,off,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1177.80,21.02,9116,10000,1128
data101,off,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1157.22,20.18,9420,10000,961
data101,off,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1158.75,19.75,9725,10000,968
data101,on,Random Walk,relocate,iterations=5000,27,2779.28,16.49,978,5000,977
data101,on,Random Walk,relocate+swap,iterations=5000,31,3244.12,17.17,1499,5000,1498
data101,on,Random Walk,relocate+swap+2opt,iterations=5000,30,3046.92,16.71,1080,5000,1079
data101,on,Descent,relocate,iterations=5000,25,1944.00,17.60,995,5000,171
data101,on,Descent,relocate+swap,iterations=5000,29,2093.14,21.03,1679,5000,227
data101,on,Descent,relocate+swap+2opt,iterations=5000,30,2158.20,22.47,1381,5000,198
data101,on,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,24,1917.46,84.76,3714,25000,500
data101,on,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,25,2044.62,84.39,4010,25000,497
data101,on,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,29,2211.88,92.28,3299,25000,498
data101,on,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,23,1959.31,33.13,1581,10000,748
data101,on,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,26,1893.14,38.07,2656,10000,767
data101,on,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,28,2061.99,38.05,1905,10000,620
data102,off,Random Walk,relocate,iterations=5000,8,3430.00,6.21,4591,5000,4590
data102,off,Random Walk,relocate+swap,iterations=5000,8,3741.18,5.53,4717,5000,4716
data102,off,Random Walk,relocate+swap+2opt,iterations=5000,8,3520.53,5.09,4906,5000,4905
data102,off,Descent,relocate,iterations=5000,8,1295.36,9.91,4614,5000,208
data102,off,Descent,relocate+swap,iterations=5000,8,1303.08,9.67,4616,5000,227
data102,off,Descent,relocate+swap+2opt,iterations=5000,8,1356.54,9.29,4910,5000,216
data102,off,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1103.36,46.32,18175,25000,500
data102,off,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1220.87,42.35,16453,25000,500
data102,off,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1148.32,43.16,20564,25000,500
data102,off,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1157.11,21.28,9085,10000,1074
data102,off,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1040.72,20.33,9423,10000,960
data102,off,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1164.68,19.57,9904,10000,996
data102,on,Random Walk,relocate,iterations=5000,26,3055.91,14.58,1742,5000,1741
data102,on,Random Walk,relocate+swap,iterations=5000,28,3256.44,14.23,1852,5000,1851
data102,on,Random Walk,relocate+swap+2opt,iterations=5000,28,3365.93,14.52,2004,5000,2003
data102,on,Descent,relocate,iterations=5000,23,1928.40,16.54,1706,5000,227
data102,on,Descent,relocate+swap,iterations=5000,25,1909.78,17.87,1962,5000,239
data102,on,Descent,relocate+swap+2opt,iterations=5000,28,2026.25,20.11,2450,5000,224
data102,on,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,22,1753.50,81.07,7017,25000,500
data102,on,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,24,1820.92,81.24,6322,25000,500
data102,on,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,23,1735.45,85.09,8095,25000,500
data102,on,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,22,1843.69,33.83,3320,10000,939
data102,on,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,22,1697.45,32.95,2994,10000,839
data102,on,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,24,1808.90,37.72,3981,10000,867
data1101,off,Random Walk,relocate,iterations=5000,9,4602.33,7.55,3313,5000,3312
data1101,off,Random Walk,relocate+swap,iterations=5000,9,4874.07,7.17,3938,5000,3937
data1101,off,Random Walk,relocate+swap+2opt,iterations=5000,10,4504.49,7.75,4945,5000,4944
data1101,off,Descent,relocate,iterations=5000,10,1554.15,12.11,4653,5000,229
data1101,off,Descent,relocate+swap,iterations=5000,9,1816.32,10.76,3961,5000,216
data1101,off,Descent,relocate+swap+2opt,iterations=5000,10,1657.12,10.22,4963,5000,227
data1101,off,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,10,1355.88,58.29,18814,25000,500
data1101,off,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,9,1504.71,48.04,13667,25000,500
data1101,off,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,9,1679.35,49.01,20139,25000,500
data1101,off,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,9,1817.85,22.48,6760,10000,998
data1101,off,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,10,1356.90,22.58,9260,10000,881
data1101,off,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,9,1888.91,21.75,9390,10000,911
data1101,on,Random Walk,relocate,iterations=5000,26,3395.70,15.87,928,5000,927
data1101,on,Random Walk,relocate+swap,iterations=5000,28,3748.58,15.48,1428,5000,1427
data1101,on,Random Walk,relocate+swap+2opt,iterations=5000,30,3787.56,16.56,1350,5000,1349
data1101,on,Descent,relocate,iterations=5000,24,2229.89,17.42,1127,5000,216
data1101,on,Descent,relocate+swap,iterations=5000,25,2360.85,17.87,1376,5000,236
data1101,on,Descent,relocate+swap+2opt,iterations=5000,30,2555.64,19.88,1581,5000,201
data1101,on,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,20,1967.79,78.82,4303,25000,499
data1101,on,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,21,2106.15,82.87,4747,25000,497
data1101,on,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,23,2116.44,88.33,5615,25000,500
data1101,on,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,22,2039.02,34.11,1983,10000,853
data1101,on,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,22,2021.56,32.60,2273,10000,750
data1101,on,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,24,2246.04,35.91,2686,10000,652
data1102,off,Random Walk,relocate,iterations=5000,10,4755.96,6.73,4717,5000,4716
data1102,off,Random Walk,relocate+swap,iterations=5000,10,4536.94,5.99,4837,5000,4836
data1102,off,Random Walk,relocate+swap+2opt,iterations=5000,10,4611.91,5.40,4957,5000,4956
data1102,off,Descent,relocate,iterations=5000,9,2048.93,10.44,3341,5000,220
data1102,off,Descent,relocate+swap,iterations=5000,9,1784.48,10.38,3901,5000,228
data1102,off,Descent,relocate+swap+2opt,iterations=5000,10,1750.64,10.47,4877,5000,221
data1102,off,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,9,1598.71,49.39,12935,25000,500
data1102,off,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,9,1475.62,46.42,13312,25000,500
data1102,off,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,10,1403.34,47.87,20452,25000,500
data1102,off,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,10,1376.24,23.57,9320,10000,1099
data1102,off,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,10,1543.37,22.24,9764,10000,847
data1102,off,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,10,1556.42,21.62,9910,10000,969
data1102,on,Random Walk,relocate,iterations=5000,25,3373.98,14.49,1515,5000,1514
data1102,on,Random Walk,relocate+swap,iterations=5000,27,3651.09,16.12,1873,5000,1872
data1102,on,Random Walk,relocate+swap+2opt,iterations=5000,30,3798.27,15.19,2162,5000,2161
data1102,on,Descent,relocate,iterations=5000,20,2062.94,17.49,1782,5000,246
data1102,on,Descent,relocate+swap,iterations=5000,24,2192.27,17.76,1999,5000,278
data1102,on,Descent,relocate+swap+2opt,iterations=5000,24,2288.72,18.36,2252,5000,258
data1102,on,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,19,1731.94,78.87,6445,25000,500
data1102,on,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,19,1923.16,74.14,5658,25000,500
data1102,on,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,23,2082.13,86.96,9538,25000,500
data1102,on,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,17,1779.47,31.69,2736,10000,993
data1102,on,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,21,1944.34,33.97,3247,10000,857
data1102,on,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,21,2100.19,36.60,4283,10000,1052
data111,off,Random Walk,relocate,iterations=5000,8,3449.94,6.15,4622,5000,4621
data111,off,Random Walk,relocate+swap,iterations=5000,8,3530.10,5.59,4718,5000,4717
data111,off,Random Walk,relocate+swap+2opt,iterations=5000,8,3397.09,5.06,4922,5000,4921
data111,off,Descent,relocate,iterations=5000,8,1262.37,10.02,4648,5000,242
data111,off,Descent,relocate+swap,iterations=5000,8,1386.35,9.59,4721,5000,232
data111,off,Descent,relocate+swap+2opt,iterations=5000,8,1331.65,9.30,4936,5000,219
data111,off,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1166.27,46.38,18219,25000,500
data111,off,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1192.61,43.35,16886,25000,500
data111,off,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1222.91,44.21,20744,25000,500
data111,off,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1121.72,21.18,9143,10000,1084
data111,off,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1244.18,20.37,9451,10000,968
data111,off,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1206.14,19.93,9860,10000,935
data111,on,Random Walk,relocate,iterations=5000,22,3004.27,13.10,2286,5000,2285
data111,on,Random Walk,relocate+swap,iterations=5000,22,2926.82,11.99,2202,5000,2201
data111,on,Random Walk,relocate+swap+2opt,iterations=5000,23,3101.99,11.78,2841,5000,2840
data111,on,Descent,relocate,iterations=5000,17,1460.37,15.96,2582,5000,260
data111,on,Descent,relocate+swap,iterations=5000,19,1595.30,16.71,2660,5000,248
data111,on,Descent,relocate+swap+2opt,iterations=5000,22,1650.20,20.45,3613,5000,269
data111,on,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,15,1264.61,66.46,8448,25000,500
data111,on,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,15,1298.44,66.65,8121,25000,500
data111,on,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,20,1492.98,76.78,13744,25000,500
data111,on,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,17,1364.20,31.03,4499,10000,1026
data111,on,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,16,1399.13,29.67,4126,10000,983
data111,on,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,19,1529.53,34.91,6492,10000,1057
data112,off,Random Walk,relocate,iterations=5000,8,3336.92,6.34,4593,5000,4592
data112,off,Random Walk,relocate+swap,iterations=5000,8,3409.94,5.63,4736,5000,4735
data112,off,Random Walk,relocate+swap+2opt,iterations=5000,8,3643.69,5.11,4924,5000,4923
data112,off,Descent,relocate,iterations=5000,8,1353.61,9.97,4616,5000,219
data112,off,Descent,relocate+swap,iterations=5000,8,1247.81,9.69,4763,5000,198
data112,off,Descent,relocate+swap+2opt,iterations=5000,8,1322.34,9.39,4911,5000,240
data112,off,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1164.96,47.26,16961,25000,500
data112,off,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1166.64,43.19,16699,25000,500
data112,off,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,8,1141.16,43.76,20438,25000,500
data112,off,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1090.70,21.26,9163,10000,1107
data112,off,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1160.29,20.39,9424,10000,946
data112,off,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,8,1133.82,19.94,9872,10000,896
data112,on,Random Walk,relocate,iterations=5000,20,2897.38,12.18,2241,5000,2240
data112,on,Random Walk,relocate+swap,iterations=5000,22,2964.51,11.34,3131,5000,3130
data112,on,Random Walk,relocate+swap+2opt,iterations=5000,21,2916.94,10.64,3531,5000,3530
data112,on,Descent,relocate,iterations=5000,13,1244.56,14.09,2791,5000,260
data112,on,Descent,relocate+swap,iterations=5000,18,1415.01,14.94,3285,5000,249
data112,on,Descent,relocate+swap+2opt,iterations=5000,19,1617.30,15.68,3972,5000,246
data112,on,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,14,1208.30,67.68,11149,25000,500
data112,on,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,14,1270.27,62.85,9672,25000,500
data112,on,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,17,1293.73,73.14,17297,25000,500
data112,on,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,14,1242.62,29.27,4962,10000,1126
data112,on,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,14,1228.75,29.14,5661,10000,985
data112,on,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,16,1363.23,32.04,7846,10000,1198
data1201,off,Random Walk,relocate,iterations=5000,2,4185.75,3.85,4999,5000,4998
data1201,off,Random Walk,relocate+swap,iterations=5000,2,4697.33,3.70,4999,5000,4998
data1201,off,Random Walk,relocate+swap+2opt,iterations=5000,2,4823.65,3.60,5001,5000,5000
data1201,off,Descent,relocate,iterations=5000,2,1278.76,6.63,4995,5000,239
data1201,off,Descent,relocate+swap,iterations=5000,2,1312.33,6.45,4995,5000,228
data1201,off,Descent,relocate+swap+2opt,iterations=5000,2,1187.34,6.39,5000,5000,242
data1201,off,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,1076.66,30.70,19981,25000,500
data1201,off,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,1100.40,28.59,17970,25000,500
data1201,off,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,986.30,29.71,20503,25000,500
data1201,off,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,1192.05,15.00,10000,10000,1004
data1201,off,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,1138.71,13.80,9965,10000,917
data1201,off,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,988.08,14.36,9989,10000,828
data1201,on,Random Walk,relocate,iterations=5000,10,4079.80,10.16,2486,5000,2485
data1201,on,Random Walk,relocate+swap,iterations=5000,14,4950.34,9.98,2719,5000,2718
data1201,on,Random Walk,relocate+swap+2opt,iterations=5000,15,4478.63,10.35,2773,5000,2772
data1201,on,Descent,relocate,iterations=5000,16,1961.86,15.06,2862,5000,227
data1201,on,Descent,relocate+swap,iterations=5000,20,2006.91,16.75,3278,5000,225
data1201,on,Descent,relocate+swap+2opt,iterations=5000,21,2225.29,20.08,3249,5000,237
data1201,on,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,14,1573.02,70.89,11257,25000,500
data1201,on,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,14,1839.20,68.14,9857,25000,500
data1201,on,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,19,1894.56,75.16,12577,25000,500
data1201,on,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,13,1722.53,27.69,5175,10000,1071
data1201,on,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,15,1856.00,28.26,5390,10000,876
data1201,on,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,17,2062.29,31.30,5969,10000,790
data1202,off,Random Walk,relocate,iterations=5000,2,4748.92,3.95,4999,5000,4998
data1202,off,Random Walk,relocate+swap,iterations=5000,2,4501.89,3.67,5000,5000,4999
data1202,off,Random Walk,relocate+swap+2opt,iterations=5000,2,4599.56,3.60,5000,5000,4999
data1202,off,Descent,relocate,iterations=5000,2,1211.66,6.76,4978,5000,232
data1202,off,Descent,relocate+swap,iterations=5000,2,1488.50,6.49,4981,5000,204
data1202,off,Descent,relocate+swap+2opt,iterations=5000,2,1049.84,6.32,5000,5000,242
data1202,off,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,948.64,30.48,20080,25000,500
data1202,off,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,1129.76,34.50,17946,25000,500
data1202,off,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,943.86,30.66,20359,25000,500
data1202,off,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,1054.38,14.35,9965,10000,1024
data1202,off,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,1304.03,13.58,10001,10000,857
data1202,off,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,979.19,13.54,10001,10000,861
data1202,on,Random Walk,relocate,iterations=5000,10,4401.35,9.16,3470,5000,3469
data1202,on,Random Walk,relocate+swap,iterations=5000,11,4631.76,8.69,3373,5000,3372
data1202,on,Random Walk,relocate+swap+2opt,iterations=5000,13,4635.09,8.91,3474,5000,3473
data1202,on,Descent,relocate,iterations=5000,15,1920.24,15.03,3946,5000,208
data1202,on,Descent,relocate+swap,iterations=5000,16,1782.69,16.00,3900,5000,270
data1202,on,Descent,relocate+swap+2opt,iterations=5000,18,2046.87,16.03,3919,5000,243
data1202,on,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,13,1560.79,67.38,14864,25000,500
data1202,on,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,13,1660.23,64.66,12247,25000,500
data1202,on,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,15,1608.31,73.08,15277,25000,500
data1202,on,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,9,1542.31,26.50,7030,10000,1160
data1202,on,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,13,1487.63,26.88,6535,10000,889
data1202,on,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,15,1704.55,30.73,7209,10000,889
data201,off,Random Walk,relocate,iterations=5000,2,3266.13,3.84,4996,5000,4995
data201,off,Random Walk,relocate+swap,iterations=5000,2,3451.60,3.63,5000,5000,4999
data201,off,Random Walk,relocate+swap+2opt,iterations=5000,2,3237.47,3.69,5001,5000,5000
data201,off,Descent,relocate,iterations=5000,2,1145.00,6.68,5000,5000,238
data201,off,Descent,relocate+swap,iterations=5000,2,1189.28,6.46,4998,5000,227
data201,off,Descent,relocate+swap+2opt,iterations=5000,2,1041.60,6.41,5000,5000,232
data201,off,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,969.94,30.51,20002,25000,500
data201,off,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,1082.72,28.56,18087,25000,500
data201,off,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,860.79,29.58,19927,25000,500
data201,off,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,942.45,13.94,10001,10000,1025
data201,off,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,1106.02,13.63,10001,10000,929
data201,off,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,866.94,13.62,10001,10000,892
data201,on,Random Walk,relocate,iterations=5000,11,3205.68,9.88,2512,5000,2511
data201,on,Random Walk,relocate+swap,iterations=5000,12,3489.36,9.05,2540,5000,2539
data201,on,Random Walk,relocate+swap+2opt,iterations=5000,14,3470.98,9.79,2674,5000,2673
data201,on,Descent,relocate,iterations=5000,17,1704.31,15.86,3086,5000,225
data201,on,Descent,relocate+swap,iterations=5000,19,1745.85,16.48,3281,5000,217
data201,on,Descent,relocate+swap+2opt,iterations=5000,22,1914.20,18.13,3325,5000,202
data201,on,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,16,1490.17,72.22,11938,25000,500
data201,on,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,17,1522.22,70.53,10789,25000,500
data201,on,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,18,1586.28,76.59,11686,25000,500
data201,on,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,14,1560.54,28.39,5394,10000,1039
data201,on,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,16,1547.73,29.93,5721,10000,919
data201,on,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,15,1600.93,29.25,5472,10000,817
data202,off,Random Walk,relocate,iterations=5000,2,3541.75,3.83,4998,5000,4997
data202,off,Random Walk,relocate+swap,iterations=5000,2,3329.63,3.63,4999,5000,4998
data202,off,Random Walk,relocate+swap+2opt,iterations=5000,2,3333.61,3.58,5000,5000,4999
data202,off,Descent,relocate,iterations=5000,2,1114.00,6.60,4997,5000,219
data202,off,Descent,relocate+swap,iterations=5000,2,1257.92,6.37,5001,5000,225
data202,off,Descent,relocate+swap+2opt,iterations=5000,2,989.82,6.30,5001,5000,245
data202,off,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,965.33,30.69,19970,25000,500
data202,off,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,1064.80,28.72,18044,25000,500
data202,off,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,2,832.66,29.65,20421,25000,500
data202,off,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,1025.38,14.32,9992,10000,1041
data202,off,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,1122.87,13.71,9999,10000,866
data202,off,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,2,844.48,13.52,9999,10000,934
data202,on,Random Walk,relocate,iterations=5000,8,3345.62,8.51,3602,5000,3601
data202,on,Random Walk,relocate+swap,iterations=5000,11,3486.61,8.35,3447,5000,3446
data202,on,Random Walk,relocate+swap+2opt,iterations=5000,11,3200.49,8.66,3596,5000,3595
data202,on,Descent,relocate,iterations=5000,16,1510.89,14.84,4080,5000,252
data202,on,Descent,relocate+swap,iterations=5000,17,1617.16,15.72,3913,5000,249
data202,on,Descent,relocate+swap+2opt,iterations=5000,21,1833.49,18.35,4155,5000,228
data202,on,Tabu Search,relocate,iterations=500;tabu_tenure=20;attempts_per_iter=50,15,1309.86,68.47,15290,25000,500
data202,on,Tabu Search,relocate+swap,iterations=500;tabu_tenure=20;attempts_per_iter=50,16,1464.36,68.88,13393,25000,500
data202,on,Tabu Search,relocate+swap+2opt,iterations=500;tabu_tenure=20;attempts_per_iter=50,18,1545.39,71.25,15140,25000,500
data202,on,Simulated Annealing,relocate,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,12,1446.96,26.71,7496,10000,1105
data202,on,Simulated Annealing,relocate+swap,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,12,1380.20,26.42,6964,10000,928
data202,on,Simulated Annealing,relocate+swap+2opt,iterations=10000;initial_temp=500.00;cooling_rate=0.9950,16,1662.01,30.24,7752,10000,897"""

# Load data
df = pd.read_csv(io.StringIO(DATA_CSV))

# Convert numeric columns
df['Distance'] = pd.to_numeric(df['Distance'])
df['Time(ms)'] = pd.to_numeric(df['Time(ms)'])
df['Veh'] = pd.to_numeric(df['Veh'])
df['Solutions'] = pd.to_numeric(df['Solutions'])

# Map solver names for shorter labels
solver_color_map = {
    'Random Walk': '#FF6B6B',
    'Descent': '#4ECDC4',
    'Tabu Search': '#D12BD1',
    'Simulated Annealing': '#FFA07A'
}

solver_order = ['Random Walk', 'Descent', 'Tabu Search', 'Simulated Annealing']

# ============================================================================
# PLOT 1: Quality comparison (Distance) by Solver - TW OFF
# ============================================================================
fig, ax = plt.subplots(figsize=(16, 6))

tw_off = df[df['TW'] == 'off']
solver_stats_off = tw_off.groupby('Solver')['Distance'].agg(['mean', 'std']).reindex(solver_order)

x = np.arange(len(solver_order))
width = 0.6
bars = ax.bar(x, solver_stats_off['mean'], width,
              yerr=solver_stats_off['std'],
              capsize=5,
              color=[solver_color_map[s] for s in solver_order],
              alpha=0.8,
              edgecolor='black',
              linewidth=1.5)

ax.set_ylabel('Distance (km)', fontsize=12, fontweight='bold')
ax.set_xlabel('Solver Method', fontsize=12, fontweight='bold')
ax.set_title('Solution Quality Comparison (Distance) - Time Windows OFF\nMean ± Std across all instances & neighborhoods',
             fontsize=13, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(solver_order, fontsize=11)
ax.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (bar, mean, std) in enumerate(zip(bars, solver_stats_off['mean'], solver_stats_off['std'])):
    ax.text(bar.get_x() + bar.get_width()/2, mean + std + 100,
            f'{mean:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('figures/01_quality_by_solver_tw_off.png', dpi=300, bbox_inches='tight')
print("✓ Saved: figures/01_quality_by_solver_tw_off.png")
plt.close()

# ============================================================================
# PLOT 2: Quality comparison by Solver - TW ON
# ============================================================================
fig, ax = plt.subplots(figsize=(16, 6))

tw_on = df[df['TW'] == 'on']
solver_stats_on = tw_on.groupby('Solver')['Distance'].agg(['mean', 'std']).reindex(solver_order)

bars = ax.bar(x, solver_stats_on['mean'], width,
              yerr=solver_stats_on['std'],
              capsize=5,
              color=[solver_color_map[s] for s in solver_order],
              alpha=0.8,
              edgecolor='black',
              linewidth=1.5)

ax.set_ylabel('Distance (km)', fontsize=12, fontweight='bold')
ax.set_xlabel('Solver Method', fontsize=12, fontweight='bold')
ax.set_title('Solution Quality Comparison (Distance) - Time Windows ON\nMean ± Std across all instances & neighborhoods',
             fontsize=13, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(solver_order, fontsize=11)
ax.grid(axis='y', alpha=0.3)

for i, (bar, mean, std) in enumerate(zip(bars, solver_stats_on['mean'], solver_stats_on['std'])):
    ax.text(bar.get_x() + bar.get_width()/2, mean + std + 100,
            f'{mean:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('figures/02_quality_by_solver_tw_on.png', dpi=300, bbox_inches='tight')
print("✓ Saved: figures/02_quality_by_solver_tw_on.png")
plt.close()

# ============================================================================
# PLOT 3: Speed comparison (Execution Time) by Solver
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for idx, (ax, tw, title_suffix) in enumerate([(axes[0], 'off', 'TW OFF'),
                                                (axes[1], 'on', 'TW ON')]):
    data = df[df['TW'] == tw]
    time_stats = data.groupby('Solver')['Time(ms)'].agg(['mean', 'std']).reindex(solver_order)

    bars = ax.bar(x, time_stats['mean'], width,
                  yerr=time_stats['std'],
                  capsize=5,
                  color=[solver_color_map[s] for s in solver_order],
                  alpha=0.8,
                  edgecolor='black',
                  linewidth=1.5)

    ax.set_ylabel('Execution Time (ms)', fontsize=11, fontweight='bold')
    ax.set_xlabel('Solver Method', fontsize=11, fontweight='bold')
    ax.set_title(f'Execution Speed Comparison - {title_suffix}', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(solver_order, fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    for bar, mean, std in zip(bars, time_stats['mean'], time_stats['std']):
        ax.text(bar.get_x() + bar.get_width()/2, mean + std + 2,
                f'{mean:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('figures/03_speed_by_solver.png', dpi=300, bbox_inches='tight')
print("✓ Saved: figures/03_speed_by_solver.png")
plt.close()

# ============================================================================
# PLOT 4: Pareto Frontier - Quality vs Speed (TW OFF)
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 8))

tw_off_data = df[df['TW'] == 'off'].copy()
for solver in solver_order:
    solver_data = tw_off_data[tw_off_data['Solver'] == solver]
    ax.scatter(solver_data['Time(ms)'], solver_data['Distance'],
              s=150, label=solver, alpha=0.7, edgecolors='black', linewidth=1.5,
              color=solver_color_map[solver])

ax.set_xlabel('Execution Time (ms)', fontsize=12, fontweight='bold')
ax.set_ylabel('Distance (km)', fontsize=12, fontweight='bold')
ax.set_title('Pareto Frontier: Quality vs Speed Trade-off (TW OFF)\nEach point = one configuration (solver + neighborhood)',
             fontsize=13, fontweight='bold', pad=20)
ax.legend(fontsize=11, loc='best')
ax.grid(alpha=0.3)

# Highlight Pareto optimal solutions
tw_off_data_sorted = tw_off_data.sort_values('Time(ms)')
pareto_front = []
for idx, row in tw_off_data_sorted.iterrows():
    if not any((pareto_front_row['Distance'] < row['Distance']) for pareto_front_row in pareto_front):
        pareto_front.append(row)

pareto_times = [r['Time(ms)'] for r in pareto_front]
pareto_dists = [r['Distance'] for r in pareto_front]
ax.plot(pareto_times, pareto_dists, 'r--', linewidth=2, alpha=0.5, label='Pareto frontier')

plt.tight_layout()
plt.savefig('figures/04_pareto_frontier_tw_off.png', dpi=300, bbox_inches='tight')
print("✓ Saved: figures/04_pareto_frontier_tw_off.png")
plt.close()

# ============================================================================
# PLOT 5: Pareto Frontier - Quality vs Speed (TW ON)
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 8))

tw_on_data = df[df['TW'] == 'on'].copy()
for solver in solver_order:
    solver_data = tw_on_data[tw_on_data['Solver'] == solver]
    ax.scatter(solver_data['Time(ms)'], solver_data['Distance'],
              s=150, label=solver, alpha=0.7, edgecolors='black', linewidth=1.5,
              color=solver_color_map[solver])

ax.set_xlabel('Execution Time (ms)', fontsize=12, fontweight='bold')
ax.set_ylabel('Distance (km)', fontsize=12, fontweight='bold')
ax.set_title('Pareto Frontier: Quality vs Speed Trade-off (TW ON)\nEach point = one configuration (solver + neighborhood)',
             fontsize=13, fontweight='bold', pad=20)
ax.legend(fontsize=11, loc='best')
ax.grid(alpha=0.3)

# Highlight Pareto optimal solutions
tw_on_data_sorted = tw_on_data.sort_values('Time(ms)')
pareto_front = []
for idx, row in tw_on_data_sorted.iterrows():
    if not any((pareto_front_row['Distance'] < row['Distance']) for pareto_front_row in pareto_front):
        pareto_front.append(row)

pareto_times = [r['Time(ms)'] for r in pareto_front]
pareto_dists = [r['Distance'] for r in pareto_front]
ax.plot(pareto_times, pareto_dists, 'r--', linewidth=2, alpha=0.5, label='Pareto frontier')

plt.tight_layout()
plt.savefig('figures/05_pareto_frontier_tw_on.png', dpi=300, bbox_inches='tight')
print("✓ Saved: figures/05_pareto_frontier_tw_on.png")
plt.close()

# ============================================================================
# PLOT 6: Impact of Neighborhoods on Solution Quality
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

neighborhood_order = ['relocate', 'relocate+swap', 'relocate+swap+2opt']
neighborhood_colors = {'relocate': '#FFB6C1', 'relocate+swap': '#87CEEB', 'relocate+swap+2opt': '#90EE90'}

for idx, (ax, tw, title) in enumerate([(axes[0], 'off', 'TW OFF'), (axes[1], 'on', 'TW ON')]):
    data = df[df['TW'] == tw]
    neighbor_stats = data.groupby('Neighbor')['Distance'].agg(['mean', 'std']).reindex(neighborhood_order)

    x_neigh = np.arange(len(neighborhood_order))
    bars = ax.bar(x_neigh, neighbor_stats['mean'], 0.6,
                  yerr=neighbor_stats['std'],
                  capsize=5,
                  color=[neighborhood_colors[n] for n in neighborhood_order],
                  alpha=0.8,
                  edgecolor='black',
                  linewidth=1.5)

    ax.set_ylabel('Distance (km)', fontsize=11, fontweight='bold')
    ax.set_title(f'Neighborhood Impact on Solution Quality - {title}', fontsize=12, fontweight='bold')
    ax.set_xticks(x_neigh)
    ax.set_xticklabels(neighborhood_order, fontsize=10, rotation=15, ha='right')
    ax.grid(axis='y', alpha=0.3)

    for bar, mean, std in zip(bars, neighbor_stats['mean'], neighbor_stats['std']):
        ax.text(bar.get_x() + bar.get_width()/2, mean + std + 100,
                f'{mean:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('figures/06_neighborhood_impact.png', dpi=300, bbox_inches='tight')
print("✓ Saved: figures/06_neighborhood_impact.png")
plt.close()

# ============================================================================
# PLOT 7: Box plot - Distribution of distances by solver (TW OFF)
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

tw_off_data = df[df['TW'] == 'off'].copy()
tw_off_data['Solver'] = pd.Categorical(tw_off_data['Solver'], categories=solver_order, ordered=True)
tw_off_data = tw_off_data.sort_values('Solver')

bp = ax.boxplot([tw_off_data[tw_off_data['Solver'] == s]['Distance'].values for s in solver_order],
                  labels=solver_order,
                  patch_artist=True,
                  notch=False,
                  widths=0.6)

for patch, solver in zip(bp['boxes'], solver_order):
    patch.set_facecolor(solver_color_map[solver])
    patch.set_alpha(0.7)

ax.set_ylabel('Distance (km)', fontsize=12, fontweight='bold')
ax.set_title('Solution Quality Distribution by Solver (TW OFF)\nBox plot showing median, quartiles, and outliers',
             fontsize=13, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)
plt.xticks(fontsize=11)
plt.tight_layout()
plt.savefig('figures/07_boxplot_quality_tw_off.png', dpi=300, bbox_inches='tight')
print("✓ Saved: figures/07_boxplot_quality_tw_off.png")
plt.close()

# ============================================================================
# PLOT 8: Box plot - Distribution of distances by solver (TW ON)
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

tw_on_data = df[df['TW'] == 'on'].copy()
tw_on_data['Solver'] = pd.Categorical(tw_on_data['Solver'], categories=solver_order, ordered=True)
tw_on_data = tw_on_data.sort_values('Solver')

bp = ax.boxplot([tw_on_data[tw_on_data['Solver'] == s]['Distance'].values for s in solver_order],
                  labels=solver_order,
                  patch_artist=True,
                  notch=False,
                  widths=0.6)

for patch, solver in zip(bp['boxes'], solver_order):
    patch.set_facecolor(solver_color_map[solver])
    patch.set_alpha(0.7)

ax.set_ylabel('Distance (km)', fontsize=12, fontweight='bold')
ax.set_title('Solution Quality Distribution by Solver (TW ON)\nBox plot showing median, quartiles, and outliers',
             fontsize=13, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)
plt.xticks(fontsize=11)
plt.tight_layout()
plt.savefig('figures/08_boxplot_quality_tw_on.png', dpi=300, bbox_inches='tight')
print("✓ Saved: figures/08_boxplot_quality_tw_on.png")
plt.close()

# ============================================================================
# PLOT 9: Vehicles Used by Solver
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for idx, (ax, tw, title) in enumerate([(axes[0], 'off', 'TW OFF'), (axes[1], 'on', 'TW ON')]):
    data = df[df['TW'] == tw]
    veh_stats = data.groupby('Solver')['Veh'].agg(['mean', 'std']).reindex(solver_order)

    bars = ax.bar(x, veh_stats['mean'], width,
                  yerr=veh_stats['std'],
                  capsize=5,
                  color=[solver_color_map[s] for s in solver_order],
                  alpha=0.8,
                  edgecolor='black',
                  linewidth=1.5)

    ax.set_ylabel('Number of Vehicles', fontsize=11, fontweight='bold')
    ax.set_title(f'Average Vehicles Used - {title}', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(solver_order, fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    for bar, mean, std in zip(bars, veh_stats['mean'], veh_stats['std']):
        ax.text(bar.get_x() + bar.get_width()/2, mean + std + 0.5,
                f'{mean:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('figures/09_vehicles_used.png', dpi=300, bbox_inches='tight')
print("✓ Saved: figures/09_vehicles_used.png")
plt.close()

# ============================================================================
# PLOT 10: Acceptance Rate (Neighbors Accepted / Attempted)
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

df['AcceptanceRate'] = (df['NeighborsAccepted'] / df['NeighborsAttempted'] * 100)

for idx, (ax, tw, title) in enumerate([(axes[0], 'off', 'TW OFF'), (axes[1], 'on', 'TW ON')]):
    data = df[df['TW'] == tw]
    accept_stats = data.groupby('Solver')['AcceptanceRate'].agg(['mean', 'std']).reindex(solver_order)

    bars = ax.bar(x, accept_stats['mean'], width,
                  yerr=accept_stats['std'],
                  capsize=5,
                  color=[solver_color_map[s] for s in solver_order],
                  alpha=0.8,
                  edgecolor='black',
                  linewidth=1.5)

    ax.set_ylabel('Acceptance Rate (%)', fontsize=11, fontweight='bold')
    ax.set_title(f'Move Acceptance Rate - {title}', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(solver_order, fontsize=10)
    ax.set_ylim([0, 105])
    ax.grid(axis='y', alpha=0.3)

    for bar, mean, std in zip(bars, accept_stats['mean'], accept_stats['std']):
        ax.text(bar.get_x() + bar.get_width()/2, mean + std + 2,
                f'{mean:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('figures/10_acceptance_rate.png', dpi=300, bbox_inches='tight')
print("✓ Saved: figures/10_acceptance_rate.png")
plt.close()

print("\n✅ All plots generated successfully!")
print("\nGenerated files:")
print("  1. 01_quality_by_solver_tw_off.png - Mean distance (TW OFF)")
print("  2. 02_quality_by_solver_tw_on.png - Mean distance (TW ON)")
print("  3. 03_speed_by_solver.png - Execution time comparison")
print("  4. 04_pareto_frontier_tw_off.png - Quality vs Speed trade-off (TW OFF)")
print("  5. 05_pareto_frontier_tw_on.png - Quality vs Speed trade-off (TW ON)")
print("  6. 06_neighborhood_impact.png - Neighborhood effects")
print("  7. 07_boxplot_quality_tw_off.png - Distribution TW OFF")
print("  8. 08_boxplot_quality_tw_on.png - Distribution TW ON")
print("  9. 09_vehicles_used.png - Vehicle count by solver")
print(" 10. 10_acceptance_rate.png - Move acceptance rates")
