# 校园二手书交易系统

基于 Django + MySQL + Bootstrap 的校园二手书交易与捐赠自提管理系统。当前已实现商品浏览、搜索、分类、详情、用户登录/个人中心、发布二手书和模拟信用卡支付等可运行页面。

> 数据库结构全部由 `sql/` 目录管理。Django 使用 `managed = False` 映射现有 MySQL 表，不创建 migration，也不会修改数据库表结构。

## 技术栈

- Python 3.12
- Django 5.2
- MySQL 8.x
- PyMySQL
- Bootstrap 5（项目本地 `static/vendor/bootstrap/`）
- python-dotenv

## 环境要求

- Windows
- Python 3.10 或更高版本
- MySQL 8.x
- 本项目只面向 Windows 本地开发，不需要 Docker、Nginx、Redis，也不需要真实支付服务

## 项目目录

```text
manage.py
config/
  settings/           # base.py / dev.py / prod.py
  urls.py
apps/
  accounts/           # 登录、退出、个人中心
  catalog/            # 商品列表、搜索、分类、详情
  marketplace/        # 发布二手书
  trade/              # 模拟支付、订单查看
  pickup/             # 自提相关 app
  reviews/            # 评价相关 app
  admin_dashboard/    # 管理端 app
sql/
  01_ddl.sql
  02_dml.sql
  03_dml_extend.sql
  04_advanced_query.sql
  05_view.sql
  06_trigger.sql
  07_procedure.sql
  08_transaction.sql
  09_performance_optimization.sql
  10_security_strategy.sql
deploy/
  aliyun_deploy.sh
  backup_database.sh
  restore_database.sh
docs/
  performance_security_backup.md
static/
templates/
.env.example
requirements.txt
```

## 快速开始

### 1. 获取项目

```bash
git clone <你的仓库地址>
cd campus-book-trade-system-main
```

### 2. 创建并激活虚拟环境

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 配置环境变量

将 `.env.example` 复制为 `.env`：

```powershell
Copy-Item .env.example .env
```

或使用命令行：

```bat
copy .env.example .env
```

然后填写本机 MySQL 信息，至少修改：

```dotenv
MYSQL_PASSWORD=你的MySQL密码
```

`.env` 中其他字段保持模板即可：

```dotenv
DJANGO_SECRET_KEY=change-me-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=campus_book_trade
MYSQL_USER=root
MYSQL_PASSWORD=
```

`.env` 已被 `.gitignore` 忽略，不要提交到 Git。

### 4. 初始化 MySQL 数据库

1. 启动 MySQL 8.0 服务。
2. 使用有建库、建表、建视图、建触发器、建存储过程权限的 MySQL 用户登录。
3. 在项目根目录打开 MySQL 命令行客户端，依次执行：

```sql
source sql/01_ddl.sql
source sql/02_dml.sql
source sql/03_dml_extend.sql
source sql/05_view.sql
source sql/06_trigger.sql
source sql/07_procedure.sql
```

说明：

- `01_ddl.sql` 会创建 `campus_book_trade` 数据库和基础表。
- `02_dml.sql`、`03_dml_extend.sql` 导入基础测试数据和扩展测试数据。
- `05_view.sql`、`06_trigger.sql`、`07_procedure.sql` 创建视图、触发器和存储过程。
- `04_advanced_query.sql` 是查询演示脚本，`08_transaction.sql` 是事务演示脚本，**不是**项目启动必须执行的初始化脚本。
- `09_performance_optimization.sql` 用于报告4的 `EXPLAIN`、索引优化和优化前后对比。
- `10_security_strategy.sql` 用于报告4的数据库用户权限与安全策略演示。
- `deploy/backup_database.sh`、`deploy/restore_database.sh` 用于报告4的备份与恢复演示。
- 请勿修改 `sql/` 中的任何文件。

### 5. 启动 Django

```bat
python manage.py check
python manage.py runserver
```

项目自定义了开发服务器命令，会跳过 migration 检查；现有 MySQL 数据库不通过 Django migration 管理。

### 6. 浏览器访问

打开 <http://127.0.0.1:8000/>

当前主要页面：

| URL | 页面 |
| --- | --- |
| `/` | 首页 |
| `/catalog/` | 商品列表 |
| `/catalog/search/` | 商品搜索 |
| `/catalog/category/<category_id>/` | 分类筛选 |
| `/catalog/<listing_id>/` | 商品详情 |
| `/marketplace/listings/new/` | 发布二手书，需要登录 |
| `/trade/payment/<listing_id>/` | 模拟支付，需要登录 |
| `/trade/payment/success/<order_id>/` | 支付成功页 |
| `/trade/orders/<order_id>/` | 订单详情 |
| `/accounts/login/` | 登录 |
| `/accounts/profile/` | 个人中心，需要登录 |

## 测试账号

数据库初始化完成后，在项目根目录运行：

```bat
python manage.py create_test_user
```

然后使用：

```text
用户名：testuser
密码：123456
```

登录系统。如果 `testuser` 已经存在，该命令会提示账号已存在，不会重复创建，也不会覆盖现有用户数据。

## 常见问题

- MySQL 未启动：检查 Windows 服务中的 MySQL 8.0 服务是否正在运行。
- MySQL 用户名或密码错误：检查 `.env` 中的 `MYSQL_USER` 和 `MYSQL_PASSWORD`。
- 数据库不存在：先执行 `sql/01_ddl.sql`，并确认 `MYSQL_DB=campus_book_trade`。
- Python 依赖没有安装：激活 `.venv` 后执行 `pip install -r requirements.txt`。
- 端口 3306 被占用：执行 `netstat -ano | findstr :3306` 检查占用进程；如需更换端口，需要同时修改 MySQL 配置和 `.env` 中的 `MYSQL_PORT`。
- Django 无法连接 MySQL：检查 MySQL 服务、`.env` 配置、用户名密码和端口，确认不是网络或权限问题后重新执行 `python manage.py check`。
- 出现 migration 相关提示：本项目数据库由 `sql/` 管理，请勿对现有数据库执行 `makemigrations` 或 `migrate`。

## 开发注意

- 数据库是唯一事实来源。
- 不要修改 `sql/` 文件。
- 不要修改数据库表结构。
- 保持 Django Model 的 `managed = False`。
- 不要新增会修改现有数据库结构的 migration。
- 不要把 `.env` 或数据库密码提交到 Git。
