# Django Web 系统架构设计

## 0. 设计原则与参考项目借鉴

### 0.1 设计原则

- MySQL 必须继续使用现有 `campus_book_trade` 数据库。
- 不重新设计数据库，不删除现有 SQL，不破坏现有触发器、视图、存储过程和事务。
- Django 使用 `managed = False` 映射现有表和视图，所有迁移只保留空迁移或不使用 Django 迁移修改现有表。
- 参考项目只借鉴代码组织方式和 UI 风格，不复制参考项目的数据库结构。
- 不新增需要新建表才能实现的功能，例如购物车、收藏夹、站内消息、通用评论、在线支付流水等。

### 0.2 从参考项目借鉴什么

- `Second_Hand_bookstore`：借鉴用户端商城式组织方式，包括首页、图书列表、图书详情、登录注册、个人中心、发布图书、我的发布等页面结构，以及 Bootstrap 风格的用户界面。
- `ruyun_library`：借鉴前后台分离的模块组织方式，包括前台列表/详情/录入，后台查询/新增/修改/删除/统计的页面习惯，以及管理端不依赖 Django 默认后台的展示方式。
- 不借鉴 `Second_Hand_bookstore` 的 SQLite、收藏、联系页面等需要新表的结构；不借鉴 `ruyun_library` 的 `t_Book`、`t_BookType` 等表结构。

## 1. Django 项目目录结构

```text
campus-book-trade-system-main/
├─ manage.py
├─ requirements.txt
├─ .env.example
├─ config/                    # Django 项目配置
│  ├─ settings/
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ dev.py
│  │  └─ prod.py
│  ├─ urls.py
│  ├─ asgi.py
│  └─ wsgi.py
├─ apps/
│  ├─ accounts/               # 用户、登录、注册、个人中心
│  ├─ catalog/                # 图书、分类、成色、自提点等基础数据
│  ├─ marketplace/            # 发布、商品浏览、搜索、卖家商品管理
│  ├─ trade/                  # 订单与审计日志
│  ├─ pickup/                 # 自提记录与自提流程
│  ├─ reviews/                # 评价流程
│  ├─ admin_dashboard/        # 管理员页面
│  └─ common/                 # 公共工具、装饰器、分页、上下文处理
├─ templates/
│  ├─ base.html
│  ├─ partials/
│  ├─ accounts/
│  ├─ catalog/
│  ├─ marketplace/
│  ├─ trade/
│  ├─ pickup/
│  ├─ reviews/
│  └─ admin/
├─ static/
│  ├─ css/
│  ├─ js/
│  └─ images/
├─ media/                     # 仅用于后续可能的非数据库文件，不建新表
└─ sql/                       # 保持现有 SQL 不变
```

建议项目配置放在 `config/`，业务代码按 App 放在 `apps/`。`sql/` 保持原样，不作为 Django 迁移来源。

## 2. App 划分

| App | 职责 | 对应现有表 |
|---|---|---|
| `accounts` | 自定义用户认证、注册、登录、个人资料、密码修改 | `user` |
| `catalog` | 图书档案、分类、成色、自提点等基础数据维护 | `book`、`book_category`、`book_condition`、`pickup_point` |
| `marketplace` | 商品发布、浏览、搜索、详情、上下架、卖家商品管理 | `listing` |
| `trade` | 订单创建、订单状态机、订单列表、取消订单、审计日志 | `orders`、`audit_log` |
| `pickup` | 自提码、自提记录、完成自提、过期/取消处理 | `pickup_record` |
| `reviews` | 订单评价、评价校验、评价列表 | `review` |
| `admin_dashboard` | 管理端页面、统计、运营操作入口 | 使用各 App 的模型和现有视图 |
| `common` | 公共表单、装饰器、分页、状态码常量、服务层工具 | 无独立表 |

模型建议按 App 归位，但所有模型必须显式设置 `db_table` 指向现有表名，并且 `Meta.managed = False`。

## 3. URL 设计

### 3.1 公开页面

