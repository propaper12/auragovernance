import duckdb
from typing import List, Dict, Any, Optional
from config import DB_PATH

def get_db_connection(read_only: bool = False):
    """DuckDB bağlantısı döner."""
    return duckdb.connect(DB_PATH, read_only=read_only)

def execute_query(query: str, params: Optional[list] = None) -> List[Dict[str, Any]]:
    """Parametreli sorgu çalıştırır ve sütun isimleriyle birlikte sözlük listesi döner."""
    con = get_db_connection()
    try:
        if params:
            res = con.execute(query, params)
        else:
            res = con.execute(query)
        columns = [desc[0] for desc in res.description] if res.description else []
        rows = res.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        con.close()

def get_existing_tables() -> List[str]:
    """Veritabanındaki kullanıcı tablolarını listeler."""
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'main' AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """
    rows = execute_query(query)
    return [r["table_name"] for r in rows]

def get_table_schema(table_name: str) -> List[Dict[str, Any]]:
    """Bir tablonun kolon isimleri ve veri tiplerini döner."""
    query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_schema = 'main' AND table_name = ?
        ORDER BY ordinal_position
    """
    return execute_query(query, [table_name])
