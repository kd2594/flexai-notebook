-- Initialize FlexAI Notebook Database
-- This script sets up the database schema for local testing

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    instance_id VARCHAR(255),
    gpu_type VARCHAR(100),
    gpu_count INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create compute_instances table
CREATE TABLE IF NOT EXISTS compute_instances (
    id SERIAL PRIMARY KEY,
    instance_id VARCHAR(255) UNIQUE NOT NULL,
    gpu_type VARCHAR(100) NOT NULL,
    gpu_count INTEGER DEFAULT 1,
    cpu_cores INTEGER DEFAULT 8,
    ram_gb INTEGER DEFAULT 32,
    status VARCHAR(50) DEFAULT 'pending',
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stopped_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Create usage_logs table for tracking compute usage
CREATE TABLE IF NOT EXISTS usage_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    instance_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_instances_instance_id ON compute_instances(instance_id);
CREATE INDEX IF NOT EXISTS idx_instances_status ON compute_instances(status);
CREATE INDEX IF NOT EXISTS idx_usage_logs_session_id ON usage_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_timestamp ON usage_logs(timestamp);

-- Insert sample data for testing
INSERT INTO sessions (session_id, user_id, status) 
VALUES ('demo-session-001', 'demo-user', 'active')
ON CONFLICT (session_id) DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for sessions table
DROP TRIGGER IF EXISTS update_sessions_updated_at ON sessions;
CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (for local development)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO flexai_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO flexai_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'FlexAI Notebook Database initialized successfully!';
END $$;
