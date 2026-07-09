# --- Unity Catalog ---
CATALOG = "dt4_team1_databricks"

# --- Blob Storage ---
BASE_PATH = "abfss://raw@dt4team1blob.dfs.core.windows.net/raw"
# --- Databricks Secret Scope --- 
SECRET_SCOPE = "dt4_team1_secrets"  # API Key, DB 연결 정보 등 모두 이 Scope에서 관리
 
# --- 보관 정책 ---
ARCHIVE_CONTAINER = "model-artifacts"
TARGET_TIER = "Cold"
DAYS_THRESHOLD = 1

# --- 지오 코딩 ---
KAKAO_API_KEY = "bac9e75e71e250e325b8a1a5963740d3" # 유출 금지..
 