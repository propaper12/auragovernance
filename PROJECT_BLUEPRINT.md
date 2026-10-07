# AuraGovernance 🛡️⚡
### Autonomous Lakehouse Data Catalog, Quality Governance & Self-Service BI Agent
**Hedef Ekosistem:** Komtaş Veri ve Analitik Ekosistemi (*Damalink & BI Technology Synergy*)  
**Geliştirici:** Ömer Çakan | **Teknoloji Yığını:** LangGraph, Python, DuckDB, FastAPI, Qlik/Starburst Mimari Uyumu

---

## 1. 📌 Proje Vizyonu ve Komtaş Ekosistemi Eşleşmesi

Komtaş, kurumsal müşterilere (Bankacılık, FinTech, Telekom, Perakende) uçtan uca veri çözümleri sunan Türkiye'nin lider veri ekosistemidir. Bu proje, Komtaş bünyesindeki iki ana şirketin ve iş ortaklığının en kritik kurumsal darboğazını çözer:

| Komtaş Şirketi / Çözümü | Kurumsal Problem | AuraGovernance Çözümü |
|---|---|---|
| **Damalink** *(Veri Yönetişimi)* | Veri ambarlarında binlerce tablo var; hangi kolonda KVKK/PII (Kişisel Veri) var bilinmiyor, veri kalitesi ve kataloglama manuel yapılıyor. | **Autonomous Governance Agent:** DuckDB/Lakehouse tablolarını otonom tarar, PII (TCKN, IBAN, Tel) tespit edip maskeler, veri sağlığı profilini çıkarır ve otomatik veri sözlüğü üretir. |
| **BI Technology** *(Qlik Distribütörü)* | İş birimleri ve yöneticiler SQL yazamıyor; Qlik panolarında bazen *"satışlar neden düştü?"* sorusunun kök nedenini hızlıca bulamıyor. | **Text-to-Insight BI Agent:** Doğal dildeki iş sorularını SQL'e dönüştürür, çalıştırır, interaktif grafik çizer ve kök neden analizli (Root-Cause) yönetici özeti yazar. |
| **Analythinx & Starburst/MinIO** | Veri ambarlarının hantal sorgu süreçleri ve yüksek bulut maliyetleri. | **In-Memory Columnar OLAP (DuckDB):** Saniyede milyonlarca satırı alt-milisaniye hızla tarayan, MinIO/S3 uyumlu modern göl evi (Lakehouse) mimarisi. |

---

## 2. 🏗️ Sistem Mimarisi (Architecture)

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      KULLANICI ARAYÜZÜ (WEB DASHBOARD)                 │
 │   • Data Governance & Catalog Ekranı (Tablo Sağlığı, PII Etiketleri)   │
 │   • Autonomous BI Copilot (Doğal Dil Sohbet, Grafikler, Yönetici Notu) │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ REST & WebSocket
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      FASTAPI ORKESTRASYON KATMANI                      │
 │    Endpoints: /api/governance/scan, /api/bi/chat, /api/catalog/schema  │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                  LANGGRAPH MULTI-AGENT STATE GRAPH                     │
 │                                                                        │
 │                      ┌──────────────────────┐                          │
 │                      │   Supervisor Agent   │                          │
 │                      │  (Intent Classifier) │                          │
 │                      └──────────┬───────────┘                          │
 │                                 │                                      │
 │               ┌─────────────────┴─────────────────┐                    │
 │               ▼                                   ▼                    │
 │  ┌─────────────────────────┐         ┌───────────────────────────────┐ │
 │  │ Governance Worker Agent │         │       BI Worker Agent         │ │
 │  │ • Schema & Stats Profiler│         │ • Semantic Text-to-SQL        │ │
 │  │ • PII / KVKK Scanner    │         │ • Query Safety Guardrail      │ │
 │  │ • Auto-Business Glossary│         │ • Root-Cause Variance Engine  │ │
 │  └─────────────────────────┘         └───────────────────────────────┘ │
 │               │                                   │                    │
 │               └─────────────────┬─────────────────┘                    │
 │                                 ▼                                      │
 │                      ┌──────────────────────┐                          │
 │                      │  Insight Synthesizer │                          │
 │                      │   (Executive Note)   │                          │
 │                      └──────────────────────┘                          │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │             MODERN LAKEHOUSE DEPOLAMA (DUCKDB COLUMNAR OLAP)           │
 │  • customers (Müşteri & PII verileri)   • transactions (Satış & Ciro)  │
 │  • products (Stok & Kategori)           • data_catalog_metadata       │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 🤖 LangGraph Multi-Agent Topolojisi ve Durum Yönetimi (State)

