# Apache AirFlow

## Запуск в Docker с Apache Airflow

Проект включает Docker-конфигурацию для запуска Apache Airflow с автоматической генерацией логов через DAG.

### Структура Docker-проекта

```
.
├── Dockerfile                    # Docker образ с Airflow и log_generator.py
├── docker-compose.yml           # Docker Compose конфигурация
├── requirements.txt             # Python зависимости
├── scripts/
│   └── entrypoint.sh           # Скрипт инициализации Airflow
├── dags/
│   └── log_generator_dag.py    # DAG для автоматической генерации логов
├── log_generator.py            # Основной скрипт генератора логов
└── README.md                   # Документация
```

### Быстрый старт

1. **Сборка и запуск контейнеров:**
   ```bash
   docker-compose up -d --build
   ```

2. **Проверка статуса:**
   ```bash
   docker-compose ps
   ```

3. **Доступ к Airflow UI:**
   - Откройте браузер и перейдите по адресу: http://localhost:8080
   - Логин: `admin`
   - Пароль: `admin`

4. **Остановка контейнеров:**
   ```bash
   docker-compose down
   ```

### Мониторинг

- **Airflow UI**: http://localhost:8080
- **Flower (Celery monitoring)**: http://localhost:5555
- **Логи контейнеров**: `docker-compose logs -f [service_name]`

### Конфигурация базы данных

По умолчанию используется PostgreSQL с следующими параметрами:
- Хост: `postgres`
- Порт: `5432`
- База данных: `airflow`
- Пользователь: `airflow`
- Пароль: `airflow`

### Планируемое API для динамических данных

В будущем планируется добавить Python API для:
- Динамической настройки параметров генерации логов
- REST API для управления генерацией
- Веб-интерфейс для конфигурации
- Интеграция с внешними системами мониторинга
