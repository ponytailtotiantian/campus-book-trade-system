
USE campus_book_trade;

INSERT INTO `user` (student_no, username, password_hash, real_name, phone, department, credit_score, role, status)
VALUES
('20230001', 'zhangsan', 'hash_zhangsan', '张三', '13800000001', '计算机学院', 100, 'USER', 'ACTIVE'),
('20230002', 'lisi', 'hash_lisi', '李四', '13800000002', '软件学院', 100, 'USER', 'ACTIVE'),
('20230003', 'wangwu', 'hash_wangwu', '王五', '13800000003', '数学学院', 95, 'USER', 'ACTIVE'),
('20230004', 'zhaoliu', 'hash_zhaoliu', '赵六', '13800000004', '外国语学院', 98, 'USER', 'ACTIVE'),
('admin0001', 'admin', 'hash_admin', '管理员', '13800000099', '信息中心', 100, 'ADMIN', 'ACTIVE');

INSERT INTO book_category (category_name, parent_id, sort_order, status)
VALUES
('教材', NULL, 1, 'ACTIVE'),
('考研', NULL, 2, 'ACTIVE'),
('编程', NULL, 3, 'ACTIVE'),
('文学', NULL, 4, 'ACTIVE');

INSERT INTO book_condition (condition_name, description)
VALUES
('全新', '几乎未使用'),
('九成新', '外观较新，少量使用痕迹'),
('八成新', '有正常使用痕迹'),
('有笔记', '书内有较多笔记'),
('轻微破损', '封面或边角有轻微破损');

INSERT INTO book (category_id, title, isbn, author, publisher, course_name, original_price, edition, publish_year)
VALUES
(1, '数据库系统概论', '9787302511054', '王珊', '高等教育出版社', '数据库系统', 59.80, '第6版', 2021),
(1, '计算机网络', '9787121381746', '谢希仁', '电子工业出版社', '计算机网络', 56.00, '第8版', 2020),
(1, '高等数学', '9787040396630', '同济大学数学系', '高等教育出版社', '高等数学', 62.50, '第7版', 2019),
(2, '考研英语词汇闪过', '9787519288886', '张国静', '世界图书出版公司', '考研英语', 49.80, '2024版', 2023),
(3, 'Python编程：从入门到实践', '9787115428028', 'Eric Matthes', '人民邮电出版社', 'Python程序设计', 89.00, '第2版', 2020),
(4, '活着', '9787506365437', '余华', '作家出版社', NULL, 39.00, '经典版', 2012);


INSERT INTO pickup_point (name, location, contact_phone, open_time, status)
VALUES
('图书馆东门自提点', '图书馆东门门口快递柜旁', '010-10000001', '09:00-18:00', 'ACTIVE'),
('宿舍A区驿站', '宿舍A区一号楼楼下', '010-10000002', '10:00-20:00', 'ACTIVE');

INSERT INTO listing (seller_id, book_id, condition_id, listing_type, price, stock, description, donation_note, status)
VALUES
(1, 1, 2, 'SALE', 25.00, 1, '数据库课教材，九成新，无明显破损', NULL, 'ON_SALE'),
(2, 2, 3, 'SALE', 20.00, 1, '计算机网络教材，八成新，有少量划线', NULL, 'ON_SALE'),
(3, 4, 1, 'SALE', 18.00, 1, '考研英语词汇书，基本全新', NULL, 'ON_SALE'),
(4, 5, 4, 'SALE', 35.00, 1, 'Python教材，书内有笔记，适合复习', NULL, 'ON_SALE'),
(1, 3, 2, 'DONATION', 0.00, 1, '高等数学教材，学完后免费送', '仅限校内自提，优先低年级同学', 'ON_SALE');


INSERT INTO orders (listing_id, buyer_id, seller_id, order_type, total_amount, status, created_at, remark)
VALUES
(1, 2, 1, 'SALE', 25.00, 'PICKUP_PENDING', NOW(), '买家已联系卖家，等待自提'),
(2, 3, 2, 'SALE', 20.00, 'COMPLETED', NOW(), '交易已完成'),
(5, 4, 1, 'DONATION', 0.00, 'PICKUP_PENDING', NOW(), '捐赠书籍已被领取，等待线下自提');


INSERT INTO pickup_record (order_id, pickup_point_id, pickup_code, scheduled_time, picked_time, status)
VALUES
(1, 1, 'PU20260709001', DATE_ADD(NOW(), INTERVAL 1 DAY), NULL, 'WAITING'),
(2, 2, 'PU20260709002', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY), 'FINISHED'),
(3, 1, 'PU20260709003', DATE_ADD(NOW(), INTERVAL 2 DAY), NULL, 'WAITING');


INSERT INTO review (order_id, reviewer_id, reviewee_id, rating, content)
VALUES
(2, 3, 2, 5, '卖家回复很快，书籍和描述一致，交易顺利完成。');


INSERT INTO audit_log (order_id, operator_id, action_type, action_detail)
VALUES
(1, 2, 'CREATE_ORDER', '买家李四创建订单，等待线下自提'),
(2, 2, 'COMPLETE_ORDER', '订单完成，买家已成功取书'),
(2, 3, 'CREATE_REVIEW', '买家王五完成评价，评分5分'),
(3, 4, 'CLAIM_DONATION', '买家赵六领取张三捐赠的高等数学教材，等待自提');
