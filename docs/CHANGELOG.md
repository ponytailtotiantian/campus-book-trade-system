# 修改说明

## 2026-09-07 验证江同学提交并修复演示问题

本次检查了江同学提交到 GitHub 的 Django 网站与 DeepSeek AI 助手相关代码，并在本地完成运行验证。

### 已验证内容

- 远程仓库更新已同步到本地，最新提交为 `Add DeepSeek AI assistant`。
- `python manage.py check` 通过，Django 项目配置无系统检查错误。
- Django ORM 能连接本地 MySQL，并能读取 `user`、`book`、`listing`、`orders` 等核心表。
- 首页、商品列表页、AI 助手页、登录页、个人中心页均可正常访问。
- `testuser / 123456` 测试账号可正常登录。
- 支付下单流程可正常创建订单和自提记录。

### 修复内容

- 修正 `sql/03_dml_extend.sql` 的演示数据状态，保留部分商品为 `ON_SALE`，避免首页、商品列表和 Agent 查询没有可展示数据。
- 修正 `proc_create_order_with_pickup` 存储过程的库存扣减逻辑，确保库存扣到 0 时发布状态会变为 `SOLD`。
- 在存储过程中增加发布状态校验，避免直接调用存储过程购买非在售商品。
- 让存储过程显式返回新订单编号，Django 下单逻辑直接使用该返回值，避免依赖 `LAST_INSERT_ID()` 造成订单号不稳定。
- 首页、商品列表、商品详情和 Agent 查询统一过滤 `status='ON_SALE'` 且 `stock>0` 的发布信息，避免库存为 0 的商品继续展示。

### 注意事项

- `.env` 为本地环境文件，不提交到 GitHub。
- 如需启用 AI 助手真实问答，需要在 `.env` 中配置 `DEEPSEEK_API_KEY`。
- 数据库结构仍以 `sql/` 目录为准，Django Model 保持 `managed = False`。
