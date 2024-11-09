# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 00:27:36 2024

@author: wooji
"""

import streamlit as st
import pandas as pd
import numpy as np

# 定义标准化采样深度的函数
def standardize_sampling_depth(df):
    new_intervals = [f'{i}-{i+0.5}' for i in np.arange(0, 15.5, 0.5)]

    
    def find_closest_interval(midpoint):
        return min(new_intervals, key=lambda x: abs((float(x.split('-')[0]) + float(x.split('-')[1])) / 2 - midpoint))
    
    df['采样深度（m）_标准化'] = df['采样深度（m）'].apply(lambda x: find_closest_interval((float(x.split('-')[0]) + float(x.split('-')[1])) / 2))
    return df

# 定义计算统计量的函数
def calculate_statistics(grouped_df, pollutant):
    stats = grouped_df[pollutant].agg([
        'mean', 
        lambda x: np.percentile(x.dropna(), 5), 
        lambda x: np.percentile(x.dropna(), 25), 
        lambda x: np.percentile(x.dropna(), 50), 
        lambda x: np.percentile(x.dropna(), 75), 
        lambda x: np.percentile(x.dropna(), 95), 
        'max', 
        'count'
    ])
    stats.columns = ['平均值', '5%', '25%', '50%', '75%', '95%', '最大值', '样本量']

    # 计算检出率
    detection_rate = grouped_df[pollutant].apply(lambda x: x.notna().sum() / len(x) * 100)
    stats['检出率'] = detection_rate

    return stats

# Streamlit应用
st.title("土壤污染物数据分析工具")

# 文件上传
uploaded_file = st.file_uploader("上传Excel文件", type=["xlsx"])

if uploaded_file is not None:
    # 读取Excel文件
    df = pd.read_excel(uploaded_file)

    # 将 "ND" 替换为 NaN
    df.replace('ND', np.nan, inplace=True)

    # 标准化采样深度
    df_standardized = standardize_sampling_depth(df)

    # 选择污染物
    pollutants = df_standardized.columns.difference(['采样深度（m）', '采样深度（m）_标准化'])
    selected_pollutant = st.selectbox("选择污染物", pollutants)

    # 按标准化后的采样深度分组
    grouped_df = df_standardized.groupby('采样深度（m）_标准化')

    # 计算统计量
    stats = calculate_statistics(grouped_df, selected_pollutant)

    # 显示结果
    st.write(f"### {selected_pollutant} 的统计结果")
    st.dataframe(stats)