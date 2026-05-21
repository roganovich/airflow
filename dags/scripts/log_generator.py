#!/usr/bin/env python3
"""
Генератор логов - создает 1 млн строк логов в формате Apache/Nginx или JSON.

Использование:
    python log_generator.py [--format apache|json] [--output FILE] [--lines N]
                 [--seed SEED] [--verbose] [--batch-size N] [--dirty-percent P]

Примеры:
    # Генерация 1 млн строк Apache логов с 5% "грязных" данных
    python log_generator.py --format apache --output access.log --lines 1000000 --dirty-percent 5
    
    # Генерация 500k JSON логов с воспроизводимым seed
    python log_generator.py --format json --output logs.json --lines 500000 --seed 42
    
    # Генерация Apache логов с 10% "грязных" данных и выводом прогресса
    python log_generator.py --format apache --lines 10000 --dirty-percent 10 --verbose
    
    # Генерация JSON логов с большим batch size для оптимизации
    python log_generator.py --format json --lines 1000000 --batch-size 50000 --output big_logs.json
    
    # Генерация чистых логов (0% "грязных" данных)
    python log_generator.py --format apache --lines 100000 --dirty-percent 0 --output clean_access.log
    
    # Просмотр всех доступных параметров
    python log_generator.py --help
"""

import argparse
import sys
import random
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Generator
import itertools


