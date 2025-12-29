import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="工单看板", layout="wide")

# 创建示例数据
data = pd.DataFrame({
    '日期': pd.date_range('2025-12-19', periods=20),
    '分校': ['US', 'UK', 'CA', 'SG', 'HK'] * 4,
    '问题类型': ['课堂', '课后', '售后'] * 6 + ['售前', '售前'],
    '状态': ['已解决', '处理中', '待处理'] * 6 + ['已解决', '已解决'],
    '影响人数': [1, 2, 1, 1, 3, 2, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1]
})

st.title("📊 极简工单看板")

# 筛选器
st.sidebar.header("筛选器")
selected_branch = st.sidebar.multiselect("分校", options=data['分校'].unique(), default=data['分校'].unique())
selected_status = st.sidebar.multiselect("状态", options=data['状态'].unique(), default=data['状态'].unique())

# 应用筛选
filtered_data = data[
    (data['分校'].isin(selected_branch)) &
    (data['状态'].isin(selected_status))
]

# 显示指标
col1, col2, col3, col4 = st.columns(4)
col1.metric("问题总数", len(filtered_data))
col2.metric("影响人数", int(filtered_data['影响人数'].sum()))
col3.metric("已解决", len(filtered_data[filtered_data['状态']=='已解决']))
col4.metric("解决率", f"{len(filtered_data[filtered_data['状态']=='已解决'])/len(filtered_data)*100:.1f}%")

# 显示图表
st.subheader("问题分类分布")
st.bar_chart(filtered_data['问题类型'].value_counts())

st.subheader("工单列表")
st.dataframe(filtered_data, use_container_width=True)

st.success("✅ 看板加载成功！")