| URL | 方法 | 功能 |
|---|---|---|
| `/` | GET | 首页，展示在售商品、分类入口 |
| `/listings/` | GET | 商品列表、搜索、筛选、分页 |
| `/listings/<listing_id>/` | GET | 商品详情 |
| `/books/<book_id>/` | GET | 图书档案页，展示同一本书的多条发布 |
| `/accounts/register/` | GET/POST | 用户注册 |
| `/accounts/login/` | GET/POST | 用户登录 |
| `/accounts/logout/` | POST | 退出登录 |

### 3.2 买家/卖家页面

| URL | 方法 | 功能 |
|---|---|---|
| `/accounts/profile/` | GET/POST | 个人资料 |
| `/accounts/password/change/` | GET/POST | 修改密码 |
| `/me/listings/` | GET | 我发布的商品 |
| `/me/orders/` | GET | 我的订单，按买家/卖家切换 |
| `/listings/new/` | GET/POST | 发布商品 |
| `/listings/<listing_id>/edit/` | GET/POST | 编辑发布 |
| `/listings/<listing_id>/off-shelf/` | POST | 卖家下架 |
| `/listings/<listing_id>/create-order/` | POST | 下单并选择自提点 |
| `/orders/<order_id>/` | GET | 订单详情 |
| `/orders/<order_id>/cancel/` | POST | 取消订单 |
| `/pickup/<pickup_record_id>/` | GET | 查看自提码和自提信息 |
| `/orders/<order_id>/review/` | GET/POST | 提交订单评价 |

### 3.3 管理员页面

| URL | 方法 | 功能 |
|---|---|---|
| `/admin/` | GET | 管理端首页/统计概览 |
| `/admin/users/` | GET/POST | 用户管理 |
| `/admin/users/<user_id>/toggle/` | POST | 启用/禁用用户 |
| `/admin/books/` | GET | 图书档案管理 |
| `/admin/books/<book_id>/edit/` | GET/POST | 编辑图书档案 |
| `/admin/listings/` | GET | 发布商品管理 |
| `/admin/listings/<listing_id>/off-shelf/` | POST | 强制下架 |
| `/admin/orders/` | GET | 订单管理 |
| `/admin/orders/<order_id>/cancel/` | POST | 管理员取消订单 |
| `/admin/pickups/` | GET | 自提记录管理 |
| `/admin/pickups/<pickup_record_id>/complete/` | POST | 确认完成自提 |
| `/admin/pickups/<pickup_record_id>/expire/` | POST | 标记自提过期 |
| `/admin/reviews/` | GET | 评价管理 |
| `/admin/reviews/<review_id>/delete/` | POST | 删除违规评价 |
| `/admin/categories/` | GET/POST | 分类管理 |
| `/admin/conditions/` | GET/POST | 成色管理 |
| `/admin/pickup-points/` | GET/POST | 自提点管理 |
| `/admin/audit-logs/` | GET | 审计日志 |
| `/admin/stats/` | GET | 销售、发布、评价、自提统计 |

不启用 Django 默认后台作为主管理界面；如需内部调试，可以单独挂载到 `/django-admin/`，避免与自定义 `/admin/` 冲突。

## 4. 页面清单

### 4.1 用户端页面

| 页面 | URL | 说明 |
|---|---|---|
| 首页 | `/` | 推荐/最新在售商品、分类快捷入口 |
| 商品列表 | `/listings/` | 关键词、分类、成色、类型、价格筛选 |
| 商品详情 | `/listings/<id>/` | 卖家、价格、成色、库存、下单入口 |
| 图书详情 | `/books/<id>/` | 图书元信息及所有相关发布 |
| 登录 | `/accounts/login/` | 用户名/学号登录 |
| 注册 | `/accounts/register/` | 学号、用户名、密码、联系方式 |
| 个人资料 | `/accounts/profile/` | 查看/修改资料 |
| 修改密码 | `/accounts/password/change/` | 修改密码 |
| 我的发布 | `/me/listings/` | 我的商品及状态 |
| 发布商品 | `/listings/new/` | 新建图书或选择已有图书，然后发布 |
| 编辑商品 | `/listings/<id>/edit/` | 修改描述、价格、库存、成色等 |
| 我的订单 | `/me/orders/` | 买家订单/卖家订单 |
| 订单详情 | `/orders/<id>/` | 订单状态、自提信息、取消入口、评价入口 |
| 下单确认 | `/listings/<id>/create-order/` | 选择自提点并提交订单 |
| 自提详情 | `/pickup/<id>/` | 自提码、自提点、预约时间 |
| 评价页面 | `/orders/<id>/review/` | 对已完成订单评分和留言 |

