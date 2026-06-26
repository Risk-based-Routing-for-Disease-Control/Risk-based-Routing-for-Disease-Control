"""기상청 API Hub ASOS 일자료(kma_sfcdd3) 조회 -> KMA/weather_daily_raw.csv

ML/ML_전국_농장현황_1year.csv 의 조사날짜마다 (조사날짜-30일 ~ 조사날짜) 구간의
전체 관측소(stn=0) 일자료를 모아 weather_daily_raw 테이블 스키마에 맞춰 저장한다.
"""
import os
import time
import urllib.request
import urllib.parse

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT, ".env")
FARM_PATH = os.path.join(ROOT, "ML", "ML_전국_농장현황_1year.csv")
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather_daily_raw.csv")

API_URL = "https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd3.php"

# kma_sfcdd3 응답의 실제 컬럼 순서 (응답 헤더가 3줄로 쪼개져 있어 파싱 대신 고정 순서로 매핑)
API_FIELD_ORDER = [
    "TM", "STN", "WS_AVG", "WR_DAY", "WD_MAX", "WS_MAX", "WS_MAX_TM",
    "WD_INS", "WS_INS", "WS_INS_TM",
    "TA_AVG", "TA_MAX", "TA_MAX_TM", "TA_MIN", "TA_MIN_TM",
    "TD_AVG", "TS_AVG", "TG_MIN",
    "HM_AVG", "HM_MIN", "HM_MIN_TM",
    "PV_AVG", "EV_S", "EV_L", "FG_DUR",
    "PA_AVG", "PS_AVG", "PS_MAX", "PS_MAX_TM", "PS_MIN", "PS_MIN_TM",
    "CA_TOT", "SS_DAY", "SS_DUR", "SS_CMB",
    "SI_DAY", "SI_60M_MAX", "SI_60M_MAX_TM",
    "RN_DAY", "RN_D99", "RN_DUR", "RN_60M_MAX", "RN_60M_MAX_TM",
    "RN_10M_MAX", "RN_10M_MAX_TM", "RN_POW_MAX", "RN_POW_MAX_TM",
    "SD_NEW", "SD_NEW_TM", "SD_MAX", "SD_MAX_TM",
    "TE_05", "TE_10", "TE_15", "TE_30", "TE_50",
]

TARGET_COLS = [  # weather_daily_raw 테이블 컬럼
    "TM", "STN", "TA_AVG", "TA_MAX", "TA_MAX_TM", "TA_MIN", "TA_MIN_TM",
    "TD_AVG", "TS_AVG", "TG_MIN",
    "RN_DAY", "RN_D99", "RN_DUR", "RN_60M_MAX", "RN_60M_MAX_TM",
    "RN_10M_MAX", "RN_10M_MAX_TM", "RN_POW_MAX", "RN_POW_MAX_TM",
    "SD_NEW", "SD_NEW_TM", "SD_MAX", "SD_MAX_TM",
    "WS_AVG", "WR_DAY", "WD_MAX", "WS_MAX", "WS_MAX_TM",
    "WD_INS", "WS_INS", "WS_INS_TM",
    "HM_AVG", "HM_MIN", "HM_MIN_TM",
    "PV_AVG", "PA_AVG", "PS_AVG", "PS_MAX", "PS_MAX_TM", "PS_MIN", "PS_MIN_TM",
    "SS_DAY", "SS_DUR", "SS_CMB",
    "SI_DAY", "SI_60M_MAX", "SI_60M_MAX_TM",
    "CA_TOT", "EV_S", "EV_L", "FG_DUR",
    "TE_05", "TE_10", "TE_15", "TE_30", "TE_50",
]
TM_FIELDS = [c for c in TARGET_COLS if c.endswith("_TM")]


def load_api_key():
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            if line.startswith("KMA_API_KEY="):
                key = line.strip().split("=", 1)[1]
                if key:
                    return key
    raise RuntimeError("KMA_API_KEY not found in .env")


def date_blocks():
    """조사날짜별 (조사날짜-30 ~ 조사날짜) 구간을 겹치는 것끼리 묶어 최소 호출 단위로 합친다."""
    df = pd.read_csv(FARM_PATH)
    dates = pd.to_datetime(df["조사날짜"]).drop_duplicates().sort_values()
    windows = sorted((d - pd.Timedelta(days=30), d) for d in dates)

    blocks = [windows[0]]
    for start, end in windows[1:]:
        last_start, last_end = blocks[-1]
        if start <= last_end + pd.Timedelta(days=1):
            blocks[-1] = (last_start, max(last_end, end))
        else:
            blocks.append((start, end))
    return blocks


def fetch_block(start, end, api_key):
    params = {
        "tm1": start.strftime("%Y%m%d"),
        "tm2": end.strftime("%Y%m%d"),
        "stn": "0",
        "help": "0",
        "authKey": api_key,
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=60) as r:
        text = r.read().decode("utf-8")

    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tokens = line.split()
        if len(tokens) == len(API_FIELD_ORDER):
            rows.append(tokens)

    return pd.DataFrame(rows, columns=API_FIELD_ORDER)


def main():
    api_key = load_api_key()
    blocks = date_blocks()
    print(f"{len(blocks)} date block(s) to fetch")

    parts = []
    for start, end in blocks:
        print(f"  fetching {start.date()} ~ {end.date()}")
        parts.append(fetch_block(start, end, api_key))
        time.sleep(0.2)

    df = pd.concat(parts, ignore_index=True)
    df = df.drop_duplicates(subset=["TM", "STN"])

    cols = [c for c in TARGET_COLS if c in df.columns]
    df = df[cols]

    df["TM"] = pd.to_datetime(df["TM"], format="%Y%m%d").dt.strftime("%Y-%m-%d")
    df["STN"] = df["STN"].astype(int)

    for c in cols:
        if c in ("TM", "STN") or c in TM_FIELDS:
            df[c] = df[c].replace("-9", pd.NA)
            continue
        df[c] = pd.to_numeric(df[c], errors="coerce")
        df.loc[df[c].isin([-9, -99, -999]), c] = pd.NA

    df = df.sort_values(["TM", "STN"]).reset_index(drop=True)
    df.insert(0, "weather_daily_id", range(1, len(df) + 1))
    df.to_csv(OUT_PATH, index=False)
    print(f"saved {len(df)} rows -> {OUT_PATH}")


if __name__ == "__main__":
    main()
