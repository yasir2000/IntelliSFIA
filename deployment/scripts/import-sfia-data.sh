#!/bin/bash
set -e

# SFIA Data Import Script for IntelliSFIA Production
# This script imports SFIA 9 framework data into PostgreSQL

echo "Starting SFIA data import..."

# Database connection parameters
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-intellisfia_prod}"
DB_USER="${POSTGRES_USER:-intellisfia}"

# Wait for database to be ready
echo "Waiting for database connection..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is ready - importing SFIA data..."

# Import SFIA Categories
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<-EOSQL

-- Insert SFIA Categories
INSERT INTO sfia.categories (code, name, description) VALUES
('STR', 'Strategy and architecture', 'Development of strategies, policies, standards, architectures and capabilities'),
('CHG', 'Change and transformation', 'Planning, management and implementation of organisational change'),
('DEV', 'Development and implementation', 'Creation, design, development and implementation of systems and services'),
('DEL', 'Delivery and operation', 'Deployment, operation and support of systems and services'),
('SKL', 'Skills and quality', 'People development, skills development and quality improvement'),
('REL', 'Relationships and engagement', 'Building relationships and engagement with stakeholders')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;

-- Insert SFIA Subcategories
INSERT INTO sfia.subcategories (category_id, code, name, description) VALUES
((SELECT id FROM sfia.categories WHERE code = 'STR'), 'INFO', 'Information', 'Management and application of information and data'),
((SELECT id FROM sfia.categories WHERE code = 'STR'), 'SOLU', 'Solution', 'Specifying, designing and maintaining solutions'),
((SELECT id FROM sfia.categories WHERE code = 'STR'), 'ARCH', 'Architecture', 'Designing and maintaining architectures'),
((SELECT id FROM sfia.categories WHERE code = 'CHG'), 'TRAN', 'Transformation', 'Leading organisational change and transformation'),
((SELECT id FROM sfia.categories WHERE code = 'CHG'), 'PROJ', 'Project management', 'Managing projects and programmes'),
((SELECT id FROM sfia.categories WHERE code = 'DEV'), 'ANAL', 'Analysis', 'Investigation, analysis and specification'),
((SELECT id FROM sfia.categories WHERE code = 'DEV'), 'DESI', 'Design', 'Design of systems, products and services'),
((SELECT id FROM sfia.categories WHERE code = 'DEV'), 'DEVE', 'Development', 'Development and implementation of systems'),
((SELECT id FROM sfia.categories WHERE code = 'DEL'), 'OPER', 'Operation', 'Operation of systems and services'),
((SELECT id FROM sfia.categories WHERE code = 'DEL'), 'SUPP', 'Support', 'Support and maintenance of systems'),
((SELECT id FROM sfia.categories WHERE code = 'SKL'), 'LEAR', 'Learning', 'Learning, development and knowledge transfer'),
((SELECT id FROM sfia.categories WHERE code = 'SKL'), 'QUAL', 'Quality', 'Quality assurance and improvement'),
((SELECT id FROM sfia.categories WHERE code = 'REL'), 'SALE', 'Sales', 'Sales and marketing'),
((SELECT id FROM sfia.categories WHERE code = 'REL'), 'PART', 'Partnership', 'Relationship and partnership management')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;

-- Insert SFIA Levels
INSERT INTO sfia.levels (level_number, name, description, responsibility_levels) VALUES
(1, 'Follow', 'Work under supervision. Uses existing procedures and tools. Limited responsibility for own work.', ARRAY['Following guidance', 'Using established procedures', 'Limited responsibility']),
(2, 'Assist', 'Work under general direction. Some choices in how tasks are performed. Responsibility for quality of own work.', ARRAY['Working under general direction', 'Some choice in methods', 'Responsibility for quality']),
(3, 'Apply', 'Work under broad direction. Full responsibility for work outcomes. Plans and organises work activities.', ARRAY['Working under broad direction', 'Full responsibility', 'Planning activities']),
(4, 'Enable', 'Work under general direction within a clear framework. Full responsibility for work design and execution.', ARRAY['General direction', 'Design and execution', 'Framework responsibility']),
(5, 'Ensure', 'Fully accountable for work in chosen specialisation. Influences strategic direction. Anticipates business needs.', ARRAY['Full accountability', 'Strategic influence', 'Business anticipation']),
(6, 'Initiate', 'Sets strategy and inspires others. Builds capability and capacity. Creates new opportunities.', ARRAY['Strategy setting', 'Inspiring others', 'Capability building']),
(7, 'Set strategy', 'Has ultimate responsibility for strategic direction. Makes decisions with industry-wide impact.', ARRAY['Ultimate responsibility', 'Strategic direction', 'Industry impact'])
ON CONFLICT (level_number) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    responsibility_levels = EXCLUDED.responsibility_levels;

