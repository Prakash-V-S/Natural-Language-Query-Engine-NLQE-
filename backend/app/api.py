from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from app.llm import parse_natural_query
from app.db import run_sql

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any] = {}

@router.post("/query", response_model=QueryResponse)
async def run_query(req: QueryRequest):
    q = req.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="query is empty")

    # STEP 1 — LLM parse
    parsed = await parse_natural_query(q)

    sql = parsed.get("sql", "SELECT 1;")

    # STEP 2 — Execute SQL
    result = run_sql(sql)

    rows = result.get("rows", [])
    cols = result.get("columns", [])
    err  = result.get("error")

    parsed["data_rows"] = rows
    parsed["data_columns"] = cols
    parsed["sql_error"] = err

    # NEW CHECK — If no data returned
    if err:
        return {
            "status": "error",
            "message": "SQL execution error",
            "data": parsed
        }

    if len(rows) == 0:
        return {
            "status": "ok",
            "message": "No data found",
            "data": parsed
        }

    return {
        "status": "ok",
        "message": "Query processed",
        "data": parsed
    }
