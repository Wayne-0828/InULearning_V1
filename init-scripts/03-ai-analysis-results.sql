-- ===============================================
-- AI Analysis Results - PostgreSQL 初始化腳本
-- 目的: 建立 AI 生成分析結果的持久化資料表與索引
-- 表: ai_analysis_results
-- ===============================================

-- 建立 ai_analysis_results 表
CREATE TABLE IF NOT EXISTS ai_analysis_results (
    id UUID PRIMARY KEY,
    exercise_record_id UUID NOT NULL,
    status VARCHAR(32) NOT NULL,
    weakness_analysis TEXT NULL,
    learning_guidance TEXT NULL,
    error TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_ai_results_record_id ON ai_analysis_results(exercise_record_id);
CREATE INDEX IF NOT EXISTS idx_ai_results_created_at ON ai_analysis_results(created_at);

-- 觸發器函數: 自動更新 updated_at
CREATE OR REPLACE FUNCTION trg_ai_results_update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 綁定觸發器
DROP TRIGGER IF EXISTS trg_ai_results_set_updated_at ON ai_analysis_results;
CREATE TRIGGER trg_ai_results_set_updated_at
BEFORE UPDATE ON ai_analysis_results
FOR EACH ROW EXECUTE FUNCTION trg_ai_results_update_updated_at();

-- 可選外鍵（預設不加，避免跨服務耦合導致寫入失敗）
-- ALTER TABLE ai_analysis_results
--   ADD CONSTRAINT fk_ai_results_exercise_record
--   FOREIGN KEY (exercise_record_id) REFERENCES exercise_records(id) ON DELETE CASCADE;


