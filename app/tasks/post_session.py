import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
from openai import AsyncOpenAI
import os

from app.database.supabase_client import get_supabase

async def analyze_conversation_history(session_id: str) -> Dict[str, Any]:
    """Analyze conversation history using LLM to generate insights"""
    
    # Fetch conversation events
    supabase = get_supabase()
    
    events_response = supabase.table("session_events")\
        .select("*")\
        .eq("session_id", session_id)\
        .order("created_at")\
        .execute()
    
    events = events_response.data
    
    # Filter relevant events for analysis
    conversation_events = []
    for event in events:
        if event["event_type"] in ["user_message", "ai_response"]:
            conversation_events.append({
                "role": "user" if event["event_type"] == "user_message" else "assistant",
                "content": event["content"],
                "timestamp": event["created_at"]
            })
    
    # Prepare analysis prompt
    analysis_prompt = f"""Analyze the following conversation and provide a comprehensive summary:
    
    Conversation History:
    {json.dumps(conversation_events, indent=2)}
    
    Please provide:
    1. Main topics discussed
    2. User's intent and needs
    3. Key insights or solutions provided
    4. Any unresolved questions or follow-up needed
    5. Overall sentiment and tone
    6. Conversation quality score (1-10)
    
    Format the response as JSON with the following structure:
    {{
        "topics": ["topic1", "topic2", ...],
        "user_intent": "description",
        "key_insights": ["insight1", "insight2", ...],
        "unresolved_questions": ["question1", "question2", ...],
        "sentiment": "positive/negative/neutral",
        "quality_score": 8,
        "summary": "comprehensive paragraph summary"
    }}"""
    
    try:
        # Use LLM to analyze conversation
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert conversation analyst. Analyze conversations thoroughly and provide structured insights."
                },
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse JSON response
        try:
            analysis_data = json.loads(analysis_text)
        except json.JSONDecodeError:
            # If not valid JSON, create a basic summary
            analysis_data = {
                "topics": ["General conversation"],
                "user_intent": "Information seeking",
                "key_insights": [analysis_text[:200]],
                "unresolved_questions": [],
                "sentiment": "neutral",
                "quality_score": 7,
                "summary": analysis_text[:500]
            }
        
        return analysis_data
    
    except Exception as e:
        print(f"Error analyzing conversation: {e}")
        # Return basic analysis
        return {
            "topics": ["Error occurred during analysis"],
            "user_intent": "Unknown",
            "key_insights": ["Analysis failed"],
            "unresolved_questions": [],
            "sentiment": "neutral",
            "quality_score": 0,
            "summary": f"Error analyzing conversation: {str(e)}"
        }

async def calculate_session_metrics(session_id: str) -> Dict[str, Any]:
    """Calculate various metrics for the session"""
    
    supabase = get_supabase()
    
    # Get session data
    session_response = supabase.table("sessions")\
        .select("*")\
        .eq("session_id", session_id)\
        .execute()
    
    session = session_response.data[0] if session_response.data else {}
    
    # Get all events for the session
    events_response = supabase.table("session_events")\
        .select("*")\
        .eq("session_id", session_id)\
        .order("created_at")\
        .execute()
    
    events = events_response.data
    
    # Calculate metrics
    user_messages = [e for e in events if e["event_type"] == "user_message"]
    ai_responses = [e for e in events if e["event_type"] == "ai_response"]
    tool_calls = [e for e in events if e["event_type"] == "tool_call"]
    
    # Calculate duration
    start_time = datetime.fromisoformat(session.get("start_time"))
    end_time = datetime.fromisoformat(session.get("end_time")) if session.get("end_time") else datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    # Calculate average response time (simplified)
    avg_response_time = 0
    if len(ai_responses) > 0:
        # This is a simplified calculation
        avg_response_time = duration / len(ai_responses)
    
    metrics = {
        "total_messages": len(user_messages) + len(ai_responses),
        "user_messages": len(user_messages),
        "ai_responses": len(ai_responses),
        "tool_calls": len(tool_calls),
        "duration_seconds": duration,
        "avg_response_time_seconds": round(avg_response_time, 2),
        "start_time": session.get("start_time"),
        "end_time": session.get("end_time"),
        "interaction_density": round(len(user_messages) / max(duration / 60, 1), 2)  # messages per minute
    }
    
    return metrics

async def generate_session_summary(session_id: str) -> str:
    """Generate a comprehensive session summary"""
    
    # Get analysis and metrics
    analysis = await analyze_conversation_history(session_id)
    metrics = await calculate_session_metrics(session_id)
    
    # Format summary
    summary = f"""SESSION SUMMARY - {session_id}
    
Duration: {metrics['duration_seconds']:.0f} seconds
Total Messages: {metrics['total_messages']} (User: {metrics['user_messages']}, AI: {metrics['ai_responses']})
Tool Calls: {metrics['tool_calls']}
Average Response Time: {metrics['avg_response_time_seconds']:.1f} seconds

MAIN TOPICS:
{chr(10).join(f'- {topic}' for topic in analysis.get('topics', []))}

USER INTENT:
{analysis.get('user_intent', 'Not determined')}

KEY INSIGHTS:
{chr(10).join(f'- {insight}' for insight in analysis.get('key_insights', []))}

SENTIMENT: {analysis.get('sentiment', 'neutral').upper()}
QUALITY SCORE: {analysis.get('quality_score', 0)}/10

COMPREHENSIVE SUMMARY:
{analysis.get('summary', 'No summary generated')}

UNRESOLVED QUESTIONS:
{chr(10).join(f'- {q}' for q in analysis.get('unresolved_questions', [])) if analysis.get('unresolved_questions') else 'None'}
"""
    
    return summary

async def process_session_summary(session_id: str):
    """Main function to process session summary asynchronously"""
    
    print(f"Starting post-session processing for {session_id}")
    
    try:
        # Generate summary
        summary = await generate_session_summary(session_id)
        
        # Get metrics
        metrics = await calculate_session_metrics(session_id)
        
        # Update session record in database
        supabase = get_supabase()
        
        update_data = {
            "summary": summary,
            "end_time": datetime.utcnow().isoformat(),
            "metadata": {
                "metrics": metrics,
                "processed_at": datetime.utcnow().isoformat()
            }
        }
        
        supabase.table("sessions")\
            .update(update_data)\
            .eq("session_id", session_id)\
            .execute()
        
        print(f"Successfully processed session {session_id}")
        
        # Log the summary generation event
        supabase.table("session_events").insert({
            "session_id": session_id,
            "event_type": "post_session_processing",
            "content": "Session summary generated",
            "metadata": {
                "summary_length": len(summary),
                "metrics": metrics
            },
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "success": True,
            "session_id": session_id,
            "summary_length": len(summary),
            "metrics": metrics
        }
        
    except Exception as e:
        print(f"Error processing session {session_id}: {e}")
        
        # Log error
        supabase = get_supabase()
        supabase.table("session_events").insert({
            "session_id": session_id,
            "event_type": "post_session_error",
            "content": f"Error generating summary: {str(e)}",
            "metadata": {"error": str(e)},
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "success": False,
            "session_id": session_id,
            "error": str(e)
        }

async def batch_process_sessions(session_ids: List[str]):
    """Process multiple sessions in batch"""
    tasks = [process_session_summary(session_id) for session_id in session_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results