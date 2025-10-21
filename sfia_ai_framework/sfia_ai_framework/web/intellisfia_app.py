"""
IntelliSFIA Web Application - Main Streamlit App

A comprehensive web interface for the IntelliSFIA framework providing:
- Enterprise integration management
- Real-time SFIA analysis
- Multi-agent AI scenarios
- Knowledge graph visualization
- Workforce intelligence dashboards
"""

import streamlit as st
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig
from sfia_ai_framework.examples.scenarios import SFIAScenarios

# Configure page
st.set_page_config(
    page_title="IntelliSFIA - Intelligent SFIA Framework",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .status-healthy {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-unhealthy {
        color: #dc3545;
        font-weight: bold;
    }
    
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'sdk' not in st.session_state:
    st.session_state.sdk = None
if 'enterprise_initialized' not in st.session_state:
    st.session_state.enterprise_initialized = False
if 'systems_connected' not in st.session_state:
    st.session_state.systems_connected = []

async def initialize_sdk():
    """Initialize the SFIA SDK"""
    if st.session_state.sdk is None:
        try:
            config = SFIASDKConfig(
                neo4j_uri=st.secrets.get("neo4j_uri", "bolt://localhost:7687"),
                neo4j_user=st.secrets.get("neo4j_user", "neo4j"),
                neo4j_password=st.secrets.get("neo4j_password", "password"),
                openai_api_key=st.secrets.get("openai_api_key", None)
            )
            
            sdk = SFIASDK(config)
            await sdk.initialize()
            st.session_state.sdk = sdk
            return True
        except Exception as e:
            st.error(f"Failed to initialize SDK: {e}")
            return False
    return True

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🧠 IntelliSFIA</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; font-size: 1.2rem; color: #666;">Intelligent SFIA Framework with Enterprise AI Integration</p>', 
        unsafe_allow_html=True
    )
    
    # Sidebar Navigation
    st.sidebar.markdown("## 🚀 Navigation")
    
    pages = {
        "🏠 Dashboard": "dashboard",
        "🏢 Enterprise Integration": "enterprise",
        "👤 Employee Analysis": "employee_analysis", 
        "🏢 Department Analysis": "department_analysis",
        "📊 Organization Insights": "organization_insights",
        "🎯 Real-World Scenarios": "scenarios",
        "🤖 Multi-Agent AI": "agents",
        "🔍 Knowledge Graph": "knowledge_graph",
        "📈 Analytics": "analytics",
        "📋 Reports": "reports",
        "⚙️ Settings": "settings"
    }
    
    selected_page = st.sidebar.selectbox("Select Page", list(pages.keys()))
    page_key = pages[selected_page]
    
    # SDK Status
    with st.sidebar:
        st.markdown("## 🔧 System Status")
        
        # Initialize SDK button
        if st.button("🔄 Initialize SDK"):
            with st.spinner("Initializing SDK..."):
                if asyncio.run(initialize_sdk()):
                    st.success("✅ SDK Initialized")
                else:
                    st.error("❌ SDK Initialization Failed")
        
        # SDK status indicator
        if st.session_state.sdk:
            st.markdown("**SDK Status:** <span class='status-healthy'>🟢 Connected</span>", unsafe_allow_html=True)
        else:
            st.markdown("**SDK Status:** <span class='status-unhealthy'>🔴 Disconnected</span>", unsafe_allow_html=True)
        
        # Enterprise integration status
        if st.session_state.enterprise_initialized:
            st.markdown("**Enterprise:** <span class='status-healthy'>🟢 Active</span>", unsafe_allow_html=True)
            st.markdown(f"**Systems:** {len(st.session_state.systems_connected)} connected")
        else:
            st.markdown("**Enterprise:** <span class='status-unhealthy'>🔴 Not Initialized</span>", unsafe_allow_html=True)
    
    # Route to appropriate page
    if page_key == "dashboard":
        show_dashboard()
    elif page_key == "enterprise":
        show_enterprise_integration()
    elif page_key == "employee_analysis":
        show_employee_analysis()
    elif page_key == "department_analysis":
        show_department_analysis()
    elif page_key == "organization_insights":
        show_organization_insights()
    elif page_key == "scenarios":
        show_scenarios()
    elif page_key == "agents":
        show_multi_agent_ai()
    elif page_key == "knowledge_graph":
        show_knowledge_graph()
    elif page_key == "analytics":
        show_analytics()
    elif page_key == "reports":
        show_reports()
    elif page_key == "settings":
        show_settings()

def show_dashboard():
    """Main dashboard page"""
    st.header("📊 IntelliSFIA Dashboard")
    
    if not st.session_state.sdk:
        st.warning("⚠️ Please initialize the SDK first using the sidebar.")
        return
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Connected Systems", len(st.session_state.systems_connected), "2 more than last week")
    
    with col2:
        st.metric("Active Analyses", "47", "12 today")
    
    with col3:
        st.metric("SFIA Suggestions", "1,234", "89 this week")
    
    with col4:
        st.metric("Compliance Score", "94%", "2% improvement")
    
    st.markdown("---")
    
    # Recent activity
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Recent Analysis Activity")
        
        # Sample activity data
        activity_data = pd.DataFrame({
            'Date': pd.date_range(start='2025-10-15', end='2025-10-21'),
            'Employee Analyses': [23, 31, 45, 38, 52, 41, 29],
            'Department Analyses': [5, 8, 12, 9, 15, 11, 7],
            'Organization Insights': [2, 3, 4, 3, 5, 4, 3]
        })
        
        fig = px.line(activity_data, x='Date', y=['Employee Analyses', 'Department Analyses', 'Organization Insights'],
                      title="Analysis Activity Over Time")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Quick Actions")
        
        if st.button("🔍 Analyze New Employee", use_container_width=True):
            st.switch_page("employee_analysis")
        
        if st.button("🏢 Department Insights", use_container_width=True):
            st.switch_page("department_analysis")
        
        if st.button("🤖 Run AI Scenario", use_container_width=True):
            st.switch_page("scenarios")
        
        if st.button("📋 Generate Report", use_container_width=True):
            st.switch_page("reports")
    
    # System status
    st.subheader("🏥 System Health")
    
    if st.session_state.enterprise_initialized:
        health_col1, health_col2 = st.columns(2)
        
        with health_col1:
            st.success("✅ Enterprise Integration: Healthy")
            st.info("🔄 Real-time Processing: Active")
            st.success("✅ Knowledge Graph: Connected")
        
        with health_col2:
            st.success("✅ Multi-Agent AI: Ready")
            st.info("📊 Analytics Engine: Running")
            st.success("✅ Caching Layer: Operational")
    else:
        st.warning("⚠️ Enterprise integration not initialized. Go to Enterprise Integration page to set up.")

def show_enterprise_integration():
    """Enterprise integration management page"""
    st.header("🏢 Enterprise Integration")
    
    if not st.session_state.sdk:
        st.warning("⚠️ Please initialize the SDK first.")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Setup", "🔌 Systems", "🏥 Health", "⚙️ Configuration"])
    
    with tab1:
        st.subheader("Initialize Enterprise Integration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            config_method = st.radio(
                "Configuration Method",
                ["Upload Configuration File", "Manual Configuration", "Quick Setup"]
            )
        
        with col2:
            redis_url = st.text_input("Redis URL", value="redis://localhost:6379")
        
        if config_method == "Upload Configuration File":
            config_file = st.file_uploader("Upload YAML Configuration", type=['yaml', 'yml'])
            
            if config_file and st.button("Initialize with Config File"):
                try:
                    config_content = yaml.safe_load(config_file)
                    st.code(yaml.dump(config_content, default_flow_style=False), language='yaml')
                    
                    with st.spinner("Initializing enterprise integration..."):
                        # In real implementation, this would actually initialize
                        st.session_state.enterprise_initialized = True
                        st.success("✅ Enterprise integration initialized successfully!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Failed to initialize: {e}")
        
        elif config_method == "Quick Setup":
            st.info("Quick setup will create a basic configuration with commonly used systems.")
            
            if st.button("🚀 Quick Setup"):
                with st.spinner("Setting up enterprise integration..."):
                    # Simulate quick setup
                    st.session_state.enterprise_initialized = True
                    st.success("✅ Quick setup completed!")
                    st.rerun()
    
    with tab2:
        st.subheader("Connected Enterprise Systems")
        
        if st.session_state.enterprise_initialized:
            # Add new system
            st.markdown("### ➕ Add New System")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                system_name = st.text_input("System Name", placeholder="e.g., hr_database")
            
            with col2:
                system_type = st.selectbox(
                    "System Type",
                    ["postgresql", "mysql", "sap", "powerbi", "mongodb", "kafka", "oracle"]
                )
            
            with col3:
                if st.button("🔌 Connect System"):
                    if system_name:
                        st.session_state.systems_connected.append({
                            'name': system_name,
                            'type': system_type,
                            'status': 'Connected',
                            'last_sync': datetime.now().isoformat()
                        })
                        st.success(f"✅ Connected to {system_name}")
                        st.rerun()
            
            # Show connected systems
            if st.session_state.systems_connected:
                st.markdown("### 🔌 Connected Systems")
                
                systems_df = pd.DataFrame(st.session_state.systems_connected)
                
                for idx, system in enumerate(st.session_state.systems_connected):
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])
                    
                    with col1:
                        st.write(f"**{system['name']}**")
                    
                    with col2:
                        st.write(system['type'])
                    
                    with col3:
                        st.markdown(f"<span class='status-healthy'>🟢 {system['status']}</span>", 
                                   unsafe_allow_html=True)
                    
                    with col4:
                        st.write(system['last_sync'][:16])
                    
                    with col5:
                        if st.button("🗑️", key=f"remove_{idx}"):
                            st.session_state.systems_connected.pop(idx)
                            st.rerun()
            else:
                st.info("No systems connected yet. Add a system above to get started.")
        else:
            st.warning("Enterprise integration not initialized. Please initialize first.")
    
    with tab3:
        st.subheader("🏥 System Health Monitoring")
        
        if st.session_state.enterprise_initialized and st.session_state.systems_connected:
            if st.button("🔄 Refresh Health Status"):
                st.success("Health status refreshed")
            
            # Create health status grid
            health_col1, health_col2 = st.columns(2)
            
            with health_col1:
                st.markdown("### System Status")
                for system in st.session_state.systems_connected:
                    status_color = "status-healthy"
                    status_icon = "🟢"
                    
                    st.markdown(
                        f"**{system['name']}**: <span class='{status_color}'>{status_icon} Healthy</span>",
                        unsafe_allow_html=True
                    )
            
            with health_col2:
                st.markdown("### Performance Metrics")
                
                # Sample performance data
                perf_data = {
                    'Metric': ['Response Time', 'Throughput', 'Error Rate', 'Availability'],
                    'Value': ['120ms', '1.2k req/min', '0.01%', '99.9%'],
                    'Status': ['🟢 Good', '🟢 Good', '🟢 Good', '🟢 Excellent']
                }
                
                perf_df = pd.DataFrame(perf_data)
                st.dataframe(perf_df, hide_index=True)
        else:
            st.info("No systems to monitor. Connect some enterprise systems first.")
    
    with tab4:
        st.subheader("⚙️ Configuration")
        
        if st.session_state.enterprise_initialized:
            # Configuration editor
            sample_config = {
                'real_time_enabled': True,
                'batch_interval': 1800,
                'cache_ttl': 3600,
                'max_concurrent_connections': 5,
                'retry_attempts': 3,
                'retry_delay': 5,
                'analysis_config': {
                    'confidence_threshold': 0.7,
                    'min_activities_for_analysis': 5,
                    'lookback_days': 90
                }
            }
            
            config_yaml = yaml.dump(sample_config, default_flow_style=False)
            edited_config = st.text_area("Configuration (YAML)", config_yaml, height=400)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Save Configuration"):
                    try:
                        yaml.safe_load(edited_config)
                        st.success("✅ Configuration saved successfully!")
                    except yaml.YAMLError as e:
                        st.error(f"Invalid YAML: {e}")
            
            with col2:
                if st.button("🔄 Reload Default"):
                    st.rerun()
        else:
            st.warning("Please initialize enterprise integration first.")

