"""
SFIA AI Framework - Comprehensive Test Suite

This module provides comprehensive testing for all components of the SFIA AI Framework
including unit tests, integration tests, and scenario validation.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any

# Test imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfia_ai_framework.sdk import SFIASDK, SFIASDKConfig, SFIASDKContext
from sfia_ai_framework.core.agents import SFIAAgentCrew, create_sfia_agent_crew
from sfia_ai_framework.core.knowledge_graph import SFIAKnowledgeGraph, create_sfia_knowledge_graph
from sfia_ai_framework.core.reasoning import SFIAReasoningEngine, create_sfia_reasoning_engine
from sfia_ai_framework.examples.scenarios import SFIAScenarios
from sfia_ai_framework.models.sfia_models import Skill, SkillLevel, ProfessionalRole, APIResponse


class TestSFIASDKConfig:
    """Test SFIA SDK Configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = SFIASDKConfig()
        
        assert config.neo4j_uri == "bolt://localhost:7687"
        assert config.neo4j_user == "neo4j"
        assert config.neo4j_password == "password"
        assert config.openai_api_key is None
        assert config.enable_agents is True
        assert config.enable_reasoning is True
        assert config.log_level == "INFO"
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = SFIASDKConfig(
            neo4j_uri="bolt://custom:7687",
            neo4j_user="custom_user",
            neo4j_password="custom_password",
            openai_api_key="test_key",
            enable_agents=False,
            enable_reasoning=False,
            log_level="DEBUG"
        )
        
        assert config.neo4j_uri == "bolt://custom:7687"
        assert config.neo4j_user == "custom_user"
        assert config.neo4j_password == "custom_password"
        assert config.openai_api_key == "test_key"
        assert config.enable_agents is False
        assert config.enable_reasoning is False
        assert config.log_level == "DEBUG"


class TestSFIASDK:
    """Test SFIA SDK Core Functionality"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing"""
        return SFIASDKConfig(
            neo4j_uri="bolt://test:7687",
            neo4j_user="test",
            neo4j_password="test",
            openai_api_key="test_key"
        )
    
    @pytest.fixture
    def sdk(self, mock_config):
        """Create SDK instance for testing"""
        return SFIASDK(mock_config)
    
    def test_sdk_initialization(self, sdk, mock_config):
        """Test SDK initialization"""
        assert sdk.config == mock_config
        assert sdk.knowledge_graph is None
        assert sdk.reasoning_engine is None
        assert sdk.agent_crew is None
        assert sdk._initialized is False
    
    def test_ensure_initialized_raises_error(self, sdk):
        """Test that operations fail when SDK is not initialized"""
        with pytest.raises(RuntimeError, match="SDK not initialized"):
            sdk._ensure_initialized()
    
    @pytest.mark.asyncio
    @patch('sfia_ai_framework.sdk.create_sfia_knowledge_graph')
    @patch('sfia_ai_framework.sdk.create_sfia_reasoning_engine')
    @patch('sfia_ai_framework.sdk.create_sfia_agent_crew')
    async def test_sdk_initialize_success(self, mock_agent_crew, mock_reasoning, mock_kg, sdk, mock_config):
        """Test successful SDK initialization"""
        # Mock the creation functions
        mock_kg_instance = AsyncMock()
        mock_reasoning_instance = AsyncMock()
        mock_agent_crew_instance = AsyncMock()
        
        mock_kg.return_value = mock_kg_instance
        mock_reasoning.return_value = mock_reasoning_instance
        mock_agent_crew.return_value = mock_agent_crew_instance
        
        # Mock the initialize_ml_models method
        mock_reasoning_instance.initialize_ml_models = AsyncMock()
        
        # Initialize SDK
        await sdk.initialize()
        
        # Assertions
        assert sdk._initialized is True
        assert sdk.knowledge_graph == mock_kg_instance
        assert sdk.reasoning_engine == mock_reasoning_instance
        assert sdk.agent_crew == mock_agent_crew_instance
        
        # Verify function calls
        mock_kg.assert_called_once_with(
            mock_config.neo4j_uri,
            mock_config.neo4j_user,
            mock_config.neo4j_password
        )
        mock_reasoning.assert_called_once_with(mock_kg_instance)
        mock_reasoning_instance.initialize_ml_models.assert_called_once()
        mock_agent_crew.assert_called_once_with(mock_kg_instance, mock_reasoning_instance)
    
    @pytest.mark.asyncio
    async def test_sdk_close(self, sdk):
        """Test SDK cleanup"""
        # Mock knowledge graph
        mock_kg = AsyncMock()
        sdk.knowledge_graph = mock_kg
        sdk._initialized = True
        
        await sdk.close()
        
        mock_kg.close.assert_called_once()
        assert sdk._initialized is False


