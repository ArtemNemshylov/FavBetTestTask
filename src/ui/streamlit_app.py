import streamlit as st
import pandas as pd
import aiohttp
import asyncio
from datetime import datetime, timedelta, timezone

API_URL = "http://localhost:8000/events/by-range"
API_URL_HOURS = "http://localhost:8000/events/by-hours"

st.set_page_config(page_title="Marathonbet Results", layout="wide")
st.title("📊 Marathonbet Results Viewer")

# -- Select mode
mode = st.radio("🔄 Режим фільтрації", ["Абсолютний діапазон", "Останні N годин"], horizontal=True)

# -- Input fields
if mode == "Останні N годин":
    hours_back = st.slider("⏱️ Кількість годин назад", min_value=1, max_value=48, value=12)
    params = {"hours_back": str(hours_back)}
    endpoint = API_URL_HOURS

else:
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("📅 Від дати", format="YYYY.MM.DD")
    with col2:
        to_date = st.date_input("📅 До дати", format="YYYY.MM.DD")

    # Show info box (dismissable)
    if "show_info_box" not in st.session_state:
        st.session_state.show_info_box = True

    if st.session_state.show_info_box:
        with st.container():
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.info("📥 Якщо даних за вибраний діапазон немає в базі, вони будуть автоматично збережені. "
                        "Це не призведе до дублювання — лише нові дні буде дозавантажено.")
            with col2:
                if st.button("❌", key="dismiss_info_popup"):
                    st.session_state.show_info_box = False

    # Warning for long date range
    if (to_date - from_date).days > 31:
        st.warning("⚠️ Рекомендую обирати не більше 31 дня - може довго оброблюватись.")

# -- Fetch data
async def fetch_results(params: dict, endpoint: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, params=params) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())
            return await resp.json()

# -- Load button
if st.button("🔍 Завантажити результати"):
    if mode == "Абсолютний діапазон" and from_date > to_date:
        st.warning("⚠️ 'Від' дата має бути раніше або дорівнювати 'До' даті.")
    else:
        params = {}
        endpoint = API_URL

        if mode == "Останні N годин":
            params = {"hours_back": str(hours_back)}
            endpoint = API_URL_HOURS
        else:
            params = {
                "from_date": from_date.strftime("%Y.%m.%d"),
                "to_date": to_date.strftime("%Y.%m.%d")
            }

        with st.spinner("⏳ Отримання даних..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                data = loop.run_until_complete(fetch_results(params, endpoint))

                if not data.get("events"):
                    st.info("🚫 Дані за обраний період відсутні.")
                else:
                    df = pd.DataFrame(data["events"])
                    st.session_state["events_df"] = df
                    st.success(f"✅ Завантажено подій: {data['total']}")

            except Exception as e:
                st.error(f"❌ Помилка під час запиту: {str(e)}")

# -- Filters and Table
if "events_df" in st.session_state:
    df = st.session_state["events_df"]

    st.markdown("### 🔎 Фільтрація")

    col1, col2 = st.columns(2)
    with col1:
        sport_options = [""] + sorted(df["sport"].dropna().astype(str).unique())
        selected_sport = st.selectbox("🎽 Вид спорту", options=sport_options)
    with col2:
        tournament_options = [""] + sorted(df["tournament"].dropna().astype(str).unique())
        selected_tournament = st.selectbox("🏆 Турнір", options=tournament_options)

    filtered_df = df.copy()
    if selected_sport:
        filtered_df = filtered_df[filtered_df["sport"].astype(str) == selected_sport]
    if selected_tournament:
        filtered_df = filtered_df[filtered_df["tournament"].astype(str) == selected_tournament]

    st.markdown(f"#### 🎯 Результатів після фільтрації: {len(filtered_df)}")
    st.dataframe(filtered_df, use_container_width=True)
