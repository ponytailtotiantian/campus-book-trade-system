USE campus_book_trade;

-- 报告4：数据库安全策略
-- 目标：体现角色划分、最小权限原则和敏感数据保护思路。
-- 注意：以下用户仅用于课程设计演示，正式生产环境应使用更强密码并限制登录来源。

-- =========================
-- 一、创建演示用户
-- =========================

DROP USER IF EXISTS 'campus_readonly'@'localhost';
DROP USER IF EXISTS 'campus_app_rw'@'localhost';
DROP USER IF EXISTS 'campus_backup'@'localhost';

CREATE USER 'campus_readonly'@'localhost' IDENTIFIED BY 'Readonly@123456';
CREATE USER 'campus_app_rw'@'localhost' IDENTIFIED BY 'AppRw@123456';
CREATE USER 'campus_backup'@'localhost' IDENTIFIED BY 'Backup@123456';

-- =========================
-- 二、权限分配
-- =========================

-- 只读用户：适合报表查看、教师验收查询，不允许修改数据。
GRANT SELECT ON campus_book_trade.* TO 'campus_readonly'@'localhost';

-- 应用读写用户：只授予 Web 系统运行所需的 DML 权限，不授予 DROP、GRANT 等高危权限。
GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE
ON campus_book_trade.*
TO 'campus_app_rw'@'localhost';

-- 备份用户：用于 mysqldump 备份，授予读取、锁表、视图和触发器相关权限。
GRANT SELECT, SHOW VIEW, TRIGGER, LOCK TABLES
ON campus_book_trade.*
TO 'campus_backup'@'localhost';

FLUSH PRIVILEGES;

-- =========================
-- 三、权限验证语句
-- =========================

SHOW GRANTS FOR 'campus_readonly'@'localhost';
SHOW GRANTS FOR 'campus_app_rw'@'localhost';
SHOW GRANTS FOR 'campus_backup'@'localhost';

-- =========================
-- 四、敏感数据保护说明
-- =========================
-- 1. 用户密码字段 password_hash 只保存哈希值，不保存明文密码。
-- 2. 生产环境配置放在 .env 文件中，不提交到 GitHub。
-- 3. Web 层启用 Django CSRF 防护，生产环境 DEBUG=False。
-- 4. 数据库层通过 CHECK、UNIQUE、FOREIGN KEY 约束减少非法数据写入。