### 4.2 管理员页面

| 页面 | URL | 说明 |
|---|---|---|
| 管理首页 | `/admin/` | 数量统计、待办概览 |
| 用户管理 | `/admin/users/` | 用户列表、禁用/启用 |
| 图书管理 | `/admin/books/` | 图书档案维护 |
| 发布管理 | `/admin/listings/` | 发布审核/下架 |
| 订单管理 | `/admin/orders/` | 订单查询、取消 |
| 自提管理 | `/admin/pickups/` | 等待自提列表、完成、过期 |
| 评价管理 | `/admin/reviews/` | 评价查看、删除 |
| 分类管理 | `/admin/categories/` | 分类新增、停用 |
| 成色管理 | `/admin/conditions/` | 成色新增、编辑 |
| 自提点管理 | `/admin/pickup-points/` | 自提点新增、停用 |
| 审计日志 | `/admin/audit-logs/` | 按订单/操作人/类型查询 |
| 统计报表 | `/admin/stats/` | 成交额、销量、评分、自提状态 |

## 5. 页面与数据库表对应关系

| 页面 | 主要数据来源 |
|---|---|
| 首页 | `v_listing_detail`、`listing`、`book_category` |
| 商品列表/搜索 | `v_listing_detail`、`listing`、`book`、`book_category`、`book_condition` |
| 商品详情 | `v_listing_detail`、`listing`、`book`、`user` |
| 图书详情 | `book`、`book_category`、`listing` |
| 发布/编辑商品 | `book`、`book_category`、`book_condition`、`listing`、`user` |
| 我的发布 | `listing`、`book`、`book_condition`、`orders` 统计 |
| 下单确认 | `listing`、`user`、`pickup_point`；最终调用 `proc_create_order_with_pickup` |
| 订单列表/详情 | `v_order_detail`、`orders`、`listing`、`pickup_record`、`review`、`audit_log` |
| 自提详情 | `v_pickup_detail`、`pickup_record`、`orders`、`pickup_point` |
| 完成自提 | `pickup_record`、`orders` |
| 评价页面 | `orders`、`user`、`review`；插入 `review` 后由触发器写审计日志 |
| 管理统计 | 现有 3 个视图 + `04_advanced_query.sql` 中的统计思路 |
| 审计日志 | `audit_log`、`orders`、`user` |

## 6. 用户业务流程

### 6.1 注册

- 用户提交学号、用户名、姓名、手机号、学院、密码。
- Django 校验 `student_no`、`username`、`phone` 唯一。
- 写入 `user`：`role = 'USER'`、`status = 'ACTIVE'`、`credit_score = 100`。
- 密码使用 Django 的密码哈希算法后存入 `password_hash`。

### 6.2 登录和退出

- 使用自定义用户认证，映射现有 `user` 表。
- 登录时校验 `status = 'ACTIVE'`，禁用用户不能登录。
- 退出时清除 Django session。

### 6.3 个人中心

- 查看和修改 `real_name`、`department`、`phone`。
- 建议 `student_no`、`username` 不可修改，保证账号稳定性。
- 修改密码通过 `password_hash` 字段完成，不新建表。

### 6.4 买家流程

浏览商品 → 查看商品详情 → 选择自提点并下单 → 查看自提码 → 到自提点取书 → 管理员确认完成 → 买家评价卖家。

### 6.5 卖家流程

发布商品 → 管理我的发布 → 收到订单 → 等待自提 → 订单完成 → 查看评价。

### 6.6 管理员流程

查看统计 → 管理用户、发布、订单、自提、评价、基础数据和审计日志。

