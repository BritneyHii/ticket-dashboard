# ticket_app.py - 无外部依赖版本
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

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
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1E3A8A;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .issue-p1 {
        background-color: #FEE2E2 !important;
        border-left: 4px solid #EF4444 !important;
    }
    .issue-p2 {
        background-color: #FEF3C7 !important;
        border-left: 4px solid #F59E0B !important;
    }
    .issue-p3 {
        background-color: #E0E7FF !important;
        border-left: 4px solid #6366F1 !important;
    }
</style>
""", unsafe_allow_html=True)

def create_sample_data():
    """创建示例数据"""
    data = []
    
    # 问题分类
    categories = {
        '课堂': ['音视频问题', 'APP闪退', '互动逻辑', '涂鸦/板书'],
        '课后': ['回放录制', '作业/考试', '其他App模块问题'],
        '售后': ['其他业务后台问题', '调课转班'],
        '售前': ['诊断', '支付'],
        'ThinkZone': ['相关问题']
    }
    
    # 分校
    branches = ['US', 'UK', 'CA', 'MYS', 'SG', 'HK', 'AUS', 'KR', 'GMC', 'JP', 'FR']
    
    # 创建35条数据（与周报一致）
    for i in range(35):
        date = datetime(2025, 12, 19) + timedelta(days=i%7)
        branch = random.choice(branches)
        
        # 随机选择分类
        main_cat = random.choice(list(categories.keys()))
        sub_cat = random.choice(categories[main_cat])
        
        # 问题状态
        status = random.choice(['已解决', '排查中', '走排期', '待验证', '无法定位'])
        
        # 优先级
        priority = random.choice(['P1', 'P2', 'P3'])
        
        # 影响人数
        if priority == 'P1':
            affected = random.choice([3, 4, 5, 6])
        else:
            affected = random.choice([1, 2, 1, 1, 2])
        
        # 团队
        team = random.choice(['前端', '服务端', '教务', '声网服务'])
        
        # 问题描述
        descriptions = [
            'APP闪退导致无法上课',
            '加入频道失败，无法进入课堂',
            '学生听不到老师声音',
            '回放视频卡顿，重复播放',
            '涂鸦同步延迟，教师端看不到',
            '作业提交失败',
            '支付页面显示异常',
            '验证码收不到',
            '课表为空，没有教室入口',
            '课件加载失败'
        ]
        
        data.append({
            '发生日期': date,
            '分校': branch,
            '问题分类': f'{main_cat}/{sub_cat}',
            '状态': status,
            '优先级': priority,
            '影响人数': affected,
            '所属团队': team,
            '问题描述': random.choice(descriptions),
            '是否有效': '是',
            'IT拦截': '是' if i < 14 else '否'
        })
    
    return pd.DataFrame(data)

def main():
    """主函数"""
    st.markdown('<div class="main-header">📊 用户反馈工单看板</div>', unsafe_allow_html=True)
    st.caption("数据时间范围: 2025-12-19 至 2025-12-25")
    
    # 加载数据
    df = create_sample_data()
    
    # 侧边栏筛选器
    st.sidebar.header("🔍 筛选器")
    
    # 日期筛选
    min_date = df['发生日期'].min().date()
    max_date = df['发生日期'].max().date()
    
    date_range = st.sidebar.date_input(
        "日期范围",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # 分校筛选
    branches = st.sidebar.multiselect(
        "选择分校",
        options=sorted(df['分校'].unique()),
        default=['US', 'UK', 'CA']
    )
    
    # 优先级筛选
    priorities = st.sidebar.multiselect(
        "选择优先级",
        options=sorted(df['优先级'].unique()),
        default=['P1', 'P2', 'P3']
    )
    
    # 状态筛选
    statuses = st.sidebar.multiselect(
        "选择状态",
        options=sorted(df['状态'].unique()),
        default=sorted(df['状态'].unique())
    )
    
    # 应用筛选
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[
            (df['发生日期'].dt.date >= start_date) &
            (df['发生日期'].dt.date <= end_date)
        ]
    else:
        filtered_df = df.copy()
    
    filtered_df = filtered_df[
        (filtered_df['分校'].isin(branches)) &
        (filtered_df['优先级'].isin(priorities)) &
        (filtered_df['状态'].isin(statuses))
    ]
    
    # 计算指标
    total_issues = len(filtered_df)
    valid_issues = len(filtered_df[filtered_df['是否有效'] == '是'])
    affected_users = filtered_df['影响人数'].sum()
    resolved_issues = len(filtered_df[filtered_df['状态'] == '已解决'])
    resolution_rate = round(resolved_issues / total_issues * 100, 2) if total_issues > 0 else 0
    it_intercepted = len(filtered_df[filtered_df['IT拦截'] == '是'])
    
    # 显示KPI卡片
    st.markdown("### 📊 核心指标")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("问题总数", total_issues, delta="-12" if total_issues < 47 else None)
    
    with col2:
        st.metric("有效问题", valid_issues, f"{round(valid_issues/total_issues*100,1)}%")
    
    with col3:
        st.metric("解决率", f"{resolution_rate}%", "+5%" if resolution_rate > 85 else None)
    
    with col4:
        st.metric("影响人数", int(affected_users))
    
    with col5:
        st.metric("IT拦截", it_intercepted)
    
    # 显示筛选信息
    st.write(f"**当前筛选结果**: {len(filtered_df)} 条记录 | **影响总人数**: {int(affected_users)}")
    
    # 使用标签页组织内容
    tab1, tab2, tab3, tab4 = st.tabs(["📈 趋势分析", "📊 数据分布", "⚠️ 重点问题", "📋 工单列表"])
    
    with tab1:
        # 按日期统计
        st.subheader("每日问题数量趋势")
        daily_counts = filtered_df.groupby(filtered_df['发生日期'].dt.date).size()
        st.line_chart(daily_counts)
        
        # 问题分类趋势
        st.subheader("问题分类趋势")
        category_counts = filtered_df['问题分类'].apply(lambda x: x.split('/')[0]).value_counts()
        st.bar_chart(category_counts)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("分校问题分布")
            branch_counts = filtered_df['分校'].value_counts()
            st.bar_chart(branch_counts)
        
        with col2:
            st.subheader("团队问题分布")
            team_counts = filtered_df['所属团队'].value_counts()
            st.bar_chart(team_counts)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("优先级分布")
            priority_counts = filtered_df['优先级'].value_counts()
            st.bar_chart(priority_counts)
        
        with col4:
            st.subheader("状态分布")
            status_counts = filtered_df['状态'].value_counts()
            st.bar_chart(status_counts)
    
    with tab3:
        st.subheader("高优先级问题 (P1)")
        
        p1_issues = filtered_df[filtered_df['优先级'] == 'P1']
        
        if len(p1_issues) > 0:
            for _, row in p1_issues.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="kpi-card issue-p1">
                        <div style="font-weight: bold;">{row['问题描述']}</div>
                        <div>分校: {row['分校']} | 影响人数: {row['影响人数']} | 状态: {row['状态']}</div>
                        <div>分类: {row['问题分类']} | 团队: {row['所属团队']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("当前无P1级别问题")
        
        st.subheader("高影响问题 (影响人数≥3)")
        high_impact = filtered_df[filtered_df['影响人数'] >= 3]
        
        if len(high_impact) > 0:
            st.dataframe(
                high_impact[['发生日期', '分校', '问题描述', '影响人数', '状态', '优先级']].sort_values('影响人数', ascending=False),
                use_container_width=True
            )
        else:
            st.info("当前无高影响问题")
    
    with tab4:
        st.subheader("工单明细")
        
        # 格式化显示
        display_df = filtered_df.copy()
        display_df['发生日期'] = display_df['发生日期'].dt.strftime('%Y-%m-%d %H:%M')
        
        # 重新排序列
        display_df = display_df[[
            '发生日期', '分校', '优先级', '影响人数', 
            '问题分类', '状态', '所属团队', '问题描述'
        ]]
        
        # 应用CSS类
        def style_row(row):
            if row['优先级'] == 'P1':
                return ['background-color: #FEE2E2'] * len(row)
            elif row['优先级'] == 'P2':
                return ['background-color: #FEF3C7'] * len(row)
            elif row['优先级'] == 'P3':
                return ['background-color: #E0E7FF'] * len(row)
            return [''] * len(row)
        
        st.dataframe(
            display_df.style.apply(style_row, axis=1),
            use_container_width=True,
            height=500
        )
        
        # 导出按钮
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 导出数据 (CSV)",
            data=csv,
            file_name=f"工单数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # 页脚
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**数据来源**: 用户反馈周报")
    with col2:
        st.write(f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col3:
        st.write("**版本**: 1.0.0")

if __name__ == "__main__":
    main()