class TestSFIAKnowledgeGraph:
    """Test Knowledge Graph Functionality"""
    
    @pytest.fixture
    def mock_driver(self):
        """Mock Neo4j driver"""
        return Mock()
    
    @pytest.fixture
    def knowledge_graph(self, mock_driver):
        """Create knowledge graph instance for testing"""
        with patch('sfia_ai_framework.core.knowledge_graph.GraphDatabase.driver') as mock_driver_class:
            mock_driver_class.return_value = mock_driver
            kg = SFIAKnowledgeGraph("bolt://test:7687", "test", "test")
            return kg
    
    def test_knowledge_graph_initialization(self, knowledge_graph):
        """Test knowledge graph initialization"""
        assert knowledge_graph.uri == "bolt://test:7687"
        assert knowledge_graph.user == "test"
        assert knowledge_graph.password == "test"
        assert knowledge_graph.driver is not None
    
    @pytest.mark.asyncio
    async def test_load_sfia_ontology_from_rdf(self, knowledge_graph):
        """Test loading SFIA ontology from RDF"""
        # Create a temporary RDF file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
            f.write("""
            @prefix sfia: <http://www.sfia-online.org/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            
            sfia:PROG a sfia:Skill ;
                rdfs:label "Programming/software development" .
            """)
            temp_file = f.name
        
        try:
            # Mock the session and transaction
            mock_session = AsyncMock()
            mock_tx = AsyncMock()
            
            knowledge_graph.driver.session = Mock(return_value=mock_session)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.begin_transaction = Mock(return_value=mock_tx)
            mock_tx.__aenter__ = AsyncMock(return_value=mock_tx)
            mock_tx.__aexit__ = AsyncMock(return_value=None)
            mock_tx.run = AsyncMock()
            
            # Test loading ontology
            await knowledge_graph.load_sfia_ontology_from_rdf(temp_file)
            
            # Verify session was used
            knowledge_graph.driver.session.assert_called()
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_query_skills(self, knowledge_graph):
        """Test querying skills from knowledge graph"""
        # Mock the session and result
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_record = Mock()
        mock_record.get.return_value = "PROG"
        mock_result.__aiter__ = AsyncMock(return_value=iter([mock_record]))
        
        knowledge_graph.driver.session = Mock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        
        # Test query
        skills = await knowledge_graph.query_skills(category="Technical", level=3)
        
        # Verify session was used
        knowledge_graph.driver.session.assert_called()
        mock_session.run.assert_called()
        assert isinstance(skills, list)


