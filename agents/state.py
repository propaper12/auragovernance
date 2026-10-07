"""
AuraGovernance - Multi-Agent State Definition
LangGraph StateGraph icin durum yapisi.
"""

from typing import TypedDict, Optional, Dict, Any, List

class AuraAgentState(TypedDict):
    """Orkestrasyon State modeli."""
    user_query: str
    intent: str  # 'GOVERNANCE', 'BI_ANALYTICS', 'HYBRID'
    governance_data: Optional[Dict[str, Any]]
    bi_data: Optional[Dict[str, Any]]
    synthesized_response: Optional[str]
    errors: List[str]
    metadata: Dict[str, Any]
