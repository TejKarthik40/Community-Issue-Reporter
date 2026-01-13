-- Supabase table for community issues
CREATE TABLE IF NOT EXISTS community_issues (
    id SERIAL PRIMARY KEY,
    issue_type TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    reporter_name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMP DEFAULT NOW()
);
