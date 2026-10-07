"""
AuraGovernance - Damalink Synergy: Veri Yonetisim, KVKK/PII Tarama ve Veri Kalitesi Motoru
Komtas Veri Yonetisim cozumu Damalink standartlarina uygun otonom lakehouse denetim mekanizmasi.
"""

import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from database.connection import get_db_connection, get_existing_tables, get_table_schema
from config import PII_PATTERNS, GOVERNANCE_CONFIG

# Damalink Is Sozlugu ve Aciklama Eslesimleri (Business Glossary Heuristics)
BUSINESS_GLOSSARY_DEFINITIONS = {
    "customers": {
        "description": "Kurumsal ve bireysel musteri temel varlik tablosu; kimlik, iletisim ve segmentasyon verilerini barindirir.",
        "category": "Musteri & CRM",
        "owner": "Musteri Deneyimi & Uyum Departmani",
        "classification": "Gizli (Confidential / KVKK)",
        "columns": {
            "customer_id": "Musteri tekil tanimlayicisi (Birincil Anahtar)",
            "full_name": "Musteri ad ve soyad bilgisi (Kimlik Verisi)",
            "tc_identity_no": "Turkiye Cumhuriyeti Kimlik Numarasi (Hassas Kisisel Veri)",
            "phone_number": "Musteri iletisim GSM numarasi (Iletisim Verisi)",
            "email": "Elektronik posta adresi",
            "city": "Musteri ikamet sehri / Lokasyon",
            "segment": "Musteri harcama ve sadakat segmenti (Bireysel, Premium, Kurumsal)",
            "account_balance": "Musterinin guncel bakiye / hesap varligi (TL)",
            "created_at": "Musteri kayit zaman damgasi"
        }
    },
    "products": {
        "description": "E-ticaret ve magaza urun katalogu; maliyet, satis fiyati ve envanter stok durumunu icerir.",
        "category": "Urun & Tedarik Zinciri",
        "owner": "Kategori Yonetimi & Lojistik",
        "classification": "Dahili (Internal)",
        "columns": {
            "product_id": "Urun tekil tanimlayici kodu (SKU)",
            "product_name": "Urunun pazarlama ve etiket adi",
            "category_name": "Ana urun kategorisi",
            "unit_cost": "Birim uretim / tedarik maliyeti (TL)",
            "unit_price": "Birim raf satis fiyati (TL)",
            "stock_quantity": "Guncel depodaki fiziki stok miktari (Adet)"
        }
    },
    "transactions": {
        "description": "Tum satis, iade ve finansal hareketlerin detayli lakehouse islem tablosu.",
        "category": "Finans & Satis Operasyonlari",
        "owner": "Finansal Raporlama & BI Direktörlugu",
        "classification": "Kritik Is Verisi (Business Critical)",
        "columns": {
            "transaction_id": "Islem tekil siparis/fis numarasi",
            "customer_id": "Islemi gerceklestiren musteri ID (Yabanci Anahtar)",
            "product_id": "Satin alinan urun kodu (Yabanci Anahtar)",
            "quantity": "Siparis edilen urun adedi",
            "total_amount": "Toplam fatura tahsilat tutari (TL)",
            "profit_amount": "Islem basina elde edilen net brut kar (TL)",
            "discount_pct": "Uygulanan kampanya/indirim yuzdesi",
            "payment_method": "Kullanilan odeme araci (Kredi Karti, EFT vb.)",
            "region": "Satisin gerceklestigi cografi bolge",
            "transaction_date": "Islemin tamamlandigi tarih ve saat"
        }
    }
}


