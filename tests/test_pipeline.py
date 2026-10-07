"""
AuraGovernance - Uctan Uca Test Senaryolari
Komtas Yonetisim (Damalink) ve Is Zekasi (Qlik) Dogrulama Suite'i
"""

import unittest
from agents.governance_engine import DamalinkGovernanceEngine
from agents.bi_engine import QlikBIEngine
from agents.guardrails import SQLGuardrails
from agents.graph import run_aura_pipeline

class TestAuraGovernance(unittest.TestCase):

    def setUp(self):
        self.gov = DamalinkGovernanceEngine()
        self.bi = QlikBIEngine()

    def test_governance_scan_and_pii(self):
        """Damalink tarama motorunun KVKK/PII ve anomali tespitini test eder."""
        res = self.gov.run_full_governance_scan()
        self.assertGreaterEqual(res["lakehouse_overview"]["total_tables"], 3)
        self.assertGreater(res["lakehouse_overview"]["total_pii_columns_flagged"], 0)
        self.assertGreater(res["lakehouse_overview"]["total_quality_anomalies"], 0)

        # Customers tablosunda TCKN yakalandi mi?
        cust_tbl = next(t for t in res["tables"] if t["table_name"] == "customers")
        pii_types = [p["type"] for p in cust_tbl["pii_columns"]]
        self.assertIn("TCKN", pii_types)
        self.assertIn("PHONE_TR", pii_types)

    def test_guardrails_safety(self):
        """Zararli veya DDL operasyonlarinin engellendigini test eder."""
        safe, sql, err = SQLGuardrails.validate_and_sanitize("SELECT * FROM products")
        self.assertTrue(safe)
        self.assertIn("LIMIT", sql)

        safe_bad, _, err_bad = SQLGuardrails.validate_and_sanitize("DROP TABLE customers;")
        self.assertFalse(safe_bad)
        self.assertIn("Guvenlik Ihiali", err_bad)

    def test_bi_root_cause_analysis(self):
        """Marmara bolgesi kok neden kurgusunun dogru tetiklendigini test eder."""
        res = self.bi.execute_and_analyze("Marmara bolgesinde kar neden dustu? Kok neden analizi yap")
        self.assertTrue(res["success"])
        self.assertEqual(res["analysis_type"], "ROOT_CAUSE")
        self.assertGreater(len(res["data"]), 0)
        self.assertIsNotNone(res["chart_config"])

    def test_langgraph_pipeline(self):
        """LangGraph StateGraph coklu ajan akisinin eksiksiz calistigini dogrular."""
        state = run_aura_pipeline("En cok ciro getiren ilk 5 urun hangisi?")
        self.assertEqual(state["intent"], "BI_ANALYTICS")
        self.assertIsNotNone(state["synthesized_response"])
        self.assertIn("Komtaş Qlik & BI Technology", state["synthesized_response"])

if __name__ == "__main__":
    unittest.main()
