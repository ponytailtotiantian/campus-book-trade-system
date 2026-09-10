# 性能优化、安全策略与备份恢复说明

本文档用于课程设计报告4配套说明，和仓库中的 SQL/脚本一一对应。

## 1. 查询性能分析

对应脚本：`sql/09_performance_optimization.sql`

该脚本包含 3 类高频查询：

- 图书/商品列表筛选：按发布状态、发布类型、图书分类、价格和发布时间筛选排序。
- 用户订单列表：按买家、订单状态、创建时间查询订单。
- 自提记录查询：按自提点、状态、预约时间查询自提记录。

建议截图方式：

- 先执行脚本中“一、优化前 EXPLAIN”的 3 条语句，截图保存执行计划。
- 再执行“二、创建优化索引”。
- 最后执行“三、优化后 EXPLAIN”，截图对比 `key`、`rows`、`Extra` 字段。

## 2. 索引设计与优化

新增索引及作用：

| 索引名 | 表 | 字段 | 作用 |
| --- | --- | --- | --- |
| `idx_listing_status_type_price_time` | `listing` | `status, listing_type, price, published_at` | 加速商品列表状态/类型筛选和价格排序 |
| `idx_book_category_title` | `book` | `category_id, title` | 加速分类浏览和按书名查询 |
| `idx_orders_buyer_status_time` | `orders` | `buyer_id, status, created_at` | 加速买家订单列表 |
| `idx_orders_seller_status_time` | `orders` | `seller_id, status, created_at` | 加速卖家订单列表 |
| `idx_pickup_point_status_time` | `pickup_record` | `pickup_point_id, status, scheduled_time` | 加速自提点待取记录查询 |
| `idx_audit_order_time` | `audit_log` | `order_id, created_at` | 加速订单日志追踪 |

优化前后对比可从以下角度说明：

- 优化前可能出现 `ALL` 全表扫描，`rows` 扫描行数较多。
- 优化后查询计划应优先使用对应复合索引，`key` 字段显示索引名。
- 对状态、用户、时间类字段建立复合索引，可以减少排序和过滤成本。

## 3. 数据库安全策略

对应脚本：`sql/10_security_strategy.sql`

安全设计包括：

- 创建 `campus_readonly` 只读用户，仅授予 `SELECT` 权限。
- 创建 `campus_app_rw` 应用读写用户，仅授予 `SELECT, INSERT, UPDATE, DELETE, EXECUTE`，不授予 `DROP`、`GRANT` 等高危权限。
- 创建 `campus_backup` 备份用户，仅授予备份所需的 `SELECT, SHOW VIEW, TRIGGER, LOCK TABLES`。
- 生产环境配置保存在 `.env`，不提交 GitHub。
- Django 生产环境 `DEBUG=False`，表单请求具备 CSRF 防护。
- 密码字段使用 `password_hash`，不保存明文密码。

## 4. 备份与恢复方案

对应脚本：

- `deploy/backup_database.sh`
- `deploy/restore_database.sh`

全量备份示例：

```bash
cd /opt/campus-book-trade-system
bash deploy/backup_database.sh
```

恢复示例：

```bash
cd /opt/campus-book-trade-system
bash deploy/restore_database.sh backups/campus_book_trade_20260910_100000.sql.gz
```

策略说明：

- 使用 `mysqldump --single-transaction` 做一致性全量备份。
- 备份包含表结构、数据、视图、触发器、存储过程。
- 备份文件保存到 `/opt/campus-book-trade-system/backups`，并使用 gzip 压缩。
- 课程演示中可截图展示备份文件生成、删除测试数据、执行恢复、查询数据恢复成功。
