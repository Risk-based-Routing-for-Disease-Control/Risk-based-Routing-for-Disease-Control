"""ML/ML_{시도}_농장현황.csv 파일들을 병합해 ML_전국_농장현황.csv로 저장한다 (기존 파일 덮어씀)."""
import glob
import os
import re
import pandas as pd

STANDARD_COLS = ["시군명", "농장명", "축종명", "상세구분", "사육두수(마리)", "소재지지번주소", "WGS84위도", "WGS84경도", "조사날짜"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

frames = []
for path in sorted(glob.glob(os.path.join(SCRIPT_DIR, "ML_*_농장현황_1year.csv"))):
    name = os.path.basename(path)
    if name == "ML_전국_농장현황_1year.csv":
        continue
    m = re.match(r"ML_(.+)_농장현황_1year\.csv$", name)
    province = m.group(1)
    df = pd.read_csv(path, encoding="utf-8-sig")
    df = df[STANDARD_COLS]
    df.insert(0, "시도명", province)
    frames.append(df)
    print(f"{province}: {len(df)}건")

national_df = pd.concat(frames, ignore_index=True)
out_path = os.path.join(SCRIPT_DIR, "ML_전국_농장현황_1year.csv")
national_df.to_csv(out_path, index=False, encoding="utf-8")
print(f"\n✓ 합계: {len(national_df)}건 -> {out_path} 저장 완료")
print(national_df["시도명"].value_counts())
