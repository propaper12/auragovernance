# 🌐 AuraGovernance
### Autonomous Lakehouse Data Catalog, Quality Governance & Self-Service BI Agent

> **Komtaş Veri ve Analitik Ekosistemi (Damalink & BI Technology / Qlik Synergy) İçin Özel Olarak Geliştirilmiş Uçtan Uca Otonom Ajan Mimarisi**

---

## 📌 Proje Vizyonu ve Çıkış Noktası

Büyük kurumsal veri ekosistemlerinde iki kritik darboğaz sıklıkla yaşanır:
1. **Veri Yönetişimi & KVKK Uyumu (Damalink):** Kurumsal göllerde (Lakehouse) biriken verilerde hassas kişisel verilerin (TCKN, GSM, E-posta) otomatik tespiti, maskelenmesi ve veri kalitesi anomalilerinin (negatif stoklar, kritik null oranları) erken uyarısı manuel olarak sürdürülemez.
2. **Self-Service İş Zekası & Kök Neden Analizi (Qlik / BI Technology):** Karar vericilerin doğal dilde sorduğu "Satışlar neden düştü?" veya "En karlı ürünler nelerdir?" sorularını güvenli (read-only guardrails) SQL sorgularına dönüştürmek, anında grafiklerle görselleştirmek ve varyansın derinindeki kök nedeni saptamak zaman alır.

**AuraGovernance**, bu iki dünyayı **LangGraph** çoklu ajan mimarisi ve yüksek performanslı **DuckDB Columnar Lakehouse** motoru üzerinde birleştirerek otonom bir çözüm sunar.

---

## 🏛️ Komtaş Ekosistem Eşleşmesi (Ecosystem Synergy)

```
                            ┌──────────────────────────────────────────────┐
                            │      Komtaş Veri ve Analitik Ekosistemi      │
                            └──────────────────────┬───────────────────────┘
                                                   │
                ┌──────────────────────────────────┴──────────────────────────────────┐
                ▼                                                                     ▼
    ┌───────────────────────┐                                             ┌───────────────────────┐
    │       DAMALİNK        │                                             │     BI TECHNOLOGY     │
    │   (Veri Yönetişimi)   │                                             │    (Qlik & Analitik)  │
    └───────────┬───────────┘                                             └───────────┬───────────┘
                │                                                                     │
                ▼                                                                     ▼
     • Otonom Şema Taraması                                                • Doğal Dil ile Text-to-SQL
     • Regex & KVKK (PII) Tespiti                                          • Kök Neden (Root-Cause) Analizi
     • Otomatik Veri Kalitesi Skoru                                        • Chart.js Görselleştirme
     • Dinamik İş Sözlüğü (Glossary)                                       • Salt-Okunur SQL Guardrails
                │                                                                     │
                └──────────────────────────────┬──────────────────────────────────────┘
                                               ▼
                              ┌──────────────────────────────────┐
                              │      DuckDB Columnar Lakehouse   │
                              │   (Analythinx / Starburst Uyumu) │
                              └──────────────────────────────────┘
```

---

## 🚀 Temel Özellikler

### 1. Damalink Synergy: Veri Yönetişim & Kataloglama Studio
- **Otonom Şema & Profil Çıkarma:** Lakehouse tablolarını tarayarak satır sayıları, null yüzdeleri, tekillik ve birincil anahtar adaylıklarını hesaplar.
- **KVKK / PII Algılama & Maskeleme:** Türkiye regülasyonlarına uygun olarak TCKN (11 hane), GSM (`+90 5xx`), e-posta formatlarını algılar ve `123*****89`, `+90 532 *** ** 12` şeklinde maskeleme stratejisi sunar.
- **Veri Kalitesi Skorlama:** Eşik değerleri aşan tabloları puanlar (0-100%); negatif stok anomalilerini (Örn: `PRD-999`) ve kabul edilemez null oranlarını anında bayraklar.
- **Otomatik İş Sözlüğü (Business Glossary):** Tablo ve kolonlar için iş tanımları, veri sorumluları ve gizlilik sınıflandırmaları üretir.

### 2. Qlik Synergy: Self-Service BI & Kök Neden Analitiği
- **Semantik Text-to-SQL:** Doğal dilde sorulan Türkçe analitik soruları DuckDB uyumlu SQL sorgularına dönüştürür.
- **SQL Güvenlik Kalkanı (Guardrails):** Yalnızca `SELECT` sorgularına izin verir; `DROP`, `DELETE`, `UPDATE`, `INSERT` gibi komutları engeller ve DoS saldırılarını önlemek için güvenli `LIMIT` enjekte eder.
- **Kök Neden & Varyans Motoru:** Örneğin "Marmara bölgesinde kâr neden düştü?" sorusunda Marmara bölgesindeki Elektronik kategorisinde son 60 günde tedarik maliyetlerindeki %28'lik artışı otomatik tespit eder ve C-Level aksiyon önerileri üretir.
- **Dinamik Chart.js Konfigürasyonu:** Sorgu yapısına göre Bar, Doughnut veya Line grafiklerini otomatik olarak derler.

