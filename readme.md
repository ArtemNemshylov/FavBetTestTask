# 1. Клонувати репозиторій (якщо потрібно)
git clone git@github.com:ArtemNemshylov/FavBetTestTask.git

# 2. Створити віртуальне середовище
python3 -m venv .venv

# 3. Активувати середовище
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 4. Встановити залежності
pip install --upgrade pip

pip install -r requirements.txt

# 5. Замінити урл бд в src.storage.mongo_storage
    def __init__(self, mongo_uri="mongodb://mongo:27017", db_name="marathonbet", collection_name="events")
mongodb://mongo:27017 -> mongodb://localhost:27017

# 6. Запустити API
uvicorn src.api.main:app --reload

# 7. Запустити Streamlit UI
streamlit run src/ui/streamlit_app.py
