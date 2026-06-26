"""기상청 API Hub 지점정보(stn_inf) 조회 -> KMA/stn_info.csv

weather_daily_raw.csv 에 등장하는 관측소(STN) 번호에 위경도를 붙이기 위한 메타데이터.
ASOS(inf=SFC) 목록을 기본으로 하고, weather_daily_raw.csv에는 있지만 ASOS 목록에는
없는 관측소(AWS 보조관측소로 운영되는 경우)는 inf=AWS 목록에서 보충한다.
"""
import os
import urllib.request
import urllib.parse

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT, ".env")
WEATHER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather_daily_raw.csv")
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stn_info.csv")

API_URL = "https://apihub.kma.go.kr/api/typ01/url/stn_inf.php"
COLS = ["STN", "LON", "LAT", "STN_SP", "HT", "HT_PA", "HT_TA", "HT_WD", "HT_RN",
        "STN_AD", "STN_KO", "STN_EN", "FCT_ID", "LAW_ID", "BASIN", "LAW_ADDR"]


def load_api_key():
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            if line.startswith("KMA_API_KEY="):
                key = line.strip().split("=", 1)[1]
                if key:
                    return key
    raise RuntimeError("KMA_API_KEY not found in .env")


def fetch_stn_list(inf, api_key):
    params = {"inf": inf, "stn": "0", "authKey": api_key}
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        text = r.read().decode("cp949")

    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tokens = line.split(maxsplit=len(COLS) - 1)
        if len(tokens) == len(COLS):
            rows.append(tokens)
    return pd.DataFrame(rows, columns=COLS)


def main():
    api_key = load_api_key()
    needed_stn = set(pd.read_csv(WEATHER_PATH, usecols=["STN"])["STN"].unique())

    sfc = fetch_stn_list("SFC", api_key)
    have = set(sfc["STN"].astype(int))
    missing = needed_stn - have
    print(f"weather_daily_raw 관측소 {len(needed_stn)}개, SFC 목록 {len(have)}개, 부족 {len(missing)}개: {sorted(missing)}")

    if missing:
        aws = fetch_stn_list("AWS", api_key)
        supplement = aws[aws["STN"].astype(int).isin(missing)]
        print(f"  AWS 목록에서 {len(supplement)}개 보충")
        sfc = pd.concat([sfc, supplement], ignore_index=True)

    still_missing = needed_stn - set(sfc["STN"].astype(int))
    if still_missing:
        print(f"  여전히 메타데이터 없는 관측소: {sorted(still_missing)} (좌표 매칭에서 제외됨)")

    out = sfc[["STN", "STN_KO", "LAT", "LON"]].copy()
    out["STN"] = out["STN"].astype(int)
    out["LAT"] = out["LAT"].astype(float)
    out["LON"] = out["LON"].astype(float)
    out = out.drop_duplicates(subset=["STN"]).sort_values("STN").reset_index(drop=True)

    out.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n✓ 저장 완료: {OUT_PATH} ({len(out)}개 관측소)")


if __name__ == "__main__":
    main()
