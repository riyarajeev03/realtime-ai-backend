-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    summary TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create session_events table
CREATE TABLE IF NOT EXISTS session_events (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_is_active ON sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_session_events_session_id ON session_events(session_id);
CREATE INDEX IF NOT EXISTS idx_session_events_created_at ON session_events(created_at);
CREATE INDEX IF NOT EXISTS idx_session_events_event_type ON session_events(event_type);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for sessions table
CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE
ON sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for session statistics
CREATE OR REPLACE VIEW session_statistics AS
SELECT 
    s.session_id,
    s.user_id,
    s.start_time,
    s.end_time,
    s.is_active,
    EXTRACT(EPOCH FROM (COALESCE(s.end_time, NOW()) - s.start_time)) as duration_seconds,
    COUNT(DISTINCT e.id) as total_events,
    COUNT(DISTINCT CASE WHEN e.event_type = 'user_message' THEN e.id END) as user_messages,
    COUNT(DISTINCT CASE WHEN e.event_type = 'ai_response' THEN e.id END) as ai_responses,
    COUNT(DISTINCT CASE WHEN e.event_type = 'tool_call' THEN e.id END) as tool_calls
FROM sessions s
LEFT JOIN session_events e ON s.session_id = e.session_id
GROUP BY s.id, s.session_id, s.user_id, s.start_time, s.end_time, s.is_active;

-- Create function to get recent sessions
CREATE OR REPLACE FUNCTION get_recent_sessions(limit_count INT DEFAULT 10)
RETURNS TABLE (
    session_id VARCHAR,
    user_id VARCHAR,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds NUMERIC,
    message_count BIGINT,
    last_activity TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.session_id,
        s.user_id,
        s.start_time,
        s.end_time,
        EXTRACT(EPOCH FROM (COALESCE(s.end_time, NOW()) - s.start_time)) as duration_seconds,
        COUNT(e.id) as message_count,
        MAX(e.created_at) as last_activity
    FROM sessions s
    LEFT JOIN session_events e ON s.session_id = e.session_id
        AND e.event_type IN ('user_message', 'ai_response')
    GROUP BY s.session_id, s.user_id, s.start_time, s.end_time
    ORDER BY MAX(e.created_at) DESC NULLS LAST, s.start_time DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;