# AI_CONTEXT

本项目为数据库系统课程设计项目，项目名称固定为：

校园二手书交易与捐赠自提管理系统

## 当前数据库方案

核心表总数固定为 10 张：

1. `user`
2. `book_category`
3. `book_condition`
4. `book`
5. `listing`
6. `orders`
7. `pickup_point`
8. `pickup_record`
9. `review`
10. `audit_log`

## 已确定的业务规则

- 本项目支持二手书出售和书籍捐赠两类业务
- 捐赠功能不单独新建 `donation` 主表
- 捐赠通过 `listing.listing_type = 'DONATION'` 表示
- 捐赠订单通过 `orders.order_type = 'DONATION'` 表示
- 捐赠订单金额固定为 `0.00`
- 自提流程继续复用 `pickup_point` 和 `pickup_record`
- 评价和日志继续复用原有设计

## 已完成内容

- 需求分析
- 数据需求分析
- E-R 图
- DDL 脚本
- DML 脚本
- 本地 MySQL 环境验证

## AI 修改限制

任何 AI 在修改本项目之前，必须遵守以下限制：

- 不得更改项目名称
- 不得擅自增加或删除主表
- 不得将 10 张核心表改成其他数量
- 不得新增 `donation` 主表
- 不得随意改动 `sql/01_ddl.sql` 中已冻结的核心结构
- 任何结构性修改必须先说明影响，再由两位成员共同确认

## 推荐开发重点

优先完成数据库课程设计评分项：

- 查询 SQL
- 视图
- 索引和 EXPLAIN
- 存储过程
- 触发器
- 事务
- 权限管理
- 备份恢复
