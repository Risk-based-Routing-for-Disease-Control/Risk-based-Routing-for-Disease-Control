"""Final/{시도}_위험라우팅_타임라인.csv를 합쳐 Final/전국_위험라우팅_타임라인.csv를 만든다.

- farm_source, date 컬럼은 제외한다 (date는 reference_date와 같은 값이라 중복).
- farm_county -> county로 이름을 바꾼다.
- 파일명에서 시/도명을 가져와 맨 앞에 city 컬럼으로 추가한다.
"""
import glob
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL_DIR = os.path.join(ROOT, "Final")
OUT_PATH = os.path.join(FINAL_DIR, "전국_위험라우팅_타임라인.csv")

DROP_COLS = ["farm_source", "date"]


def main():
    files = sorted(
        f
        for f in glob.glob(os.path.join(FINAL_DIR, "*_위험라우팅_타임라인.csv"))
        if not os.path.basename(f).startswith("전국_")
    )
    print(f"대상 파일 {len(files)}개")

    frames = []
    for f in files:
        province = os.path.basename(f).replace("_위험라우팅_타임라인.csv", "")
        df = pd.read_csv(f, encoding="utf-8-sig")
        df = df.drop(columns=DROP_COLS)
        df = df.rename(columns={"farm_county": "county"})
        df.insert(0, "city", province)
        frames.append(df)
        print(f"  {os.path.basename(f)}: {len(df)}행")

    merged = pd.concat(frames, ignore_index=True)
    merged.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n✓ 저장 완료: {OUT_PATH} ({len(merged)}행)")


if __name__ == "__main__":
    main()
