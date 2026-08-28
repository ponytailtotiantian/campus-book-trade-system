sql/

├── 01\_ddl.sql

├── 02\_dml.sql

├── 03\_dml\_extend.sql

├── 04\_advanced\_query.sql

├── 05\_view.sql

├── 06\_trigger.sql

├── 07\_procedure.sql

└── 08\_transaction.sql



其中：



01\_ddl.sql：数据库及表结构

02\_dml.sql：基础测试数据

03\_dml\_extend.sql：扩展测试数据

04\_advanced\_query.sql：复杂查询

05\_view.sql：视图

06\_trigger.sql：触发器

07\_procedure.sql：存储过程

08\_transaction.sql：事务



不要因为方便 Web 开发而修改、删除或重新设计现有表结构。

如果发现数据库结构与 Web 功能存在冲突：

先检查现有 SQL；

优先通过 Django 后端逻辑解决；

不要直接修改数据库；

如果确实必须修改数据库，先说明原因并等待确认

