"""
AuraGovernance - FastAPI Application Server
Komtas Veri ve Analitik Ekosistemi (Damalink & BI Technology) Icin
Otonom Yonetisim ve Is Zekasi Servisi.
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from config import APP_NAME, APP_SUBTITLE, APP_VERSION, ECOSYSTEM_TARGET
from agents.governance_engine import DamalinkGovernanceEngine
from agents.bi_engine import QlikBIEngine
from agents.graph import run_aura_pipeline
from database.connection import get_db_connection

app = FastAPI(
    title=APP_NAME,
    description=APP_SUBTITLE,
    version=APP_VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gov_engine = DamalinkGovernanceEngine()
bi_engine = QlikBIEngine()

# Request Modelleri
class BIQueryRequest(BaseModel):
    query: str
    custom_sql: Optional[str] = None

class ChatRequest(BaseModel):
    message: str


@app.get("/api/status")
def get_system_status():
    """Sistem genel durumu ve ekosistem bilgisi."""
    return {
        "app_name": APP_NAME,
        "subtitle": APP_SUBTITLE,
        "version": APP_VERSION,
        "target": ECOSYSTEM_TARGET,
        "status": "ONLINE",
        "engine_technologies": [
            "DuckDB In-Memory Lakehouse",
            "LangGraph Multi-Agent Orchestration",
            "Damalink PII & Governance Profiler",
            "Qlik Semantic Text-to-SQL & Variance Engine"
        ]
    }


@app.get("/api/governance/scan")
def get_governance_scan():
    """Damalink otonom sema, PII ve veri kalitesi taramasi."""
    try:
        return gov_engine.run_full_governance_scan()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/governance/table/{table_name}")
def get_table_governance(table_name: str):
    """Belirli bir tablonun detayli yonetisim profili."""
    try:
        return gov_engine.profile_table(table_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Tablo bulunamadi: {str(e)}")


@app.post("/api/bi/query")
def execute_bi_query(req: BIQueryRequest):
    """Qlik Self-Service BI dogal dil sorgulama ve analiz servisi."""
    try:
        res = bi_engine.execute_and_analyze(req.query, req.custom_sql)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/orchestrator/chat")
def orchestrator_chat(req: ChatRequest):
    """LangGraph Coklu Ajan Yonlendiricisi ve Sentezleyici."""
    try:
        final_state = run_aura_pipeline(req.message)
        chart_config = None
        if final_state.get("bi_data") and final_state["bi_data"].get("chart_config"):
            chart_config = final_state["bi_data"]["chart_config"]

        return {
            "query": req.message,
            "intent": final_state.get("intent"),
            "response": final_state.get("synthesized_response"),
            "governance_data": final_state.get("governance_data"),
            "bi_data": final_state.get("bi_data"),
            "chart_config": chart_config,
            "errors": final_state.get("errors")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bi/quick-insights")
def get_quick_insights():
    """Dashboard ust KPI kartlari."""
    con = get_db_connection()
    try:
        tx_stats = con.execute("""
            SELECT 
                COUNT(*) as total_tx,
                ROUND(SUM(total_amount), 2) as total_rev,
                ROUND(SUM(profit_amount), 2) as total_profit,
                ROUND(SUM(profit_amount) / NULLIF(SUM(total_amount), 0) * 100, 1) as profit_margin
            FROM transactions
        """).fetchone()

        cust_count = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        prod_count = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]

        return {
            "total_transactions": tx_stats[0],
            "total_revenue": tx_stats[1],
            "total_profit": tx_stats[2],
            "profit_margin_pct": tx_stats[3],
            "total_customers": cust_count,
            "total_products": prod_count,
            "lakehouse_engine": "DuckDB Columnar In-Memory"
        }
    finally:
        con.close()


# Frontend Statik Dizin Yonlendirmesi
web_dir = os.path.join(os.path.dirname(__file__), "web")
if os.path.exists(web_dir):
    app.mount("/static", StaticFiles(directory=web_dir), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(web_dir, "index.html"))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False)
