USE campus_book_trade;

DROP PROCEDURE IF EXISTS proc_create_order_with_pickup;

DELIMITER $$

CREATE PROCEDURE proc_create_order_with_pickup(
    IN p_listing_id BIGINT,
    IN p_buyer_id BIGINT,
    IN p_pickup_point_id BIGINT,
    IN p_remark VARCHAR(255)
)
BEGIN
    DECLARE v_seller_id BIGINT;
    DECLARE v_price DECIMAL(10,2);
    DECLARE v_stock INT;
    DECLARE v_listing_type VARCHAR(20);
    DECLARE v_listing_status VARCHAR(20);
    DECLARE v_order_type VARCHAR(20);
    DECLARE v_total_amount DECIMAL(10,2);
    DECLARE v_order_id BIGINT;
    DECLARE v_pickup_code VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT seller_id, price, stock, listing_type, status
    INTO v_seller_id, v_price, v_stock, v_listing_type, v_listing_status
    FROM listing
    WHERE listing_id = p_listing_id
    FOR UPDATE;

    IF v_seller_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '发布信息不存在';
    END IF;

    IF p_buyer_id = v_seller_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '买家不能购买自己发布的书籍';
    END IF;

    IF v_listing_status <> 'ON_SALE' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '该发布信息当前不在售';
    END IF;

    IF v_stock <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '库存不足，无法创建订单';
    END IF;

    IF v_listing_type = 'DONATION' THEN
        SET v_order_type = 'DONATION';
        SET v_total_amount = 0.00;
    ELSE
        SET v_order_type = 'SALE';
        SET v_total_amount = v_price;
    END IF;

    INSERT INTO orders (
        listing_id, buyer_id, seller_id, order_type, total_amount, status, created_at, remark
    ) VALUES (
        p_listing_id, p_buyer_id, v_seller_id, v_order_type, v_total_amount, 'PICKUP_PENDING', NOW(), p_remark
    );

    SET v_order_id = LAST_INSERT_ID();

    UPDATE listing
    SET stock = stock - 1,
        status = CASE WHEN v_stock - 1 = 0 THEN 'SOLD' ELSE 'ON_SALE' END
    WHERE listing_id = p_listing_id;

    SET v_pickup_code = CONCAT('PU', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(v_order_id, 4, '0'));

    INSERT INTO pickup_record (
        order_id, pickup_point_id, pickup_code, scheduled_time, status
    ) VALUES (
        v_order_id, p_pickup_point_id, v_pickup_code, DATE_ADD(NOW(), INTERVAL 1 DAY), 'WAITING'
    );

    COMMIT;

    SELECT v_order_id AS created_order_id;
END$$

DELIMITER ;

-- 调用示例：
-- CALL proc_create_order_with_pickup(8, 5, 2, '通过存储过程创建订单');
