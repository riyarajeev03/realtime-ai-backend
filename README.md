# Realtime AI Backend Project Documentation

## Project Overview
A high-performance asynchronous Python backend built for real-time conversational AI using WebSockets. The system integrates Google Gemini AI for streaming LLM responses and Supabase PostgreSQL for persistent session storage. This project demonstrates a complete full-stack assignment with real-time communication, tool calling, and post-session analytics.

## Key Features

### Real-Time Session & Streaming
- FastAPI WebSocket endpoint: /ws/session/{session_id}
- Bi-directional, low-latency communication
- Token-by-token streaming AI responses
- Connection pooling and session lifecycle management

### Advanced LLM Interaction
- Google Gemini AI integration (models/gemini-2.0-flash)
- Function / Tool calling support
- Calculator tool for mathematical expressions
- Data fetcher tool for simulated data retrieval
- Context-aware routing of conversations
- Multi-turn session state preservation

### Data Persistence (Supabase PostgreSQL)
- Session metadata storage
- Detailed event-level logging
- Automatic timestamp management
- Real-time synchronization with database
- Foreign key constraints and relational integrity

### Post-Session Processing
- Automatic cleanup on WebSocket disconnect
- Conversation history analysis
- AI-generated session summaries
- Metrics computation (duration, message count)
- Session finalization with end timestamps

### Additional Capabilities
- Lightweight web frontend for testing
- Health monitoring endpoints
- Swagger UI API documentation
- Environment-based configuration
- Robust error handling with graceful degradation
- Connection and status monitoring

## Technology Stack
- Backend: FastAPI (async / await)
- Real-Time Protocol: WebSockets
- AI Model: Google Gemini AI (google-generativeai)
- Database: Supabase PostgreSQL
- Frontend: HTML, CSS, JavaScript (WebSocket client)
- Environment Management: python-dotenv
- API Testing: Swagger UI

## Prerequisites
- Python 3.9 or higher
- Google Gemini API key (https://aistudio.google.com/apikeys)
- Supabase account and active project
- Internet connectivity for external APIs

## Setup Instructions

### 1. Clone the Repository
- Clone or download the project repository
- Navigate to the project root directory

### 2. Environment Configuration
- Create a .env file in the project root
- Add GEMINI_API_KEY
- Add SUPABASE_URL
- Add SUPABASE_SERVICE_KEY

### 3. Install Dependencies
- Install all required Python packages from requirements.txt
- Verify dependency versions

### 4. Database Setup
- Create a Supabase project
- Execute SQL schema scripts to create tables
- Configure database permissions
- Test the database connection

### 5. Run the Application
- Start the FastAPI server using uvicorn
- Open the frontend at http://localhost:8000
- Establish a WebSocket session and start chatting
- Validate streaming responses and tool execution

## Database Schema

### Sessions Table
- session_id (VARCHAR, Primary Key)
- user_id (VARCHAR)
- start_time (TIMESTAMP)
- end_time (TIMESTAMP)
- is_active (BOOLEAN)
- summary (TEXT)
- metadata (JSONB)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### Session Events Table
- id (BIGSERIAL, Primary Key)
- session_id (VARCHAR, Foreign Key)
- event_type (VARCHAR)
- content (TEXT)
- metadata (JSONB)
- created_at (TIMESTAMP)

### Relationships
- One session to many session events
- Foreign key with cascade delete
- Indexed fields for performance
- JSONB columns for flexible metadata storage

## File Structure
project-root/
├── app/
│   ├── main.py
│   ├── llm/
│   │   └── client.py
│   └── database/
│       └── supabase_client.py
├── requirements.txt
├── .env.example
└── README.md

## Application Architecture
- Central FastAPI application with WebSocket support
- Streaming-capable LLM client abstraction
- Database access layer with connection pooling
- Frontend testing interface
- Centralized configuration and logging
- Structured error handling utilities

## Running the Application

### Start the Server
python -m app.main

### Access Points
- Frontend UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### WebSocket Communication
- ws://localhost:8000/ws/session/{session_id}
- Send JSON payloads with type and content
- Receive streaming AI responses
- Tool calls execute automatically

## Testing Guidelines

### Functional Testing
- Connect via frontend UI
- Send greeting messages
- Verify streamed AI responses
- Test calculator tool with math queries
- Confirm session and event persistence

### API Testing
- Root endpoint for API metadata
- Health endpoint for status checks
- Session retrieval endpoints
- Swagger UI for interactive testing

### Database Validation
- Verify entries in sessions table
- Check session_events logging
- Validate timestamps
- Confirm foreign key constraints
- Inspect JSONB metadata

## Design Decisions

### Asynchronous System Design
- FastAPI for async execution
- WebSockets for persistent real-time connections
- Non-blocking I/O for scalability
- Concurrent session handling

### LLM Integration Approach
- Google Gemini for cost efficiency
- Streaming responses for better UX
- Tool calling for advanced interactions
- Fallback handling

### Database Strategy
- Minimal yet extensible schema
- Event-sourcing pattern
- JSONB for dynamic metadata
- Indexed fields for performance

### Error Handling
- Graceful degradation on failures
- Clear error messages
- Connection recovery
- Comprehensive logging

### Security
- Secrets via environment variables
- Input validation
- CORS configuration
- Secure database connections

## Troubleshooting

### Common Issues
- Missing API keys
- Supabase connection issues
- WebSocket errors
- Dependency conflicts
- Port 8000 conflicts

### Solutions
- Verify .env configuration
- Check Supabase credentials
- Ensure WebSocket support
- Reinstall dependencies
- Change server port if needed

### Debugging Tips
- Review server logs
- Confirm database tables exist
- Test endpoints independently
- Monitor WebSocket traffic
- Validate JSON formats

## Future Enhancements
- User authentication
- Conversation history search
- Multiple AI model support
- File upload and processing
- Analytics dashboard
- Mobile app
- Voice input/output
- Plugin-based tools
- Rate limiting
- CI/CD automation

## Conclusion

### Project Completion Checklist
- Real-time WebSocket communication
- Streaming AI responses
- Tool calling implementation
- Supabase persistence
- Post-session analytics
- Frontend interface
- Robust error handling
- Complete documentation

### Key Achievements
- End-to-end real-time AI system
- Production-grade architecture
- Scalable design
- Industry best practices

### Learning Outcomes
- Async Python programming
- WebSocket systems
- AI API integration
- Database schema design
- Full-stack development
- Deployment basics
- Technical documentation
