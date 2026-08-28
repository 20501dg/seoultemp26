import streamlit as st
import csv
from datetime import date, datetime, timedelta

st.set_page_config(
page_title="서울 기온 랭킹",
page_icon="🌡️",
layout="centered"
)

st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: "Noto Sans KR", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(99,102,241,0.10), transparent 30%),
        radial-gradient(circle at 90% 10%, rgba(14,165,233,0.10), transparent 30%),
        #f7f8fc;
}

.block-container {
    max-width: 900px;
    padding-top: 40px;
    padding-bottom: 60px;
}

.hero {
    padding: 34px 30px;
    border-radius: 28px;
    background: linear-gradient(135deg, #111827, #334155);
    color: white;
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
    margin-bottom: 25px;
}

.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,0.12);
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 14px;
}

.hero h1 {
    margin: 0;
    font-size: 36px;
    font-weight: 900;
    letter-spacing: -1.5px;
}

.hero p {
    margin-top: 12px;
    color: #cbd5e1;
    line-height: 1.7;
}

.section-title {
    font-size: 20px;
    font-weight: 800;
    color: #111827;
    margin: 28px 0 12px;
}

.card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(15,23,42,0.06);
}

.big-temp {
    font-size: 48px;
    font-weight: 900;
    color: #111827;
    letter-spacing: -2px;
}

.rank-card {
    background: white;
    border-radius: 22px;
    padding: 24px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 10px 30px rgba(15,23,42,0.06);
}

.rank-title {
    color: #64748b;
    font-size: 14px;
    font-weight: 700;
}

.rank {
    font-size: 50px;
    font-weight: 900;
    color: #111827;
    margin-top: 5px;
}

.rank span {
    font-size: 20px;
}

