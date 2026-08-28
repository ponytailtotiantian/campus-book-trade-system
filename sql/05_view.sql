USE campus_book_trade;

DROP VIEW IF EXISTS v_listing_detail;
DROP VIEW IF EXISTS v_order_detail;
DROP VIEW IF EXISTS v_pickup_detail;

-- 视图1：发布信息详情视图
CREATE VIEW v_listing_detail AS
SELECT
    l.listing_id,
    l.listing_type,
    l.price,
    l.stock,
    l.status AS listing_status,
    l.donation_note,
    u.user_id AS seller_id,
    u.real_name AS seller_name,
    u.department AS seller_department,
    b.book_id,
    b.title,
    b.author,
    b.publisher,
    c.category_name,
    bc.condition_name,
    l.published_at
FROM listing l
JOIN `user` u ON l.seller_id = u.user_id
JOIN book b ON l.book_id = b.book_id
JOIN book_category c ON b.category_id = c.category_id
JOIN book_condition bc ON l.condition_id = bc.condition_id;

-- 视图2：订单详情视图
CREATE VIEW v_order_detail AS
SELECT
    o.order_id,
    o.order_type,
    o.total_amount,
    o.status AS order_status,
    o.created_at,
    o.completed_at,
    b.title,
    l.listing_type,
    buyer.real_name AS buyer_name,
    seller.real_name AS seller_name,
    seller.department AS seller_department
FROM orders o
JOIN listing l ON o.listing_id = l.listing_id
JOIN book b ON l.book_id = b.book_id
JOIN `user` buyer ON o.buyer_id = buyer.user_id
JOIN `user` seller ON o.seller_id = seller.user_id;

-- 视图3：自提记录详情视图
CREATE VIEW v_pickup_detail AS
SELECT
    pr.pickup_record_id,
    pr.pickup_code,
    pr.status AS pickup_status,
    pr.scheduled_time,
    pr.picked_time,
    pp.name AS pickup_point_name,
    pp.location AS pickup_location,
    o.order_id,
    o.order_type,
    b.title,
    buyer.real_name AS buyer_name
FROM pickup_record pr
JOIN pickup_point pp ON pr.pickup_point_id = pp.pickup_point_id
JOIN orders o ON pr.order_id = o.order_id
JOIN listing l ON o.listing_id = l.listing_id
JOIN book b ON l.book_id = b.book_id
JOIN `user` buyer ON o.buyer_id = buyer.user_id;

-- 视图使用示例
SELECT * FROM v_listing_detail;
SELECT * FROM v_order_detail;
SELECT * FROM v_pickup_detail;
