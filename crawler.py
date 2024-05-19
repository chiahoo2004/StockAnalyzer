#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 21:58:53 2023

@author: chiahoo2004
"""

# https://www.finlab.tw/one-line-info-dataframe/

import datetime
import pandas as pd
import warnings
import requests
from io import StringIO
#import pandas_profiling

def crawler(date):
    datestr = date.strftime('%Y%m%d')
    url = 'https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date='+datestr+'&selectType=ALL'
    print(url)
    res = requests.get(url)
    df = pd.read_csv(StringIO(res.text), header=1)
    df['本益比'] = pd.to_numeric(df['本益比'], errors='coerce')
    
    return df.dropna(thresh=3).dropna(thresh=0.8, axis=1)


df = crawler(datetime.date(2023,12,7))
df = df.head()