class LogGenerator:
    """Базовый класс для генерации логов."""
    
    def __init__(self, seed: int = None):
        """Инициализация генератора случайных данных."""
        if seed is not None:
            random.seed(seed)
        self._init_data_sources()
    
    def _init_data_sources(self):
        """Инициализация источников данных для генерации логов."""
        # IP-адреса
        self.ip_pools = [
            "192.168.1.{}".format(i) for i in range(1, 255)
        ] + [
            "10.0.0.{}".format(i) for i in range(1, 100)
        ] + [
            "172.16.0.{}".format(i) for i in range(1, 50)
        ] + [
            "203.0.113.{}".format(i) for i in range(1, 50)  # Дополнительные публичные IP
        ]
        
        # Пользовательские агенты
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0",
            "curl/7.68.0",
            "PostmanRuntime/7.28.0",
            "python-requests/2.25.1",
            "Go-http-client/1.1",
            "Java/11.0.11",
        ]
        
        # HTTP методы
        self.http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        
        # URL пути (включая параметры)
        self.url_paths = [
            "/", "/index.html", "/home", "/about", "/contact",
            "/api/v1/users", "/api/v1/products", "/api/v1/orders",
            "/static/css/style.css", "/static/js/app.js", "/images/logo.png",
            "/blog/post/123", "/shop/category/electronics",
            "/admin", "/login", "/logout", "/register",
            "/search?q=python", "/products?category=books&page=2",
            "/api/data?format=json&limit=100", "/user/profile?id=12345",
            "/cart/add?product_id=987&quantity=2", "/checkout/payment",
        ]
        
        # HTTP статусы с разными вероятностями
        self.status_codes = [200, 200, 200, 200, 201, 204, 301, 302,  # Успешные и редиректы (чаще)
                            400, 401, 403, 404, 404, 404, 500, 502, 503]  # Ошибки
        
        # Референты
        self.referrers = [
            "-",  # прямой заход
            "https://www.google.com/",
            "https://www.bing.com/",
            "https://www.yahoo.com/",
            "https://stackoverflow.com/",
            "https://github.com/",
            "https://example.com/",
            "https://internal.company.com/",
            "https://twitter.com/",
            "https://www.facebook.com/",
            "https://www.linkedin.com/",
        ]
        
        # Имена пользователей для базовой аутентификации
        self.usernames = ["-", "admin", "user123", "john_doe", "jane_smith", "api_user", "test_user", "guest"]
        
        # Протоколы
        self.protocols = ["HTTP/1.0", "HTTP/1.1", "HTTP/2"]
    
    def generate_log_entry(self, timestamp: datetime = None, make_dirty: bool = False,
                          dirty_probability: float = 0.05) -> Dict[str, Any]:
        """Генерирует одну запись лога в виде словаря.
        
        Args:
            timestamp: Временная метка (если None, генерируется случайная)
            make_dirty: Если True, генерирует "грязные" данные с проблемами
            dirty_probability: Вероятность "грязных" данных (0.0-1.0) если make_dirty=True
            
        Returns:
            Словарь с полями лога.
        """
        if timestamp is None:
            # Генерируем временную метку в пределах последних 30 дней
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            seconds_ago = random.randint(0, 59)
            
            timestamp = datetime.now() - timedelta(
                days=days_ago,
                hours=hours_ago,
                minutes=minutes_ago,
                seconds=seconds_ago
            )
        
        # Определяем, будет ли эта запись "грязной" (dirty_probability chance если make_dirty=True)
        is_dirty = make_dirty and random.random() < dirty_probability
        
        # Базовые поля
        ip = random.choice(self.ip_pools)
        user = random.choice(self.usernames)
        method = random.choice(self.http_methods)
        path = random.choice(self.url_paths)
        status = random.choice(self.status_codes)
        
        # Размер ответа с некоторой вариативностью
        if status >= 400:
            # Для ошибок размер обычно меньше
            size = random.randint(50, 5000)
        else:
            size = random.randint(100, 1024 * 1024 * 10)  # от 100 байт до 10 МБ
        
        referrer = random.choice(self.referrers)
        user_agent = random.choice(self.user_agents)
        protocol = random.choice(self.protocols)
        
        # Время ответа в миллисекундах (логарифмическое распределение для реалистичности)
        response_time = int(random.lognormvariate(4, 1.2))  # большинство 50-500 мс, некоторые до 10 сек
        response_time = min(response_time, 30000)  # ограничим 30 секундами
        
        # Применяем "грязные" данные если нужно
        if is_dirty:
            dirty_type = random.choice(["null_fields", "malformed", "extra_fields", "missing_fields"])
            
            if dirty_type == "null_fields":
                # Некоторые поля имеют значение None или пустые строки
                null_field = random.choice(["user", "referrer", "user_agent", "ip"])
                if null_field == "user":
                    user = "-"
                elif null_field == "referrer":
                    referrer = ""
                elif null_field == "user_agent":
                    user_agent = ""
                elif null_field == "ip":
                    ip = "0.0.0.0"
            
            elif dirty_type == "malformed":
                # Искаженные данные
                ip = "invalid_ip_address"
                path = "/path with spaces and \"quotes\""
                user_agent = "Mozilla/5.0 (broken; user agent"
            
            elif dirty_type == "extra_fields":
                # Добавляем лишние символы или поля (обрабатывается в форматировании)
                path = path + "?param=<script>alert('xss')</script>"
                user_agent = user_agent + "; " + "A" * 1000  # Очень длинный user agent
            
            elif dirty_type == "missing_fields":
                # Пропускаем некоторые поля (будут заменены на "-" в форматировании)
                user = ""
                referrer = ""
        
        entry = {
            "timestamp": timestamp,
            "ip_address": ip,
            "user": user,
            "method": method,
            "url": path,
            "status_code": status,
            "response_time_ms": response_time,
            "size": size,
            "referrer": referrer,
            "user_agent": user_agent,
            "protocol": protocol,
            "is_dirty": is_dirty,
        }
        
        return entry