def mask_pii_value(value: Any, pii_type: str) -> str:
    """Kisisel verileri maskeleme algoritmasi (KVKK / Maskeleme)."""
    if value is None:
        return "[NULL]"
    s = str(value).strip()
    if not s:
        return ""
    
    if pii_type == "TCKN":
        # Ornek: 12345678901 -> 123*****89
        if len(s) == 11:
            return s[:3] + "*****" + s[-2:]
        return s[:2] + "****" + s[-1:]
    elif pii_type == "PHONE_TR":
        # Ornek: +90 532 123 45 67 -> +90 532 *** ** 67
        parts = s.split()
        if len(parts) >= 4:
            return f"{parts[0]} {parts[1]} *** ** {parts[-1]}"
        return s[:6] + "******" + s[-2:]
    elif pii_type == "EMAIL":
        # Ornek: ahmet.yilmaz@example.com -> a***z@example.com
        if "@" in s:
            user_part, domain = s.split("@", 1)
            if len(user_part) > 2:
                masked_user = user_part[0] + "***" + user_part[-1]
            else:
                masked_user = user_part[0] + "***"
            return f"{masked_user}@{domain}"
        return s[:2] + "***"
    elif pii_type == "CREDIT_CARD":
        # Ornek: 1234-5678-9012-3456 -> 1234-****-****-3456
        digits = re.sub(r"\D", "", s)
        if len(digits) == 16:
            return f"{digits[:4]}-****-****-{digits[-4:]}"
        return "****-****-****-****"
    elif pii_type == "IBAN_TR":
        # Ornek: TR12 3456 ... -> TR12 **** **** **** **** 34
        if len(s) >= 10:
            return s[:4] + " **** **** **** " + s[-4:]
        return "TR** ****"
    
    return s[:2] + "***" + s[-2:] if len(s) > 4 else "***"


