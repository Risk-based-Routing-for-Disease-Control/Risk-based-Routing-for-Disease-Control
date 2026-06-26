"""Kakao 지오코딩 공용 함수. 주소 -> (lat, lon, 정밀도태그)."""
import os
import re
import time
import json
import urllib.request
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT, ".env")
CACHE_PATH = os.path.join(ROOT, "scripts", "geocode_cache.json")


def load_api_key():
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            if line.startswith("KAKAO_REST_API_KEY="):
                return line.strip().split("=", 1)[1]
    raise RuntimeError("KAKAO_REST_API_KEY not found in .env")


def kakao_request(url, query, api_key):
    qs = urllib.parse.urlencode({"query": query})
    req = urllib.request.Request(
        f"{url}?{qs}", headers={"Authorization": f"KakaoAK {api_key}"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def truncate_to_dong(address):
    """번지/필지/마스킹(***) 등 지번 상세부를 잘라내고 읍/면/동·리까지만 남긴다."""
    tokens = address.split()
    out = []
    for t in tokens:
        if re.search(r"[0-9*]", t) or t == "외":
            break
        out.append(t)
    return " ".join(out)


def truncate_to_single_parcel(address):
    """여러 필지/마스킹/부가설명이 붙은 주소에서 맨 앞 필지 하나만 남긴다."""
    address = re.sub(r"\(.*?\)", "", address)
    address = address.split(",")[0].strip()
    address = address.split("외")[0].strip()

    tokens = address.split()
    out = []
    have_parcel = False
    for t in tokens:
        if "*" in t:
            break
        has_digit = bool(re.search(r"[0-9]", t))
        if not have_parcel:
            out.append(t)
            if has_digit:
                have_parcel = True
            continue
        if has_digit and t.endswith("호"):
            out.append(t)
            break
        break
    return " ".join(out)


def try_geocode_once(address, api_key):
    try:
        data = kakao_request(
            "https://dapi.kakao.com/v2/local/search/address.json", address, api_key
        )
        docs = data.get("documents", [])
        if docs:
            d = docs[0]
            return float(d["y"]), float(d["x"]), "address"
    except Exception as e:
        print(f"  address API error for {address!r}: {e}")

    try:
        data = kakao_request(
            "https://dapi.kakao.com/v2/local/search/keyword.json", address, api_key
        )
        docs = data.get("documents", [])
        if docs:
            d = docs[0]
            return float(d["y"]), float(d["x"]), "keyword"
    except Exception as e:
        print(f"  keyword API error for {address!r}: {e}")

    return None, None, None


def truncate_to_town(dong_address):
    """리/동(자연마을명 등 비공식 지명 포함)을 떼고 읍/면 단위까지만 남긴다."""
    tokens = dong_address.split()
    if len(tokens) <= 2:
        return ""
    return " ".join(tokens[:-1])


def geocode(address, api_key):
    """원주소 -> 단일 필지(다중 필지/마스킹 제거) -> 읍/면/동·리 단위 -> 읍/면 단위 순으로 점점 뭉뚱그려 재시도.
    마지막 읍/면 단계는 자연마을명처럼 Kakao DB에 없는 비공식 지명을 위한 최종 fallback이다."""
    single = truncate_to_single_parcel(address)
    dong = truncate_to_dong(address)
    town = truncate_to_town(dong)

    tried = set()
    for cand, label in [
        (address, "exact_addr"),
        (single, "single_parcel"),
        (dong, "dong"),
        (town, "town"),
    ]:
        if not cand or cand in tried:
            continue
        tried.add(cand)
        lat, lon, source = try_geocode_once(cand, api_key)
        time.sleep(0.05)
        if lat is not None:
            suffix = "" if label == "exact_addr" else f"_{label}"
            return lat, lon, source + suffix

    return None, None, None


def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def geocode_addresses(addresses, api_key, cache):
    """addresses(유니크 목록)를 캐시에 채운다. 캐시는 in-place 갱신."""
    failed = []
    for i, addr in enumerate(addresses):
        if addr in cache and cache[addr]["lat"] is not None:
            continue
        lat, lon, source = geocode(addr, api_key)
        cache[addr] = {"lat": lat, "lon": lon, "source": source}
        if lat is None:
            failed.append(addr)
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(addresses)} done")
            save_cache(cache)
    save_cache(cache)
    return failed
