"""data/전국_농장현황.csv 의 축종명/상세구분을 livestock_codes.csv 기준으로 정규화한다.

livestock_codes.csv 에 있는 (축종명,상세구분) 매핑만 근거로 사용한다.
예: 축종명에 '산란계'처럼 사실은 상세구분 값이 들어간 경우 -> 축종명=닭, 상세구분=산란계로 정정.
테이블에 없는 용어(꿩, 타조, 관상조류, 오골계, 혼합축종 등)는 임의로 추측하지 않고 원본 값을 그대로 둔다.
"""
import os
import re
import collections

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODES_PATH = os.path.join(ROOT, "livestock_codes.csv")
CSV_PATH = os.path.join(ROOT, "data", "전국_농장현황.csv")

NOISE_TOKENS = {"가금"}  # 가금=가축 일반을 뜻하는 상위 범주어. 구체 축종명이 따로 있으면 무시한다.


def load_codes():
    codes = pd.read_csv(CODES_PATH)
    species_set = set(codes.loc[codes["상세구분"].isna(), "축종명"])
    detail_map = {}
    dup_details = set()
    for _, row in codes.iterrows():
        detail = row["상세구분"]
        if pd.isna(detail) or detail in ("비분류", "기타"):
            continue
        if detail in detail_map and detail_map[detail] != row["축종명"]:
            dup_details.add(detail)
        detail_map[detail] = row["축종명"]
    for d in dup_details:
        detail_map.pop(d, None)
    return species_set, detail_map


SPECIES_SET, DETAIL_MAP = load_codes()


def clean_text(t):
    if pd.isna(t):
        return None
    t = re.sub(r"\(.*?\)", "", str(t)).strip()
    return t or None


def resolve_token(t):
    """단일 토큰을 (축종명,상세구분) 으로 해석. 실패하면 None."""
    if t is None:
        return None
    if t in SPECIES_SET:
        return (t, None)
    if t in DETAIL_MAP:
        return (DETAIL_MAP[t], t)
    if t.endswith("업") and len(t) > 1:
        return resolve_token(t[:-1])
    return None


def split_tokens(t):
    return [p.strip() for p in re.split(r"[-+/,]", t) if p.strip()]


def resolve_combo(t):
    """콤보 문자열을 토큰으로 쪼개 전부 해석 가능하면 (species_set, detail_set) 반환, 아니면 None."""
    parts = [p for p in split_tokens(t) if p not in NOISE_TOKENS]
    if not parts:
        return None
    resolved = [resolve_token(p) for p in parts]
    if any(r is None for r in resolved):
        return None
    species = {r[0] for r in resolved}
    details = {r[1] for r in resolved if r[1]}
    return species, details


def resolve_row(a, b):
    """(축종명,상세구분) 원본 값을 받아 정정된 (축종명,상세구분)을 반환. 못 풀면 None (변경 없음)."""
    a_n = clean_text(a)
    b_n = clean_text(b)
    rb = resolve_token(b_n) if b_n else None

    if rb is not None:
        species, detail = rb
        ra = resolve_token(a_n) if a_n else None
        if ra is not None:
            if ra[0] != species:
                return None
            if ra[1] and detail and ra[1] != detail:
                return None
            if not detail and ra[1]:
                detail = ra[1]
        elif a_n and a_n not in NOISE_TOKENS:
            combo = resolve_combo(a_n)
            if combo is None:
                return None
            species_from_a, details_from_a = combo
            if species_from_a and species_from_a != {species}:
                return None
            if details_from_a:
                if detail:
                    if detail not in details_from_a:
                        return None
                elif len(details_from_a) == 1:
                    detail = next(iter(details_from_a))
                else:
                    return None
        return species, detail

    # b가 단독으로 해석되지 않으면 a,b 토큰을 모두 모아 일괄 해석
    tokens = []
    for raw in (a_n, b_n):
        if raw:
            for p in split_tokens(raw):
                if p not in NOISE_TOKENS and p not in tokens:
                    tokens.append(p)
    if not tokens:
        return None
    resolved = [resolve_token(t) for t in tokens]
    if any(r is None for r in resolved):
        return None
    species = {r[0] for r in resolved}
    details = {r[1] for r in resolved if r[1]}
    if len(species) != 1 or len(details) > 1:
        return None
    return next(iter(species)), (next(iter(details)) if details else None)


def main():
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

    changed = 0
    unresolved = collections.Counter()
    for idx, row in df.iterrows():
        a, b = row["축종명"], row["상세구분"]
        if pd.isna(a) and pd.isna(b):
            continue
        result = resolve_row(a, b)
        if result is None:
            unresolved[(a if pd.notna(a) else None, b if pd.notna(b) else None)] += 1
            continue
        species, detail = result
        if (a if pd.notna(a) else None) != species or (b if pd.notna(b) else None) != detail:
            df.at[idx, "축종명"] = species
            df.at[idx, "상세구분"] = detail
            changed += 1

    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")

    print(f"정정 {changed}건")
    print(f"\n해석 불가(원본 유지) {sum(unresolved.values())}건, 고유 조합 {len(unresolved)}개:")
    for (a, b), n in unresolved.most_common():
        print(f"  {n:5d}건  축종명={a!r:20}  상세구분={b!r}")


if __name__ == "__main__":
    main()
