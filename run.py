"""
AuraGovernance - Calistirma Scripti (Entrypoint)
Komtas Veri ve Analitik Ekosistemi Cozum Projesi
"""

import sys
import uvicorn
from pathlib import Path

# Proje ana dizinini path'e ekle
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 AuraGovernance: Autonomous Lakehouse Catalog, Governance & BI Copilot")
    print("🎯 Hedef: Komtaş Veri ve Analitik Ekosistemi (Damalink & Qlik Synergy)")
    print("📍 URL: http://127.0.0.1:8001")
    print("=" * 70)
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
