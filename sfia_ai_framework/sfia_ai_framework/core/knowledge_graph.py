"""
SFIA Knowledge Graph - Neo4j-based semantic knowledge representation

This module provides a comprehensive knowledge graph implementation for SFIA ontology
with advanced querying, reasoning, and visualization capabilities.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
import json
from datetime import datetime, date
import logging

from neo4j import GraphDatabase, AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable, ClientError
import pandas as pd
import networkx as nx
from rdflib import Graph as RDFGraph, URIRef, Literal, Namespace
import plotly.graph_objects as go
import plotly.express as px
from pyvis.network import Network

from ..models.sfia_models import (
    Skill, SkillLevel, ProfessionalRole, CareerPathway, 
    SkillGap, CompetencyProfile, LearningResource
)


class SFIAKnowledgeGraph:
    """
    Advanced Knowledge Graph for SFIA ontology with semantic reasoning capabilities
    """
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
        # SFIA namespaces
        self.sfia_ns = Namespace("https://rdf.sfia-online.org/9/ontology/")
        self.skills_ns = Namespace("https://rdf.sfia-online.org/9/skills/")
        self.levels_ns = Namespace("https://rdf.sfia-online.org/9/lor/")
        
        # NetworkX graph for local analysis
        self.nx_graph = nx.DiGraph()
        
    async def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as test")
                await result.consume()
            self.logger.info("Successfully connected to Neo4j database")
            await self._initialize_schema()
        except ServiceUnavailable as e:
            self.logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    async def close(self):
        """Close database connection"""
        if self.driver:
            await self.driver.close()
    
    async def _initialize_schema(self):
        """Initialize Neo4j schema with SFIA-specific constraints and indexes"""
        schema_queries = [
            # Unique constraints
            "CREATE CONSTRAINT skill_code_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.code IS UNIQUE",
            "CREATE CONSTRAINT role_code_unique IF NOT EXISTS FOR (r:Role) REQUIRE r.code IS UNIQUE",
            "CREATE CONSTRAINT level_number_unique IF NOT EXISTS FOR (l:Level) REQUIRE l.number IS UNIQUE",
            
            # Indexes for performance
            "CREATE INDEX skill_name_index IF NOT EXISTS FOR (s:Skill) ON (s.name)",
            "CREATE INDEX role_name_index IF NOT EXISTS FOR (r:Role) ON (r.name)",
            "CREATE INDEX category_name_index IF NOT EXISTS FOR (c:Category) ON (c.name)",
            "CREATE INDEX skill_level_index IF NOT EXISTS FOR (sl:SkillLevel) ON (sl.level)",
            
            # Full-text search indexes
            "CREATE FULLTEXT INDEX skill_search IF NOT EXISTS FOR (s:Skill) ON EACH [s.name, s.description, s.notes]",
            "CREATE FULLTEXT INDEX role_search IF NOT EXISTS FOR (r:Role) ON EACH [r.name, r.description]"
        ]
        
        async with self.driver.session() as session:
            for query in schema_queries:
                try:
                    await session.run(query)
                except ClientError as e:
                    if "already exists" not in str(e):
                        self.logger.warning(f"Schema query failed: {query}, Error: {e}")
    
    async def load_sfia_ontology_from_rdf(self, rdf_file_path: str):
        """Load SFIA ontology from RDF file into Neo4j knowledge graph"""
        rdf_graph = RDFGraph()
        rdf_graph.parse(rdf_file_path, format='turtle')
        
        async with self.driver.session() as session:
            # Load Skills
            await self._load_skills_from_rdf(session, rdf_graph)
            # Load Levels
            await self._load_levels_from_rdf(session, rdf_graph)
            # Load Categories
            await self._load_categories_from_rdf(session, rdf_graph)
            # Load Skill Levels
            await self._load_skill_levels_from_rdf(session, rdf_graph)
            # Load Attributes
            await self._load_attributes_from_rdf(session, rdf_graph)
            
        self.logger.info("Successfully loaded SFIA ontology into knowledge graph")
    
    async def _load_skills_from_rdf(self, session, rdf_graph):
        """Load skills from RDF graph"""
        query = """
        SELECT ?skill ?label ?code ?description ?notes ?category WHERE {
            ?skill a sfia:Skill ;
                   rdfs:label ?label ;
                   skos:notation ?code .
            OPTIONAL { ?skill sfia:skillDescription ?description }
            OPTIONAL { ?skill sfia:skillNotes ?notes }
            OPTIONAL { ?skill sfia:skillCategory ?category }
        }
        """
        
        skills_data = []
        for row in rdf_graph.query(query):
            skill_data = {
                'uri': str(row.skill),
                'code': str(row.code),
                'name': str(row.label),
                'description': str(row.description) if row.description else '',
                'notes': str(row.notes) if row.notes else '',
                'category_uri': str(row.category) if row.category else ''
            }
            skills_data.append(skill_data)
        
        # Batch insert skills
        if skills_data:
            cypher_query = """
            UNWIND $skills as skill
            CREATE (s:Skill {
                uri: skill.uri,
                code: skill.code,
                name: skill.name,
                description: skill.description,
                notes: skill.notes,
                category_uri: skill.category_uri,
                created_at: datetime()
            })
            """
            await session.run(cypher_query, skills=skills_data)
    
    async def _load_levels_from_rdf(self, session, rdf_graph):
        """Load responsibility levels from RDF graph"""
        query = """
        SELECT ?level ?number ?essence ?phrase ?url WHERE {
            ?level a sfia:Level ;
                   skos:notation ?number .
            OPTIONAL { ?level sfia:levelEssence ?essence }
            OPTIONAL { ?level sfia:levelGuidingPhrase ?phrase }
            OPTIONAL { ?level sfia:url ?url }
        }
        """
        
        levels_data = []
        for row in rdf_graph.query(query):
            level_data = {
                'uri': str(row.level),
                'number': int(row.number),
                'essence': str(row.essence) if row.essence else '',
                'guiding_phrase': str(row.phrase) if row.phrase else '',
                'url': str(row.url) if row.url else ''
            }
            levels_data.append(level_data)
        
        if levels_data:
            cypher_query = """
            UNWIND $levels as level
            CREATE (l:Level {
                uri: level.uri,
                number: level.number,
                essence: level.essence,
                guiding_phrase: level.guiding_phrase,
                url: level.url,
                created_at: datetime()
            })
            """
            await session.run(cypher_query, levels=levels_data)
    
    async def _load_categories_from_rdf(self, session, rdf_graph):
        """Load skill categories from RDF graph"""
        query = """
        SELECT ?category ?label ?broader WHERE {
            ?category a sfia:Category ;
                      skos:prefLabel ?label .
            OPTIONAL { ?category skos:broader ?broader }
        }
        """
        
        categories_data = []
        for row in rdf_graph.query(query):
            category_data = {
                'uri': str(row.category),
                'name': str(row.label),
                'broader_uri': str(row.broader) if row.broader else ''
            }
            categories_data.append(category_data)
        
        if categories_data:
            # Create categories
            cypher_query = """
            UNWIND $categories as category
            CREATE (c:Category {
                uri: category.uri,
                name: category.name,
                broader_uri: category.broader_uri,
                created_at: datetime()
            })
            """
            await session.run(cypher_query, categories=categories_data)
            
            # Create hierarchy relationships
            hierarchy_query = """
            MATCH (child:Category), (parent:Category)
            WHERE child.broader_uri = parent.uri AND child.broader_uri <> ""
            CREATE (child)-[:SUBCATEGORY_OF]->(parent)
            """
            await session.run(hierarchy_query)
    
    async def _load_skill_levels_from_rdf(self, session, rdf_graph):
        """Load skill-level combinations from RDF graph"""
        query = """
        SELECT ?skillLevel ?skill ?level ?description WHERE {
            ?skillLevel a sfia:SkillLevel ;
                        sfia:level ?level ;
                        sfia:skillLevelDescription ?description .
            ?skill sfia:definedAtLevel ?skillLevel .
        }
        """
        
        skill_levels_data = []
        for row in rdf_graph.query(query):
            skill_level_data = {
                'uri': str(row.skillLevel),
                'skill_uri': str(row.skill),
                'level_uri': str(row.level),
                'description': str(row.description)
            }
            skill_levels_data.append(skill_level_data)
        
        if skill_levels_data:
            # Create skill levels
            cypher_query = """
            UNWIND $skillLevels as sl
            CREATE (sklvl:SkillLevel {
                uri: sl.uri,
                skill_uri: sl.skill_uri,
                level_uri: sl.level_uri,
                description: sl.description,
                created_at: datetime()
            })
            """
            await session.run(cypher_query, skillLevels=skill_levels_data)
            
            # Create relationships
            relationship_queries = [
                # Connect skills to skill levels
                """
                MATCH (s:Skill), (sl:SkillLevel)
                WHERE s.uri = sl.skill_uri
                CREATE (s)-[:HAS_LEVEL]->(sl)
                """,
                # Connect skill levels to levels
                """
                MATCH (sl:SkillLevel), (l:Level)
                WHERE sl.level_uri = l.uri
                CREATE (sl)-[:AT_LEVEL]->(l)
                """
            ]
            
            for query in relationship_queries:
                await session.run(query)
    
    async def _load_attributes_from_rdf(self, session, rdf_graph):
        """Load SFIA attributes from RDF graph"""
        # This would load attributes like Autonomy, Collaboration, etc.
        # Implementation depends on the specific RDF structure
        pass
    
    async def add_professional_roles(self, roles: List[Dict[str, Any]]):
        """Add professional roles to the knowledge graph"""
        async with self.driver.session() as session:
            cypher_query = """
            UNWIND $roles as role
            CREATE (r:Role {
                code: role.code,
                name: role.name,
                level: role.level,
                description: role.description,
                created_at: datetime()
            })
            """
            await session.run(cypher_query, roles=roles)
            
            # Create skill requirements relationships
            for role in roles:
                if 'required_skills' in role:
                    skill_req_query = """
                    MATCH (r:Role {code: $role_code})
                    UNWIND $skills as skill_code
                    MATCH (s:Skill {code: skill_code})
                    CREATE (r)-[:REQUIRES_SKILL {priority: 'essential'}]->(s)
                    """
                    await session.run(skill_req_query, 
                                    role_code=role['code'], 
                                    skills=role['required_skills'])
    
    async def add_career_pathways(self, pathways: List[Dict[str, Any]]):
        """Add career pathways to the knowledge graph"""
        async with self.driver.session() as session:
            for pathway in pathways:
                pathway_query = """
                MATCH (from_role:Role {code: $from_role}), (to_role:Role {code: $to_role})
                CREATE (from_role)-[:PROGRESSES_TO {
                    pathway_type: $pathway_type,
                    difficulty: $difficulty,
                    timeline_months: $timeline
                }]->(to_role)
                """
                await session.run(pathway_query,
                                from_role=pathway['from_role'],
                                to_role=pathway['to_role'],
                                pathway_type=pathway.get('type', 'progression'),
                                difficulty=pathway.get('difficulty', 'medium'),
                                timeline=pathway.get('timeline_months', 12))
    
    async def query_skills(self, category: str = None, level: int = None, keyword: str = None) -> List[Dict[str, Any]]:
        """Query skills based on various criteria"""
        async with self.driver.session() as session:
            base_query = "MATCH (s:Skill)"
            where_clauses = []
            params = {}
            
            if category:
                base_query += "-[:BELONGS_TO]->(c:Category)"
                where_clauses.append("c.name CONTAINS $category")
                params['category'] = category
            
            if level:
                base_query += "-[:HAS_LEVEL]->(sl:SkillLevel)-[:AT_LEVEL]->(l:Level)"
                where_clauses.append("l.number = $level")
                params['level'] = level
            
            if keyword:
                where_clauses.append("(s.name CONTAINS $keyword OR s.description CONTAINS $keyword)")
                params['keyword'] = keyword
            
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            
            base_query += " RETURN DISTINCT s.code as code, s.name as name, s.description as description"
            
            result = await session.run(base_query, **params)
            return [record.data() for record in await result.fetch(100)]
    
    async def find_career_paths(self, from_role: str, to_role: str, max_steps: int = 3) -> List[List[str]]:
        """Find career progression paths between roles"""
        async with self.driver.session() as session:
            path_query = """
            MATCH path = (from:Role {code: $from_role})-[:PROGRESSES_TO*1..$max_steps]->(to:Role {code: $to_role})
            RETURN [node in nodes(path) | node.code] as pathway
            ORDER BY length(path)
            LIMIT 10
            """
            
            result = await session.run(path_query, 
                                     from_role=from_role, 
                                     to_role=to_role, 
                                     max_steps=max_steps)
            return [record['pathway'] for record in await result.fetch(10)]
    
    async def analyze_skill_gaps(self, current_role: str, target_role: str) -> List[Dict[str, Any]]:
        """Analyze skill gaps between current and target roles"""
        async with self.driver.session() as session:
            gap_query = """
            MATCH (current:Role {code: $current_role})-[:REQUIRES_SKILL]->(current_skills:Skill)
            MATCH (target:Role {code: $target_role})-[:REQUIRES_SKILL]->(target_skills:Skill)
            WHERE NOT (current)-[:REQUIRES_SKILL]->(target_skills)
            RETURN target_skills.code as skill_code, target_skills.name as skill_name,
                   target_skills.description as description
            """
            
            result = await session.run(gap_query, current_role=current_role, target_role=target_role)
            return [record.data() for record in await result.fetch(50)]
    
    async def get_role_skill_matrix(self) -> pd.DataFrame:
        """Generate a role-skill matrix for analysis"""
        async with self.driver.session() as session:
            matrix_query = """
            MATCH (r:Role)-[req:REQUIRES_SKILL]->(s:Skill)
            RETURN r.code as role, s.code as skill, req.priority as priority
            """
            
            result = await session.run(matrix_query)
            data = [record.data() for record in await result.fetch(1000)]
            
            if data:
                df = pd.DataFrame(data)
                # Create pivot table
                matrix = df.pivot_table(index='role', columns='skill', values='priority', 
                                      aggfunc='first', fill_value='none')
                return matrix
            return pd.DataFrame()
    
    async def get_network_analysis(self) -> Dict[str, Any]:
        """Perform network analysis on the knowledge graph"""
        async with self.driver.session() as session:
            # Get all relationships for network analysis
            network_query = """
            MATCH (n1)-[r]->(n2)
            RETURN labels(n1)[0] as source_type, n1.code as source,
                   type(r) as relationship, 
                   labels(n2)[0] as target_type, n2.code as target
            """
            
            result = await session.run(network_query)
            edges = [record.data() for record in await result.fetch(1000)]
            
            # Build NetworkX graph
            G = nx.DiGraph()
            for edge in edges:
                G.add_edge(
                    f"{edge['source_type']}:{edge['source']}", 
                    f"{edge['target_type']}:{edge['target']}",
                    relationship=edge['relationship']
                )
            
            # Calculate network metrics
            metrics = {
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': nx.density(G),
                'strongly_connected_components': len(list(nx.strongly_connected_components(G))),
                'weakly_connected_components': len(list(nx.weakly_connected_components(G)))
            }
            
            # Calculate centrality measures
            try:
                centrality = {
                    'degree_centrality': nx.degree_centrality(G),
                    'betweenness_centrality': nx.betweenness_centrality(G),
                    'closeness_centrality': nx.closeness_centrality(G)
                }
                metrics['centrality'] = centrality
            except:
                self.logger.warning("Could not calculate centrality measures")
            
            return metrics
    
    async def visualize_knowledge_graph(self, output_file: str = "sfia_knowledge_graph.html"):
        """Create an interactive visualization of the knowledge graph"""
        async with self.driver.session() as session:
            # Get nodes and relationships
            viz_query = """
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN labels(n)[0] as source_type, n.code as source_id, n.name as source_name,
                   type(r) as relationship,
                   labels(m)[0] as target_type, m.code as target_id, m.name as target_name
            """
            
            result = await session.run(viz_query)
            data = [record.data() for record in await result.fetch(500)]
            
            # Create PyVis network
            net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")
            net.set_options("""
            var options = {
              "physics": {
                "enabled": true,
                "stabilization": {"iterations": 100}
              }
            }
            """)
            
            # Add nodes and edges
            nodes_added = set()
            for record in data:
                if record['source_id'] and record['source_id'] not in nodes_added:
                    color = self._get_node_color(record['source_type'])
                    net.add_node(record['source_id'], 
                                label=record['source_name'] or record['source_id'],
                                color=color,
                                title=f"{record['source_type']}: {record['source_name']}")
                    nodes_added.add(record['source_id'])
                
                if record['target_id'] and record['target_id'] not in nodes_added:
                    color = self._get_node_color(record['target_type'])
                    net.add_node(record['target_id'], 
                                label=record['target_name'] or record['target_id'],
                                color=color,
                                title=f"{record['target_type']}: {record['target_name']}")
                    nodes_added.add(record['target_id'])
                
                if record['relationship'] and record['source_id'] and record['target_id']:
                    net.add_edge(record['source_id'], record['target_id'], 
                               label=record['relationship'],
                               title=record['relationship'])
            
            net.save_graph(output_file)
            return output_file
    
    def _get_node_color(self, node_type: str) -> str:
        """Get color for different node types"""
        colors = {
            'Skill': '#FF6B6B',
            'Role': '#4ECDC4',
            'Level': '#45B7D1',
            'Category': '#96CEB4',
            'SkillLevel': '#FFEAA7'
        }
        return colors.get(node_type, '#DDA0DD')
    
    def to_networkx(self) -> nx.DiGraph:
        """Convert knowledge graph to NetworkX format for analysis"""
        return self.nx_graph.copy()
    
    async def export_to_rdf(self, output_file: str):
        """Export knowledge graph back to RDF format"""
        # Implementation for exporting Neo4j data back to RDF
        pass
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the knowledge graph"""
        async with self.driver.session() as session:
            stats_queries = {
                'skills_count': "MATCH (s:Skill) RETURN count(s) as count",
                'roles_count': "MATCH (r:Role) RETURN count(r) as count",
                'levels_count': "MATCH (l:Level) RETURN count(l) as count",
                'categories_count': "MATCH (c:Category) RETURN count(c) as count",
                'skill_levels_count': "MATCH (sl:SkillLevel) RETURN count(sl) as count",
                'relationships_count': "MATCH ()-[r]->() RETURN count(r) as count"
            }
            
            stats = {}
            for key, query in stats_queries.items():
                result = await session.run(query)
                record = await result.single()
                stats[key] = record['count'] if record else 0
            
            return stats


# Factory function
async def create_sfia_knowledge_graph(neo4j_uri: str = "bolt://localhost:7687", 
                                    user: str = "neo4j", 
                                    password: str = "password") -> SFIAKnowledgeGraph:
    """Factory function to create and initialize SFIA knowledge graph"""
    kg = SFIAKnowledgeGraph(neo4j_uri, user, password)
    await kg.connect()
    return kg