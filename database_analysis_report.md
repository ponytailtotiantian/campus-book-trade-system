# 校园二手书交易系统数据库分析报告

## 0. 分析范围与现状

- 分析对象：仓库 `sql/` 目录下的 `01_ddl.sql` 至 `08_transaction.sql`。
- 数据库：MySQL，库名为 `campus_book_trade`，字符集 `utf8mb4`。
- 当前仓库只有数据库脚本和需求文档，尚未看到 Django 应用代码。
- 本报告只做分析，不修改、删除或新增任何数据库脚本。

## 1. 数据库核心表

数据库共有 10 张核心表：

| 表名 | 业务含义 | 关键字段 |
|---|---|---|
| `user` | 用户、卖家、买家、管理员 | `student_no`、`username`、`password_hash`、`phone`、`credit_score`、`role`、`status` |
| `book_category` | 图书分类，支持父子分类 | `category_name`、`parent_id`、`sort_order`、`status` |
| `book_condition` | 图书成色/品相字典 | `condition_name`、`description` |
| `book` | 图书档案，不是某一个卖家的库存 | `category_id`、`title`、`isbn`、`author`、`publisher`、`original_price` |
| `pickup_point` | 自提点 | `name`、`location`、`contact_phone`、`open_time`、`status` |
| `listing` | 发布记录，即卖家上架的具体商品 | `seller_id`、`book_id`、`condition_id`、`listing_type`、`price`、`stock`、`status` |
| `orders` | 交易订单 | `listing_id`、`buyer_id`、`seller_id`、`order_type`、`total_amount`、`status` |
| `pickup_record` | 自提记录，一个订单最多一条 | `order_id`、`pickup_point_id`、`pickup_code`、`scheduled_time`、`picked_time`、`status` |
| `review` | 订单评价 | `order_id`、`reviewer_id`、`reviewee_id`、`rating`、`content` |
| `audit_log` | 操作审计日志 | `order_id`、`operator_id`、`action_type`、`action_detail` |

## 2. 表之间的关系

主要关系如下：

- `user` 与 `listing`：一个用户可以发布多条商品，`1 : N`。
- `book_category` 与 `book`：一个分类下有多本图书，`1 : N`。
- `book_category` 与自身：`parent_id` 自关联，支持多级分类，`1 : N`。
- `book` 与 `listing`：一本图书可以有多条发布记录，`1 : N`。
- `book_condition` 与 `listing`：一种成色可以对应多条发布记录，`1 : N`。
- `listing` 与 `orders`：一条发布记录可以产生多笔订单，`1 : N`。
- `user` 与 `orders`：一个用户作为买家或卖家都可以有多笔订单，`1 : N`；通过 `buyer_id`、`seller_id` 两个外键实现。
- `orders` 与 `pickup_record`：`pickup_record.order_id` 唯一，所以一个订单只有一条自提记录，`1 : 1`。
- `pickup_point` 与 `pickup_record`：一个自提点可以服务多条自提记录，`1 : N`。
- `orders` 与 `review`：`review.order_id` 唯一，所以一个订单只有一条评价，`1 : 1`。
- `user` 与 `review`：一个用户可以作为评价人或被评价人拥有多条评价，通过 `reviewer_id`、`reviewee_id` 两个外键实现。
- `orders` 与 `audit_log`：一个订单可以有多条日志，`1 : N`。
- `user` 与 `audit_log`：一个操作人可以产生多条日志，`1 : N`。

ER 关系概览：

```text
book_category --< book --< listing >-- book_condition
                              |
user --< listing               |
user --< orders <-- listing    |
user --< orders >-- listing    |
pickup_point --< pickup_record >-- orders
user --< review >-- orders
user --< audit_log >-- orders
```

## 3. 主键和外键

