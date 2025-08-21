-- ==========================
-- Database Drop 
-- ==========================
-- This section drops all tables in the correct order to handle foreign key dependencies

-- Drop junction tables first (they reference other tables)
DROP TABLE IF EXISTS experience_skills CASCADE;
DROP TABLE IF EXISTS certification_skills CASCADE;

-- Drop tables that reference users table
DROP TABLE IF EXISTS websites CASCADE;
DROP TABLE IF EXISTS summaries CASCADE;
DROP TABLE IF EXISTS certifications CASCADE;
DROP TABLE IF EXISTS experiences CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS job_experience CASCADE;
DROP TABLE IF EXISTS education CASCADE;

-- Drop users table last (referenced by other tables)
DROP TABLE IF EXISTS users CASCADE;

-- Optional: Drop the extension if no longer needed
-- DROP EXTENSION IF EXISTS "pgcrypto";

-- ==========================
-- Database Initialization 
-- ==========================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================
-- Users Table
-- ==========================
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- Education Table
-- ==========================
CREATE TABLE education (
    education_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    institution_name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    date_started DATE NOT NULL,
    date_finished DATE,
    major VARCHAR(255),
    minor VARCHAR(255),
    gpa NUMERIC(3,2),
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- Job Experience Table
-- ==========================
CREATE TABLE job_experience (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255),
    location VARCHAR(255),
    date_started DATE NOT NULL,
    date_left DATE,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- Skills Table
-- ==========================
CREATE TABLE skills (
    skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    skill_type VARCHAR(50) CHECK (skill_type IN ('Soft', 'Hard', 'Technical')),
    short_description VARCHAR(255),
    long_description TEXT,
    years_experience INT CHECK (years_experience >= 0),
    skill_level VARCHAR(50) CHECK (skill_level IN ('Entry', 'Intermediate', 'Advanced', 'Expert', 'Mastery')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, title)
);

-- ==========================
-- Experiences Table
-- ==========================
CREATE TABLE experiences (
    experience_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    context TEXT,
    actions TEXT,
    results TEXT,
    reflection TEXT,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Many-to-many link between Experiences and Skills
CREATE TABLE experience_skills (
    experience_id UUID NOT NULL REFERENCES experiences(experience_id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    PRIMARY KEY (experience_id, skill_id)
);

-- ==========================
-- Certifications Table
-- ==========================
CREATE TABLE certifications (
    certification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    issuing_organization VARCHAR(255),
    issue_date DATE,
    expiration_date DATE,
    credential_id VARCHAR(255),
    credential_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Many-to-many link between Certifications and Skills
CREATE TABLE certification_skills (
    certification_id UUID NOT NULL REFERENCES certifications(certification_id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    PRIMARY KEY (certification_id, skill_id)
);

-- ==========================
-- Summaries Table
-- ==========================
CREATE TABLE summaries (
    summary_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    blurb TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, title)
);

-- Optional: enforce only one active summary per user
-- CREATE UNIQUE INDEX one_active_summary_per_user 
-- ON summaries(user_id) 
-- WHERE is_active = TRUE;

-- ==========================
-- Websites Table
-- ==========================
CREATE TABLE websites (
    website_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    label VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, url)
);

-- Optional: enforce only one primary website per user
-- CREATE UNIQUE INDEX one_primary_website_per_user
-- ON websites(user_id)
-- WHERE is_primary = TRUE;

-- ==========================
-- Indexes for Performance
-- ==========================
CREATE INDEX idx_education_user_id ON education(user_id);
CREATE INDEX idx_job_experience_user_id ON job_experience(user_id);
CREATE INDEX idx_skills_user_id ON skills(user_id);
CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_experiences_user_id ON experiences(user_id);
CREATE INDEX idx_certifications_user_id ON certifications(user_id);
CREATE INDEX idx_summaries_user_id ON summaries(user_id);
CREATE INDEX idx_websites_user_id ON websites(user_id);

-- ==========================
-- Sample Data (Optional)
-- ==========================
-- INSERT INTO users (email, full_name, password_hash) 
-- VALUES ('test@example.com', 'Test User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeANEKEfPP3gGpgOe');

COMMIT;