class TestSFIAReasoningEngine:
    """Test Reasoning Engine Functionality"""
    
    @pytest.fixture
    def mock_knowledge_graph(self):
        """Mock knowledge graph for testing"""
        return Mock()
    
    @pytest.fixture
    def reasoning_engine(self, mock_knowledge_graph):
        """Create reasoning engine instance for testing"""
        return SFIAReasoningEngine(mock_knowledge_graph)
    
    def test_reasoning_engine_initialization(self, reasoning_engine, mock_knowledge_graph):
        """Test reasoning engine initialization"""
        assert reasoning_engine.knowledge_graph == mock_knowledge_graph
        assert reasoning_engine.skill_similarity_model is None
        assert reasoning_engine.career_prediction_model is None
    
    @pytest.mark.asyncio
    async def test_initialize_ml_models(self, reasoning_engine):
        """Test ML models initialization"""
        with patch('sfia_ai_framework.core.reasoning.RandomForestClassifier') as mock_rf:
            with patch('sfia_ai_framework.core.reasoning.TfidfVectorizer') as mock_tfidf:
                mock_rf_instance = Mock()
                mock_tfidf_instance = Mock()
                mock_rf.return_value = mock_rf_instance
                mock_tfidf.return_value = mock_tfidf_instance
                
                await reasoning_engine.initialize_ml_models()
                
                assert reasoning_engine.career_prediction_model == mock_rf_instance
                assert reasoning_engine.skill_vectorizer == mock_tfidf_instance
    
    def test_find_similar_skills(self, reasoning_engine):
        """Test finding similar skills"""
        # Mock skill similarity model
        mock_model = Mock()
        mock_model.kneighbors.return_value = (None, [[0, 1, 2]])
        reasoning_engine.skill_similarity_model = mock_model
        reasoning_engine.skill_names = ["PROG", "SENG", "TEST", "ARCH"]
        
        similar_skills = reasoning_engine.find_similar_skills("PROG", n_similar=3)
        
        assert len(similar_skills) == 3
        assert "PROG" in similar_skills
    
    @pytest.mark.asyncio
    async def test_analyze_skill_gaps(self, reasoning_engine, mock_knowledge_graph):
        """Test skill gap analysis"""
        # Mock knowledge graph query
        mock_knowledge_graph.find_role_skills = AsyncMock()
        mock_knowledge_graph.find_role_skills.side_effect = [
            ["PROG", "TEST"],  # Current role skills
            ["PROG", "TEST", "ARCH", "SENG"]  # Target role skills
        ]
        
        skill_gaps = await reasoning_engine.analyze_skill_gaps("Junior Developer", "Senior Developer")
        
        assert isinstance(skill_gaps, list)
        mock_knowledge_graph.find_role_skills.assert_called()


class TestSFIAScenarios:
    """Test Real-World Scenarios"""
    
    @pytest.fixture
    def mock_sdk(self):
        """Mock SDK for testing scenarios"""
        sdk = Mock()
        sdk.assess_role_fit = AsyncMock(return_value={
            "success": True,
            "assessment": {"overall_score": 0.85}
        })
        sdk.analyze_skill_gaps = AsyncMock(return_value={
            "success": True,
            "skill_gaps": [{"skill_code": "ARCH", "priority": 1}]
        })
        sdk.optimize_team_composition = AsyncMock(return_value={
            "success": True,
            "optimization_result": {"recommended_team": []}
        })
        sdk.generate_development_plan = AsyncMock(return_value={
            "success": True,
            "skill_gap_analysis": {"skill_gaps": []},
            "learning_recommendations": [],
            "timeline": {}
        })
        sdk.assess_organizational_skills = AsyncMock(return_value={
            "success": True,
            "result": {}
        })
        return sdk
    
    @pytest.fixture
    def scenarios(self, mock_sdk):
        """Create scenarios instance for testing"""
        return SFIAScenarios(mock_sdk)
    
    @pytest.mark.asyncio
    async def test_hiring_optimization_scenario(self, scenarios):
        """Test hiring optimization scenario"""
        result = await scenarios.hiring_optimization_scenario()
        
        assert result["scenario"] == "Hiring Optimization"
        assert "company" in result
        assert "analysis_date" in result
        assert "position_analysis" in result
        assert "recommendations" in result
        assert isinstance(result["position_analysis"], list)
        assert isinstance(result["recommendations"], list)
    
    @pytest.mark.asyncio
    async def test_career_development_scenario(self, scenarios):
        """Test career development scenario"""
        result = await scenarios.career_development_scenario()
        
        assert result["scenario"] == "Career Development Planning"
        assert "employee" in result
        assert "analysis_date" in result
        assert "career_pathways" in result
        assert "development_plan" in result
        assert isinstance(result["career_pathways"], list)
    
    @pytest.mark.asyncio
    async def test_team_formation_scenario(self, scenarios):
        """Test team formation scenario"""
        result = await scenarios.team_formation_scenario()
        
        assert result["scenario"] == "Team Formation Optimization"
        assert "organization" in result
        assert "analysis_date" in result
        assert "project_teams" in result
        assert "optimization_metrics" in result
        assert isinstance(result["project_teams"], list)
    
    @pytest.mark.asyncio
    async def test_organizational_assessment_scenario(self, scenarios):
        """Test organizational assessment scenario"""
        result = await scenarios.organizational_assessment_scenario()
        
        assert result["scenario"] == "Organizational Skills Assessment"
        assert "company" in result
        assert "analysis_date" in result
        assert "assessment_results" in result
        assert "strategic_recommendations" in result
        assert "workforce_planning" in result
    
    @pytest.mark.asyncio
    async def test_skills_gap_analysis_scenario(self, scenarios):
        """Test skills gap analysis scenario"""
        result = await scenarios.skills_gap_analysis_scenario()
        
        assert result["scenario"] == "Industry Skills Gap Analysis"
        assert "industry" in result
        assert "analysis_date" in result
        assert "current_state" in result
        assert "future_requirements" in result
        assert "gap_analysis" in result
        assert "strategic_plan" in result


