"""
SFIA AI SDK Examples and Real-World Scenarios

This module provides comprehensive examples demonstrating how to use the SFIA AI SDK
for various real-world scenarios including hiring optimization, career development,
team formation, and organizational skills assessment.
"""

import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta

from ..sdk import SFIASDK, SFIASDKConfig, SFIASDKContext


class SFIAScenarios:
    """Real-world scenarios demonstrating SFIA AI capabilities"""
    
    def __init__(self, sdk: SFIASDK):
        self.sdk = sdk
    
    async def hiring_optimization_scenario(self) -> Dict[str, Any]:
        """
        Scenario: Tech company needs to hire for multiple roles
        Challenge: Optimize hiring decisions based on skills, team fit, and career growth potential
        """
        
        scenario_data = {
            "company": "TechCorp Inc.",
            "open_positions": [
                {
                    "role": "Senior Software Engineer",
                    "required_skills": ["PROG", "SENG", "ARCH"],
                    "team": "Product Development",
                    "urgency": "high"
                },
                {
                    "role": "DevOps Engineer", 
                    "required_skills": ["DTAN", "ITOP", "ITMG"],
                    "team": "Infrastructure",
                    "urgency": "medium"
                },
                {
                    "role": "Data Scientist",
                    "required_skills": ["DTAN", "STAT", "PROG"],
                    "team": "Analytics",
                    "urgency": "low"
                }
            ],
            "candidates": [
                {
                    "id": "C001",
                    "name": "Alice Johnson",
                    "current_skills": ["PROG", "SENG", "TEST"],
                    "experience_years": 5,
                    "current_role": "Software Engineer",
                    "career_goals": ["Technical Leadership", "Solution Architecture"]
                },
                {
                    "id": "C002", 
                    "name": "Bob Smith",
                    "current_skills": ["DTAN", "ITOP", "NTAN"],
                    "experience_years": 7,
                    "current_role": "Systems Administrator",
                    "career_goals": ["DevOps Leadership", "Cloud Architecture"]
                },
                {
                    "id": "C003",
                    "name": "Carol Davis",
                    "current_skills": ["DTAN", "STAT", "RSCH"],
                    "experience_years": 4,
                    "current_role": "Business Analyst",
                    "career_goals": ["Data Science", "ML Engineering"]
                }
            ]
        }
        
        results = {
            "scenario": "Hiring Optimization",
            "company": scenario_data["company"],
            "analysis_date": datetime.now().isoformat(),
            "position_analysis": [],
            "recommendations": []
        }
        
        # Analyze each position
        for position in scenario_data["open_positions"]:
            position_analysis = {
                "position": position["role"],
                "candidate_fits": []
            }
            
            # Assess each candidate for this position
            for candidate in scenario_data["candidates"]:
                fit_assessment = await self.sdk.assess_role_fit(
                    candidate["current_skills"],
                    {
                        "required_skills": position["required_skills"],
                        "role": position["role"]
                    }
                )
                
                # Get skill gaps
                gap_analysis = await self.sdk.analyze_skill_gaps(
                    candidate["current_role"],
                    position["role"]
                )
                
                candidate_fit = {
                    "candidate": candidate["name"],
                    "candidate_id": candidate["id"],
                    "fit_score": fit_assessment.get("assessment", {}).get("overall_score", 0),
                    "skill_gaps": gap_analysis.get("skill_gaps", []),
                    "development_potential": self._assess_development_potential(
                        candidate, position
                    )
                }
                
                position_analysis["candidate_fits"].append(candidate_fit)
            
            # Sort candidates by fit score
            position_analysis["candidate_fits"].sort(
                key=lambda x: x["fit_score"], reverse=True
            )
            
            results["position_analysis"].append(position_analysis)
        
        # Generate hiring recommendations
        results["recommendations"] = self._generate_hiring_recommendations(
            scenario_data, results["position_analysis"]
        )
        
        return results
    
    async def career_development_scenario(self) -> Dict[str, Any]:
        """
        Scenario: Individual career development planning
        Challenge: Create personalized development path with specific learning resources
        """
        
        employee_profile = {
            "name": "Sarah Wilson",
            "employee_id": "E12345",
            "current_role": "Junior Developer",
            "current_skills": ["PROG", "TEST"],
            "skill_levels": {"PROG": 2, "TEST": 2},
            "experience_years": 2,
            "career_aspirations": [
                "Senior Software Engineer",
                "Technical Lead",
                "Solution Architect"
            ],
            "learning_preferences": ["online_courses", "mentorship", "hands_on_projects"],
            "time_availability": "10 hours per week"
        }
        
        results = {
            "scenario": "Career Development Planning",
            "employee": employee_profile["name"],
            "analysis_date": datetime.now().isoformat(),
            "current_assessment": {},
            "career_pathways": [],
            "development_plan": {}
        }
        
        # Current skills assessment
        for aspiration in employee_profile["career_aspirations"]:
            gap_analysis = await self.sdk.analyze_skill_gaps(
                employee_profile["current_role"],
                aspiration
            )
            
            career_path = {
                "target_role": aspiration,
                "skill_gaps": gap_analysis.get("skill_gaps", []),
                "estimated_timeline": self._estimate_development_timeline(
                    gap_analysis.get("skill_gaps", []),
                    employee_profile["time_availability"]
                )
            }
            
            results["career_pathways"].append(career_path)
        
        # Generate comprehensive development plan
        primary_goal = employee_profile["career_aspirations"][0]
        development_plan = await self.sdk.generate_development_plan(
            employee_profile, primary_goal
        )
        
        results["development_plan"] = development_plan
        
        # Add personalized learning recommendations
        critical_skills = [
            gap["skill_code"] for gap in 
            development_plan.get("skill_gap_analysis", {}).get("skill_gaps", [])[:3]
        ]
        
        if critical_skills:
            learning_recs = await self.sdk.get_learning_recommendations(critical_skills)
            results["learning_recommendations"] = learning_recs.get("learning_recommendations", [])
        
        return results
    
    async def team_formation_scenario(self) -> Dict[str, Any]:
        """
        Scenario: Forming optimal teams for multiple projects
        Challenge: Balance skills, workload, and development opportunities
        """
        
        project_portfolio = {
            "organization": "InnovaCorp",
            "projects": [
                {
                    "name": "Mobile Banking App",
                    "duration": "6 months",
                    "required_skills": ["PROG", "MOBP", "UNAN", "TEST", "SCTY"],
                    "team_size": 6,
                    "priority": "high"
                },
                {
                    "name": "Data Analytics Platform",
                    "duration": "9 months", 
                    "required_skills": ["DTAN", "PROG", "DBAD", "VISL", "STAT"],
                    "team_size": 5,
                    "priority": "medium"
                },
                {
                    "name": "Cloud Migration",
                    "duration": "12 months",
                    "required_skills": ["ITOP", "ARCH", "NTAN", "SCTY", "ITMG"],
                    "team_size": 4,
                    "priority": "high"
                }
            ],
            "available_staff": [
                {
                    "name": "Alice Chen",
                    "skills": ["PROG", "MOBP", "TEST"],
                    "current_project": None,
                    "development_goals": ["ARCH", "UNAN"]
                },
                {
                    "name": "Bob Rodriguez",
                    "skills": ["DTAN", "STAT", "PROG"],
                    "current_project": None,
                    "development_goals": ["VISL", "MLNG"]
                },
                {
                    "name": "Carol Kim",
                    "skills": ["ITOP", "NTAN", "SCTY"],
                    "current_project": None,
                    "development_goals": ["ARCH", "ITMG"]
                },
                {
                    "name": "David Brown",
                    "skills": ["PROG", "ARCH", "TEST"],
                    "current_project": None,
                    "development_goals": ["SENG", "TECH"]
                },
                {
                    "name": "Eva Martinez",
                    "skills": ["UNAN", "VISL", "TEST"],
                    "current_project": None,
                    "development_goals": ["DTAN", "RSCH"]
                }
            ]
        }
        
        results = {
            "scenario": "Team Formation Optimization",
            "organization": project_portfolio["organization"],
            "analysis_date": datetime.now().isoformat(),
            "project_teams": [],
            "optimization_metrics": {}
        }
        
        # Analyze each project for team optimization
        for project in project_portfolio["projects"]:
            team_optimization = await self.sdk.optimize_team_composition(
                {
                    "project_name": project["name"],
                    "required_skills": project["required_skills"],
                    "team_size": project["team_size"],
                    "duration": project["duration"]
                },
                project_portfolio["available_staff"]
            )
            
            project_team = {
                "project": project["name"],
                "optimization_result": team_optimization.get("optimization_result", {}),
                "skill_coverage": self._calculate_skill_coverage(
                    project["required_skills"],
                    team_optimization.get("optimization_result", {}).get("recommended_team", [])
                ),
                "development_opportunities": self._identify_development_opportunities(
                    project["required_skills"],
                    team_optimization.get("optimization_result", {}).get("recommended_team", [])
                )
            }
            
            results["project_teams"].append(project_team)
        
        # Calculate overall optimization metrics
        results["optimization_metrics"] = self._calculate_portfolio_metrics(
            project_portfolio, results["project_teams"]
        )
        
        return results
    
    async def organizational_assessment_scenario(self) -> Dict[str, Any]:
        """
        Scenario: Organization-wide skills assessment and strategic planning
        Challenge: Identify skills gaps and plan workforce development strategy
        """
        
        organization_data = {
            "company": "TechSolutions Ltd",
            "departments": [
                {
                    "name": "Software Development",
                    "staff_count": 45,
                    "key_skills": ["PROG", "SENG", "TEST", "ARCH"],
                    "current_projects": ["ERP System", "Mobile Platform", "API Gateway"]
                },
                {
                    "name": "Data & Analytics",
                    "staff_count": 20,
                    "key_skills": ["DTAN", "STAT", "VISL", "RSCH"],
                    "current_projects": ["Business Intelligence", "Predictive Analytics"]
                },
                {
                    "name": "Infrastructure",
                    "staff_count": 15,
                    "key_skills": ["ITOP", "NTAN", "SCTY", "ITMG"],
                    "current_projects": ["Cloud Migration", "Security Hardening"]
                }
            ],
            "strategic_initiatives": [
                "Digital Transformation",
                "AI/ML Adoption", 
                "Cloud-First Strategy",
                "Cybersecurity Enhancement"
            ],
            "market_trends": [
                "Increased demand for cloud skills",
                "Growing importance of data science",
                "Rising cybersecurity threats",
                "Agile and DevOps practices"
            ]
        }
        
        # Perform organizational assessment
        assessment = await self.sdk.assess_organizational_skills(organization_data)
        
        results = {
            "scenario": "Organizational Skills Assessment",
            "company": organization_data["company"],
            "analysis_date": datetime.now().isoformat(),
            "assessment_results": assessment.get("result", {}),
            "strategic_recommendations": self._generate_strategic_recommendations(
                organization_data, assessment.get("result", {})
            ),
            "workforce_planning": self._create_workforce_plan(
                organization_data, assessment.get("result", {})
            )
        }
        
        return results
    
    async def skills_gap_analysis_scenario(self) -> Dict[str, Any]:
        """
        Scenario: Industry skills gap analysis for strategic planning
        Challenge: Identify market trends and prepare workforce accordingly
        """
        
        industry_analysis = {
            "industry": "Financial Technology",
            "current_workforce": {
                "total_employees": 200,
                "skill_distribution": {
                    "PROG": 80,
                    "SENG": 45,
                    "TEST": 35,
                    "ARCH": 20,
                    "DTAN": 25,
                    "SCTY": 15,
                    "FINM": 30
                }
            },
            "future_requirements": {
                "ai_ml_adoption": ["MLNG", "DTAN", "STAT"],
                "blockchain_integration": ["PROG", "SCTY", "ARCH"],
                "regulatory_compliance": ["GOVN", "RSKM", "RLMT"],
                "customer_experience": ["UNAN", "VISL", "HCEV"]
            },
            "timeline": "2-year strategic plan"
        }
        
        results = {
            "scenario": "Industry Skills Gap Analysis",
            "industry": industry_analysis["industry"],
            "analysis_date": datetime.now().isoformat(),
            "current_state": industry_analysis["current_workforce"],
            "future_requirements": industry_analysis["future_requirements"],
            "gap_analysis": {},
            "strategic_plan": {}
        }
        
        # Analyze gaps for each future requirement area
        for area, required_skills in industry_analysis["future_requirements"].items():
            gap_analysis = {
                "area": area,
                "required_skills": required_skills,
                "current_capability": {},
                "gaps": [],
                "development_priority": ""
            }
            
            # Calculate current capability for required skills
            current_dist = industry_analysis["current_workforce"]["skill_distribution"]
            for skill in required_skills:
                current_count = current_dist.get(skill, 0)
                required_count = int(industry_analysis["current_workforce"]["total_employees"] * 0.3)  # 30% target
                
                if current_count < required_count:
                    gap_analysis["gaps"].append({
                        "skill": skill,
                        "current": current_count,
                        "required": required_count,
                        "gap": required_count - current_count
                    })
            
            # Determine priority
            total_gap = sum(gap["gap"] for gap in gap_analysis["gaps"])
            if total_gap > 50:
                gap_analysis["development_priority"] = "Critical"
            elif total_gap > 20:
                gap_analysis["development_priority"] = "High"
            else:
                gap_analysis["development_priority"] = "Medium"
            
            results["gap_analysis"][area] = gap_analysis
        
        # Generate strategic plan
        results["strategic_plan"] = self._create_skills_strategic_plan(
            industry_analysis, results["gap_analysis"]
        )
        
        return results
    
    # Helper methods
    def _assess_development_potential(self, candidate: Dict[str, Any], 
                                    position: Dict[str, Any]) -> str:
        """Assess candidate's development potential for a position"""
        current_skills = set(candidate["current_skills"])
        required_skills = set(position["required_skills"])
        
        overlap = len(current_skills.intersection(required_skills))
        gap = len(required_skills - current_skills)
        
        if overlap >= len(required_skills) * 0.8:
            return "High - Minimal development needed"
        elif overlap >= len(required_skills) * 0.5:
            return "Medium - Moderate development required"
        else:
            return "Low - Significant development needed"
    
    def _generate_hiring_recommendations(self, scenario_data: Dict[str, Any], 
                                       analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate hiring recommendations based on analysis"""
        recommendations = []
        
        for position_analysis in analysis:
            best_candidate = position_analysis["candidate_fits"][0] if position_analysis["candidate_fits"] else None
            
            if best_candidate:
                recommendation = {
                    "position": position_analysis["position"],
                    "recommended_candidate": best_candidate["candidate"],
                    "fit_score": best_candidate["fit_score"],
                    "reasoning": f"Best overall fit with {best_candidate['fit_score']:.2f} compatibility score",
                    "development_needed": len(best_candidate["skill_gaps"]),
                    "onboarding_timeline": "2-4 weeks" if len(best_candidate["skill_gaps"]) <= 2 else "1-2 months"
                }
                recommendations.append(recommendation)
        
        return recommendations
    
    def _estimate_development_timeline(self, skill_gaps: List[Dict[str, Any]], 
                                     time_availability: str) -> str:
        """Estimate timeline for skill development"""
        gap_count = len(skill_gaps)
        
        if "10 hours" in time_availability:
            if gap_count <= 2:
                return "3-6 months"
            elif gap_count <= 4:
                return "6-12 months"
            else:
                return "12-18 months"
        
        return "Timeline varies based on commitment"
    
    def _calculate_skill_coverage(self, required_skills: List[str], 
                                 team: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate how well team covers required skills"""
        coverage = {}
        
        for skill in required_skills:
            team_members_with_skill = [
                member for member in team 
                if skill in member.get("skills", [])
            ]
            coverage[skill] = {
                "covered": len(team_members_with_skill) > 0,
                "redundancy": len(team_members_with_skill),
                "team_members": [m["name"] for m in team_members_with_skill]
            }
        
        return coverage
    
    def _identify_development_opportunities(self, required_skills: List[str], 
                                          team: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify development opportunities for team members"""
        opportunities = []
        
        for member in team:
            member_skills = set(member.get("skills", []))
            missing_skills = set(required_skills) - member_skills
            development_goals = set(member.get("development_goals", []))
            
            relevant_opportunities = missing_skills.intersection(development_goals)
            
            if relevant_opportunities:
                opportunities.append({
                    "team_member": member["name"],
                    "development_skills": list(relevant_opportunities),
                    "learning_method": "On-the-job training during project"
                })
        
        return opportunities
    
    def _calculate_portfolio_metrics(self, portfolio: Dict[str, Any], 
                                   teams: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate portfolio-level optimization metrics"""
        total_staff = len(portfolio["available_staff"])
        allocated_staff = sum(
            len(team.get("optimization_result", {}).get("recommended_team", []))
            for team in teams
        )
        
        return {
            "staff_utilization": f"{(allocated_staff / total_staff) * 100:.1f}%",
            "skills_coverage": "95%",  # Would calculate based on actual coverage
            "development_opportunities": sum(
                len(team.get("development_opportunities", []))
                for team in teams
            ),
            "project_readiness": "High"
        }
    
    def _generate_strategic_recommendations(self, org_data: Dict[str, Any], 
                                          assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate strategic recommendations for organization"""
        return [
            {
                "area": "Skills Development",
                "recommendation": "Implement comprehensive upskilling program focusing on cloud and AI technologies",
                "priority": "High",
                "timeline": "6-12 months"
            },
            {
                "area": "Talent Acquisition",
                "recommendation": "Recruit specialists in cybersecurity and data science",
                "priority": "Medium",
                "timeline": "3-6 months"
            },
            {
                "area": "Knowledge Management",
                "recommendation": "Establish centers of excellence for emerging technologies",
                "priority": "Medium",
                "timeline": "9-12 months"
            }
        ]
    
    def _create_workforce_plan(self, org_data: Dict[str, Any], 
                             assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive workforce development plan"""
        return {
            "current_workforce": sum(dept["staff_count"] for dept in org_data["departments"]),
            "projected_needs": {
                "new_hires": 15,
                "internal_development": 25,
                "role_transitions": 8
            },
            "budget_allocation": {
                "training_programs": "40%",
                "external_recruitment": "35%",
                "knowledge_transfer": "25%"
            },
            "success_metrics": [
                "Skills gap reduction by 60%",
                "Employee satisfaction improvement",
                "Project delivery efficiency increase"
            ]
        }
    
    def _create_skills_strategic_plan(self, industry_data: Dict[str, Any], 
                                    gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create strategic plan for addressing skills gaps"""
        return {
            "executive_summary": "Strategic skills development plan to address critical gaps in AI/ML and blockchain technologies",
            "key_initiatives": [
                {
                    "name": "AI/ML Skills Development Program",
                    "duration": "18 months",
                    "target_skills": ["MLNG", "DTAN", "STAT"],
                    "approach": "Internal training + external partnerships"
                },
                {
                    "name": "Blockchain Competency Center",
                    "duration": "12 months", 
                    "target_skills": ["PROG", "SCTY", "ARCH"],
                    "approach": "Specialized recruitment + certification programs"
                }
            ],
            "investment_required": "$2.5M over 2 years",
            "expected_outcomes": {
                "skills_gap_reduction": "70%",
                "innovation_capacity": "Increased by 40%",
                "market_competitiveness": "Top quartile in fintech"
            },
            "risk_mitigation": [
                "Phased implementation to manage change",
                "Partnership with educational institutions",
                "Retention strategies for developed talent"
            ]
        }


# Example usage and demonstrations
async def run_all_scenarios():
    """Run all scenarios with sample data"""
    
    # Configuration for SDK
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        openai_api_key="your-openai-key-here",  # Replace with actual key
        enable_agents=True,
        enable_reasoning=True
    )
    
    async with SFIASDKContext(config) as sdk:
        # Load SFIA ontology
        await sdk.load_sfia_ontology("../../SFIA_9_2025-10-21.ttl")
        
        scenarios = SFIAScenarios(sdk)
        
        print("Running SFIA AI Framework Scenarios...")
        print("=" * 50)
        
        # Run all scenarios
        scenario_results = {}
        
        print("\n1. Hiring Optimization Scenario")
        scenario_results["hiring"] = await scenarios.hiring_optimization_scenario()
        print(f"✅ Analyzed {len(scenario_results['hiring']['position_analysis'])} positions")
        
        print("\n2. Career Development Scenario")
        scenario_results["career"] = await scenarios.career_development_scenario()
        print(f"✅ Generated development plan with {len(scenario_results['career']['career_pathways'])} pathways")
        
        print("\n3. Team Formation Scenario")
        scenario_results["team"] = await scenarios.team_formation_scenario()
        print(f"✅ Optimized teams for {len(scenario_results['team']['project_teams'])} projects")
        
        print("\n4. Organizational Assessment Scenario")
        scenario_results["organization"] = await scenarios.organizational_assessment_scenario()
        print("✅ Completed organization-wide skills assessment")
        
        print("\n5. Skills Gap Analysis Scenario")
        scenario_results["skills_gap"] = await scenarios.skills_gap_analysis_scenario()
        print("✅ Analyzed industry-wide skills gaps and strategic planning")
        
        # Save results
        with open("sfia_scenarios_results.json", "w") as f:
            json.dump(scenario_results, f, indent=2, default=str)
        
        print(f"\n📊 All scenario results saved to 'sfia_scenarios_results.json'")
        print(f"🎯 SFIA AI Framework demonstration completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_all_scenarios())