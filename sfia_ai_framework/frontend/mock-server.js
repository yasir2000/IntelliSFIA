/**
 * Mock API Server for SFIA 9 Web Application
 * Provides mock data for development when backend is not available
 */

const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 8000;

// Middleware
app.use(cors());
app.use(express.json());

// Mock SFIA 9 data
const mockSkills = [
  {
    code: "PROG",
    name: "Programming/software engineering",
    category: "Development and implementation",
    subcategory: "Systems development",
    description: "The planning, design, creation, modification, verification, testing and documentation of new and amended software components in order to deliver agreed value to stakeholders.",
    guidance_notes: "Programming is fundamental to software development...",
    available_levels: [2, 3, 4, 5, 6],
    level_descriptions: {
      "2": "Uses existing programming languages, tools and techniques to write or modify simple programs and scripts.",
      "3": "Designs, codes, tests, corrects and documents simple programs or scripts under the direction of others.",
      "4": "Designs, codes, tests, corrects and documents moderately complex programs/scripts and integration software components.",
      "5": "Designs, codes, tests, corrects and documents programs and integration software components from specifications.",
      "6": "Takes technical responsibility for complex software development and integration."
    },
    sfia_version: "SFIA 9"
  },
  {
    code: "DTAN",
    name: "Data analysis",
    category: "Strategy and architecture", 
    subcategory: "Information strategy",
    description: "The investigation, evaluation, interpretation and classification of data in order to define and clarify information structures, data relationships and rules for assembling and processing data.",
    guidance_notes: "Data analysis involves examining data systematically...",
    available_levels: [3, 4, 5, 6],
    level_descriptions: {
      "3": "Investigates corporate data requirements and applies data analysis, data modeling and quality assurance techniques.",
      "4": "Interprets data analysis requirements and applies appropriate data analysis and data modeling techniques.",
      "5": "Advises on the interpretation of data analysis requirements and the analytical approach to be taken.",
      "6": "Sets organizational policy and standards for data analysis activities."
    },
    sfia_version: "SFIA 9"
  }
];

const mockAttributes = [
  {
    code: "AUTO",
    name: "Autonomy",
    type: "Attributes",
    description: "The level of independence, discretion and accountability for results in your role.",
    guidance_notes: "Autonomy in SFIA represents a progression from following instructions...",
    levels: ["1", "2", "3", "4", "5", "6", "7"],
    level_descriptions: {
      "1": "Follows instructions and works under close direction.",
      "2": "Works under routine direction.",
      "3": "Works under general direction to complete assigned tasks.",
      "4": "Works under broad direction within a clear framework.",
      "5": "Works under broad direction.",
      "6": "Has responsibility for setting direction.",
      "7": "Has responsibility for setting organisational direction."
    },
    sfia_version: "SFIA 9"
  }
];

const mockStatistics = {
  sfia_version: "SFIA 9",
  total_attributes: 16,
  total_skills: 147,
  total_categories: 6,
  total_subcategories: 22,
  level_definitions: 21,
  data_loaded: true
};

// Health check
app.get('/health', (req, res) => {
  res.json({
    success: true,
    data: [
      { service: 'API', status: 'healthy', timestamp: new Date().toISOString() },
      { service: 'Database', status: 'healthy', timestamp: new Date().toISOString() },
      { service: 'SFIA Service', status: 'healthy', timestamp: new Date().toISOString() }
    ]
  });
});

// SFIA 9 endpoints
app.get('/api/sfia9/statistics', (req, res) => {
  res.json({
    success: true,
    data: {
      success: true,
      statistics: mockStatistics
    }
  });
});

app.get('/api/sfia9/skills', (req, res) => {
  const query = req.query.query?.toString().toLowerCase() || '';
  const limit = parseInt(req.query.limit?.toString() || '10');
  
  let filteredSkills = mockSkills;
  if (query) {
    filteredSkills = mockSkills.filter(skill => 
      skill.name.toLowerCase().includes(query) ||
      skill.description.toLowerCase().includes(query) ||
      skill.code.toLowerCase().includes(query)
    );
  }
  
  res.json({
    success: true,
    data: {
      success: true,
      skills: filteredSkills.slice(0, limit)
    }
  });
});

app.get('/api/sfia9/skills/:code', (req, res) => {
  const code = req.params.code.toUpperCase();
  const skill = mockSkills.find(s => s.code === code);
  
  if (skill) {
    res.json({
      success: true,
      data: {
        success: true,
        skill: skill
      }
    });
  } else {
    res.status(404).json({
      success: false,
      error: `Skill ${code} not found`
    });
  }
});

app.post('/api/sfia9/assess-evidence', (req, res) => {
  const { skill_code, level, evidence } = req.body;
  
  // Mock assessment response
  res.json({
    success: true,
    data: {
      success: true,
      assessment: {
        skill_code,
        target_level: level,
        evidence_provided: evidence,
        assessment_score: Math.floor(Math.random() * 40) + 60, // 60-100
        confidence: Math.floor(Math.random() * 30) + 70, // 70-100
        feedback: "The evidence demonstrates good understanding of the skill requirements.",
        recommendations: [
          "Consider providing more specific examples",
          "Include quantitative results where possible",
          "Document the impact of your work"
        ]
      }
    }
  });
});

app.get('/api/sfia9/categories', (req, res) => {
  res.json({
    success: true,
    data: {
      success: true,
      categories: [
        { name: "Strategy and architecture", skill_count: 31 },
        { name: "Change and transformation", skill_count: 16 },
        { name: "Development and implementation", skill_count: 41 },
        { name: "Delivery and operation", skill_count: 31 },
        { name: "People and skills", skill_count: 13 },
        { name: "Relationships and engagement", skill_count: 15 }
      ]
    }
  });
});

// Portfolio assessment endpoints
app.post('/api/portfolio/assess', (req, res) => {
  res.json({
    success: true,
    summary: {
      skills_assessed: 5,
      average_confidence: 85,
      recommendations: ["Continue developing technical skills", "Focus on leadership competencies"]
    }
  });
});

app.post('/api/portfolio/guidance', (req, res) => {
  res.json({
    status: 'success',
    guidance: {
      next_steps: ["Document more evidence", "Seek feedback from peers"],
      development_areas: ["Technical depth", "Communication skills"]
    }
  });
});

// Catch-all for other endpoints
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: `Endpoint ${req.originalUrl} not found`
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Mock API Server running on http://localhost:${PORT}`);
  console.log(`📊 Available endpoints:`);
  console.log(`   GET  /health`);
  console.log(`   GET  /api/sfia9/statistics`);
  console.log(`   GET  /api/sfia9/skills`);
  console.log(`   GET  /api/sfia9/skills/:code`);
  console.log(`   POST /api/sfia9/assess-evidence`);
  console.log(`   GET  /api/sfia9/categories`);
  console.log(`   POST /api/portfolio/assess`);
  console.log(`   POST /api/portfolio/guidance`);
});

module.exports = app;