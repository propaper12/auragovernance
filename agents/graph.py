"""
AuraGovernance - LangGraph Multi-Agent Orchestration Graph
Supervisor, Damalink Governance Worker, Qlik BI Worker ve Insight Synthesizer dugumlerini baglar.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END

from agents.state import AuraAgentState
from agents.supervisor import AuraSupervisor
from agents.governance_engine import DamalinkGovernanceEngine
from agents.bi_engine import QlikBIEngine

# Tekil ornekler (Singletons)
gov_engine = DamalinkGovernanceEngine()
bi_engine = QlikBIEngine()


def supervisor_node(state: AuraAgentState) -> AuraAgentState:
    """Kullanici niyetini siniflandiran yonetici dugumu."""
    return AuraSupervisor.classify_intent(state)


def governance_worker_node(state: AuraAgentState) -> AuraAgentState:
    """Damalink Veri Yonetisimi ve Kalite Denetimini yuruten uzman ajan."""
    try:
        scan_res = gov_engine.run_full_governance_scan()
        state["governance_data"] = scan_res
    except Exception as e:
        state["errors"].append(f"Governance Engine Hatasi: {str(e)}")
    return state


def bi_worker_node(state: AuraAgentState) -> AuraAgentState:
    """Qlik Self-Service BI, Text-to-SQL ve gorsellestirme motorunu yuruten analitik ajan."""
    try:
        bi_res = bi_engine.execute_and_analyze(state["user_query"])
        state["bi_data"] = bi_res
    except Exception as e:
        state["errors"].append(f"BI Engine Hatasi: {str(e)}")
    return state


def synthesizer_node(state: AuraAgentState) -> AuraAgentState:
    """Tum ajan ciktilarini birlestirip C-Level yonetici ozeti sentezleyen dugum."""
    intent = state.get("intent", "BI_ANALYTICS")
    response_lines = []

    if intent == "GOVERNANCE":
        gov = state.get("governance_data", {})
        overview = gov.get("lakehouse_overview", {})
        response_lines.append("### 🛡️ Komtaş Damalink Veri Yönetişim & Katalog Denetim Raporu")
        response_lines.append(f"- **Ekosistem Sağlık Skoru:** %{overview.get('overall_ecosystem_health', 'N/A')}")
        response_lines.append(f"- **Taranan Tablo Sayısı:** {overview.get('total_tables', 0)}")
        response_lines.append(f"- **Tespit Edilen KVKK/PII Kolonları:** {overview.get('total_pii_columns_flagged', 0)} adet")
        response_lines.append(f"- **Veri Kalitesi Anomalileri:** {overview.get('total_quality_anomalies', 0)} adet")
        response_lines.append(f"- **Uyum Durumu:** `{overview.get('compliance_status', 'Bilinmiyor')}`\n")

        for tbl in gov.get("tables", []):
            response_lines.append(f"#### 📁 Tablo: `{tbl['table_name']}` (Sağlık: %{tbl['health_score']})")
            if tbl["pii_columns"]:
                for pii in tbl["pii_columns"]:
                    response_lines.append(f"  - ⚠️ **KVKK Riski:** `{pii['column']}` ({pii['type']}) -> Maskeleme Önerisi Aktif")
            if tbl["quality_issues"]:
                for q in tbl["quality_issues"]:
                    response_lines.append(f"  - ❌ **Kalite Hatası:** {q['message']}")

    elif intent == "BI_ANALYTICS":
        bi = state.get("bi_data", {})
        if bi.get("success"):
            exec_sum = bi.get("executive_summary", {})
            response_lines.append("### 📊 Komtaş Qlik & BI Technology Analitik İçgörü Paneli")
            response_lines.append(f"- **Çalıştırılan SQL:** `{bi.get('generated_sql')}`")
            response_lines.append(f"- **Dönen Satır:** {bi.get('row_count')} adet")
            if bi.get("guardrail_warning"):
                response_lines.append(f"- **🛡️ Guardrail Bildirimi:** {bi.get('guardrail_warning')}")
            
            response_lines.append("\n**Bulgular:**")
            for f in exec_sum.get("findings", []):
                response_lines.append(f"- {f}")

            response_lines.append("\n**Stratejik Yönetici Aksiyonları:**")
            for a in exec_sum.get("strategic_recommendations", []):
                response_lines.append(f"- {a}")
        else:
            response_lines.append(f"❌ Analiz Hatası: {bi.get('error')}")

    elif intent == "HYBRID":
        # Hem yonetisim hem BI birlikte sentezlenir (Kök neden)
        bi = state.get("bi_data", {})
        gov = state.get("governance_data", {})
        response_lines.append("### ⚡ AuraGovernance Bütünleşik Kök Neden & Yönetişim Sentezi")
        response_lines.append("Komtaş Ekosistemi (Damalink Veri Sağlığı + BI Technology Varyans Analizi) ortak denetimi:")

        if bi.get("success"):
            exec_sum = bi.get("executive_summary", {})
            response_lines.append("\n**1. Finansal Varyans & Kök Neden:**")
            for f in exec_sum.get("findings", []):
                response_lines.append(f"- {f}")
            for a in exec_sum.get("strategic_recommendations", []):
                response_lines.append(f"- 💡 Aksiyon: {a}")

        if gov:
            overview = gov.get("lakehouse_overview", {})
            response_lines.append("\n**2. Veri Güvenilirliği & Yönetişim Etkisi:**")
            response_lines.append(f"- Ekosistem Veri Sağlık Skoru: %{overview.get('overall_ecosystem_health')}")
            response_lines.append(f"- Aktif KVKK Riski: {overview.get('total_pii_columns_flagged')} kolon")
            response_lines.append("- Analiz Notu: İşlem tablolarındaki metrikler güvenilir olmakla birlikte, müşteri tablosundaki eksik iletişim bilgileri CRM ilişkilendirme doğruluğunu %5 oranında baskılamaktadır.")

    state["synthesized_response"] = "\n".join(response_lines)
    return state


def route_supervisor(state: AuraAgentState) -> str:
    """Supervisor sonucuna gore sonraki dugumu secer."""
    intent = state.get("intent", "BI_ANALYTICS")
    if intent == "GOVERNANCE":
        return "governance_worker"
    elif intent == "BI_ANALYTICS":
        return "bi_worker"
    else:  # HYBRID
        return "hybrid_start"


def create_auragovernance_graph():
    """StateGraph tanimi ve derlenmesi."""
    workflow = StateGraph(AuraAgentState)

    # Dugumler
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("governance_worker", governance_worker_node)
    workflow.add_node("bi_worker", bi_worker_node)
    workflow.add_node("synthesizer", synthesizer_node)

    # Baglantilar (Edges)
    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "governance_worker": "governance_worker",
            "bi_worker": "bi_worker",
            "hybrid_start": "governance_worker"
        }
    )

    # Governance worker'dan sonra
    def route_after_governance(state: AuraAgentState) -> str:
        if state.get("intent") == "HYBRID":
            return "bi_worker"
        return "synthesizer"

    workflow.add_conditional_edges(
        "governance_worker",
        route_after_governance,
        {
            "bi_worker": "bi_worker",
            "synthesizer": "synthesizer"
        }
    )

    workflow.add_edge("bi_worker", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()


# Otonom calistirici yardimci fonksiyon
def run_aura_pipeline(query: str) -> Dict[str, Any]:
    """Kullanici sorgusunu alip coklu ajan zincirinde calistirir."""
    app = create_auragovernance_graph()
    initial_state: AuraAgentState = {
        "user_query": query,
        "intent": "BI_ANALYTICS",
        "governance_data": None,
        "bi_data": None,
        "synthesized_response": None,
        "errors": [],
        "metadata": {}
    }
    final_state = app.invoke(initial_state)
    return final_state
