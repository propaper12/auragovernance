import random
from datetime import datetime, timedelta
from database.connection import get_db_connection

def seed_enterprise_lakehouse(num_customers: int = 250, num_transactions: int = 1500):
    """
    Komtaş Veri Yönetişimi (Damalink) ve İş Zekası (Qlik/BI) senaryolarını test etmek üzere
    gerçekçi kurumsal veri, PII (Kişisel Veri) ve planlı veri kalitesi anomalileri üretir.
    """
    con = get_db_connection()
    print(">>> [Seed Engine] DuckDB Lakehouse tabloları temizleniyor ve oluşturuluyor...")

    # 1. Tabloları oluştur
    con.execute("DROP TABLE IF EXISTS transactions;")
    con.execute("DROP TABLE IF EXISTS customers;")
    con.execute("DROP TABLE IF EXISTS products;")
    con.execute("DROP TABLE IF EXISTS data_catalog_metadata;")

    con.execute("""
        CREATE TABLE customers (
            customer_id VARCHAR PRIMARY KEY,
            full_name VARCHAR,
            tc_identity_no VARCHAR,
            phone_number VARCHAR,
            email VARCHAR,
            city VARCHAR,
            segment VARCHAR,
            account_balance DOUBLE,
            created_at TIMESTAMP
        );
    """)

    con.execute("""
        CREATE TABLE products (
            product_id VARCHAR PRIMARY KEY,
            product_name VARCHAR,
            category_name VARCHAR,
            unit_cost DOUBLE,
            unit_price DOUBLE,
            stock_quantity INTEGER
        );
    """)

    con.execute("""
        CREATE TABLE transactions (
            transaction_id VARCHAR PRIMARY KEY,
            customer_id VARCHAR,
            product_id VARCHAR,
            quantity INTEGER,
            total_amount DOUBLE,
            profit_amount DOUBLE,
            discount_pct DOUBLE,
            payment_method VARCHAR,
            region VARCHAR,
            transaction_date TIMESTAMP
        );
    """)

    con.execute("""
        CREATE TABLE data_catalog_metadata (
            audit_id VARCHAR PRIMARY KEY,
            table_name VARCHAR,
            total_rows INTEGER,
            column_count INTEGER,
            overall_health_score DOUBLE,
            pii_columns_detected VARCHAR[],
            quality_issues_detected VARCHAR[],
            business_description VARCHAR,
            audited_at TIMESTAMP
        );
    """)

    print(">>> [Seed Engine] 1. 'products' tablosu dolduruluyor (Kategoriler & Fiyatlar)...")
    categories = {
        "Elektronik": [
            ("Dizüstü Bilgisayar Pro", 22000.0, 28500.0),
            ("Akıllı Telefon X12", 18000.0, 23500.0),
            ("Gürültü Önleyici Kulaklık", 2400.0, 3600.0),
            ("4K Ultra Akıllı TV", 16500.0, 21000.0),
            ("Mekanik Oyuncu Klavyesi", 1100.0, 1850.0)
        ],
        "Ev & Yaşam": [
            ("Robot Süpürge SmartV", 8500.0, 12000.0),
            ("Otomatik Kahve Makinesi", 4500.0, 6800.0),
            ("Hava Temizleyici Pro", 3200.0, 4900.0),
            ("Ergonomik Çalışma Koltuğu", 2800.0, 4200.0)
        ],
        "Moda & Giyim": [
            ("Su Geçirmez Outdoor Mont", 1400.0, 2600.0),
            ("Deri Evrak Çantası", 950.0, 1950.0),
            ("Koşu Ayakkabısı AirTrack", 1200.0, 2400.0)
        ],
        "Kozmetik & Bakım": [
            ("Anti-Aging Bakım Serumu", 450.0, 950.0),
            ("Sonik Diş Fırçası Seti", 750.0, 1450.0)
        ]
    }

    product_ids = []
    p_counter = 101
    for cat, prod_list in categories.items():
        for p_name, cost, price in prod_list:
            pid = f"PRD-{p_counter}"
            product_ids.append((pid, cat, cost, price))
            stock = random.randint(15, 120)
            con.execute("""
                INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)
            """, [pid, p_name, cat, cost, price, stock])
            p_counter += 1

    # Planlı Veri Kalitesi Hatası: 1 üründe negatif stok anomalisi (Ajanın yakalaması için)
    con.execute("""
        INSERT INTO products VALUES ('PRD-999', 'Hatalı Stoklu Test Ürünü', 'Elektronik', 1500.0, 2200.0, -14)
    """)
    product_ids.append(('PRD-999', 'Elektronik', 1500.0, 2200.0))

    print(">>> [Seed Engine] 2. 'customers' tablosu dolduruluyor (KVKK / PII Alanları ile)...")
    first_names = ["Ahmet", "Mehmet", "Ayşe", "Fatma", "Mustafa", "Zeynep", "Emre", "Büşra", "Can", "Elif", "Burak", "Selin"]
    last_names = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Öztürk", "Aydın", "Özdemir", "Arslan", "Doğan", "Koç"]
    cities = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Kocaeli", "Adana"]
    segments = ["Bireysel", "Premium", "Kurumsal", "Yeni"]

    customer_ids = []
    for i in range(1, num_customers + 1):
        cid = f"CUST-{i:04d}"
        customer_ids.append(cid)
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        full_name = f"{fn} {ln}"
        
        # Gerçekçi 11 haneli TCKN simülasyonu
        tckn = f"{random.randint(100000000, 999999999)}{random.randint(10, 99)}"
        phone = f"+90 5{random.randint(30, 59)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
        email = f"{fn.lower()}.{ln.lower()}{random.randint(1, 999)}@example.com"
        city = random.choice(cities)
        seg = random.choice(segments)
        balance = round(random.uniform(250.0, 45000.0), 2)
        days_ago = random.randint(10, 400)
        c_date = datetime.now() - timedelta(days=days_ago)

        # Planlı Veri Kalitesi Hatası: %8 oranında null telefon ve e-posta (Damalink'in yakalaması için)
        if random.random() < 0.08:
            phone = None
        if random.random() < 0.05:
            email = None

        con.execute("""
            INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [cid, full_name, tckn, phone, email, city, seg, balance, c_date])

    print(">>> [Seed Engine] 3. 'transactions' tablosu dolduruluyor (Kök Neden Anomalisi ile)...")
    regions = ["Marmara", "İç Anadolu", "Ege", "Akdeniz", "Karadeniz"]
    methods = ["Kredi Kartı", "Havale / EFT", "Banka Kartı", "Dijital Cüzdan"]

    # Trend Kurgusu: 2026 Ağustos ve Eylül aylarında Marmara bölgesinde Elektronik ürünlerinde
    # kâr marjı tedarik maliyet artışı yüzünden belirgin şekilde düşürülecek (Kök Neden Analizi için).
    for i in range(1, num_transactions + 1):
        tx_id = f"TX-{10000 + i}"
        cid = random.choice(customer_ids)
        pid, pcat, pcost, pprice = random.choice(product_ids)
        qty = random.choices([1, 2, 3, 4], weights=[0.65, 0.22, 0.09, 0.04])[0]
        region = random.choice(regions)
        method = random.choice(methods)
        discount = round(random.choice([0.0, 0.05, 0.10, 0.15]), 2)

        # Son 180 gün içine rastgele tarih dağıtımı
        tx_days = random.randint(0, 180)
        tx_date = datetime.now() - timedelta(days=tx_days)

        unit_sell_price = pprice * (1.0 - discount)
        total_amount = round(unit_sell_price * qty, 2)

        # KÖK NEDEN SENARYOSU (Root-Cause):
        # Eğer tarih son 60 gün içindeyse (Ağustos-Eylül) ve bölge Marmara ve kategori Elektronik ise
        # tedarik maliyeti arttığı için kâr marjı çöker!
        actual_cost = pcost
        if tx_days < 60 and region == "Marmara" and pcat == "Elektronik":
            actual_cost = pcost * 1.28  # %28 hammadde/tedarik maliyeti artışı

        profit = round((unit_sell_price - actual_cost) * qty, 2)

        con.execute("""
            INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [tx_id, cid, pid, qty, total_amount, profit, discount, method, region, tx_date])

    con.close()
    print(">>> [Seed Engine] [SUCCESS] DuckDB Lakehouse basariyla olusturuldu:")
    print(f"    * customers: {num_customers} satir (PII ve null anomalileri eklendi)")
    print(f"    * products: {p_counter - 100} urun (Negatif stok hatasi eklendi)")
    print(f"    * transactions: {num_transactions} islem (Marmara/Elektronik kar dusus anomalisi kurgulandi)")

if __name__ == "__main__":
    seed_enterprise_lakehouse()
