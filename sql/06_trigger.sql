USE campus_book_trade;

DROP TRIGGER IF EXISTS trg_orders_after_insert_audit;
DROP TRIGGER IF EXISTS trg_review_after_insert_audit;

DELIMITER $$

-- 触发器1：订单创建后自动写入审计日志
CREATE TRIGGER trg_orders_after_insert_audit
AFTER INSERT ON orders
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (order_id, operator_id, action_type, action_detail)
    VALUES (
        NEW.order_id,
        NEW.buyer_id,
        'AUTO_CREATE_ORDER',
        CONCAT('系统自动记录：用户', NEW.buyer_id, '创建了订单', NEW.order_id)
    );
END$$

-- 触发器2：评价提交后自动写入审计日志
CREATE TRIGGER trg_review_after_insert_audit
AFTER INSERT ON review
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (order_id, operator_id, action_type, action_detail)
    VALUES (
        NEW.order_id,
        NEW.reviewer_id,
        'AUTO_CREATE_REVIEW',
        CONCAT('系统自动记录：用户', NEW.reviewer_id, '提交了订单', NEW.order_id, '的评价')
    );
END$$

DELIMITER ;
