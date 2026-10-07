"""
AuraGovernance - Supervisor Intent Router
Kullanicidan gelen istegi analiz ederek Damalink Yonetisim Ajanina,
Qlik BI Ajanina veya Hibrit Kök Neden orkestrasyonuna yonlendirir.
"""

from typing import Dict, Any
from agents.state import AuraAgentState

class AuraSupervisor:
    """Niyet siniflandirici ve orkestrasyon yonlendiricisi."""

    @classmethod
    def classify_intent(cls, state: AuraAgentState) -> AuraAgentState:
        query = state.get("user_query", "").lower().strip()

        governance_keywords = [
            "yonetisim", "yönetişim", "kvkk", "pii", "kisisel veri", "kişisel veri",
            "katalog", "catalog", "sema", "şema", "null", "kalite", "saglik skoru",
            "sağlık skoru", "tckn", "telefon", "maskeleme", "denetim"
        ]

        hybrid_keywords = [
            "kok neden", "kök neden", "neden dustu", "neden düştü", "varyans",
            "ekosistem ozeti", "ekosistem özeti", "kapsamli analiz", "kapsamlı analiz"
        ]

        if any(hk in query for hk in hybrid_keywords):
            state["intent"] = "HYBRID"
        elif any(gk in query for gk in governance_keywords):
            state["intent"] = "GOVERNANCE"
        else:
            state["intent"] = "BI_ANALYTICS"

        return state