| 表名 | 主键 | 外键 | 其他重要约束 |
|---|---|---|---|
| `user` | `user_id` | 无 | `student_no`、`username`、`phone` 唯一；`credit_score >= 0`；`role`、`status` 有枚举校验 |
| `book_category` | `category_id` | `parent_id` 指向 `book_category.category_id` | `category_name` 唯一；`parent_id` 可空 |
| `book_condition` | `condition_id` | 无 | `condition_name` 唯一 |
| `book` | `book_id` | `category_id` 指向 `book_category.category_id` | `original_price >= 0`；`isbn`、`course_name` 等可空 |
| `pickup_point` | `pickup_point_id` | 无 | `name` 唯一；`status` 有枚举校验 |
| `listing` | `listing_id` | `seller_id` 指向 `user.user_id`；`book_id` 指向 `book.book_id`；`condition_id` 指向 `book_condition.condition_id` | `SALE` 时 `price >= 0`，`DONATION` 时 `price = 0`；`stock >= 0`；`status` 有枚举校验 |
| `orders` | `order_id` | `listing_id` 指向 `listing.listing_id`；`buyer_id`、`seller_id` 都指向 `user.user_id` | `SALE` 时 `total_amount >= 0`，`DONATION` 时 `total_amount = 0`；`status` 有枚举校验 |
| `pickup_record` | `pickup_record_id` | `order_id` 指向 `orders.order_id` 且唯一；`pickup_point_id` 指向 `pickup_point.pickup_point_id` | `pickup_code` 唯一；`status` 有枚举校验 |
| `review` | `review_id` | `order_id` 指向 `orders.order_id` 且唯一；`reviewer_id`、`reviewee_id` 都指向 `user.user_id` | `rating BETWEEN 1 AND 5` |
| `audit_log` | `audit_log_id` | `order_id` 指向 `orders.order_id` 且可空；`operator_id` 指向 `user.user_id` 且可空 | 无状态约束 |

注意：

- 所有表都使用 InnoDB，外键默认没有显式 `ON DELETE`，因此 MySQL 会采用默认的 `RESTRICT` 行为。
- 数据库没有强制“买家不能购买自己的商品”，也没有强制“评价人必须是订单参与方”，这些规则需要由 Django 或存储过程校验。
- 数据库没有强制“每个订单必须有自提记录”，`orders` 表本身不包含指向 `pickup_record` 的外键。

## 4. 商品发布流程

当前数据库没有提供“发布商品”的存储过程或触发器，因此发布流程由 Django 应用层控制，数据库只提供约束。

建议流程：

1. 校验卖家账号存在且 `status = 'ACTIVE'`，且不能发布不存在的用户。
2. 选择或创建图书档案 `book`：
   - 如果图书已存在，直接复用 `book.book_id`。
   - 如果不存在，插入 `book`，并校验 `category_id` 有效。
3. 选择有效的图书成色 `book_condition`。
4. 插入 `listing`：
   - `listing_type = 'SALE'` 时，`price >= 0`。
   - `listing_type = 'DONATION'` 时，`price = 0`，可填 `donation_note`。
   - `stock >= 0`。
   - 新发布默认 `status = 'ON_SALE'`。
   - `published_at`、`updated_at` 由数据库默认值或自动更新时间维护。
5. Django 应额外判断当前是否已有相同图书的重复在售发布；数据库没有唯一约束，因此不限制同一本书被多个用户或同一用户多次发布。

需要注意：`book` 是“图书档案”，`listing` 才是“某个卖家的在售商品”。同一本 `book` 可以有多条 `listing`，同一 `listing` 的库存由 `stock` 控制。

## 5. 订单状态流转

`orders.status` 允许的值：

| 状态 | 含义 |
|---|---|
| `PENDING` | 初始待确认/待处理 |
| `LOCKED` | 订单或库存被锁定 |
| `PICKUP_PENDING` | 已下单，等待线下自提 |
| `COMPLETED` | 已完成 |
| `CANCELLED` | 已取消 |

当前数据库没有触发器或检查约束强制状态机的合法流转，只有状态值枚举校验。也就是说，`PENDING -> COMPLETED` 这类非法跳转数据库不会直接拒绝，Django 必须实现状态机。

结合现有存储过程，推荐流转：

```text
PENDING -> LOCKED -> PICKUP_PENDING -> COMPLETED
                 \                    /
                  -----> CANCELLED <--
```

更具体的规则：

- 未确认订单可以取消：`PENDING -> CANCELLED`。
- 锁定后可以取消：`LOCKED -> CANCELLED`。
- 下单等待自提后仍可取消：`PICKUP_PENDING -> CANCELLED`，取消时应恢复库存并把发布状态恢复为 `ON_SALE`。
- 自提完成：`PICKUP_PENDING -> COMPLETED`，并写入 `completed_at`。
- `COMPLETED` 和 `CANCELLED` 都是终态，不应再流转。

`listing.status` 的状态值：

| 状态 | 含义 |
|---|---|
| `ON_SALE` | 正常在售 |
| `LOCKED` | 被锁定，不能继续下单 |
| `SOLD` | 已售出 |
| `OFF_SHELF` | 卖家下架 |

