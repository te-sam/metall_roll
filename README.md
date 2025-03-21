# MetallRoll

### Компоненты
* Postgres 17

---
### Запуск 
Путь /metall_roll
```
Создайте файл .env-non-dev в корне проекта и добавьте в него следующие переменные:

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=metal_roll_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

```
Используйте команду 

docker compose up -d

```

### FastAPI app
Url : 
```
https://localhost:7777
```

### Postgres

Url : 
```
https://localhost:5432
```

| id  | length | width | created_at          | deleted_at          |
|-----|--------|-------|---------------------|---------------------|
| 1   | 10.5   | 2.3   | 2025-03-21 07:13:49 | NULL                |
| 2   | 12.0   | 2.5   | 2025-03-21 07:14:00 | NULL                |
| 3   | 8.7    | 1.8   | 2025-03-21 07:14:10 | 2025-03-21 07:15:00 |

---