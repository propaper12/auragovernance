# 📨 Komtaş Ekosistemi Özel İletişim / Cold Outreach Metinleri

Bu metinler, Komtaş Yönetim Ekibine (CTO Emre Yiğit, CEO Yüksel Çomak veya Veri Liderleri) doğrudan ulaştığınızda fark yaratacak şekilde; yapay zeka kokmayan, somut çözümü ve teknik mimariyi net olarak öne çıkaran bir dille kaleme alınmıştır.

---

### Seçenek 1: LinkedIn Mesajı (Doğrudan & Net - Önerilen)

**Kime:** Emre Yiğit (CTO, Komtaş Ekosistemi) veya Ekip Liderleri  
**Konu/Başlık:** Komtaş Ekosistemi (Damalink & Qlik) İçin Geliştirdiğim Otonom Yönetişim & BI Ajanı (AuraGovernance)

Merhaba Emre Bey,

Komtaş Ekosistemi’nin Türkiye veri pazarında özellikle **Damalink** (veri yönetişimi/katalog) ve **BI Technology** (Qlik/analitik) dikeyindeki öncü projelerini ilgiyle takip ediyorum.

Genel bir başvuru yapmak yerine; ekosisteminizin çözdüğü iki temel operasyonel darboğaza doğrudan odaklanan uçtan uca çalışan bir mimari prototip geliştirdim: **AuraGovernance**.

Projeyi özetle şu yetkinlikler üzerine kurguladım:
1. **Damalink Sinerjisi (Yönetişim & KVKK):** Lakehouse üzerinde otonom şema profillemesi yapıyor; TCKN, telefon ve e-posta gibi kişisel verileri regex/sezgisel analizle tespit edip otomatik maskeleme öneriyor. Kritik null oranlarını ve negatif stok gibi anomalileri algılayıp tablo bazlı sağlık skoru (%0-100) üretiyor.
2. **BI Technology Sinerjisi (Text-to-SQL & Kök Neden):** İş birimlerinin doğal dilde sorduğu soruları salt-okunur (guardrails korumalı) SQL'e dönüştürüyor, anında Chart.js görselleştirmesi sunuyor ve varyansın arkasındaki kök nedeni (örn. son 60 gündeki tedarik maliyeti artışının kâr marjına etkisi) C-Level yönetici özeti olarak sentezliyor.
3. **Mimarisi:** In-memory columnar **DuckDB** ve **LangGraph** çoklu ajan orkestrasyonu (Supervisor -> Governance Worker -> BI Worker -> Synthesizer) ile FastAPI + Tailwind tabanlı interaktif bir stüdyo olarak çalışıyor.

YBS 2026 mezuniyetim öncesinde, Komtaş bünyesindeki Veri Yönetişimi veya AI/Veri Mühendisliği ekiplerinizde bu değer odaklı vizyonla katma değer sağlamak isterim. 

GitHub repom ve canlı demom üzerinden 10-15 dakikalık kısa bir tanışma toplantısında projeyi size sunmaktan memnuniyet duyarım:
🔗 GitHub: [github.com/omercakan/auragovernance]
🔗 LinkedIn: linkedin.com/in/ömer-çakan-819751261

İyi çalışmalar dilerim,  
**Ömer Çakan**  
0553 177 60 89 | omercakan.ybs@gmail.com

---

### Seçenek 2: E-Posta Formatı (Detaylı & Kurumsal)

**Kime:** emre.yigit@komtas.com / ik@komtas.com / kariyer@komtas.com  
**Konu:** Komtaş Veri Ekosistemi (Damalink & BI Technology) İçin Çözüm Projem & İş Başvurusu - Ömer Çakan

Sayın Emre Bey ve Değerli Komtaş Ekibi,

Veri ekosisteminde kurumsal göller büyüdükçe iki kritik ihtiyaç öne çıkıyor: Birincisi verinin güvenliği ve regülasyon uyumu (Damalink), ikincisi ise karar vericilerin verilere self-service ulaşıp sapmaların kök nedenini hızlıca analiz edebilmesi (BI Technology / Qlik).

Bu iki ihtiyacı tek bir otonom ajan mimarisinde birleştiren **AuraGovernance** projesini geliştirdim. 

**Projede hayata geçirdiğim somut çözümler:**
- **Damalink Otonom Katalog ve KVKK Kalkanı:** DuckDB Lakehouse üzerinde tabloları otomatik tarayarak TCKN, GSM ve E-posta alanlarını sınıflandırıyor, maskeleme desenleri uyguluyor ve veri kalitesi anomalilerini (negatif envanter, eşik aşımı yapan null değerler) yakalayıp dinamik İş Sözlüğü (Business Glossary) üretiyor.
- **Qlik Self-Service & Kök Neden Motoru:** Kullanıcının doğal dil sorularını (örn: "Marmara bölgesinde kâr neden düştü?") semantik olarak çözümlüyor. Read-only SQL Guardrails ile sistem güvenliğini sağlayarak çalıştırıyor, uygun grafiği (Bar/Doughnut) render ediyor ve marj düşüşünün tedarik maliyetlerindeki %28'lik artıştan kaynaklandığını tespit eden C-Level yönetici raporu sunuyor.
- **LangGraph Çoklu Ajan Topolojisi:** Supervisor yönlendiricisi gelen isteğe göre Governance Worker, BI Worker ve Insight Synthesizer ajanlarını koordine ediyor.

Bu projeyi geliştirirken amacım yalnızca teknik yetkinliğimi değil, Komtaş'ın müşterilerine sunduğu ürün portföyünü ve iş modelini ne kadar iyi anladığımı göstermekti.

Projemi ekte ve GitHub üzerinden incelemenize sunuyor; Veri Mühendisliği, AI Çözümleri veya Veri Yönetişimi ekiplerinizde görev alarak bu değeri kurumsal ölçeğe taşımak istiyorum. Uygun göreceğiniz kısa bir online görüşmede projeyi canlı olarak paylaşmayı çok isterim.

Saygılarımla,

**Ömer Çakan**  
*YBS 2026 Mezunu | Data & AI Engineer*  
Tel: 0553 177 60 89  
LinkedIn: linkedin.com/in/ömer-çakan-819751261  
GitHub: github.com/omercakan/auragovernance