## 7. 商品发布流程

1. 校验当前用户已登录、`status = 'ACTIVE'`。
2. 搜索现有 `book`：
   - 优先按 ISBN、书名、作者搜索。
   - 如果存在，直接选择该图书档案。
   - 如果不存在，先创建 `book`，填写分类、书名、作者、出版社、原价、版次、出版年份等。
3. 选择 `book_condition` 成色。
4. 选择 `listing_type`：
   - `SALE`：填写价格，数据库要求 `price >= 0`。
   - `DONATION`：价格必须为 `0`，可填写 `donation_note`。
5. 填写 `stock`，默认 1，数据库要求 `stock >= 0`。
6. 新发布状态为 `ON_SALE`，`published_at`、`updated_at` 由数据库维护。
7. 发布操作在 Django 事务中完成：先创建图书档案，再创建 `listing`。
8. 卖家只能编辑 `ON_SALE` 且没有活跃订单的发布中的价格和库存；描述、成色等可以更宽松地修改。
9. 下架操作只能用于 `ON_SALE` 发布；有 `PICKUP_PENDING` 订单时，应先处理订单。

## 8. 订单流程

### 8.1 创建订单

1. 校验买家已登录且 `status = 'ACTIVE'`。
2. 校验发布状态为 `ON_SALE`，库存大于 0，买家不能是卖家本人。
3. 校验自提点 `status = 'ACTIVE'`。
4. 调用现有存储过程 `proc_create_order_with_pickup`。
5. 存储过程负责：
   - 锁定发布记录，防止并发超卖。
   - 校验库存和买卖双方。
   - 创建 `PICKUP_PENDING` 订单。
   - 扣减库存，库存为 0 时发布状态变为 `SOLD`。
   - 创建 `WAITING` 自提记录和唯一自提码。
   - 在同一个事务中提交。
6. 订单创建后，`trg_orders_after_insert_audit` 自动写入 `AUTO_CREATE_ORDER` 审计日志，Django 不重复写入。

### 8.2 订单状态

- `PENDING`：待确认。
- `LOCKED`：锁定，不能继续交易。
- `PICKUP_PENDING`：等待自提。
- `COMPLETED`：已完成。
- `CANCELLED`：已取消。

### 8.3 取消订单

- 允许取消 `PENDING`、`LOCKED`、`PICKUP_PENDING` 订单。
- Django 在 `transaction.atomic` 中使用 `select_for_update()` 锁定订单和发布记录。
- 订单变为 `CANCELLED`，写入 `cancelled_at`。
- 如果自提记录存在，变为 `CANCELLED`。
- 如果库存已扣减，`stock + 1`；发布状态如果是 `SOLD`，恢复为 `ON_SALE`，如果是 `LOCKED`，保持 `LOCKED`。
- 写入 `audit_log`，动作类型如 `CANCEL_ORDER`。

### 8.4 完成订单

- 完成订单由自提流程触发，不是单独操作。
- `pickup_record` 变为 `FINISHED` 后，订单才变为 `COMPLETED`。

### 8.5 支付处理

- 现有数据库没有支付表和支付状态，`paid_at` 只是可空时间字段。
- Web 端按线下校园自提交易设计，不做在线支付流程，也不为支付新建表。

## 9. 自提流程

1. 下单时选择自提点，存储过程自动创建 `pickup_record`。
2. 初始状态为 `WAITING`，`pickup_code` 唯一，`scheduled_time` 默认下单后一天。
3. 买家在订单详情或自提详情页查看自提码。
4. 管理员在自提管理页输入/核对自提码，点击“完成自提”。
5. Django 在同一个事务中：
   - 将 `pickup_record.status` 改为 `FINISHED`。
   - 写入 `picked_time = NOW()`。
   - 将 `orders.status` 改为 `COMPLETED`。
   - 写入 `completed_at = NOW()`。
6. 超时未取：
   - 页面根据 `scheduled_time` 显示“已过期”提醒。
   - 实际状态改为 `EXPIRED` 可由管理员操作，或由 Django 定时任务/管理命令处理。
   - 如果订单未完成，则同步取消订单并恢复库存。
