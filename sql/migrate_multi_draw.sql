-- ============================================
-- 多次抽奖功能增量迁移脚本
-- 执行时间：2026.03.19
-- 说明：支持按天轮次抽奖功能
-- ============================================

USE lucky_wheel;

-- 1. 活动表新增字段：抽奖间隔天数
ALTER TABLE activities ADD COLUMN draw_interval_days INT DEFAULT 1 COMMENT '抽奖间隔天数';

-- 2. 抽奖记录表新增字段：轮次
ALTER TABLE lottery_records ADD COLUMN round_number INT DEFAULT 1 COMMENT '第几轮抽奖';

-- 3. 更新历史抽奖记录的轮次
UPDATE lottery_records SET round_number = 1 WHERE round_number IS NULL;