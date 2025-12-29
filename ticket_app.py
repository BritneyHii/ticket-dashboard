import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt

# 设置页面配置
st.set_page_config(
    page_title="用户反馈工单看板",
    page_icon="📊",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1E3A8A;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

def create_sample_data():
    """创建示例数据"""
    # 创建基础数据
    dates = pd.date_range('2025-12-19', periods=20, freq='D')
    
    data = pd.DataFrame({
        '日期': dates,
        '分校': ['US', 'UK', 'CA', 'SG', 'HK'] * 4,
        '问题类型': ['课堂', '课后', '售后'] * 6 + ['售前', '售前'],
        '状态': ['已解决', '处理中', '待处理'] * 6 + ['已解决', '已解决'],
        '影响人数': [1, 2, 1, 1, 3, 2, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1],
        '响应级别': ['P2', 'P1', 'P2', 'P3', 'P1', 'P2', 'P3', 'P2', 'P2', 'P1', 
                   'P3', 'P2', 'P2', 'P1', 'P3', 'P2', 'P2', 'P3', 'P1', 'P2'],
        '所属团队': ['前端', '服务端', '教务', '前端', '服务端'] * 4,
        '问题描述': [
            'APP闪退', '加入频道失败', '音视频问题', '涂鸦问题', '课件异常',
            '回放卡顿', '作业提交失败', '支付失败', '验证码收不到', '课表为空',
            '学员看不到主讲', '主讲看不到学员', '游戏卡住', '课件打包失败', '用户不支持webgl',
            '涂鸦同步延迟', '信令慢', '断网重连失败', '回声问题', '游戏加载失败'
        ]
    })
    
    return data

def main():
    """主函数"""
    st.markdown('<div class="main-header">📊 用户反馈工单看板</div>', unsafe_allow_html=True)
    
    # 创建数据
    data = create_sample_data()
    
    # 侧边栏筛选器
    st.sidebar.header("🔍 筛选器")
    
    # 日期范围筛选
    min_date = data['日期'].min().date()
    max_date = data['日期'].max().date()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("开始日期", min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("结束日期", max_date, min_value=min_date, max_value=max_date)
    
    # 其他筛选器
    selected_branch = st.sidebar.multiselect(
        "分校",
        options=sorted(data['分校'].unique()),
        default=sorted(data['分校'].unique())
    )
    
    selected_status = st.sidebar.multiselect(
        "状态",
        options=sorted(data['状态'].unique()),
        default=sorted(data['状态'].unique())
    )
    
    selected_priority = st.sidebar.multiselect(
        "优先级",
        options=sorted(data['响应级别'].unique()),
        default=sorted(data['响应级别'].unique())
    )
    
    # 应用筛选
    filtered_data = data[
        (data['日期'].dt.date >= start_date) &
        (data['日期'].dt.date <= end_date) &
        (data['分校'].isin(selected_branch)) &
        (data['状态'].isin(selected_status)) &
        (data['响应级别'].isin(selected_priority))
    ]
    
    # 计算指标
    total_issues = len(filtered_data)
    resolved_issues = len(filtered_data[filtered_data['状态'] == '已解决'])
    affected_users = int(filtered_data['影响人数'].sum())
    resolution_rate = round(resolved_issues / total_issues * 100, 2) if total_issues > 0 else 0
    
    # 显示KPI卡片
    st.markdown("### 📊 核心指标")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.9rem; color: #666;">问题总数</div>
            <div class="metric-value">{total_issues}</div>
            <div style="font-size: 0.8rem; color: #666;">筛选结果</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.9rem; color: #666;">已解决</div>
            <div class="metric-value">{resolved_issues}</div>
            <div style="font-size: 0.8rem; color: #666;">解决率: {resolution_rate}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.9rem; color: #666;">影响人数</div>
            <div class="metric-value">{affected_users}</div>
            <div style="font-size: 0.8rem; color: #666;">平均影响: {round(affected_users/total_issues, 1) if total_issues>0 else 0}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        p1_issues = len(filtered_data[filtered_data['响应级别'] == 'P1'])
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.9rem; color: #666;">P1问题</div>
            <div class="metric-value">{p1_issues}</div>
            <div style="font-size: 0.8rem; color: #666;">高优先级</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["📈 图表分析", "📋 数据明细", "⚠️ 重点关注"])
    
    with tab1:
        # 问题类型分布
        st.subheader("问题类型分布")
        
        # 使用Altair创建图表
        chart_data = filtered_data['问题类型'].value_counts().reset_index()
        chart_data.columns = ['问题类型', '数量']
        
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('问题类型', sort='-y'),
            y='数量',
            color=alt.Color('问题类型', legend=None)
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
        
        # 团队分布
        st.subheader("团队问题分布")
        team_data = filtered_data['所属团队'].value_counts().reset_index()
        team_data.columns = ['团队', '数量']
        
        team_chart = alt.Chart(team_data).mark_arc().encode(
            theta='数量',
            color='团队',
            tooltip=['团队', '数量']
        ).properties(height=300)
        
        st.altair_chart(team_chart, use_container_width=True)
    
    with tab2:
        st.subheader("工单明细")
        
        # 格式化显示
        display_data = filtered_data.copy()
        display_data['日期'] = display_data['日期'].dt.strftime('%Y-%m-%d')
        
        # 重新排序列
        display_data = display_data[['日期', '分校', '问题类型', '状态', '响应级别', 
                                   '影响人数', '所属团队', '问题描述']]
        
        st.dataframe(
            display_data,
            use_container_width=True,
            height=400
        )
        
        # 导出按钮
        csv = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 导出数据 (CSV)",
            data=csv,
            file_name=f"工单数据_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.subheader("高优先级问题 (P1)")
        
        p1_data = filtered_data[filtered_data['响应级别'] == 'P1']
        
        if len(p1_data) > 0:
            for idx, row in p1_data.iterrows():
                with st.expander(f"📌 {row['问题描述']} (影响: {row['影响人数']}人)"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("分校", row['分校'])
                    col2.metric("问题类型", row['问题类型'])
                    col3.metric("状态", row['状态'])
                    st.write(f"**详细描述**: {row['问题描述']}")
        else:
            st.info("当前无P1级别问题")
        
        # 高影响问题
        st.subheader("高影响问题 (影响人数≥3)")
        high_impact = filtered_data[filtered_data['影响人数'] >= 3]
        
        if len(high_impact) > 0:
            st.dataframe(
                high_impact[['日期', '分校', '问题描述', '影响人数', '状态']],
                use_container_width=True
            )
        else:
            st.info("当前无高影响问题")
    
    # 页脚信息
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**数据更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    with col2:
        st.write(f"**当前显示记录数**: {len(filtered_data)}")

if __name__ == "__main__":
    main()
