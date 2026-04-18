# URL Shortener — projekt na zajęcia z Systemów Rozproszonych

Prosty serwis skracający adresy URL, przygotowany jako zadanie kursowe na przedmiot "Systemy Rozproszone".

Cel projektu
- Demonstracja podstawowych mechanizmów tworzenia prostego serwisu sieciowego.
- Omówienie aspektów przechowywania skróconych linków, obsługi żądań i zadania okresowego (czyszczenia danych).

Zawartość repozytorium
- `app/` — kod aplikacji (FastAPI)

Wymagania
- Python 3.10+ (zalecane)

Uruchomienie lokalne (zalecany, prosty sposób)
1. Utwórz i aktywuj środowisko wirtualne:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Zainstaluj zależności:

```bash
pip install -r requirements.txt
```

Jeżeli plik `requirements.txt` nie istnieje, zainstaluj minimalne pakiety:

```bash
pip install fastapi uvicorn pydantic httpx
```

3. Uruchom aplikację:

```bash
uvicorn app.main:app --reload
```

4. Interfejs API i dokumentacja dostępne są pod:

```
http://localhost:8000/docs
```

