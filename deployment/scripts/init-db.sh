#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - executing commands"

# Create databases if they don't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

-- Create IntelliSFIA main database
CREATE DATABASE IF NOT EXISTS intellisfia_prod;

-- Create separate database for analytics
CREATE DATABASE IF NOT EXISTS intellisfia_analytics;

-- Create database for caching metadata
CREATE DATABASE IF NOT EXISTS intellisfia_cache;

-- Switch to main database
\c intellisfia_prod;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS sfia;
CREATE SCHEMA IF NOT EXISTS assessments;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Core tables
CREATE TABLE IF NOT EXISTS core.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS core.organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    industry VARCHAR(100),
    size VARCHAR(50),
    country VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.user_organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES core.organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, organization_id)
);

-- SFIA Framework tables
CREATE TABLE IF NOT EXISTS sfia.categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sfia.subcategories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES sfia.categories(id) ON DELETE CASCADE,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sfia.skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subcategory_id UUID REFERENCES sfia.subcategories(id) ON DELETE CASCADE,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    guidance TEXT,
    levels INTEGER[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sfia.attributes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sfia.levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level_number INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    responsibility_levels TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sfia.skill_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_id UUID REFERENCES sfia.skills(id) ON DELETE CASCADE,
    level_id UUID REFERENCES sfia.levels(id) ON DELETE CASCADE,
    description TEXT,
    indicators TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(skill_id, level_id)
);

-- Assessment tables
CREATE TABLE IF NOT EXISTS assessments.assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES core.organizations(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assessment_type VARCHAR(50) DEFAULT 'skill_assessment',
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS assessments.assessment_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID REFERENCES assessments.assessments(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES sfia.skills(id) ON DELETE CASCADE,
    current_level INTEGER,
    target_level INTEGER,
    evidence TEXT,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(assessment_id, skill_id)
);

CREATE TABLE IF NOT EXISTS assessments.skill_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES sfia.skills(id) ON DELETE CASCADE,
    current_level INTEGER,
    recommended_level INTEGER,
    priority VARCHAR(50) DEFAULT 'medium',
    reasoning TEXT,
    learning_resources JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Analytics tables
CREATE TABLE IF NOT EXISTS analytics.user_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics.skill_usage_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_id UUID REFERENCES sfia.skills(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES core.organizations(id) ON DELETE SET NULL,
    view_count INTEGER DEFAULT 0,
    assessment_count INTEGER DEFAULT 0,
    average_current_level DECIMAL(3,2),
    average_target_level DECIMAL(3,2),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit tables
CREATE TABLE IF NOT EXISTS audit.audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(id) ON DELETE SET NULL,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON core.users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON core.users(username);
CREATE INDEX IF NOT EXISTS idx_users_active ON core.users(is_active);
CREATE INDEX IF NOT EXISTS idx_skills_code ON sfia.skills(code);
CREATE INDEX IF NOT EXISTS idx_skills_subcategory ON sfia.skills(subcategory_id);
CREATE INDEX IF NOT EXISTS idx_skills_name_gin ON sfia.skills USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_assessments_user ON assessments.assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_assessments_org ON assessments.assessments(organization_id);
CREATE INDEX IF NOT EXISTS idx_assessment_skills_assessment ON assessments.assessment_skills(assessment_id);
CREATE INDEX IF NOT EXISTS idx_assessment_skills_skill ON assessments.assessment_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_activities_user ON analytics.user_activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_type ON analytics.user_activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_activities_created ON analytics.user_activities(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_table ON audit.audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit.audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit.audit_log(created_at);

-- Create functions for audit logging
CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS TRIGGER AS \$\$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit.audit_log (table_name, operation, old_values)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD));
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit.audit_log (table_name, operation, old_values, new_values)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit.audit_log (table_name, operation, new_values)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
\$\$ LANGUAGE plpgsql;

-- Create triggers for audit logging on key tables
CREATE TRIGGER users_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON core.users
    FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

CREATE TRIGGER assessments_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON assessments.assessments
    FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

CREATE TRIGGER assessment_skills_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON assessments.assessment_skills
    FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS \$\$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
\$\$ LANGUAGE plpgsql;

-- Create triggers for updated_at timestamp
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON core.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON core.organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON sfia.skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments.assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assessment_skills_updated_at BEFORE UPDATE ON assessments.assessment_skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE OR REPLACE VIEW sfia.skills_with_categories AS
SELECT 
    s.id,
    s.code,
    s.name,
    s.description,
    s.guidance,
    s.levels,
    sc.code as subcategory_code,
    sc.name as subcategory_name,
    c.code as category_code,
    c.name as category_name
FROM sfia.skills s
JOIN sfia.subcategories sc ON s.subcategory_id = sc.id
JOIN sfia.categories c ON sc.category_id = c.id;

CREATE OR REPLACE VIEW assessments.assessment_summary AS
SELECT 
    a.id,
    a.title,
    a.description,
    a.status,
    a.created_at,
    a.completed_at,
    u.username,
    u.first_name,
    u.last_name,
    o.name as organization_name,
    COUNT(asr.id) as skills_count,
    AVG(asr.current_level) as avg_current_level,
    AVG(asr.target_level) as avg_target_level
FROM assessments.assessments a
JOIN core.users u ON a.user_id = u.id
LEFT JOIN core.organizations o ON a.organization_id = o.id
LEFT JOIN assessments.assessment_skills asr ON a.id = asr.assessment_id
GROUP BY a.id, u.username, u.first_name, u.last_name, o.name;

-- Grant permissions
GRANT USAGE ON SCHEMA core TO intellisfia_api;
GRANT USAGE ON SCHEMA sfia TO intellisfia_api;
GRANT USAGE ON SCHEMA assessments TO intellisfia_api;
GRANT USAGE ON SCHEMA analytics TO intellisfia_api;
GRANT USAGE ON SCHEMA audit TO intellisfia_api;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA core TO intellisfia_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sfia TO intellisfia_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA assessments TO intellisfia_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA analytics TO intellisfia_api;
GRANT SELECT ON ALL TABLES IN SCHEMA audit TO intellisfia_api;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA core TO intellisfia_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA sfia TO intellisfia_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA assessments TO intellisfia_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA analytics TO intellisfia_api;

EOSQL

echo "Database initialization completed successfully!"