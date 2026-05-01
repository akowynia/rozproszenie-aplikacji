# URL Shortener - Rozproszony

Aplikacja do skracania URL podzielona na dwa niezależne serwisy z bazą danych PostgreSQL.

## Architektura
- **Write Service** (port 8001): Tworzenie i usuwanie skrótów.
- **Read Service** (port 8000): Przekierowania i informacje o kodach.
- **PostgreSQL**: Współdzielona baza danych.

## Uruchomienie (Docker)

To najszybsza metoda uruchomienia całego środowiska:

```bash
docker-compose up --build
```

Po uruchomieniu:
- Dokumentacja serwisu zapisu: `http://localhost:8001/docs`
- Dokumentacja serwisu odczytu: `http://localhost:8000/docs`

## Uruchomienie Lokalne (bez Dockera)

1. Wymagane zainstalowanie zależności:
```bash
pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy asyncpg
```

2. Konfiguracja bazy danych w `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
```

3. Uruchomienie serwisu zapisu:
```bash
uvicorn main_write:app --port 8001 --reload
```

4. Uruchomienie serwisu odczytu:
```bash
uvicorn main_read:app --port 8000 --reload
```