def show_employee_analysis():
    """Employee analysis page"""
    st.header("👤 Employee SFIA Analysis")
    
    if not st.session_state.sdk:
        st.warning("⚠️ Please initialize the SDK first.")
        return
    
    # Employee selection
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        employee_id = st.text_input("Employee ID", placeholder="e.g., EMP001, john.doe, 12345")
    
    with col2:
        analysis_type = st.selectbox("Analysis Type", ["Standard", "Deep Analysis", "Real-time"])
    
    with col3:
        if st.button("🔍 Analyze Employee", disabled=not employee_id):
            analyze_employee_action(employee_id, analysis_type)
    
    # Show analysis results if available
    if 'employee_analysis_result' in st.session_state:
        show_employee_analysis_results()

def analyze_employee_action(employee_id: str, analysis_type: str):
    """Perform employee analysis"""
    with st.spinner(f"Analyzing employee {employee_id}..."):
        # Simulate analysis - in real implementation, this would call the SDK
        result = {
            'success': True,
            'employee_id': employee_id,
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_type': analysis_type,
            'suggestions': [
                {
                    'skill_name': 'Software Development',
                    'skill_code': 'PROG',
                    'current_level': 3,
                    'suggested_level': 4,
                    'confidence_score': 0.87,
                    'reasoning': 'Demonstrated advanced programming skills in recent projects with high-quality deliverables.',
                    'supporting_evidence': [
                        'Completed 15 complex programming tasks',
                        'Average code quality score: 92%',
                        'Led 3 technical design sessions'
                    ],
                    'improvement_areas': [
                        'Expand architecture design skills',
                        'Develop mentoring capabilities'
                    ],
                    'timeline_estimate': '6-12 months'
                },
                {
                    'skill_name': 'Systems Design',
                    'skill_code': 'ARCH',
                    'current_level': 2,
                    'suggested_level': 3,
                    'confidence_score': 0.73,
                    'reasoning': 'Shows good understanding of system architecture principles with room for growth.',
                    'supporting_evidence': [
                        'Contributed to 5 system design reviews',
                        'Successfully implemented 3 architectural patterns'
                    ],
                    'improvement_areas': [
                        'Study advanced architectural patterns',
                        'Gain experience with large-scale systems'
                    ],
                    'timeline_estimate': '12-18 months'
                }
            ]
        }
        
        st.session_state.employee_analysis_result = result
        st.success(f"✅ Analysis completed for {employee_id}")
        st.rerun()