class TestSFIAModels:
    """Test Pydantic Data Models"""
    
    def test_skill_model(self):
        """Test Skill model"""
        skill_data = {
            "skill_code": "PROG",
            "skill_name": "Programming/software development",
            "category": "Development and implementation",
            "subcategory": "Systems development"
        }
        
        skill = Skill(**skill_data)
        
        assert skill.skill_code == "PROG"
        assert skill.skill_name == "Programming/software development"
        assert skill.category == "Development and implementation"
        assert skill.subcategory == "Systems development"
    
    def test_skill_level_model(self):
        """Test SkillLevel model"""
        level_data = {
            "level": 3,
            "description": "Designs, codes, tests, corrects and documents simple programs or scripts under the direction of others."
        }
        
        skill_level = SkillLevel(**level_data)
        
        assert skill_level.level == 3
        assert "Designs, codes, tests" in skill_level.description
    
    def test_professional_role_model(self):
        """Test ProfessionalRole model"""
        role_data = {
            "role_code": "DEV001",
            "role_title": "Software Developer",
            "role_description": "Develops software applications",
            "required_skills": [
                {"skill_code": "PROG", "minimum_level": 3},
                {"skill_code": "TEST", "minimum_level": 2}
            ]
        }
        
        role = ProfessionalRole(**role_data)
        
        assert role.role_code == "DEV001"
        assert role.role_title == "Software Developer"
        assert len(role.required_skills) == 2
        assert role.required_skills[0]["skill_code"] == "PROG"
    
    def test_api_response_model(self):
        """Test APIResponse model"""
        # Success response
        success_response = APIResponse(message="Operation completed successfully")
        assert success_response.success is True
        assert success_response.message == "Operation completed successfully"
        assert success_response.error is None
        
        # Error response
        error_response = APIResponse(success=False, message="Operation failed", error="Database connection error")
        assert error_response.success is False
        assert error_response.message == "Operation failed"
        assert error_response.error == "Database connection error"