-- Insert SFIA Attributes
INSERT INTO sfia.attributes (code, name, description) VALUES
('AUT', 'Autonomy', 'The extent of the influence a practitioner has over their work'),
('INF', 'Influence', 'The scope of the influence a practitioner has beyond their own work'),
('COM', 'Complexity', 'The types of thinking required for a practitioner to be effective'),
('BUS', 'Business skills', 'The business skills that support the technical skills'),
('KNO', 'Knowledge', 'The practitioner''s breadth and depth of knowledge'),
('LEA', 'Learning', 'How a practitioner maintains and develops their capability'),
('SEC', 'Security', 'The security-related knowledge and skills required'),
('SUS', 'Sustainability', 'Understanding and applying sustainability principles'),
('ETH', 'Ethics', 'Understanding and applying ethical principles'),
('DIV', 'Diversity', 'Promoting and supporting diversity and inclusion'),
('HUM', 'Human factors', 'Understanding of human factors in technology'),
('LEG', 'Legal', 'Understanding of legal and regulatory requirements'),
('SOC', 'Social', 'Understanding of social and cultural factors'),
('COM2', 'Communication', 'Ability to communicate effectively'),
('COL', 'Collaboration', 'Ability to work effectively with others'),
('INN', 'Innovation', 'Ability to innovate and adapt to change')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;

EOSQL

echo "Basic SFIA framework structure imported successfully!"

# Import sample SFIA skills (top 20 most common skills)
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<-EOSQL

