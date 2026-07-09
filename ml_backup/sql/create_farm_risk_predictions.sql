
-- farm_risk_predictions
-- Supabase/PostgreSQL용 테이블 생성 SQL
-- Job2 최종 예측 결과 10개 컬럼을 snake_case로 저장

CREATE TABLE IF NOT EXISTS public.farm_risk_predictions (
    farm_id TEXT NOT NULL,
    risk_date DATE NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL,
    risk_level TEXT NOT NULL,
    model_version TEXT NOT NULL,
    last_updated TIMESTAMPTZ,
    risk_factors JSONB,
    prediction_batch_id TEXT NOT NULL,
    risk_rank BIGINT NOT NULL,
    is_top20_risk BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (farm_id, risk_date, model_version)
);

CREATE INDEX IF NOT EXISTS idx_farm_risk_predictions_risk_date
ON public.farm_risk_predictions (risk_date);

CREATE INDEX IF NOT EXISTS idx_farm_risk_predictions_risk_level
ON public.farm_risk_predictions (risk_level);

CREATE INDEX IF NOT EXISTS idx_farm_risk_predictions_top20
ON public.farm_risk_predictions (is_top20_risk);

CREATE INDEX IF NOT EXISTS idx_farm_risk_predictions_rank
ON public.farm_risk_predictions (risk_rank);
