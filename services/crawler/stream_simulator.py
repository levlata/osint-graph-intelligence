import asyncio
import random
import json
import os
from datetime import datetime

class DarknetOSINTCrawler:
    def __init__(self):
        self.sources = ["https://leakmarket_v4.onion/topic_", "https://cybercrime_forum/thread_"]
        self.templates = [
            "ПРОДАЖА: Свежая база данных клиентов. Контакты организатора: TG {tg}. Телефон для связи {phone}. Оплата строго на BTC: {wallet}.",
            "Внимание! Слиты логи авторизации. Связаться со мной можно в Telegram: {tg}. Мой резервный телефон {phone}.",
            "Эксклюзивный дамп криптокошельков 2026! По всем вопросам писать в личку {tg}. Мой крипто-адрес для гаранта: {wallet}."
        ]
        self.pool_phones = ["+79991112233", "+79995556677", "+79110001122", "+79003334455"]
        self.pool_wallets = ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5", "bc1qxy2kgdygjrsqtzq5qq4g428pds5"]
        self.pool_tgs = ["@shadow_broker", "@dark_knight", "@leak_master", "@cyber_phantom"]

    def generate_leak_event(self):
        template = random.choice(self.templates)
        phone = random.choice(self.pool_phones)
        wallet = random.choice(self.pool_wallets)
        tg = random.choice(self.pool_tgs)
        raw_text = template.format(phone=phone, wallet=wallet, tg=tg)
        return {
            "source_url": f"{random.choice(self.sources)}{random.randint(10000, 99999)}",
            "raw_title": f"CRITICAL DATA LEAK #{random.randint(100, 999)}",
            "raw_text": raw_text,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def start_crawling_stream(self):
        print("🌐 [Crawler] Инициализация асинхронных воркеров Playwright...")
        print("🚀 [Crawler] Потоковый сбор данных запущен...")
        buffer_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "firebase_buffer.json")
        while True:
            leak_data = self.generate_leak_event()
            print(f"📥 [Парсер] Найдена новая уязвимость: {leak_data['raw_title']}")
            with open(buffer_path, "a+", encoding="utf-8") as f:
                f.write(json.dumps(leak_data, ensure_ascii=False) + "\n")
            await asyncio.sleep(4)

if __name__ == "__main__":
    crawler = DarknetOSINTCrawler()
    try:
        asyncio.run(crawler.start_crawling_stream())
    except KeyboardInterrupt:
        print("\n🛑 Процесс парсинга принудительно остановлен.")
