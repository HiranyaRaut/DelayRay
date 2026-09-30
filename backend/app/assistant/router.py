"""
DelayRay Assistant Router & Tool Registry
"""

from typing import Dict, Any, List

AVAILABLE_TOOLS = [
    "sql_query",
    "project_lookup",
    "top_risk",
    "compare_projects",
    "explain_project",
    "alerts_summary",
    "model_leaderboard",
    "remarks_search"
]

def route_user_query(query: str) -> Dict[str, Any]:
    """Routes query to appropriate tool or intent."""
    return {"intent": "general", "tool": "sql_query", "params": {}}
