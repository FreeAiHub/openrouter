-- OpenRouter Phase 2 Database Schema
-- Core tables for routing and model management

CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    provider VARCHAR(100) NOT NULL,
    endpoint_url TEXT NOT NULL,
    max_tokens INTEGER DEFAULT 4096,
    supports_streaming BOOLEAN DEFAULT true,
    cost_per_1k_tokens DECIMAL(10, 6),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    route_name VARCHAR(255) NOT NULL UNIQUE,
    model_id INTEGER REFERENCES models(id),
    priority INTEGER DEFAULT 0,
    load_balancing_strategy VARCHAR(50) DEFAULT 'round_robin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS request_logs (
    id SERIAL PRIMARY KEY,
    route_id INTEGER REFERENCES routes(id),
    model_id INTEGER REFERENCES models(id),
    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    status_code INTEGER,
    tokens_used INTEGER,
    error_message TEXT
);

CREATE INDEX idx_request_logs_timestamp ON request_logs(request_timestamp);
CREATE INDEX idx_models_status ON models(status);
