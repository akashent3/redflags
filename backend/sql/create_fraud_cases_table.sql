-- Create fraud_cases table for historical fraud pattern matching
-- Run this SQL in your PostgreSQL database

CREATE TABLE IF NOT EXISTS fraud_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Case identification
    case_id VARCHAR(100) UNIQUE NOT NULL,
    company_name VARCHAR(300) NOT NULL,
    year INTEGER NOT NULL,

    -- Classification
    sector VARCHAR(100),
    industry VARCHAR(255),
    fraud_type VARCHAR(100) NOT NULL,
    detection_difficulty VARCHAR(50),

    -- Financial impact
    stock_decline_percent NUMERIC(10, 2),
    market_cap_lost_cr NUMERIC(15, 2),

    -- Analysis data (JSONB for flexibility)
    primary_flags JSONB,
    timeline JSONB,
    red_flags_detected JSONB NOT NULL,
    what_investors_missed JSONB,
    lessons_learned JSONB,

    -- Outcome & regulatory action
    outcome TEXT,
    regulatory_action TEXT,

    -- PDF document URL
    pdf_url TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
    created_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_fraud_cases_case_id ON fraud_cases(case_id);
CREATE INDEX idx_fraud_cases_year ON fraud_cases(year);
CREATE INDEX idx_fraud_cases_fraud_type ON fraud_cases(fraud_type);
CREATE INDEX idx_fraud_cases_sector ON fraud_cases(sector);

-- Add comment
COMMENT ON TABLE fraud_cases IS 'Historical fraud cases for pattern matching against company analyses';