-- Insert sample SFIA Skills
INSERT INTO sfia.skills (subcategory_id, code, name, description, guidance, levels) VALUES
((SELECT id FROM sfia.subcategories WHERE code = 'DEVE'), 'PROG', 'Programming/software development', 'Planning, designing, creating, amending, verifying, testing and documenting programs or program components from supplied specifications.', 'Programming involves the creation and maintenance of software applications. This includes analysis of requirements, design of solutions, coding, testing, and documentation.', ARRAY[1,2,3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'PROJ'), 'PRMG', 'Project management', 'The application of processes, methods, skills, knowledge and experience to achieve specific objectives according to acceptance criteria within agreed parameters.', 'Project management encompasses the planning, execution, monitoring, and completion of projects within scope, time, and budget constraints.', ARRAY[2,3,4,5,6,7]),
((SELECT id FROM sfia.subcategories WHERE code = 'ANAL'), 'BUAN', 'Business analysis', 'The identification and specification of business requirements and the evaluation of options for meeting those requirements.', 'Business analysis involves understanding business needs, problems and opportunities to recommend solutions that enable the organisation to achieve its goals.', ARRAY[2,3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'DESI'), 'DESN', 'Systems design', 'The design of systems to meet specified requirements.', 'Systems design involves creating detailed specifications for systems architecture, components, interfaces, and data to satisfy business requirements.', ARRAY[2,3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'QUAL'), 'TEST', 'Testing', 'The planning, design, management, execution and reporting of tests.', 'Testing involves systematic examination of systems and their components to verify they meet specified requirements and perform as expected.', ARRAY[1,2,3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'INFO'), 'DTAN', 'Data analytics', 'The application of analytic and statistical techniques to discover meaningful patterns in data.', 'Data analytics involves examining data sets to draw conclusions and support decision-making through statistical analysis and modeling.', ARRAY[2,3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'OPER'), 'ITOP', 'IT infrastructure', 'The operation and control of IT infrastructure facilities and services.', 'IT infrastructure management involves maintaining and operating technology systems that support business operations.', ARRAY[1,2,3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'ARCH'), 'ARCH', 'Solution architecture', 'The development and maintenance of solution architectures consistent with agreed architectural principles.', 'Solution architecture involves designing integrated solutions that meet business requirements while aligning with enterprise architecture.', ARRAY[4,5,6,7]),
((SELECT id FROM sfia.subcategories WHERE code = 'SUPP'), 'USUP', 'User support', 'The provision of advice and assistance to users.', 'User support involves helping users resolve technical issues and providing guidance on system usage and functionality.', ARRAY[1,2,3,4,5]),
((SELECT id FROM sfia.subcategories WHERE code = 'LEAR'), 'TDLV', 'Learning and development', 'The specification, design, development, delivery and evaluation of learning and development solutions.', 'Learning and development focuses on creating and delivering educational programs to develop skills and capabilities.', ARRAY[2,3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'DEVE'), 'DBDS', 'Database design', 'The specification, design and maintenance of mechanisms for storage and access to data.', 'Database design involves creating efficient data storage solutions that support application requirements and ensure data integrity.', ARRAY[2,3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'OPER'), 'SCTY', 'Information security', 'The application of appropriate policy, procedure, technology and monitoring to ensure information security.', 'Information security involves protecting systems, networks and data from security threats through comprehensive security measures.', ARRAY[2,3,4,5,6,7]),
((SELECT id FROM sfia.subcategories WHERE code = 'DESI'), 'HCEV', 'User experience design', 'The iterative process of understanding users and designing solutions that provide meaningful and relevant experiences.', 'User experience design focuses on creating intuitive and effective interfaces that enhance user satisfaction and usability.', ARRAY[2,3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'TRAN'), 'BURM', 'Business process improvement', 'The analysis and improvement of business processes.', 'Business process improvement involves analyzing current processes and implementing changes to increase efficiency and effectiveness.', ARRAY[3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'SALE'), 'SALE', 'Sales management', 'The management and development of a sales function within an organisation.', 'Sales management involves leading sales teams and developing strategies to achieve revenue targets and customer satisfaction.', ARRAY[3,4,5,6,7]),
((SELECT id FROM sfia.subcategories WHERE code = 'ANAL'), 'REQM', 'Requirements definition and management', 'The elicitation, analysis, specification and validation of requirements.', 'Requirements management involves capturing, documenting, and managing stakeholder needs throughout the project lifecycle.', ARRAY[2,3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'DEVE'), 'SWDN', 'Software design', 'The specification and design of software to meet defined requirements.', 'Software design involves creating detailed specifications for software applications including architecture, components, and interfaces.', ARRAY[2,3,4,5,6]),
((SELECT id FROM sfia.subcategories WHERE code = 'PART'), 'RLMT', 'Relationship management', 'The development and maintenance of business relationships between stakeholders.', 'Relationship management focuses on building and maintaining effective partnerships with customers, suppliers, and other stakeholders.', ARRAY[3,4,5,6,7]),
((SELECT id FROM sfia.subcategories WHERE code = 'OPER'), 'ITSP', 'Service desk and incident management', 'The operation of service desk and incident management processes.', 'Service desk operations involve providing first-line support and managing incidents to restore normal service operations quickly.', ARRAY[1,2,3,4,5]),
((SELECT id FROM sfia.subcategories WHERE code = 'INFO'), 'DGOV', 'Data governance', 'The development and implementation of data governance policies, standards and processes.', 'Data governance involves establishing policies and procedures to ensure data quality, security, and compliance across the organization.', ARRAY[3,4,5,6,7])
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    guidance = EXCLUDED.guidance,
    levels = EXCLUDED.levels;

EOSQL

echo "Sample SFIA skills imported successfully!"

# Create sample skill level descriptions
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<-EOSQL

-- Insert skill level descriptions for Programming
INSERT INTO sfia.skill_levels (skill_id, level_id, description, indicators) 
SELECT 
    s.id,
    l.id,
    CASE l.level_number
        WHEN 1 THEN 'Uses existing code libraries and frameworks under close supervision. Follows coding standards and practices.'
        WHEN 2 THEN 'Writes simple programs and modifies existing code with minimal guidance. Understands basic programming concepts.'
        WHEN 3 THEN 'Designs and develops software components independently. Plans and organizes programming tasks effectively.'
        WHEN 4 THEN 'Leads development of complex software systems. Mentors junior developers and ensures code quality.'
        WHEN 5 THEN 'Defines programming standards and best practices. Leads strategic technical decisions for development teams.'
        WHEN 6 THEN 'Sets organizational programming strategy. Creates new development methodologies and frameworks.'
    END,
    CASE l.level_number
        WHEN 1 THEN ARRAY['Uses existing libraries', 'Follows coding standards', 'Works under supervision']
        WHEN 2 THEN ARRAY['Writes simple programs', 'Modifies existing code', 'Basic programming knowledge']
        WHEN 3 THEN ARRAY['Designs software components', 'Works independently', 'Plans programming tasks']
        WHEN 4 THEN ARRAY['Leads complex development', 'Mentors developers', 'Ensures code quality']
        WHEN 5 THEN ARRAY['Defines programming standards', 'Makes strategic decisions', 'Leads technical teams']
        WHEN 6 THEN ARRAY['Sets organizational strategy', 'Creates methodologies', 'Influences industry practices']
    END