class ApacheLogGenerator(LogGenerator):
    """Генератор логов в формате Apache/Nginx Common Log Format."""
    
    def __init__(self, seed: int = None, dirty_percent: float = 5.0):
        """Инициализация генератора Apache логов.
        
        Args:
            seed: Seed для генератора случайных чисел
            dirty_percent: Процент "грязных" данных (0-100)
        """
        super().__init__(seed)
        self.dirty_percent = dirty_percent / 100.0  # Конвертируем в долю
    
    def format_entry(self, entry: Dict[str, Any]) -> str:
        """Форматирует запись лога в расширенном Apache Common Log Format.
        
        Расширенный формат включает время ответа: IP - user [timestamp] "METHOD URL PROTOCOL" STATUS SIZE "REFERRER" "USER_AGENT" RESPONSE_TIME
        Пример: 192.168.1.1 - - [21/May/2026:14:22:13 +0300] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0..." 142
        
        Для "грязных" данных может возвращаться нестандартный формат.
        """
        # Обработка "грязных" данных - специальное форматирование
        if entry.get("is_dirty", False):
            return self._format_dirty_entry(entry)
        
        # Форматируем timestamp в Apache формате
        timestamp_str = entry["timestamp"].strftime("%d/%b/%Y:%H:%M:%S +0300")
        
        # Подготавливаем поля, заменяем пустые значения на "-"
        ip = entry["ip_address"] if entry["ip_address"] else "-"
        user = entry["user"] if entry["user"] else "-"
        method = entry["method"]
        url = entry["url"]
        protocol = entry.get("protocol", "HTTP/1.1")
        status = entry["status_code"]
        size = entry["size"]
        referrer = entry["referrer"] if entry["referrer"] else "-"
        user_agent = entry["user_agent"] if entry["user_agent"] else "-"
        response_time = entry.get("response_time_ms", 0)
        
        # Экранируем кавычки в referrer и user_agent
        referrer = referrer.replace('"', '\\"')
        user_agent = user_agent.replace('"', '\\"')
        
        # Расширенный формат с временем ответа
        return '{ip} - {user} [{timestamp}] "{method} {url} {protocol}" {status} {size} "{referrer}" "{user_agent}" {response_time}'.format(
            ip=ip,
            user=user,
            timestamp=timestamp_str,
            method=method,
            url=url,
            protocol=protocol,
            status=status,
            size=size,
            referrer=referrer,
            user_agent=user_agent,
            response_time=response_time,
        )
    
    def _format_dirty_entry(self, entry: Dict[str, Any]) -> str:
        """Форматирует "грязную" запись лога с проблемами в формате."""
        # Несколько вариантов "грязного" форматирования
        dirty_format = random.choice([
            "malformed",      # Неполная строка
            "extra_fields",   # Лишние поля
            "wrong_order",    # Неправильный порядок полей
            "unclosed_quote", # Незакрытые кавычки
        ])
        
        timestamp_str = entry["timestamp"].strftime("%d/%b/%Y:%H:%M:%S +0300")
        ip = entry["ip_address"] if entry["ip_address"] else "-"
        user = entry["user"] if entry["user"] else "-"
        
        if dirty_format == "malformed":
            # Неполная строка (обрывается посередине)
            return '{ip} - {user} [{timestamp}] "GET /malformed'.format(
                ip=ip, user=user, timestamp=timestamp_str
            )
        
        elif dirty_format == "extra_fields":
            # Лишние поля или разделители
            return '{ip} - {user} - EXTRA [{timestamp}] "GET {url} HTTP/1.1" 200 {size} "{referrer}" "{user_agent}" {response_time} EXTRA_DATA'.format(
                ip=ip,
                user=user,
                timestamp=timestamp_str,
                url=entry["url"],
                size=entry["size"],
                referrer=entry["referrer"] if entry["referrer"] else "-",
                user_agent=entry["user_agent"] if entry["user_agent"] else "-",
                response_time=entry.get("response_time_ms", 0),
            )
        
        elif dirty_format == "wrong_order":
            # Неправильный порядок полей
            return '[{timestamp}] {ip} - {user} "{method} {url}" {status} {size}'.format(
                timestamp=timestamp_str,
                ip=ip,
                user=user,
                method=entry["method"],
                url=entry["url"],
                status=entry["status_code"],
                size=entry["size"],
            )
        
        else:  # unclosed_quote
            # Незакрытые кавычки
            return '{ip} - {user} [{timestamp}] "GET {url} HTTP/1.1" 200 {size} "unclosed quote'.format(
                ip=ip,
                user=user,
                timestamp=timestamp_str,
                url=entry["url"],
                size=entry["size"],
            )
    
    def generate(self, num_lines: int) -> Generator[str, None, None]:
        """Генерирует указанное количество строк логов в Apache формате.
        
        Args:
            num_lines: Количество строк для генерации.
            
        Yields:
            Строки логов в Apache формате.
        """
        for i in range(num_lines):
            # Определяем, должна ли эта строка быть "грязной" (на основе процента)
            make_dirty = random.random() < self.dirty_percent
            entry = self.generate_log_entry(make_dirty=make_dirty, dirty_probability=self.dirty_percent)
            yield self.format_entry(entry)


