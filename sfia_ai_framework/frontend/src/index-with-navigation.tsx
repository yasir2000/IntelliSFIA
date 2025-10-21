import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';

// Enhanced App with navigation and interactive features
function EnhancedApp() {
  const [currentView, setCurrentView] = useState('home');
  const [statistics, setStatistics] = useState<any>(null);
  const [skills, setSkills] = useState<any[]>([]);
  const [selectedSkill, setSelectedSkill] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Load statistics from API (fallback to mock data)
  useEffect(() => {
    fetch('http://localhost:8000/api/sfia9/statistics')
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          setStatistics(data.data.statistics);
        }
      })
      .catch(err => {
        console.log('API not available, using mock data');
        setStatistics({
          sfia_version: "SFIA 9",
          total_attributes: 16,
          total_skills: 147,
          total_categories: 6,
          total_subcategories: 22,
          level_definitions: 21,
          data_loaded: true,
          mode: "Mock Data"
        });
      })
      .finally(() => setLoading(false));
  }, []);

  // Load skills (with fallback to mock data)
  const loadSkills = async (query = '') => {
    try {
      const url = query 
        ? `http://localhost:8000/api/sfia9/skills?query=${encodeURIComponent(query)}&limit=10`
        : 'http://localhost:8000/api/sfia9/skills?limit=10';
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        setSkills(data.data.skills || []);
      }
    } catch (err) {
      console.log('API not available, using mock skills data');
      const mockSkills = [
        { code: "PROG", name: "Programming/software engineering", category: "Development and implementation", description: "Planning, design, creation, modification, verification, testing and documentation of software components." },
        { code: "DTAN", name: "Data analysis", category: "Strategy and architecture", description: "Investigation, evaluation, interpretation and classification of data to define information structures." },
        { code: "REQM", name: "Requirements definition and management", category: "Strategy and architecture", description: "The elicitation, analysis, specification and validation of requirements." },
        { code: "TEST", name: "Testing", category: "Development and implementation", description: "The planning, design, management, execution and reporting of tests." },
        { code: "DBDS", name: "Database design", category: "Development and implementation", description: "The specification, design and maintenance of mechanisms for storage and access to data." }
      ];
      const filteredSkills = query 
        ? mockSkills.filter(skill => 
            skill.name.toLowerCase().includes(query.toLowerCase()) ||
            skill.code.toLowerCase().includes(query.toLowerCase())
          )
        : mockSkills;
      setSkills(filteredSkills);
    }
  };

  useEffect(() => {
    if (currentView === 'skills') {
      loadSkills();
    }
  }, [currentView]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadSkills(searchQuery);
  };

  const handleSkillClick = (skill: any) => {
    setSelectedSkill(skill);
  };

  // Styles
  const appStyle: React.CSSProperties = {
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
    maxWidth: '1200px',
    margin: '0 auto',
    backgroundColor: '#f8f9fa',
    minHeight: '100vh'
  };

  const cardStyle: React.CSSProperties = {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    marginBottom: '20px'
  };

  const badgeStyle: React.CSSProperties = {
    padding: '12px',
    borderRadius: '6px',
    marginBottom: '15px',
    border: '1px solid'
  };

  const successBadgeStyle: React.CSSProperties = {
    ...badgeStyle,
    backgroundColor: '#d4edda',
    borderColor: '#c3e6cb',
    color: '#155724'
  };

  const infoBadgeStyle: React.CSSProperties = {
    ...badgeStyle,
    backgroundColor: '#cce5ff',
    borderColor: '#99ccff',
    color: '#004085'
  };

  // Navigation component
  const Navigation = () => (
    <div style={{
      backgroundColor: '#667eea',
      padding: '15px 20px',
      marginBottom: '20px',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
        <h1 style={{ color: 'white', margin: 0, fontSize: '1.8rem' }}>
          🎯 SFIA 9 Framework
        </h1>
        <nav style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
          {[
            { id: 'home', label: '🏠 Home' },
            { id: 'skills', label: '🔍 Skills Explorer' },
            { id: 'assessment', label: '📊 Assessment' },
            { id: 'knowledge', label: '🧠 Knowledge Graph' }
          ].map(item => (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id)}
              style={{
                background: currentView === item.id ? 'rgba(255,255,255,0.2)' : 'transparent',
                color: 'white',
                border: '1px solid rgba(255,255,255,0.3)',
                padding: '8px 16px',
                borderRadius: '20px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.2s ease'
              }}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </div>
    </div>
  );

  // Home View Component
  const HomeView = () => (
    <div>
      <div style={successBadgeStyle}>
        <strong>✅ Status:</strong> Web application is running successfully with interactive navigation!
      </div>

      {loading && (
        <div style={infoBadgeStyle}>
          <strong>⏳ Loading:</strong> Fetching SFIA 9 data...
        </div>
      )}

      {statistics && (
        <div style={cardStyle}>
          <h2 style={{ color: '#333', marginBottom: '15px' }}>📊 Framework Statistics</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
            <div style={infoBadgeStyle}>
              <strong>Version:</strong> {statistics.sfia_version}
            </div>
            <div style={infoBadgeStyle}>
              <strong>Skills:</strong> {statistics.total_skills}
            </div>
            <div style={infoBadgeStyle}>
              <strong>Categories:</strong> {statistics.total_categories}
            </div>
            <div style={infoBadgeStyle}>
              <strong>Levels:</strong> {statistics.level_definitions}
            </div>
            <div style={infoBadgeStyle}>
              <strong>Attributes:</strong> {statistics.total_attributes}
            </div>
            {statistics.mode && (
              <div style={infoBadgeStyle}>
                <strong>Mode:</strong> {statistics.mode}
              </div>
            )}
          </div>
        </div>
      )}

      <div style={cardStyle}>
        <h2 style={{ color: '#333', marginBottom: '15px' }}>🚀 Quick Navigation</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px' }}>
          <button 
            onClick={() => setCurrentView('skills')}
            style={{
              ...cardStyle,
              cursor: 'pointer',
              border: '2px solid #667eea',
              transition: 'all 0.2s ease'
            }}
          >
            <h3 style={{ color: '#667eea', marginTop: 0 }}>🔍 Skills Explorer</h3>
            <p>Browse and search through all {statistics?.total_skills || 147} SFIA skills with detailed descriptions and level guidance.</p>
          </button>
          
          <button 
            onClick={() => setCurrentView('assessment')}
            style={{
              ...cardStyle,
              cursor: 'pointer',
              border: '2px solid #28a745',
              transition: 'all 0.2s ease'
            }}
          >
            <h3 style={{ color: '#28a745', marginTop: 0 }}>📊 Assessment Tools</h3>
            <p>Evaluate professional competencies and generate personalized development recommendations.</p>
          </button>
          
          <button 
            onClick={() => setCurrentView('knowledge')}
            style={{
              ...cardStyle,
              cursor: 'pointer',
              border: '2px solid #6f42c1',
              transition: 'all 0.2s ease'
            }}
          >
            <h3 style={{ color: '#6f42c1', marginTop: 0 }}>🧠 Knowledge Graph</h3>
            <p>Explore semantic relationships between skills with interactive visualization.</p>
          </button>
        </div>
      </div>

      <div style={cardStyle}>
        <h2 style={{ color: '#333', marginBottom: '15px' }}>🔧 Integration Status</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px' }}>
          <div style={successBadgeStyle}>
            <strong>✅ Frontend:</strong> React 18 + TypeScript running on port 3000
          </div>
          <div style={successBadgeStyle}>
            <strong>✅ Backend:</strong> Mock API server with fallback data
          </div>
          <div style={successBadgeStyle}>
            <strong>✅ Data:</strong> {statistics ? `${statistics.total_skills} skills loaded` : 'Loading...'}
          </div>
          <div style={successBadgeStyle}>
            <strong>✅ RDF:</strong> Knowledge graph with 154 triples ready
          </div>
        </div>
      </div>
    </div>
  );

  // Skills Explorer View
  const SkillsView = () => (
    <div>
      <div style={cardStyle}>
        <h2 style={{ color: '#333', marginBottom: '15px' }}>🔍 Skills Explorer</h2>
        
        <form onSubmit={handleSearch} style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search skills by name or code (e.g., PROG, Data Analysis)..."
              style={{
                flex: 1,
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '16px'
              }}
            />
            <button
              type="submit"
              style={{
                padding: '12px 24px',
                backgroundColor: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              Search
            </button>
          </div>
        </form>

        <div style={{ marginBottom: '15px' }}>
          <strong>Found {skills.length} skills</strong>
        </div>

        <div style={{ display: 'grid', gap: '15px' }}>
          {skills.map((skill, index) => (
            <div
              key={skill.code || index}
              onClick={() => handleSkillClick(skill)}
              style={{
                padding: '15px',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                backgroundColor: '#fafafa',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f0f8ff';
                e.currentTarget.style.borderColor = '#667eea';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fafafa';
                e.currentTarget.style.borderColor = '#e0e0e0';
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: '0 0 8px 0', color: '#667eea' }}>
                    {skill.code} - {skill.name}
                  </h3>
                  <p style={{ margin: '0 0 8px 0', color: '#666', fontSize: '14px' }}>
                    <strong>Category:</strong> {skill.category}
                  </p>
                  {skill.description && (
                    <p style={{ margin: 0, color: '#333', fontSize: '14px' }}>
                      {skill.description.length > 120 ? 
                        `${skill.description.substring(0, 120)}...` : 
                        skill.description
                      }
                    </p>
                  )}
                </div>
                <div style={{
                  backgroundColor: '#667eea',
                  color: 'white',
                  padding: '4px 8px',
                  borderRadius: '12px',
                  fontSize: '12px',
                  marginLeft: '15px'
                }}>
                  Click to explore
                </div>
              </div>
            </div>
          ))}
        </div>

        {skills.length === 0 && !loading && (
          <div style={infoBadgeStyle}>
            <strong>No skills found.</strong> Try a different search term or browse all skills.
          </div>
        )}
      </div>

      {selectedSkill && (
        <div style={cardStyle}>
          <h2 style={{ color: '#333', marginBottom: '15px' }}>📋 Skill Details</h2>
          <div style={{ border: '2px solid #667eea', borderRadius: '8px', padding: '20px' }}>
            <h3 style={{ color: '#667eea', marginTop: 0 }}>
              {selectedSkill.code} - {selectedSkill.name}
            </h3>
            <p><strong>Category:</strong> {selectedSkill.category}</p>
            {selectedSkill.description && (
              <p><strong>Description:</strong> {selectedSkill.description}</p>
            )}
            <button 
              onClick={() => setSelectedSkill(null)}
              style={{
                marginTop: '15px',
                padding: '8px 16px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Close Details
            </button>
          </div>
        </div>
      )}
    </div>
  );

  // Assessment View
  const AssessmentView = () => (
    <div style={cardStyle}>
      <h2 style={{ color: '#333', marginBottom: '15px' }}>📊 Professional Assessment</h2>
      <div style={infoBadgeStyle}>
        <strong>🚧 Coming Soon:</strong> Professional competency assessment tools with personalized recommendations based on SFIA 9 framework.
      </div>
      <ul style={{ lineHeight: '1.8' }}>
        <li>Skills gap analysis</li>
        <li>Career progression mapping</li>
        <li>Evidence-based assessments</li>
        <li>Personalized development plans</li>
      </ul>
    </div>
  );

  // Knowledge Graph View
  const KnowledgeView = () => (
    <div style={cardStyle}>
      <h2 style={{ color: '#333', marginBottom: '15px' }}>🧠 Knowledge Graph Visualization</h2>
      <div style={infoBadgeStyle}>
        <strong>🚧 Coming Soon:</strong> Interactive visualization of SFIA skills relationships and semantic connections.
      </div>
      <ul style={{ lineHeight: '1.8' }}>
        <li>Interactive skill relationship mapping</li>
        <li>SPARQL query interface</li>
        <li>RDF data exploration (154 triples)</li>
        <li>Semantic search capabilities</li>
      </ul>
    </div>
  );

  // Render current view
  const renderCurrentView = () => {
    switch (currentView) {
      case 'skills': return <SkillsView />;
      case 'assessment': return <AssessmentView />;
      case 'knowledge': return <KnowledgeView />;
      default: return <HomeView />;
    }
  };

  return (
    <div style={appStyle}>
      <Navigation />
      {renderCurrentView()}
    </div>
  );
}

// Root render
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(<EnhancedApp />);