"""ML/ML_{시도}_농장현황_{윈도우}.csv 파일들을 병합해 ML_전국_농장현황_{윈도우}.csv로 저장한다 (기존 파일 덮어씀).
윈도우는 6months/1year 각각의 1건 버전과, 조사날짜를 다 보존하는 alldates 버전 총 4가지를 처리한다."""
import glob
import os
import re
import pandas as pd

STANDARD_COLS = ["시군명", "농장명", "축종명", "상세구분", "사육두수(마리)", "소재지지번주소", "WGS84위도", "WGS84경도", "조사날짜", "감염날짜"]
WINDOWS = ["6months", "1year", "6months_alldates", "1year_alldates"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

for window in WINDOWS:
    national_name = f"ML_전국_농장현황_{window}.csv"
    frames = []
    for path in sorted(glob.glob(os.path.join(SCRIPT_DIR, f"ML_*_농장현황_{window}.csv"))):
        name = os.path.basename(path)
        if name == national_name:
            continue
        m = re.match(rf"ML_(.+)_농장현황_{window}\.csv$", name)
        province = m.group(1)
        df = pd.read_csv(path, encoding="utf-8-sig")
        df = df[STANDARD_COLS]
        df.insert(0, "시도명", province)
        frames.append(df)
        print(f"[{window}] {province}: {len(df)}건")

    national_df = pd.concat(frames, ignore_index=True)
    out_path = os.path.join(SCRIPT_DIR, national_name)
    national_df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"✓ [{window}] 합계: {len(national_df)}건 -> {out_path} 저장 완료")
    print(national_df["시도명"].value_counts())
    print()
