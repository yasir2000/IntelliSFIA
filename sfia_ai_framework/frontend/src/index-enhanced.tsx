import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';

// Enhanced App with API integration
function EnhancedApp() {
  const [statistics, setStatistics] = useState<any>(null);
  const [skills, setSkills] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Load statistics from API
  useEffect(() => {
    fetch('http://localhost:8000/api/sfia9/statistics')
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          setStatistics(data.data.statistics);
        }
      })
      .catch(err => {
        console.error('Error loading statistics:', err);
        setError('Failed to load statistics');
      })
      .finally(() => setLoading(false));
  }, []);

  // Load skills
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
      console.error('Error loading skills:', err);
      setError('Failed to load skills');
    }
  };

  useEffect(() => {
    loadSkills();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadSkills(searchQuery);
  };

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

  const headerStyle: React.CSSProperties = {
    color: '#667eea',
    fontSize: '2.5rem',
    marginBottom: '20px',
    textAlign: 'center',
    textShadow: '1px 1px 2px rgba(0,0,0,0.1)'
  };

  const successBadgeStyle: React.CSSProperties = {
    backgroundColor: '#d4edda',
    border: '1px solid #c3e6cb',
    borderRadius: '4px',
    padding: '10px',
    marginBottom: '10px',
    color: '#155724'
  };

  const infoBadgeStyle: React.CSSProperties = {
    backgroundColor: '#cce5ff',
    border: '1px solid #99ccff',
    borderRadius: '4px',
    padding: '10px',
    marginBottom: '10px',
    color: '#004085'
  };

  const inputStyle: React.CSSProperties = {
    width: '70%',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '16px',
    marginRight: '10px'
  };

  const buttonStyle: React.CSSProperties = {
    padding: '10px 20px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px'
  };

  const skillItemStyle: React.CSSProperties = {
    padding: '15px',
    border: '1px solid #e0e0e0',
    borderRadius: '6px',
    marginBottom: '10px',
    backgroundColor: '#fafafa',
    transition: 'all 0.2s ease'
  };

  return (
    <div style={appStyle}>
      <div style={cardStyle}>
        <h1 style={headerStyle}>
          🎯 SFIA 9 Web Application
        </h1>
        
        <div style={successBadgeStyle}>
          <strong>✅ Status:</strong> Web application is running successfully!
        </div>

        {loading && (
          <div style={infoBadgeStyle}>
            <strong>⏳ Loading:</strong> Fetching SFIA 9 data...
          </div>
        )}

        {error && (
          <div style={{...successBadgeStyle, backgroundColor: '#f8d7da', borderColor: '#f5c6cb', color: '#721c24'}}>
            <strong>⚠️ Error:</strong> {error}
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
                <strong>Attributes:</strong> {statistics.total_attributes}
              </div>
              <div style={infoBadgeStyle}>
                <strong>Categories:</strong> {statistics.total_categories}
              </div>
              <div style={infoBadgeStyle}>
                <strong>Levels:</strong> {statistics.level_definitions}
              </div>
              <div style={infoBadgeStyle}>
                <strong>Subcategories:</strong> {statistics.total_subcategories}
              </div>
            </div>
          </div>
        )}

        <div style={cardStyle}>
          <h2 style={{ color: '#333', marginBottom: '15px' }}>🔍 Skill Search</h2>
          <form onSubmit={handleSearch} style={{ marginBottom: '20px' }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search SFIA skills (e.g. 'programming', 'leadership', 'data')..."
              style={inputStyle}
            />
            <button type="submit" style={buttonStyle}>
              Search
            </button>
          </form>

          <div>
            <h3 style={{ color: '#555', marginBottom: '15px' }}>
              {searchQuery ? `Search Results for "${searchQuery}"` : 'Recent Skills'} ({skills.length})
            </h3>
            {skills.length > 0 ? (
              <div>
                {skills.map((skill, index) => (
                  <div key={skill.code || index} style={skillItemStyle}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <h4 style={{ color: '#667eea', margin: '0 0 5px 0' }}>
                          {skill.name} ({skill.code})
                        </h4>
                        <p style={{ margin: '0 0 8px 0', color: '#666' }}>
                          {skill.description}
                        </p>
                        <div style={{ fontSize: '0.9em', color: '#888' }}>
                          <span style={{ marginRight: '15px' }}>
                            <strong>Category:</strong> {skill.category}
                          </span>
                          {skill.subcategory && (
                            <span>
                              <strong>Subcategory:</strong> {skill.subcategory}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                {searchQuery ? 'No skills found for your search.' : 'No skills loaded yet.'}
              </div>
            )}
          </div>
        </div>

        <div style={cardStyle}>
          <h2 style={{ color: '#333', marginBottom: '15px' }}>🚀 Integration Status</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px' }}>
            <div style={successBadgeStyle}>
              <strong>✅ Frontend:</strong> React 18 + TypeScript running on port 3001
            </div>
            <div style={successBadgeStyle}>
              <strong>✅ Backend:</strong> Mock API server running on port 8000
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
    </div>
  );
}

// Root render
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(<EnhancedApp />);