.warm {
    background: linear-gradient(135deg, #fff7ed, #ffffff);
    border-color: #fed7aa;
}

.cold {
    background: linear-gradient(135deg, #eff6ff, #ffffff);
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
    border-radius: 15px;
    padding: 16px;
}

.info-label {
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
}

.info-value {
    font-size: 21px;
    font-weight: 800;
    color: #111827;
    margin-top: 5px;
}

.message {
    margin-top: 18px;
    padding: 18px;
    background: #eef2ff;
    border: 1px solid #c7d2fe;
    border-radius: 17px;
    color: #3730a3;
    line-height: 1.7;
}

.footer {
    text-align: center;
    margin-top: 35px;
    color: #94a3b8;
    font-size: 11px;
}

@media (max-width: 600px) {
    .block-container {
        padding: 20px 14px 40px;
    }

    .hero {
        padding: 26px 21px;
        border-radius: 22px;
    }

    .hero h1 {
        font-size: 28px;
    }

    .info-grid {
        grid-template-columns: 1fr;
    }

    .rank {
        font-size: 42px;
    }
}
</style>

""", unsafe_allow_html=True)

# ============================================================

# CSV 읽기

# ============================================================

@st.cache_data
def load_data():

```
data = {}

with open("seoul.csv", "r", encoding="utf-8-sig", newline="") as f:

    reader = csv.DictReader(f)

    for row in reader:

        raw_date = str(row.get("날짜", "")).strip()
        raw_temp = str(row.get("평균기온", "")).strip()

        if not raw_date or not raw_temp:
            continue

        try:
            d = datetime.strptime(
                raw_date,
                "%Y-%m-%d"
            ).date()

            temp = float(raw_temp)

        except (ValueError, TypeError):
            continue

        data[d] = temp

return dict(sorted(data.items()))
```

# ============================================================

# 기간 평균 계산

# ============================================================

def get_period(data, start_date, end_date):

```
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
```

# ============================================================

# 역사적 동일 기간 비교

# ============================================================

@st.cache_data
def calculate_ranking(data, start_date, end_date):

```
period_days = (end_date - start_date).days + 1

first_date = min(data.keys())
last_date = max(data.keys())

candidates = []

current_start = first_date

final_start = last_date - timedelta(days=period_days - 1)

while current_start <= final_start:

    current_end = current_start + timedelta(
        days=period_days - 1
    )

    values = []

    current = current_start
    complete = True

    while current <= current_end:

        if current not in data:
            complete = False
            break

        values.append(data[current])

        current += timedelta(days=1)

    if complete and len(values) == period_days:

        candidates.append({
            "start": current_start,
            "end": current_end,
            "avg": sum(values) / len(values)
        })

    current_start += timedelta(days=1)

selected = get_period(
    data,
    start_date,
    end_date
)

if selected is None or not candidates:
    return None

selected_avg = selected["avg"]

warm_rank = 1

cold_rank = 1

for item in candidates:

    if item["avg"] > selected_avg:
        warm_rank += 1

    if item["avg"] < selected_avg:
        cold_rank += 1

hottest = max(
    candidates,
    key=lambda x: x["avg"]
)

coldest = min(
    candidates,
    key=lambda x: x["avg"]
)

return {
    "selected": selected,
    "warm_rank": warm_rank,
    "cold_rank": cold_rank,
    "total": len(candidates),
    "hottest": hottest,
    "coldest": coldest
}
```

# ============================================================

# 날짜 표시

# ============================================================

def date_text(d):
return f"{d.year}.{d.month:02d}.{d.day:02d}"

def temp_text(t):
return f"{t:.1f}°C"

# ============================================================

# 데이터 불러오기

# ============================================================

try:

```
data = load_data()
```

except FileNotFoundError:

```
st.error(
    "❌ seoul.csv 파일을 찾을 수 없습니다.\n\n"
    "GitHub 저장소에서 main.py와 seoul.csv가 "
    "같은 폴더에 있는지 확인해주세요."
)

st.stop()
```

if not data:

```
st.error(
    "❌ seoul.csv에서 유효한 데이터를 찾지 못했습니다."
)

st.stop()
```

min_date = min(data.keys())
max_date = max(data.keys())

# ============================================================

# 화면 상단

# ============================================================

st.markdown("""

<div class="hero">

```
<div class="badge">
    SEOUL TEMPERATURE ARCHIVE
</div>

<h1>
    이 기간, 역대 몇 위일까?
</h1>

<p>
    서울의 과거 기온 데이터를 이용해
    선택한 기간이 역사적으로 얼마나 따뜻했거나
    추웠는지 확인해보세요.
</p>
```

</div>
""", unsafe_allow_html=True)

# ============================================================

# 날짜 선택

# ============================================================

st.markdown(
'<div class="section-title">📅 비교할 기간</div>',
unsafe_allow_html=True
)

selected_dates = st.date_input(
"시작일과 종료일을 선택하세요",
value=(
max(min_date, date(2025, 1, 1)),
max(min_date, date(2025, 1, 7))
),
min_value=min_date,
max_value=max_date,
format="YYYY-MM-DD",
label_visibility="collapsed"
)

if not isinstance(selected_dates, (tuple, list)):
st.info("달력에서 시작일과 종료일을 모두 선택해주세요.")
st.stop()

if len(selected_dates) != 2:
st.info("달력에서 시작일과 종료일을 모두 선택해주세요.")
st.stop()

start_date = selected_dates[0]
end_date = selected_dates[1]

if start_date > end_date:

```
start_date, end_date = end_date, start_date
```

# ============================================================

# 선택 기간 데이터 확인

# ============================================================

selected = get_period(
data,
start_date,
end_date
)

if selected is None:

```
st.warning(
    "⚠️ 선택한 기간 중 기온 데이터가 없는 날짜가 있습니다. "
    "다른 날짜를 선택해주세요."
)

st.stop()
```

# ============================================================

# 역사적 순위

# ============================================================

result = calculate_ranking(
data,
start_date,
end_date
)

if result is None:

```
st.warning(
    "⚠️ 선택한 기간을 역사 데이터와 비교할 수 없습니다."
)

st.stop()
```

days = selected["days"]
avg_temp = selected["avg"]
min_temp = selected["min"]
max_temp = selected["max"]

warm_rank = result["warm_rank"]
cold_rank = result["cold_rank"]
total = result["total"]

# ============================================================

# 선택 기간 결과

# ============================================================

st.markdown(
'<div class="section-title">🌡️ 선택한 기간</div>',
unsafe_allow_html=True
)

st.markdown(f"""

<div class="card">

```
<div style="color:#64748b;font-size:14px;font-weight:700;">
    {date_text(start_date)}
    —
    {date_text(end_date)}
    · {days}일
</div>

<div style="margin-top:15px;color:#64748b;font-size:14px;">
    기간 평균기온
</div>

<div class="big-temp">
    {temp_text(avg_temp)}
</div>

<div class="info-grid">

    <div class="info">
        <div class="info-label">
            평균기온
        </div>
        <div class="info-value">
            {temp_text(avg_temp)}
        </div>
    </div>

    <div class="info">
        <div class="info-label">
            기간 최저기온
        </div>
        <div class="info-value">
            {temp_text(min_temp)}
        </div>
    </div>

    <div class="info">
        <div class="info-label">
            기간 최고기온
        </div>
        <div class="info-value">
            {temp_text(max_temp)}
        </div>
    </div>

</div>
```

</div>
""", unsafe_allow_html=True)

# ============================================================

# 순위

# ============================================================

st.markdown(
'<div class="section-title">🏆 역대 순위</div>',
unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

```
st.markdown(f"""
<div class="rank-card warm">

    <div class="rank-title">
        🔥 따뜻한 기간 기준
    </div>

    <div class="rank">
        {warm_rank:,}<span>위</span>
    </div>

    <div style="color:#64748b;font-size:12px;">
        동일한 {days}일 기간
        {total:,}개 중
    </div>

</div>
""", unsafe_allow_html=True)
```

with col2:

```
st.markdown(f"""
<div class="rank-card cold">

    <div class="rank-title">
        ❄️ 추운 기간 기준
    </div>

    <div class="rank">
        {cold_rank:,}<span>위</span>
    </div>

    <div style="color:#64748b;font-size:12px;">
        동일한 {days}일 기간
        {total:,}개 중
    </div>

</div>
""", unsafe_allow_html=True)
```

# ============================================================

# 자동 해석

# ============================================================

if warm_rank <= max(1, int(total * 0.01)):

```
message = "🔥 역대급으로 매우 따뜻한 기간입니다."
```

elif warm_rank <= max(1, int(total * 0.05)):

```
message = "☀️ 역사적으로 상당히 따뜻한 기간입니다."
```

elif warm_rank <= max(1, int(total * 0.25)):

```
message = "🌤️ 평년보다 따뜻한 편에 속합니다."
```

elif warm_rank >= int(total * 0.75):

```
message = "🧊 역사적으로 꽤 추운 편에 속합니다."
```

else:

```
message = "🌡️ 역사적인 관점에서 중간 정도의 기온입니다."
```

st.markdown(f"""

<div class="message">

```
<strong>{message}</strong>
<br>

선택한 기간의 평균기온
<strong>{avg_temp:.1f}°C</strong>는

역대 동일한 길이의 기간
<strong>{total:,}개</strong>와 비교했을 때

따뜻한 순위
<strong>{warm_rank:,}위</strong>입니다.
```

</div>
""", unsafe_allow_html=True)

# ============================================================

# 역대 최고 / 최저

# ============================================================

st.markdown(
'<div class="section-title">📌 같은 기간 길이의 역대 기록</div>',
unsafe_allow_html=True
)

col1, col2 = st.columns(2)

hottest = result["hottest"]
coldest = result["coldest"]

with col1:

```
st.markdown(f"""
<div class="card">

    <div style="color:#64748b;font-size:14px;font-weight:700;">
        🔥 가장 따뜻했던 {days}일
    </div>

    <div class="big-temp">
        {hottest["avg"]:.1f}°C
    </div>

    <div style="color:#64748b;font-size:12px;">
        {date_text(hottest["start"])}
        —
        {date_text(hottest["end"])}
    </div>

</div>
""", unsafe_allow_html=True)
```

with col2:

```
st.markdown(f"""
<div class="card">

    <div style="color:#64748b;font-size:14px;font-weight:700;">
        ❄️ 가장 추웠던 {days}일
    </div>

    <div class="big-temp">
        {coldest["avg"]:.1f}°C
    </div>

    <div style="color:#64748b;font-size:12px;">
        {date_text(coldest["start"])}
        —
        {date_text(coldest["end"])}
    </div>

</div>
""", unsafe_allow_html=True)
```

# ============================================================

# 계산 방법

# ============================================================

st.markdown(f"""

<div class="message">

```
<strong>📊 어떻게 계산했나요?</strong>
<br><br>

선택한 기간이 <strong>{days}일</strong>이라면,
서울 기상 데이터에서 과거의 모든
<strong>연속 {days}일</strong> 기간을 찾아
평균기온을 계산합니다.

<br><br>

그 후 평균기온이 높은 순서대로 정렬하여
선택한 기간의 순위를 계산합니다.

<br><br>

데이터가 하나라도 빠져 있는 기간은
공정한 비교를 위해 제외합니다.
```

</div>
""", unsafe_allow_html=True)

# ============================================================

# Footer

# ============================================================

st.markdown(f"""

<div class="footer">

```
서울 기온 데이터 · {min_date.year}–{max_date.year}
· 유효 데이터 {len(data):,}일
```

</div>
""", unsafe_allow_html=True)