现有存储过程 `proc_create_order_with_pickup` 在下单时执行：

- 锁定 `listing` 行，防止并发超卖。
- 校验发布存在、买家不是卖家、`stock > 0`。
- 创建订单，状态直接为 `PICKUP_PENDING`。
- 库存减 1；如果减完后为 0，则 `listing.status = 'SOLD'`，否则保持 `ON_SALE`。
- 创建一条 `WAITING` 自提记录。

因此，在该存储过程被使用的前提下，正常下单流程不会出现 `PENDING` 状态；`PENDING`、`LOCKED` 更适合作为后续扩展或应用层自定义流程使用。

## 6. 自提流程

自提记录状态：

| 状态 | 含义 |
|---|---|
| `WAITING` | 等待取书 |
| `FINISHED` | 已完成取书 |
| `EXPIRED` | 已过期 |
| `CANCELLED` | 已取消 |

当前数据库提供了下单时自动创建自提记录的存储过程，但没有提供“完成自提”或“取消自提”的存储过程。

推荐流程：

1. 下单前选择 `status = 'ACTIVE'` 的自提点。
2. 调用 `proc_create_order_with_pickup`，由存储过程同时创建订单和 `pickup_record`。
3. 自提记录初始状态为 `WAITING`，`pickup_code` 唯一，默认 `scheduled_time` 为下单后一天。
4. 买家到自提点出示 `pickup_code`，工作人员确认后：
   - 将 `pickup_record.status` 更新为 `FINISHED`。
   - 写入 `picked_time = NOW()`。
   - 将对应订单更新为 `COMPLETED`，写入 `completed_at = NOW()`。
   - 这三个操作必须在同一个 Django 事务中完成。
5. 超时未取、取消订单时：
   - 将 `pickup_record.status` 更新为 `EXPIRED` 或 `CANCELLED`。
   - 将订单更新为 `CANCELLED`。
   - 如果库存已扣减，则恢复 `listing.stock`；如果发布状态被改为 `SOLD`，则恢复为 `ON_SALE` 或 `LOCKED`。

需要说明：`pickup_record.order_id` 唯一，所以一个订单只能有一条自提记录；Django 创建自提记录前应先检查是否已存在。

## 7. 评价流程

当前 `review` 表只允许一个订单一条评价，因为 `order_id` 有唯一约束。如果业务希望买卖双方互相评价，现有表结构无法直接支持，需要和数据库负责同学确认后另行设计；在此之前 Web 端应按“一个订单一条评价”实现。

推荐流程：

1. 只允许评价 `COMPLETED` 状态的订单。
2. 校验 `reviewer_id` 必须是订单的买家或卖家，`reviewee_id` 必须是订单的另一方；数据库没有这个约束，Django 必须校验。
3. 校验 `rating` 在 1 到 5 之间；数据库的 `CHECK` 会兜底。
4. 校验该订单尚未评价；数据库的 `order_id UNIQUE` 会兜底。
5. 插入 `review` 后，触发器 `trg_review_after_insert_audit` 会自动写入审计日志，Django 不需要重复写 `AUTO_CREATE_REVIEW`。
6. 当前数据库没有自动维护 `credit_score` 的触发器或存储过程；测试数据中信用分是直接 `UPDATE` 的。如果 Web 系统需要根据评价调整信用分，应由 Django 在事务中实现，并明确规则。

## 8. 已有的视图、触发器、存储过程、事务

### 视图

| 视图名 | 内容 |
|---|---|
| `v_listing_detail` | 发布信息详情：卖家、图书、分类、成色、价格、状态 |
| `v_order_detail` | 订单详情：订单类型、金额、状态、图书、买卖双方 |
| `v_pickup_detail` | 自提详情：自提点、取件码、时间、订单、图书、买家 |

三个视图都是只读查询视图，可直接作为 Django 中 `managed = False` 的模型使用。

### 触发器

| 触发器名 | 事件 | 行为 |
|---|---|---|
| `trg_orders_after_insert_audit` | `orders` 插入后 | 自动写入一条 `AUTO_CREATE_ORDER` 审计日志 |
| `trg_review_after_insert_audit` | `review` 插入后 | 自动写入一条 `AUTO_CREATE_REVIEW` 审计日志 |

### 存储过程

| 存储过程名 | 用途 |
|---|---|
| `proc_create_order_with_pickup` | 在一个事务内完成下单、扣库存、更新发布状态、生成自提码、创建自提记录 |

