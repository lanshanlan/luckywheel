-- 幸运轮盘抽奖系统数据库初始化脚本
-- MySQL 8.4 LTS

-- 创建数据库
CREATE DATABASE IF NOT EXISTS lucky_wheel DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE lucky_wheel;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    openid VARCHAR(64) NOT NULL UNIQUE COMMENT '微信用户唯一标识',
    nickname VARCHAR(64) COMMENT '昵称',
    avatar_url VARCHAR(255) COMMENT '头像地址',
    is_admin TINYINT DEFAULT 0 COMMENT '是否管理员：0-否，1-是',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_openid (openid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 活动表
CREATE TABLE IF NOT EXISTS activities (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    title VARCHAR(100) NOT NULL COMMENT '活动标题',
    description TEXT COMMENT '活动描述',
    status TINYINT DEFAULT 1 COMMENT '状态：0-未开始，1-进行中，2-已结束',
    start_time DATETIME COMMENT '开始时间',
    end_time DATETIME COMMENT '结束时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活动表';

-- 奖品表
CREATE TABLE IF NOT EXISTS prizes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    activity_id INT NOT NULL COMMENT '关联活动ID',
    name VARCHAR(100) NOT NULL COMMENT '奖品名称',
    image_url VARCHAR(255) COMMENT '奖品图片',
    probability DECIMAL(5,4) NOT NULL COMMENT '中奖概率（0-1）',
    stock INT DEFAULT 0 COMMENT '库存数量',
    sort_order INT DEFAULT 0 COMMENT '轮盘显示顺序',
    INDEX idx_activity (activity_id),
    CONSTRAINT fk_prize_activity FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='奖品表';

-- 抽奖记录表
CREATE TABLE IF NOT EXISTS lottery_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    user_id INT NOT NULL COMMENT '用户ID',
    activity_id INT NOT NULL COMMENT '活动ID',
    prize_id INT COMMENT '中奖奖品ID',
    is_won TINYINT DEFAULT 0 COMMENT '是否中奖：0-未中奖，1-中奖',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '抽奖时间',
    INDEX idx_user (user_id),
    INDEX idx_activity (activity_id),
    INDEX idx_created (created_at),
    CONSTRAINT fk_record_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_record_activity FOREIGN KEY (activity_id) REFERENCES activities(id),
    CONSTRAINT fk_record_prize FOREIGN KEY (prize_id) REFERENCES prizes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='抽奖记录表';

-- 插入测试数据

-- 测试管理员用户（开发环境使用）
INSERT INTO users (openid, nickname, is_admin) VALUES
('dev_test_openid_001', '开发测试用户', 1);

-- 测试活动
INSERT INTO activities (title, description, status, start_time, end_time) VALUES
('新年大抽奖', '新年幸运轮盘抽奖活动，丰厚奖品等你来拿！', 1, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY)),
('春节特惠抽奖', '春节限时抽奖活动', 1, NOW(), DATE_ADD(NOW(), INTERVAL 15 DAY));

-- 测试奖品（活动1）
INSERT INTO prizes (activity_id, name, probability, stock, sort_order) VALUES
(1, '一等奖：iPhone 15', 0.0100, 5, 1),
(1, '二等奖：iPad Air', 0.0200, 10, 2),
(1, '三等奖：AirPods', 0.0500, 20, 3),
(1, '四等奖：京东卡100元', 0.1000, 50, 4),
(1, '五等奖：优惠券50元', 0.2000, 100, 5),
(1, '谢谢参与', 0.6200, 10000, 6);

-- 测试奖品（活动2）
INSERT INTO prizes (activity_id, name, probability, stock, sort_order) VALUES
(2, '一等奖：小米手机', 0.0100, 3, 1),
(2, '二等奖：小米手表', 0.0300, 10, 2),
(2, '三等奖：小米手环', 0.0600, 30, 3),
(2, '谢谢参与', 0.9000, 5000, 4);