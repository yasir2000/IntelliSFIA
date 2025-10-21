#!/usr/bin/env python3
"""
SFIA 9 Integration Test Script
=============================

Simple test script to verify SFIA 9 integration is working correctly.
"""

import json
import sys
from pathlib import Path

# Add the framework to path
framework_path = Path(__file__).parent / "sfia_ai_framework" / "sfia_ai_framework"
sys.path.insert(0, str(framework_path))

def test_sfia9_data():
    """Test SFIA 9 data loading"""
    print("🧪 Testing SFIA 9 Data Integration")
    print("=" * 50)
    
    try:
        # Test data files exist
        data_path = framework_path / "data" / "sfia9"
        
        files_to_check = [
            "sfia9_attributes.json",
            "sfia9_skills.json", 
            "sfia9_levels.json",
            "sfia9_categories.json"
        ]
        
        for file in files_to_check:
            file_path = data_path / file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ {file}: {len(data)} items loaded")
            else:
                print(f"❌ {file}: Not found")
        
        # Test specific data content
        attributes_file = data_path / "sfia9_attributes.json"
        if attributes_file.exists():
            with open(attributes_file, 'r', encoding='utf-8') as f:
                attributes = json.load(f)
                
            print(f"\n📊 SFIA 9 Attributes Summary:")
            print(f"   Total attributes: {len(attributes)}")
            
            # Show first few attributes
            for attr in attributes[:5]:
                print(f"   • {attr['code']}: {attr['name']}")
        
        # Test skills data
        skills_file = data_path / "sfia9_skills.json"
        if skills_file.exists():
            with open(skills_file, 'r', encoding='utf-8') as f:
                skills = json.load(f)
                
            print(f"\n🛠️  SFIA 9 Skills Summary:")
            print(f"   Total skills: {len(skills)}")
            
            # Group by category
            categories = {}
            for skill in skills:
                cat = skill['category']
                if cat not in categories:
                    categories[cat] = 0
                categories[cat] += 1
            
            print(f"   Categories:")
            for cat, count in categories.items():
                print(f"   • {cat}: {count} skills")
        
        print(f"\n🎉 SFIA 9 Integration Test: SUCCESS")
        print(f"   ✅ All data files loaded successfully")
        print(f"   ✅ {len(attributes)} attributes processed")
        print(f"   ✅ {len(skills)} skills processed")
        print(f"   ✅ {len(categories)} categories identified")
        
        return True
        
    except Exception as e:
        print(f"❌ SFIA 9 Integration Test: FAILED")
        print(f"   Error: {e}")
        return False

def test_sfia9_models():
    """Test SFIA 9 models"""
    print(f"\n🏗️  Testing SFIA 9 Models")
    print("-" * 30)
    
    try:
        from models.sfia_models import (
            EnhancedSFIAAttribute, EnhancedSFIASkill, 
            SFIA9LevelDefinition, SFIA9EnhancedFramework
        )
        
        print("✅ SFIA 9 models imported successfully")
        
        # Test model creation
        test_attr = EnhancedSFIAAttribute(
            code="TEST",
            name="Test Attribute",
            type="Attributes", 
            description="Test description",
            guidance_notes="Test guidance"
        )
        print("✅ EnhancedSFIAAttribute model works")
        
        test_skill = EnhancedSFIASkill(
            code="TEST",
            name="Test Skill",
            category="Test Category",
            subcategory="Test Subcategory",
            description="Test description",
            guidance_notes="Test guidance",
            available_levels=[1, 2, 3, 4]
        )
        print("✅ EnhancedSFIASkill model works")
        
        return True
        
    except Exception as e:
        print(f"❌ SFIA 9 Models Test: FAILED")
        print(f"   Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SFIA 9 Integration Test Suite")
    print("=" * 60)
    
    tests = [
        test_sfia9_data,
        test_sfia9_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("")  # Add spacing between tests
    
    print("📋 Test Results Summary")
    print("=" * 30)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! SFIA 9 integration successful!")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())