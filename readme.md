

#  Marathonbet Results Tracker

Це система для асинхронного збору результатів з Marathonbet з можливістю перегляду через Streamlit-інтерфейс.

##  Можливості

- Вибір діапазону дат або останніх `N` годин
- Автоматичне дозавантаження відсутніх днів
- Streamlit UI з фільтрами
- FastAPI бекенд
- MongoDB як сховище
- Docker/Docker Compose підтримка

##  Запуск у Docker

### 1. Побудова

```bash
make build
```

### 2. Запуск

```bash
make up
```

- FastAPI: http://localhost:8000
- Streamlit: http://localhost:8501

### 3. Зупинка

```bash
make down
```

## 💻 Локальний запуск (без Docker)

```bash
git clone git@github.com:ArtemNemshylov/FavBetTestTask.git
cd FavBetTestTask

python3 -m venv .venv
source .venv/bin/activate        # або .venv\Scripts\activate на Windows

pip install --upgrade pip
pip install -r requirements.txt
```

У `src/storage/mongo_storage.py` змінити:
```python
mongo_uri="mongodb://localhost:27017"
```

Потім:
```bash
uvicorn src.api.main:app --reload
streamlit run src/ui/streamlit_app.py
```