参数：

- `p_listing_id`：发布记录 ID。
- `p_buyer_id`：买家 ID。
- `p_pickup_point_id`：自提点 ID。
- `p_remark`：订单备注。

该存储过程内部使用 `SELECT ... FOR UPDATE` 锁定发布记录，并在异常时 `ROLLBACK`，是一个完整的事务单元。

### 事务

`08_transaction.sql` 只是两个演示脚本，不是数据库中的可调用对象：

- 示例 1：展示 `START TRANSACTION`、`FOR UPDATE`、扣库存、插入订单、`COMMIT`。
- 示例 2：展示 `SAVEPOINT`、`ROLLBACK TO` 的用法。

这两个示例不应被 Django 当作业务接口重复执行，Web 端应使用存储过程或 Django 自身的 `transaction.atomic` 实现等价逻辑。

## 9. 哪些数据库逻辑应在 Django 中直接调用，而不是重复实现

### 9.1 应直接使用数据库已有能力

1. **三个视图**
   - 列表页、详情页、统计页应读取 `v_listing_detail`、`v_order_detail`、`v_pickup_detail`。
   - Django 中使用 `managed = False` 的模型映射这些视图，只读使用，不执行迁移。

2. **下单存储过程 `proc_create_order_with_pickup`**
   - Web 端“下单并预约自提”应调用该存储过程，而不是用 Django ORM 分别插入订单、扣库存、生成自提记录。
   - 存储过程已经处理行锁、库存判断、库存扣减、订单创建、自提码生成和事务回滚，重复实现容易造成并发超卖或数据不一致。
   - 调用前 Django 仍应做业务预校验，例如发布状态必须是 `ON_SALE`、买家账号可用、自提点可用；这些校验存储过程没有完整覆盖。

3. **两个审计触发器**
   - 订单创建后的 `AUTO_CREATE_ORDER`、评价创建后的 `AUTO_CREATE_REVIEW` 已由触发器自动生成。
   - Django 不应在 ORM 中再次写入这两类日志，否则会产生重复审计记录。

4. **数据库约束和默认值**
   - 价格与类型一致性、评分范围、状态枚举、唯一键、时间戳默认值等由数据库兜底。
   - Django 可以做用户友好校验，但不应绕过或重复实现数据库层已经保证的约束。

### 9.2 应在 Django 中实现，因为数据库没有现成对象

1. **商品发布流程**
   - 图书选择/新建、分类校验、成色选择、发布记录插入、重复发布检查等目前没有存储过程，应由 Django 在 `transaction.atomic` 中实现。

2. **订单状态机**
   - `PENDING`、`LOCKED`、`PICKUP_PENDING`、`COMPLETED`、`CANCELLED` 的合法流转没有数据库约束，应由 Django 集中维护。
   - 对订单、发布记录使用 `select_for_update()` 防止并发取消、并发完成导致状态错乱。

3. **取消订单与库存恢复**
   - 存储过程没有提供取消逻辑，取消时恢复 `listing.stock` 和发布状态应由 Django 在事务中完成。

4. **完成自提**
   - 将 `pickup_record` 标记为 `FINISHED`、订单标记为 `COMPLETED` 没有存储过程，应由 Django 在事务中完成。

5. **自提过期处理**
   - 数据库没有调度任务或事件，超时未取需要由 Django 定时任务、管理命令或在查询时惰性处理。

6. **评价业务校验**
   - 校验订单已完成、评价人/被评价人是订单双方、一个订单只评价一次；除唯一约束外，其余规则需要 Django 实现。
   - 如果需要更新用户信用分，也应由 Django 定义并事务化，因为当前数据库没有对应触发器或过程。

7. **非自动审计日志**
   - 取消订单、完成自提、上下架、发布商品、信用分调整等动作没有触发器，Django 应在同一事务中写入 `audit_log`。

### 9.3 Django 与现有数据库配合时的底线

- 所有 10 张核心表和 3 个视图都用 `managed = False` 映射，避免 Django 迁移修改数据库。
- 不要运行会生成或执行 DDL 的迁移去改表、删表、加表。
- 不要用 ORM 重复实现 `proc_create_order_with_pickup` 已完成的下单/扣库存/自提记录逻辑。
- 如果 Web 功能与现有表结构冲突，优先用 Django 逻辑解决；确需改库时先提交方案，等待数据库负责人确认。

