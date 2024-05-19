#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 21:12:45 2023

@author: chiahoo2004
"""
import sys
import datetime
import pandas as pd
from crawler import crawler
from monthly_report import monthly_report
# from price import stock_crawler

## Threshold
PE_ratio = 10.0
Yield = 7.0
YoY = 20.0

df_stat = crawler(datetime.date(2022,12,7))
df_stat = df_stat.rename(columns={'殖利率(%)':'殖利率'})
df_PE_ratio = df_stat[['證券名稱','本益比']]
df_yield = df_stat[['證券名稱','殖利率']]
df_PB_ratio = df_stat[['證券名稱','股價淨值比']]
date_iter = pd.date_range('2022-12-5', periods = 11, freq='MS')
for date in date_iter:
    year = date.year
    month = date.month
    day = date.day
    print(year, month, day)
    try:
        df_stat_next = crawler(datetime.date(year,month,day))
        df_PE_ratio = pd.merge(df_PE_ratio, df_stat_next[['證券名稱', '本益比']], how='outer', on='證券名稱')
        df_yield = pd.merge(df_yield, df_stat_next[['證券名稱', '殖利率(%)']], how='outer', on='證券名稱')
        df_PB_ratio = pd.merge(df_PB_ratio, df_stat_next[['證券名稱', '股價淨值比']], how='outer', on='證券名稱')
    except:
        print("no data on: ", year, month, day)

df_stat = df_stat.rename(columns={'證券代號':'公司 代號', '證券名稱':'公司名稱'})
df_stat = df_stat[['公司 代號', '公司名稱', '殖利率', '本益比', '股價淨值比']]
df_PE_ratio = df_PE_ratio[list(df_PE_ratio.filter(regex='本益比'))].mean(axis=1)
df_yield = df_yield[list(df_yield.filter(regex='殖利率'))].mean(axis=1)
df_PB_ratio = df_PB_ratio[list(df_PB_ratio.filter(regex='股價淨值比'))].mean(axis=1)
df_stat['本益比'] = df_PE_ratio
df_stat['殖利率'] = df_yield
df_stat['股價淨值比'] = df_PB_ratio



df_report = monthly_report(111,12)
df_revenue = df_report[['公司 代號', '公司名稱', '當月營收']]
df_revenue_lastyear = df_report[['公司名稱', '去年當月營收']]
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
df_stat = pd.merge(df_stat, df_revenue[['公司名稱', '年營收成長(%)']], how='outer', on='公司名稱')


df_summary = pd.read_csv("t51sb01_20240217_221813744.csv_utf8.csv", header=None)
df_share = df_summary.iloc[:, [0, 17]]
df_share.rename(columns = {0: '公司 代號'}, inplace = True)
df_share.rename(columns = {17: '發行股數'}, inplace = True)
df_share['公司 代號'] = df_share['公司 代號'].apply(str)
df_revenue = pd.merge(df_revenue, df_share, how='outer', on='公司 代號')
df_revenue['EPS'] = df_revenue['當月營收'] * 12 / df_revenue['發行股數']


#stock_list = ['1101','1102','1103','2330']
#df = stock_crawler(stock_list,)
#df_revenue['本益比'] = 股價 / df_revenue['EPS']


df_stat['彼得數字'] = (df_stat['年營收成長(%)']+df_stat['殖利率'])/(df_stat['本益比'])
#df_result = df_stat.loc[(df_stat['本益比'] <= PE_ratio) & (df_stat['殖利率(%)'] >= Yield) & (df_stat['年營收成長(%)'] >= YoY)]
df_result = df_stat.loc[df_stat['彼得數字'] > 1.6]


date_time = datetime.datetime.now().strftime("%Y%m%d")
df_result.to_csv('result_'+date_time+'.csv', encoding = 'utf-8',index = False)
