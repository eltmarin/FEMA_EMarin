#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 09:36:12 2022

@author: liz
"""
#This script looks various variables of interest and produces histograms at the county and zipcode level.
#This script also produces two bins for comparing white and non-white populations' distributions.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

files = ['census_info_zips', 'census_info_fips']

for file in files:
    fh = pd.read_csv(file+'.csv')
    fh['more_white'] = fh['pct_white']
    more_white = fh['more_white']>=0.5
    more_white = more_white.replace ({False: 'No', True:'Yes'})
    #what this means is that where the pct_white is more than 50 it is a Yes
    #where pct_white is less than 50 it is a no
    var = ['approved_rate','application_per_thousand', 'median_income', 'average_project']
    for v in var:
        fig, ax1 = plt.subplots()
        print (file,v)
        sns.histplot(data=fh,x=v,hue=more_white,kde=True, ax=ax1)
        fig.tight_layout()
        fig.savefig(f'{file}_{v}.png')
