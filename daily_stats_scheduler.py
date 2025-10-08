"""
Скрипт для ежедневной отправки статистики в 00:00 МСК
"""

import asyncio
import logging
import schedule
import time
import os
from datetime import datetime, timedelta
from telegram import Bot
from statistics import StatisticsManager
from stats_handler import StatsHandler
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('token.env')

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы из переменных окружения
TOKEN = os.getenv("TOKEN")
ADMIN_CHAT_ID = "-4742593122"  # Оставляем в коде, так как это не секретная информация

# Устройства для StatsHandler
devices = {
    'printer': type('Device', (), {'name': 'Принтер'})()
}

async def send_daily_stats():
    """Отправка ежедневной статистики"""
    try:
        if not TOKEN:
            logger.error("TOKEN не найден в переменных окружения!")
            return
            
        logger.info("Начинаем отправку ежедневной статистики...")
        
        # Создаем экземпляры
        stats_manager = StatisticsManager()
        stats_handler = StatsHandler(stats_manager, devices)
        
        # Создаем бота
        bot = Bot(token=TOKEN)
        
        # Получаем статистику за вчерашний день
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        stats = stats_manager.get_daily_stats(yesterday)
        
        # Сохраняем статистику
        stats_manager.save_daily_stats(yesterday, stats)
        
        # Форматируем сообщение
        message = stats_handler.format_stats_message(stats)
        
        # Отправляем сообщение
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode='HTML'
        )
        
        logger.info(f"Ежедневная статистика отправлена в чат за {yesterday}")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке ежедневной статистики: {e}")

def run_daily_stats():
    """Запуск ежедневной статистики в синхронном режиме"""
    asyncio.run(send_daily_stats())

def main():
    """Основная функция"""
    logger.info("Запуск планировщика ежедневной статистики...")
    logger.info("Статистика будет отправляться каждый день в 00:00 МСК")
    
    # Планируем задачу на каждый день в 00:00 МСК
    schedule.every().day.at("00:00").do(run_daily_stats)
    
    # Бесконечный цикл проверки расписания
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Проверяем каждую минуту
        except KeyboardInterrupt:
            logger.info("Остановка планировщика...")
            break
        except Exception as e:
            logger.error(f"Ошибка в планировщике: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()
