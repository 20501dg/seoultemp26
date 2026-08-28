```python
import streamlit as st
import csv
from datetime import date, datetime, timedelta
from html import escape


# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="서울 기온 랭킹",
    page_icon="🌡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
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
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    .hero {
        padding: 34px 30px 30px 30px;
        border-radius: 28px;
        background: linear-gradient(135deg, #111827 0%, #1f2937 55%, #334155 100%);
        color: white;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
        margin-bottom: 24px;
    }

    .hero-badge {
        display: inline-block;
        padding: 6px 11px;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.15);
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 14px;
    }

    .hero h1 {
        margin: 0;
        font-size: 36px;
        line-height: 1.2;
        font-weight: 900;
        letter-spacing: -1.5px;
    }

    .hero p {
        margin: 12px 0 0 0;
        color: #cbd5e1;
        font-size: 15px;
        line-height: 1.7;
    }

    .section-title {
        font-size: 20px;
        font-weight: 800;
        color: #111827;
        margin: 28px 0 12px 2px;
        letter-spacing: -0.5px;
    }

    .result-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 24px;
        padding: 26px;
        box-shadow: 0 10px 30px rgba(15,23,42,0.06);
        margin-top: 18px;
    }

    .rank-label {
        color: #64748b;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .rank-number {
        font-size: 52px;
        line-height: 1;
        font-weight: 900;
        letter-spacing: -2px;
        color: #111827;
    }

    .rank-number span {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 0;
        margin-left: 5px;
    }

    .rank-desc {
        color: #64748b;
        font-size: 13px;
        margin-top: 9px;
    }

    .warm-box {
        background: linear-gradient(135deg, #fff7ed, #fff);
        border: 1px solid #fed7aa;
        border-radius: 20px;
        padding: 20px;
        height: 100%;
    }

    .cold-box {
        background: linear-gradient(135deg, #eff6ff, #fff);
        border: 1px solid #bfdbfe;
        border-radius: 20px;
        padding: 20px;
        height: 100%;
    }

    .box-title {
        font-size: 14px;
        font-weight: 800;
        color: #475569;
        margin-bottom: 7px;
    }

    .big-temp {
        font-size: 32px;
        font-weight: 900;
        color: #111827;
        letter-spacing: -1px;
    }

    .subtext {
        font-size: 12px;
        color: #64748b;
        margin-top: 5px;
    }

    .info-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 18px;
    }

    .info-card {
        background: #f8fafc;
        border-radius: 16px;
        padding: 17px;
        border: 1px solid #e2e8f0;
    }

    .info-card .label {
        color: #64748b;
        font-size: 12px;
        font-weight: 600;
    }

    .info-card .value {
        color: #0f172a;
        font-size: 22px;
        font-weight: 800;
        margin-top: 5px;
    }

    .percentile {
        margin-top: 20px;
        padding: 15px 17px;
        border-radius: 15px;
        background: #f8fafc;
        color: #334155;
        font-size: 13px;
        line-height: 1.7;
    }

    .highlight {
        font-weight: 800;
        color: #111827;
    }

    .method {
        margin-top: 25px;
        padding: 18px 20px;
        border-radius: 18px;
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        color: #3730a3;
        font-size: 13px;
        line-height: 1.7;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 11px;
        margin-top: 35px;
    }

    @media (max-width: 600px) {
        .block-container {
            padding: 1.2rem 1rem 3rem 1rem;
        }

        .hero {
            padding: 26px 22px;
            border-radius: 22px;
        }

        .hero h1 {
            font-size: 28px;
        }

        .rank-number {
            font-size: 43px;
        }

        .info-grid {
            grid-template-columns: 1fr;
        }
    }

    /* Streamlit 기본 요소 조금 정리 */
    div[data-testid="stDateInput"] {
        background: white;
        padding: 15px;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
    }

    button[kind="primary"] {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 데이터 읽기
# 추가 라이브러리 없이 Python 표준 csv 사용
# =========================================================

@st.cache_data
def load_data():
    records = []

    with open("seoul.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            raw_date = (row.get("날짜") or "").strip()
            raw_temp = (row.get("평균기온") or "").strip()

            if not raw_date or not raw_temp:
                continue

            try:
                # 날짜 앞의 탭이나 공백도 자동 제거
                d = datetime.strptime(raw_date, "%Y-%m-%d").date()
                temp = float(raw_temp)
            except (ValueError, TypeError):
                continue

            records.append((d, temp))

    records.sort(key=lambda x: x[0])

    # 날짜 중복 제거
    data = {}
    for d, temp in records:
        data[d] = temp

    return dict(sorted(data.items()))


# =========================================================
# 기간 평균 및 역사적 순위 계산
# =========================================================

@st.cache_data
def make_daily_series(data):
    """
    데이터 전체 기간을 날짜 단위로 만들고,
    결측일은 None으로 표시한다.
    """
    if not data:
        return [], [], [], []

    first_day = min(data.keys())
    last_day = max(data.keys())

    dates = []
    temps = []
    prefix_sum = [0.0]
    prefix_count = [0]

    current = first_day

    while current <= last_day:
        value = data.get(current)

        dates.append(current)
        temps.append(value)

        if value is None:
            prefix_sum.append(prefix_sum[-1])
            prefix_count.append(prefix_count[-1])
        else:
            prefix_sum.append(prefix_sum[-1] + value)
            prefix_count.append(prefix_count[-1] + 1)

        current += timedelta(days=1)

    return dates, temps, prefix_sum, prefix_count


def get_period_stats(data, start_date, end_date):
    values = []

    current = start_date

    while current <= end_date:
        value = data.get(current)

        if value is None:
            return None

        values.append(value)
        current += timedelta(days=1)

    if not values:
        return None

    return {
        "days": len(values),
        "avg": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
    }


def calculate_historical_ranks(data, start_date, end_date):
    """
    선택한 기간과 동일한 길이의 모든 연속 기간을 비교한다.

    예:
    10일을 선택하면 역사상 모든 '연속 10일' 기간의
    평균기온과 비교한다.

    결측치가 포함된 기간은 비교 대상에서 제외한다.
    """

    days = (end_date - start_date).days + 1

    dates, temps, prefix_sum, prefix_count = make_daily_series(data)

    if not dates or days <= 0 or days > len(dates):
        return None

    first = dates[0]
    last = dates[-1]

    candidates = []

    candidate_start = first
    last_start = last - timedelta(days=days - 1)

    while candidate_start <= last_start:
        candidate_end = candidate_start + timedelta(days=days - 1)

        start_index = (candidate_start - first).days
        end_index = (candidate_end - first).days

        count = prefix_count[end_index + 1] - prefix_count[start_index]

        # 해당 기간의 모든 날짜에 평균기온 데이터가 있어야 함
        if count == days:
            total = prefix_sum[end_index + 1] - prefix_sum[start_index]
            avg = total / days

            candidates.append(
                {
                    "start": candidate_start,
                    "end": candidate_end,
                    "avg": avg,
                }
            )

        candidate_start += timedelta(days=1)

    selected = get_period_stats(data, start_date, end_date)

    if selected is None or not candidates:
        return None

    selected_avg = selected["avg"]

    # 높은 평균기온부터 정렬
    warm_sorted = sorted(
        candidates,
        key=lambda x: x["avg"],
        reverse=True
    )

    # 낮은 평균기온부터 정렬
    cold_sorted = sorted(
        candidates,
        key=lambda x: x["avg"]
    )

    # 동점은 같은 순위
    warm_rank = 1 + sum(
        1 for x in candidates if x["avg"] > selected_avg
    )

    cold_rank = 1 + sum(
        1 for x in candidates if x["avg"] < selected_avg
    )

    total_periods = len(candidates)

    warm_percentile = (1 - (warm_rank - 1) / total_periods) * 100
    cold_percentile = (1 - (cold_rank - 1) / total_periods) * 100

    # 역대 최고/최저 기간
    hottest = warm_sorted[0]
    coldest = cold_sorted[0]

    return {
        "selected": selected,
        "warm_rank": warm_rank,
        "cold_rank": cold_rank,
        "total_periods": total_periods,
        "warm_percentile": warm_percentile,
        "cold_percentile": cold_percentile,
        "hottest": hottest,
        "coldest": coldest,
    }


# =========================================================
# 유틸
# =========================================================

def fmt_temp(value):
    return f"{value:.1f}°C"


def fmt_date(d):
    return f"{d.year}.{d.month:02d}.{d.day:02d}"


def fmt_rank(rank):
    return f"{rank:,}"


# =========================================================
# 데이터 로드
# =========================================================

try:
    data = load_data()
except FileNotFoundError:
    st.error(
        "seoul.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 반드시 seoul.csv를 넣어주세요."
    )
    st.stop()

if not data:
    st.error("seoul.csv에서 유효한 기온 데이터를 찾지 못했습니다.")
    st.stop()


min_date = min(data.keys())
max_date = max(data.keys())


# =========================================================
# Header
# =========================================================

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-badge">SEOUL TEMPERATURE ARCHIVE</div>
        <h1>이 기간, 역대 몇 위일까?</h1>
        <p>
            서울의 과거 기온 데이터를 바탕으로 선택한 기간이
            역사적으로 얼마나 따뜻했거나 추웠는지 비교합니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 날짜 선택
# =========================================================

st.markdown(
    '<div class="section-title">📅 비교할 기간을 선택하세요</div>',
    unsafe_allow_html=True,
)

default_start = date(2025, 1, 1)
default_end = date(2025, 1, 7)

# 데이터 범위 안으로 보정
if default_start < min_date:
    default_start = min_date

if default_end > max_date:
    default_end = max_date

selected_range = st.date_input(
    "시작일과 종료일",
    value=(default_start, default_end),
    min_value=min_date,
    max_value=max_date,
    format="YYYY-MM-DD",
    label_visibility="collapsed",
)


# =========================================================
# 선택값 확인
# =========================================================

if not isinstance(selected_range, (tuple, list)) or len(selected_range) != 2:
    st.info("달력에서 시작일과 종료일을 모두 선택해주세요.")
    st.stop()

start_date, end_date = selected_range

if start_date > end_date:
    start_date, end_date = end_date, start_date


# =========================================================
# 결과 계산
# =========================================================

selected_stats = get_period_stats(data, start_date, end_date)

if selected_stats is None:
    st.warning(
        "선택한 기간에 기온 데이터가 없는 날짜가 포함되어 있습니다. "
        "다른 기간을 선택해주세요."
    )
    st.stop()

result = calculate_historical_ranks(
    data,
    start_date,
    end_date,
)

if result is None:
    st.warning("선택한 기간을 역사 데이터와 비교할 수 없습니다.")
    st.stop()


days = selected_stats["days"]
avg_temp = selected_stats["avg"]
min_temp = selected_stats["min"]
max_temp = selected_stats["max"]

warm_rank = result["warm_rank"]
cold_rank = result["cold_rank"]
total_periods = result["total_periods"]


# =========================================================
# 선택 기간 요약
# =========================================================

st.markdown(
    '<div class="section-title">🌡️ 선택한 기간</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="result-card">
        <div class="rank-label">
            {escape(fmt_date(start_date))} — {escape(fmt_date(end_date))}
            · 총 {days}일
        </div>

        <div style="margin-top:10px;">
            <span style="font-size:14px;color:#64748b;font-weight:600;">
                기간 평균기온
            </span>
        </div>

        <div style="font-size:48px;font-weight:900;letter-spacing:-2px;color:#111827;">
            {fmt_temp(avg_temp)}
        </div>

        <div class="info-grid">
            <div class="info-card">
                <div class="label">평균기온</div>
                <div class="value">{fmt_temp(avg_temp)}</div>
            </div>

            <div class="info-card">
                <div class="label">기간 최저기온</div>
                <div class="value">{fmt_temp(min_temp)}</div>
            </div>

            <div class="info-card">
                <div class="label">기간 최고기온</div>
                <div class="value">{fmt_temp(max_temp)}</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 역사적 순위
# =========================================================

st.markdown(
    '<div class="section-title">🏆 역대 순위</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="warm-box">
            <div class="box-title">🔥 가장 따뜻한 기간 기준</div>
            <div class="rank-number">
                {fmt_rank(warm_rank)}<span>위</span>
            </div>
            <div class="rank-desc">
                역대 동일 기간 {total_periods:,}개 중
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="cold-box">
            <div class="box-title">❄️ 가장 추운 기간 기준</div>
            <div class="rank-number">
                {fmt_rank(cold_rank)}<span>위</span>
            </div>
            <div class="rank-desc">
                역대 동일 기간 {total_periods:,}개 중
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 해석
# =========================================================

if warm_rank <= max(1, int(total_periods * 0.01)):
    warm_message = "🔥 역대급으로 매우 따뜻한 기간입니다."
elif warm_rank <= max(1, int(total_periods * 0.05)):
    warm_message = "☀️ 역사적으로 상당히 따뜻한 기간입니다."
elif warm_rank <= max(1, int(total_periods * 0.25)):
    warm_message = "🌤️ 평년보다 따뜻한 편에 속합니다."
elif warm_rank >= int(total_periods * 0.75):
    warm_message = "🧊 역사적으로 꽤 추운 편에 속합니다."
else:
    warm_message = "🌡️ 역사적인 관점에서 중간 정도의 기온입니다."


st.markdown(
    f"""
    <div class="percentile">
        <span class="highlight">{warm_message}</span><br>
        선택한 기간의 평균기온은
        <span class="highlight">
        역대 동일 길이 기간 중 따뜻한 순위 {warm_rank:,}위
        </span>
        입니다.
        전체 비교 대상의 약
        <span class="highlight">{result["warm_percentile"]:.1f}%</span>
        지점에 해당합니다.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 역대 극값 기간
# =========================================================

hottest = result["hottest"]
coldest = result["coldest"]

st.markdown(
    '<div class="section-title">📌 같은 기간 길이의 역대 기록</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="result-card">
            <div class="rank-label">🔥 가장 따뜻했던 {days}일</div>
            <div class="big-temp">{hottest["avg"]:.1f}°C</div>
            <div class="subtext">
                {fmt_date(hottest["start"])}
                —
                {fmt_date(hottest["end"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="result-card">
            <div class="rank-label">❄️ 가장 추웠던 {days}일</div>
            <div class="big-temp">{coldest["avg"]:.1f}°C</div>
            <div class="subtext">
                {fmt_date(coldest["start"])}
                —
                {fmt_date(coldest["end"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 계산 방법
# =========================================================

st.markdown(
    f"""
    <div class="method">
        <strong>📊 순위 계산 방법</strong><br>
        선택한 기간이 <strong>{days}일</strong>이므로,
        서울 기상관측 데이터에서 과거의 모든
        <strong>연속 {days}일</strong> 기간을 찾아
        기간 평균기온을 비교했습니다.<br>
        기온 데이터가 하나라도 빠진 기간은 공정한 비교를 위해
        순위 계산에서 제외했습니다.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Footer
# =========================================================

st.markdown(
    f"""
    <div class="footer">
        서울 기온 데이터 · {min_date.year}–{max_date.year}
        · 총 {len(data):,}개 유효 일자
    </div>
    """,
    unsafe_allow_html=True,
)
```
