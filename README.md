# URL Shortener - Rozproszony (Cassandra)

Aplikacja do skracania URL podzielona na dwa niezależne serwisy, wykorzystująca rozproszoną bazę danych **Apache Cassandra** działającą w dwuwęzłowym klastrze.

## Architektura
- **Write Service** (port 8001): Tworzenie i usuwanie skrótów URL.
- **Read Service** (port 8000): Przekierowania i pobieranie metadanych o kodach.
- **Klaster Cassandra (2 węzły)**:
  - `cassandra-seed` (port 9042): Węzeł rozruchowy (punkt kontaktowy).
  - `cassandra-node`: Węzeł roboczy, synchronizujący stan klastra poprzez protokół *Gossip*.
  - **Automatyczne usuwanie:** Wykorzystuje natywny mechanizm Cassandra TTL (`USING TTL`) do samoczynnego usuwania wygasłych skrótów bezpośrednio na poziomie bazy danych.

## Uruchomienie (Docker)

To najszybsza metoda uruchomienia całego rozproszonego środowiska:

```bash
docker compose up --build -d
```

> **Uwaga:** Kontenery klastra bazy danych potrzebują około 30–45 sekund na pełny start i synchronizację. Serwisy aplikacji posiadają wbudowany mechanizm prób ponownego połączenia (*retry*) i automatycznie zaczną działać, gdy klaster będzie gotowy.

### Weryfikacja stanu klastra
Możesz sprawdzić poprawność synchronizacji i działania węzłów bezpośrednio w klastrze za pomocą komendy:

```bash
docker exec -it cassandra-seed nodetool status
```

Oczekiwany rezultat powinien pokazać oba węzły w stanie `UN` (Up/Normal):
```text
Datacenter: datacenter1
=======================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address     Load       Tokens  Owns (effective)  Host ID                               Rack
UN  172.20.0.2  105.12 KiB  256     100.0%            a3c61d5f-d890-482a-a92c-e1bc17676e10  rack1
UN  172.20.0.3  105.12 KiB  256     100.0%            b1c23d4e-d901-492b-b92c-e2bc27677e20  rack1
```

Po uruchomieniu:
- Dokumentacja serwisu zapisu: `http://localhost:8001/docs`
- Dokumentacja serwisu odczytu: `http://localhost:8000/docs`

## Uruchomienie Lokalne (bez Dockera)

1. Wymagane zainstalowanie zależności:
```bash
pip install fastapi uvicorn pydantic pydantic-settings cassandra-driver
```

2. Konfiguracja parametrów w pliku `.env`:
```env
CASSANDRA_HOSTS=localhost
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE=url_shortener
```

3. Uruchomienie serwisu zapisu:
```bash
uvicorn main_write:app --port 8001 --reload
```

4. Uruchomienie serwisu odczytu:
```bash
uvicorn main_read:app --port 8000 --reload
```