class TestIntegration:
    """Integration Tests"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_sdk_context_manager(self):
        """Test SDK context manager"""
        config = SFIASDKConfig(
            neo4j_uri="bolt://localhost:7687",
            neo4j_user="neo4j",
            neo4j_password="test",
            enable_agents=False,  # Disable agents for testing
            enable_reasoning=False  # Disable reasoning for testing
        )
        
        # Mock the knowledge graph creation to avoid actual Neo4j connection
        with patch('sfia_ai_framework.sdk.create_sfia_knowledge_graph') as mock_create_kg:
            mock_kg = AsyncMock()
            mock_create_kg.return_value = mock_kg
            
            async with SFIASDKContext(config) as sdk:
                assert isinstance(sdk, SFIASDK)
                assert sdk._initialized is True
                assert sdk.knowledge_graph == mock_kg
            
            # Verify cleanup was called
            mock_kg.close.assert_called_once()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_scenario_workflow(self):
        """Test complete scenario workflow"""
        # Mock configuration
        config = SFIASDKConfig(
            neo4j_uri="bolt://test:7687",
            neo4j_user="test",
            neo4j_password="test",
            openai_api_key="test_key",
            enable_agents=False,
            enable_reasoning=False
        )
        
        # Mock all the creation functions
        with patch('sfia_ai_framework.sdk.create_sfia_knowledge_graph') as mock_create_kg:
            mock_kg = AsyncMock()
            mock_kg.query_skills = AsyncMock(return_value=[])
            mock_kg.analyze_skill_gaps = AsyncMock(return_value=[])
            mock_create_kg.return_value = mock_kg
            
            # Create SDK and scenarios
            sdk = SFIASDK(config)
            await sdk.initialize()
            scenarios = SFIAScenarios(sdk)
            
            # Test basic functionality
            skills_result = await sdk.query_skills()
            assert skills_result["success"] is True
            
            # Test scenario execution
            hiring_result = await scenarios.hiring_optimization_scenario()
            assert hiring_result["scenario"] == "Hiring Optimization"
            
            # Cleanup
            await sdk.close()


class TestErrorHandling:
    """Test Error Handling and Edge Cases"""
    
    @pytest.mark.asyncio
    async def test_sdk_initialization_failure(self):
        """Test SDK initialization failure handling"""
        config = SFIASDKConfig(
            neo4j_uri="bolt://invalid:7687",
            neo4j_user="invalid",
            neo4j_password="invalid"
        )
        
        sdk = SFIASDK(config)
        
        with patch('sfia_ai_framework.sdk.create_sfia_knowledge_graph') as mock_create_kg:
            mock_create_kg.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception, match="Connection failed"):
                await sdk.initialize()
            
            assert sdk._initialized is False
    
    def test_invalid_skill_code(self):
        """Test handling of invalid skill codes"""
        with pytest.raises(ValueError):
            Skill(skill_code="", skill_name="Invalid skill")
    
    def test_invalid_skill_level(self):
        """Test handling of invalid skill levels"""
        with pytest.raises(ValueError):
            SkillLevel(level=0, description="Invalid level")  # Level must be 1-7
        
        with pytest.raises(ValueError):
            SkillLevel(level=8, description="Invalid level")  # Level must be 1-7


class TestPerformance:
    """Performance Tests"""
    
    @pytest.mark.performance
    def test_large_skills_query_performance(self):
        """Test performance with large skills dataset"""
        # Mock large dataset
        large_skills_data = [
            {"skill_code": f"SKILL{i:03d}", "skill_name": f"Skill {i}"}
            for i in range(1000)
        ]
        
        # Time the processing
        import time
        start_time = time.time()
        
        # Process skills
        skills = [Skill(**skill_data) for skill_data in large_skills_data]
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Assert reasonable performance (should process 1000 skills in under 1 second)
        assert len(skills) == 1000
        assert processing_time < 1.0
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_scenario_execution(self):
        """Test concurrent execution of multiple scenarios"""
        # Mock SDK
        mock_sdk = Mock()
        mock_sdk.assess_role_fit = AsyncMock(return_value={"success": True, "assessment": {}})
        mock_sdk.analyze_skill_gaps = AsyncMock(return_value={"success": True, "skill_gaps": []})
        mock_sdk.optimize_team_composition = AsyncMock(return_value={"success": True, "optimization_result": {}})
        mock_sdk.generate_development_plan = AsyncMock(return_value={"success": True})
        mock_sdk.assess_organizational_skills = AsyncMock(return_value={"success": True, "result": {}})
        
        scenarios = SFIAScenarios(mock_sdk)
        
        # Execute multiple scenarios concurrently
        import time
        start_time = time.time()
        
        tasks = [
            scenarios.hiring_optimization_scenario(),
            scenarios.career_development_scenario(),
            scenarios.team_formation_scenario()
        ]
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Assert all scenarios completed successfully
        assert len(results) == 3
        assert all("scenario" in result for result in results)
        
        # Assert reasonable performance (concurrent execution should be faster than sequential)
        assert execution_time < 5.0  # Should complete within 5 seconds


# Test configuration
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add slow marker for integration and performance tests
        if "integration" in item.keywords or "performance" in item.keywords:
            item.add_marker(pytest.mark.slow)


if __name__ == "__main__":
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--strict-markers"
    ])