import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "lakehouse_warehouse.duckdb")

APP_NAME = "AuraGovernance"
APP_SUBTITLE = "Autonomous Lakehouse Data Catalog, Quality Governance & Self-Service BI Agent"
APP_VERSION = "1.0.0"
ECOSYSTEM_TARGET = "Komtaş Veri ve Analitik Ekosistemi (Damalink & BI Technology Synergy)"

# Veri Yönetişim ve Kalite Eşikleri
GOVERNANCE_CONFIG = {
    "max_acceptable_null_pct": 5.0,        # %5'ten fazla null değer kalite uyarısı üretir
    "critical_null_pct": 15.0,             # %15'ten fazlası kritik hata üretir
    "min_uniqueness_for_pk": 99.0,         # Birincil anahtar adaylığı için benzersizlik oranı
    "pii_mask_char": "*",
}

# KVKK & Kişisel Veri (PII) Regex Desenleri
PII_PATTERNS = {
    "TCKN": r"\b[1-9]\d{10}\b",
    "PHONE_TR": r"(?:\+90|0)?\s?5\d{2}\s?\d{3}\s?\d{2}\s?\d{2}",
    "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "IBAN_TR": r"TR\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{2}",
    "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
}
