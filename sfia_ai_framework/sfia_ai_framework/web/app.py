"""
SFIA AI Web Application

A comprehensive web application built with Streamlit that demonstrates
the capabilities of the SFIA AI Framework through interactive interfaces.
"""

import streamlit as st
import asyncio
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import os
from datetime import datetime, timedelta

# Add parent directory to Python path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig, SFIASDKContext
from sfia_ai_framework.examples.scenarios import SFIAScenarios


# Page configuration
st.set_page_config(
    page_title="SFIA AI Framework",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'sdk_initialized' not in st.session_state:
    st.session_state.sdk_initialized = False
if 'sdk' not in st.session_state:
    st.session_state.sdk = None
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = None

# App title
st.markdown('<h1 class="main-header">🧠 SFIA AI Framework</h1>', unsafe_allow_html=True)
st.markdown("**Intelligent Skills Framework Analysis with Multi-Agent AI and Knowledge Graphs**")

# Sidebar for configuration
st.sidebar.title("⚙️ Configuration")

# SDK Configuration
with st.sidebar.expander("🔧 SDK Settings", expanded=True):
    neo4j_uri = st.text_input("Neo4j URI", value="bolt://localhost:7687")
    neo4j_user = st.text_input("Neo4j Username", value="neo4j")
    neo4j_password = st.text_input("Neo4j Password", type="password")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    
    enable_agents = st.checkbox("Enable AI Agents", value=True)
    enable_reasoning = st.checkbox("Enable Reasoning Engine", value=True)

# Initialize SDK button
if st.sidebar.button("🚀 Initialize SDK"):
    with st.spinner("Initializing SFIA AI SDK..."):
        try:
            config = SFIASDKConfig(
                neo4j_uri=neo4j_uri,
                neo4j_user=neo4j_user,
                neo4j_password=neo4j_password,
                openai_api_key=openai_api_key,
                enable_agents=enable_agents,
                enable_reasoning=enable_reasoning
            )
            
            # Create SDK instance
            st.session_state.sdk = SFIASDK(config)
            
            # Initialize SDK (this is async, so we need to handle it properly)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(st.session_state.sdk.initialize())
            
            st.session_state.sdk_initialized = True
            st.session_state.scenarios = SFIAScenarios(st.session_state.sdk)
            
            st.sidebar.success("✅ SDK Initialized Successfully!")
            
        except Exception as e:
            st.sidebar.error(f"❌ Failed to initialize SDK: {str(e)}")
            st.session_state.sdk_initialized = False

# Main content area
if not st.session_state.sdk_initialized:
    st.warning("⚠️ Please configure and initialize the SDK in the sidebar to continue.")
    
    # Show introduction while SDK is not initialized
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="sub-header">🎯 Key Features</div>', unsafe_allow_html=True)
        st.markdown("""
        - **Multi-Agent Intelligence**: CrewAI-powered agents for specialized analysis
        - **Knowledge Graph**: Neo4j-based semantic understanding
        - **Skills Analysis**: Comprehensive SFIA skills framework processing
        - **Career Planning**: AI-driven career development recommendations
        - **Team Optimization**: Intelligent team formation and optimization
        - **Real-time Insights**: Interactive dashboards and visualizations
        """)
    
    with col2:
        st.markdown('<div class="sub-header">🔧 System Requirements</div>', unsafe_allow_html=True)
        st.markdown("""
        - **Neo4j Database**: For knowledge graph storage
        - **OpenAI API**: For AI agent capabilities (optional)
        - **Python 3.11+**: With required dependencies
        - **SFIA Ontology**: RDF data loaded into system
        - **Network Access**: For external AI services
        """)
    
    st.info("💡 **Tip**: Make sure Neo4j is running and accessible before initializing the SDK.")

else:
    # Main application tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Dashboard", 
        "👥 Hiring Optimization", 
        "📈 Career Development", 
        "🔧 Team Formation", 
        "🏢 Organization Analysis", 
        "📊 Skills Insights"
    ])
    
    with tab1:
        st.markdown('<div class="sub-header">📊 SFIA Knowledge Graph Dashboard</div>', unsafe_allow_html=True)
        
        # Dashboard metrics
        col1, col2, col3, col4 = st.columns(4)
        
        if st.button("🔄 Refresh Statistics"):
            with st.spinner("Loading knowledge graph statistics..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    stats = loop.run_until_complete(st.session_state.sdk.get_knowledge_graph_statistics())
                    
                    if stats.get("success"):
                        basic_stats = stats.get("basic_stats", {})
                        network_stats = stats.get("network_analysis", {})
                        
                        with col1:
                            st.metric("Skills", basic_stats.get("skills_count", 0))
                        with col2:
                            st.metric("Levels", basic_stats.get("levels_count", 0))
                        with col3:
                            st.metric("Categories", basic_stats.get("categories_count", 0))
                        with col4:
                            st.metric("Relationships", basic_stats.get("relationships_count", 0))
                        
                        # Network analysis visualization
                        if network_stats:
                            st.markdown("### 🕸️ Network Analysis")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Network Density", f"{network_stats.get('density', 0):.3f}")
                                st.metric("Avg Clustering", f"{network_stats.get('avg_clustering', 0):.3f}")
                            
                            with col2:
                                st.metric("Connected Components", network_stats.get('connected_components', 0))
                                st.metric("Network Diameter", network_stats.get('diameter', 0))
                    
                except Exception as e:
                    st.error(f"Failed to load statistics: {str(e)}")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📈 Load Sample Data"):
                with st.spinner("Loading SFIA ontology..."):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(
                            st.session_state.sdk.load_sfia_ontology("../SFIA_9_2025-10-21.ttl")
                        )
                        if result.success:
                            st.success("✅ SFIA ontology loaded successfully!")
                        else:
                            st.error(f"❌ Failed to load ontology: {result.message}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col2:
            if st.button("🎨 Generate Visualization"):
                with st.spinner("Creating knowledge graph visualization..."):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(
                            st.session_state.sdk.visualize_knowledge_graph("sfia_viz.html")
                        )
                        if result.get("success"):
                            st.success(f"✅ Visualization saved: {result.get('visualization_file')}")
                        else:
                            st.error(f"❌ Visualization failed: {result.get('error')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col3:
            if st.button("💾 Export Data"):
                with st.spinner("Exporting knowledge graph..."):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(
                            st.session_state.sdk.export_knowledge_graph("rdf", "sfia_export")
                        )
                        if result.get("success"):
                            st.success(f"✅ Data exported: {result.get('export_file')}")
                        else:
                            st.error(f"❌ Export failed: {result.get('error')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.markdown('<div class="sub-header">👥 Hiring Optimization</div>', unsafe_allow_html=True)
        
        # Hiring scenario interface
        st.markdown("### 🎯 Configure Hiring Scenario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Open Positions")
            num_positions = st.number_input("Number of positions", min_value=1, max_value=10, value=3)
            
            positions = []
            for i in range(num_positions):
                with st.expander(f"Position {i+1}"):
                    role = st.text_input(f"Role Title {i+1}", value=f"Software Engineer {i+1}")
                    skills = st.text_input(f"Required Skills {i+1}", value="PROG,SENG,TEST").split(",")
                    team = st.text_input(f"Team {i+1}", value="Development")
                    urgency = st.selectbox(f"Urgency {i+1}", ["low", "medium", "high"])
                    
                    positions.append({
                        "role": role,
                        "required_skills": [s.strip() for s in skills],
                        "team": team,
                        "urgency": urgency
                    })
        
        with col2:
            st.markdown("#### Candidates")
            num_candidates = st.number_input("Number of candidates", min_value=1, max_value=20, value=5)
            
            candidates = []
            for i in range(num_candidates):
                with st.expander(f"Candidate {i+1}"):
                    name = st.text_input(f"Name {i+1}", value=f"Candidate {i+1}")
                    current_skills = st.text_input(f"Current Skills {i+1}", value="PROG,TEST").split(",")
                    experience = st.number_input(f"Experience Years {i+1}", min_value=0, max_value=30, value=3)
                    current_role = st.text_input(f"Current Role {i+1}", value="Junior Developer")
                    
                    candidates.append({
                        "id": f"C{i+1:03d}",
                        "name": name,
                        "current_skills": [s.strip() for s in current_skills],
                        "experience_years": experience,
                        "current_role": current_role,
                        "career_goals": ["Senior Developer", "Tech Lead"]
                    })
        
        if st.button("🚀 Run Hiring Optimization"):
            with st.spinner("Analyzing hiring optimization scenario..."):
                try:
                    # Create scenario data
                    scenario_data = {
                        "company": "Demo Company",
                        "open_positions": positions,
                        "candidates": candidates
                    }
                    
                    # Run optimization
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    results = loop.run_until_complete(st.session_state.scenarios.hiring_optimization_scenario())
                    
                    # Display results
                    st.success("✅ Hiring optimization completed!")
                    
                    # Show recommendations
                    st.markdown("### 📋 Hiring Recommendations")
                    for rec in results.get("recommendations", []):
                        with st.expander(f"Recommendation for {rec['position']}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Recommended Candidate", rec["recommended_candidate"])
                            with col2:
                                st.metric("Fit Score", f"{rec['fit_score']:.2f}")
                            with col3:
                                st.metric("Skills to Develop", rec["development_needed"])
                            
                            st.write(f"**Reasoning**: {rec['reasoning']}")
                            st.write(f"**Onboarding Timeline**: {rec['onboarding_timeline']}")
                    
                    # Detailed analysis
                    st.markdown("### 📊 Detailed Analysis")
                    for analysis in results.get("position_analysis", []):
                        st.markdown(f"#### {analysis['position']}")
                        
                        # Create DataFrame for candidates
                        candidates_df = pd.DataFrame(analysis["candidate_fits"])
                        st.dataframe(candidates_df)
                        
                        # Visualization
                        fig = px.bar(
                            candidates_df, 
                            x="candidate", 
                            y="fit_score",
                            title=f"Candidate Fit Scores for {analysis['position']}"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                except Exception as e:
                    st.error(f"❌ Error running hiring optimization: {str(e)}")
    
    with tab3:
        st.markdown('<div class="sub-header">📈 Career Development Planning</div>', unsafe_allow_html=True)
        
        # Career development interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Employee Profile")
            employee_name = st.text_input("Employee Name", value="John Doe")
            current_role = st.text_input("Current Role", value="Junior Developer")
            current_skills = st.text_input("Current Skills (comma-separated)", value="PROG,TEST").split(",")
            experience_years = st.number_input("Years of Experience", min_value=0, max_value=30, value=2)
            time_availability = st.selectbox("Learning Time Available", 
                                           ["5 hours per week", "10 hours per week", "15 hours per week"])
        
        with col2:
            st.markdown("#### Career Goals")
            career_aspirations = st.multiselect(
                "Career Aspirations",
                ["Senior Developer", "Tech Lead", "Solution Architect", "Product Manager", "CTO"],
                default=["Senior Developer", "Tech Lead"]
            )
            learning_preferences = st.multiselect(
                "Learning Preferences",
                ["online_courses", "mentorship", "hands_on_projects", "conferences", "certifications"],
                default=["online_courses", "hands_on_projects"]
            )
        
        if st.button("🎯 Generate Development Plan"):
            with st.spinner("Creating personalized development plan..."):
                try:
                    # Create employee profile
                    employee_profile = {
                        "name": employee_name,
                        "current_role": current_role,
                        "current_skills": [s.strip() for s in current_skills],
                        "experience_years": experience_years,
                        "career_aspirations": career_aspirations,
                        "learning_preferences": learning_preferences,
                        "time_availability": time_availability
                    }
                    
                    # Generate development plan
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Use the actual method to generate development plan
                    primary_goal = career_aspirations[0] if career_aspirations else "Senior Developer"
                    development_plan = loop.run_until_complete(
                        st.session_state.sdk.generate_development_plan(employee_profile, primary_goal)
                    )
                    
                    if development_plan.get("success"):
                        st.success("✅ Development plan generated successfully!")
                        
                        # Display plan overview
                        st.markdown("### 📋 Development Plan Overview")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Primary Goal", primary_goal)
                        with col2:
                            skill_gaps = development_plan.get("skill_gap_analysis", {}).get("skill_gaps", [])
                            st.metric("Skills to Develop", len(skill_gaps))
                        with col3:
                            st.metric("Estimated Timeline", "12-18 months")
                        
                        # Skill gaps analysis
                        if skill_gaps:
                            st.markdown("### 🎯 Skills Gap Analysis")
                            gaps_df = pd.DataFrame(skill_gaps)
                            st.dataframe(gaps_df)
                            
                            # Visualization
                            if len(skill_gaps) > 0:
                                fig = px.bar(
                                    x=[gap.get("skill_code", f"Skill {i}") for i, gap in enumerate(skill_gaps)],
                                    y=[gap.get("priority", 1) for gap in skill_gaps],
                                    title="Skills Development Priority"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        
                        # Learning recommendations
                        learning_recs = development_plan.get("learning_recommendations", [])
                        if learning_recs:
                            st.markdown("### 📚 Learning Recommendations")
                            for rec in learning_recs[:5]:  # Show top 5
                                with st.expander(f"Learn {rec.get('skill', 'Skill')}"):
                                    st.write(f"**Resource**: {rec.get('resource_name', 'Online Course')}")
                                    st.write(f"**Type**: {rec.get('resource_type', 'Course')}")
                                    st.write(f"**Duration**: {rec.get('duration', '4-6 weeks')}")
                        
                        # Timeline
                        st.markdown("### ⏱️ Development Timeline")
                        timeline = development_plan.get("timeline", {})
                        for phase, description in timeline.items():
                            st.write(f"**{phase.replace('_', ' ').title()}**: {description}")
                    
                    else:
                        st.error(f"❌ Failed to generate development plan: {development_plan.get('error')}")
                
                except Exception as e:
                    st.error(f"❌ Error generating development plan: {str(e)}")
    
    with tab4:
        st.markdown('<div class="sub-header">🔧 Team Formation & Optimization</div>', unsafe_allow_html=True)
        
        # Team formation interface
        st.markdown("### 🎯 Project Requirements")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("Project Name", value="Mobile Banking App")
            project_duration = st.selectbox("Duration", ["3 months", "6 months", "9 months", "12 months"])
            team_size = st.number_input("Team Size", min_value=2, max_value=20, value=5)
            project_priority = st.selectbox("Priority", ["low", "medium", "high"])
        
        with col2:
            required_skills = st.text_input("Required Skills (comma-separated)", 
                                          value="PROG,MOBP,UNAN,TEST,SCTY").split(",")
            required_skills = [s.strip() for s in required_skills]
            
            st.markdown("#### Skills Breakdown")
            for skill in required_skills:
                st.write(f"• {skill}")
        
        # Available team members
        st.markdown("### 👥 Available Team Members")
        
        num_members = st.number_input("Number of available members", min_value=1, max_value=50, value=10)
        
        team_members = []
        for i in range(min(num_members, 5)):  # Limit to 5 for demo
            with st.expander(f"Team Member {i+1}"):
                name = st.text_input(f"Name {i+1}", value=f"Member {i+1}")
                skills = st.text_input(f"Skills {i+1}", value="PROG,TEST").split(",")
                current_project = st.text_input(f"Current Project {i+1}", value="None")
                development_goals = st.text_input(f"Development Goals {i+1}", value="ARCH,SENG").split(",")
                
                team_members.append({
                    "name": name,
                    "skills": [s.strip() for s in skills],
                    "current_project": current_project if current_project != "None" else None,
                    "development_goals": [s.strip() for s in development_goals]
                })
        
        if st.button("⚡ Optimize Team Formation"):
            with st.spinner("Optimizing team composition..."):
                try:
                    # Run team optimization
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    optimization_result = loop.run_until_complete(
                        st.session_state.sdk.optimize_team_composition(
                            {
                                "project_name": project_name,
                                "required_skills": required_skills,
                                "team_size": team_size,
                                "duration": project_duration
                            },
                            team_members
                        )
                    )
                    
                    if optimization_result.get("success"):
                        st.success("✅ Team optimization completed!")
                        
                        # Display optimization results
                        optimization = optimization_result.get("optimization_result", {})
                        
                        st.markdown("### 🎯 Optimized Team Composition")
                        
                        recommended_team = optimization.get("recommended_team", [])
                        if recommended_team:
                            # Team overview
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Team Size", len(recommended_team))
                            with col2:
                                total_skills = set()
                                for member in recommended_team:
                                    total_skills.update(member.get("skills", []))
                                st.metric("Unique Skills", len(total_skills))
                            with col3:
                                coverage = len(set(required_skills).intersection(total_skills))
                                st.metric("Skill Coverage", f"{coverage}/{len(required_skills)}")
                            
                            # Team members table
                            st.markdown("#### 👥 Selected Team Members")
                            team_df = pd.DataFrame(recommended_team)
                            st.dataframe(team_df)
                            
                            # Skills coverage visualization
                            st.markdown("#### 📊 Skills Coverage Analysis")
                            
                            coverage_data = []
                            for skill in required_skills:
                                members_with_skill = [
                                    member["name"] for member in recommended_team 
                                    if skill in member.get("skills", [])
                                ]
                                coverage_data.append({
                                    "Skill": skill,
                                    "Coverage": len(members_with_skill),
                                    "Members": ", ".join(members_with_skill)
                                })
                            
                            coverage_df = pd.DataFrame(coverage_data)
                            st.dataframe(coverage_df)
                            
                            # Coverage chart
                            fig = px.bar(
                                coverage_df,
                                x="Skill",
                                y="Coverage",
                                title="Skills Coverage by Team Members"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    else:
                        st.error(f"❌ Team optimization failed: {optimization_result.get('error')}")
                
                except Exception as e:
                    st.error(f"❌ Error optimizing team: {str(e)}")
    
    with tab5:
        st.markdown('<div class="sub-header">🏢 Organizational Skills Analysis</div>', unsafe_allow_html=True)
        
        # Organization analysis interface
        st.markdown("### 🏢 Organization Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            org_name = st.text_input("Organization Name", value="TechCorp Inc.")
            industry = st.selectbox("Industry", 
                                  ["Technology", "Finance", "Healthcare", "Manufacturing", "Retail"])
            total_employees = st.number_input("Total Employees", min_value=10, max_value=10000, value=200)
        
        with col2:
            strategic_focus = st.multiselect(
                "Strategic Focus Areas",
                ["Digital Transformation", "AI/ML Adoption", "Cloud Migration", 
                 "Cybersecurity", "Data Analytics", "Mobile Development"],
                default=["Digital Transformation", "AI/ML Adoption"]
            )
        
        # Department configuration
        st.markdown("### 🏬 Departments")
        
        departments = []
        num_departments = st.number_input("Number of departments", min_value=1, max_value=10, value=3)
        
        for i in range(num_departments):
            with st.expander(f"Department {i+1}"):
                dept_name = st.text_input(f"Department Name {i+1}", value=f"Department {i+1}")
                staff_count = st.number_input(f"Staff Count {i+1}", min_value=1, max_value=500, value=20)
                key_skills = st.text_input(f"Key Skills {i+1}", value="PROG,SENG,TEST").split(",")
                
                departments.append({
                    "name": dept_name,
                    "staff_count": staff_count,
                    "key_skills": [s.strip() for s in key_skills]
                })
        
        if st.button("📊 Analyze Organization"):
            with st.spinner("Performing organizational skills analysis..."):
                try:
                    # Create organization data
                    org_data = {
                        "company": org_name,
                        "industry": industry,
                        "total_employees": total_employees,
                        "departments": departments,
                        "strategic_initiatives": strategic_focus
                    }
                    
                    # Run organizational assessment
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    assessment = loop.run_until_complete(
                        st.session_state.sdk.assess_organizational_skills(org_data)
                    )
                    
                    if assessment.get("success"):
                        st.success("✅ Organizational analysis completed!")
                        
                        # Display results
                        st.markdown("### 📊 Analysis Results")
                        
                        # Overall metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Employees", total_employees)
                        with col2:
                            st.metric("Departments", len(departments))
                        with col3:
                            unique_skills = set()
                            for dept in departments:
                                unique_skills.update(dept["key_skills"])
                            st.metric("Unique Skills", len(unique_skills))
                        with col4:
                            st.metric("Strategic Initiatives", len(strategic_focus))
                        
                        # Department analysis
                        st.markdown("### 🏬 Department Breakdown")
                        
                        dept_data = []
                        for dept in departments:
                            dept_data.append({
                                "Department": dept["name"],
                                "Staff Count": dept["staff_count"],
                                "Key Skills": ", ".join(dept["key_skills"]),
                                "Skills Count": len(dept["key_skills"])
                            })
                        
                        dept_df = pd.DataFrame(dept_data)
                        st.dataframe(dept_df)
                        
                        # Visualization
                        fig = px.pie(
                            dept_df,
                            values="Staff Count",
                            names="Department",
                            title="Staff Distribution by Department"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Skills distribution
                        st.markdown("### 🎯 Skills Distribution")
                        
                        skills_count = {}
                        for dept in departments:
                            for skill in dept["key_skills"]:
                                skills_count[skill] = skills_count.get(skill, 0) + dept["staff_count"]
                        
                        skills_df = pd.DataFrame([
                            {"Skill": skill, "Employee Count": count}
                            for skill, count in skills_count.items()
                        ])
                        
                        fig = px.bar(
                            skills_df,
                            x="Skill",
                            y="Employee Count",
                            title="Skills Distribution Across Organization"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Strategic recommendations
                        st.markdown("### 💡 Strategic Recommendations")
                        recommendations = [
                            "Invest in AI/ML training programs for technical staff",
                            "Establish cross-functional teams for digital transformation",
                            "Create centers of excellence for emerging technologies",
                            "Implement comprehensive skills assessment program"
                        ]
                        
                        for i, rec in enumerate(recommendations, 1):
                            st.write(f"{i}. {rec}")
                    
                    else:
                        st.error(f"❌ Analysis failed: {assessment.get('error')}")
                
                except Exception as e:
                    st.error(f"❌ Error analyzing organization: {str(e)}")
    
    with tab6:
        st.markdown('<div class="sub-header">📊 Skills Insights & Analytics</div>', unsafe_allow_html=True)
        
        # Skills insights interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔍 Skill Analysis")
            skill_code = st.text_input("Skill Code", value="PROG", help="Enter SFIA skill code")
            
            if st.button("📈 Analyze Skill"):
                with st.spinner(f"Analyzing skill: {skill_code}"):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        insights = loop.run_until_complete(
                            st.session_state.sdk.get_skill_insights(skill_code)
                        )
                        
                        if insights.get("success"):
                            st.success(f"✅ Analysis completed for {skill_code}")
                            
                            # Basic skill information
                            skills_info = insights.get("basic_info", [])
                            if skills_info:
                                st.markdown("##### 📋 Skill Information")
                                for skill in skills_info[:3]:  # Show top 3
                                    st.write(f"**Skill**: {skill.get('skill_name', skill_code)}")
                                    st.write(f"**Category**: {skill.get('category', 'Unknown')}")
                                    st.write(f"**Level**: {skill.get('level', 'N/A')}")
                            
                            # Similar skills
                            similar_skills = insights.get("insights", {}).get("similar_skills", [])
                            if similar_skills:
                                st.markdown("##### 🔗 Similar Skills")
                                for similar in similar_skills[:5]:
                                    st.write(f"• {similar}")
                        
                        else:
                            st.error(f"❌ Failed to analyze skill: {insights.get('error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error analyzing skill: {str(e)}")
        
        with col2:
            st.markdown("#### 🎯 Skills Queries")
            
            # Query form
            with st.form("skills_query"):
                category_filter = st.text_input("Category Filter", placeholder="e.g., Technical")
                level_filter = st.number_input("Level Filter", min_value=1, max_value=7, value=3)
                keyword_filter = st.text_input("Keyword Filter", placeholder="e.g., programming")
                
                submitted = st.form_submit_button("🔍 Search Skills")
                
                if submitted:
                    with st.spinner("Searching skills..."):
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            skills_results = loop.run_until_complete(
                                st.session_state.sdk.query_skills(
                                    category=category_filter if category_filter else None,
                                    level=level_filter,
                                    keyword=keyword_filter if keyword_filter else None
                                )
                            )
                            
                            if skills_results.get("success"):
                                skills = skills_results.get("skills", [])
                                st.success(f"✅ Found {len(skills)} skills")
                                
                                if skills:
                                    # Display skills table
                                    skills_df = pd.DataFrame(skills)
                                    st.dataframe(skills_df)
                                else:
                                    st.info("No skills found matching the criteria")
                            
                            else:
                                st.error(f"❌ Search failed: {skills_results.get('error')}")
                        
                        except Exception as e:
                            st.error(f"❌ Error searching skills: {str(e)}")
        
        # Skills analytics dashboard
        st.markdown("### 📊 Skills Analytics Dashboard")
        
        if st.button("📈 Generate Analytics"):
            with st.spinner("Generating skills analytics..."):
                try:
                    # Sample analytics data (in real implementation, this would come from the knowledge graph)
                    analytics_data = {
                        "skill_levels": {
                            "Level 1": 15,
                            "Level 2": 25,
                            "Level 3": 35,
                            "Level 4": 20,
                            "Level 5": 15,
                            "Level 6": 8,
                            "Level 7": 5
                        },
                        "skill_categories": {
                            "Strategy and architecture": 12,
                            "Change and transformation": 8,
                            "Development and implementation": 45,
                            "Delivery and operation": 30,
                            "Skills and quality": 15,
                            "Relationships and engagement": 10
                        },
                        "trending_skills": [
                            {"skill": "MLNG", "growth": 45},
                            {"skill": "DTAN", "growth": 38},
                            {"skill": "SCTY", "growth": 32},
                            {"skill": "ARCH", "growth": 28},
                            {"skill": "PROG", "growth": 25}
                        ]
                    }
                    
                    # Skills by level
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📊 Skills by Level")
                        levels_df = pd.DataFrame([
                            {"Level": level, "Count": count}
                            for level, count in analytics_data["skill_levels"].items()
                        ])
                        
                        fig = px.bar(
                            levels_df,
                            x="Level",
                            y="Count",
                            title="Skills Distribution by SFIA Level"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("#### 🎯 Skills by Category")
                        categories_df = pd.DataFrame([
                            {"Category": cat[:20] + "..." if len(cat) > 20 else cat, "Count": count}
                            for cat, count in analytics_data["skill_categories"].items()
                        ])
                        
                        fig = px.pie(
                            categories_df,
                            values="Count",
                            names="Category",
                            title="Skills Distribution by Category"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Trending skills
                    st.markdown("#### 🚀 Trending Skills")
                    trending_df = pd.DataFrame(analytics_data["trending_skills"])
                    
                    fig = px.bar(
                        trending_df,
                        x="skill",
                        y="growth",
                        title="Skills Growth Trends (%)",
                        color="growth",
                        color_continuous_scale="viridis"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.success("✅ Analytics generated successfully!")
                
                except Exception as e:
                    st.error(f"❌ Error generating analytics: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "🧠 **SFIA AI Framework** - Intelligent Skills Analysis with Multi-Agent AI | "
    "Built with Streamlit, CrewAI, Neo4j, and OpenAI"
)