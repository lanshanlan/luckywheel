-- ============================================
-- 心愿功能增量迁移脚本
-- 执行时间：2026.03.21
-- 说明：为奖品表添加心愿相关字段，创建心愿计数表
-- ============================================

USE lucky_wheel;

-- 1. 奖品表新增字段：奖品类型
ALTER TABLE prizes ADD COLUMN prize_type TINYINT DEFAULT 0 COMMENT '奖品类型：0-普通奖品，1-神秘大奖';

-- 2. 奖品表新增字段：心愿次数
ALTER TABLE prizes ADD COLUMN guarantee_count INT DEFAULT 0 COMMENT '心愿次数：0表示无心愿机制，>0表示抽N次必得';

-- 3. 创建心愿计数表
CREATE TABLE IF NOT EXISTS guarantee_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    user_id INT NOT NULL COMMENT '用户ID',
    activity_id INT NOT NULL COMMENT '活动ID',
    prize_id INT NOT NULL COMMENT '神秘大奖ID',
    current_count INT DEFAULT 0 COMMENT '当前已抽奖次数（未中该奖品）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE INDEX idx_user_activity_prize (user_id, activity_id, prize_id),
    CONSTRAINT fk_guarantee_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_guarantee_activity FOREIGN KEY (activity_id) REFERENCES activities(id),
    CONSTRAINT fk_guarantee_prize FOREIGN KEY (prize_id) REFERENCES prizes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='心愿计数表';