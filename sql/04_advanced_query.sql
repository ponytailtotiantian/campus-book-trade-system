USE campus_book_trade;

-- 1. 查询所有发布信息的详细情况（多表连接）
SELECT
    l.listing_id,
    u.real_name AS seller_name,
    b.title,
    c.category_name,
    bc.condition_name,
    l.listing_type,
    l.price,
    l.status
FROM listing l
JOIN `user` u ON l.seller_id = u.user_id
JOIN book b ON l.book_id = b.book_id
JOIN book_category c ON b.category_id = c.category_id
JOIN book_condition bc ON l.condition_id = bc.condition_id
ORDER BY l.listing_id;

-- 2. 统计每个图书类别的图书数量和平均原价（聚合）
SELECT
    c.category_name,
    COUNT(b.book_id) AS book_count,
    ROUND(AVG(b.original_price), 2) AS avg_original_price
FROM book_category c
LEFT JOIN book b ON c.category_id = b.category_id
GROUP BY c.category_id, c.category_name
HAVING COUNT(b.book_id) > 0
ORDER BY book_count DESC, avg_original_price DESC;

-- 3. 统计每个用户作为卖家的已完成订单数和成交总额（多表 + 聚合）
SELECT
    u.user_id,
    u.real_name,
    COUNT(o.order_id) AS completed_order_count,
    ROUND(SUM(o.total_amount), 2) AS total_sales_amount
FROM `user` u
LEFT JOIN orders o
    ON u.user_id = o.seller_id
   AND o.status = 'COMPLETED'
GROUP BY u.user_id, u.real_name
ORDER BY total_sales_amount DESC, completed_order_count DESC;

-- 4. 查询所有自提完成的订单详情（多表连接）
SELECT
    pr.pickup_record_id,
    o.order_id,
    b.title,
    buyer.real_name AS buyer_name,
    seller.real_name AS seller_name,
    pp.name AS pickup_point_name,
    pr.pickup_code,
    pr.picked_time
FROM pickup_record pr
JOIN orders o ON pr.order_id = o.order_id
JOIN listing l ON o.listing_id = l.listing_id
JOIN book b ON l.book_id = b.book_id
JOIN `user` buyer ON o.buyer_id = buyer.user_id
JOIN `user` seller ON o.seller_id = seller.user_id
JOIN pickup_point pp ON pr.pickup_point_id = pp.pickup_point_id
WHERE pr.status = 'FINISHED'
ORDER BY pr.picked_time DESC;

-- 5. 查询发布过捐赠书籍的用户（子查询）
SELECT
    user_id,
    real_name,
    department
FROM `user`
WHERE user_id IN (
    SELECT seller_id
    FROM listing
    WHERE listing_type = 'DONATION'
)
ORDER BY user_id;

-- 6. 查询各类别中价格最高的出售发布（相关子查询）
SELECT
    c.category_name,
    b.title,
    l.price,
    u.real_name AS seller_name
FROM listing l
JOIN book b ON l.book_id = b.book_id
JOIN book_category c ON b.category_id = c.category_id
JOIN `user` u ON l.seller_id = u.user_id
WHERE l.listing_type = 'SALE'
  AND l.price = (
      SELECT MAX(l2.price)
      FROM listing l2
      JOIN book b2 ON l2.book_id = b2.book_id
      WHERE b2.category_id = b.category_id
        AND l2.listing_type = 'SALE'
  )
ORDER BY l.price DESC;

-- 7. 查询既买过书又卖过书的用户（EXISTS）
SELECT
    u.user_id,
    u.real_name,
    u.department
FROM `user` u
WHERE EXISTS (
    SELECT 1 FROM orders o1
    WHERE o1.buyer_id = u.user_id
)
AND EXISTS (
    SELECT 1 FROM orders o2
    WHERE o2.seller_id = u.user_id
)
ORDER BY u.user_id;

-- 8. 查询评价信息及平均评分（连接 + 聚合）
SELECT
    reviewee.user_id AS reviewee_id,
    reviewee.real_name AS reviewee_name,
    COUNT(r.review_id) AS review_count,
    ROUND(AVG(r.rating), 2) AS avg_rating
FROM review r
JOIN `user` reviewee ON r.reviewee_id = reviewee.user_id
GROUP BY reviewee.user_id, reviewee.real_name
ORDER BY avg_rating DESC, review_count DESC;
