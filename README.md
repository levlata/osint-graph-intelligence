# Real-Time OSINT Graph Intelligence Platform

An enterprise-grade, event-driven analytics pipeline designed for real-time shadow forum monitoring, automated entity resolution, and predictive fraud network mapping.

## 🛠️ Tech Stack & Architecture

- **Python (Asyncio)**: High-performance asynchronous engine powering the distributed headless crawlers and telemetry processor.
- **Docker Desktop**: Component isolation via a multi-container network separating database storage and analytical layers.
- **PostgreSQL (DWH)**: Low-latency data warehouse running automated DDL initializations inside Docker on a custom port `5439`.
- **NetworkX**: In-memory mathematical graph library calculating PageRank and centrality weights to detect fraud syndicates.
- **Power BI Desktop**: Bi-directional interactive dashboard connected via **DirectQuery** for live network visualization.

## 🚀 System Architecture Flow

1. **Ingestion**: Async crawlers simulate high-frequency darknet data scraping, packing items into a high-throughput streaming buffer (`firebase_buffer.json`).
2. **Entity Resolution**: Python processors extract regex-based indicators (crypto wallets, phone numbers, telegram tags).
3. **Graph Scoring**: NetworkX constructs multi-dimensional edge connections and scores risk vectors in real time.
4. **DWH Persistence**: `asyncpg` commits high-speed batch executions directly into an isolated Dockerized PostgreSQL instance.

## 📦 Local Deployment Instructions

1. Ensure **Docker Desktop** is running.
2. Clone the repository and initialize the infrastructure:
   ```bash
   docker-compose up -d
   ```
3. Run the microservices concurrently inside PyCharm:
   ```bash
   python services/crawler/stream_simulator.py
   python services/processor/streaming_processor.py
   ```
4. Open **Power BI Desktop**, connect to PostgreSQL via `127.0.0.1:5439` using **DirectQuery**, and load the `mart_fraud_networks` datamart.