class JsonLogGenerator(LogGenerator):
    """Генератор логов в формате JSON (по одной JSON-объекту на строку)."""
    
    def __init__(self, seed: int = None, dirty_percent: float = 5.0):
        """Инициализация генератора JSON логов.
        
        Args:
            seed: Seed для генератора случайных чисел
            dirty_percent: Процент "грязных" данных (0-100)
        """
        super().__init__(seed)
        self.dirty_percent = dirty_percent / 100.0  # Конвертируем в долю
    
    def format_entry(self, entry: Dict[str, Any]) -> str:
        """Форматирует запись лога в формате JSON.
        
        Returns:
            JSON-строка с полями лога. Для "грязных" данных может возвращаться
            невалидный JSON или JSON с проблемами.
        """
        # Обработка "грязных" данных
        if entry.get("is_dirty", False):
            return self._format_dirty_json(entry)
        
        # Нормальная запись - конвертируем datetime в строку ISO формата
        entry_copy = entry.copy()
        entry_copy["timestamp"] = entry_copy["timestamp"].isoformat()
        
        # Удаляем служебное поле is_dirty из финального JSON
        if "is_dirty" in entry_copy:
            del entry_copy["is_dirty"]
        
        return json.dumps(entry_copy, ensure_ascii=False)
    
    def _format_dirty_json(self, entry: Dict[str, Any]) -> str:
        """Форматирует "грязную" запись лога с проблемами в JSON."""
        dirty_type = random.choice([
            "malformed_json",    # Невалидный JSON
            "null_values",       # Null значения
            "missing_fields",    # Отсутствующие поля
            "extra_fields",      # Лишние/нестандартные поля
            "unclosed_brace",    # Незакрытая скобка
        ])
        
        # Создаем копию для модификации
        entry_copy = entry.copy()
        entry_copy["timestamp"] = entry_copy["timestamp"].isoformat()
        
        if dirty_type == "malformed_json":
            # Невалидный JSON (пропущена запятая, незакрытая кавычка и т.д.)
            json_str = json.dumps(entry_copy, ensure_ascii=False)
            # Искажаем JSON разными способами
            if random.random() < 0.5:
                # Пропускаем запятую
                json_str = json_str.replace('", "', '" "', 1)
            else:
                # Незакрытая кавычка
                json_str = json_str.replace('"', '', 1)
            return json_str
        
        elif dirty_type == "null_values":
            # Некоторые поля имеют значение null
            for key in ["user_agent", "referrer", "user", "ip_address"]:
                if random.random() < 0.3:
                    entry_copy[key] = None
            return json.dumps(entry_copy, ensure_ascii=False)
        
        elif dirty_type == "missing_fields":
            # Удаляем некоторые обязательные поля
            fields_to_remove = random.sample(
                ["timestamp", "ip_address", "method", "url", "status_code"],
                k=random.randint(1, 2)
            )
            for field in fields_to_remove:
                if field in entry_copy:
                    del entry_copy[field]
            return json.dumps(entry_copy, ensure_ascii=False)
        
        elif dirty_type == "extra_fields":
            # Добавляем лишние/нестандартные поля
            extra_fields = {
                "debug_info": "some debug data " * 10,
                "correlation_id": None,
                "unexpected_field": "<script>alert('xss')</script>",
                "nested": {"level1": {"level2": {"level3": "deep"}}}
            }
            entry_copy.update(extra_fields)
            return json.dumps(entry_copy, ensure_ascii=False)
        
        else:  # unclosed_brace
            # Незакрытая фигурная скобка
            json_str = json.dumps(entry_copy, ensure_ascii=False)
            return json_str[:-1]  # Удаляем последнюю закрывающую скобку
    
    def generate(self, num_lines: int) -> Generator[str, None, None]:
        """Генерирует указанное количество строк логов в JSON формате.
        
        Args:
            num_lines: Количество строк для генерации.
            
        Yields:
            Строки логов в JSON формате.
        """
        for i in range(num_lines):
            # Определяем, должна ли эта строка быть "грязной" (на основе процента)
            make_dirty = random.random() < self.dirty_percent
            entry = self.generate_log_entry(make_dirty=make_dirty, dirty_probability=self.dirty_percent)
            yield self.format_entry(entry)