### 3. LangGraph Çoklu Ajan Mimarisi
- **Supervisor Router:** Kullanıcı niyetini `GOVERNANCE`, `BI_ANALYTICS` veya `HYBRID` olarak sınıflandırır.
- **Governance Worker:** Damalink denetimini koşturur.
- **BI Worker:** Qlik analitik motorunu koşturur.
- **Insight Synthesizer:** Bulguları tek bir yönetici raporunda sentezler.

---

## 📂 Proje Dizin Yapısı

```
auragovernance/
├── agents/
│   ├── __init__.py
│   ├── governance_engine.py    # Damalink şema, PII ve kalite analizörü
│   ├── bi_engine.py            # Qlik Text-to-SQL, Chart.js & kök neden motoru
│   ├── guardrails.py           # SQL güvenlik ve read-only kalkanı
│   ├── state.py                # LangGraph State modeli
│   ├── supervisor.py           # Akıllı niyet yönlendiricisi
│   └── graph.py                # LangGraph çoklu ajan akış şeması
├── database/
│   ├── __init__.py
│   ├── connection.py           # DuckDB bağlantı yöneticisi
│   └── seed_data.py            # Kurumsal lakehouse veri üreticisi
├── web/
│   └── index.html              # Tailwind CSS & Chart.js tabanlı çift panelli arayüz
├── tests/
│   └── test_pipeline.py        # Kapsamlı birim test paketi
├── config.py                   # PII regex desenleri ve yönetişim eşikleri
├── main.py                     # FastAPI REST API & statik sunucu
├── run.py                      # Tek komutla başlatma scripti
├── requirements.txt            # Python bağımlılıkları
├── PROJECT_BLUEPRINT.md        # Mimari plan ve Komtaş eşleşme dokümanı
└── README.md                   # Proje dokümantasyonu
```

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 2. Lakehouse Veri Ambarını Oluşturun (Seed Data)
```bash
python -m database.seed_data
```
*Bu komut DuckDB üzerinde 250 müşteri, 15 ürün ve 1.500 işlem kaydını oluşturur; PII verilerini ve planlı kök neden anomalilerini enjekte eder.*

### 3. Uygulamayı Başlatın
```bash
python run.py
```
*AuraGovernance arayüzü `http://127.0.0.1:8001` adresinde yayına başlar.*

### 4. Testleri Koşun
```bash
python -m unittest tests/test_pipeline.py
```

---

## 🧪 Örnek Analitik ve Yönetişim Senaryoları

| Kullanıcı Sorgusu | Tetiklenen Ajan | Çıktı / İçgörü |
|---|---|---|
| *"KVKK ve veri yönetişim durumu nedir?"* | Damalink Governance Worker | 3 tabloda 25 kolon tarandı; TCKN, telefon ve e-posta alanlarında KVKK uyarısı ve maskeleme önerisi. |
| *"Marmara bölgesinde kâr neden düştü? Kök neden analizi yap"* | Hybrid (Damalink + Qlik BI) | Marmara / Elektronik kategorisinde son 60 gündeki tedarik maliyeti artışı (%28) ve düşen marj varyansı tespiti. |
| *"En çok ciro getiren ilk 5 ürün hangisi?"* | Qlik BI Worker | DuckDB üzerinden anlık aggregasyon, interaktif Bar Chart ve ürün sıralaması. |
| *"Bölgelere göre satış ve kâr dağılımı"* | Qlik BI Worker | Ciro ve kâr marjının coğrafi kırılımı + Chart.js görselleştirmesi. |
| *"DROP TABLE customers;"* | SQL Guardrails | **BLOCKED:** `Güvenlik İhlali: Yalnızca salt-okunur 'SELECT' sorgularına izin verilir.` |

---

## 👨‍💻 Geliştirici

**Ömer Çakan**  
*Yönetim Bilişim Sistemleri (YBS / MIS) 2026 Mezunu*  
*Data & AI Engineer*  
- **LinkedIn:** [linkedin.com/in/ömer-çakan-819751261](https://www.linkedin.com/in/ömer-çakan-819751261)  
- **Teknoloji Odağı:** Modern Lakehouse Mimarileri (DuckDB, Starburst), LLM & Multi-Agent Sistemler (LangGraph, Guardrails), Veri Yönetişimi (Metadata, KVKK/PII) & Self-Service BI (Qlik).