class DamalinkGovernanceEngine:
    """
    Komtas Damalink Veri Yonetisim ve Kataloglama Ajaninin Cekirdek Motoru.
    """

    def __init__(self):
        self.config = GOVERNANCE_CONFIG
        self.pii_patterns = {k: re.compile(v) for k, v in PII_PATTERNS.items()}

    def inspect_column_pii(self, col_name: str, sample_values: List[Any]) -> Optional[Dict[str, Any]]:
        """Bir kolonun PII/KVKK verisi barindirip barindirmadigini analiz eder."""
        col_lower = col_name.lower()
        
        # Kolon ismi ipuclari
        name_hint_map = {
            "tc": "TCKN",
            "tckn": "TCKN",
            "identity": "TCKN",
            "phone": "PHONE_TR",
            "tel": "PHONE_TR",
            "gsm": "PHONE_TR",
            "email": "EMAIL",
            "mail": "EMAIL",
            "iban": "IBAN_TR",
            "card": "CREDIT_CARD"
        }

        detected_type = None
        for hint, p_type in name_hint_map.items():
            if hint in col_lower:
                detected_type = p_type
                break

        # Deger ornekleri uzerinden regex denetimi
        valid_samples = [str(v) for v in sample_values if v is not None and str(v).strip() != ""]
        if valid_samples:
            for p_type, regex in self.pii_patterns.items():
                match_count = sum(1 for val in valid_samples if regex.search(val))
                if match_count / len(valid_samples) >= 0.4:  # Orneklerin %40'i uyuyorsa
                    detected_type = p_type
                    break

        if detected_type:
            masked_samples = [mask_pii_value(v, detected_type) for v in valid_samples[:3]]
            return {
                "is_pii": True,
                "pii_type": detected_type,
                "severity": "CRITICAL" if detected_type in ["TCKN", "CREDIT_CARD"] else "HIGH",
                "recommended_action": f"KVKK Uyumsuzluk Riski: {detected_type} kolonu sifrelenmeli veya sorgularda dinamik maskelenmeli.",
                "sample_masked": masked_samples
            }
        
        return None

    def profile_table(self, table_name: str) -> Dict[str, Any]:
        """Bir tablonun detayli sema, kalite ve yonetisim profilini cikarir."""
        con = get_db_connection()
        try:
            # 1. Satir sayisi
            row_count_res = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            total_rows = row_count_res[0] if row_count_res else 0

            # 2. Kolon semasi
            schema_info = get_table_schema(table_name)
            column_profiles = []
            pii_columns = []
            quality_issues = []

            for col in schema_info:
                c_name = col["column_name"]
                c_type = col["data_type"]

                # Null analizi
                null_res = con.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {c_name} IS NULL").fetchone()
                null_count = null_res[0] if null_res else 0
                null_pct = round((null_count / total_rows * 100), 2) if total_rows > 0 else 0.0

                # Unique analizi
                uniq_res = con.execute(f"SELECT COUNT(DISTINCT {c_name}) FROM {table_name}").fetchone()
                unique_count = uniq_res[0] if uniq_res else 0
                unique_pct = round((unique_count / total_rows * 100), 2) if total_rows > 0 else 0.0

                # Ornek degerler
                sample_rows = con.execute(f"SELECT {c_name} FROM {table_name} WHERE {c_name} IS NOT NULL LIMIT 10").fetchall()
                sample_vals = [r[0] for r in sample_rows]

                # PII Denetimi
                pii_info = self.inspect_column_pii(c_name, sample_vals)
                if pii_info:
                    pii_columns.append({
                        "column": c_name,
                        "type": pii_info["pii_type"],
                        "severity": pii_info["severity"],
                        "recommendation": pii_info["recommended_action"],
                        "masked_preview": pii_info["sample_masked"]
                    })

                # Kalite kurallari (Null oranlari)
                if null_pct > self.config["critical_null_pct"]:
                    quality_issues.append({
                        "level": "CRITICAL",
                        "column": c_name,
                        "message": f"Kritik Null Orani: '{c_name}' alaninda %{null_pct} bos deger var (Eşik: %{self.config['critical_null_pct']})."
                    })
                elif null_pct > self.config["max_acceptable_null_pct"]:
                    quality_issues.append({
                        "level": "WARNING",
                        "column": c_name,
                        "message": f"Kabul Edilebilir Null Esigi Asildi: '{c_name}' alaninda %{null_pct} bos deger tespit edildi."
                    })

                # Kolon profili
                col_profile = {
                    "name": c_name,
                    "type": c_type,
                    "null_count": null_count,
                    "null_pct": null_pct,
                    "unique_count": unique_count,
                    "unique_pct": unique_pct,
                    "is_primary_key_candidate": unique_pct >= self.config["min_uniqueness_for_pk"] and null_count == 0,
                    "is_pii": pii_info is not None,
                    "pii_meta": pii_info
                }
                column_profiles.append(col_profile)

            # 3. Ozel Domain Kalite Kontrolleri (Anomaliler)
            if table_name == "products":
                neg_stock = con.execute("SELECT COUNT(*) FROM products WHERE stock_quantity < 0").fetchone()[0]
                if neg_stock > 0:
                    quality_issues.append({
                        "level": "CRITICAL",
                        "column": "stock_quantity",
                        "message": f"Fiziki Stok Tutarsizligi: {neg_stock} adet urunde negatif stok degeri saptandi! (Damalink Anomaly Alert)"
                    })

            if table_name == "transactions":
                zero_or_neg = con.execute("SELECT COUNT(*) FROM transactions WHERE total_amount <= 0").fetchone()[0]
                if zero_or_neg > 0:
                    quality_issues.append({
                        "level": "CRITICAL",
                        "column": "total_amount",
                        "message": f"Satis Tutari Anomali: {zero_or_neg} islemde 0 veya negatif tutar tespit edildi."
                    })

            # 4. Genel Saglik Skoru Hesaplama (0 - 100)
            score = 100.0
            for issue in quality_issues:
                if issue["level"] == "CRITICAL":
                    score -= 15.0
                elif issue["level"] == "WARNING":
                    score -= 5.0
            
            # Maskelenmemis PII her kolon icin -5 ceza
            for pii in pii_columns:
                score -= 5.0
            
            health_score = max(0.0, min(100.0, score))

            # 5. Is Sozlugu (Glossary) Zenginlestirme
            glossary_meta = BUSINESS_GLOSSARY_DEFINITIONS.get(table_name, {
                "description": f"{table_name} lakehouse tablosu",
                "category": "Genel Veri Varligi",
                "owner": "Veri Muhendisligi",
                "classification": "Dahili",
                "columns": {}
            })

            return {
                "table_name": table_name,
                "total_rows": total_rows,
                "column_count": len(column_profiles),
                "columns": column_profiles,
                "pii_columns": pii_columns,
                "quality_issues": quality_issues,
                "health_score": round(health_score, 1),
                "health_status": "EXCELLENT" if health_score >= 90 else ("GOOD" if health_score >= 75 else ("RISKY" if health_score >= 50 else "CRITICAL")),
                "business_glossary": glossary_meta,
                "scanned_at": datetime.now().isoformat()
            }
        finally:
            con.close()

    def run_full_governance_scan(self) -> Dict[str, Any]:
        """Lakehouse'taki tum tablolari tarar ve denetim ozetini uretir."""
        tables = get_existing_tables()
        # Sistem tablosunu filtrele
        target_tables = [t for t in tables if t != "data_catalog_metadata"]

        catalog = []
        total_pii_detected = 0
        total_issues_detected = 0
        cumulative_health = 0.0

        for tbl in target_tables:
            profile = self.profile_table(tbl)
            catalog.append(profile)
            total_pii_detected += len(profile["pii_columns"])
            total_issues_detected += len(profile["quality_issues"])
            cumulative_health += profile["health_score"]

            # Snapshot kaydi
            self._save_catalog_snapshot(profile)

        avg_health = round(cumulative_health / len(catalog), 1) if catalog else 100.0

        return {
            "lakehouse_overview": {
                "total_tables": len(catalog),
                "overall_ecosystem_health": avg_health,
                "total_pii_columns_flagged": total_pii_detected,
                "total_quality_anomalies": total_issues_detected,
                "compliance_status": "KVKK & Kalite Eylemi Gerekli" if total_pii_detected > 0 or total_issues_detected > 0 else "Uyumlu",
                "scan_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "tables": catalog
        }

    def _save_catalog_snapshot(self, profile: Dict[str, Any]):
        """Denetim ozetini data_catalog_metadata tablosuna kaydeder."""
        con = get_db_connection()
        try:
            audit_id = f"AUD-{uuid.uuid4().hex[:8]}"
            pii_cols = [p["column"] for p in profile["pii_columns"]]
            issues = [i["message"] for i in profile["quality_issues"]]
            desc = profile["business_glossary"].get("description", "")
            
            con.execute("""
                INSERT INTO data_catalog_metadata VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                audit_id,
                profile["table_name"],
                profile["total_rows"],
                profile["column_count"],
                profile["health_score"],
                pii_cols,
                issues,
                desc,
                datetime.now()
            ])
        except Exception as e:
            # Snapshot hatasi ana akisi bozmasin
            pass
        finally:
            con.close()


if __name__ == "__main__":
    engine = DamalinkGovernanceEngine()
    result = engine.run_full_governance_scan()
    print(">>> [Damalink Governance Engine] Tarama Tamamlandi:")
    print(f"    * Toplam Tablo: {result['lakehouse_overview']['total_tables']}")
    print(f"    * Ekosistem Saglik Skoru: %{result['lakehouse_overview']['overall_ecosystem_health']}")
    print(f"    * Tespit Edilen PII Kolonlari: {result['lakehouse_overview']['total_pii_columns_flagged']}")
    print(f"    * Veri Kalitesi Anomalileri: {result['lakehouse_overview']['total_quality_anomalies']}")
    for tbl in result["tables"]:
        print(f"\n--- Tablo: {tbl['table_name']} (Skor: {tbl['health_score']} - {tbl['health_status']}) ---")
        for p in tbl["pii_columns"]:
            print(f"    [KVKK UYARISI] {p['column']} -> Tip: {p['type']} ({p['severity']})")
        for q in tbl["quality_issues"]:
            print(f"    [KALITE HATASI] {q['column']} -> {q['message']}")
