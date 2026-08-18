USE campus_book_trade;

-- 事务示例1：正常提交事务（购买出售书籍）
START TRANSACTION;

SELECT stock
FROM listing
WHERE listing_id = 8
FOR UPDATE;

UPDATE listing
SET stock = stock - 1
WHERE listing_id = 8
  AND stock > 0;

INSERT INTO orders (
    listing_id, buyer_id, seller_id, order_type, total_amount, status, created_at, remark
)
VALUES (
    8, 5, 8, 'SALE', 28.00, 'PICKUP_PENDING', NOW(), '事务示例：正常提交'
);

COMMIT;

-- 事务示例2：使用 SAVEPOINT 与 ROLLBACK
START TRANSACTION;

SAVEPOINT sp_before_demo;

SELECT stock
FROM listing
WHERE listing_id = 9
FOR UPDATE;

UPDATE listing
SET stock = stock - 1
WHERE listing_id = 9
  AND stock > 0;

INSERT INTO orders (
    listing_id, buyer_id, seller_id, order_type, total_amount, status, created_at, remark
)
VALUES (
    9, 6, 9, 'SALE', 15.00, 'PICKUP_PENDING', NOW(), '事务示例：后续回滚'
);

ROLLBACK TO sp_before_demo;

COMMIT;
