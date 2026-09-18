import asyncio
import re
import json
import random
import os
import asyncpg
import networkx as nx

DB_CONFIG = {
    "user": "quant_user",
    "password": "crypto_pass123",
    "database": "osint_analytics",
    "host": "127.0.0.1",
    "port": 5439
}


class OSINTGraphEngine:
    def __init__(self):
        self.phone_regex = r'\+7\d{10}'
        self.wallet_regex = r'(?:1|3|bc1)[a-zA-Z0-9]{25,39}'
        self.tg_regex = r'@[a-zA-Z0-9_]{5,}'

    async def init_database_tables(self, conn):
        """Хардкорная авто-инициализация таблиц прямо из Python"""
        print("🤖 [SQL DWH] Проверка структуры базы данных и создание таблиц...")
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS raw_leaks (
                id SERIAL PRIMARY KEY,
                source_url TEXT NOT NULL,
                raw_title TEXT,
                raw_text TEXT NOT NULL,
                parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS entities (
                entity_id SERIAL PRIMARY KEY,
                entity_type VARCHAR(50) NOT NULL,
                entity_value TEXT NOT NULL UNIQUE,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS leak_entities (
                leak_id INT REFERENCES raw_leaks(id) ON DELETE CASCADE,
                entity_id INT REFERENCES entities(entity_id) ON DELETE CASCADE,
                PRIMARY KEY (leak_id, entity_id)
            );

            CREATE TABLE IF NOT EXISTS analytics_vectors (
                leak_id INT PRIMARY KEY REFERENCES raw_leaks(id) ON DELETE CASCADE,
                risk_score NUMERIC(4,3),
                text_embedding REAL[]    
            );

            CREATE TABLE IF NOT EXISTS mart_fraud_networks (
                id SERIAL PRIMARY KEY,
                network_id VARCHAR(100),
                node_from TEXT,
                node_to TEXT,
                connection_type TEXT,
                weight INT,
                max_risk_score NUMERIC(4,3),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        print("✅ [SQL DWH] Все таблицы успешно проверены и созданы в базе!")

    def extract_entities(self, text):
        entities = []
        for p in re.findall(self.phone_regex, text): entities.append(('phone', p))
        for w in re.findall(self.wallet_regex, text): entities.append(('crypto_wallet', w))
        for t in re.findall(self.tg_regex, text): entities.append(('telegram', t))
        return entities

    def generate_nlp_embedding(self):
        return [random.uniform(-1.0, 1.0) for _ in range(384)]

    async def process_live_buffer(self):
        buffer_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "firebase_buffer.json")
        if not os.path.exists(buffer_path): return
        with open(buffer_path, "r+", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines: return
            f.seek(0)
            f.truncate()

        print(f"⚡ [Risk Engine] Перехвачено {len(lines)} событий. Начинаем расчет графа...")
        conn = await asyncpg.connect(**DB_CONFIG)

        # Гарантируем наличие таблиц перед началом вставки
        await self.init_database_tables(conn)

        G = nx.Graph()

        for line in lines:
            if not line.strip(): continue
            item = json.loads(line.strip())
            leak_id = await conn.fetchval(
                "INSERT INTO raw_leaks (source_url, raw_title, raw_text) VALUES ($1, $2, $3) RETURNING id",
                item['source_url'], item['raw_title'], item['raw_text']
            )
            embedding = self.generate_nlp_embedding()
            risk_score = random.uniform(0.35, 0.98)
            await conn.execute(
                "INSERT INTO analytics_vectors (leak_id, risk_score, text_embedding) VALUES ($1, $2, $3)",
                leak_id, risk_score, embedding
            )
            extracted = self.extract_entities(item['raw_text'])
            for ent_type, ent_val in extracted:
                ent_id = await conn.fetchval(
                    "INSERT INTO entities (entity_type, entity_value) VALUES ($1, $2) "
                    "ON CONFLICT (entity_value) DO UPDATE SET entity_value = EXCLUDED.entity_value RETURNING entity_id",
                    ent_type, ent_val
                )
                await conn.execute(
                    "INSERT INTO leak_entities (leak_id, entity_id) VALUES ($1, $2) ON CONFLICT DO NOTHING", leak_id,
                    ent_id)

            for i in range(len(extracted)):
                for j in range(i + 1, len(extracted)):
                    node_a = f"{extracted[i][0]}: {extracted[i][1]}"
                    node_b = f"{extracted[j][0]}: {extracted[j][1]}"
                    G.add_edge(node_a, node_b, risk=risk_score)

        if len(G.nodes) > 0:
            pagerank_weights = nx.pagerank(G, weight='risk')
            print(f"📊 [Граф] Выделено {len(G.nodes)} узлов и {len(G.edges)} связей.")
            for u, v, edge_data in G.edges(data=True):
                network_id = f"NET_GROUP_{abs(hash(u) + hash(v)) % 100000}"
                calculated_weight = int((pagerank_weights[u] + pagerank_weights[v]) * 500)
                await conn.execute(
                    "INSERT INTO mart_fraud_networks (network_id, node_from, node_to, connection_type, weight, max_risk_score) "
                    "VALUES ($1, $2, $3, $4, $5, $6)",
                    network_id, u, v, "shared_incident_context", calculated_weight, edge_data['risk']
                )
        await conn.close()
        print("💾 [SQL DWH] Аналитическая витрина успешно обновлена.")

    async def execution_loop(self):
        while True:
            await self.process_live_buffer()
            await asyncio.sleep(5)


if __name__ == "__main__":
    engine = OSINTGraphEngine()
    print("🚀 [Risk Engine] Движок графовой аналитики запущен. Ожидание данных...")
    try:
        asyncio.run(engine.execution_loop())
    except KeyboardInterrupt:
        print("\n🛑 Аналитический движок остановлен.")