Ajan sistemi, paylaşılan bir `AgentState` üzerinden durumsal (stateful) olarak çalışır:

```python
class AgentState(TypedDict):
    user_query: str
    intent: str                      # "GOVERNANCE", "BI_ANALYTICS", "HYBRID"
    selected_tables: List[str]
    generated_sql: Optional[str]
    sql_valid: bool
    query_results: Optional[List[Dict[str, Any]]]
    governance_findings: Optional[Dict[str, Any]]
    chart_config: Optional[Dict[str, Any]]
    executive_summary: str
    messages: List[BaseMessage]
```

### Ajan Düğümleri (Graph Nodes):
1. **`Supervisor_Router` Node:** Kullanıcı girdisini analiz eder.
   * *"Müşteri tablosunda KVKK riski var mı?"* ──► `Governance_Worker`
   * *"Son ay kâr marjı neden düştü?"* ──► `BI_Worker`
2. **`Governance_Worker` Node:**
   * Tablo şemalarını, null oranlarını, benzersizlik (uniqueness) metriklerini çıkarır.
   * Regex ve semantik analizle TCKN, Telefon, Kredi Kartı tespit edip `PII_MASKED` durumuna alır.
   * Tablo ve kolonlar için iş açıklamaları (Business Description) üretir.
3. **`BI_Worker` Node:**
   * Veri kataloğundaki şema ve açıklamaları prompt bağlamına alır (In-Context Learning).
   * Yalnızca `SELECT` sorguları üreten katı SQL güvenlik kuralını (Safety Guardrail) uygular.
   * DuckDB üzerinde sorguyu çalıştırır. Eğer satış düşüşü varsa alt kategorilere kırarak varyans analizi (Kök Neden) yapar.
4. **`Insight_Synthesizer` Node:**
   * Sayısal çıktıyı ve grafik verilerini alır; bir üst düzey yöneticiye (C-Level) sunulacak 2-3 cümlelik net aksiyon notuna dönüştürür.

---

## 4. 🗄️ Kurumsal Sentetik Veri Seti Mimarisi (Mock Enterprise Lakehouse)

DuckDB üzerinde gerçekçi kurumsal perakende/fintech senaryosu:

1. **`customers` Tablosu:**
   * `customer_id`, `full_name` (PII), `tc_identity_no` (PII), `phone_number` (PII), `city`, `segment`, `created_at`
2. **`transactions` Tablosu:**
   * `tx_id`, `customer_id`, `product_id`, `amount`, `profit_margin`, `tx_date`, `status`
   * *Veri Kalitesi Anomalileri:* Bazı satırlarda null değerler ve eksi bakiye hataları içerir (Ajanın tespit etmesi için).
3. **`products` Tablosu:**
   * `product_id`, `category_name`, `unit_cost`, `unit_price`, `stock_qty`
4. **`data_catalog_metadata` Tablosu:**
   * Ajanın otomatik doldurduğu veri sözlüğü, kalite puanı (Health Score %0-100) ve PII uyarıları.

---

## 5. 📂 Proje Dizin Yapısı (Project Structure)

