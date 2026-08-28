import streamlit as st
import csv
from datetime import datetime, timedelta

st.set_page_config(
    page_title="서울 기온 랭킹",
    page_icon="🌡️",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
}
.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}
.hero {
    padding: 32px;
    border-radius: 26px;
    background: linear-gradient(135deg, #111827, #334155);
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 15px 40px rgba(15,23,42,.15);
}
.hero h1 {
    margin: 0;
    font-size: 36px;
    font-weight: 900;
}
.hero p {
    color: #cbd5e1;
    line-height: 1.7;
}
.title {
    font-size: 20px;
    font-weight: 800;
    margin: 24px 0 12px;
}
.card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 8px 25px rgba(15,23,42,.06);
}
.temp {
    font-size: 46px;
    font-weight: 900;
}
.rank {
    font-size: 48px;
    font-weight: 900;
}
.small {
    color: #64748b;
    font-size: 13px;
}
.warm {
    background: linear-gradient(135deg, #fff7ed, white);
    border-color: #fed7aa;
}
.cold {
    background: linear-gradient(135deg, #eff6ff, white);
    border-color: #bfdbfe;
}
.info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 18px;
}
.info {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 15px;
}
.info-label {
    color: #64748b;
    font-size: 12px;
}
.info-value {
    font-size: 21px;
    font-weight: 800;
    margin-top: 5px;
}
.notice {
    margin-top: 18px;
    padding: 17px;
    border-radius: 16px;
    background: #eef2ff;
    border: 1px solid #c7d2fe;
    color: #3730a3;
    line-height: 1.7;
}
@media (max-width: 600px) {
    .hero h1 { font-size: 28px; }
    .hero { padding: 24px; }
    .info-grid { grid-template-columns: 1fr; }
    .rank { font-size: 40px; }
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    data = {}

    with open("seoul.csv", "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            raw_date = str(row.get("날짜", "")).strip()
            raw_temp = str(row.get("평균기온", "")).strip()

            if not raw_date or not raw_temp:
                continue

            try:
                d = datetime.strptime(raw_date, "%Y-%m-%d").date()
                temp = float(raw_temp)
            except (ValueError, TypeError):
                continue

            data[d] = temp

    return dict(sorted(data.items()))


def period_stats(data, start_date, end_date):
    values = []
    current = start_date

    while current <= end_date:
        if current not in data:
            return None
        values.append(data[current])
        current += timedelta(days=1)

    if not values:
        return None

    return {
        "days": len(values),
        "avg": sum(values) / len(values),
        "min": min(values),
        "max": max(values)
    }


@st.cache_data
def calculate_ranking(data, start_date, end_date):
    days = (end_date - start_date).days + 1
    first_date = min(data)
    last_date = max(data)

    candidates = []
    current_start = first_date
    last_start = last_date - timedelta(days=days - 1)

    while current_start <= last_start:
        current_end = current_start + timedelta(days=days - 1)
        values = []
        current = current_start
        complete = True

        while current <= current_end:
            if current not in data:
                complete = False
                break
            values.append(data[current])
            current += timedelta(days=1)

        if complete:
            candidates.append({
                "start": current_start,
                "end": current_end,
                "avg": sum(values) / len(values)
            })

        current_start += timedelta(days=1)

    selected = period_stats(data, start_date, end_date)

    if selected is None or not candidates:
        return None

    avg = selected["avg"]

    warm_rank = 1 + sum(x["avg"] > avg for x in candidates)
    cold_rank = 1 + sum(x["avg"] < avg for x in candidates)

    hottest = max(candidates, key=lambda x: x["avg"])
    coldest = min(candidates, key=lambda x: x["avg"])

    return {
        "selected": selected,
        "warm_rank": warm_rank,
        "cold_rank": cold_rank,
        "total": len(candidates),
        "hottest": hottest,
        "coldest": coldest
    }


def dtext(d):
    return f"{d.year}.{d.month:02d}.{d.day:02d}"


def ttext(x):
    return f"{x:.1f}°C"


try:
    data = load_data()
except FileNotFoundError:
    st.error("seoul.csv 파일을 찾을 수 없습니다. main.py와 같은 폴더에 넣어주세요.")
    st.stop()

if not data:
    st.error("seoul.csv에서 유효한 데이터를 찾지 못했습니다.")
    st.stop()

min_date = min(data)
max_date = max(data)

st.markdown("""
<div class="hero">
    <div style="font-size:12px;font-weight:800;margin-bottom:12px;">
        SEOUL TEMPERATURE ARCHIVE
    </div>
    <h1>이 기간, 역대 몇 위일까?</h1>
    <p>
        서울의 과거 기온 데이터를 비교해 선택한 기간이
        역사적으로 얼마나 따뜻했거나 추웠는지 확인해보세요.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📅 비교할 기간</div>', unsafe_allow_html=True)

default_start = max(min_date, datetime(2025, 1, 1).date())
default_end = min(max_date, default_start + timedelta(days=6))

selected_dates = st.date_input(
    "시작일과 종료일",
    value=(default_start, default_end),
    min_value=min_date,
    max_value=max_date,
    format="YYYY-MM-DD",
    label_visibility="collapsed"
)

if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
    st.info("달력에서 시작일과 종료일을 모두 선택해주세요.")
    st.stop()

start_date, end_date = selected_dates

if start_date > end_date:
    start_date, end_date = end_date, start_date

selected = period_stats(data, start_date, end_date)

if selected is None:
    st.warning("선택한 기간에 기온 데이터가 없는 날짜가 포함되어 있습니다.")
    st.stop()

result = calculate_ranking(data, start_date, end_date)

if result is None:
    st.warning("선택한 기간을 역사 데이터와 비교할 수 없습니다.")
    st.stop()

days = selected["days"]
avg_temp = selected["avg"]

st.markdown('<div class="title">🌡️ 선택한 기간</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="card">
    <div class="small">{dtext(start_date)} — {dtext(end_date)} · {days}일</div>
    <div class="small" style="margin-top:15px;">기간 평균기온</div>
    <div class="temp">{ttext(avg_temp)}</div>

    <div class="info-grid">
        <div class="info">
            <div class="info-label">평균기온</div>
            <div class="info-value">{ttext(avg_temp)}</div>
        </div>
        <div class="info">
            <div class="info-label">기간 최저기온</div>
            <div class="info-value">{ttext(selected["min"])}</div>
        </div>
        <div class="info">
            <div class="info-label">기간 최고기온</div>
            <div class="info-value">{ttext(selected["max"])}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🏆 역대 순위</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    st.markdown(f"""
    <div class="card warm">
        <div class="small">🔥 따뜻한 기간 기준</div>
        <div class="rank">{result["warm_rank"]:,}<span style="font-size:20px;">위</span></div>
        <div class="small">동일한 {days}일 기간 {result["total"]:,}개 중</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card cold">
        <div class="small">❄️ 추운 기간 기준</div>
        <div class="rank">{result["cold_rank"]:,}<span style="font-size:20px;">위</span></div>
        <div class="small">동일한 {days}일 기간 {result["total"]:,}개 중</div>
    </div>
    """, unsafe_allow_html=True)

total = result["total"]

if result["warm_rank"] <= max(1, int(total * 0.01)):
    message = "🔥 역대급으로 매우 따뜻한 기간입니다."
elif result["warm_rank"] <= max(1, int(total * 0.05)):
    message = "☀️ 역사적으로 상당히 따뜻한 기간입니다."
elif result["warm_rank"] <= max(1, int(total * 0.25)):
    message = "🌤️ 평년보다 따뜻한 편에 속합니다."
elif result["warm_rank"] >= int(total * 0.75):
    message = "🧊 역사적으로 꽤 추운 편에 속합니다."
else:
    message = "🌡️ 역사적인 관점에서 중간 정도의 기온입니다."

st.markdown(f"""
<div class="notice">
    <strong>{message}</strong><br>
    선택한 {days}일의 평균기온은 역대 동일한 길이의 기간 중
    <strong>{result["warm_rank"]:,}위</strong>입니다.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📌 같은 기간 길이의 역대 기록</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    h = result["hottest"]
    st.markdown(f"""
    <div class="card">
        <div class="small">🔥 가장 따뜻했던 {days}일</div>
        <div class="temp">{h["avg"]:.1f}°C</div>
        <div class="small">{dtext(h["start"])} — {dtext(h["end"])}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    c = result["coldest"]
    st.markdown(f"""
    <div class="card">
        <div class="small">❄️ 가장 추웠던 {days}일</div>
        <div class="temp">{c["avg"]:.1f}°C</div>
        <div class="small">{dtext(c["start"])} — {dtext(c["end"])}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="notice">
    <strong>📊 계산 방법</strong><br>
    선택한 기간이 {days}일이면 과거의 모든 연속 {days}일 기간을 찾아
    평균기온을 계산합니다. 평균기온이 높은 순서와 낮은 순서로 각각
    순위를 계산합니다. 기온 데이터가 하나라도 없는 기간은 비교에서 제외합니다.
</div>
""", unsafe_allow_html=True)

st.markdown(
    f'<div style="text-align:center;color:#94a3b8;font-size:11px;margin-top:30px;">'
    f'서울 기온 데이터 · {min_date.year}–{max_date.year} · 유효 데이터 {len(data):,}일'
    f'</div>',
    unsafe_allow_html=True
)