def parse_arguments():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Генератор логов - создает 1 млн строк логов в формате Apache/Nginx или JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --format apache --output access.log --lines 1000000
  %(prog)s --format json --output logs.json --lines 100000
  %(prog)s --format apache --verbose  # вывод в stdout с прогрессом
  %(prog)s --seed 42  # воспроизводимая генерация
        """
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["apache", "json"],
        default="apache",
        help="Формат логов: 'apache' для Apache/Nginx формата, 'json' для JSON (по умолчанию: apache)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Выходной файл (по умолчанию: stdout)"
    )
    
    parser.add_argument(
        "-l", "--lines",
        type=int,
        default=1000000,
        help="Количество строк для генерации (по умолчанию: 1000000)"
    )
    
    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=None,
        help="Seed для генератора случайных чисел (для воспроизводимости)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Выводить прогресс генерации"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10000,
        help="Размер батча для записи в файл (по умолчанию: 10000)"
    )
    
    parser.add_argument(
        "--dirty-percent",
        type=float,
        default=5.0,
        help="Процент 'грязных' данных с проблемами в формате (0-100, по умолчанию: 5.0)"
    )
    
    return parser.parse_args()


def main():
    """Основная функция скрипта."""
    args = parse_arguments()
    
    # Выбираем генератор в зависимости от формата
    if args.format == "apache":
        generator = ApacheLogGenerator(seed=args.seed, dirty_percent=args.dirty_percent)
        file_ext = ".log"
    else:  # json
        generator = JsonLogGenerator(seed=args.seed, dirty_percent=args.dirty_percent)
        file_ext = ".json"
    
    # Определяем выходной поток
    if args.output:
        output_file = args.output
    else:
        # Если файл не указан, генерируем имя по умолчанию
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"generated_logs_{timestamp}{file_ext}"
    
    start_time = time.time()
    lines_generated = 0
    
    try:
        if args.verbose:
            print(f"Генерация {args.lines:,} строк логов в формате {args.format}...")
            print(f"Выходной файл: {output_file}")
            print(f"Seed: {args.seed if args.seed else 'случайный'}")
            print("-" * 50)
        
        # Открываем файл для записи
        with open(output_file, 'w', encoding='utf-8') as f:
            batch = []
            
            for i, line in enumerate(generator.generate(args.lines)):
                batch.append(line)
                
                # Записываем батчами для эффективности
                if len(batch) >= args.batch_size:
                    f.write('\n'.join(batch) + '\n')
                    lines_generated += len(batch)
                    batch = []
                    
                    if args.verbose and (i + 1) % (args.batch_size * 10) == 0:
                        elapsed = time.time() - start_time
                        rate = (i + 1) / elapsed if elapsed > 0 else 0
                        print(f"  Сгенерировано: {i + 1:,} строк ({rate:.0f} строк/сек)")
            
            # Записываем оставшиеся строки
            if batch:
                f.write('\n'.join(batch) + '\n')
                lines_generated += len(batch)
        
        elapsed_time = time.time() - start_time
        
        if args.verbose:
            print("-" * 50)
            print(f"Генерация завершена!")
            print(f"Всего строк: {lines_generated:,}")
            print(f"Затраченное время: {elapsed_time:.2f} секунд")
            print(f"Скорость: {lines_generated / elapsed_time:.0f} строк/сек" if elapsed_time > 0 else "Скорость: N/A")
            print(f"Файл сохранен: {output_file}")
        
    except KeyboardInterrupt:
        print(f"\nГенерация прервана пользователем.")
        print(f"Сгенерировано строк: {lines_generated:,}")
        if lines_generated > 0:
            print(f"Частичный результат сохранен в: {output_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при генерации логов: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()