```text
C:\Users\omerc\Desktop\auragovernance/
├── README.md                      # Komtaş odaklı üst düzey sunum ve mimari dökümanı
├── PROJECT_BLUEPRINT.md           # Bu detaylı teknik planlama dosyası
├── requirements.txt               # Bağımlılıklar (langgraph, duckdb, fastapi, uvicorn vb.)
├── config.py                      # Veritabanı ve LLM yapılandırmaları
├── main.py                        # FastAPI backend sunucusu ve API rotaları
├── database/
│   ├── connection.py              # DuckDB bağlantı yöneticisi
│   └── seed_data.py               # Sentetik kurumsal göl evi verisi üreteci
├── agents/
│   ├── state.py                   # LangGraph durum tanımları
│   ├── graph.py                   # LangGraph StateGraph akış orkestrasyonu
│   ├── supervisor.py              # Niyet sınıflandırıcı ve yönlendirici
│   ├── governance_agent.py        # Damalink: Veri kalitesi, katalog ve PII motoru
│   ├── bi_agent.py                # Qlik/BI: Text-to-SQL ve Kök Neden motoru
│   └── guardrails.py              # SQL enjeksiyon ve güvenlik denetleyicisi
├── web/
│   ├── index.html                 # Modern Tailwind CSS + Chart.js dashboard
│   ├── app.js                     # Frontend API ve interaktif grafik yöneticisi
│   └── styles.css                 # Temiz kurumsal arayüz stilleri
└── tests/
    └── test_agents.py             # Ajan test senaryoları
```

---

## 6. 🚀 Adım Adım Geliştirme Yol Haritası (Implementation Roadmap)

### Faz 1: Altyapı ve Veri Tabanı (Database & Seed)
* `database/connection.py` ve `database/seed_data.py` hazırlanacak.
* DuckDB üzerinde `customers`, `transactions` ve `products` tabloları gerçekçi veri ve bilerek yerleştirilmiş PII/Kalite anomalileriyle oluşturulacak.

### Faz 2: Damalink Veri Yönetişim Ajanı (Governance Engine)
* Tablo şemalarını otomatik tarayan fonksiyon yazılacak.
* Regex ve kural tabanlı PII tarayıcı (TCKN, telefon, e-posta) kurulacak.
* Veri kalitesi kuralları (null oranı, benzersizlik, aralık kontrolleri) kodlanacak.
* Tablolar için otomatik iş açıklaması (Business Glossary) üreten LLM düğümü eklenecek.

### Faz 3: Qlik / BI Text-to-Insight Ajanı (BI Engine)
* Doğal dilden DuckDB SQL üreten Text-to-SQL motoru yazılacak.
* Sadece `SELECT` sorgularına izin veren katı SQL Guardrail güvenlik filtresi yazılacak.
* Satış/kâr anomalilerinde alt kırılımlara inen Kök Neden (Variance/Root-Cause) fonksiyonu kodlanacak.

### Faz 4: LangGraph Multi-Agent Orkestrasyonu
* `AgentState` tanımlanacak.
* `Supervisor`, `Governance_Worker`, `BI_Worker` ve `Insight_Synthesizer` düğümleri `StateGraph` üzerinde birleştirilecek.

### Faz 5: FastAPI Servisleri ve Modern Web Paneli
* REST endpoint'leri (`/api/governance/audit`, `/api/bi/query`, `/api/catalog`) kurulacak.
* Tailwind CSS ve Chart.js ile iki sekmeli harika bir kurumsal arayüz yapılacak:
  * **Sekme 1:** Damalink Yönetişim Paneli (Tablolar, PII Durumları, Kalite Skorları).
  * **Sekme 2:** Qlik BI Copilot (Doğal dille sohbet, otomatik grafikler, yönetici özeti).

### Faz 6: GitHub ve Komtaş Outreach
* GitHub reposu oluşturulup pushlanacak.
* Komtaş CTO'su Emre Yiğit ve İK ekibine yönelik nokta atışı e-posta gönderilecek.

---

## 7. 🎯 Komtaş İle Görüşürken Kullanılacak Cümle

> *"Emre Bey, kurumsal şirketlerin veri ambarlarında yaşadığı en büyük iki sorunu biliyorum: Damalink tarafında yönetişim ve PII takibinin manuel yapılması; BI/Qlik tarafında ise iş birimlerinin teknik analitik bariyeri yaşaması.*  
> *Geliştirdiğim **AuraGovernance** projesiyle bu iki dünyayı LangGraph tabanlı otonom bir mimaride birleştirdim. Sistem göl evindeki tabloları tarayarak PII ve veri kalitesi denetimini otonom yapıyor, aynı zamanda doğal dildeki soruları analiz edip kök neden açıklamalı iş zekası raporları üretiyor."*
