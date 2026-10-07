"""
AuraGovernance - SQL Safety & PII Guardrails
Sorgu guvenlik filtresi: Yalnizca salt-okunur (SELECT) sorgularina izin verir,
DDL/DML operasyonlarini engeller ve PII alanlari icin dinamik maskeleme/guvenlik uyarisi saglar.
"""

import re
from typing import Tuple, Optional

# Yasakli DDL/DML anahtar kelimeleri
FORBIDDEN_KEYWORDS = [
    r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", r"\bINSERT\b",
    r"\bALTER\b", r"\bTRUNCATE\b", r"\bCREATE\b", r"\bREPLACE\b",
    r"\bGRANT\b", r"\bREVOKE\b", r"\bATTACH\b", r"\bDETACH\b",
    r"\bEXEC\b", r"\bEXECUTE\b", r"\bPRAGMA\b", r"\bCOPY\b"
]

PII_SUSPICIOUS_COLUMNS = [
    "tc_identity_no", "phone_number", "email", "tc_no", "iban"
]

class SQLGuardrails:
    """Kurumsal SQL Guvenlik ve KVKK Filtreleme Kalkanı."""

    @classmethod
    def validate_and_sanitize(cls, sql_query: str) -> Tuple[bool, str, Optional[str]]:
        """
        Sorgunun guvenli bir SELECT sorgusu oldugunu dogrular ve gerekiyorsa LIMIT ekler.
        Returns: (is_safe, sanitized_sql, error_or_warning_message)
        """
        if not sql_query or not sql_query.strip():
            return False, "", "Bos sorgu calistirilamaz."

        cleaned = sql_query.strip()
        # Sondaki noktali virgulu temizle
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()

        # 1. Yalnizca SELECT ile baslamalidir (veya WITH cte AS ... SELECT)
        normalized_query = re.sub(r"\s+", " ", cleaned).upper()
        if not (normalized_query.startswith("SELECT") or normalized_query.startswith("WITH")):
            return False, cleaned, "Guvenlik Ihiali: Yalnizca salt-okunur 'SELECT' veya 'WITH' analiz sorgularina izin verilir."

        # 2. Yasakli operasyon regex kontrolu
        for pattern in FORBIDDEN_KEYWORDS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                matched = re.search(pattern, cleaned, re.IGNORECASE).group(0)
                return False, cleaned, f"Guvenlik Ihiali: '{matched}' gibi degisiklik/DDL/DML komutlarina izin verilmez."

        # 3. PII Kolon Denetimi (Kullanici acik PII cekmek istiyorsa bilgilendirici uyari ver)
        pii_warning = None
        for pii_col in PII_SUSPICIOUS_COLUMNS:
            if re.search(rf"\b{pii_col}\b", cleaned, re.IGNORECASE):
                pii_warning = f"KVKK Uyarisi: Sorgu dogrudan hassas kisisel veri ('{pii_col}') iceriyor. Maskeleme onerilir."
                break

        # 4. Limit Guvenligi: Cok yuksek yuk olmamasi icin LIMIT yoksa ekle
        if not re.search(r"\bLIMIT\s+\d+", cleaned, re.IGNORECASE):
            cleaned += " LIMIT 100"

        return True, cleaned, pii_warning
