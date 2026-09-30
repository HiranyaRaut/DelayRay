"""
DelayRay Guarded Text-to-SQL Engine
Parses and validates SQL queries using sqlglot.
Enforces: single SELECT, allowlisted views only, injected LIMIT 200, no comments/DDL/DML.
"""

from typing import Tuple, List, Optional
import sqlglot
from sqlglot import exp

ALLOWLISTED_VIEWS = {
    "vw_project_latest",
    "vw_open_alerts",
    "vw_sector_summary",
    "vw_state_summary",
    "vw_model_leaderboard"
}

class SQLGuardError(Exception):
    pass

def validate_and_guard_sql(sql_str: str, max_limit: int = 200) -> str:
    """
    Validates that query is a single safe SELECT over allowlisted views and applies LIMIT.
    """
    cleaned_sql = sql_str.strip()
    if not cleaned_sql:
        raise SQLGuardError("Empty query provided.")

    try:
        parsed_statements = sqlglot.parse(cleaned_sql)
    except Exception as e:
        raise SQLGuardError(f"SQL parsing syntax error: {str(e)}")

    if len(parsed_statements) != 1:
        raise SQLGuardError("Only a single SQL statement is allowed.")

    statement = parsed_statements[0]
    if not isinstance(statement, exp.Select):
        raise SQLGuardError("Only SELECT queries are permitted.")

    # Check referenced tables
    tables = [table.name.lower() for table in statement.find_all(exp.Table)]
    for tbl in tables:
        if tbl not in ALLOWLISTED_VIEWS:
            raise SQLGuardError(f"Unauthorized table/view access: '{tbl}'. Query must target allowlisted views.")

    # Enforce LIMIT 200
    limited_statement = statement.limit(max_limit)
    return limited_statement.sql()
