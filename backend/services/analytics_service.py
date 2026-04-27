"""
Call analytics service - Track and analyze call metrics
"""
from datetime import datetime, timedelta
from typing import Dict, List
import logging
import json

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Track call analytics and metrics"""
    
    def __init__(self):
        # In-memory storage for POC
        # In production, use database (PostgreSQL, MongoDB)
        self.calls = []
        self.queries = {}
    
    def log_call(
        self,
        call_sid: str,
        direction: str,  # "inbound" or "outbound"
        from_number: str,
        to_number: str,
        duration: int = 0,
        status: str = "initiated",
        cost: float = 0.0,
        agent_type: str = "general",
        emotion: str = "neutral",
        transferred: bool = False,
        query_summary: str = ""
    ):
        """Log a call for analytics"""
        
        call_data = {
            "call_sid": call_sid,
            "direction": direction,
            "from_number": from_number,
            "to_number": to_number,
            "duration": duration,
            "status": status,
            "cost": cost,
            "agent_type": agent_type,
            "emotion": emotion,
            "transferred": transferred,
            "query_summary": query_summary,
            "timestamp": datetime.now().isoformat()
        }
        
        self.calls.append(call_data)
        
        # Track common queries
        if query_summary:
            self.queries[query_summary] = self.queries.get(query_summary, 0) + 1
        
        logger.info(f"Call logged: {call_sid} - {direction} - {duration}s")
    
    def get_dashboard_stats(self, days: int = 7) -> Dict:
        """Get analytics dashboard statistics"""
        
        # Filter calls from last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_calls = [
            call for call in self.calls
            if datetime.fromisoformat(call["timestamp"]) > cutoff_date
        ]
        
        if not recent_calls:
            return {
                "total_calls": 0,
                "inbound_calls": 0,
                "outbound_calls": 0,
                "avg_duration": 0,
                "total_cost": 0,
                "success_rate": 0,
                "transfer_rate": 0,
                "top_queries": [],
                "calls_by_agent": {},
                "calls_by_emotion": {},
                "daily_calls": []
            }
        
        # Calculate metrics
        total_calls = len(recent_calls)
        inbound_calls = len([c for c in recent_calls if c["direction"] == "inbound"])
        outbound_calls = len([c for c in recent_calls if c["direction"] == "outbound"])
        
        total_duration = sum(c["duration"] for c in recent_calls)
        avg_duration = total_duration / total_calls if total_calls > 0 else 0
        
        total_cost = sum(c["cost"] for c in recent_calls)
        
        completed_calls = len([c for c in recent_calls if c["status"] == "completed"])
        success_rate = (completed_calls / total_calls * 100) if total_calls > 0 else 0
        
        transferred_calls = len([c for c in recent_calls if c["transferred"]])
        transfer_rate = (transferred_calls / total_calls * 100) if total_calls > 0 else 0
        
        # Top queries
        top_queries = sorted(
            self.queries.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Calls by agent type
        calls_by_agent = {}
        for call in recent_calls:
            agent = call["agent_type"]
            calls_by_agent[agent] = calls_by_agent.get(agent, 0) + 1
        
        # Calls by emotion
        calls_by_emotion = {}
        for call in recent_calls:
            emotion = call["emotion"]
            calls_by_emotion[emotion] = calls_by_emotion.get(emotion, 0) + 1
        
        # Daily call volume
        daily_calls = {}
        for call in recent_calls:
            date = datetime.fromisoformat(call["timestamp"]).date().isoformat()
            daily_calls[date] = daily_calls.get(date, 0) + 1
        
        return {
            "total_calls": total_calls,
            "inbound_calls": inbound_calls,
            "outbound_calls": outbound_calls,
            "avg_duration": round(avg_duration, 2),
            "total_cost": round(total_cost, 2),
            "cost_per_call": round(total_cost / total_calls, 2) if total_calls > 0 else 0,
            "success_rate": round(success_rate, 2),
            "transfer_rate": round(transfer_rate, 2),
            "top_queries": [{"query": q, "count": c} for q, c in top_queries],
            "calls_by_agent": calls_by_agent,
            "calls_by_emotion": calls_by_emotion,
            "daily_calls": [{"date": d, "count": c} for d, c in sorted(daily_calls.items())]
        }
    
    def export_report(self, days: int = 30) -> str:
        """Export analytics report as JSON"""
        stats = self.get_dashboard_stats(days)
        return json.dumps(stats, indent=2)