FROM sfia.skills s, sfia.levels l
WHERE s.code = 'PROG' AND l.level_number = ANY(s.levels)
ON CONFLICT (skill_id, level_id) DO UPDATE SET
    description = EXCLUDED.description,
    indicators = EXCLUDED.indicators;

-- Insert skill level descriptions for Project Management
INSERT INTO sfia.skill_levels (skill_id, level_id, description, indicators)
SELECT 
    s.id,
    l.id,
    CASE l.level_number
        WHEN 2 THEN 'Assists in project planning and execution. Maintains project documentation and tracks progress.'
        WHEN 3 THEN 'Manages small to medium projects independently. Coordinates resources and communicates with stakeholders.'
        WHEN 4 THEN 'Manages complex projects and multiple project streams. Leads project teams and ensures delivery.'
        WHEN 5 THEN 'Manages strategic programs and portfolios. Influences organizational project management practices.'
        WHEN 6 THEN 'Sets project management strategy across the organization. Develops PM capabilities and methodologies.'
        WHEN 7 THEN 'Leads enterprise-wide transformation programs. Sets industry standards for project management.'
    END,
    CASE l.level_number
        WHEN 2 THEN ARRAY['Assists in planning', 'Maintains documentation', 'Tracks progress']
        WHEN 3 THEN ARRAY['Manages projects independently', 'Coordinates resources', 'Communicates with stakeholders']
        WHEN 4 THEN ARRAY['Manages complex projects', 'Leads project teams', 'Ensures delivery']
        WHEN 5 THEN ARRAY['Manages strategic programs', 'Influences PM practices', 'Portfolio management']
        WHEN 6 THEN ARRAY['Sets PM strategy', 'Develops capabilities', 'Creates methodologies']
        WHEN 7 THEN ARRAY['Leads transformation', 'Sets industry standards', 'Enterprise leadership']
    END
FROM sfia.skills s, sfia.levels l
WHERE s.code = 'PRMG' AND l.level_number = ANY(s.levels)
ON CONFLICT (skill_id, level_id) DO UPDATE SET
    description = EXCLUDED.description,
    indicators = EXCLUDED.indicators;

EOSQL

echo "SFIA skill level descriptions imported successfully!"

# Create admin user and sample organization
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<-EOSQL

-- Create default admin user
INSERT INTO core.users (email, username, password_hash, first_name, last_name, role, is_active, is_verified) VALUES
('admin@intellisfia.com', 'admin', '\$2b\$12\$LQv3c1yqBwEHxPuNV7uZTO8jcRe0V.VQHlKHjZ5a5.4sI8mQ5XvFq', 'System', 'Administrator', 'admin', true, true)
ON CONFLICT (email) DO UPDATE SET
    username = EXCLUDED.username,
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active,
    is_verified = EXCLUDED.is_verified;

-- Create sample organization
INSERT INTO core.organizations (name, description, industry, size, country) VALUES
('IntelliSFIA Demo Organization', 'Sample organization for demonstration purposes', 'Technology', 'Medium (100-500)', 'United Kingdom')
ON CONFLICT DO NOTHING;

-- Link admin user to organization
INSERT INTO core.user_organizations (user_id, organization_id, role)
SELECT u.id, o.id, 'admin'
FROM core.users u, core.organizations o
WHERE u.email = 'admin@intellisfia.com' AND o.name = 'IntelliSFIA Demo Organization'
ON CONFLICT (user_id, organization_id) DO UPDATE SET role = EXCLUDED.role;

EOSQL

echo "Default admin user and organization created successfully!"

# Update statistics for query optimization
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "ANALYZE;"

echo "SFIA data import completed successfully!"
echo "Total skills imported: $(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM sfia.skills;")"
echo "Total categories: $(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM sfia.categories;")"
echo "Total subcategories: $(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM sfia.subcategories;")"
echo "Total levels: $(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM sfia.levels;")"