7. 取消订单时，自提记录同步改为 `CANCELLED`。

## 10. 评价流程

1. 只允许评价 `COMPLETED` 订单。
2. 按现有测试数据约定，默认“买家评价卖家”：
   - `reviewer_id = orders.buyer_id`
   - `reviewee_id = orders.seller_id`
3. 校验：
   - 评价人必须是订单买家。
   - 被评价人必须是订单卖家。
   - 评分在 1 到 5 之间。
   - 内容不超过 500 字符。
4. 因为 `review.order_id` 唯一，一个订单只能有一条评价。
5. 插入 `review` 后，`trg_review_after_insert_audit` 自动写入 `AUTO_CREATE_REVIEW` 审计日志。
6. 如果后续需要买卖双方互评，当前表结构不支持，需要先和数据库负责人确认；当前阶段不新增表。
7. `credit_score` 当前没有数据库触发器或存储过程自动维护。如果业务确认需要评分影响信用分，应在 Django 事务中实现；如果没有明确规则，暂不自动修改。

## 11. 管理员功能

### 11.1 用户管理

- 查看用户列表，按学号、用户名、学院、状态筛选。
- 禁用/启用用户，对应 `status = 'DISABLED'` / `'ACTIVE'`。
- 管理员可重置用户密码。

### 11.2 图书和发布管理

- 维护 `book` 图书档案。
- 维护 `book_category` 分类和 `book_condition` 成色。
- 查看所有 `listing`，可强制下架违规发布。

### 11.3 订单和自提管理

- 查看所有订单和自提记录。
- 管理员可取消未完成订单。
- 管理员负责核对自提码、完成自提、处理过期自提。

### 11.4 评价管理

- 查看所有评价和评分。
- 删除违规评价，删除时写入审计日志。

### 11.5 基础数据管理

- 自提点：新增、编辑、启用/停用。
- 分类：新增、编辑、启用/停用。
- 成色：新增、编辑；注意 `book_condition` 没有 `status` 字段，被引用时不能删除。

### 11.6 审计和统计

- 查看 `audit_log`。
- 使用 `v_listing_detail`、`v_order_detail`、`v_pickup_detail` 和统计查询展示商品数、订单数、成交额、评价均分、自提状态等。

## 12. 推荐开发顺序

### 第 1 阶段：项目骨架与数据库映射

- 创建 Django 项目和 App 目录。
- 配置 MySQL 连接。
- 用 `managed = False` 映射 10 张表和 3 个视图。
- 实现自定义用户认证，验证登录注册。
- 验证现有触发器、视图、存储过程不被影响。

### 第 2 阶段：公共 UI 骨架

- 编写 `base.html`、导航栏、页脚、消息提示。
- 配置静态资源目录。
- 实现通用分页和筛选控件。

### 第 3 阶段：商品浏览

- 首页。
- 商品列表、搜索、分类筛选。
- 商品详情、图书详情。
- 使用 `v_listing_detail` 减少重复查询。

### 第 4 阶段：发布与卖家管理

- 发布商品表单。
- 我的发布。
- 编辑发布、下架。
- 图书档案搜索和新建。

### 第 5 阶段：订单流程

- 下单确认页。
- 调用 `proc_create_order_with_pickup`。
- 我的订单。
- 订单详情。
- 取消订单及库存恢复。

### 第 6 阶段：自提流程

- 自提详情页。
- 管理员完成自提。
- 过期和取消处理。

### 第 7 阶段：评价流程

- 评价页面。
- 评价校验。
- 评价列表展示。
- 依赖现有评价触发器。

### 第 8 阶段：管理端

- 管理首页和统计。
- 用户、图书、发布、订单、自提、评价管理。
- 分类、成色、自提点维护。
- 审计日志页面。

### 第 9 阶段：收尾

- 错误页面和权限控制检查。
- CSRF、登录校验、防止越权操作。
- 表单边界值测试。
- 并发下单、并发取消、自提过期等场景验证。
- 整体 UI 打磨和浏览器测试。

