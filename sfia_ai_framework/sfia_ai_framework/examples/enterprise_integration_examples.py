"""
Enterprise Integration Usage Examples

This module demonstrates how to use IntelliSFIA's enterprise integration
capabilities to automatically analyze SFIA levels from business systems.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

# Example 1: Basic Enterprise Integration Setup
async def example_basic_setup():
    """Example of basic enterprise integration setup"""
    print("=== Example 1: Basic Enterprise Integration Setup ===")
    
    from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig
    from sfia_ai_framework.enterprise import EnterpriseIntegrationManager
    
    # Configure SDK
    config = SFIASDKConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        openai_api_key="your-openai-key-here"
    )
    
    # Initialize SDK
    sdk = SFIASDK(config)
    await sdk.initialize()
    
    # Initialize enterprise integration
    result = await sdk.initialize_enterprise_integration(
        integration_config_path="../config/integration_config.yaml"
    )
    
    if result.success:
        print("✅ Enterprise integration initialized successfully")
        
        # Check system health
        health_status = await sdk.get_system_health_status()
        print(f"Connected systems: {len(health_status.get('systems', {}))}")
    else:
        print(f"❌ Failed to initialize: {result.message}")
    
    await sdk.close()


# Example 2: Real-time Employee Analysis
async def example_real_time_analysis():
    """Example of real-time employee SFIA analysis"""
    print("\n=== Example 2: Real-time Employee Analysis ===")
    
    from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig
    
    config = SFIASDKConfig()
    sdk = SFIASDK(config)
    await sdk.initialize()
    await sdk.initialize_enterprise_integration()
    
    # Analyze specific employee
    employee_id = "EMP001"
    result = await sdk.analyze_employee_sfia_levels(employee_id)
    
    if result.get("success"):
        print(f"📊 Analysis for Employee {employee_id}:")
        print(f"🕐 Timestamp: {result['analysis_timestamp']}")
        print(f"📈 Suggestions: {len(result['suggestions'])}")
        
        for suggestion in result['suggestions'][:3]:  # Show first 3
            print(f"  • {suggestion['skill_name']}: Level {suggestion['suggested_level']} "
                  f"(Confidence: {suggestion['confidence_score']:.1%})")
            print(f"    Reasoning: {suggestion['reasoning'][:100]}...")
    else:
        print(f"❌ Analysis failed: {result.get('error')}")
    
    await sdk.close()


# Example 3: Department-wide Analysis
async def example_department_analysis():
    """Example of analyzing an entire department"""
    print("\n=== Example 3: Department-wide Analysis ===")
    
    from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig
    
    config = SFIASDKConfig()
    sdk = SFIASDK(config)
    await sdk.initialize()
    await sdk.initialize_enterprise_integration()
    
    # Analyze IT department
    department = "Information Technology"
    result = await sdk.analyze_department_sfia_levels(department)
    
    if result.get("success"):
        print(f"📊 Analysis for {department} Department:")
        print(f"👥 Employees analyzed: {len(result['employees'])}")
        
        # Calculate department statistics
        total_suggestions = sum(len(suggestions) for suggestions in result['employees'].values())
        avg_levels = []
        avg_confidences = []
        
        for employee_id, suggestions in result['employees'].items():
            if suggestions:
                emp_avg_level = sum(s['suggested_level'] for s in suggestions) / len(suggestions)
                emp_avg_confidence = sum(s['confidence_score'] for s in suggestions) / len(suggestions)
                avg_levels.append(emp_avg_level)
                avg_confidences.append(emp_avg_confidence)
                
                print(f"  • {employee_id}: {len(suggestions)} skills, "
                      f"avg level {emp_avg_level:.1f}, "
                      f"confidence {emp_avg_confidence:.1%}")
        
        if avg_levels:
            dept_avg_level = sum(avg_levels) / len(avg_levels)
            dept_avg_confidence = sum(avg_confidences) / len(avg_confidences)
            print(f"\n📈 Department averages:")
            print(f"  Average SFIA Level: {dept_avg_level:.1f}")
            print(f"  Average Confidence: {dept_avg_confidence:.1%}")
    else:
        print(f"❌ Analysis failed: {result.get('error')}")
    
    await sdk.close()


# Example 4: Organization-wide Insights
async def example_organization_insights():
    """Example of getting organization-wide insights"""
    print("\n=== Example 4: Organization-wide Insights ===")
    
    from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig
    
    config = SFIASDKConfig()
    sdk = SFIASDK(config)
    await sdk.initialize()
    await sdk.initialize_enterprise_integration()
    
    # Get organization insights
    result = await sdk.get_organization_sfia_insights()
    
    if result.get("success"):
        print("🏢 Organization SFIA Insights:")
        print(f"👥 Total employees: {result.get('total_employees', 0)}")
        print(f"🏢 Departments: {len(result.get('departments', {}))}")
        print(f"🎯 Skills tracked: {len(result.get('skill_distribution', {}))}")
        
        # Show top departments
        if result.get('departments'):
            print(f"\n🏢 Top Departments by Employee Count:")
            dept_sorted = sorted(result['departments'].items(), 
                               key=lambda x: x[1].get('employee_count', 0), 
                               reverse=True)
            for dept_name, dept_data in dept_sorted[:5]:
                print(f"  • {dept_name}: {dept_data.get('employee_count', 0)} employees, "
                      f"avg level {dept_data.get('avg_level', 0):.1f}")
        
        # Show level distribution
        if result.get('level_distribution'):
            print(f"\n📈 SFIA Level Distribution:")
            for level, count in sorted(result['level_distribution'].items()):
                print(f"  Level {level}: {count} assignments")
        
        # Show high performers
        if result.get('high_performers'):
            print(f"\n⭐ High Performers ({len(result['high_performers'])}):")
            for performer in result['high_performers'][:5]:
                print(f"  • {performer['employee_id']}: {performer['skill']} "
                      f"Level {performer['level']} (confidence: {performer['confidence']:.1%})")
        
        # Show improvement opportunities
        if result.get('improvement_opportunities'):
            print(f"\n💡 Improvement Opportunities ({len(result['improvement_opportunities'])}):")
            for opp in result['improvement_opportunities'][:5]:
                print(f"  • {opp['employee_id']}: {opp['skill']} "
                      f"(current level {opp['current_level']})")
                if opp.get('improvements'):
                    print(f"    - {opp['improvements'][0]}")
    else:
        print(f"❌ Failed to get insights: {result.get('error')}")
    
    await sdk.close()


# Example 5: Real-time Callback System
async def example_real_time_callbacks():
    """Example of setting up real-time callbacks for continuous monitoring"""
    print("\n=== Example 5: Real-time Callback System ===")
    
    from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig
    
    # Define callback function
    async def sfia_analysis_callback(event_type: str, data):
        """Callback function for real-time SFIA analysis events"""
        if event_type == 'real_time_analysis':
            employee_id = data['employee_id']
            suggestions = data['suggestions']
            print(f"🔔 Real-time analysis for {employee_id}: {len(suggestions)} suggestions")
            
            # Check for significant changes
            high_confidence_suggestions = [s for s in suggestions if s.confidence_score > 0.9]
            if high_confidence_suggestions:
                print(f"  ⚡ High confidence suggestions: {len(high_confidence_suggestions)}")
                
        elif event_type == 'batch_analysis':
            print(f"📊 Batch analysis completed for {len(data)} employees")
            
        elif event_type == 'health_check':
            unhealthy_systems = [name for name, health in data.items() 
                               if health['status'] != 'healthy']
            if unhealthy_systems:
                print(f"🚨 Unhealthy systems detected: {unhealthy_systems}")
    
    config = SFIASDKConfig()
    sdk = SFIASDK(config)
    await sdk.initialize()
    await sdk.initialize_enterprise_integration()
    
    # Register callback
    result = await sdk.register_real_time_callback(sfia_analysis_callback)
    if result.success:
        print("✅ Real-time callback registered successfully")
        print("🔄 System is now monitoring for real-time SFIA analysis events...")
        
        # Simulate waiting for real-time events
        print("⏰ Waiting for events (this would run continuously in production)...")
        await asyncio.sleep(5)  # In production, this would run indefinitely
    else:
        print(f"❌ Failed to register callback: {result.message}")
    
    await sdk.close()


# Example 6: SFIA Compliance Report Generation
async def example_compliance_report():
    """Example of generating SFIA compliance reports"""
    print("\n=== Example 6: SFIA Compliance Report Generation ===")
    
    from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig
    
    config = SFIASDKConfig()
    sdk = SFIASDK(config)
    await sdk.initialize()
    await sdk.initialize_enterprise_integration()
    
    # Generate organization-wide compliance report
    result = await sdk.generate_sfia_compliance_report()
    
    if result.get("success"):
        print("📋 SFIA Compliance Report Generated:")
        print(f"🎯 Scope: {result['scope']}")
        print(f"🕐 Generated: {result['generated_at']}")
        
        summary = result['summary']
        print(f"\n📊 Compliance Summary:")
        print(f"  👥 Employees Analyzed: {summary['total_employees_analyzed']}")
        print(f"  🎯 Skills Assessed: {summary['skills_assessed']}")
        print(f"  📈 Average Confidence: {summary['average_confidence_score']:.1%}")
        print(f"  ✅ Compliance Rate: {summary['compliance_percentage']:.1%}")
        
        # Show level distribution
        if result.get('level_distribution'):
            print(f"\n📈 Level Distribution:")
            for level, count in sorted(result['level_distribution'].items()):
                print(f"  Level {level}: {count} assignments")
        
        # Show recommendations
        if result.get('recommendations'):
            print(f"\n💡 Top Recommendations:")
            for rec in result['recommendations'][:3]:
                print(f"  • {rec}")
        
        # Save report to file
        report_filename = f"sfia_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Report saved to: {report_filename}")
    else:
        print(f"❌ Failed to generate report: {result.get('error')}")
    
    await sdk.close()


# Example 7: Custom Enterprise System Integration
async def example_custom_system_integration():
    """Example of integrating a custom enterprise system"""
    print("\n=== Example 7: Custom Enterprise System Integration ===")
    
    from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig
    
    config = SFIASDKConfig()
    sdk = SFIASDK(config)
    await sdk.initialize()
    await sdk.initialize_enterprise_integration()
    
    # Add custom database connection
    database_credentials = {
        'system_type': 'postgresql',
        'connection_string': 'postgresql://user:password@localhost:5432/hr_db'
    }
    
    database_config = {
        'schema': 'hr',
        'timeout': 15,
        'employees_table': 'employees',
        'activities_table': 'task_activities',
        'performance_table': 'performance_metrics'
    }
    
    result = await sdk.add_enterprise_system(
        system_name='hr_database',
        system_type='database',
        credentials=database_credentials,
        config=database_config
    )
    
    if result.success:
        print("✅ Custom HR database connected successfully")
        
        # Add SAP integration
        sap_credentials = {
            'system_type': 'sap',
            'endpoint': 'https://sap.company.com:8443',
            'username': 'SFIA_USER',
            'password': 'secure_password'
        }
        
        sap_config = {
            'client': '100',
            'language': 'EN',
            'timeout': 30
        }
        
        sap_result = await sdk.add_enterprise_system(
            system_name='sap_production',
            system_type='sap',
            credentials=sap_credentials,
            config=sap_config
        )
        
        if sap_result.success:
            print("✅ SAP system connected successfully")
            
            # Check health of all systems
            health_status = await sdk.get_system_health_status()
            print(f"\n🏥 System Health Status:")
            for system_name, health in health_status.get('systems', {}).items():
                status_icon = "✅" if health['status'] == 'healthy' else "❌"
                print(f"  {status_icon} {system_name}: {health['status']}")
        else:
            print(f"❌ SAP connection failed: {sap_result.message}")
    else:
        print(f"❌ Database connection failed: {result.message}")
    
    await sdk.close()


# Example 8: CLI Usage Examples
def example_cli_usage():
    """Example CLI commands for enterprise integration"""
    print("\n=== Example 8: CLI Usage Examples ===")
    
    cli_commands = [
        # Initialize enterprise integration
        "intellisfia enterprise init --config config/integration_config.yaml",
        
        # Analyze specific employee
        "intellisfia enterprise analyze_employee --employee-id EMP001 --format table",
        
        # Analyze department
        "intellisfia enterprise analyze_department --department 'IT' --format summary",
        
        # Get organization insights
        "intellisfia enterprise insights --format dashboard",
        
        # Generate compliance report
        "intellisfia enterprise compliance_report --department 'Engineering' --output report.json",
        
        # Check system health
        "intellisfia enterprise health",
        
        # Interactive shell
        "intellisfia shell"
    ]
    
    print("💻 CLI Command Examples:")
    for i, cmd in enumerate(cli_commands, 1):
        print(f"{i:2d}. {cmd}")
    
    print("\n📚 For more CLI options, run: intellisfia enterprise --help")


# Main execution function
async def run_all_examples():
    """Run all enterprise integration examples"""
    print("🚀 IntelliSFIA Enterprise Integration Examples")
    print("=" * 60)
    
    try:
        # Run examples (some may need actual systems to work)
        await example_basic_setup()
        await example_real_time_analysis()
        await example_department_analysis()
        await example_organization_insights()
        await example_real_time_callbacks()
        await example_compliance_report()
        await example_custom_system_integration()
        
        # CLI examples (informational only)
        example_cli_usage()
        
        print("\n✅ All examples completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Configure your enterprise systems in integration_config.yaml")
        print("2. Set up Redis for caching and real-time processing")
        print("3. Initialize enterprise integration: intellisfia enterprise init")
        print("4. Start analyzing your workforce: intellisfia enterprise insights")
        
    except Exception as e:
        print(f"\n❌ Example execution failed: {e}")
        print("Note: Some examples require actual enterprise systems to be configured")


if __name__ == "__main__":
    asyncio.run(run_all_examples())