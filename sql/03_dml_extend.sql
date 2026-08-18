USE campus_book_trade;

-- 1. 补充用户数据（补足到 10 条）
INSERT INTO `user` (student_no, username, password_hash, real_name, phone, department, credit_score, role, status)
VALUES
('20230005', 'sunqiang', 'hash_sunqiang', '孙强', '13800000005', '物理学院', 96, 'USER', 'ACTIVE'),
('20230006', 'chenyu', 'hash_chenyu', '陈宇', '13800000006', '经济学院', 97, 'USER', 'ACTIVE'),
('20230007', 'linna', 'hash_linna', '林娜', '13800000007', '法学院', 99, 'USER', 'ACTIVE'),
('20230008', 'heming', 'hash_heming', '何明', '13800000008', '土木工程学院', 95, 'USER', 'ACTIVE'),
('20230009', 'xiaoyu', 'hash_xiaoyu', '肖雨', '13800000009', '新闻传播学院', 98, 'USER', 'ACTIVE');

-- 2. 补充图书类别（补足到 10 条）
INSERT INTO book_category (category_name, parent_id, sort_order, status)
VALUES
('教材-计算机', 1, 11, 'ACTIVE'),
('教材-数学', 1, 12, 'ACTIVE'),
('考研-英语', 2, 21, 'ACTIVE'),
('编程-Python', 3, 31, 'ACTIVE'),
('文学-小说', 4, 41, 'ACTIVE'),
('文学-散文', 4, 42, 'ACTIVE');

-- 3. 补充书籍成色（补足到 10 条）
INSERT INTO book_condition (condition_name, description)
VALUES
('七成新', '有一定使用痕迹但不影响阅读'),
('六成新', '封面和边角磨损较明显'),
('少量划线', '书内有少量重点划线'),
('封面折痕', '封面存在明显折痕'),
('内页整洁', '内页干净整洁，几乎无笔记');

-- 4. 补充图书数据（补足到 10 条）
INSERT INTO book (category_id, title, isbn, author, publisher, course_name, original_price, edition, publish_year)
VALUES
(5, '操作系统概念', '9787111213826', 'Abraham Silberschatz', '机械工业出版社', '操作系统', 88.00, '第9版', 2020),
(6, '线性代数', '9787040326217', '同济大学数学系', '高等教育出版社', '线性代数', 42.00, '第6版', 2018),
(8, '算法导论', '9787111407010', 'Thomas H. Cormen', '机械工业出版社', '算法设计', 128.00, '第3版', 2019),
(9, '人间失格', '9787544253996', '太宰治', '南海出版公司', NULL, 39.50, '经典版', 2011);

-- 5. 补充自提点（补足到 10 条）
INSERT INTO pickup_point (name, location, contact_phone, open_time, status)
VALUES
('教学楼A区服务点', '教学楼A区一层大厅', '010-10000003', '08:30-17:30', 'ACTIVE'),
('教学楼B区服务点', '教学楼B区门口值班室旁', '010-10000004', '08:30-17:30', 'ACTIVE'),
('图书馆西门自提点', '图书馆西门门岗旁', '010-10000005', '09:00-18:00', 'ACTIVE'),
('南门快递驿站', '学校南门快递综合服务站', '010-10000006', '09:00-20:00', 'ACTIVE'),
('北门学生服务站', '学校北门学生服务中心', '010-10000007', '10:00-19:00', 'ACTIVE'),
('一食堂服务台', '一食堂入口右侧服务台', '010-10000008', '11:00-19:00', 'ACTIVE'),
('二食堂服务台', '二食堂入口左侧服务台', '010-10000009', '11:00-19:00', 'ACTIVE'),
('宿舍B区驿站', '宿舍B区综合驿站', '010-10000010', '10:00-21:00', 'ACTIVE');

-- 6. 补充发布信息（补足到 10 条）
INSERT INTO listing (seller_id, book_id, condition_id, listing_type, price, stock, description, donation_note, status)
VALUES
(6, 7, 6, 'SALE', 22.00, 1, '操作系统教材，七成新，适合期末复习', NULL, 'ON_SALE'),
(7, 8, 7, 'DONATION', 0.00, 1, '线性代数教材，愿意免费送给需要的同学', '优先大一新生，校内自提', 'ON_SALE'),
(8, 9, 8, 'SALE', 28.00, 1, '算法导论，少量划线，不影响阅读', NULL, 'ON_SALE'),
(9, 10, 9, 'SALE', 15.00, 1, '人间失格，封面有折痕，适合课外阅读', NULL, 'ON_SALE'),
(10, 6, 10, 'SALE', 30.00, 1, '活着，内页整洁，保存较好', NULL, 'ON_SALE');

-- 7. 更新已有订单状态，形成更多已完成交易
UPDATE orders
SET status = 'COMPLETED',
    completed_at = NOW(),
    remark = '已补充为完成状态，用于评价与统计测试'
