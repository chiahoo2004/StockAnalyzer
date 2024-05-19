#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 21:12:45 2023

@author: chiahoo2004
"""

import datetime
import pandas as pd
from crawler import crawler
from monthly_report import monthly_report

## Threshold
PE_ratio = 10.0
Yield = 7.0
YoY = 20.0

df_summary = crawler(datetime.date(2023,12,7))
df_summary = df_summary.rename(columns={'證券代號':'公司 代號', '證券名稱':'公司名稱'})
df_summary = df_summary[['公司名稱', '殖利率(%)', '本益比', '股價淨值比']]

df_report = monthly_report(111,12)
df_revenue = df_report[['公司名稱', '當月營收']]
df_revenue_lastyear = df_report[['公司名稱', '去年當月營收']]
date_iter = pd.date_range('2022-12-5', periods = 11, freq='MS')

for date in date_iter:
    year = date.year - 1911
    month = date.month
    day = date.day
    print(year, month, day)
    
    df_report_next = monthly_report(year, month)
    df_revenue_next = df_report_next[['公司名稱', '當月營收']]
    df_revenue_next = df_revenue_next.rename(columns={'當月營收':'當月營收_'+str(month)})
    df_revenue_lastyear_next = df_report_next[['公司名稱', '去年當月營收']]
    df_revenue_lastyear_next = df_revenue_lastyear_next.rename(columns={'去年當月營收':'去年當月營收_'+str(month)})
    
    df_revenue = pd.merge(df_revenue, df_revenue_next, how='outer', on='公司名稱')
    df_revenue_lastyear = pd.merge(df_revenue_lastyear, df_revenue_lastyear_next, how='outer', on='公司名稱')
    
df_revenue['年度營收']= df_revenue[list(df_revenue.filter(regex='當月營收'))].sum(axis=1)
df_revenue_lastyear['去年年度營收']= df_revenue_lastyear[list(df_revenue_lastyear.filter(regex='去年當月營收'))].sum(axis=1)

df_revenue['年營收成長(%)'] = 100*(df_revenue['年度營收'] - df_revenue_lastyear['去年年度營收'])/(df_revenue_lastyear['去年年度營收'])

df_summary = pd.merge(df_summary, df_revenue[['公司名稱', '年營收成長(%)']], how='outer', on='公司名稱')
df_summary['彼得數字'] = (df_summary['年營收成長(%)']+df_summary['殖利率(%)'])/(df_summary['本益比'])
#df_result = df_summary.loc[(df_summary['本益比'] <= PE_ratio) & (df_summary['殖利率(%)'] >= Yield) & (df_summary['年營收成長(%)'] >= YoY)]
df_result = df_summary.loc[df_summary['彼得數字'] > 1.6]

