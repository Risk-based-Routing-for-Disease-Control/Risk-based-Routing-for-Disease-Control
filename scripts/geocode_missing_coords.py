"""전국_최종감염농장.csv 의 위경도 결측 행을 farm_address 기준으로 Kakao 지오코딩 API를 통해 대략 채운다."""
import os

import pandas as pd

import geocode_lib as gl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "전국_최종감염농장.csv")


def main():
    api_key = gl.load_api_key()
    df = pd.read_csv(CSV_PATH)

    missing_mask = df["latitude"].isna() | df["longitude"].isna()
    addresses = df.loc[missing_mask, "farm_address"].dropna().unique().tolist()
    print(f"missing rows: {missing_mask.sum()}, unique addresses: {len(addresses)}")

    cache = gl.load_cache()
    failed = gl.geocode_addresses(addresses, api_key, cache)
    print(f"geocoded: {len(addresses) - len(failed)}, failed: {len(failed)}")
    for a in failed:
        print(" ", a)

    if "coord_precision" not in df.columns:
        df["coord_precision"] = "exact"

    filled = 0
    for idx in df.index[missing_mask]:
        addr = df.at[idx, "farm_address"]
        entry = cache.get(addr)
        if entry and entry["lat"] is not None:
            df.at[idx, "latitude"] = entry["lat"]
            df.at[idx, "longitude"] = entry["lon"]
            df.at[idx, "coord_precision"] = "approx_" + entry["source"]
            filled += 1

    print(f"filled {filled} / {missing_mask.sum()} rows")
    df.to_csv(CSV_PATH, index=False)
    print(f"saved to {CSV_PATH}")


if __name__ == "__main__":
    main()
