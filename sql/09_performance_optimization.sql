USE campus_book_trade;

-- 报告4：查询性能分析、索引设计与优化
-- 使用方式：
-- 1. 先执行本文件中的“优化前 EXPLAIN”截图。
-- 2. 再执行“创建索引”部分。
-- 3. 最后执行“优化后 EXPLAIN”截图，对比 type、key、rows、Extra 等字段。

-- =========================
-- 一、优化前 EXPLAIN
-- =========================

-- 查询1：图书/商品列表筛选，常用于首页与图书商品页
EXPLAIN
SELECT
    l.listing_id,
    l.listing_type,
    l.price,
    l.status,
    b.title,
    b.author,
    c.category_name,
    u.real_name AS seller_name
FROM listing l
JOIN book b ON l.book_id = b.book_id
JOIN book_category c ON b.category_id = c.category_id
JOIN `user` u ON l.seller_id = u.user_id
WHERE l.status = 'ON_SALE'
  AND l.listing_type = 'SALE'
  AND b.category_id = 1
ORDER BY l.price ASC, l.published_at DESC;

-- 查询2：用户订单列表，常用于个人中心查看买入/卖出订单
EXPLAIN
SELECT
    o.order_id,
    o.status,
    o.created_at,
    o.total_amount,
    b.title,
    buyer.real_name AS buyer_name,
    seller.real_name AS seller_name
FROM orders o
JOIN listing l ON o.listing_id = l.listing_id
JOIN book b ON l.book_id = b.book_id
JOIN `user` buyer ON o.buyer_id = buyer.user_id
JOIN `user` seller ON o.seller_id = seller.user_id
WHERE o.buyer_id = 2
  AND o.status IN ('PICKUP_PENDING', 'COMPLETED')
ORDER BY o.created_at DESC;

-- 查询3：自提记录查询，常用于查询自提码和自提状态
EXPLAIN
SELECT
    pr.pickup_code,
    pr.status,
    pr.scheduled_time,
    pr.picked_time,
    pp.name AS pickup_point_name,
    b.title
FROM pickup_record pr
JOIN pickup_point pp ON pr.pickup_point_id = pp.pickup_point_id
JOIN orders o ON pr.order_id = o.order_id
JOIN listing l ON o.listing_id = l.listing_id
JOIN book b ON l.book_id = b.book_id
WHERE pr.status = 'WAITING'
  AND pr.pickup_point_id = 1
ORDER BY pr.scheduled_time ASC;

-- =========================
-- 二、创建优化索引
-- =========================
-- 说明：
-- 1. MySQL 的外键列会自动生成部分索引，但不一定满足筛选 + 排序的复合查询。
-- 2. 以下索引面向高频查询字段：状态、类型、分类、用户、时间、自提点。
-- 3. 如果重复执行提示索引已存在，说明已经优化过，可跳过对应语句。

CREATE INDEX idx_listing_status_type_price_time
ON listing(status, listing_type, price, published_at);

CREATE INDEX idx_book_category_title
ON book(category_id, title);

CREATE INDEX idx_orders_buyer_status_time
ON orders(buyer_id, status, created_at);

CREATE INDEX idx_orders_seller_status_time
ON orders(seller_id, status, created_at);

CREATE INDEX idx_pickup_point_status_time
ON pickup_record(pickup_point_id, status, scheduled_time);

CREATE INDEX idx_audit_order_time
ON audit_log(order_id, created_at);

-- =========================
-- 三、优化后 EXPLAIN
-- =========================

EXPLAIN
SELECT
    l.listing_id,
    l.listing_type,
    l.price,
    l.status,
    b.title,
    b.author,
    c.category_name,
    u.real_name AS seller_name
FROM listing l
JOIN book b ON l.book_id = b.book_id
JOIN book_category c ON b.category_id = c.category_id
JOIN `user` u ON l.seller_id = u.user_id
WHERE l.status = 'ON_SALE'
  AND l.listing_type = 'SALE'
  AND b.category_id = 1
ORDER BY l.price ASC, l.published_at DESC;

EXPLAIN
SELECT
    o.order_id,
    o.status,
    o.created_at,
    o.total_amount,
    b.title,
    buyer.real_name AS buyer_name,
    seller.real_name AS seller_name
FROM orders o
JOIN listing l ON o.listing_id = l.listing_id
JOIN book b ON l.book_id = b.book_id
JOIN `user` buyer ON o.buyer_id = buyer.user_id
JOIN `user` seller ON o.seller_id = seller.user_id
WHERE o.buyer_id = 2
  AND o.status IN ('PICKUP_PENDING', 'COMPLETED')
ORDER BY o.created_at DESC;

EXPLAIN
SELECT
    pr.pickup_code,
    pr.status,
    pr.scheduled_time,
    pr.picked_time,
    pp.name AS pickup_point_name,
    b.title
FROM pickup_record pr
JOIN pickup_point pp ON pr.pickup_point_id = pp.pickup_point_id
JOIN orders o ON pr.order_id = o.order_id
JOIN listing l ON o.listing_id = l.listing_id
JOIN book b ON l.book_id = b.book_id
WHERE pr.status = 'WAITING'
  AND pr.pickup_point_id = 1
ORDER BY pr.scheduled_time ASC;
