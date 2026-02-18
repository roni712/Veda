 - For FastApi cd backend
 uvicorn app.main:app --reload --port 8000

- For Docker
 To remove all container
docker compose -f infra/docker-compose.yml down -v
 To start container
docker compose -f infra/docker-compose.yml up -d

- for db create
python -m app.db.init_db

-- for demo db
docker exec -i veda_client_postgres psql -U client_user -d client_db << 'SQL'
CREATE SCHEMA IF NOT EXISTS sales;
CREATE SCHEMA IF NOT EXISTS ops;

CREATE TABLE IF NOT EXISTS sales.orders (
  order_id SERIAL PRIMARY KEY,
  customer_name TEXT NOT NULL,
  order_amount NUMERIC(10,2) NOT NULL,
  order_status TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sales.order_items (
  item_id SERIAL PRIMARY KEY,
  order_id INT NOT NULL,
  sku TEXT NOT NULL,
  qty INT NOT NULL,
  price NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS ops.pipeline_runs (
  run_id SERIAL PRIMARY KEY,
  pipeline_name TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TIMESTAMP NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMP NULL
);

INSERT INTO sales.orders (customer_name, order_amount, order_status)
VALUES
('Alice', 120.50, 'PAID'),
('Bob', 55.00, 'PENDING'),
('Charlie', 300.00, 'PAID');

INSERT INTO sales.order_items (order_id, sku, qty, price)
VALUES
(1, 'SKU-RED-001', 1, 120.50),
(2, 'SKU-BLU-002', 2, 27.50),
(3, 'SKU-GRN-003', 3, 100.00);

INSERT INTO ops.pipeline_runs (pipeline_name, status, finished_at)
VALUES
('daily_sales_etl', 'SUCCESS', NOW()),
('inventory_sync', 'FAILED', NOW());
SQL



## altering the table to see
docker exec -it veda_client_postgres psql -U client_user -d client_db -c "ALTER TABLE sales.orders ADD COLUMN coupon_code TEXT;"



## create a table in slaes schema
docker exec -it veda_client_postgres psql -U client_user -d client_db -c "CREATE TABLE IF NOT EXISTS sales.coupons (id SERIAL PRIMARY KEY,coupons_name TEXT NOT NULL);"