WHERE order_id IN (1, 3);

UPDATE pickup_record
SET status = 'FINISHED',
    picked_time = NOW()
WHERE order_id IN (1, 3);

UPDATE listing
SET status = 'SOLD'
WHERE listing_id IN (1, 2, 5);

-- 8. 补充订单数据（补足到 10 条）
INSERT INTO orders (listing_id, buyer_id, seller_id, order_type, total_amount, status, created_at, completed_at, remark)
VALUES
(3, 6, 3, 'SALE', 18.00, 'COMPLETED', NOW(), NOW(), '购买考研英语词汇书'),
(4, 7, 4, 'SALE', 35.00, 'COMPLETED', NOW(), NOW(), '购买 Python 教材'),
(6, 2, 6, 'SALE', 22.00, 'COMPLETED', NOW(), NOW(), '购买操作系统教材'),
(7, 3, 7, 'DONATION', 0.00, 'COMPLETED', NOW(), NOW(), '领取线性代数捐赠书籍'),
(8, 4, 8, 'SALE', 28.00, 'COMPLETED', NOW(), NOW(), '购买算法导论'),
(9, 1, 9, 'SALE', 15.00, 'COMPLETED', NOW(), NOW(), '购买人间失格'),
(10, 2, 10, 'SALE', 30.00, 'COMPLETED', NOW(), NOW(), '购买活着');

UPDATE listing
SET status = 'SOLD'
WHERE listing_id IN (3, 4, 6, 7, 8, 9, 10);

-- 9. 补充自提记录（补足到 10 条）
INSERT INTO pickup_record (order_id, pickup_point_id, pickup_code, scheduled_time, picked_time, status)
VALUES
(4, 3, 'PU20260807004', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY), 'FINISHED'),
(5, 4, 'PU20260807005', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY), 'FINISHED'),
(6, 5, 'PU20260807006', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY), 'FINISHED'),
(7, 6, 'PU20260807007', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY), 'FINISHED'),
(8, 7, 'PU20260807008', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY), 'FINISHED'),
(9, 8, 'PU20260807009', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY), 'FINISHED'),
(10, 9, 'PU20260807010', DATE_SUB(NOW(), INTERVAL 1 DAY), NOW(), 'FINISHED');

-- 10. 补充评价（补足到 10 条）
INSERT INTO review (order_id, reviewer_id, reviewee_id, rating, content)
VALUES
(1, 2, 1, 5, '教材保存较好，卖家沟通顺畅。'),
(3, 4, 1, 5, '捐赠流程很顺利，感谢分享教材。'),
(4, 6, 3, 4, '书籍整体不错，和描述基本一致。'),
(5, 7, 4, 5, 'Python 教材内容完整，适合复习。'),
(6, 2, 6, 5, '卖家发货很快，自提体验很好。'),
(7, 3, 7, 5, '捐赠很有意义，领取过程很方便。'),
(8, 4, 8, 4, '算法导论有少量划线，但不影响使用。'),
(9, 1, 9, 4, '价格合适，交易过程顺利。'),
(10, 2, 10, 5, '书籍整洁，卖家态度很好。');

-- 11. 补充审计日志（补足到 10 条以上）
INSERT INTO audit_log (order_id, operator_id, action_type, action_detail)
VALUES
(4, 6, 'CREATE_ORDER', '用户孙强创建购买考研英语词汇书的订单'),
(4, 6, 'COMPLETE_ORDER', '订单4已完成自提'),
(5, 7, 'CREATE_ORDER', '用户林娜创建购买 Python 教材的订单'),
(5, 7, 'COMPLETE_ORDER', '订单5已完成自提'),
(6, 2, 'CREATE_ORDER', '用户李四创建购买操作系统教材的订单'),
(7, 3, 'CLAIM_DONATION', '用户王五领取线性代数捐赠书籍'),
(8, 4, 'CREATE_ORDER', '用户赵六创建购买算法导论的订单'),
(9, 1, 'CREATE_ORDER', '用户张三创建购买人间失格的订单'),
(10, 2, 'CREATE_ORDER', '用户李四创建购买活着的订单');

-- 12. DML 中的 UPDATE 示例
UPDATE `user`
SET credit_score = credit_score + 1
WHERE user_id IN (1, 2, 3);

UPDATE pickup_point
SET open_time = '09:00-21:00'
WHERE pickup_point_id = 10;

-- 13. DML 中的 DELETE 示例（先插入测试日志再删除）
INSERT INTO audit_log (order_id, operator_id, action_type, action_detail)
VALUES (NULL, 5, 'TEMP_TEST', '临时测试日志，用于演示 DELETE 操作');

DELETE FROM audit_log
WHERE action_type = 'TEMP_TEST';
