-- Initialize IntelliSFIA database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- SFIA Skills table
CREATE TABLE IF NOT EXISTS sfia_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SFIA Levels table
CREATE TABLE IF NOT EXISTS sfia_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level_number INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Assessments table
CREATE TABLE IF NOT EXISTS user_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    skill_code VARCHAR(10) REFERENCES sfia_skills(code),
    current_level INTEGER,
    target_level INTEGER,
    evidence TEXT,
    ai_assessment TEXT,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Conversations table
CREATE TABLE IF NOT EXISTS ai_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL,
    user_input TEXT,
    ai_response TEXT,
    llm_provider VARCHAR(50),
    model_name VARCHAR(100),
    tokens_used INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sfia_skills_code ON sfia_skills(code);
CREATE INDEX IF NOT EXISTS idx_sfia_skills_category ON sfia_skills(category);
CREATE INDEX IF NOT EXISTS idx_user_assessments_user_id ON user_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_user_assessments_skill_code ON user_assessments(skill_code);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_session_id ON ai_conversations(session_id);

-- Insert default SFIA levels
INSERT INTO sfia_levels (level_number, name, description) VALUES
(1, 'Follow', 'Working under close direction to contribute to work activities'),
(2, 'Assist', 'Working under general direction to contribute to work activities'),
(3, 'Apply', 'Working under general direction with responsibility for own outputs'),
(4, 'Enable', 'Working under limited direction to manage work activities'),
(5, 'Ensure', 'Working independently to define and influence work activities'),
(6, 'Initiate', 'Working independently to create and manage significant programs'),
(7, 'Set strategy', 'Working as a recognised authority to set overall strategy')
ON CONFLICT DO NOTHING;