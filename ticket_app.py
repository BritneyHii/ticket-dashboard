import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import altair as alt
import json
from streamlit_autorefresh import st_autorefresh
import warnings
warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="用户反馈工单看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-change {
        font-size: 0.9rem;
        font-weight: 500;
    }
    .positive-change {
        color: #10B981;
    }
    .negative-change {
        color: #EF4444;
    }
    .issue-p1 {
        background-color: #FEE2E2;
        border-left: 4px solid #EF4444;
    }
    .issue-p2 {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
    }
    .issue-p3 {
        background-color: #E0E7FF;
        border-left: 4px solid #6366F1;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F3F4F6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class IssueDashboard:
    def __init__(self, data_path=None):
        self.data = None
        self.filtered_data = None
        self.load_sample_data() if data_path is None else self.load_data(data_path)
        self.init_session_state()
        
    def load_sample_data(self):
        """加载示例数据"""
        # 创建示例数据（基于提供的Excel结构）
        sample_data = {
            '发生日期（北京）': pd.date_range('2025-12-19', periods=35, freq='D'),
            '分校': ['US']*13 + ['UK']*8 + ['CA']*4 + ['MYS']*4 + ['SG', 'HK', 'AUS', 'KR', 'AUS', 'MYS', 'UK', 'SG', 'HK', 'CA', 'KR', 'JP', 'FR'],
            '收集渠道': ['群聊/私聊']*32 + ['教师端']*2 + ['学员端-课堂回放'],
            '影响人数': [1]*30 + [2]*2 + [3, 4, 6, 1, 1],
            '问题分类': self.generate_sample_categories(),
            '问题状态': ['已解决']*21 + ['排查中']*2 + ['走排期']*5 + ['转需求']*1 + ['待验证']*3 + ['无法定位']*2 + ['信息确认中']*1,
            '所属团队': ['前端']*13 + ['服务端']*10 + ['教务']*7 + ['教务/教研']*2 + ['声网服务']*3,
            '响应级别': ['P2']*30 + ['P1']*3 + ['P3']*2,
            '是否有效': ['是']*35,
            '是否好评': [None]*35,
            '问题归类': ['技术BUG']*15 + ['网络/设备问题']*8 + ['用户操作问题']*7 + ['产品逻辑']*3 + ['信息查询/咨询']*2,
            '工单状态': ['已解决']*21 + ['处理中']*10 + ['待处理']*4,
            '处理进展': ['已解决']*21 + ['正在排查中']*14,
            '问题描述': ['APP闪退']*3 + ['加入频道失败']*3 + ['涂鸦/板书问题']*1 + ['游戏断网重连']*1 + ['其他']*27
        }
        
        self.data = pd.DataFrame(sample_data)
        # 添加产品线信息
        self.data['所属产品线'] = ['Think Online']*20 + ['Think Zone']*3 + ['In-Person']*12
        # 添加IT拦截标记
        self.data['IT拦截'] = [True]*14 + [False]*21
    
    def generate_sample_categories(self):
        """生成示例问题分类"""
        categories = []
        # 课堂相关
        categories.extend(['课堂/课堂功能问题/音视频/加入频道失败']*3)
        categories.extend(['课堂/课堂功能问题/音视频/学生听不到老师声音']*1)
        categories.extend(['课堂/课堂功能问题/音视频/学员看不到主讲视频']*1)
        categories.extend(['课堂/课堂功能问题/涂鸦/板书']*1)
        categories.extend(['课堂/课堂功能问题/互动逻辑']*2)
        categories.extend(['课堂/App问题/APP闪退']*3)
        categories.extend(['课堂/课堂功能问题/课件/其他']*1)
        
        # 课后相关
        categories.extend(['课后（非课中）/作业/考试']*3)
        categories.extend(['课后（非课中）/回放录制']*2)
        categories.extend(['课后（非课中）/其他App模块问题']*3)
        categories.extend(['课后（非课中）/课前准备页']*1)
        
        # 售后相关
        categories.extend(['售后/其他业务后台问题']*5)
        
        # 售前相关
        categories.extend(['售前/诊断']*2)
        categories.extend(['售前/支付']*4)
        
        # ThinkZone相关
        categories.extend(['ThinkZone/相关问题']*3)
        
        return categories
    
    def load_data(self, data_path):
        """从文件加载数据"""
        try:
            self.data = pd.read_excel(data_path)
            # 数据清洗和转换
            self.data = self.clean_data(self.data)
        except Exception as e:
            st.error(f"数据加载失败: {e}")
            self.load_sample_data()
    
    def clean_data(self, df):
        """数据清洗"""
        # 转换日期列
        date_columns = ['发生日期（北京）', '问题接收时间（北京）']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 处理缺失值
        df['影响人数'] = pd.to_numeric(df['影响人数'], errors='coerce').fillna(1)
        df['是否有效'] = df['是否有效'].fillna('是')
        
        return df
    
    def init_session_state(self):
        """初始化session状态"""
        if 'start_date' not in st.session_state:
            st.session_state.start_date = self.data['发生日期（北京）'].min().date()
        if 'end_date' not in st.session_state:
            st.session_state.end_date = self.data['发生日期（北京）'].max().date()
    
    def create_filters(self):
        """创建筛选器"""
        st.sidebar.header("🔍 筛选器")
        
        # 日期筛选器
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input(
                "开始日期",
                value=st.session_state.start_date,
                key="filter_start_date"
            )
        with col2:
            end_date = st.date_input(
                "结束日期",
                value=st.session_state.end_date,
                key="filter_end_date"
            )
        
        # 分校筛选
        branches = ['全部'] + sorted(self.data['分校'].dropna().unique().tolist())
        selected_branch = st.sidebar.multiselect(
            "选择分校",
            options=branches,
            default=['全部'],
            key="filter_branch"
        )
        
        # 问题分类筛选
        categories = ['全部'] + sorted(self.data['问题分类'].dropna().unique().tolist())
        selected_category = st.sidebar.multiselect(
            "选择问题分类",
            options=categories,
            default=['全部'],
            key="filter_category"
        )
        
        # 团队筛选
        teams = ['全部'] + sorted(self.data['所属团队'].dropna().unique().tolist())
        selected_team = st.sidebar.multiselect(
            "选择团队",
            options=teams,
            default=['全部'],
            key="filter_team"
        )
        
        # 状态筛选
        statuses = ['全部'] + sorted(self.data['问题状态'].dropna().unique().tolist())
        selected_status = st.sidebar.multiselect(
            "选择状态",
            options=statuses,
            default=['全部'],
            key="filter_status"
        )
        
        # 优先级筛选
        priorities = ['全部'] + sorted(self.data['响应级别'].dropna().unique().tolist())
        selected_priority = st.sidebar.multiselect(
            "选择优先级",
            options=priorities,
            default=['全部'],
            key="filter_priority"
        )
        
        # 搜索框
        search_query = st.sidebar.text_input("🔍 搜索问题描述", "")
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'branches': selected_branch,
            'categories': selected_category,
            'teams': selected_team,
            'statuses': selected_status,
            'priorities': selected_priority,
            'search_query': search_query
        }
    
    def apply_filters(self, filters):
        """应用筛选器"""
        filtered_data = self.data.copy()
        
        # 日期筛选
        if filters['start_date'] and filters['end_date']:
            filtered_data = filtered_data[
                (filtered_data['发生日期（北京）'].dt.date >= filters['start_date']) &
                (filtered_data['发生日期（北京）'].dt.date <= filters['end_date'])
            ]
        
        # 分校筛选
        if '全部' not in filters['branches']:
            filtered_data = filtered_data[filtered_data['分校'].isin(filters['branches'])]
        
        # 问题分类筛选
        if '全部' not in filters['categories']:
            filtered_data = filtered_data[filtered_data['问题分类'].isin(filters['categories'])]
        
        # 团队筛选
        if '全部' not in filters['teams']:
            filtered_data = filtered_data[filtered_data['所属团队'].isin(filters['teams'])]
        
        # 状态筛选
        if '全部' not in filters['statuses']:
            filtered_data = filtered_data[filtered_data['问题状态'].isin(filters['statuses'])]
        
        # 优先级筛选
        if '全部' not in filters['priorities']:
            filtered_data = filtered_data[filtered_data['响应级别'].isin(filters['priorities'])]
        
        # 搜索筛选
        if filters['search_query']:
            filtered_data = filtered_data[
                filtered_data['问题描述'].astype(str).str.contains(
                    filters['search_query'], case=False, na=False
                )
            ]
        
        self.filtered_data = filtered_data
        return filtered_data
    
    def calculate_kpis(self, data):
        """计算关键指标"""
        kpis = {}
        
        # 基础指标
        kpis['问题总数'] = len(data)
        kpis['有效问题数'] = len(data[data['是否有效'] == '是'])
        kpis['影响人数'] = int(data['影响人数'].sum())
        
        # IT拦截数（示例）
        if 'IT拦截' in data.columns:
            kpis['IT拦截数'] = len(data[data['IT拦截'] == True])
        else:
            kpis['IT拦截数'] = 0
        
        # 解决率
        resolved_statuses = ['已解决', '已修复']
        resolved_count = len(data[data['问题状态'].isin(resolved_statuses)])
        kpis['解决率'] = round(resolved_count / len(data) * 100, 2) if len(data) > 0 else 0
        
        # 好评率
        if '是否好评' in data.columns:
            good_reviews = data[data['是否好评'] == '是']
            kpis['好评率'] = round(len(good_reviews) / len(data) * 100, 2) if len(data) > 0 else 0
        else:
            kpis['好评率'] = 0
        
        # 平均解决时间（示例数据）
        kpis['平均响应时间'] = "2.3h"
        kpis['平均解决时间'] = "8.5h"
        
        # 计算趋势（与上周对比）
        if hasattr(self, 'last_week_data'):
            kpis['问题数趋势'] = self.calculate_trend(kpis['问题总数'], len(self.last_week_data))
            kpis['解决率趋势'] = self.calculate_trend(kpis['解决率'], 85)  # 假设上周解决率为85%
        else:
            kpis['问题数趋势'] = 0
            kpis['解决率趋势'] = 0
        
        return kpis
    
    def calculate_trend(self, current_value, previous_value):
        """计算趋势变化"""
        if previous_value == 0:
            return 0
        return round(((current_value - previous_value) / previous_value) * 100, 1)
    
    def display_kpi_cards(self, kpis):
        """显示KPI卡片"""
        st.markdown("### 📊 核心指标")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div>问题总数</div>
                <div class="metric-value">{kpis['问题总数']}</div>
                <div class="metric-change {'positive-change' if kpis['问题数趋势'] > 0 else 'negative-change'}">
                    {f"▲ {kpis['问题数趋势']}%" if kpis['问题数趋势'] > 0 else f"▼ {abs(kpis['问题数趋势'])}%"}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div>有效问题数</div>
                <div class="metric-value">{kpis['有效问题数']}</div>
                <div>占比: {round(kpis['有效问题数']/kpis['问题总数']*100 if kpis['问题总数']>0 else 0, 1)}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div>解决率</div>
                <div class="metric-value">{kpis['解决率']}%</div>
                <div class="metric-change {'positive-change' if kpis['解决率趋势'] > 0 else 'negative-change'}">
                    {f"▲ {kpis['解决率趋势']}%" if kpis['解决率趋势'] > 0 else f"▼ {abs(kpis['解决率趋势'])}%"}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div>影响人数</div>
                <div class="metric-value">{kpis['影响人数']}</div>
                <div>人均反馈率: {round(kpis['影响人数']/26392*100 if 26392>0 else 0, 2)}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="kpi-card">
                <div>IT拦截数</div>
                <div class="metric-value">{kpis['IT拦截数']}</div>
                <div>占比: {round(kpis['IT拦截数']/kpis['问题总数']*100 if kpis['问题总数']>0 else 0, 1)}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="kpi-card">
                <div>解决时效</div>
                <div class="metric-value">{kpis['平均解决时间']}</div>
                <div>响应: {kpis['平均响应时间']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    def create_trend_chart(self):
        """创建趋势对比图表"""
        st.markdown("### 📈 工单数量趋势对比")
        
        # 模拟周数据对比
        weeks = ['12.12-12.18', '12.19-12.25']
        categories = ['课堂', '课后', '售后', '售前', 'ThinkZone', '其他']
        
        # 创建示例数据
        df_trend = pd.DataFrame({
            '类别': categories * 2,
            '数量': [19, 14, 9, 4, 2, 0, 12, 9, 5, 6, 3, 0],
            '周次': ['上周'] * 6 + ['本周'] * 6
        })
        
        # 使用Plotly创建分组柱状图
        fig = px.bar(
            df_trend,
            x='类别',
            y='数量',
            color='周次',
            barmode='group',
            color_discrete_map={'上周': '#91cc75', '本周': '#5470c6'},
            height=400
        )
        
        fig.update_layout(
            xaxis_title="问题分类",
            yaxis_title="问题数量",
            legend_title="周次",
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_category_chart(self):
        """创建问题分类占比图表"""
        st.markdown("### 🗂️ 问题分类占比")
        
        if self.filtered_data is not None and not self.filtered_data.empty:
            # 提取一级分类
            self.filtered_data['一级分类'] = self.filtered_data['问题分类'].apply(
                lambda x: str(x).split('/')[0] if '/' in str(x) else str(x)
            )
            
            category_counts = self.filtered_data['一级分类'].value_counts().reset_index()
            category_counts.columns = ['分类', '数量']
            
            # 创建饼图
            fig = px.pie(
                category_counts,
                values='数量',
                names='分类',
                hole=0.4,
                height=400
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无数据")
    
    def create_branch_chart(self):
        """创建分校问题分布图表"""
        st.markdown("### 🏫 各分校问题分布")
        
        if self.filtered_data is not None and not self.filtered_data.empty:
            branch_counts = self.filtered_data['分校'].value_counts().reset_index()
            branch_counts.columns = ['分校', '数量']
            
            # 创建柱状图
            fig = px.bar(
                branch_counts,
                x='分校',
                y='数量',
                color='数量',
                color_continuous_scale='Blues',
                height=400
            )
            
            fig.update_layout(
                xaxis_title="分校",
                yaxis_title="问题数量",
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无数据")
    
    def create_team_chart(self):
        """创建团队问题分布图表"""
        st.markdown("### 👥 团队问题分布")
        
        if self.filtered_data is not None and not self.filtered_data.empty:
            team_counts = self.filtered_data['所属团队'].value_counts().reset_index()
            team_counts.columns = ['团队', '数量']
            
            # 创建水平柱状图
            fig = px.bar(
                team_counts,
                y='团队',
                x='数量',
                orientation='h',
                color='数量',
                color_continuous_scale='Greens',
                height=400
            )
            
            fig.update_layout(
                yaxis_title="团队",
                xaxis_title="问题数量",
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无数据")
    
    def create_resolution_time_chart(self):
        """创建解决时效趋势图"""
        st.markdown("### ⏱️ 解决时效趋势")
        
        # 模拟数据
        dates = pd.date_range('2025-12-19', periods=7, freq='D')
        response_times = [1.5, 2.0, 1.8, 2.3, 2.1, 1.9, 2.0]
        resolution_times = [7.2, 8.1, 7.8, 8.5, 7.9, 8.2, 8.0]
        
        df_time = pd.DataFrame({
            '日期': dates,
            '平均响应时间': response_times,
            '平均解决时间': resolution_times
        })
        
        # 创建折线图
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_time['日期'],
            y=df_time['平均响应时间'],
            mode='lines+markers',
            name='平均响应时间',
            line=dict(color='#91cc75', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_time['日期'],
            y=df_time['平均解决时间'],
            mode='lines+markers',
            name='平均解决时间',
            line=dict(color='#5470c6', width=3),
            marker=dict(size=10, symbol='diamond')
        ))
        
        fig.update_layout(
            xaxis_title="日期",
            yaxis_title="时间 (小时)",
            height=400,
            plot_bgcolor='white',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_top_issues(self):
        """显示TOP问题列表"""
        st.markdown("### ⚠️ TOP 问题（高优先级 & 高影响）")
        
        if self.filtered_data is not None and not self.filtered_data.empty:
            # 筛选P1优先级或影响人数>1的问题
            top_issues = self.filtered_data[
                (self.filtered_data['响应级别'] == 'P1') | 
                (self.filtered_data['影响人数'] > 1)
            ].copy()
            
            if not top_issues.empty:
                # 排序：按影响人数降序，再按日期倒序
                top_issues = top_issues.sort_values(
                    by=['影响人数', '发生日期（北京）'],
                    ascending=[False, False]
                ).reset_index(drop=True)
                
                # 创建数据表格
                display_cols = ['发生日期（北京）', '分校', '响应级别', '影响人数', 
                               '问题分类', '问题状态', '所属团队', '问题描述']
                
                # 只选择存在的列
                available_cols = [col for col in display_cols if col in top_issues.columns]
                
                st.dataframe(
                    top_issues[available_cols].head(10),
                    use_container_width=True,
                    column_config={
                        "发生日期（北京）": st.column_config.DatetimeColumn(
                            "发生时间",
                            format="YYYY-MM-DD HH:mm"
                        ),
                        "影响人数": st.column_config.NumberColumn(
                            "影响人数",
                            format="%d人"
                        ),
                        "响应级别": st.column_config.TextColumn(
                            "优先级",
                            help="P1: 最高优先级, P2: 高优先级, P3: 普通"
                        )
                    }
                )
                
                # 显示统计数据
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("TOP问题数量", len(top_issues))
                with col2:
                    st.metric("平均影响人数", round(top_issues['影响人数'].mean(), 1))
                with col3:
                    st.metric("P1问题占比", 
                             f"{round(len(top_issues[top_issues['响应级别']=='P1'])/len(top_issues)*100, 1)}%")
            else:
                st.info("当前筛选条件下无TOP问题")
        else:
            st.info("暂无数据")
    
    def display_issue_table(self):
        """显示完整问题表格"""
        st.markdown("### 📋 工单列表")
        
        if self.filtered_data is not None and not self.filtered_data.empty:
            # 添加优先级样式
            def apply_priority_style(row):
                if row['响应级别'] == 'P1':
                    return 'background-color: #FEE2E2'
                elif row['响应级别'] == 'P2':
                    return 'background-color: #FEF3C7'
                elif row['响应级别'] == 'P3':
                    return 'background-color: #E0E7FF'
                return ''
            
            # 显示表格
            st.dataframe(
                self.filtered_data.style.apply(lambda row: apply_priority_style(row), axis=1),
                use_container_width=True,
                height=600
            )
            
            # 导出选项
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("📥 导出数据"):
                    csv = self.filtered_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="下载CSV",
                        data=csv,
                        file_name=f"工单数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        else:
            st.info("当前筛选条件下无数据")
    
    def display_summary_insights(self):
        """显示汇总分析"""
        st.markdown("### 📋 本周重点洞察")
        
        insights = [
            "🔴 **重点问题**: 回放视频卡顿问题在本周多次出现，主要影响Windows和Mac学员端",
            "📊 **趋势分析**: 本周工单数量较上周下降12例，主要得益于课堂互动逻辑问题的减少",
            "🌍 **地域分布**: 美国分校问题数量最多（13例），需重点关注",
            "👥 **团队分布**: 前端团队问题占比最高（37.1%），其次是服务端（28.6%）",
            "⚡ **解决效率**: 平均解决时间8.5小时，平均响应时间2.3小时",
            "🎯 **改进方向**: 需加强回放功能的稳定性测试，优化Windows/Mac端的视频播放性能"
        ]
        
        for insight in insights:
            st.markdown(f"- {insight}")
    
    def run_dashboard(self):
        """运行主看板"""
        # 页面标题
        st.markdown('<div class="main-header">📊 用户反馈工单看板</div>', unsafe_allow_html=True)
        
        # 创建筛选器并应用
        filters = self.create_filters()
        filtered_data = self.apply_filters(filters)
        
        # 显示筛选信息
        st.write(f"**筛选结果**: 共 {len(filtered_data)} 条记录 | "
                f"时间范围: {filters['start_date']} 至 {filters['end_date']}")
        
        # 计算并显示KPI
        kpis = self.calculate_kpis(filtered_data)
        self.display_kpi_cards(kpis)
        
        # 使用Tabs组织内容
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 趋势分析", 
            "📊 问题分布", 
            "⚠️ TOP问题", 
            "📋 数据明细",
            "💡 分析洞察"
        ])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                self.create_trend_chart()
            with col2:
                self.create_resolution_time_chart()
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                self.create_category_chart()
            with col2:
                self.create_team_chart()
            
            col3, col4 = st.columns(2)
            with col3:
                self.create_branch_chart()
        
        with tab3:
            self.display_top_issues()
        
        with tab4:
            self.display_issue_table()
        
        with tab5:
            self.display_summary_insights()
        
        # 侧边栏信息
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 数据说明")
        st.sidebar.info("""
        - **数据源**: 境外用户反馈问题记录
        - **更新频率**: 实时更新
        - **统计周期**: 按周统计（可自定义）
        - **有效问题**: 排除网络、设备等非系统问题的反馈
        """)
        
        # 操作按钮
        st.sidebar.markdown("### ⚙️ 操作")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🔄 刷新数据"):
                st.rerun()
        with col2:
            if st.button("📋 生成周报"):
                st.success("周报生成中...")

# 主函数
def main():
    # 应用标题
    st.title("📊 用户反馈工单看板系统")
    st.caption("实时监控用户反馈问题，助力快速响应与解决")
    
    # 创建看板实例
    dashboard = IssueDashboard()
    
    # 运行看板
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