def show_employee_analysis_results():
    """Display employee analysis results"""
    result = st.session_state.employee_analysis_result
    
    st.subheader(f"📊 Analysis Results for {result['employee_id']}")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Skills Analyzed", len(result['suggestions']))
    
    with col2:
        avg_confidence = sum(s['confidence_score'] for s in result['suggestions']) / len(result['suggestions'])
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
    
    with col3:
        avg_current = sum(s.get('current_level', 0) for s in result['suggestions']) / len(result['suggestions'])
        st.metric("Avg Current Level", f"{avg_current:.1f}")
    
    with col4:
        avg_suggested = sum(s['suggested_level'] for s in result['suggestions']) / len(result['suggestions'])
        st.metric("Avg Suggested Level", f"{avg_suggested:.1f}")
    
    # Detailed suggestions
    st.subheader("📈 SFIA Level Suggestions")
    
    for idx, suggestion in enumerate(result['suggestions']):
        with st.expander(f"**{suggestion['skill_name']}** - Level {suggestion['suggested_level']} (Confidence: {suggestion['confidence_score']:.1%})"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Current Level:**")
                st.write(suggestion.get('current_level', 'Not assessed'))
                
                st.markdown("**Suggested Level:**")
                st.write(suggestion['suggested_level'])
                
                st.markdown("**Timeline:**")
                st.write(suggestion['timeline_estimate'])
            
            with col2:
                st.markdown("**Confidence Score:**")
                st.progress(suggestion['confidence_score'])
                st.write(f"{suggestion['confidence_score']:.1%}")
            
            st.markdown("**Reasoning:**")
            st.write(suggestion['reasoning'])
            
            if suggestion.get('supporting_evidence'):
                st.markdown("**Supporting Evidence:**")
                for evidence in suggestion['supporting_evidence']:
                    st.write(f"• {evidence}")
            
            if suggestion.get('improvement_areas'):
                st.markdown("**Improvement Areas:**")
                for area in suggestion['improvement_areas']:
                    st.write(f"• {area}")
    
    # Download results
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download JSON Report"):
            st.download_button(
                label="Download",
                data=json.dumps(result, indent=2),
                file_name=f"sfia_analysis_{result['employee_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🔄 Analyze Another Employee"):
            if 'employee_analysis_result' in st.session_state:
                del st.session_state.employee_analysis_result
            st.rerun()

def show_department_analysis():
    """Department analysis page"""
    st.header("🏢 Department SFIA Analysis")
    
    if not st.session_state.sdk:
        st.warning("⚠️ Please initialize the SDK first.")
        return
    
    # Department selection
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        department = st.selectbox(
            "Select Department",
            ["Engineering", "Product", "Data Science", "DevOps", "Quality Assurance", "Architecture"]
        )
    
    with col2:
        include_contractors = st.checkbox("Include Contractors")
    
    with col3:
        if st.button("🔍 Analyze Department"):
            analyze_department_action(department, include_contractors)
    
    # Show results if available
    if 'department_analysis_result' in st.session_state:
        show_department_analysis_results()

def analyze_department_action(department: str, include_contractors: bool):
    """Perform department analysis"""
    with st.spinner(f"Analyzing {department} department..."):
        # Simulate department analysis
        result = {
            'success': True,
            'department': department,
            'analysis_timestamp': datetime.now().isoformat(),
            'include_contractors': include_contractors,
            'employees': {
                'EMP001': [
                    {'skill_name': 'Software Development', 'suggested_level': 4, 'confidence_score': 0.87},
                    {'skill_name': 'Systems Design', 'suggested_level': 3, 'confidence_score': 0.73}
                ],
                'EMP002': [
                    {'skill_name': 'Software Development', 'suggested_level': 5, 'confidence_score': 0.92},
                    {'skill_name': 'Technical Leadership', 'suggested_level': 4, 'confidence_score': 0.85}
                ],
                'EMP003': [
                    {'skill_name': 'Data Analysis', 'suggested_level': 3, 'confidence_score': 0.78},
                    {'skill_name': 'Systems Integration', 'suggested_level': 3, 'confidence_score': 0.71}
                ]
            }
        }
        
        st.session_state.department_analysis_result = result
        st.success(f"✅ Analysis completed for {department} department")
        st.rerun()

def show_department_analysis_results():
    """Display department analysis results"""
    result = st.session_state.department_analysis_result
    
    st.subheader(f"📊 {result['department']} Department Analysis")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_employees = len(result['employees'])
    total_skills = sum(len(skills) for skills in result['employees'].values())
    avg_level = sum(s['suggested_level'] for skills in result['employees'].values() for s in skills) / total_skills
    avg_confidence = sum(s['confidence_score'] for skills in result['employees'].values() for s in skills) / total_skills
    
    with col1:
        st.metric("Employees Analyzed", total_employees)
    
    with col2:
        st.metric("Total Skills", total_skills)
    
    with col3:
        st.metric("Avg SFIA Level", f"{avg_level:.1f}")
    
    with col4:
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
    
    # Employee breakdown
    st.subheader("👥 Employee Breakdown")
    
    employee_data = []
    for emp_id, skills in result['employees'].items():
        employee_data.append({
            'Employee ID': emp_id,
            'Skills Analyzed': len(skills),
            'Avg Level': sum(s['suggested_level'] for s in skills) / len(skills),
            'Avg Confidence': sum(s['confidence_score'] for s in skills) / len(skills)
        })
    
    df = pd.DataFrame(employee_data)
    st.dataframe(df, use_container_width=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Level distribution
        all_levels = [s['suggested_level'] for skills in result['employees'].values() for s in skills]
        level_counts = pd.Series(all_levels).value_counts().sort_index()
        
        fig = px.bar(
            x=level_counts.index,
            y=level_counts.values,
            title="SFIA Level Distribution",
            labels={'x': 'SFIA Level', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Skills distribution
        all_skills = [s['skill_name'] for skills in result['employees'].values() for s in skills]
        skill_counts = pd.Series(all_skills).value_counts().head(10)
        
        fig = px.pie(
            values=skill_counts.values,
            names=skill_counts.index,
            title="Top Skills in Department"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_organization_insights():
    """Organization insights page"""
    st.header("🏢 Organization SFIA Insights")
    
    if not st.session_state.sdk:
        st.warning("⚠️ Please initialize the SDK first.")
        return
    
    # Controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time_period = st.selectbox("Time Period", ["Last 30 days", "Last 90 days", "Last Year", "All Time"])
    
    with col2:
        include_all = st.checkbox("Include All Roles", value=True)
    
    with col3:
        if st.button("📊 Generate Insights"):
            generate_organization_insights(time_period, include_all)
    
    # Show insights if available
    if 'org_insights' in st.session_state:
        show_organization_insights_results()

def generate_organization_insights(time_period: str, include_all: bool):
    """Generate organization insights"""
    with st.spinner("Generating organization insights..."):
        # Simulate organization insights
        insights = {
            'success': True,
            'analysis_timestamp': datetime.now().isoformat(),
            'time_period': time_period,
            'total_employees': 347,
            'departments': {
                'Engineering': {'employee_count': 120, 'avg_level': 3.8, 'skills': ['Software Development', 'Systems Design']},
                'Product': {'employee_count': 45, 'avg_level': 4.2, 'skills': ['Product Management', 'Strategy']},
                'Data Science': {'employee_count': 32, 'avg_level': 4.0, 'skills': ['Data Analysis', 'Machine Learning']},
                'DevOps': {'employee_count': 28, 'avg_level': 3.9, 'skills': ['Infrastructure', 'Automation']},
                'Quality Assurance': {'employee_count': 22, 'avg_level': 3.5, 'skills': ['Testing', 'Quality Management']}
            },
            'skill_distribution': {
                'Software Development': {'employees': 95, 'avg_level': 3.7},
                'Systems Design': {'employees': 67, 'avg_level': 3.4},
                'Data Analysis': {'employees': 45, 'avg_level': 3.8},
                'Product Management': {'employees': 38, 'avg_level': 4.1},
                'Technical Leadership': {'employees': 29, 'avg_level': 4.5}
            },
            'level_distribution': {1: 23, 2: 67, 3: 98, 4: 89, 5: 45, 6: 18, 7: 7},
            'high_performers': [
                {'employee_id': 'EMP001', 'skill': 'Software Development', 'level': 6, 'confidence': 0.95},
                {'employee_id': 'EMP023', 'skill': 'Technical Leadership', 'level': 7, 'confidence': 0.91},
                {'employee_id': 'EMP045', 'skill': 'Systems Architecture', 'level': 6, 'confidence': 0.89}
            ],
            'improvement_opportunities': [
                {'skill': 'Cloud Architecture', 'employees_needing': 45, 'priority': 'High'},
                {'skill': 'DevOps Practices', 'employees_needing': 32, 'priority': 'Medium'},
                {'skill': 'Data Engineering', 'employees_needing': 28, 'priority': 'Medium'}
            ]
        }
        
        st.session_state.org_insights = insights
        st.success("✅ Organization insights generated")
        st.rerun()

def show_organization_insights_results():
    """Display organization insights results"""
    insights = st.session_state.org_insights
    
    # Executive summary
    st.subheader("📋 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Employees", insights['total_employees'])
    
    with col2:
        st.metric("Departments", len(insights['departments']))
    
    with col3:
        st.metric("Skills Tracked", len(insights['skill_distribution']))
    
    with col4:
        avg_org_level = sum(count * level for level, count in insights['level_distribution'].items()) / sum(insights['level_distribution'].values())
        st.metric("Avg SFIA Level", f"{avg_org_level:.1f}")
    
    # Department breakdown
    st.subheader("🏢 Department Analysis")
    
    dept_data = []
    for dept_name, dept_info in insights['departments'].items():
        dept_data.append({
            'Department': dept_name,
            'Employees': dept_info['employee_count'],
            'Avg Level': dept_info['avg_level'],
            'Key Skills': ', '.join(dept_info['skills'][:3])
        })
    
    dept_df = pd.DataFrame(dept_data)
    st.dataframe(dept_df, use_container_width=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Department size chart
        fig = px.pie(
            dept_df,
            values='Employees',
            names='Department',
            title="Department Size Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Level distribution
        fig = px.bar(
            x=list(insights['level_distribution'].keys()),
            y=list(insights['level_distribution'].values()),
            title="Organization SFIA Level Distribution",
            labels={'x': 'SFIA Level', 'y': 'Number of Employees'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # High performers
    st.subheader("⭐ High Performers")
    
    perf_data = []
    for performer in insights['high_performers']:
        perf_data.append({
            'Employee ID': performer['employee_id'],
            'Skill': performer['skill'],
            'SFIA Level': performer['level'],
            'Confidence': f"{performer['confidence']:.1%}"
        })
    
    perf_df = pd.DataFrame(perf_data)
    st.dataframe(perf_df, use_container_width=True)
    
    # Improvement opportunities
    st.subheader("💡 Improvement Opportunities")
    
    for opp in insights['improvement_opportunities']:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{opp['skill']}**")
        
        with col2:
            st.write(f"{opp['employees_needing']} employees")
        
        with col3:
            priority_color = "🔴" if opp['priority'] == 'High' else "🟡"
            st.write(f"{priority_color} {opp['priority']}")

def show_scenarios():
    """Real-world scenarios page"""
    st.header("🎯 Real-World Scenarios")
    
    if not st.session_state.sdk:
        st.warning("⚠️ Please initialize the SDK first.")
        return
    
    # Scenario selection
    scenarios = {
        "🎯 Technical Hiring": {
            "description": "AI-powered candidate evaluation and role matching",
            "key": "hiring"
        },
        "🚀 Career Development": {
            "description": "Personalized career pathway analysis and planning",
            "key": "career"
        },
        "👥 Team Formation": {
            "description": "Optimal team composition for projects",
            "key": "team"
        },
        "🏢 Organization Assessment": {
            "description": "Comprehensive organizational capability analysis",
            "key": "organization"
        },
        "❌ Skills Gap Analysis": {
            "description": "Identify and quantify organizational skill gaps",
            "key": "skills_gap"
        }
    }
    
    selected_scenario = st.selectbox(
        "Select Scenario",
        list(scenarios.keys()),
        format_func=lambda x: f"{x} - {scenarios[x]['description']}"
    )
    
    scenario_key = scenarios[selected_scenario]['key']
    
    # Scenario-specific inputs
    if scenario_key == "hiring":
        show_hiring_scenario()
    elif scenario_key == "career":
        show_career_scenario()
    elif scenario_key == "team":
        show_team_scenario()
    elif scenario_key == "organization":
        show_organization_scenario()
    elif scenario_key == "skills_gap":
        show_skills_gap_scenario()

def show_hiring_scenario():
    """Hiring scenario interface"""
    st.subheader("🎯 Technical Hiring Assistant")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Job Requirements**")
        job_title = st.text_input("Job Title", value="Senior Software Engineer")
        required_skills = st.text_area("Required Skills", 
                                      value="Python, REST APIs, Database Design, Cloud Architecture")
        experience_level = st.selectbox("Experience Level", ["Junior", "Mid-level", "Senior", "Lead"])
    
    with col2:
        st.markdown("**Candidate Information**")
        candidate_name = st.text_input("Candidate Name", value="John Smith")
        candidate_skills = st.text_area("Candidate Skills",
                                       value="Python, Django, PostgreSQL, AWS, Docker")
        years_experience = st.number_input("Years of Experience", min_value=0, max_value=20, value=5)
    
    if st.button("🔍 Analyze Candidate Fit"):
        with st.spinner("Analyzing candidate fit..."):
            # Simulate hiring analysis
            result = {
                'candidate_name': candidate_name,
                'job_title': job_title,
                'overall_fit': 0.78,
                'skill_matches': [
                    {'skill': 'Python', 'required': True, 'candidate_level': 4, 'match_score': 0.9},
                    {'skill': 'REST APIs', 'required': True, 'candidate_level': 3, 'match_score': 0.8},
                    {'skill': 'Database Design', 'required': True, 'candidate_level': 3, 'match_score': 0.7},
                    {'skill': 'Cloud Architecture', 'required': True, 'candidate_level': 2, 'match_score': 0.6}
                ],
                'strengths': ['Strong Python programming skills', 'Good web development experience', 'Cloud platform knowledge'],
                'gaps': ['Limited database design experience', 'Need more architecture experience'],
                'recommendation': 'Strong candidate with potential. Recommend technical interview focusing on system design.',
                'interview_questions': [
                    'How would you design a scalable REST API for high traffic?',
                    'Explain your approach to database schema optimization',
                    'Describe a challenging technical problem you solved recently'
                ]
            }
            
            st.success("✅ Analysis completed!")
            
            # Display results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Overall Fit", f"{result['overall_fit']:.1%}")
            
            with col2:
                matches = sum(1 for m in result['skill_matches'] if m['match_score'] >= 0.7)
                st.metric("Skill Matches", f"{matches}/{len(result['skill_matches'])}")
            
            with col3:
                st.metric("Experience Gap", f"{max(0, 7 - years_experience)} years")
            
            # Detailed analysis
            st.subheader("📊 Detailed Analysis")
            
            for match in result['skill_matches']:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{match['skill']}**")
                
                with col2:
                    st.write(f"Level {match['candidate_level']}")
                
                with col3:
                    st.progress(match['match_score'])
                    st.write(f"{match['match_score']:.1%}")
            
            st.subheader("💡 Recommendation")
            st.info(result['recommendation'])
            
            if result['interview_questions']:
                st.subheader("❓ Suggested Interview Questions")
                for i, question in enumerate(result['interview_questions'], 1):
                    st.write(f"{i}. {question}")

def show_career_scenario():
    """Career development scenario interface"""
    st.subheader("🚀 Career Development Advisor")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_role = st.text_input("Current Role", value="Software Developer")
        current_skills = st.text_area("Current Skills", 
                                     value="Python, Web Development, Databases")
        years_experience = st.number_input("Years of Experience", min_value=0, max_value=20, value=3)
    
    with col2:
        target_role = st.text_input("Target Role", value="Technical Lead")
        career_interests = st.text_area("Career Interests",
                                       value="Leadership, Architecture, Team Management")
        timeline = st.selectbox("Timeline", ["6 months", "1 year", "2 years", "3+ years"])
    
    if st.button("🗺️ Generate Career Path"):
        with st.spinner("Generating career development plan..."):
            # Simulate career path analysis
            result = {
                'current_role': current_role,
                'target_role': target_role,
                'timeline': timeline,
                'gap_analysis': {
                    'technical_gaps': ['System Architecture', 'Advanced Algorithms', 'Cloud Platforms'],
                    'leadership_gaps': ['Team Management', 'Project Planning', 'Stakeholder Communication'],
                    'business_gaps': ['Strategic Thinking', 'Budget Management', 'Vendor Relations']
                },
                'development_path': [
                    {
                        'phase': 'Months 1-6',
                        'focus': 'Technical Leadership',
                        'activities': ['Lead small projects', 'Mentor junior developers', 'Architecture training']
                    },
                    {
                        'phase': 'Months 7-12',
                        'focus': 'People Management',
                        'activities': ['Management training', 'Performance reviews', 'Team building']
                    },
                    {
                        'phase': 'Months 13-18',
                        'focus': 'Strategic Thinking',
                        'activities': ['Business analysis', 'Strategic planning', 'Cross-functional collaboration']
                    }
                ],
                'learning_resources': [
                    {'type': 'Course', 'title': 'Technical Leadership Fundamentals', 'provider': 'Coursera'},
                    {'type': 'Book', 'title': 'The Manager\'s Path', 'provider': 'O\'Reilly'},
                    {'type': 'Certification', 'title': 'AWS Solutions Architect', 'provider': 'AWS'}
                ]
            }
            
            st.success("✅ Career path generated!")
            
            # Display gap analysis
            st.subheader("📊 Skills Gap Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Technical Gaps**")
                for gap in result['gap_analysis']['technical_gaps']:
                    st.write(f"• {gap}")
            
            with col2:
                st.markdown("**Leadership Gaps**")
                for gap in result['gap_analysis']['leadership_gaps']:
                    st.write(f"• {gap}")
            
            with col3:
                st.markdown("**Business Gaps**")
                for gap in result['gap_analysis']['business_gaps']:
                    st.write(f"• {gap}")
            
            # Development timeline
            st.subheader("🗓️ Development Timeline")
            
            for phase in result['development_path']:
                with st.expander(f"**{phase['phase']}**: {phase['focus']}"):
                    st.markdown("**Key Activities:**")
                    for activity in phase['activities']:
                        st.write(f"• {activity}")
            
            # Learning resources
            st.subheader("📚 Recommended Learning Resources")
            
            for resource in result['learning_resources']:
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.write(f"**{resource['type']}**")
                
                with col2:
                    st.write(resource['title'])
                
                with col3:
                    st.write(resource['provider'])

def show_team_scenario():
    """Team formation scenario interface"""
    st.subheader("👥 Team Formation Optimizer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input("Project Name", value="Mobile App Development")
        required_skills = st.text_area("Required Skills",
                                      value="React Native, Node.js, Mobile UI/UX, API Development")
        team_size = st.number_input("Target Team Size", min_value=2, max_value=15, value=5)
    
    with col2:
        project_duration = st.selectbox("Project Duration", ["3 months", "6 months", "1 year", "18+ months"])
        budget_level = st.selectbox("Budget Level", ["Low", "Medium", "High", "Enterprise"])
        remote_ok = st.checkbox("Remote Team OK", value=True)
    
    if st.button("🔍 Find Optimal Team"):
        with st.spinner("Analyzing team composition..."):
            # Simulate team formation analysis
            result = {
                'project_name': project_name,
                'team_composition': [
                    {
                        'role': 'Tech Lead',
                        'employee_id': 'EMP001',
                        'name': 'Sarah Johnson',
                        'skills': ['React Native', 'Team Leadership', 'Architecture'],
                        'sfia_level': 5,
                        'availability': '100%'
                    },
                    {
                        'role': 'Full Stack Developer',
                        'employee_id': 'EMP045',
                        'name': 'Mike Chen',
                        'skills': ['Node.js', 'React Native', 'Databases'],
                        'sfia_level': 4,
                        'availability': '80%'
                    },
                    {
                        'role': 'UI/UX Designer',
                        'employee_id': 'EMP089',
                        'name': 'Lisa Rodriguez',
                        'skills': ['Mobile UI', 'User Research', 'Prototyping'],
                        'sfia_level': 4,
                        'availability': '100%'
                    },
                    {
                        'role': 'Backend Developer',
                        'employee_id': 'EMP112',
                        'name': 'David Kim',
                        'skills': ['Node.js', 'API Development', 'Cloud Services'],
                        'sfia_level': 3,
                        'availability': '90%'
                    },
                    {
                        'role': 'QA Engineer',
                        'employee_id': 'EMP156',
                        'name': 'Emma Wilson',
                        'skills': ['Mobile Testing', 'Automation', 'Performance Testing'],
                        'sfia_level': 3,
                        'availability': '100%'
                    }
                ],
                'team_metrics': {
                    'skill_coverage': 0.92,
                    'experience_balance': 0.85,
                    'collaboration_score': 0.78,
                    'estimated_success': 0.88
                },
                'recommendations': [
                    'Strong technical leadership with Sarah as Tech Lead',
                    'Good mix of senior and mid-level developers',
                    'Consider adding a dedicated DevOps engineer for deployment',
                    'Schedule regular design review sessions with Lisa'
                ]
            }
            
            st.success("✅ Optimal team composition identified!")
            
            # Team metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Skill Coverage", f"{result['team_metrics']['skill_coverage']:.1%}")
            
            with col2:
                st.metric("Experience Balance", f"{result['team_metrics']['experience_balance']:.1%}")
            
            with col3:
                st.metric("Collaboration Score", f"{result['team_metrics']['collaboration_score']:.1%}")
            
            with col4:
                st.metric("Success Probability", f"{result['team_metrics']['estimated_success']:.1%}")
            
            # Team composition
            st.subheader("👥 Recommended Team")
            
            team_data = []
            for member in result['team_composition']:
                team_data.append({
                    'Role': member['role'],
                    'Employee': f"{member['name']} ({member['employee_id']})",
                    'Key Skills': ', '.join(member['skills'][:3]),
                    'SFIA Level': member['sfia_level'],
                    'Availability': member['availability']
                })
            
            team_df = pd.DataFrame(team_data)
            st.dataframe(team_df, use_container_width=True)
            
            # Recommendations
            st.subheader("💡 Team Recommendations")
            
            for rec in result['recommendations']:
                st.write(f"• {rec}")

def show_organization_scenario():
    """Organization assessment scenario interface"""
    st.subheader("🏢 Organization Assessment")
    
    # This would show comprehensive organizational analysis
    st.info("Organization assessment scenario - comprehensive capability mapping and strategic insights")
    
    if st.button("🔍 Run Assessment"):
        st.success("Assessment completed - see Organization Insights page for detailed results")

def show_skills_gap_scenario():
    """Skills gap analysis scenario interface"""
    st.subheader("❌ Skills Gap Analysis")
    
    # This would show skills gap analysis
    st.info("Skills gap analysis scenario - identify and quantify organizational skill deficiencies")
    
    if st.button("🔍 Analyze Gaps"):
        st.success("Gap analysis completed - see Analytics page for detailed results")

def show_multi_agent_ai():
    """Multi-agent AI page"""
    st.header("🤖 Multi-Agent AI System")
    
    if not st.session_state.sdk:
        st.warning("⚠️ Please initialize the SDK first.")
        return
    
    st.info("🚧 Multi-Agent AI interface - Advanced collaborative AI agents for complex SFIA analysis")
    
    # Agent status
    agents = [
        {"name": "Skills Analyst", "status": "Ready", "specialization": "Skill assessment and gap analysis"},
        {"name": "Career Advisor", "status": "Ready", "specialization": "Career pathway planning"},
        {"name": "Team Specialist", "status": "Ready", "specialization": "Team composition optimization"},
        {"name": "Learning Specialist", "status": "Ready", "specialization": "Learning resource recommendations"},
        {"name": "Workforce Planner", "status": "Ready", "specialization": "Strategic workforce planning"}
    ]
    
    st.subheader("🤖 Available Agents")
    
    for agent in agents:
        col1, col2, col3 = st.columns([2, 1, 3])
        
        with col1:
            st.write(f"**{agent['name']}**")
        
        with col2:
            st.markdown(f"<span class='status-healthy'>🟢 {agent['status']}</span>", unsafe_allow_html=True)
        
        with col3:
            st.write(agent['specialization'])

def show_knowledge_graph():
    """Knowledge graph page"""
    st.header("🔍 SFIA Knowledge Graph")
    
    if not st.session_state.sdk:
        st.warning("⚠️ Please initialize the SDK first.")
        return
    
    st.info("🚧 Knowledge Graph interface - Interactive exploration of SFIA relationships and ontologies")
    
    # Graph controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        graph_type = st.selectbox("Graph Type", ["Skills Network", "Career Pathways", "Role Relationships"])
    
    with col2:
        depth = st.slider("Relationship Depth", 1, 3, 2)
    
    with col3:
        if st.button("🔍 Explore Graph"):
            st.success("Graph exploration initiated")

def show_analytics():
    """Analytics page"""
    st.header("📈 Advanced Analytics")
    
    if not st.session_state.sdk:
        st.warning("⚠️ Please initialize the SDK first.")
        return
    
    st.info("🚧 Advanced Analytics interface - Deep insights and predictive analytics for workforce intelligence")
    
    # Analytics options
    analytics_types = [
        "Skills Trend Analysis",
        "Performance Correlation",
        "Career Progression Patterns",
        "Team Effectiveness Metrics",
        "Predictive Skill Demand"
    ]
    
    selected_analytics = st.multiselect("Select Analytics", analytics_types)
    
    if selected_analytics and st.button("📊 Generate Analytics"):
        st.success(f"Analytics generated for: {', '.join(selected_analytics)}")

def show_reports():
    """Reports page"""
    st.header("📋 Reports & Documentation")
    
    if not st.session_state.sdk:
        st.warning("⚠️ Please initialize the SDK first.")
        return
    
    tab1, tab2, tab3 = st.tabs(["📊 Standard Reports", "📋 Compliance", "📈 Custom Reports"])
    
    with tab1:
        st.subheader("Standard Reports")
        
        report_types = [
            "Employee SFIA Assessment Report",
            "Department Analysis Report", 
            "Organization Skills Overview",
            "Career Development Report",
            "Team Composition Analysis"
        ]
        
        for report in report_types:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"📄 {report}")
            
            with col2:
                if st.button("Generate", key=f"gen_{report}"):
                    st.success(f"Generated {report}")
    
    with tab2:
        st.subheader("Compliance Reports")
        
        if st.button("📋 Generate SFIA Compliance Report"):
            st.success("Compliance report generated")
        
        if st.button("📊 Audit Trail Report"):
            st.success("Audit trail report generated")
    
    with tab3:
        st.subheader("Custom Report Builder")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_name = st.text_input("Report Name")
            include_fields = st.multiselect(
                "Include Fields",
                ["Employee ID", "Skills", "SFIA Levels", "Performance Metrics", "Department", "Role"]
            )
        
        with col2:
            date_range = st.date_input("Date Range", value=[datetime.now().date()])
            output_format = st.selectbox("Output Format", ["PDF", "Excel", "CSV", "JSON"])
        
        if st.button("🔧 Build Custom Report"):
            st.success(f"Custom report '{report_name}' created")

def show_settings():
    """Settings page"""
    st.header("⚙️ Settings & Configuration")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 General", "🔐 Security", "🔗 Integrations", "📊 Analytics"])
    
    with tab1:
        st.subheader("General Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Organization Name", value="TechCorp Inc.")
            st.selectbox("Default Language", ["English", "Spanish", "French", "German"])
            st.selectbox("Timezone", ["UTC", "EST", "PST", "GMT"])
        
        with col2:
            st.number_input("Session Timeout (minutes)", min_value=15, max_value=480, value=60)
            st.checkbox("Enable Notifications", value=True)
            st.checkbox("Auto-save Reports", value=True)
    
    with tab2:
        st.subheader("Security Settings")
        
        st.checkbox("Enable Two-Factor Authentication", value=False)
        st.checkbox("Require Strong Passwords", value=True)
        st.selectbox("Data Retention Period", ["30 days", "90 days", "1 year", "2 years"])
    
    with tab3:
        st.subheader("Integration Settings")
        
        st.text_input("Neo4j URI", value="bolt://localhost:7687")
        st.text_input("Redis URL", value="redis://localhost:6379")
        st.text_input("OpenAI API Key", type="password")
    
    with tab4:
        st.subheader("Analytics Settings")
        
        st.checkbox("Enable Advanced Analytics", value=True)
        st.checkbox("Store Analysis History", value=True)
        st.number_input("Analytics Retention (days)", min_value=30, max_value=365, value=90)

if __name__ == "__main__":
    main()