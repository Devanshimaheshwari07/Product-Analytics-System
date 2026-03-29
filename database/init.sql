-- ============================================================
-- Product Analytics Database Schema & Seed Data
-- ============================================================

-- ─── EXTENSIONS ──────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── TABLES ──────────────────────────────────────────────────

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(100) NOT NULL,
    timezone VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    price NUMERIC(10,2) NOT NULL,
    cost NUMERIC(10,2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    launch_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sales_transactions (
    id SERIAL PRIMARY KEY,
    transaction_id UUID DEFAULT uuid_generate_v4(),
    product_id INTEGER REFERENCES products(id),
    region_id INTEGER REFERENCES regions(id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    discount_pct NUMERIC(5,2) DEFAULT 0,
    total_amount NUMERIC(12,2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    channel VARCHAR(50) DEFAULT 'online',
    customer_segment VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE daily_product_metrics (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    region_id INTEGER REFERENCES regions(id),
    metric_date DATE NOT NULL,
    total_revenue NUMERIC(14,2) DEFAULT 0,
    total_units_sold INTEGER DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    avg_order_value NUMERIC(10,2) DEFAULT 0,
    avg_discount_pct NUMERIC(5,2) DEFAULT 0,
    gross_profit NUMERIC(14,2) DEFAULT 0,
    profit_margin NUMERIC(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(product_id, region_id, metric_date)
);

CREATE TABLE kpi_summary (
    id SERIAL PRIMARY KEY,
    kpi_name VARCHAR(100) NOT NULL,
    kpi_value NUMERIC(16,4),
    kpi_unit VARCHAR(20),
    period_type VARCHAR(20) NOT NULL,         -- daily, weekly, monthly, yearly
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    dimension_type VARCHAR(50),               -- category, region, product, overall
    dimension_value VARCHAR(100),
    previous_value NUMERIC(16,4),
    change_pct NUMERIC(8,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(kpi_name, period_type, period_start, dimension_type, dimension_value)
);

-- ─── INDEXES ─────────────────────────────────────────────────

CREATE INDEX idx_sales_product ON sales_transactions(product_id);
CREATE INDEX idx_sales_region ON sales_transactions(region_id);
CREATE INDEX idx_sales_date ON sales_transactions(transaction_date);
CREATE INDEX idx_sales_channel ON sales_transactions(channel);
CREATE INDEX idx_metrics_date ON daily_product_metrics(metric_date);
CREATE INDEX idx_metrics_product ON daily_product_metrics(product_id);
CREATE INDEX idx_kpi_period ON kpi_summary(period_type, period_start);
CREATE INDEX idx_kpi_name ON kpi_summary(kpi_name);

-- ─── SEED: CATEGORIES ────────────────────────────────────────

INSERT INTO categories (name, description) VALUES
('Electronics',      'Consumer electronic devices and accessories'),
('Clothing',         'Apparel, footwear, and fashion accessories'),
('Home & Kitchen',   'Home appliances, cookware, and decor'),
('Sports & Outdoors','Sporting goods and outdoor recreation equipment'),
('Books & Media',    'Books, e-books, audiobooks, and digital media'),
('Health & Beauty',  'Personal care, cosmetics, and health products'),
('Toys & Games',     'Toys, board games, and gaming accessories'),
('Food & Beverages', 'Packaged food, snacks, and beverages');

-- ─── SEED: REGIONS ───────────────────────────────────────────

INSERT INTO regions (name, country, timezone) VALUES
('North America',  'United States', 'America/New_York'),
('Europe West',    'United Kingdom', 'Europe/London'),
('Europe Central', 'Germany',        'Europe/Berlin'),
('Asia Pacific',   'Japan',          'Asia/Tokyo'),
('South Asia',     'India',          'Asia/Kolkata');

-- ─── SEED: PRODUCTS (56 products) ────────────────────────────

INSERT INTO products (sku, name, category_id, price, cost, stock_quantity, launch_date, description) VALUES
-- Electronics (cat 1)
('ELC-001', 'ProMax Wireless Earbuds',       1, 79.99,  32.00, 1200, '2025-01-15', 'Noise-canceling TWS earbuds with 36h battery'),
('ELC-002', 'UltraSlim 15" Laptop',          1, 1299.99, 780.00, 340, '2025-02-01', '15-inch laptop, 16GB RAM, 512GB SSD'),
('ELC-003', '4K Action Camera',              1, 249.99, 110.00, 650, '2025-03-10', 'Waterproof 4K action camera with stabilization'),
('ELC-004', 'SmartHome Hub Pro',             1, 149.99,  65.00, 890, '2025-01-20', 'Voice-controlled smart home central hub'),
('ELC-005', 'PowerBank 20000mAh',            1, 39.99,  14.00, 2100, '2025-04-01', 'Fast-charge portable power bank'),
('ELC-006', 'Curved Gaming Monitor 32"',     1, 449.99, 220.00, 420, '2025-02-15', '32-inch QHD 165Hz curved gaming monitor'),
('ELC-007', 'Mechanical Gaming Keyboard',    1, 129.99,  52.00, 780, '2025-05-01', 'RGB mechanical keyboard with hot-swap switches'),
-- Clothing (cat 2)
('CLT-001', 'Performance Running Shoes',     2, 119.99,  42.00, 950, '2025-01-10', 'Lightweight carbon-plate running shoes'),
('CLT-002', 'Premium Denim Jacket',          2, 89.99,  35.00, 600, '2025-03-01', 'Slim-fit stretch denim jacket'),
('CLT-003', 'Merino Wool Sweater',           2, 69.99,  28.00, 750, '2025-02-20', 'Fine-knit merino wool crew neck sweater'),
('CLT-004', 'Quick-Dry Hiking Pants',        2, 59.99,  22.00, 880, '2025-04-15', 'Waterproof quick-dry convertible hiking pants'),
('CLT-005', 'Urban Backpack 30L',            2, 49.99,  18.00, 1100, '2025-01-25', 'Water-resistant urban commuter backpack'),
('CLT-006', 'Compression Sports Tights',     2, 44.99,  16.00, 1300, '2025-05-10', 'High-waist compression leggings with pockets'),
('CLT-007', 'Polarized Sunglasses',          2, 34.99,  11.00, 1600, '2025-03-20', 'UV400 polarized sport sunglasses'),
-- Home & Kitchen (cat 3)
('HMK-001', 'Smart Air Purifier',            3, 199.99,  85.00, 520, '2025-01-05', 'HEPA air purifier with app control'),
('HMK-002', 'Espresso Machine Pro',          3, 349.99, 160.00, 310, '2025-02-10', 'Dual-boiler espresso machine with grinder'),
('HMK-003', 'Robot Vacuum X1',              3, 299.99, 130.00, 440, '2025-03-15', 'LiDAR navigation robot vacuum and mop'),
('HMK-004', 'Cast Iron Dutch Oven 6Qt',     3, 79.99,  30.00, 680, '2025-01-30', 'Enameled cast iron dutch oven'),
('HMK-005', 'Smart LED Bulb Pack (4)',       3, 29.99,  10.00, 2200, '2025-04-20', 'WiFi RGBW smart bulbs, pack of 4'),
('HMK-006', 'Memory Foam Pillow Set',       3, 54.99,  19.00, 900, '2025-02-25', 'Cooling gel memory foam pillows, set of 2'),
('HMK-007', 'Stainless Steel Knife Set',    3, 129.99,  48.00, 550, '2025-05-05', '15-piece professional knife block set'),
-- Sports & Outdoors (cat 4)
('SPT-001', 'Carbon Fiber Tennis Racket',    4, 179.99,  72.00, 380, '2025-01-12', 'Tournament-grade carbon fiber racket'),
('SPT-002', 'Yoga Mat Premium 6mm',          4, 39.99,  12.00, 1400, '2025-03-05', 'Non-slip TPE yoga mat with alignment lines'),
('SPT-003', 'Adjustable Dumbbell Set',       4, 299.99, 130.00, 290, '2025-02-18', 'Adjustable dumbbells 5-52.5 lbs each'),
('SPT-004', 'Hiking Tent 2-Person',          4, 189.99,  78.00, 340, '2025-04-10', 'Ultralight 3-season backpacking tent'),
('SPT-005', 'GPS Sports Watch',              4, 249.99, 100.00, 560, '2025-01-28', 'Multi-sport GPS watch with heart rate'),
('SPT-006', 'Resistance Band Set',           4, 24.99,   8.00, 1800, '2025-05-15', '5-level resistance band set with handles'),
('SPT-007', 'Insulated Water Bottle 32oz',   4, 34.99,  11.00, 1500, '2025-03-22', 'Vacuum insulated stainless steel bottle'),
-- Books & Media (cat 5)
('BKM-001', 'Data Science Handbook',         5, 49.99,  15.00, 800, '2025-01-08', 'Comprehensive guide to modern data science'),
('BKM-002', 'Wireless Noise-Cancel Headphones', 5, 199.99, 82.00, 470, '2025-02-22', 'Over-ear ANC headphones with 40h battery'),
('BKM-003', 'E-Reader Pro 7"',              5, 139.99,  58.00, 620, '2025-03-28', '7-inch e-ink reader with warm light'),
('BKM-004', 'Coding Bootcamp Course',        5, 29.99,   5.00, 9999, '2025-04-05', 'Online full-stack development course'),
('BKM-005', 'Productivity Planner 2026',     5, 19.99,   6.00, 2500, '2025-01-02', 'Goal-setting daily/weekly productivity planner'),
('BKM-006', 'Photography Masterclass',       5, 39.99,   8.00, 9999, '2025-05-20', 'Online photography and editing course'),
('BKM-007', 'Business Strategy Audiobook',   5, 14.99,   3.00, 9999, '2025-02-14', '12-hour audiobook on competitive strategy'),
-- Health & Beauty (cat 6)
('HLB-001', 'Organic Face Serum',            6, 44.99,  12.00, 1100, '2025-01-18', 'Vitamin C + Hyaluronic acid face serum'),
('HLB-002', 'Electric Toothbrush Pro',       6, 79.99,  28.00, 750, '2025-03-12', 'Sonic toothbrush with 5 modes and timer'),
('HLB-003', 'Aromatherapy Diffuser',         6, 34.99,  13.00, 960, '2025-02-08', 'Ultrasonic essential oil diffuser 300ml'),
('HLB-004', 'Collagen Supplement 60ct',      6, 29.99,   9.00, 1400, '2025-04-25', 'Marine collagen peptides capsules'),
('HLB-005', 'Hair Dryer Ionic Pro',          6, 59.99,  22.00, 680, '2025-01-22', 'Professional ionic hair dryer 1875W'),
('HLB-006', 'SPF 50 Sunscreen Lotion',       6, 18.99,   5.00, 2000, '2025-05-01', 'Broad spectrum SPF 50 face sunscreen'),
('HLB-007', 'Digital Body Scale',            6, 39.99,  14.00, 850, '2025-03-18', 'Smart scale with body composition analysis'),
-- Toys & Games (cat 7)
('TOY-001', 'Building Block Set 1000pc',     7, 49.99,  16.00, 700, '2025-01-14', 'Compatible brick set with 1000 pieces'),
('TOY-002', 'RC Racing Drone',              7, 89.99,  35.00, 450, '2025-02-28', 'FPV racing drone with HD camera'),
('TOY-003', 'Strategy Board Game',           7, 39.99,  14.00, 900, '2025-03-08', 'Award-winning strategy board game for 2-6 players'),
('TOY-004', 'STEM Robot Kit',               7, 69.99,  25.00, 550, '2025-04-18', 'Programmable robot kit for ages 8+'),
('TOY-005', 'Wireless Game Controller',      7, 54.99,  20.00, 1000, '2025-01-30', 'Multi-platform wireless game controller'),
('TOY-006', 'Puzzle Set 3-in-1',            7, 24.99,   8.00, 1200, '2025-05-12', '3D wooden puzzle set, 3 designs'),
('TOY-007', 'Card Game Collection',          7, 19.99,   6.00, 1500, '2025-02-16', 'Classic card game collection box'),
-- Food & Beverages (cat 8)
('FNB-001', 'Organic Coffee Beans 1kg',      8, 24.99,   9.00, 1800, '2025-01-06', 'Single-origin arabica whole bean coffee'),
('FNB-002', 'Protein Bar Variety 12-pack',   8, 29.99,  11.00, 1400, '2025-03-02', 'Mixed flavor protein bars, 20g protein each'),
('FNB-003', 'Premium Green Tea 100 bags',    8, 14.99,   4.00, 2200, '2025-02-12', 'Organic Japanese green tea sachets'),
('FNB-004', 'Mixed Nuts Gift Tin 1kg',       8, 34.99,  14.00, 800, '2025-04-08', 'Premium roasted mixed nuts assortment'),
('FNB-005', 'Artisan Hot Sauce Set',         8, 19.99,   7.00, 1100, '2025-01-24', '3-bottle craft hot sauce collection'),
('FNB-006', 'Sparkling Water 24-pack',       8, 18.99,   8.00, 2500, '2025-05-08', 'Natural sparkling mineral water cans'),
('FNB-007', 'Dark Chocolate Box 500g',       8, 22.99,   8.00, 1000, '2025-03-14', '70% cacao Belgian dark chocolate assortment');

-- ─── SEED: SALES TRANSACTIONS (~12,000 rows) ────────────────
-- Generate realistic sales data for the past 12 months using a procedural approach

DO $$
DECLARE
    v_product_id   INTEGER;
    v_region_id    INTEGER;
    v_price        NUMERIC(10,2);
    v_cost         NUMERIC(10,2);
    v_quantity     INTEGER;
    v_discount     NUMERIC(5,2);
    v_total        NUMERIC(12,2);
    v_date         TIMESTAMP;
    v_channel      VARCHAR(50);
    v_segment      VARCHAR(50);
    v_channels     TEXT[] := ARRAY['online','retail','wholesale','marketplace'];
    v_segments     TEXT[] := ARRAY['consumer','business','premium','student'];
    v_day_offset   INTEGER;
    v_hour         INTEGER;
    i              INTEGER;
BEGIN
    FOR v_day_offset IN 0..364 LOOP
        -- Generate 25-45 transactions per day
        FOR i IN 1..(25 + floor(random() * 20)::int) LOOP
            v_product_id := 1 + floor(random() * 56)::int;
            v_region_id  := 1 + floor(random() * 5)::int;
            v_hour       := 6 + floor(random() * 16)::int;

            SELECT price, cost INTO v_price, v_cost
            FROM products WHERE id = v_product_id;

            v_quantity := 1 + floor(random() * 5)::int;
            v_discount := CASE
                WHEN random() < 0.3 THEN round((5 + random() * 20)::numeric, 2)
                ELSE 0
            END;
            v_total := round(v_price * v_quantity * (1 - v_discount / 100), 2);
            v_date  := (CURRENT_DATE - v_day_offset * INTERVAL '1 day')
                        + v_hour * INTERVAL '1 hour'
                        + floor(random() * 60)::int * INTERVAL '1 minute';
            v_channel := v_channels[1 + floor(random() * 4)::int];
            v_segment := v_segments[1 + floor(random() * 4)::int];

            INSERT INTO sales_transactions
                (product_id, region_id, quantity, unit_price, discount_pct,
                 total_amount, transaction_date, channel, customer_segment)
            VALUES
                (v_product_id, v_region_id, v_quantity, v_price, v_discount,
                 v_total, v_date, v_channel, v_segment);
        END LOOP;
    END LOOP;
END $$;

-- ─── PRE-COMPUTE: DAILY PRODUCT METRICS ──────────────────────

INSERT INTO daily_product_metrics
    (product_id, region_id, metric_date, total_revenue, total_units_sold,
     total_orders, avg_order_value, avg_discount_pct, gross_profit, profit_margin)
SELECT
    s.product_id,
    s.region_id,
    s.transaction_date::date AS metric_date,
    SUM(s.total_amount)                                        AS total_revenue,
    SUM(s.quantity)                                            AS total_units_sold,
    COUNT(*)                                                   AS total_orders,
    ROUND(AVG(s.total_amount), 2)                              AS avg_order_value,
    ROUND(AVG(s.discount_pct), 2)                              AS avg_discount_pct,
    SUM(s.total_amount) - SUM(s.quantity * p.cost)             AS gross_profit,
    ROUND(
        (SUM(s.total_amount) - SUM(s.quantity * p.cost))
        / NULLIF(SUM(s.total_amount), 0) * 100, 2
    )                                                          AS profit_margin
FROM sales_transactions s
JOIN products p ON s.product_id = p.id
GROUP BY s.product_id, s.region_id, s.transaction_date::date
ON CONFLICT (product_id, region_id, metric_date) DO UPDATE SET
    total_revenue    = EXCLUDED.total_revenue,
    total_units_sold = EXCLUDED.total_units_sold,
    total_orders     = EXCLUDED.total_orders,
    avg_order_value  = EXCLUDED.avg_order_value,
    avg_discount_pct = EXCLUDED.avg_discount_pct,
    gross_profit     = EXCLUDED.gross_profit,
    profit_margin    = EXCLUDED.profit_margin;

-- ─── PRE-COMPUTE: KPI SUMMARY (Monthly Overall) ─────────────

INSERT INTO kpi_summary
    (kpi_name, kpi_value, kpi_unit, period_type, period_start, period_end,
     dimension_type, dimension_value)
SELECT
    'total_revenue',
    SUM(total_revenue),
    'USD',
    'monthly',
    date_trunc('month', metric_date)::date,
    (date_trunc('month', metric_date) + INTERVAL '1 month' - INTERVAL '1 day')::date,
    'overall',
    'all'
FROM daily_product_metrics
GROUP BY date_trunc('month', metric_date)
ON CONFLICT (kpi_name, period_type, period_start, dimension_type, dimension_value) DO UPDATE SET
    kpi_value = EXCLUDED.kpi_value;

INSERT INTO kpi_summary
    (kpi_name, kpi_value, kpi_unit, period_type, period_start, period_end,
     dimension_type, dimension_value)
SELECT
    'total_units_sold',
    SUM(total_units_sold),
    'units',
    'monthly',
    date_trunc('month', metric_date)::date,
    (date_trunc('month', metric_date) + INTERVAL '1 month' - INTERVAL '1 day')::date,
    'overall',
    'all'
FROM daily_product_metrics
GROUP BY date_trunc('month', metric_date)
ON CONFLICT (kpi_name, period_type, period_start, dimension_type, dimension_value) DO UPDATE SET
    kpi_value = EXCLUDED.kpi_value;

INSERT INTO kpi_summary
    (kpi_name, kpi_value, kpi_unit, period_type, period_start, period_end,
     dimension_type, dimension_value)
SELECT
    'avg_order_value',
    ROUND(AVG(avg_order_value), 2),
    'USD',
    'monthly',
    date_trunc('month', metric_date)::date,
    (date_trunc('month', metric_date) + INTERVAL '1 month' - INTERVAL '1 day')::date,
    'overall',
    'all'
FROM daily_product_metrics
GROUP BY date_trunc('month', metric_date)
ON CONFLICT (kpi_name, period_type, period_start, dimension_type, dimension_value) DO UPDATE SET
    kpi_value = EXCLUDED.kpi_value;

INSERT INTO kpi_summary
    (kpi_name, kpi_value, kpi_unit, period_type, period_start, period_end,
     dimension_type, dimension_value)
SELECT
    'gross_profit',
    SUM(gross_profit),
    'USD',
    'monthly',
    date_trunc('month', metric_date)::date,
    (date_trunc('month', metric_date) + INTERVAL '1 month' - INTERVAL '1 day')::date,
    'overall',
    'all'
FROM daily_product_metrics
GROUP BY date_trunc('month', metric_date)
ON CONFLICT (kpi_name, period_type, period_start, dimension_type, dimension_value) DO UPDATE SET
    kpi_value = EXCLUDED.kpi_value;

-- ─── PRE-COMPUTE: KPI SUMMARY (Monthly by Category) ─────────

INSERT INTO kpi_summary
    (kpi_name, kpi_value, kpi_unit, period_type, period_start, period_end,
     dimension_type, dimension_value)
SELECT
    'category_revenue',
    SUM(dm.total_revenue),
    'USD',
    'monthly',
    date_trunc('month', dm.metric_date)::date,
    (date_trunc('month', dm.metric_date) + INTERVAL '1 month' - INTERVAL '1 day')::date,
    'category',
    c.name
FROM daily_product_metrics dm
JOIN products p ON dm.product_id = p.id
JOIN categories c ON p.category_id = c.id
GROUP BY date_trunc('month', dm.metric_date), c.name
ON CONFLICT (kpi_name, period_type, period_start, dimension_type, dimension_value) DO UPDATE SET
    kpi_value = EXCLUDED.kpi_value;

-- ─── VIEWS FOR EASY QUERYING ─────────────────────────────────

CREATE OR REPLACE VIEW v_product_performance AS
SELECT
    p.id AS product_id,
    p.sku,
    p.name AS product_name,
    c.name AS category,
    p.price,
    p.cost,
    COALESCE(SUM(dm.total_revenue), 0) AS lifetime_revenue,
    COALESCE(SUM(dm.total_units_sold), 0) AS lifetime_units,
    COALESCE(SUM(dm.total_orders), 0) AS lifetime_orders,
    COALESCE(SUM(dm.gross_profit), 0) AS lifetime_profit,
    ROUND(COALESCE(AVG(dm.profit_margin), 0), 2) AS avg_profit_margin
FROM products p
JOIN categories c ON p.category_id = c.id
LEFT JOIN daily_product_metrics dm ON p.id = dm.product_id
GROUP BY p.id, p.sku, p.name, c.name, p.price, p.cost;

CREATE OR REPLACE VIEW v_regional_performance AS
SELECT
    r.id AS region_id,
    r.name AS region_name,
    r.country,
    COALESCE(SUM(dm.total_revenue), 0) AS total_revenue,
    COALESCE(SUM(dm.total_units_sold), 0) AS total_units,
    COALESCE(SUM(dm.total_orders), 0) AS total_orders,
    COALESCE(SUM(dm.gross_profit), 0) AS gross_profit
FROM regions r
LEFT JOIN daily_product_metrics dm ON r.id = dm.region_id
GROUP BY r.id, r.name, r.country;

CREATE OR REPLACE VIEW v_monthly_trends AS
SELECT
    date_trunc('month', metric_date)::date AS month,
    SUM(total_revenue) AS revenue,
    SUM(total_units_sold) AS units_sold,
    SUM(total_orders) AS orders,
    ROUND(AVG(avg_order_value), 2) AS avg_order_value,
    SUM(gross_profit) AS gross_profit,
    ROUND(AVG(profit_margin), 2) AS avg_profit_margin
FROM daily_product_metrics
GROUP BY date_trunc('month', metric_date)
ORDER BY month;
